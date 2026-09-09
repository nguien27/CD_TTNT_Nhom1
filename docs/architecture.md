# ARCHITECTURE — KIẾN TRÚC HỆ THỐNG TRUY XUẤT THÔNG TIN NHÂN VIÊN

**Phiên bản:** 0.2  
**Ngày cập nhật:** 09/09/2026

## 1. Mục tiêu kiến trúc

Kiến trúc phải đáp ứng hai đặc điểm chính:

1. Input nhiều định dạng và nhiều cấu trúc.
2. Chỉ `ho_ten` là field bắt buộc; các field khác được giữ động.

## 2. Kiến trúc tổng thể

```text
                NGƯỜI DÙNG
                    │
                    ▼
                   UI
                    │
                    ▼
                 BACKEND
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
       UPLOAD               SEARCH
          │                   │
          ▼                   ▼
    FILE PROCESSOR       SEARCH ENGINE
          │                   │
   ┌──────┼──────┐            │
   │      │      │            │
 Excel   Word   CSV           │
   │      │      │            │
   └──────┼──────┘            │
          │                   │
          ▼                   │
         PDF                  │
      /       \               │
 PDF text   PDF scan           │
    │          │               │
 extract      OCR              │
    \          /               │
     \        /                │
      ▼      ▼                 │
   EXTRACTION / STRUCTURE      │
          │                    │
          ▼                    │
  DETECT `ho_ten` FIELD        │
          │                    │
     ┌────┴────┐               │
     │         │               │
   Không      Có               │
     │         │               │
  Cảnh báo     ▼               │
         NORMALIZATION         │
              │                │
              ▼                │
    FLEXIBLE RECORD MODEL      │
  ho_ten + extra_fields(JSON)  │
              │                │
              ▼                │
          SQLite / SQL ◄───────┘
              │
              ▼
             UI
```

## 3. File Processing Layer

Trách nhiệm:

- nhận file;
- phát hiện định dạng;
- đọc Excel/CSV/Word/PDF;
- với PDF: phân biệt text/scan;
- OCR PDF scan;
- không làm mất các cột/trường chưa biết;
- trả dữ liệu thô có cấu trúc hoặc text để bước tiếp theo xử lý.

## 4. Extraction / Name Detection Layer

Trách nhiệm:

- từ dữ liệu đọc được, xác định field tương ứng với `ho_ten`;
- sử dụng danh sách alias ban đầu;
- với Word/PDF unstructured, trích xuất tên theo label/pattern nếu có;
- nếu không phát hiện được `ho_ten`, trả lỗi nghiệp vụ `MISSING_NAME_FIELD`.

AI cho name-field detection có thể được bổ sung sau nếu cần; CK1 chưa được tự ý thay contract.

## 5. Normalization Layer

Trách nhiệm:

- chuẩn hóa giá trị `ho_ten`;
- tạo `ho_ten_chuan`;
- giữ toàn bộ field còn lại thành dictionary `thong_tin_mo_rong`;
- loại/báo record có `ho_ten` rỗng;
- giữ tên field nguồn để UI có thể hiển thị đúng nghĩa.

## 6. Storage Layer — SQLite

Mô hình lưu trữ:

```text
nhan_vien
├── id
├── ho_ten
├── ho_ten_chuan
├── thong_tin_mo_rong (JSON text)
├── nguon_file
├── nguon_sheet
└── created_at
```

SQLite không phụ thuộc số lượng field của file đầu vào.

## 7. Search Engine

Search chỉ phụ thuộc các trường:

- `ho_ten`;
- `ho_ten_chuan`.

Các extra fields không cần tham gia thuật toán tìm tên trong MVP, nhưng phải được giữ để trả về khi tìm thấy record.

Search flow:

```text
query
 ↓
normalize
 ↓
exact / partial / no-accent / fuzzy
 ↓
ranking
 ↓
record IDs
 ↓
SQLite
 ↓
ho_ten + toàn bộ extra fields
```

## 8. Backend

Backend là lớp điều phối:

### Upload

```text
UI → Backend → File Processor → Extraction → Normalization → SQLite
```

### Search

```text
UI → Backend → Search Engine → SQLite → Backend → UI
```

Backend không được giả định record chỉ có 6 field.

## 9. UI động

UI cần có:

- upload file;
- trạng thái xử lý;
- search box;
- danh sách kết quả;
- detail view hiển thị `ho_ten` + tất cả field mở rộng.

Ví dụ record A có 3 field và record B có 15 field thì UI vẫn phải hiển thị phù hợp từng record.

## 10. Server-client

```text
Máy leader
├── UI
├── Backend
├── SQLite
├── OCR runtime
└── File processing
      │
      ▼
0.0.0.0:PORT
      │
      ├── Máy thành viên
      ├── Máy giảng viên
      └── Điện thoại cùng mạng
```

## 11. Kiến trúc theo chu kỳ

### CK1 — Xây module riêng

- CK1-01: requirement/schema/architecture/rules/mock data.
- CK1-02: File Processor + OCR.
- CK1-03: Search Engine.
- CK1-04: SQLite + Backend prototype.
- CK1-05: UI + server prototype.

Các task 02–05 có thể làm song song sau khi CK1-01 phát hành baseline v0.2.

### CK2 — Tích hợp end-to-end

```text
File + OCR
  ↓
Detect ho_ten
  ↓
Normalize + preserve extras
  ↓
SQLite
  ↓
Search
  ↓
Backend
  ↓
Dynamic UI
```

### CK3 — Hoàn thiện

- system test;
- sửa lỗi;
- đóng gói;
- server test;
- User Guide;
- báo cáo kỹ thuật;
- GitHub;
- rehearsal demo.

## 12. Nguyên tắc kiến trúc bắt buộc

1. Không module nào được drop field lạ chỉ vì không có trong schema cũ.
2. Search không phụ thuộc `ma_nhan_vien`.
3. `id` SQLite là internal ID, không phải mã nhân viên doanh nghiệp.
4. Không hard-code danh sách 6 cột trong Backend/UI.
5. Thay đổi contract phải cập nhật tài liệu trước khi merge.
