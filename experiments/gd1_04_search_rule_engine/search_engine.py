# -*- coding: utf-8 -*-
"""Search Engine GĐ1-04.

Chỉ chịu trách nhiệm tìm và xếp hạng đối tượng.
KHÔNG quyết định YES/NO và KHÔNG chứa business rule.
"""

from __future__ import annotations

import re
import sqlite3
import unicodedata
from typing import Dict, List, Optional, Tuple

from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein

FUZZY_THRESHOLD = 0.85


def chuan_hoa(text: Optional[str]) -> str:
    if text is None:
        return ""
    text = str(text).strip().lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tach_token(text_norm: str) -> List[str]:
    """Tách chuỗi đã chuẩn hóa thành các từ/token không rỗng."""
    return [token for token in str(text_norm).split(" ") if token]


def la_query_msnv(query: str) -> bool:
    """Nhận biết query có hình dạng mã nhân viên như NV001, CB00025, EMP102."""
    q = re.sub(r"[\s_-]+", "", str(query).strip()).upper()
    return bool(re.fullmatch(r"[A-Z]{1,6}\d{2,}", q))


def diem_fuzzy(query_norm: str, field_norm: str) -> Tuple[float, Dict[str, float]]:
    """Tính các độ tương đồng đã khảo sát và trả score cuối cùng 0..1.

    - Levenshtein normalized similarity
    - Ratio
    - Partial Ratio
    - Token Set Ratio

    Partial Ratio chỉ đóng vai trò hỗ trợ, không được phép một mình kéo một
    kết quả yếu vượt ngưỡng. Điều này giúp giảm nhiễu với tên người.
    """
    ratio = fuzz.ratio(query_norm, field_norm) / 100.0
    partial = fuzz.partial_ratio(query_norm, field_norm) / 100.0
    token = fuzz.token_set_ratio(query_norm, field_norm) / 100.0
    levenshtein = Levenshtein.normalized_similarity(query_norm, field_norm)

    # Điểm chính dựa trên toàn chuỗi/token; partial chỉ hỗ trợ tối đa 10%.
    core = max(ratio, token, levenshtein)
    score = min(1.0, 0.90 * core + 0.10 * partial)
    chi_tiet = {
        "ratio": round(ratio, 4),
        "partial_ratio": round(partial, 4),
        "token_ratio": round(token, 4),
        "levenshtein": round(levenshtein, 4),
    }
    return round(score, 4), chi_tiet


def _match_text(query_norm: str, field_raw: Optional[str]) -> Optional[Tuple[float, str, Dict[str, float]]]:
    field_norm = chuan_hoa(field_raw)
    if not query_norm or not field_norm:
        return None

    if query_norm == field_norm:
        return 1.0, "EXACT", {}

    # Với query một từ, ưu tiên khớp nguyên token.
    # Ví dụ "an" khớp "Nguyễn Văn An"/"Trần Quốc Ân" nhưng không coi
    # "Nguyễn Anh" là cùng mức, vì token của "Anh" là "anh", không phải "an".
    query_tokens = tach_token(query_norm)
    field_tokens = tach_token(field_norm)
    if len(query_tokens) == 1 and query_tokens[0] in field_tokens:
        return 0.97, "TOKEN", {}

    if query_norm in field_norm:
        ti_le = len(query_norm) / max(len(field_norm), 1)
        score = 0.90 + 0.05 * min(ti_le, 1.0)
        return round(min(score, 0.95), 4), "PARTIAL", {}

    score, chi_tiet = diem_fuzzy(query_norm, field_norm)
    if score >= FUZZY_THRESHOLD:
        # Fuzzy luôn thấp hơn Partial để ranking ổn định.
        return min(score, 0.89), "FUZZY", chi_tiet

    return None


