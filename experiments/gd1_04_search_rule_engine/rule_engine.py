# -*- coding: utf-8 -*-
"""Rule Engine GĐ1-04.

Chỉ module này được phép quyết định YES / NO / CHUA_XAC_DINH.
AI Schema Mapping và Search Engine không được thực hiện quyết định nghiệp vụ.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from typing import Dict, Optional

from search_engine import chuan_hoa


class RuleEngine:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def xac_dinh_trang_thai(
        self,
        loai_doi_tuong: str,
        id_doi_tuong: str,
        ngay_xet: Optional[str] = None,
        loai_don_vi: Optional[str] = None,
    ) -> Dict:
        ngay_xet = ngay_xet or date.today().isoformat()

        if loai_doi_tuong == "CA_NHAN":
            return self._xet_ca_nhan(id_doi_tuong, ngay_xet)
        if loai_doi_tuong == "DON_VI":
            return self._xet_don_vi(id_doi_tuong, loai_don_vi, ngay_xet)

        return {
            "loi": True,
            "ma_loi": "LOAI_DOI_TUONG_KHONG_HOP_LE",
            "thong_diep": "loai_doi_tuong phải là CA_NHAN hoặc DON_VI.",
        }

    @staticmethod
    def _dang_hieu_luc(row: sqlite3.Row, ngay_xet: str) -> bool:
        if not row["dang_ap_dung"]:
            return False
        bat_dau = row["ngay_hieu_luc"]
        ket_thuc = row["ngay_het_hieu_luc"]
        if bat_dau and bat_dau > ngay_xet:
            return False
        if ket_thuc and ket_thuc < ngay_xet:
            return False
        return True

    def _xet_ca_nhan(self, ma_nhan_vien: str, ngay_xet: str) -> Dict:
        nhan_vien = self.conn.execute(
            "SELECT * FROM nhan_vien WHERE UPPER(ma_nhan_vien) = UPPER(?)",
            (ma_nhan_vien,),
        ).fetchone()
        if not nhan_vien:
            return self._chua_xac_dinh("Không tìm thấy cá nhân trong hệ thống.")

        ngoai_le = self._chon_ngoai_le(ma_nhan_vien, ngay_xet)
        if ngoai_le:
            return self._format_rule_result(
                ngoai_le,
                ma_quy_tac="NGOAI_LE_CA_NHAN",
                nguon="NGOAI_LE_CA_NHAN",
            )

        if not nhan_vien["don_vi"]:
            return self._chua_xac_dinh("Cá nhân chưa có thông tin đơn vị công tác.")

        return self._xet_don_vi(nhan_vien["don_vi"], None, ngay_xet)

    def _chon_ngoai_le(self, ma_nhan_vien: str, ngay_xet: str) -> Optional[sqlite3.Row]:
        rows = self.conn.execute(
            """
            SELECT * FROM ngoai_le_ca_nhan
            WHERE UPPER(ma_nhan_vien) = UPPER(?)
            ORDER BY muc_uu_tien DESC, COALESCE(ngay_hieu_luc, '') DESC, id DESC
            """,
            (ma_nhan_vien,),
        ).fetchall()
        for row in rows:
            if self._dang_hieu_luc(row, ngay_xet):
                return row
        return None

    def _xet_don_vi(
        self,
        ten_don_vi: str,
        loai_don_vi: Optional[str],
        ngay_xet: str,
    ) -> Dict:
        rows = self.conn.execute(
            """
            SELECT * FROM business_rule
            ORDER BY muc_uu_tien DESC, COALESCE(ngay_hieu_luc, '') DESC, id DESC
            """
        ).fetchall()

        rules_hieu_luc = [row for row in rows if self._dang_hieu_luc(row, ngay_xet)]
        ten_norm = chuan_hoa(ten_don_vi)

        # Ưu tiên rule khớp đúng tên đơn vị.
        exact_rules = [
            row for row in rules_hieu_luc
            if row["ten_don_vi"] and chuan_hoa(row["ten_don_vi"]) == ten_norm
        ]
        if exact_rules:
            return self._format_rule_result(exact_rules[0], exact_rules[0]["ma_quy_tac"], "BUSINESS_RULE")

        # Nếu caller có loại đơn vị, cho phép dùng rule chung theo loại đơn vị
        # với ten_don_vi để trống.
        if loai_don_vi:
            loai_norm = chuan_hoa(loai_don_vi)
            generic_rules = [
                row for row in rules_hieu_luc
                if not row["ten_don_vi"]
                and row["loai_don_vi"]
                and chuan_hoa(row["loai_don_vi"]) == loai_norm
            ]
            if generic_rules:
                return self._format_rule_result(generic_rules[0], generic_rules[0]["ma_quy_tac"], "BUSINESS_RULE")

        return self._chua_xac_dinh(
            f"Chưa có quy tắc đang hiệu lực áp dụng cho đơn vị '{ten_don_vi}'."
        )

    @staticmethod
    def _format_rule_result(row: sqlite3.Row, ma_quy_tac: str, nguon: str) -> Dict:
        can_cu = row["can_cu"]
        if row["la_mock"] and not str(can_cu).startswith("[MOCK]"):
            can_cu = "[MOCK] " + str(can_cu)

        return {
            "ket_qua": row["ket_qua"],
            "can_cu": can_cu,
            "ma_quy_tac": ma_quy_tac,
            "nguon_quy_tac": nguon,
            "muc_uu_tien": row["muc_uu_tien"],
            "ngay_hieu_luc": row["ngay_hieu_luc"],
            "ngay_het_hieu_luc": row["ngay_het_hieu_luc"],
            "ghi_chu": row["ghi_chu"] or "",
        }

    @staticmethod
    def _chua_xac_dinh(can_cu: str) -> Dict:
        return {
            "ket_qua": "CHUA_XAC_DINH",
            "can_cu": can_cu,
            "ma_quy_tac": None,
            "nguon_quy_tac": None,
            "muc_uu_tien": None,
            "ngay_hieu_luc": None,
            "ngay_het_hieu_luc": None,
            "ghi_chu": "",
        }
