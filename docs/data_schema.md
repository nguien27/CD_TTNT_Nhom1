# DATA SCHEMA — SCHEMA LINH HOẠT CHO THÔNG TIN NHÂN VIÊN

**Phiên bản:** 0.2  
**Ngày cập nhật:** 09/09/2026

## 1. Nguyên tắc chính

Hệ thống không sử dụng schema cố định gồm 6 trường. Từ phiên bản 0.2:

- `ho_ten` là **trường nghiệp vụ bắt buộc duy nhất** để record tham gia tìm kiếm theo tên.
- Tất cả trường còn lại là **dynamic extra fields — trường mở rộng động**.
- Số lượng trường mở rộng phụ thuộc dữ liệu đầu vào và không bị giới hạn cố định.

## 2. Cấu trúc record chuẩn nội bộ

```python
{
    "ho_ten": "Nguyễn Văn A",
    "ho_ten_chuan": "nguyen van a",
    "thong_tin_mo_rong": {
        "Mã NV": "NV001",
        "Đơn vị": "Phòng CNTT",
        "Chức vụ": "Chuyên viên",
        "Dự án đang làm": "Hệ thống ERP",
        "Kỹ năng": "Python, SQL"
    }
}
```

### Giải thích

- `ho_ten`: tên gốc dùng hiển thị.
- `ho_ten_chuan`: tên đã chuẩn hóa để tìm kiếm; có thể đưa về chữ thường, gộp khoảng trắng, tạo bản không dấu.
- `thong_tin_mo_rong`: JSON/dictionary chứa **mọi trường còn lại** của record.

## 3. Nhận diện `ho_ten`

Các alias ban đầu:

| Tên trường nguồn | Canonical field |
|---|---|
| Họ tên | `ho_ten` |
| Họ và tên | `ho_ten` |
| Tên nhân viên | `ho_ten` |
| Tên NV | `ho_ten` |
| Tên CBCNV | `ho_ten` |
| Họ tên nhân viên | `ho_ten` |
| Full Name | `ho_ten` |
| Employee Name | `ho_ten` |
| Staff Name | `ho_ten` |

Việc mở rộng alias phải thông qua leader hoặc cập nhật tài liệu chung.

## 4. Trường mở rộng

Tất cả trường khác được giữ lại. Ví dụ:

- Mã NV
- Mã cán bộ
- Đơn vị
- Phòng ban
- Chức vụ
- Email
- Số điện thoại
- Dự án đang làm
- Kỹ năng
- Ngày vào làm
- Trình độ
- Chuyên môn
- Địa điểm làm việc
- Người quản lý
- Bất kỳ trường mới nào xuất hiện trong file

### Quy tắc bảo toàn

Nếu file có 15 cột và một cột được ánh xạ thành `ho_ten`, 14 cột còn lại phải được giữ trong `thong_tin_mo_rong` nếu có giá trị.

## 5. Validation

### Cấp file

- Không phát hiện được trường `ho_ten` → file không đủ điều kiện nhập vào kho tìm kiếm theo tên.
- Hệ thống trả cảnh báo rõ ràng thay vì crash.

### Cấp record

- `ho_ten` rỗng / null / chỉ có khoảng trắng → record không hợp lệ cho search; đánh dấu lỗi hoặc bỏ qua record.
- Các trường mở rộng rỗng → có thể bỏ khỏi JSON hoặc lưu `null` theo implementation thống nhất.

## 6. Chuẩn hóa họ tên

Ví dụ:

```text
"   NGUYỄN    VĂN   A "
      ↓
ho_ten = "NGUYỄN VĂN A"
ho_ten_chuan = "nguyen van a"
```

Các bước gợi ý:

1. trim đầu/cuối;
2. gộp nhiều khoảng trắng;
3. chuẩn hóa Unicode;
4. tạo bản chữ thường;
5. tạo bản không dấu cho search.

Không được làm thay đổi `ho_ten` gốc dùng hiển thị ngoài các chuẩn hóa khoảng trắng cần thiết.

## 7. Schema SQLite chính thức

```sql
CREATE TABLE IF NOT EXISTS nhan_vien (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten TEXT NOT NULL,
    ho_ten_chuan TEXT NOT NULL,
    thong_tin_mo_rong TEXT NOT NULL DEFAULT '{}',
    nguon_file TEXT,
    nguon_sheet TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Lý do có `id` nội bộ

- File có thể không có mã nhân viên.
- Mã nhân viên có thể nằm trong trường mở rộng.
- Hai người có thể trùng họ tên.
- Không được dùng `ho_ten` làm khóa chính.

## 8. Ví dụ file chỉ có 3 trường

Nguồn:

```text
Họ tên | Đơn vị | Dự án
```

Record chuẩn:

```python
{
    "ho_ten": "Nguyễn Văn A",
    "ho_ten_chuan": "nguyen van a",
    "thong_tin_mo_rong": {
        "Đơn vị": "CNTT",
        "Dự án": "ERP"
    }
}
```

→ Hợp lệ.

## 9. Ví dụ file có 15 trường

Nếu file có:

```text
Họ tên, Mã NV, Đơn vị, Chức vụ, Email, SĐT, Dự án, Kỹ năng,
Ngày vào làm, Trình độ, Chuyên môn, Địa điểm, Quản lý, Loại HĐ, Ghi chú
```

thì:

- `Họ tên` → `ho_ten`;
- 14 trường còn lại → `thong_tin_mo_rong`.

Không được tự loại bỏ trường chỉ vì hệ thống chưa từng gặp tên cột đó.

## 10. Ví dụ file không có họ tên

Nguồn:

```text
Mã NV | Đơn vị | Chức vụ
```

Kết quả:

```python
{
    "trang_thai": "error",
    "ma_loi": "MISSING_NAME_FIELD",
    "thong_bao": "Không phát hiện trường họ tên. File chưa thể dùng để tìm kiếm nhân viên theo tên."
}
```

## 11. Search result schema

```python
{
    "id": 1,
    "ho_ten": "Nguyễn Văn A",
    "do_khop": 96.5,
    "thong_tin_mo_rong": {
        "Mã NV": "NV001",
        "Đơn vị": "CNTT",
        "Dự án": "ERP",
        "Kỹ năng": "Python"
    }
}
```

## 12. Nguyên tắc UI

UI không được giả định cố định các cột `Mã NV`, `Đơn vị`, `Chức vụ`.

- `ho_ten` luôn hiển thị.
- Các trường khác được render động từ `thong_tin_mo_rong`.
- Nếu nhiều kết quả có tập field khác nhau, UI có thể dùng card/detail view hoặc bảng động theo union các field.
