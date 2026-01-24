"""
Data Input Center
Single entry point for Excel import and quick manual entry.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
import re
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

import pandas as pd
import streamlit as st
from dateutil import parser as date_parser
from sqlalchemy import text

from config.theme import generate_css
from models.database import DatabaseManager, Project, ProjectStatus, Transaction, TransactionType
from utils.consultant_db import ensure_consultant_schema


st.set_page_config(page_title="Data Input Center", page_icon="📥", layout="wide")
st.markdown(generate_css("light"), unsafe_allow_html=True)

st.title("📥 Data Input Center")
st.caption("Single entry point for all data - Excel import or manual entry")


@st.cache_resource
def get_database() -> DatabaseManager:
    return DatabaseManager("sqlite:///industrial_real_estate.db")


def get_db_connection() -> DatabaseManager:
    return get_database()


def ensure_excel_import_tables(db: DatabaseManager) -> None:
    create_statements = [
        """
        CREATE TABLE IF NOT EXISTS monthly_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER,
            project_id INTEGER,
            expense_month INTEGER NOT NULL,
            expense_year INTEGER NOT NULL,
            category TEXT,
            amount NUMERIC(15, 2) NOT NULL,
            currency TEXT NOT NULL DEFAULT 'AUD',
            notes TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS excel_import_batches (
            batch_id TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            sheet_name TEXT,
            sheet_type TEXT,
            asset_id INTEGER,
            project_id INTEGER,
            record_count INTEGER NOT NULL DEFAULT 0,
            updated_count INTEGER NOT NULL DEFAULT 0,
            duplicate_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'success',
            error_message TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS excel_import_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            previous_data TEXT
        );
        """,
    ]
    with db.engine.begin() as conn:
        for stmt in create_statements:
            conn.execute(text(stmt))


def normalize_label(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def parse_month(value: object) -> Optional[date]:
    if value is None:
        return None
    text_value = str(value).strip()
    if not text_value:
        return None
    try:
        parsed = date_parser.parse(text_value, fuzzy=True, default=datetime(1900, 1, 1))
        if parsed.year < 2000:
            return None
        return date(parsed.year, parsed.month, 1)
    except (ValueError, TypeError):
        return None


def detect_sheet_type(df: pd.DataFrame, sheet_name: str) -> str:
    name_lower = sheet_name.lower()
    if "cash summary" in name_lower or "summary" in name_lower:
        return "Cash Summary"
    if "payment" in name_lower or "detail" in name_lower:
        return "Payment Details"
    if "budget" in name_lower:
        return "Budget"

    preview = df.head(12).astype(str).fillna("")
    joined = " ".join(preview.values.flatten()).lower()

    if "invoice" in joined and "company" in joined:
        return "Payment Details"
    if "discipline" in joined and "consultant" in joined:
        return "Budget"
    if re.search(r"\bjan\b|\bfeb\b|\bmar\b|\bapr\b|\bmay\b|\bjun\b|\bjul\b|\baug\b|\bsep\b|\boct\b|\bnov\b|\bdec\b", joined):
        return "Cash Summary"
    return "Unknown"


def extract_entity_name(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    row0 = df.iloc[0].tolist()
    for cell in row0:
        if cell is not None and str(cell).strip():
            return str(cell).strip()
    return ""


def find_header_row(df: pd.DataFrame, required_keywords: List[str], search_rows: int = 15) -> Optional[int]:
    max_rows = min(search_rows, len(df))
    for idx in range(max_rows):
        row = df.iloc[idx].astype(str).fillna("").str.lower()
        row_text = " ".join(row.values)
        if all(keyword in row_text for keyword in required_keywords):
            return idx
    return None


def parse_cash_summary(df: pd.DataFrame, entity_name: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["entity_name", "expense_category", "month_year", "amount"])

    header_row_idx = 4 if len(df) > 4 else 0
    month_row = df.iloc[header_row_idx].tolist()

    month_cols: Dict[int, date] = {}
    for col_idx, value in enumerate(month_row):
        month_date = parse_month(value)
        if month_date:
            month_cols[col_idx] = month_date

    if not month_cols:
        for idx in range(min(10, len(df))):
            row = df.iloc[idx].tolist()
            for col_idx, value in enumerate(row):
                month_date = parse_month(value)
                if month_date:
                    month_cols[col_idx] = month_date
            if month_cols:
                header_row_idx = idx
                break

    start_row_idx = 7 if len(df) > 7 else header_row_idx + 1
    rows = []
    for idx in range(start_row_idx, len(df)):
        row = df.iloc[idx].tolist()
        category = str(row[0]).strip() if len(row) > 0 and row[0] is not None else ""
        if not category and len(row) > 1 and row[1] is not None:
            category = str(row[1]).strip()
        if not category or category.lower() in {"total", "grand total"}:
            continue
        for col_idx, month_date in month_cols.items():
            if col_idx >= len(row):
                continue
            amount = pd.to_numeric(row[col_idx], errors="coerce")
            if pd.isna(amount):
                continue
            rows.append(
                {
                    "entity_name": entity_name,
                    "expense_category": category,
                    "month_year": month_date,
                    "amount": float(amount),
                }
            )

    return pd.DataFrame(rows, columns=["entity_name", "expense_category", "month_year", "amount"])


def parse_payment_details(df: pd.DataFrame, entity_name: str) -> pd.DataFrame:
    header_row_idx = find_header_row(df, ["company", "invoice"]) or 0
    header = df.iloc[header_row_idx].tolist()
    data = df.iloc[header_row_idx + 1 :].copy()
    data.columns = header
    data = data.dropna(how="all")

    col_map = {}
    for col in data.columns:
        label = normalize_label(col)
        if "company" in label or "vendor" in label:
            col_map[col] = "company"
        elif "invoice" in label and "num" in label:
            col_map[col] = "invoice_number"
        elif "due date" in label:
            col_map[col] = "due_date"
        elif "payment" in label and "date" in label:
            col_map[col] = "payment_date"
        elif "excl" in label and "gst" in label:
            col_map[col] = "amount_excl_gst"
        elif "incl" in label and "gst" in label:
            col_map[col] = "amount_incl_gst"
        elif "amount" in label and "gst" not in label:
            col_map[col] = "amount_incl_gst"
        elif "description" in label or "details" in label:
            col_map[col] = "description"

    normalized = pd.DataFrame()
    for source_col, target_col in col_map.items():
        normalized[target_col] = data[source_col]

    for col in ["company", "invoice_number", "due_date", "payment_date", "amount_excl_gst", "amount_incl_gst", "description"]:
        if col not in normalized.columns:
            normalized[col] = None

    normalized["due_date"] = pd.to_datetime(normalized["due_date"], errors="coerce").dt.date
    normalized["payment_date"] = pd.to_datetime(normalized["payment_date"], errors="coerce").dt.date
    normalized["amount_excl_gst"] = pd.to_numeric(normalized["amount_excl_gst"], errors="coerce")
    normalized["amount_incl_gst"] = pd.to_numeric(normalized["amount_incl_gst"], errors="coerce")
    normalized["entity_name"] = entity_name

    return normalized[
        [
            "entity_name",
            "company",
            "invoice_number",
            "due_date",
            "payment_date",
            "amount_excl_gst",
            "amount_incl_gst",
            "description",
        ]
    ]


def parse_budget(df: pd.DataFrame, entity_name: str) -> pd.DataFrame:
    header_row_idx = find_header_row(df, ["discipline", "consultant"]) or 1
    header = df.iloc[header_row_idx].tolist()
    data = df.iloc[header_row_idx + 1 :].copy()
    data.columns = header
    data = data.dropna(how="all")

    col_map = {}
    for col in data.columns:
        label = normalize_label(col)
        if "discipline" in label:
            col_map[col] = "discipline"
        elif "consultant" in label:
            col_map[col] = "consultant_name"
        elif "contact" in label:
            col_map[col] = "contact_person"
        elif "scope" in label or "work" in label:
            col_map[col] = "work_scope"
        elif "budget" in label or "amount" in label:
            col_map[col] = "budgeted_amount"

    normalized = pd.DataFrame()
    for source_col, target_col in col_map.items():
        normalized[target_col] = data[source_col]

    for col in ["discipline", "consultant_name", "contact_person", "work_scope", "budgeted_amount"]:
        if col not in normalized.columns:
            normalized[col] = None

    normalized["budgeted_amount"] = pd.to_numeric(normalized["budgeted_amount"], errors="coerce")
    normalized["entity_name"] = entity_name

    return normalized[
        [
            "entity_name",
            "discipline",
            "consultant_name",
            "contact_person",
            "work_scope",
            "budgeted_amount",
        ]
    ]


def get_assets() -> List[Dict]:
    db = get_db_connection()
    with db.engine.begin() as conn:
        rows = conn.execute(text("SELECT id, name FROM assets ORDER BY name")).mappings()
        return [dict(row) for row in rows]


def get_projects_by_asset(asset_id: Optional[int]) -> List[Dict]:
    if not asset_id:
        return []
    db = get_db_connection()
    with db.engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, project_name FROM projects WHERE asset_id = :asset_id ORDER BY project_name"),
            {"asset_id": asset_id},
        ).mappings()
        return [dict(row) for row in rows]


def get_all_projects() -> List[Dict]:
    db = get_db_connection()
    with db.engine.begin() as conn:
        rows = conn.execute(text("SELECT id, project_name FROM projects ORDER BY project_name")).mappings()
        return [dict(row) for row in rows]


def get_consultants() -> List[Dict]:
    db = get_db_connection()
    ensure_consultant_schema(db)
    with db.engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, name FROM consultants WHERE is_active = 1 ORDER BY name")
        ).mappings()
        return [dict(row) for row in rows]


def get_transaction_categories() -> List[str]:
    return [
        "Rental Income",
        "Sale Proceeds",
        "Facility Line Fee",
        "Consulting & Accounting",
        "Legal Fees",
        "Construction Costs",
        "Marketing",
        "Insurance",
        "Rates & Taxes",
        "Other",
    ]


def record_import_action(session, batch_id: str, table_name: str, record_id: int, action: str, previous: Optional[dict]):
    session.execute(
        text(
            """
            INSERT INTO excel_import_records (batch_id, table_name, record_id, action, previous_data)
            VALUES (:batch_id, :table_name, :record_id, :action, :previous_data)
            """
        ),
        {
            "batch_id": batch_id,
            "table_name": table_name,
            "record_id": record_id,
            "action": action,
            "previous_data": None,
        },
    )


def get_cash_summary_existing(session, asset_id: int) -> Dict[Tuple[str, int, int], Dict[str, object]]:
    rows = session.execute(
        text(
            """
            SELECT id, category, expense_year, expense_month, amount
            FROM monthly_expenses
            WHERE asset_id = :asset_id
            """
        ),
        {"asset_id": asset_id},
    ).mappings()
    existing = {}
    for row in rows:
        key = (row["category"] or "", int(row["expense_year"]), int(row["expense_month"]))
        existing[key] = dict(row)
    return existing


def get_payment_existing(session, asset_id: int, invoice_numbers: List[str], dates: List[date]) -> set:
    if not invoice_numbers and not dates:
        return set()
    query = session.query(Transaction).filter(Transaction.asset_id == asset_id)
    if invoice_numbers:
        query = query.filter(Transaction.reference_number.in_(invoice_numbers))
    if dates:
        query = query.filter(Transaction.transaction_date.in_(dates))
    existing = set()
    for tx in query.all():
        key = (tx.reference_number or "", float(tx.amount), tx.transaction_date)
        existing.add(key)
    return existing


def calculate_import_stats(
    session,
    sheet_type: str,
    asset_id: int,
    parsed_df: pd.DataFrame,
) -> Tuple[int, int, int]:
    if sheet_type == "Cash Summary":
        existing = get_cash_summary_existing(session, asset_id)
        new_count = 0
        update_count = 0
        for _, row in parsed_df.iterrows():
            month_date = row["month_year"]
            key = (row["expense_category"], month_date.year, month_date.month)
            if key in existing:
                update_count += 1
            else:
                new_count += 1
        return new_count, update_count, 0
    if sheet_type == "Payment Details":
        invoice_numbers = (
            parsed_df["invoice_number"].dropna().astype(str).str.strip().tolist()
            if "invoice_number" in parsed_df
            else []
        )
        dates = []
        for _, row in parsed_df.iterrows():
            tx_date = row["payment_date"] or row["due_date"]
            if isinstance(tx_date, date):
                dates.append(tx_date)
        existing = get_payment_existing(session, asset_id, invoice_numbers, dates)
        new_count = 0
        duplicate_count = 0
        for _, row in parsed_df.iterrows():
            tx_date = row["payment_date"] or row["due_date"]
            amount = row["amount_incl_gst"] if pd.notna(row["amount_incl_gst"]) else row["amount_excl_gst"]
            if pd.isna(amount) or not isinstance(tx_date, date):
                continue
            key = (str(row["invoice_number"] or "").strip(), -float(amount), tx_date)
            if key in existing:
                duplicate_count += 1
            else:
                new_count += 1
        return new_count, 0, duplicate_count
    if sheet_type == "Budget":
        valid_rows = parsed_df[pd.notna(parsed_df["consultant_name"]) & pd.notna(parsed_df["budgeted_amount"])]
        return len(valid_rows), 0, 0
    return 0, 0, 0


def import_cash_summary(session, batch_id: str, asset_id: int, project_id: Optional[int], parsed_df: pd.DataFrame):
    existing = get_cash_summary_existing(session, asset_id)
    inserted = 0
    updated = 0

    for _, row in parsed_df.iterrows():
        month_date = row["month_year"]
        key = (row["expense_category"], month_date.year, month_date.month)
        amount = float(row["amount"])
        if key in existing:
            prev = existing[key]
            session.execute(
                text(
                    """
                    UPDATE monthly_expenses
                    SET amount = :amount, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                    """
                ),
                {"amount": amount, "id": prev["id"]},
            )
            record_import_action(session, batch_id, "monthly_expenses", prev["id"], "update", {"amount": prev["amount"]})
            updated += 1
        else:
            result = session.execute(
                text(
                    """
                    INSERT INTO monthly_expenses (
                        asset_id, project_id, expense_month, expense_year, category, amount, currency, notes
                    )
                    VALUES (:asset_id, :project_id, :expense_month, :expense_year, :category, :amount, 'AUD', :notes)
                    """
                ),
                {
                    "asset_id": asset_id,
                    "project_id": project_id,
                    "expense_month": int(month_date.month),
                    "expense_year": int(month_date.year),
                    "category": row["expense_category"],
                    "amount": amount,
                    "notes": f"Imported via Excel batch {batch_id}",
                },
            )
            record_id = result.lastrowid
            record_import_action(session, batch_id, "monthly_expenses", record_id, "insert", None)
            inserted += 1

    return inserted, updated, 0


def import_payment_details(session, batch_id: str, asset_id: int, project_id: Optional[int], parsed_df: pd.DataFrame):
    invoice_numbers = (
        parsed_df["invoice_number"].dropna().astype(str).str.strip().tolist()
        if "invoice_number" in parsed_df
        else []
    )
    dates = []
    for _, row in parsed_df.iterrows():
        tx_date = row["payment_date"] or row["due_date"]
        if isinstance(tx_date, date):
            dates.append(tx_date)
    existing = get_payment_existing(session, asset_id, invoice_numbers, dates)

    inserted = 0
    duplicate = 0

    for _, row in parsed_df.iterrows():
        tx_date = row["payment_date"] or row["due_date"]
        amount = row["amount_incl_gst"] if pd.notna(row["amount_incl_gst"]) else row["amount_excl_gst"]
        if pd.isna(amount) or not isinstance(tx_date, date):
            continue

        amount_value = float(amount)
        invoice_number = str(row["invoice_number"] or "").strip()
        key = (invoice_number, -amount_value, tx_date)
        if key in existing:
            duplicate += 1
            continue

        description = row["description"] if pd.notna(row["description"]) else ""
        if not description:
            description = f"Payment to {row['company']}" if pd.notna(row["company"]) else "Imported payment"

        tx = Transaction(
            asset_id=asset_id,
            project_id=project_id,
            transaction_date=tx_date,
            transaction_type=TransactionType.EXPENSE,
            amount=-amount_value,
            category="Payment Details",
            description=description,
            reference_number=invoice_number or None,
            vendor_payee=row["company"] if pd.notna(row["company"]) else None,
            notes=f"Imported via Excel batch {batch_id}",
        )
        session.add(tx)
        session.flush()
        record_import_action(session, batch_id, "transactions", tx.id, "insert", None)
        inserted += 1

    return inserted, 0, duplicate


def import_budget(session, batch_id: str, asset_id: int, project_id: Optional[int], parsed_df: pd.DataFrame):
    inserted = 0
    for _, row in parsed_df.iterrows():
        consultant_name = row["consultant_name"]
        amount = row["budgeted_amount"]
        if pd.isna(consultant_name) or pd.isna(amount):
            continue

        consultant_name = str(consultant_name).strip()
        if not consultant_name:
            continue

        existing_consultant = session.execute(
            text("SELECT id FROM consultants WHERE lower(name) = lower(:name)"),
            {"name": consultant_name},
        ).fetchone()
        if existing_consultant:
            consultant_id = existing_consultant[0]
        else:
            result = session.execute(
                text(
                    """
                    INSERT INTO consultants (name, specialty, notes, is_active)
                    VALUES (:name, :specialty, :notes, 1)
                    """
                ),
                {
                    "name": consultant_name,
                    "specialty": row["discipline"] if pd.notna(row["discipline"]) else None,
                    "notes": "Imported via Excel",
                },
            )
            consultant_id = result.lastrowid
            record_import_action(session, batch_id, "consultants", consultant_id, "insert", None)

        notes = []
        if pd.notna(row["contact_person"]):
            notes.append(f"Contact: {row['contact_person']}")
        if pd.notna(row["discipline"]):
            notes.append(f"Discipline: {row['discipline']}")
        notes_text = " | ".join(notes) if notes else None

        result = session.execute(
            text(
                """
                INSERT INTO consultant_quotes (
                    consultant_id, asset_id, project_id, quote_date, amount, currency, status, scope, notes
                )
                VALUES (:consultant_id, :asset_id, :project_id, :quote_date, :amount, 'AUD', 'budgeted', :scope, :notes)
                """
            ),
            {
                "consultant_id": consultant_id,
                "asset_id": asset_id,
                "project_id": project_id,
                "quote_date": date.today(),
                "amount": float(amount),
                "scope": row["work_scope"] if pd.notna(row["work_scope"]) else None,
                "notes": notes_text,
            },
        )
        record_id = result.lastrowid
        record_import_action(session, batch_id, "consultant_quotes", record_id, "insert", None)
        inserted += 1

    return inserted, 0, 0


def detect_excel_type(df: pd.DataFrame, sheet_name: str) -> str:
    legacy_type = detect_sheet_type(df, sheet_name)
    if legacy_type != "Unknown":
        return legacy_type

    header_row = find_header_row(df, ["project", "asset"])
    if header_row is not None:
        return "Projects"

    header_row = find_header_row(df, ["date", "amount"])
    if header_row is not None:
        return "Transactions"

    header_row = find_header_row(df, ["name", "email"])
    if header_row is not None:
        return "Consultants"

    header_row = find_header_row(df, ["quote", "amount"])
    if header_row is not None:
        return "Consultant Quotes"

    return "Unknown"


def build_structured_df(df_raw: pd.DataFrame, required_keywords: List[str]) -> pd.DataFrame:
    header_row_idx = find_header_row(df_raw, required_keywords)
    if header_row_idx is None:
        return pd.DataFrame()
    header = df_raw.iloc[header_row_idx].tolist()
    data = df_raw.iloc[header_row_idx + 1 :].copy()
    data.columns = header
    return data.dropna(how="all")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_label(col).replace(" ", "_") for col in df.columns]
    return df


def parse_date_value(value: object) -> Optional[date]:
    if isinstance(value, date):
        return value
    if value is None or str(value).strip() == "":
        return None
    try:
        return date_parser.parse(str(value), fuzzy=True).date()
    except Exception:
        return None


def import_projects_from_excel(session, batch_id: str, df_raw: pd.DataFrame, target_asset_id: Optional[int]) -> Tuple[int, int]:
    df = build_structured_df(df_raw, ["project", "asset"])
    if df.empty:
        return 0, 0
    df = normalize_columns(df)

    inserted = 0
    duplicate = 0

    for _, row in df.iterrows():
        project_name = str(row.get("project_name") or row.get("project") or row.get("name") or "").strip()
        if not project_name:
            continue

        asset_id = row.get("asset_id")
        asset_name = row.get("asset") or row.get("asset_name")
        if pd.notna(asset_id):
            asset_id = int(asset_id)
        elif asset_name:
            asset_id = get_asset_id_by_name(str(asset_name))
        elif target_asset_id:
            asset_id = target_asset_id
        else:
            continue

        if not asset_exists(session, asset_id):
            continue

        existing = session.query(Project).filter(
            Project.asset_id == asset_id,
            Project.project_name == project_name,
        ).first()
        if existing:
            duplicate += 1
            continue

        status_label = str(row.get("status") or "Planning")
        status_enum = map_project_status(status_label)
        total_budget = row.get("budget") or row.get("total_budget")
        start_date = parse_date_value(row.get("start_date") or row.get("planned_start_date"))
        completion_date = parse_date_value(row.get("planned_completion_date") or row.get("expected_completion"))

        notes = build_project_notes(row.get("location"), row.get("building_area"), row.get("area"))

        project = Project(
            asset_id=asset_id,
            project_name=project_name,
            status=status_enum,
            total_budget=float(total_budget) if pd.notna(total_budget) else None,
            planned_start_date=start_date,
            planned_completion_date=completion_date,
            notes=notes,
        )
        session.add(project)
        session.flush()
        record_import_action(session, batch_id, "projects", project.id, "insert", None)
        inserted += 1

    return inserted, duplicate


def import_transactions_from_excel(
    session,
    batch_id: str,
    df_raw: pd.DataFrame,
    target_asset_id: Optional[int],
    target_project_id: Optional[int],
) -> Tuple[int, int]:
    df = build_structured_df(df_raw, ["date", "amount"])
    if df.empty:
        return 0, 0
    df = normalize_columns(df)

    inserted = 0
    duplicate = 0

    for _, row in df.iterrows():
        tx_date = parse_date_value(row.get("transaction_date") or row.get("date"))
        amount = row.get("amount")
        if not tx_date or pd.isna(amount):
            continue

        asset_id = row.get("asset_id")
        asset_name = row.get("asset") or row.get("asset_name")
        if pd.notna(asset_id):
            asset_id = int(asset_id)
        elif asset_name:
            asset_id = get_asset_id_by_name(str(asset_name))
        elif target_asset_id:
            asset_id = target_asset_id
        else:
            continue

        if not asset_exists(session, asset_id):
            continue

        project_id = row.get("project_id")
        project_name = row.get("project") or row.get("project_name")
        if pd.notna(project_id):
            project_id = int(project_id)
        elif project_name:
            project_id = get_project_id_by_name(str(project_name))
        elif target_project_id:
            project_id = target_project_id

        if project_id and not project_exists(session, project_id):
            project_id = None

        tx_type_label = str(row.get("type") or row.get("transaction_type") or "Expense")
        tx_type = TransactionType.INCOME if tx_type_label.lower().startswith("inc") else TransactionType.EXPENSE
        amount_value = float(amount)
        signed_amount = amount_value if tx_type == TransactionType.INCOME else -abs(amount_value)

        reference_number = str(row.get("invoice_number") or row.get("reference_number") or "").strip() or None
        category = str(row.get("category") or "Other").strip()
        description = str(row.get("description") or category).strip()
        vendor = str(row.get("counterparty") or row.get("vendor") or row.get("payee") or "").strip() or None

        if is_duplicate_transaction(
            session,
            asset_id=asset_id,
            project_id=project_id,
            tx_date=tx_date,
            amount=signed_amount,
            category=category,
            reference_number=reference_number,
        ):
            duplicate += 1
            continue

        tx = Transaction(
            asset_id=asset_id,
            project_id=project_id,
            transaction_date=tx_date,
            transaction_type=tx_type,
            amount=signed_amount,
            category=category,
            description=description,
            reference_number=reference_number,
            vendor_payee=vendor,
            notes=f"Imported via Excel batch {batch_id}",
        )
        session.add(tx)
        session.flush()
        record_import_action(session, batch_id, "transactions", tx.id, "insert", None)
        inserted += 1

    return inserted, duplicate


def import_consultants_from_excel(session, batch_id: str, df_raw: pd.DataFrame) -> Tuple[int, int]:
    df = build_structured_df(df_raw, ["name", "email"])
    if df.empty:
        return 0, 0
    df = normalize_columns(df)

    inserted = 0
    duplicate = 0

    for _, row in df.iterrows():
        name = str(row.get("name") or row.get("consultant_name") or "").strip()
        email = str(row.get("email") or "").strip()
        if not name or not email:
            continue

        if is_duplicate_consultant(session, name, email):
            duplicate += 1
            continue

        result = session.execute(
            text(
                """
                INSERT INTO consultants (
                    name, company, email, phone, specialty, notes, is_active, category, contact_person, typical_scopes
                )
                VALUES (
                    :name, :company, :email, :phone, :specialty, :notes, 1, :category, :contact_person, :typical_scopes
                )
                """
            ),
            {
                "name": name,
                "company": row.get("company"),
                "email": email,
                "phone": row.get("phone"),
                "specialty": row.get("specialty") or row.get("category"),
                "notes": row.get("notes"),
                "category": row.get("category"),
                "contact_person": row.get("contact_person"),
                "typical_scopes": row.get("specialty") or row.get("typical_scopes"),
            },
        )
        record_id = result.lastrowid
        record_import_action(session, batch_id, "consultants", record_id, "insert", None)
        inserted += 1

    return inserted, duplicate


def import_quotes_from_excel(
    session,
    batch_id: str,
    df_raw: pd.DataFrame,
    target_project_id: Optional[int],
) -> Tuple[int, int]:
    df = build_structured_df(df_raw, ["quote", "amount"])
    if df.empty:
        return 0, 0
    df = normalize_columns(df)

    inserted = 0
    duplicate = 0

    for _, row in df.iterrows():
        consultant_id = row.get("consultant_id")
        consultant_name = row.get("consultant") or row.get("consultant_name")
        if pd.notna(consultant_id):
            consultant_id = int(consultant_id)
        elif consultant_name:
            consultant_id = get_consultant_id_by_name(str(consultant_name))

        if not consultant_id:
            continue

        amount = row.get("quote_amount") or row.get("amount")
        quote_date = parse_date_value(row.get("quote_date") or row.get("date"))
        if pd.isna(amount) or not quote_date:
            continue

        project_id = row.get("project_id")
        project_name = row.get("project") or row.get("project_name")
        if pd.notna(project_id):
            project_id = int(project_id)
        elif project_name:
            project_id = get_project_id_by_name(str(project_name))
        elif target_project_id:
            project_id = target_project_id

        if project_id and not project_exists(session, project_id):
            project_id = None

        asset_id = get_asset_id_for_project(session, project_id) if project_id else None

        scope = str(row.get("scope_of_work") or row.get("scope") or "").strip()
        status = str(row.get("status") or "Quoted").strip()

        if is_duplicate_quote(session, consultant_id, project_id, quote_date, float(amount)):
            duplicate += 1
            continue

        result = session.execute(
            text(
                """
                INSERT INTO consultant_quotes (
                    consultant_id, asset_id, project_id, quote_date, amount, currency, status, scope, notes
                )
                VALUES (:consultant_id, :asset_id, :project_id, :quote_date, :amount, 'AUD', :status, :scope, :notes)
                """
            ),
            {
                "consultant_id": consultant_id,
                "asset_id": asset_id,
                "project_id": project_id,
                "quote_date": quote_date,
                "amount": float(amount),
                "status": status,
                "scope": scope,
                "notes": row.get("notes"),
            },
        )
        record_id = result.lastrowid
        record_import_action(session, batch_id, "consultant_quotes", record_id, "insert", None)
        inserted += 1

    return inserted, duplicate


def asset_exists(session, asset_id: Optional[int]) -> bool:
    if not asset_id:
        return False
    return session.execute(text("SELECT 1 FROM assets WHERE id = :id"), {"id": asset_id}).fetchone() is not None


def project_exists(session, project_id: Optional[int]) -> bool:
    if not project_id:
        return False
    return session.execute(text("SELECT 1 FROM projects WHERE id = :id"), {"id": project_id}).fetchone() is not None


def get_asset_id_by_name(name: str) -> Optional[int]:
    db = get_db_connection()
    with db.engine.begin() as conn:
        row = conn.execute(
            text("SELECT id FROM assets WHERE lower(name) = lower(:name)"),
            {"name": name},
        ).fetchone()
        return int(row[0]) if row else None


def get_project_id_by_name(name: str) -> Optional[int]:
    db = get_db_connection()
    with db.engine.begin() as conn:
        row = conn.execute(
            text("SELECT id FROM projects WHERE lower(project_name) = lower(:name)"),
            {"name": name},
        ).fetchone()
        return int(row[0]) if row else None


def get_consultant_id_by_name(name: str) -> Optional[int]:
    db = get_db_connection()
    with db.engine.begin() as conn:
        row = conn.execute(
            text("SELECT id FROM consultants WHERE lower(name) = lower(:name)"),
            {"name": name},
        ).fetchone()
        return int(row[0]) if row else None


def get_asset_id_for_project(session, project_id: Optional[int]) -> Optional[int]:
    if not project_id:
        return None
    row = session.execute(
        text("SELECT asset_id FROM projects WHERE id = :id"),
        {"id": project_id},
    ).fetchone()
    return int(row[0]) if row else None


def is_duplicate_transaction(
    session,
    asset_id: int,
    project_id: Optional[int],
    tx_date: date,
    amount: float,
    category: str,
    reference_number: Optional[str],
) -> bool:
    if reference_number:
        row = session.execute(
            text(
                """
                SELECT 1 FROM transactions
                WHERE asset_id = :asset_id
                  AND reference_number = :ref
                  AND transaction_date = :tx_date
                  AND amount = :amount
                """
            ),
            {
                "asset_id": asset_id,
                "ref": reference_number,
                "tx_date": tx_date,
                "amount": amount,
            },
        ).fetchone()
        return row is not None

    row = session.execute(
        text(
            """
            SELECT 1 FROM transactions
            WHERE asset_id = :asset_id
              AND transaction_date = :tx_date
              AND amount = :amount
              AND category = :category
              AND (:project_id IS NULL OR project_id = :project_id)
            """
        ),
        {
            "asset_id": asset_id,
            "project_id": project_id,
            "tx_date": tx_date,
            "amount": amount,
            "category": category,
        },
    ).fetchone()
    return row is not None


def is_duplicate_consultant(session, name: str, email: str) -> bool:
    row = session.execute(
        text(
            """
            SELECT 1 FROM consultants
            WHERE lower(name) = lower(:name) OR lower(email) = lower(:email)
            """
        ),
        {"name": name, "email": email},
    ).fetchone()
    return row is not None


def is_duplicate_quote(session, consultant_id: int, project_id: Optional[int], quote_date: date, amount: float) -> bool:
    row = session.execute(
        text(
            """
            SELECT 1 FROM consultant_quotes
            WHERE consultant_id = :consultant_id
              AND (:project_id IS NULL OR project_id = :project_id)
              AND quote_date = :quote_date
              AND amount = :amount
            """
        ),
        {
            "consultant_id": consultant_id,
            "project_id": project_id,
            "quote_date": quote_date,
            "amount": amount,
        },
    ).fetchone()
    return row is not None


def map_project_status(label: str) -> ProjectStatus:
    normalized = str(label).lower().replace(" ", "_")
    mapping = {
        "planning": ProjectStatus.PLANNING,
        "da": ProjectStatus.APPROVAL_PENDING,
        "approval_pending": ProjectStatus.APPROVAL_PENDING,
        "approved": ProjectStatus.APPROVED,
        "construction": ProjectStatus.CONSTRUCTION,
        "completed": ProjectStatus.COMPLETED,
    }
    return mapping.get(normalized, ProjectStatus.PLANNING)


def build_project_notes(location: object, area: object, building_area: object) -> Optional[str]:
    parts = []
    if location and str(location).strip():
        parts.append(f"Location: {location}")
    area_value = area or building_area
    if area_value and str(area_value).strip():
        parts.append(f"Building area: {area_value} sqm")
    return " | ".join(parts) if parts else None


def import_data(
    df_raw: pd.DataFrame,
    excel_type: str,
    target_asset_id: Optional[int],
    target_project_id: Optional[int],
    file_name: str,
    sheet_name: str,
) -> Dict[str, object]:
    db = get_db_connection()
    ensure_excel_import_tables(db)
    ensure_consultant_schema(db)
    session = db.get_session()
    batch_id = str(uuid4())

    inserted = updated = duplicate = 0

    try:
        with session.begin():
            session.execute(
                text(
                    """
                    INSERT INTO excel_import_batches (
                        batch_id, file_name, sheet_name, sheet_type, asset_id, project_id,
                        record_count, updated_count, duplicate_count, status
                    )
                    VALUES (:batch_id, :file_name, :sheet_name, :sheet_type, :asset_id, :project_id,
                            0, 0, 0, 'success')
                    """
                ),
                {
                    "batch_id": batch_id,
                    "file_name": file_name,
                    "sheet_name": sheet_name,
                    "sheet_type": excel_type,
                    "asset_id": target_asset_id,
                    "project_id": target_project_id,
                },
            )

            if excel_type == "Cash Summary":
                parsed_df = parse_cash_summary(df_raw, extract_entity_name(df_raw))
                inserted, updated, duplicate = import_cash_summary(
                    session, batch_id, target_asset_id, target_project_id, parsed_df
                )
            elif excel_type == "Payment Details":
                parsed_df = parse_payment_details(df_raw, extract_entity_name(df_raw))
                inserted, updated, duplicate = import_payment_details(
                    session, batch_id, target_asset_id, target_project_id, parsed_df
                )
            elif excel_type == "Budget":
                parsed_df = parse_budget(df_raw, extract_entity_name(df_raw))
                inserted, updated, duplicate = import_budget(
                    session, batch_id, target_asset_id, target_project_id, parsed_df
                )
            elif excel_type == "Projects":
                inserted, duplicate = import_projects_from_excel(session, batch_id, df_raw, target_asset_id)
            elif excel_type == "Transactions":
                inserted, duplicate = import_transactions_from_excel(
                    session, batch_id, df_raw, target_asset_id, target_project_id
                )
            elif excel_type == "Consultants":
                inserted, duplicate = import_consultants_from_excel(session, batch_id, df_raw)
            elif excel_type == "Consultant Quotes":
                inserted, duplicate = import_quotes_from_excel(session, batch_id, df_raw, target_project_id)

            session.execute(
                text(
                    """
                    UPDATE excel_import_batches
                    SET record_count = :record_count,
                        updated_count = :updated_count,
                        duplicate_count = :duplicate_count
                    WHERE batch_id = :batch_id
                    """
                ),
                {
                    "record_count": inserted,
                    "updated_count": updated,
                    "duplicate_count": duplicate,
                    "batch_id": batch_id,
                },
            )
    finally:
        db.close_session(session)

    target_page = "1_Assets"
    if excel_type == "Projects":
        target_page = "3_Projects"
    elif excel_type in {"Transactions", "Payment Details", "Cash Summary"}:
        target_page = "10_transaction_management"
    elif excel_type in {"Consultants", "Consultant Quotes", "Budget"}:
        target_page = "8_consultants"

    return {"count": inserted, "updated": updated, "duplicate": duplicate, "batch_id": batch_id, "target_page": target_page}


def reset_form_state(base_key: str):
    counter_key = f"{base_key}_counter"
    st.session_state[counter_key] = st.session_state.get(counter_key, 0) + 1


def get_form_key(base_key: str) -> str:
    counter_key = f"{base_key}_counter"
    if counter_key not in st.session_state:
        st.session_state[counter_key] = 0
    return f"{base_key}_{st.session_state[counter_key]}"


def show_success_navigation(target_page: str):
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("📊 View in Dashboard"):
            st.switch_page(f"pages/{target_page}.py")
    with col2:
        st.caption("You can continue adding more records.")


def show_quick_add_project_form():
    form_key = get_form_key("quick_add_project")
    with st.form(form_key):
        assets = get_assets()
        asset_options = {a["name"]: a["id"] for a in assets}

        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.selectbox("Asset *", ["Select Asset"] + list(asset_options.keys()))
            project_name = st.text_input("Project Name *")
            location = st.text_input("Location")

        with col2:
            status = st.selectbox("Status", ["Planning", "DA", "Construction"])
            budget = st.number_input("Budget (AUD)", min_value=0.0, step=1000.0)
            area = st.number_input("Building Area (sqm)", min_value=0.0)

        submitted = st.form_submit_button("💾 Quick Add")

    if submitted:
        if asset_name == "Select Asset" or not project_name.strip():
            st.error("Please fill in required fields.")
            return

        asset_id = asset_options.get(asset_name)
        db = get_db_connection()
        session = db.get_session()
        try:
            existing = session.query(Project).filter(
                Project.asset_id == asset_id,
                Project.project_name == project_name.strip(),
            ).first()
            if existing:
                st.warning("Duplicate project detected for this asset.")
                return

            project = Project(
                asset_id=asset_id,
                project_name=project_name.strip(),
                status=map_project_status(status),
                total_budget=budget if budget > 0 else None,
                notes=build_project_notes(location, area, None),
            )
            session.add(project)
            session.commit()
            st.success("✅ Project saved successfully.")
            show_success_navigation("3_Projects")
            reset_form_state("quick_add_project")
        except Exception as exc:
            session.rollback()
            st.error(f"Failed to save project: {exc}")
        finally:
            db.close_session(session)


def show_quick_add_transaction_form():
    form_key = get_form_key("quick_add_transaction")
    with st.form(form_key):
        assets = get_assets()
        asset_options = {a["name"]: a["id"] for a in assets}

        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.selectbox("Asset *", ["Select Asset"] + list(asset_options.keys()))
            asset_id = asset_options.get(asset_name)
            project_options = get_projects_by_asset(asset_id)
            project_map = {p["project_name"]: p["id"] for p in project_options}
            project_name = st.selectbox("Project (Optional)", ["None"] + list(project_map.keys()))
            transaction_type = st.radio("Type *", ["Income", "Expense"])
            transaction_date = st.date_input("Date *")

        with col2:
            category = st.selectbox("Category *", get_transaction_categories())
            amount = st.number_input("Amount (AUD) *", min_value=0.0, step=0.01)
            counterparty = st.text_input("Counterparty")
            invoice_number = st.text_input("Invoice Number")

        description = st.text_area("Description")
        submitted = st.form_submit_button("💾 Quick Add")

    if submitted:
        if asset_name == "Select Asset" or amount <= 0:
            st.error("Please fill in required fields.")
            return

        db = get_db_connection()
        session = db.get_session()
        try:
            project_id = project_map.get(project_name) if project_name != "None" else None
            tx_type = TransactionType.INCOME if transaction_type == "Income" else TransactionType.EXPENSE
            signed_amount = amount if tx_type == TransactionType.INCOME else -abs(amount)

            if is_duplicate_transaction(
                session,
                asset_id=asset_id,
                project_id=project_id,
                tx_date=transaction_date,
                amount=signed_amount,
                category=category,
                reference_number=invoice_number.strip() or None,
            ):
                st.warning("Duplicate transaction detected.")
                return

            tx = Transaction(
                asset_id=asset_id,
                project_id=project_id,
                transaction_date=transaction_date,
                transaction_type=tx_type,
                amount=signed_amount,
                category=category,
                description=description.strip() or category,
                reference_number=invoice_number.strip() or None,
                vendor_payee=counterparty.strip() or None,
            )
            session.add(tx)
            session.commit()
            st.success("✅ Transaction saved successfully.")
            show_success_navigation("10_transaction_management")
            reset_form_state("quick_add_transaction")
        except Exception as exc:
            session.rollback()
            st.error(f"Failed to save transaction: {exc}")
        finally:
            db.close_session(session)


def show_quick_add_consultant_form():
    form_key = get_form_key("quick_add_consultant")
    with st.form(form_key):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Consultant Name *")
            company = st.text_input("Company")
            category = st.selectbox(
                "Category *",
                [
                    "Town Planning",
                    "Architecture",
                    "Civil Engineer",
                    "QS",
                    "Surveyor",
                    "Geotechnical",
                    "Electrical",
                    "Other",
                ],
            )

        with col2:
            contact_person = st.text_input("Contact Person")
            email = st.text_input("Email *")
            phone = st.text_input("Phone")

        specialty = st.text_area("Specialty / Typical Scopes")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("💾 Quick Add")

    if submitted:
        if not name.strip() or not email.strip():
            st.error("Please fill in required fields.")
            return

        db = get_db_connection()
        ensure_consultant_schema(db)
        session = db.get_session()
        try:
            if is_duplicate_consultant(session, name.strip(), email.strip()):
                st.warning("Duplicate consultant detected.")
                return

            result = session.execute(
                text(
                    """
                    INSERT INTO consultants (
                        name, company, email, phone, specialty, notes, is_active, category, contact_person, typical_scopes
                    )
                    VALUES (
                        :name, :company, :email, :phone, :specialty, :notes, 1, :category, :contact_person, :typical_scopes
                    )
                    """
                ),
                {
                    "name": name.strip(),
                    "company": company.strip() or None,
                    "email": email.strip(),
                    "phone": phone.strip() or None,
                    "specialty": category,
                    "notes": notes.strip() or None,
                    "category": category,
                    "contact_person": contact_person.strip() or None,
                    "typical_scopes": specialty.strip() or None,
                },
            )
            session.commit()
            st.success("✅ Consultant saved successfully.")
            show_success_navigation("8_consultants")
            reset_form_state("quick_add_consultant")
        except Exception as exc:
            session.rollback()
            st.error(f"Failed to save consultant: {exc}")
        finally:
            db.close_session(session)


def show_quick_add_quote_form():
    form_key = get_form_key("quick_add_quote")
    with st.form(form_key):
        col1, col2 = st.columns(2)

        consultants = get_consultants()
        consultant_map = {c["name"]: c["id"] for c in consultants}

        projects = get_all_projects()
        project_map = {p["project_name"]: p["id"] for p in projects}

        with col1:
            consultant_name = st.selectbox("Consultant *", ["Select Consultant"] + list(consultant_map.keys()))
            project_name = st.selectbox("Project (Optional)", ["None"] + list(project_map.keys()))
            scope_of_work = st.text_area("Scope of Work *")

        with col2:
            quote_amount = st.number_input("Quote Amount (AUD) *", min_value=0.0)
            quote_date = st.date_input("Quote Date *")
            status = st.selectbox("Status", ["Quoted", "Awarded", "In Progress", "Completed"])

        submitted = st.form_submit_button("💾 Quick Add")

    if submitted:
        if consultant_name == "Select Consultant" or quote_amount <= 0 or not scope_of_work.strip():
            st.error("Please fill in required fields.")
            return

        consultant_id = consultant_map.get(consultant_name)
        project_id = project_map.get(project_name) if project_name != "None" else None

        db = get_db_connection()
        ensure_consultant_schema(db)
        session = db.get_session()
        try:
            if is_duplicate_quote(session, consultant_id, project_id, quote_date, float(quote_amount)):
                st.warning("Duplicate quote detected.")
                return

            asset_id = get_asset_id_for_project(session, project_id) if project_id else None

            session.execute(
                text(
                    """
                    INSERT INTO consultant_quotes (
                        consultant_id, asset_id, project_id, quote_date, amount, currency, status, scope, notes
                    )
                    VALUES (
                        :consultant_id, :asset_id, :project_id, :quote_date, :amount, 'AUD', :status, :scope, :notes
                    )
                    """
                ),
                {
                    "consultant_id": consultant_id,
                    "asset_id": asset_id,
                    "project_id": project_id,
                    "quote_date": quote_date,
                    "amount": float(quote_amount),
                    "status": status,
                    "scope": scope_of_work.strip(),
                    "notes": None,
                },
            )
            session.commit()
            st.success("✅ Quote saved successfully.")
            show_success_navigation("8_consultants")
            reset_form_state("quick_add_quote")
        except Exception as exc:
            session.rollback()
            st.error(f"Failed to save quote: {exc}")
        finally:
            db.close_session(session)


input_method = st.radio(
    "Choose Input Method:",
    ["📊 Excel Import", "✍️ Manual Entry"],
    horizontal=True,
)

st.divider()

db = get_db_connection()
ensure_excel_import_tables(db)
ensure_consultant_schema(db)

if input_method == "📊 Excel Import":
    st.header("📊 Excel Batch Import")

    uploaded_file = st.file_uploader(
        "Upload Excel file (.xlsx)",
        type=["xlsx"],
        help="Supports: Cash Summary, Payment Details, Budget, Projects, Transactions, Consultants, Quotes",
    )

    if uploaded_file:
        try:
            file_bytes = uploaded_file.getvalue()
            excel_file = pd.ExcelFile(BytesIO(file_bytes))
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info(f"📑 Found {len(excel_file.sheet_names)} sheets: {', '.join(excel_file.sheet_names)}")

            selected_sheet = st.selectbox("Select sheet to import:", excel_file.sheet_names)
            raw_df = pd.read_excel(BytesIO(file_bytes), sheet_name=selected_sheet, header=None)

            excel_type = detect_excel_type(raw_df, selected_sheet)
            st.write(f"**Detected Type:** {excel_type}")

            with st.expander("📋 Preview Data", expanded=True):
                st.dataframe(raw_df.head(20), use_container_width=True)

            if excel_type == "Unknown":
                excel_type = st.selectbox(
                    "Manual override type",
                    [
                        "Cash Summary",
                        "Payment Details",
                        "Budget",
                        "Projects",
                        "Transactions",
                        "Consultants",
                        "Consultant Quotes",
                    ],
                )

            st.subheader("Import Settings")
            assets = get_assets()
            asset_map = {a["name"]: a["id"] for a in assets}

            col1, col2 = st.columns(2)
            with col1:
                asset_name = st.selectbox("Link to Asset (if needed):", ["None"] + list(asset_map.keys()))
                target_asset_id = asset_map.get(asset_name) if asset_name != "None" else None

            with col2:
                project_map = {p["project_name"]: p["id"] for p in get_all_projects()}
                project_name = st.selectbox("Link to Project (Optional):", ["None"] + list(project_map.keys()))
                target_project_id = project_map.get(project_name) if project_name != "None" else None

            if st.button("✅ Confirm Import", type="primary", use_container_width=True):
                with st.spinner("Importing data..."):
                    try:
                        result = import_data(
                            raw_df,
                            excel_type,
                            target_asset_id,
                            target_project_id,
                            uploaded_file.name,
                            selected_sheet,
                        )
                        st.success(f"🎉 Successfully imported {result['count']} records!")
                        if result["updated"]:
                            st.info(f"Updated: {result['updated']} | Duplicates: {result['duplicate']}")
                        elif result["duplicate"]:
                            st.info(f"Duplicates skipped: {result['duplicate']}")

                        show_success_navigation(result["target_page"])
                    except Exception as exc:
                        st.error(f"❌ Import failed: {exc}")

        except Exception as exc:
            st.error(f"❌ Error reading file: {exc}")

else:
    st.header("✍️ Quick Manual Entry")

    data_type = st.selectbox(
        "What do you want to add?",
        ["🏗️ New Project", "💰 New Transaction", "👤 New Consultant", "📝 New Quote"],
    )

    st.divider()

    if data_type == "🏗️ New Project":
        show_quick_add_project_form()
    elif data_type == "💰 New Transaction":
        show_quick_add_transaction_form()
    elif data_type == "👤 New Consultant":
        show_quick_add_consultant_form()
    elif data_type == "📝 New Quote":
        show_quick_add_quote_form()


st.divider()
with st.expander("📜 Recent Import History"):
    with db.engine.begin() as conn:
        history = pd.read_sql(
            "SELECT batch_id, file_name, sheet_name, sheet_type, record_count, updated_count, duplicate_count, status, created_at "
            "FROM excel_import_batches ORDER BY created_at DESC LIMIT 10",
            conn,
        )

    if not history.empty:
        st.dataframe(history, use_container_width=True)
    else:
        st.info("No import history yet.")
