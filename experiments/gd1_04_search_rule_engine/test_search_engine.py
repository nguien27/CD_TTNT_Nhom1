# -*- coding: utf-8 -*-

import sqlite3
import unittest

from db import init_schema, seed_mock_data
from search_engine import SearchEngine, chuan_hoa, la_query_msnv


class TestSearchEngine(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_schema(self.conn)
        seed_mock_data(self.conn)
        self.search = SearchEngine(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_normalize_vietnamese(self):
        self.assertEqual(chuan_hoa("  Nguyễn   Văn  An "), "nguyen van an")

    def test_detect_employee_code(self):
        self.assertTrue(la_query_msnv("NV001"))
        self.assertTrue(la_query_msnv("CB00025"))
        self.assertTrue(la_query_msnv("EMP102"))
        self.assertFalse(la_query_msnv("Nguyen Van An"))

    def test_msnv_exact_only(self):
        result = self.search.search("NV001")
        self.assertFalse(result["loi"])
        self.assertEqual(len(result["ket_qua"]), 1)
        self.assertEqual(result["ket_qua"][0]["id_doi_tuong"], "NV001")
        self.assertEqual(result["ket_qua"][0]["loai_khop"], "EXACT")

    def test_unknown_msnv_no_fuzzy_noise(self):
        result = self.search.search("NV999")
        self.assertEqual(result["ket_qua"], [])

    def test_full_name_no_accent_exact(self):
        result = self.search.search("nguyen van an", "CA_NHAN")
        self.assertGreaterEqual(len(result["ket_qua"]), 1)
        self.assertEqual(result["ket_qua"][0]["id_doi_tuong"], "NV001")
        self.assertEqual(result["ket_qua"][0]["loai_khop"], "EXACT")

    def test_partial_name(self):
        result = self.search.search("nguyen van", "CA_NHAN")
        ids = [x["id_doi_tuong"] for x in result["ket_qua"]]
        self.assertIn("NV001", ids)
        self.assertIn("NV005", ids)

    def test_fuzzy_typo_relevant(self):
        result = self.search.search("nguyen van anh", "CA_NHAN")
        self.assertTrue(result["ket_qua"])
        self.assertEqual(result["ket_qua"][0]["id_doi_tuong"], "NV001")
        self.assertEqual(result["ket_qua"][0]["loai_khop"], "FUZZY")

    def test_no_bad_name_noise(self):
        result = self.search.search("Do Thi Phuong", "CA_NHAN")
        ids = [x["id_doi_tuong"] for x in result["ket_qua"]]
        self.assertEqual(ids[0], "NV007")
        self.assertNotIn("NV004", ids)


    def test_single_token_name_prefers_whole_token(self):
        self.conn.executemany(
            """
            INSERT INTO nhan_vien
                (ma_nhan_vien, ho_ten, ho_ten_chuan, don_vi, chuc_vu, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                ("NV101", "Đỗ Đức An", "do duc an", "Trung tâm Công nghệ thông tin", "NV", None),
                ("NV102", "Nguyễn Văn Ân", "nguyen van an", "Trung tâm Công nghệ thông tin", "NV", None),
                ("NV103", "Lê Hoàng Anh", "le hoang anh", "Trung tâm Công nghệ thông tin", "NV", None),
            ],
        )
        self.conn.commit()

        result = self.search.search("an", "CA_NHAN", limit=20)
        ids = [x["id_doi_tuong"] for x in result["ket_qua"]]
        self.assertIn("NV101", ids)
        self.assertIn("NV102", ids)
        self.assertNotIn("NV103", ids)
        self.assertTrue(all(x["loai_khop"] == "TOKEN" for x in result["ket_qua"]))

    def test_duplicate_names_do_not_fill_top_results(self):
        rows = []
        for i in range(30):
            rows.append(
                (
                    f"DUP{i:03d}",
                    "Đỗ Đức An",
                    "do duc an",
                    "Trung tâm Công nghệ thông tin",
                    "NV",
                    None,
                )
            )
        rows.extend(
            [
                ("VAR001", "Phạm Văn An", "pham van an", "Trung tâm Công nghệ thông tin", "NV", None),
                ("VAR002", "Lê Quốc An", "le quoc an", "Trung tâm Công nghệ thông tin", "NV", None),
            ]
        )
        self.conn.executemany(
            """
            INSERT INTO nhan_vien
                (ma_nhan_vien, ho_ten, ho_ten_chuan, don_vi, chuc_vu, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit()

        result = self.search.search("an", "CA_NHAN", limit=5)
        names = [x["ten_hien_thi"] for x in result["ket_qua"]]
        self.assertIn("Đỗ Đức An", names)
        self.assertIn("Phạm Văn An", names)
        self.assertIn("Lê Quốc An", names)
        self.assertGreaterEqual(len(set(names)), 3)

    def test_unit_partial(self):
        result = self.search.search("cong nghe", "DON_VI")
        self.assertTrue(result["ket_qua"])
        self.assertEqual(result["ket_qua"][0]["thong_tin"]["ten_don_vi"], "Trung tâm Công nghệ thông tin")

    def test_search_has_no_business_result(self):
        result = self.search.search("NV001")
        item = result["ket_qua"][0]
        self.assertNotIn("ket_qua_luong", item)
        self.assertNotIn("trang_thai_luong", item)
        self.assertNotIn("can_cu", item)

    def test_empty_query(self):
        result = self.search.search("   ")
        self.assertTrue(result["loi"])
        self.assertEqual(result["ma_loi"], "QUERY_RONG")


if __name__ == "__main__":
    unittest.main(verbosity=2)
