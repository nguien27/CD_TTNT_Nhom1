# -*- coding: utf-8 -*-
"""SQLite demo cho GĐ1-04.

Schema bám theo kiến trúc hiện tại của nhóm:
- nhan_vien: chỉ lưu thông tin nhân viên, KHÔNG lưu YES/NO.
- business_rule: lưu quy tắc nghiệp vụ theo đơn vị/loại đơn vị.
- ngoai_le_ca_nhan: quy tắc ngoại lệ riêng cho cá nhân nếu có.

Dữ liệu trong file này chỉ là MOCK để thử nghiệm GĐ1.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("gd1_04_demo.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS nhan_vien (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nhan_vien    TEXT UNIQUE NOT NULL,
    ho_ten          TEXT NOT NULL,
    ho_ten_chuan    TEXT,
    don_vi          TEXT,
    chuc_vu         TEXT,
    email           TEXT
);

CREATE TABLE IF NOT EXISTS business_rule (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_quy_tac          TEXT UNIQUE NOT NULL,
    ten_quy_tac         TEXT,
    ten_don_vi          TEXT,
    loai_don_vi         TEXT,
    pham_vi             TEXT,
    ket_qua             TEXT NOT NULL CHECK (ket_qua IN ('YES', 'NO')),
    can_cu              TEXT NOT NULL,
    muc_uu_tien         INTEGER NOT NULL DEFAULT 0,
    ngay_hieu_luc       TEXT,
    ngay_het_hieu_luc   TEXT,
    dang_ap_dung        INTEGER NOT NULL DEFAULT 1,
    la_mock             INTEGER NOT NULL DEFAULT 1,
    ghi_chu             TEXT
);

CREATE TABLE IF NOT EXISTS ngoai_le_ca_nhan (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nhan_vien        TEXT NOT NULL,
    ket_qua             TEXT NOT NULL CHECK (ket_qua IN ('YES', 'NO')),
    can_cu              TEXT NOT NULL,
    muc_uu_tien         INTEGER NOT NULL DEFAULT 100,
    ngay_hieu_luc       TEXT,
    ngay_het_hieu_luc   TEXT,
    dang_ap_dung        INTEGER NOT NULL DEFAULT 1,
    la_mock             INTEGER NOT NULL DEFAULT 1,
    ghi_chu             TEXT
);

CREATE INDEX IF NOT EXISTS idx_nhan_vien_msnv ON nhan_vien(ma_nhan_vien);
CREATE INDEX IF NOT EXISTS idx_nhan_vien_ho_ten ON nhan_vien(ho_ten);
CREATE INDEX IF NOT EXISTS idx_nhan_vien_don_vi ON nhan_vien(don_vi);
CREATE INDEX IF NOT EXISTS idx_rule_ten_don_vi ON business_rule(ten_don_vi);
CREATE INDEX IF NOT EXISTS idx_rule_loai_don_vi ON business_rule(loai_don_vi);
"""


