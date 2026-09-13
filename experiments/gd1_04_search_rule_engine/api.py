# -*- coding: utf-8 -*-
"""Facade demo nối Search Engine và Rule Engine.

Đây chưa phải REST API production; chỉ là hợp đồng tích hợp cho GĐ sau.
"""

from __future__ import annotations

import sqlite3
from typing import Dict, Optional

from rule_engine import RuleEngine
from search_engine import SearchEngine


class PayrollLookupAPI:
    def __init__(self, conn: sqlite3.Connection):
        self.search_engine = SearchEngine(conn)
        self.rule_engine = RuleEngine(conn)

    def tra_cuu(
        self,
        query: str,
        loai_doi_tuong: Optional[str] = None,
        limit: int = 20,
        ngay_xet: Optional[str] = None,
    ) -> Dict:
        search_result = self.search_engine.search(query, loai_doi_tuong, limit)
        if search_result.get("loi"):
            return search_result

        ket_qua = []
        for item in search_result["ket_qua"]:
            loai = item["loai_doi_tuong"]
            if loai == "CA_NHAN":
                trang_thai = self.rule_engine.xac_dinh_trang_thai(
                    "CA_NHAN", item["thong_tin"]["ma_nhan_vien"], ngay_xet=ngay_xet
                )
            else:
                trang_thai = self.rule_engine.xac_dinh_trang_thai(
                    "DON_VI",
                    item["thong_tin"]["ten_don_vi"],
                    ngay_xet=ngay_xet,
                    loai_don_vi=item["thong_tin"].get("loai_don_vi"),
                )
            ket_qua.append({**item, "trang_thai_luong": trang_thai})

        return {
            "loi": False,
            "truy_van": query,
            "so_ket_qua": len(ket_qua),
            "ket_qua": ket_qua,
        }
