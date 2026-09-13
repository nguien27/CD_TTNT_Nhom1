# GĐ1-05 - SQLite + Backend + UI + Server

Bản đã sửa để đặt tại:

```text
experiments/gd1_05_sqlite_backend_ui_server/
```

## Kiến trúc

```text
GĐ1-02 File Reader/OCR
        -> GĐ1-03 Schema Mapping
        -> SQLite GĐ1-05
        -> GĐ1-04 Search Engine
        -> GĐ1-04 Rule Engine
        -> FastAPI GĐ1-05
        -> UI
```

GĐ1-05 không viết lại Search/Rule. Folder `gd1_03_ai_schema_mapping`, `gd1_04_search_rule_engine` và `gd1_05_sqlite_backend_ui_server` nên nằm cạnh nhau trong `experiments/`.

## Data model

Core schema đồng bộ GĐ1-04:

- `nhan_vien`: thông tin nhân viên, không có YES/NO.
- `business_rule`: nơi lưu YES/NO, căn cứ, hiệu lực, ưu tiên, MOCK.
- `ngoai_le_ca_nhan`: ngoại lệ nếu có.

Không dùng `ma_don_vi` và không bắt buộc bảng `don_vi` riêng trong core. Danh sách đơn vị được suy ra từ `nhan_vien.don_vi` và `business_rule.ten_don_vi`.

## Dữ liệu

- Giữ đóng góp 100.000 nhân viên dưới dạng `data/nhan_vien_chuan.csv`.
- `data/don_vi_nguon.csv` chỉ là metadata đơn vị, không chứa trạng thái lương.
- `data/business_rules_mock.csv` chứa kết quả YES/NO giả lập, tách khỏi dữ liệu nhân viên/đơn vị.

## API

- `GET /health`
- `POST /upload`
- `GET /search?q=...`
- `GET /employees/{id}`
- `GET /units/{id}`
- `GET /payroll-status/employee/{id}`
- `GET /payroll-status/unit/{id}`

`/search` dùng trực tiếp GĐ1-04. `/upload` ở GĐ1 chỉ chạy CSV để kiểm tra integration; XLSX/DOCX/PDF sẽ nối GĐ1-02 ở GĐ2. Header CSV ưu tiên GĐ1-03 Schema Mapping.

## Chạy

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run_server.py
```

Mở:

```text
http://127.0.0.1:8000
```

LAN:

```text
http://IP_MAY_LEADER:8000
```

Server bind `0.0.0.0:8000`. Nếu máy khác không truy cập được cần kiểm tra Windows Firewall và cùng mạng LAN.

## Những gì để GĐ2

- Nối thật XLSX/DOCX/PDF từ GĐ1-02 vào `/upload`.
- Dùng model Schema Mapping đã train ở GĐ1-03.
- Benchmark search/rule trên dữ liệu thật.
- Thay Business Rule MOCK bằng rule khách hàng cung cấp.