def get_connection(db_path: str | os.PathLike | None = None) -> sqlite3.Connection:
    duong_dan = str(db_path or DB_PATH)
    conn = sqlite3.connect(duong_dan)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def seed_mock_data(conn: sqlite3.Connection) -> None:
    """Seed dữ liệu giả lập để chạy demo và unit test."""
    nhan_vien = [
        ("NV001", "Nguyễn Văn An", "nguyen van an", "Trung tâm Công nghệ thông tin", "Chuyên viên", "nv001@example.com"),
        ("NV002", "Trần Thị Bình", "tran thi binh", "Trung tâm Công nghệ thông tin", "Chuyên viên", "nv002@example.com"),
        ("NV003", "Lê Văn Cường", "le van cuong", "Công ty TNHH Dịch vụ Thương mại ABC", "Nhân viên", "nv003@example.com"),
        ("NV004", "Phạm Thị Dung", "pham thi dung", "Phòng Nội vụ Quận 1", "Chuyên viên", "nv004@example.com"),
        ("NV005", "Nguyễn Văn Được", "nguyen van duoc", "Hội Chữ thập đỏ Phường X", "Nhân viên", "nv005@example.com"),
        ("NV006", "Hoàng Minh Em", "hoang minh em", "Ban Quản lý Dự án Đầu tư Công", "Chuyên viên", "nv006@example.com"),
        ("NV007", "Đỗ Thị Phương", "do thi phuong", None, "Chuyên viên", "nv007@example.com"),
    ]
    conn.executemany(
        """
        INSERT OR IGNORE INTO nhan_vien
            (ma_nhan_vien, ho_ten, ho_ten_chuan, don_vi, chuc_vu, email)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        nhan_vien,
    )

    rules = [
        (
            "R01", "Trung tâm CNTT", "Trung tâm Công nghệ thông tin", "DON_VI_SU_NGHIEP",
            "DON_VI", "YES", "Quy tắc giả lập R01", 50,
            "2025-01-01", None, 1, 1,
            "MOCK: đơn vị thuộc phạm vi chi trả trong bộ quy tắc demo."
        ),
        (
            "R02", "Doanh nghiệp tư nhân", "Công ty TNHH Dịch vụ Thương mại ABC", "DOANH_NGHIEP_TU_NHAN",
            "DON_VI", "NO", "Quy tắc giả lập R02", 50,
            "2025-01-01", None, 1, 1,
            "MOCK: đơn vị không thuộc phạm vi chi trả trong bộ quy tắc demo."
        ),
        (
            "R03", "Phòng Nội vụ", "Phòng Nội vụ Quận 1", "CO_QUAN_NHA_NUOC",
            "DON_VI", "YES", "Quy tắc giả lập R03", 50,
            "2025-01-01", None, 1, 1,
            "MOCK: cơ quan nhà nước thuộc phạm vi chi trả trong bộ quy tắc demo."
        ),
        (
            "R04", "Ban Quản lý dự án", "Ban Quản lý Dự án Đầu tư Công", "DON_VI_SU_NGHIEP",
            "DON_VI", "YES", "Quy tắc giả lập R04", 50,
            "2025-01-01", None, 1, 1,
            "MOCK: đơn vị thuộc phạm vi chi trả trong bộ quy tắc demo."
        ),
        # Không tạo rule cho Hội Chữ thập đỏ Phường X để demo CHUA_XAC_DINH.
        # Rule hết hiệu lực để kiểm tra engine phải bỏ qua.
        (
            "R_OLD", "Rule cũ đã hết hạn", "Trung tâm Công nghệ thông tin", "DON_VI_SU_NGHIEP",
            "DON_VI", "NO", "Quy tắc cũ đã hết hiệu lực", 999,
            "2020-01-01", "2020-12-31", 1, 1,
            "Không được áp dụng vì đã hết hiệu lực."
        ),
    ]
    conn.executemany(
        """
        INSERT OR IGNORE INTO business_rule
            (ma_quy_tac, ten_quy_tac, ten_don_vi, loai_don_vi, pham_vi,
             ket_qua, can_cu, muc_uu_tien, ngay_hieu_luc, ngay_het_hieu_luc,
             dang_ap_dung, la_mock, ghi_chu)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rules,
    )

    conn.execute(
        """
        INSERT INTO ngoai_le_ca_nhan
            (ma_nhan_vien, ket_qua, can_cu, muc_uu_tien,
             ngay_hieu_luc, ngay_het_hieu_luc, dang_ap_dung, la_mock, ghi_chu)
        SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM ngoai_le_ca_nhan WHERE ma_nhan_vien = ?
        )
        """,
        (
            "NV003", "YES", "Ngoại lệ cá nhân giả lập EX01", 100,
            "2025-01-01", None, 1, 1,
            "MOCK: ngoại lệ cá nhân được ưu tiên hơn rule của đơn vị.",
            "NV003",
        ),
    )
    conn.commit()


def tao_db_demo(db_path: str | os.PathLike | None = None, reset: bool = True) -> sqlite3.Connection:
    duong_dan = Path(db_path or DB_PATH)
    if reset and duong_dan.exists():
        duong_dan.unlink()
    conn = get_connection(duong_dan)
    init_schema(conn)
    seed_mock_data(conn)
    return conn


if __name__ == "__main__":
    conn = tao_db_demo()
    print(f"Đã tạo DB demo: {DB_PATH}")
    print("- nhan_vien:", conn.execute("SELECT COUNT(*) FROM nhan_vien").fetchone()[0])
    print("- business_rule:", conn.execute("SELECT COUNT(*) FROM business_rule").fetchone()[0])
    print("- ngoai_le_ca_nhan:", conn.execute("SELECT COUNT(*) FROM ngoai_le_ca_nhan").fetchone()[0])
    conn.close()
