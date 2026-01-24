"""
Consultant database utilities.
Handles CRUD operations, quote history, and recommendation logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

import numpy as np
from sqlalchemy import text

from models.database import DatabaseManager


CONSULTANT_COLUMNS = {
    "category": "TEXT",
    "contact_person": "TEXT",
    "address": "TEXT",
    "typical_scopes": "TEXT",
    "quality_rating": "INTEGER",
    "reliability_rating": "INTEGER",
    "cost_competitiveness": "INTEGER",
    "strengths": "TEXT",
    "weaknesses": "TEXT",
    "general_notes": "TEXT",
}

QUOTE_COLUMNS = {
    "project_type": "TEXT",
    "project_size": "FLOAT",
    "scope_of_work": "TEXT",
    "deliverables": "TEXT",
    "quote_amount": "NUMERIC(15,2)",
    "actual_amount": "NUMERIC(15,2)",
    "actual_start_date": "DATE",
    "actual_completion_date": "DATE",
    "service_quality_score": "INTEGER",
    "on_time_delivery": "BOOLEAN",
    "met_scope": "BOOLEAN",
    "lessons_learned": "TEXT",
}


def ensure_consultant_schema(db: DatabaseManager) -> None:
    """Ensure consultant tables and columns exist."""
    create_statements = [
        """
        CREATE TABLE IF NOT EXISTS consultants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            email TEXT,
            phone TEXT,
            specialty TEXT,
            notes TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS consultant_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultant_id INTEGER NOT NULL,
            asset_id INTEGER,
            project_id INTEGER,
            quote_date DATE,
            valid_until DATE,
            amount NUMERIC(15, 2),
            currency TEXT NOT NULL DEFAULT 'AUD',
            status TEXT,
            scope TEXT,
            notes TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ]
    with db.engine.begin() as conn:
        for stmt in create_statements:
            conn.execute(text(stmt))

        existing_cols = {
            row["name"] for row in conn.execute(text("PRAGMA table_info(consultants)")).mappings()
        }
        for col, col_type in CONSULTANT_COLUMNS.items():
            if col not in existing_cols:
                conn.execute(text(f"ALTER TABLE consultants ADD COLUMN {col} {col_type}"))

        quote_cols = {
            row["name"] for row in conn.execute(text("PRAGMA table_info(consultant_quotes)")).mappings()
        }
        for col, col_type in QUOTE_COLUMNS.items():
            if col not in quote_cols:
                conn.execute(text(f"ALTER TABLE consultant_quotes ADD COLUMN {col} {col_type}"))


def get_all_consultants(category_filter: Optional[str] = None, active_only: bool = True) -> List[Dict]:
    db = DatabaseManager("sqlite:///industrial_real_estate.db")
    ensure_consultant_schema(db)
    where = []
    params = {}
    if active_only:
        where.append("is_active = 1")
    if category_filter and category_filter != "All":
        where.append("category = :category")
        params["category"] = category_filter
    where_clause = f"WHERE {' AND '.join(where)}" if where else ""
    with db.engine.begin() as conn:
        rows = conn.execute(
            text(f"SELECT * FROM consultants {where_clause} ORDER BY name"),
            params,
        ).mappings()
        return [dict(row) for row in rows]


def add_consultant(data_dict: Dict) -> int:
    db = DatabaseManager("sqlite:///industrial_real_estate.db")
    ensure_consultant_schema(db)
    columns = ", ".join(data_dict.keys())
    values = ", ".join(f":{k}" for k in data_dict.keys())
    with db.engine.begin() as conn:
        result = conn.execute(
            text(f"INSERT INTO consultants ({columns}) VALUES ({values})"),
            data_dict,
        )
        return result.lastrowid


def update_consultant(consultant_id: int, data_dict: Dict) -> None:
    db = DatabaseManager("sqlite:///industrial_real_estate.db")
    ensure_consultant_schema(db)
    assignments = ", ".join(f"{k} = :{k}" for k in data_dict.keys())
    data_dict["consultant_id"] = consultant_id
    with db.engine.begin() as conn:
        conn.execute(
            text(f"UPDATE consultants SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = :consultant_id"),
            data_dict,
        )


