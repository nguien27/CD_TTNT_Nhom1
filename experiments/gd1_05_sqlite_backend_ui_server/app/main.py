# -*- coding: utf-8 -*-
"""FastAPI GĐ1-05.

Backend chỉ điều phối. Search/Rule được gọi từ GĐ1-04, schema mapping CSV ưu tiên GĐ1-03.
"""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import DEFAULT_DB_PATH, ensure_database, get_connection
from .gd1_04_bridge import PayrollLookupAPI, RuleEngine, chuan_hoa
from .upload_service import import_employee_csv

APP_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(APP_DIR / "templates"))


def _row_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def _common_response(doi_tuong: dict[str, Any], status: dict[str, Any]) -> dict[str, Any]:
    return {
        "loi": False,
        "doi_tuong": doi_tuong,
        "trang_thai_tra_luong": status.get("ket_qua", "CHUA_XAC_DINH"),
        "can_cu": status.get("can_cu"),
        "ma_quy_tac": status.get("ma_quy_tac"),
        "ghi_chu": status.get("ghi_chu", ""),
    }


def _list_units(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    units: dict[str, dict[str, Any]] = {}
    for row in conn.execute(
        "SELECT DISTINCT don_vi FROM nhan_vien WHERE don_vi IS NOT NULL AND TRIM(don_vi) <> ''"
    ).fetchall():
        ten = row["don_vi"]
        units[chuan_hoa(ten)] = {"ten_don_vi": ten, "loai_don_vi": None}

    for row in conn.execute(
        """
        SELECT ten_don_vi, loai_don_vi, muc_uu_tien
        FROM business_rule
        WHERE ten_don_vi IS NOT NULL AND TRIM(ten_don_vi) <> ''
        ORDER BY muc_uu_tien DESC, id DESC
        """
    ).fetchall():
        key = chuan_hoa(row["ten_don_vi"])
        item = units.get(key, {"ten_don_vi": row["ten_don_vi"], "loai_don_vi": None})
        if not item.get("loai_don_vi") and row["loai_don_vi"]:
            item["loai_don_vi"] = row["loai_don_vi"]
        units[key] = item

    out = sorted(units.values(), key=lambda x: chuan_hoa(x["ten_don_vi"]))
    for i, item in enumerate(out, 1):
        item["id"] = i
        item["loai_doi_tuong"] = "DON_VI"
    return out


def create_app(db_path: str | Path | None = None, seed: bool = True) -> FastAPI:
    db_path = Path(db_path or DEFAULT_DB_PATH)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        conn = ensure_database(db_path, seed=seed)
        conn.close()
        yield

    app = FastAPI(title="TTNT Payroll Search - GD1-05", version="1.1.0", lifespan=lifespan)
    app.state.db_path = db_path
    app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

    def conn_now() -> sqlite3.Connection:
        return get_connection(app.state.db_path)

    @app.get("/health")
    def health() -> dict[str, Any]:
        conn = conn_now()
        try:
            return {
                "status": "ok",
                "nhan_vien": conn.execute("SELECT COUNT(*) FROM nhan_vien").fetchone()[0],
                "business_rule": conn.execute("SELECT COUNT(*) FROM business_rule").fetchone()[0],
                "gd1_04_integration": True,
            }
        finally:
            conn.close()

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return TEMPLATES.TemplateResponse("index.html", {"request": request})

    @app.get("/search")
    def search(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=50)) -> dict[str, Any]:
        conn = conn_now()
        try:
            raw = PayrollLookupAPI(conn).tra_cuu(q, limit=limit)
            if raw.get("loi"):
                raise HTTPException(status_code=400, detail=raw.get("thong_diep", "Lỗi tìm kiếm"))

            items = []
            for item in raw.get("ket_qua", []):
                status = item.get("trang_thai_luong", {})
                items.append(
                    {
                        "doi_tuong": item.get("thong_tin", {}),
                        "loai_doi_tuong": item.get("loai_doi_tuong"),
                        "id_doi_tuong": item.get("id_doi_tuong"),
                        "ten_hien_thi": item.get("ten_hien_thi"),
                        "do_khop": item.get("do_khop"),
                        "loai_khop": item.get("loai_khop"),
                        "trang_thai_tra_luong": status.get("ket_qua", "CHUA_XAC_DINH"),
                        "can_cu": status.get("can_cu"),
                        "ma_quy_tac": status.get("ma_quy_tac"),
                        "ghi_chu": status.get("ghi_chu", ""),
                    }
                )
            return {"loi": False, "truy_van": q, "so_ket_qua": len(items), "ket_qua": items}
        finally:
            conn.close()

    @app.get("/employees/{employee_id}")
    def employee(employee_id: int) -> dict[str, Any]:
        conn = conn_now()
        try:
            row = conn.execute("SELECT * FROM nhan_vien WHERE id = ?", (employee_id,)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")
            return {"loi": False, "doi_tuong": _row_dict(row)}
        finally:
            conn.close()

    @app.get("/units/{unit_id}")
    def unit(unit_id: int) -> dict[str, Any]:
        conn = conn_now()
        try:
            units = _list_units(conn)
            if unit_id < 1 or unit_id > len(units):
                raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị")
            return {"loi": False, "doi_tuong": units[unit_id - 1]}
        finally:
            conn.close()

    @app.get("/payroll-status/employee/{employee_id}")
    def employee_status(employee_id: int) -> dict[str, Any]:
        conn = conn_now()
        try:
            row = conn.execute("SELECT * FROM nhan_vien WHERE id = ?", (employee_id,)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")
            status = RuleEngine(conn).xac_dinh_trang_thai("CA_NHAN", row["ma_nhan_vien"])
            return _common_response(_row_dict(row), status)
        finally:
            conn.close()

    @app.get("/payroll-status/unit/{unit_id}")
    def unit_status(unit_id: int) -> dict[str, Any]:
        conn = conn_now()
        try:
            units = _list_units(conn)
            if unit_id < 1 or unit_id > len(units):
                raise HTTPException(status_code=404, detail="Không tìm thấy đơn vị")
            unit_data = units[unit_id - 1]
            status = RuleEngine(conn).xac_dinh_trang_thai(
                "DON_VI",
                unit_data["ten_don_vi"],
                loai_don_vi=unit_data.get("loai_don_vi"),
            )
            return _common_response(unit_data, status)
        finally:
            conn.close()

    @app.post("/upload")
    async def upload(file: UploadFile = File(...)) -> dict[str, Any]:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Thiếu tên file")
        suffix = Path(file.filename).suffix.lower()
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File rỗng")

        if suffix != ".csv":
            raise HTTPException(
                status_code=501,
                detail=(
                    "GĐ1-05 không tự viết File Reader/OCR. "
                    "XLSX/DOCX/PDF sẽ đi qua GĐ1-02 rồi GĐ1-03 ở bước tích hợp GĐ2."
                ),
            )

        conn = conn_now()
        try:
            result = import_employee_csv(conn, content)
            if not result["ok"]:
                raise HTTPException(status_code=422, detail=result)
            return {"loi": False, **result}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            conn.close()

    return app


app = create_app()
