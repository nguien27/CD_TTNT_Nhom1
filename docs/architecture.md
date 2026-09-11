# Architecture

## 1. Kiến trúc tổng thể
```text
XLSX / CSV / DOCX / PDF
        │
        ▼
   File Reader
        │
        ├── PDF text → Text Extraction
        │
        └── PDF scan → OCR
        │
        ▼
Information Extraction
        │
        ▼
 AI Schema Mapping
        │
        ▼
   Normalization
        │
        ▼
      SQLite
        │
        ▼
  Search Engine
        │
        ▼
Xác định đối tượng
 Cá nhân / Đơn vị
        │
        ▼
   Rule Engine
        │
        ▼
YES / NO / CHUA_XAC_DINH
+ căn cứ
        │
        ▼
   Backend API
        │
        ▼
        UI
```

## 2. Trách nhiệm module
- File Reader: phát hiện và đọc loại file
- OCR: PDF scan → text
- Information Extraction: lấy bảng/trường/giá trị
- AI Schema Mapping: dự đoán ý nghĩa tên cột, không dự đoán YES/NO
- Normalization: chuẩn hóa Unicode, khoảng trắng, tên, MSNV
- SQLite: lưu nhân viên, đơn vị, business rules
- Search Engine: MSNV, tên NV, tên đơn vị, Exact/Partial/Fuzzy/Ranking
- Rule Engine: lấy rule đang hiệu lực và trả YES/NO/CHUA_XAC_DINH + căn cứ
- Backend: kết nối module và cung cấp API
- UI: upload, search, kết quả, quản lý rule cho admin

## 3. Thay đổi quy tắc sau khi hệ thống chạy
Không cần sửa code.

```text
Admin UI / API
      ↓
Thêm / sửa / ngừng áp dụng rule
      ↓
SQLite
      ↓
Rule Engine đọc rule mới
      ↓
Kết quả tra cứu tiếp theo sử dụng rule mới
```

Khuyến nghị không xóa lịch sử rule; dùng ngày hiệu lực và cờ `dang_ap_dung`.