class SearchEngine:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def search(
        self,
        query: str,
        loai_doi_tuong: Optional[str] = None,
        limit: int = 20,
    ) -> Dict:
        if query is None or not str(query).strip():
            return {
                "loi": True,
                "ma_loi": "QUERY_RONG",
                "thong_diep": "Chuỗi tra cứu không được để trống.",
            }

        if loai_doi_tuong not in (None, "CA_NHAN", "DON_VI"):
            return {
                "loi": True,
                "ma_loi": "LOAI_DOI_TUONG_KHONG_HOP_LE",
                "thong_diep": "loai_doi_tuong phải là CA_NHAN, DON_VI hoặc None.",
            }

        query = str(query).strip()

        # MSNV: Exact Match trước và không fuzzy sang các mã khác.
        if la_query_msnv(query) and loai_doi_tuong in (None, "CA_NHAN"):
            exact = self._search_msnv_exact(query)
            if exact:
                return {"loi": False, "ket_qua": exact[:limit], "tong_so_truoc_gioi_han": len(exact)}
            # Query trông như MSNV nhưng không tồn tại -> không fuzzy mã.
            if loai_doi_tuong == "CA_NHAN" or loai_doi_tuong is None:
                return {"loi": False, "ket_qua": [], "tong_so_truoc_gioi_han": 0}

        query_norm = chuan_hoa(query)
        ket_qua: List[Dict] = []

        if loai_doi_tuong in (None, "CA_NHAN"):
            ket_qua.extend(self._search_ca_nhan_by_name(query_norm))

        if loai_doi_tuong in (None, "DON_VI"):
            ket_qua.extend(self._search_don_vi(query_norm))

        # Dùng chiến lược theo tầng để giảm nhiễu:
        # EXACT > TOKEN > PARTIAL > FUZZY.
        # TOKEN giúp query ngắn theo tên người hợp lý hơn: "an" ưu tiên đúng
        # từ An/Ân thay vì substring trong "Anh".
        for loai_tot_nhat in ("EXACT", "TOKEN", "PARTIAL", "FUZZY"):
            if any(x["loai_khop"] == loai_tot_nhat for x in ket_qua):
                ket_qua = [x for x in ket_qua if x["loai_khop"] == loai_tot_nhat]
                break

        thu_tu = {"EXACT": 0, "TOKEN": 1, "PARTIAL": 2, "FUZZY": 3}
        ket_qua.sort(
            key=lambda x: (
                thu_tu.get(x["loai_khop"], 9),
                -x["do_khop"],
                chuan_hoa(x["ten_hien_thi"]),
                str(x.get("id_doi_tuong", "")),
            )
        )

        # Với truy vấn rộng, nhiều nhân viên có thể trùng hoàn toàn họ tên.
        # Xếp xen kẽ theo tên để 20 kết quả đầu không bị một tên lặp chiếm hết.
        ket_qua = self._da_dang_hoa_ten(ket_qua)

        return {
            "loi": False,
            "ket_qua": ket_qua[:limit],
            "tong_so_truoc_gioi_han": len(ket_qua),
        }

    @staticmethod
    def _da_dang_hoa_ten(ket_qua: List[Dict]) -> List[Dict]:
        """Xen kẽ các kết quả trùng tên để top-N đa dạng hơn.

        Không loại bỏ bản ghi: nếu tăng limit vẫn có thể xem đủ những nhân viên
        trùng họ tên nhưng khác MSNV/đơn vị.
        """
        if len(ket_qua) <= 1:
            return ket_qua

        nhom: Dict[Tuple[str, str], List[Dict]] = {}
        thu_tu_nhom: List[Tuple[str, str]] = []
        for item in ket_qua:
            key = (item.get("loai_doi_tuong", ""), chuan_hoa(item.get("ten_hien_thi", "")))
            if key not in nhom:
                nhom[key] = []
                thu_tu_nhom.append(key)
            nhom[key].append(item)

        if len(nhom) == len(ket_qua):
            return ket_qua

        out: List[Dict] = []
        vi_tri = 0
        while True:
            co_them = False
            for key in thu_tu_nhom:
                group = nhom[key]
                if vi_tri < len(group):
                    out.append(group[vi_tri])
                    co_them = True
            if not co_them:
                break
            vi_tri += 1
        return out

    def _search_msnv_exact(self, query: str) -> List[Dict]:
        q = re.sub(r"[\s_-]+", "", query).upper()
        rows = self.conn.execute("SELECT * FROM nhan_vien").fetchall()
        for row in rows:
            ma = re.sub(r"[\s_-]+", "", row["ma_nhan_vien"]).upper()
            if ma == q:
                return [self._format_ca_nhan(row, 1.0, "EXACT", field="ma_nhan_vien")]
        return []

    def _search_ca_nhan_by_name(self, query_norm: str) -> List[Dict]:
        rows = self.conn.execute("SELECT * FROM nhan_vien").fetchall()
        out: List[Dict] = []
        for row in rows:
            match = _match_text(query_norm, row["ho_ten"])
            if match:
                score, loai_khop, chi_tiet = match
                out.append(self._format_ca_nhan(row, score, loai_khop, "ho_ten", chi_tiet))
        return out

    def _lay_danh_sach_don_vi(self) -> List[Dict]:
        """Không dùng bảng don_vi riêng; gom tên đơn vị từ nhân viên và business_rule."""
        thong_tin: Dict[str, Dict] = {}

        rows_nv = self.conn.execute(
            "SELECT DISTINCT don_vi FROM nhan_vien WHERE don_vi IS NOT NULL AND TRIM(don_vi) <> ''"
        ).fetchall()
        for row in rows_nv:
            ten = row["don_vi"]
            thong_tin[chuan_hoa(ten)] = {"ten_don_vi": ten, "loai_don_vi": None}

        rows_rule = self.conn.execute(
            """
            SELECT ten_don_vi, loai_don_vi, muc_uu_tien
            FROM business_rule
            WHERE ten_don_vi IS NOT NULL AND TRIM(ten_don_vi) <> ''
            ORDER BY muc_uu_tien DESC, id DESC
            """
        ).fetchall()
        for row in rows_rule:
            key = chuan_hoa(row["ten_don_vi"])
            current = thong_tin.get(key, {"ten_don_vi": row["ten_don_vi"], "loai_don_vi": None})
            if current.get("loai_don_vi") is None and row["loai_don_vi"]:
                current["loai_don_vi"] = row["loai_don_vi"]
            thong_tin[key] = current

        return list(thong_tin.values())

    def _search_don_vi(self, query_norm: str) -> List[Dict]:
        out: List[Dict] = []
        for item in self._lay_danh_sach_don_vi():
            match = _match_text(query_norm, item["ten_don_vi"])
            if not match:
                continue
            score, loai_khop, chi_tiet = match
            out.append(
                {
                    "loai_doi_tuong": "DON_VI",
                    "id_doi_tuong": item["ten_don_vi"],
                    "ten_hien_thi": item["ten_don_vi"],
                    "thong_tin": dict(item),
                    "do_khop": score,
                    "loai_khop": loai_khop,
                    "truong_khop": "ten_don_vi",
                    "chi_tiet_fuzzy": chi_tiet,
                }
            )
        return out

    @staticmethod
    def _format_ca_nhan(
        row: sqlite3.Row,
        score: float,
        loai_khop: str,
        field: str,
        chi_tiet: Optional[Dict[str, float]] = None,
    ) -> Dict:
        return {
            "loai_doi_tuong": "CA_NHAN",
            "id_doi_tuong": row["ma_nhan_vien"],
            "ten_hien_thi": row["ho_ten"],
            "thong_tin": dict(row),
            "do_khop": round(float(score), 4),
            "loai_khop": loai_khop,
            "truong_khop": field,
            "chi_tiet_fuzzy": chi_tiet or {},
        }
