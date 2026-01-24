"""
Database Migration Script: v1 -> v2

- Creates a backup of the existing database
- Builds a new database using schema_v2.sql
- Migrates projects and transactions
- Creates assets from "Related Asset" when needed
- Validates record counts and foreign keys
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def normalize_col(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def quote_ident(name: str) -> str:
    return f"\"{name.replace('\"', '\"\"')}\""


def get_table_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    rows = conn.execute(f"PRAGMA table_info({quote_ident(table_name)});").fetchall()
    return [row[1] for row in rows]


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table_name,),
    ).fetchone()
    return row is not None


def find_column(columns: List[str], candidates: List[str]) -> Optional[str]:
    normalized = {normalize_col(col): col for col in columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    return None


def load_schema(schema_path: Path) -> str:
    with schema_path.open("r", encoding="utf-8") as handle:
        return handle.read()


def init_target_db(target_path: Path, schema_sql: str) -> sqlite3.Connection:
    if target_path.exists():
        target_path.unlink()
    conn = sqlite3.connect(str(target_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema_sql)
    conn.commit()
    return conn


def copy_assets_from_source(
    src_conn: sqlite3.Connection,
    dst_conn: sqlite3.Connection,
) -> Dict[int, int]:
    if not table_exists(src_conn, "assets"):
        return {}

    src_columns = get_table_columns(src_conn, "assets")
    dst_columns = get_table_columns(dst_conn, "assets")
    columns_to_copy = [col for col in dst_columns if col in src_columns]

    if not columns_to_copy:
        return {}

    select_sql = f"SELECT {', '.join(quote_ident(c) for c in columns_to_copy)} FROM assets;"
    rows = src_conn.execute(select_sql).fetchall()

    insert_sql = f"""
        INSERT INTO assets ({', '.join(quote_ident(c) for c in columns_to_copy)})
        VALUES ({', '.join(['?'] * len(columns_to_copy))});
    """

    for row in rows:
        dst_conn.execute(insert_sql, row)

    dst_conn.commit()

    if "id" not in columns_to_copy:
        return {}

    id_index = columns_to_copy.index("id")
    return {row[id_index]: row[id_index] for row in rows}


def create_assets_from_projects(
    src_conn: sqlite3.Connection,
    dst_conn: sqlite3.Connection,
    related_asset_col: str,
) -> Dict[str, int]:
    asset_map: Dict[str, int] = {}
    select_sql = f"""
        SELECT DISTINCT {quote_ident(related_asset_col)}
        FROM projects
        WHERE {quote_ident(related_asset_col)} IS NOT NULL
          AND TRIM({quote_ident(related_asset_col)}) <> '';
    """
    rows = src_conn.execute(select_sql).fetchall()
    for (asset_name,) in rows:
        if asset_name in asset_map:
            continue
        cursor = dst_conn.execute(
            "INSERT INTO assets (name) VALUES (?);",
            (asset_name,),
        )
        asset_map[asset_name] = cursor.lastrowid
    dst_conn.commit()
    return asset_map


def migrate_projects(
    src_conn: sqlite3.Connection,
    dst_conn: sqlite3.Connection,
    asset_name_map: Dict[str, int],
    asset_id_map: Dict[int, int],
) -> Dict[str, int]:
    src_columns = get_table_columns(src_conn, "projects")
    dst_columns = get_table_columns(dst_conn, "projects")

    src_asset_id_col = find_column(src_columns, ["asset_id"])
    related_asset_col = find_column(
        src_columns,
        ["related_asset", "relatedasset", "asset_name", "related_asset_name"],
    )
    src_by_normalized = {normalize_col(col): col for col in src_columns}
    project_name_col = find_column(src_columns, ["project_name", "project", "name"])
    project_code_col = find_column(src_columns, ["project_code", "code"])

    rows = src_conn.execute("SELECT * FROM projects;").fetchall()

    project_name_map: Dict[str, int] = {}
    project_code_map: Dict[str, int] = {}

    for row in rows:
        row_data = {}
        row_dict = dict(row)

        for col in dst_columns:
            if col == "asset_id":
                asset_id = None
                if src_asset_id_col and row_dict.get(src_asset_id_col) is not None:
                    asset_id = asset_id_map.get(row_dict[src_asset_id_col], row_dict[src_asset_id_col])
                elif related_asset_col:
                    asset_name = row_dict.get(related_asset_col)
                    if asset_name:
                        asset_id = asset_name_map.get(asset_name)
                row_data[col] = asset_id
            elif col in src_columns:
                row_data[col] = row_dict.get(col)
            else:
                normalized = normalize_col(col)
                src_match = src_by_normalized.get(normalized)
                if src_match:
                    row_data[col] = row_dict.get(src_match)

        insert_cols = [col for col in row_data.keys() if col in dst_columns]
        insert_sql = f"""
            INSERT INTO projects ({', '.join(quote_ident(c) for c in insert_cols)})
            VALUES ({', '.join(['?'] * len(insert_cols))});
        """
        dst_conn.execute(insert_sql, [row_data[col] for col in insert_cols])

        if project_name_col and row_dict.get(project_name_col):
            project_name_map[row_dict[project_name_col]] = row_dict.get("id")
        if project_code_col and row_dict.get(project_code_col):
            project_code_map[row_dict[project_code_col]] = row_dict.get("id")

    dst_conn.commit()

    # Combine maps, giving priority to project_name
    combined_map = {**project_code_map, **project_name_map}
    return combined_map


def migrate_transactions(
    src_conn: sqlite3.Connection,
    dst_conn: sqlite3.Connection,
    asset_name_map: Dict[str, int],
    asset_id_map: Dict[int, int],
    project_lookup: Dict[str, int],
) -> None:
    src_columns = get_table_columns(src_conn, "transactions")
    dst_columns = get_table_columns(dst_conn, "transactions")

    src_asset_id_col = find_column(src_columns, ["asset_id"])
    src_project_id_col = find_column(src_columns, ["project_id"])
    related_asset_col = find_column(
        src_columns,
        ["related_asset", "relatedasset", "asset_name", "related_asset_name"],
    )
    project_name_col = find_column(
        src_columns,
        ["project_name", "project", "project_code"],
    )
    src_by_normalized = {normalize_col(col): col for col in src_columns}

    rows = src_conn.execute("SELECT * FROM transactions;").fetchall()

    for row in rows:
        row_dict = dict(row)
        row_data = {}

        for col in dst_columns:
            if col == "asset_id":
                asset_id = None
                if src_asset_id_col and row_dict.get(src_asset_id_col) is not None:
                    asset_id = asset_id_map.get(row_dict[src_asset_id_col], row_dict[src_asset_id_col])
                elif related_asset_col:
                    asset_name = row_dict.get(related_asset_col)
                    if asset_name:
                        asset_id = asset_name_map.get(asset_name)
                row_data[col] = asset_id
            elif col == "project_id":
                project_id = None
                if src_project_id_col and row_dict.get(src_project_id_col) is not None:
                    project_id = row_dict.get(src_project_id_col)
                elif project_name_col:
                    project_key = row_dict.get(project_name_col)
                    if project_key:
                        project_id = project_lookup.get(project_key)
                row_data[col] = project_id
            elif col in src_columns:
                row_data[col] = row_dict.get(col)
            else:
                normalized = normalize_col(col)
                src_match = src_by_normalized.get(normalized)
                if src_match:
                    row_data[col] = row_dict.get(src_match)

        if "currency" in dst_columns and "currency" not in row_data:
            row_data["currency"] = "AUD"

        insert_cols = [col for col in row_data.keys() if col in dst_columns]
        insert_sql = f"""
            INSERT INTO transactions ({', '.join(quote_ident(c) for c in insert_cols)})
            VALUES ({', '.join(['?'] * len(insert_cols))});
        """
        dst_conn.execute(insert_sql, [row_data[col] for col in insert_cols])

    dst_conn.commit()


def validate_migration(src_conn: sqlite3.Connection, dst_conn: sqlite3.Connection) -> None:
    src_projects = src_conn.execute("SELECT COUNT(*) FROM projects;").fetchone()[0]
    src_transactions = src_conn.execute("SELECT COUNT(*) FROM transactions;").fetchone()[0]

    dst_projects = dst_conn.execute("SELECT COUNT(*) FROM projects;").fetchone()[0]
    dst_transactions = dst_conn.execute("SELECT COUNT(*) FROM transactions;").fetchone()[0]

    if src_projects != dst_projects:
        raise RuntimeError(f"Project count mismatch: {src_projects} -> {dst_projects}")
    if src_transactions != dst_transactions:
        raise RuntimeError(f"Transaction count mismatch: {src_transactions} -> {dst_transactions}")

    orphan_projects = dst_conn.execute("""
        SELECT COUNT(*) FROM projects
        WHERE asset_id IS NOT NULL
          AND asset_id NOT IN (SELECT id FROM assets);
    """).fetchone()[0]
    if orphan_projects:
        raise RuntimeError(f"Found {orphan_projects} projects with missing assets")

    orphan_transactions = dst_conn.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE project_id IS NOT NULL
          AND project_id NOT IN (SELECT id FROM projects);
    """).fetchone()[0]
    if orphan_transactions:
        raise RuntimeError(f"Found {orphan_transactions} transactions with missing projects")

    orphan_transaction_assets = dst_conn.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE asset_id IS NOT NULL
          AND asset_id NOT IN (SELECT id FROM assets);
    """).fetchone()[0]
    if orphan_transaction_assets:
        raise RuntimeError(f"Found {orphan_transaction_assets} transactions with missing assets")


def migrate_database(source_db: Path, output_db: Optional[Path], replace: bool) -> Path:
    if not source_db.exists():
        raise FileNotFoundError(f"Source database not found: {source_db}")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = source_db.with_suffix(source_db.suffix + f".backup.{timestamp}")
    shutil.copy2(source_db, backup_path)

    schema_path = Path(__file__).parent / "schema_v2.sql"
    schema_sql = load_schema(schema_path)

    temp_target = source_db.with_suffix(source_db.suffix + ".v2.tmp")
    src_conn = sqlite3.connect(str(source_db))
    src_conn.row_factory = sqlite3.Row
    dst_conn = init_target_db(temp_target, schema_sql)

    try:
        if not table_exists(src_conn, "projects") or not table_exists(src_conn, "transactions"):
            raise RuntimeError("Source database must contain projects and transactions tables")

        asset_id_map = copy_assets_from_source(src_conn, dst_conn)

        related_asset_col = None
        if not asset_id_map:
            project_columns = get_table_columns(src_conn, "projects")
            related_asset_col = find_column(
                project_columns,
                ["related_asset", "relatedasset", "asset_name", "related_asset_name"],
            )
        asset_name_map: Dict[str, int] = {}
        if related_asset_col:
            asset_name_map = create_assets_from_projects(src_conn, dst_conn, related_asset_col)

        project_lookup = migrate_projects(src_conn, dst_conn, asset_name_map, asset_id_map)
        migrate_transactions(src_conn, dst_conn, asset_name_map, asset_id_map, project_lookup)

        validate_migration(src_conn, dst_conn)

        dst_conn.close()
        src_conn.close()

        if not replace:
            if output_db is None:
                output_db = source_db.with_name(f"{source_db.stem}_v2{source_db.suffix}")
            if output_db.exists():
                output_db.unlink()
            shutil.move(temp_target, output_db)
            return output_db

        if replace:
            os.replace(temp_target, source_db)
            return source_db

    except Exception:
        dst_conn.close()
        src_conn.close()
        if temp_target.exists():
            temp_target.unlink()
        shutil.copy2(backup_path, source_db)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate database from v1 to v2.")
    parser.add_argument(
        "--source",
        type=str,
        default="industrial_real_estate.db",
        help="Source SQLite database path",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output database path (used when --replace is false)",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace source database after successful migration",
    )

    args = parser.parse_args()
    source_db = Path(args.source).resolve()
    output_db = Path(args.output).resolve() if args.output else None

    print("=" * 70)
    print("Migration: v1 -> v2")
    print("=" * 70)
    print(f"Source DB: {source_db}")
    if output_db:
        print(f"Output DB: {output_db}")
    print(f"Replace source: {'YES' if args.replace else 'NO'}")

    result_path = migrate_database(source_db, output_db, args.replace)
    print("\n✅ Migration completed successfully!")
    print(f"Result DB: {result_path}")


if __name__ == "__main__":
    main()
