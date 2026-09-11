# GĐ1 – Bộ tài liệu bàn giao cho GĐ1-02, GĐ1-03, GĐ1-04, GĐ1-05

## Mục tiêu bài toán
Xây dựng hệ thống tra cứu một cá nhân hoặc đơn vị để xác định đối tượng đó có thuộc diện được trả lương hay không.

Người dùng có thể tra cứu bằng MSNV, tên nhân viên, một phần tên nhân viên, tên đơn vị hoặc một phần tên đơn vị.

Kết quả nghiệp vụ: `YES`, `NO`, `CHUA_XAC_DINH`.

Kết quả `YES/NO` không do AI tự dự đoán. AI dùng để hỗ trợ nhận diện cấu trúc dữ liệu đầu vào. Quyết định chi trả do Rule Engine đối chiếu các quy tắc nghiệp vụ/pháp lý đã được cấu hình trong hệ thống.

## Luồng hệ thống
```text
XLSX / CSV / DOCX / PDF
        ↓
File Reader
        ↓
PDF scan → OCR
        ↓
Information Extraction
        ↓
AI Schema Mapping
        ↓
Normalization
        ↓
SQLite
        ↓
Search Engine
        ↓
Xác định cá nhân / đơn vị
        ↓
Rule Engine
        ↓
YES / NO / CHUA_XAC_DINH + căn cứ
        ↓
Backend
        ↓
UI
```

## Thứ tự đọc
1. `docs/requirements.md`
2. `docs/data_schema.md`
3. `docs/architecture.md`
4. `docs/integration_rules.md`
5. Tài liệu handoff theo task
6. `docs/business_rules.md` nếu task liên quan Rule Engine/Database/Backend/UI

## Phân công tài liệu
- GĐ1-02: `handoff/GD1-02_file_ocr.md`
- GĐ1-03: `handoff/GD1-03_ai_schema_mapping.md`
- GĐ1-04: `handoff/GD1-04_search_rule.md`
- GĐ1-05: `handoff/GD1-05_database_backend_ui.md`

## File hỗ trợ
- `sql/schema.sql`
- `config/field_aliases.json`
- `data/mock_business_rules.csv`
