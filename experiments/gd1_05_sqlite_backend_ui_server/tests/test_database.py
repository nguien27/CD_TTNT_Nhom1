# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from app.database import ensure_database

ROOT = Path(__file__).resolve().parents[1]


class TestDatabase(unittest.TestCase):
    def test_schema_matches_gd1_04(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            conn = ensure_database(db, seed=False)
            try:
                tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertIn("nhan_vien", tables)
                self.assertIn("business_rule", tables)
                self.assertIn("ngoai_le_ca_nhan", tables)
                self.assertNotIn("don_vi", tables)

                columns = {r[1] for r in conn.execute("PRAGMA table_info(nhan_vien)")}
                self.assertNotIn("ma_don_vi", columns)
                self.assertNotIn("ket_qua", columns)
                self.assertIn("don_vi", columns)
            finally:
                conn.close()

    def test_contributed_employee_data_preserved(self):
        path = ROOT / "data" / "nhan_vien_chuan.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            count = sum(1 for _ in csv.DictReader(f))
        self.assertEqual(count, 100000)

    def test_unit_file_has_no_payroll_result(self):
        path = ROOT / "data" / "don_vi_nguon.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            headers = [h.lower() for h in (csv.DictReader(f).fieldnames or [])]
        self.assertFalse(any(h in {"luong", "ket_qua", "yes_no", "trang_thai_luong"} for h in headers))

    def test_business_rules_are_separate_and_mock(self):
        path = ROOT / "data" / "business_rules_mock.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 54)
        self.assertTrue(all(r["ket_qua"] in {"YES", "NO"} for r in rows))
        self.assertTrue(all(r["la_mock"] == "1" for r in rows))
        self.assertTrue(all("[MOCK]" in r["can_cu"] for r in rows))


if __name__ == "__main__":
    unittest.main(verbosity=2)
