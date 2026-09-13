# -*- coding: utf-8 -*-
"""SQLite cho GĐ1-05, dùng cùng schema với GĐ1-04."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BASE_DIR / "runtime" / "gd1_05.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
EMPLOYEE_DATA_PATH = BASE_DIR / "data" / "nhan_vien_chuan.csv"
RULE_DATA_PATH = BASE_DIR / "data" / "business_rules_mock.csv"


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path or DEFAULT_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def load_employees(conn: sqlite3.Connection, csv_path: str | Path = EMPLOYEE_DATA_PATH) -> int:
    path = Path(csv_path)
    if not path.exists():
        return 0

    count = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            ma = (row.get("ma_nhan_vien") or "").strip()
            ho_ten = (row.get("ho_ten") or "").strip()
            if not ma or not ho_ten:
                continue
            rows.append(
                (
                    ma,
                    ho_ten,
                    (row.get("ho_ten_chuan") or "").strip(),
                    (row.get("don_vi") or "").strip() or None,
                    (row.get("chuc_vu") or "").strip() or None,
                    (row.get("email") or "").strip() or None,
                )
            )
            if len(rows) >= 5000:
                conn.executemany(
                    """
                    INSERT OR IGNORE INTO nhan_vien
                    (ma_nhan_vien, ho_ten, ho_ten_chuan, don_vi, chuc_vu, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    rows,
                )
                count += len(rows)
                rows.clear()
        if rows:
            conn.executemany(
                """
                INSERT OR IGNORE INTO nhan_vien
                (ma_nhan_vien, ho_ten, ho_ten_chuan, don_vi, chuc_vu, email)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            count += len(rows)
    conn.commit()
    return count


def _to_int(value: Optional[str], default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def load_rules(conn: sqlite3.Connection, csv_path: str | Path = RULE_DATA_PATH) -> int:
    path = Path(csv_path)
    if not path.exists():
        return 0

    count = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ma = (row.get("ma_quy_tac") or "").strip()
            ket_qua = (row.get("ket_qua") or "").strip().upper()
            can_cu = (row.get("can_cu") or "").strip()
            if not ma or ket_qua not in {"YES", "NO"} or not can_cu:
                continue
            conn.execute(
                """
                INSERT OR IGNORE INTO business_rule
                (ma_quy_tac, ten_quy_tac, ten_don_vi, loai_don_vi, pham_vi,
                 ket_qua, can_cu, muc_uu_tien, ngay_hieu_luc, ngay_het_hieu_luc,
                 dang_ap_dung, la_mock, ghi_chu)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ma,
                    (row.get("ten_quy_tac") or "").strip() or None,
                    (row.get("ten_don_vi") or "").strip() or None,
                    (row.get("loai_don_vi") or "").strip() or None,
                    (row.get("pham_vi") or "DON_VI").strip(),
                    ket_qua,
                    can_cu,
                    _to_int(row.get("muc_uu_tien"), 0),
                    (row.get("ngay_hieu_luc") or "").strip() or None,
                    (row.get("ngay_het_hieu_luc") or "").strip() or None,
                    _to_int(row.get("dang_ap_dung"), 1),
                    _to_int(row.get("la_mock"), 1),
                    (row.get("ghi_chu") or "").strip() or None,
                ),
            )
            count += 1
    conn.commit()
    return count


def ensure_database(db_path: str | Path | None = None, seed: bool = True) -> sqlite3.Connection:
    conn = get_connection(db_path)
    init_schema(conn)
    if seed:
        if conn.execute("SELECT COUNT(*) FROM nhan_vien").fetchone()[0] == 0:
            load_employees(conn)
        if conn.execute("SELECT COUNT(*) FROM business_rule").fetchone()[0] == 0:
            load_rules(conn)
    return conn