def delete_consultant(consultant_id: int) -> None:
    db = DatabaseManager("sqlite:///industrial_real_estate.db")
    ensure_consultant_schema(db)
    with db.engine.begin() as conn:
        conn.execute(
            text("UPDATE consultants SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
            {"id": consultant_id},
        )


def get_consultant_quotes(consultant_id: int) -> List[Dict]:
    db = DatabaseManager("sqlite:///industrial_real_estate.db")
    ensure_consultant_schema(db)
    with db.engine.begin() as conn:
        rows = conn.execute(
            text("SELECT * FROM consultant_quotes WHERE consultant_id = :id ORDER BY quote_date DESC"),
            {"id": consultant_id},
        ).mappings()
        return [dict(row) for row in rows]


def add_quote(data_dict: Dict) -> int:
    db = DatabaseManager("sqlite:///industrial_real_estate.db")
    ensure_consultant_schema(db)
    columns = ", ".join(data_dict.keys())
    values = ", ".join(f":{k}" for k in data_dict.keys())
    with db.engine.begin() as conn:
        result = conn.execute(
            text(f"INSERT INTO consultant_quotes ({columns}) VALUES ({values})"),
            data_dict,
        )
        return result.lastrowid


def get_quote_history(project_id: Optional[int] = None, consultant_id: Optional[int] = None) -> List[Dict]:
    db = DatabaseManager("sqlite:///industrial_real_estate.db")
    ensure_consultant_schema(db)
    where = []
    params = {}
    if project_id:
        where.append("project_id = :project_id")
        params["project_id"] = project_id
    if consultant_id:
        where.append("consultant_id = :consultant_id")
        params["consultant_id"] = consultant_id
    where_clause = f"WHERE {' AND '.join(where)}" if where else ""
    with db.engine.begin() as conn:
        rows = conn.execute(
            text(
                f"""
                SELECT cq.*, c.name AS consultant_name, p.project_name
                FROM consultant_quotes cq
                LEFT JOIN consultants c ON cq.consultant_id = c.id
                LEFT JOIN projects p ON cq.project_id = p.id
                {where_clause}
                ORDER BY cq.quote_date DESC
                """
            ),
            params,
        ).mappings()
        return [dict(row) for row in rows]


def calculate_scope_match(consultant_scopes_json: str, required_scopes_list: List[str]) -> Dict:
    consultant_scopes = json.loads(consultant_scopes_json or "[]")
    matched = []
    unmatched = []

    for req_scope in required_scopes_list:
        best_match = None
        best_score = 0.0
        for cons_scope in consultant_scopes:
            score = SequenceMatcher(None, req_scope.lower(), str(cons_scope).lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = cons_scope
        if best_score > 0.6:
            matched.append((req_scope, best_match, best_score))
        else:
            unmatched.append(req_scope)

    match_rate = len(matched) / len(required_scopes_list) if required_scopes_list else 0
    return {"match_rate": match_rate, "matched": matched, "unmatched": unmatched}


def estimate_price(consultant_id: int, project_size: float, project_type: Optional[str]) -> Tuple[Optional[float], Optional[float], int]:
    db = DatabaseManager("sqlite:///industrial_real_estate.db")
    ensure_consultant_schema(db)
    with db.engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT project_size, COALESCE(quote_amount, amount) AS quote_amount, project_type
                FROM consultant_quotes
                WHERE consultant_id = :cid AND COALESCE(quote_amount, amount) IS NOT NULL
                """
            ),
            {"cid": consultant_id},
        ).mappings()
        data = []
        for row in rows:
            size = row["project_size"]
            amount = row["quote_amount"]
            if size and amount and (project_type is None or row["project_type"] == project_type):
                data.append((float(size), float(amount)))

        if len(data) < 2:
            return None, None, len(data)

        sizes = np.array([d[0] for d in data])
        amounts = np.array([d[1] for d in data])
        slope, intercept = np.polyfit(sizes, amounts, 1)
        estimate = intercept + slope * project_size
        low = estimate * 0.9
        high = estimate * 1.1
        return float(low), float(high), len(data)


def recommend_consultants(
    category: str,
    project_size: float,
    required_scopes: List[str],
    project_type: Optional[str],
) -> List[Dict]:
    consultants = get_all_consultants(category_filter=category, active_only=True)
    recommendations = []

    for consultant in consultants:
        scope_match = calculate_scope_match(consultant.get("typical_scopes") or "[]", required_scopes)
        scope_match_score = scope_match["match_rate"]

        quality_rating = float(consultant.get("quality_rating") or 0) / 5.0
        reliability_rating = float(consultant.get("reliability_rating") or 0) / 5.0
        cost_competitiveness = float(consultant.get("cost_competitiveness") or 0) / 5.0

        low_est, high_est, history_count = estimate_price(consultant["id"], project_size, project_type)
        has_history = history_count > 0

        score = (
            scope_match_score * 0.35
            + quality_rating * 0.25
            + cost_competitiveness * 0.20
            + reliability_rating * 0.15
            + (0.05 if has_history else 0.0)
        )

        recommendations.append(
            {
                "consultant": consultant,
                "score": round(score * 5, 2),
                "scope_match": scope_match,
                "price_estimate": (low_est, high_est, history_count),
            }
        )

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:5]
