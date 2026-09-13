# -*- coding: utf-8 -*-
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.database import ensure_database
from app.main import create_app


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "api.db"
        conn = ensure_database(self.db_path, seed=False)
        conn.executemany(
            """
            INSERT INTO nhan_vien (ma_nhan_vien, ho_ten, ho_ten_chuan, don_vi, chuc_vu, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                ("NV001", "Nguyễn Văn An", "nguyen van an", "Trung tâm Công nghệ thông tin", "Chuyên viên", "a@example.com"),
                ("NV002", "Trần Thị Bình", "tran thi binh", "Công ty B", "Nhân viên", "b@example.com"),
            ],
        )
        conn.executemany(
            """
            INSERT INTO business_rule
            (ma_quy_tac, ten_quy_tac, ten_don_vi, loai_don_vi, pham_vi, ket_qua, can_cu,
             muc_uu_tien, ngay_hieu_luc, ngay_het_hieu_luc, dang_ap_dung, la_mock, ghi_chu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("R01", "Rule A", "Trung tâm Công nghệ thông tin", "CA", "DON_VI", "YES", "Mock R01", 50, "2025-01-01", None, 1, 1, "MOCK"),
                ("R02", "Rule B", "Công ty B", "BQP", "DON_VI", "NO", "Mock R02", 50, "2025-01-01", None, 1, 1, "MOCK"),
            ],
        )
        conn.commit()
        conn.close()
        self.client_ctx = TestClient(create_app(self.db_path, seed=False))
        self.client = self.client_ctx.__enter__()

    def tearDown(self):
        self.client_ctx.__exit__(None, None, None)
        self.tmp.cleanup()

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["gd1_04_integration"])

    def test_search_reuses_gd1_04_exact_msnv(self):
        data = self.client.get("/search", params={"q": "NV001"}).json()
        self.assertEqual(data["so_ket_qua"], 1)
        item = data["ket_qua"][0]
        self.assertEqual(item["id_doi_tuong"], "NV001")
        self.assertEqual(item["loai_khop"], "EXACT")
        self.assertEqual(item["trang_thai_tra_luong"], "YES")

    def test_employee_and_payroll_response_contract(self):
        emp = self.client.get("/employees/1")
        self.assertEqual(emp.status_code, 200)
        self.assertIn("doi_tuong", emp.json())

        payroll = self.client.get("/payroll-status/employee/1")
        body = payroll.json()
        self.assertEqual(body["trang_thai_tra_luong"], "YES")
        self.assertIn("can_cu", body)
        self.assertIn("ghi_chu", body)
        self.assertNotIn("ly_do", body)

    def test_unit_endpoint_and_status(self):
        unit = self.client.get("/units/1")
        self.assertEqual(unit.status_code, 200)
        status = self.client.get("/payroll-status/unit/1")
        self.assertEqual(status.status_code, 200)
        self.assertIn(status.json()["trang_thai_tra_luong"], {"YES", "NO", "CHUA_XAC_DINH"})

    def test_upload_csv_uses_schema_mapping_contract(self):
        csv_bytes = "ma_nhan_vien,ho_ten,don_vi\nNV099,Le Thi Lan,Trung tam X\n".encode("utf-8")
        r = self.client.post("/upload", files={"file": ("nv.csv", csv_bytes, "text/csv")})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["so_dong_import"], 1)

    def test_non_csv_is_delegated_to_gd1_02_later(self):
        r = self.client.post("/upload", files={"file": ("nv.xlsx", b"demo", "application/octet-stream")})
        self.assertEqual(r.status_code, 501)
        self.assertIn("GĐ1-02", r.json()["detail"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
