# -*- coding: utf-8 -*-

import sqlite3
import unittest

from db import init_schema, seed_mock_data
from rule_engine import RuleEngine


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_schema(self.conn)
        seed_mock_data(self.conn)
        self.rule = RuleEngine(self.conn)
        self.ngay_xet = "2026-09-12"

    def tearDown(self):
        self.conn.close()

    def test_employee_yes(self):
        result = self.rule.xac_dinh_trang_thai("CA_NHAN", "NV001", self.ngay_xet)
        self.assertEqual(result["ket_qua"], "YES")
        self.assertEqual(result["ma_quy_tac"], "R01")
        self.assertTrue(result["can_cu"].startswith("[MOCK]"))

    def test_employee_no(self):
        # NV003 có ngoại lệ YES, nên dùng đơn vị trực tiếp để kiểm tra R02 = NO.
        result = self.rule.xac_dinh_trang_thai(
            "DON_VI", "Công ty TNHH Dịch vụ Thương mại ABC", self.ngay_xet
        )
        self.assertEqual(result["ket_qua"], "NO")
        self.assertEqual(result["ma_quy_tac"], "R02")

    def test_personal_exception_has_priority(self):
        result = self.rule.xac_dinh_trang_thai("CA_NHAN", "NV003", self.ngay_xet)
        self.assertEqual(result["ket_qua"], "YES")
        self.assertEqual(result["nguon_quy_tac"], "NGOAI_LE_CA_NHAN")

    def test_missing_unit_is_unknown(self):
        result = self.rule.xac_dinh_trang_thai("CA_NHAN", "NV007", self.ngay_xet)
        self.assertEqual(result["ket_qua"], "CHUA_XAC_DINH")

    def test_no_rule_is_unknown(self):
        result = self.rule.xac_dinh_trang_thai(
            "DON_VI", "Hội Chữ thập đỏ Phường X", self.ngay_xet
        )
        self.assertEqual(result["ket_qua"], "CHUA_XAC_DINH")

    def test_expired_high_priority_rule_is_ignored(self):
        result = self.rule.xac_dinh_trang_thai(
            "DON_VI", "Trung tâm Công nghệ thông tin", self.ngay_xet
        )
        self.assertEqual(result["ket_qua"], "YES")
        self.assertEqual(result["ma_quy_tac"], "R01")

    def test_future_rule_is_ignored(self):
        self.conn.execute(
            """
            INSERT INTO business_rule
            (ma_quy_tac, ten_quy_tac, ten_don_vi, loai_don_vi, pham_vi,
             ket_qua, can_cu, muc_uu_tien, ngay_hieu_luc, ngay_het_hieu_luc,
             dang_ap_dung, la_mock, ghi_chu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "R_FUTURE", "Future", "Trung tâm Công nghệ thông tin", "DON_VI_SU_NGHIEP",
                "DON_VI", "NO", "future", 9999, "2030-01-01", None, 1, 1, "future"
            ),
        )
        self.conn.commit()
        result = self.rule.xac_dinh_trang_thai(
            "DON_VI", "Trung tâm Công nghệ thông tin", self.ngay_xet
        )
        self.assertEqual(result["ma_quy_tac"], "R01")

    def test_no_yes_no_in_employee_table(self):
        columns = [r[1] for r in self.conn.execute("PRAGMA table_info(nhan_vien)").fetchall()]
        self.assertNotIn("ket_qua", columns)
        self.assertNotIn("duoc_tra_luong", columns)
        self.assertNotIn("trang_thai_luong", columns)

    def test_no_ma_don_vi_core_column(self):
        nv_columns = [r[1] for r in self.conn.execute("PRAGMA table_info(nhan_vien)").fetchall()]
        self.assertNotIn("ma_don_vi", nv_columns)
        tables = [r[0] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        self.assertNotIn("don_vi", tables)


if __name__ == "__main__":
    unittest.main(verbosity=2)
