# CÁC MÔ TẢ TASK CK1 CẦN CẬP NHẬT SAU KHI CHUYỂN SANG SCHEMA LINH HOẠT

> Dùng nội dung dưới đây để cập nhật Description trên Jira. Đây là các phần **cần sửa/bổ sung** so với mô tả trước, không phải toàn bộ Description.

## CK1-02 — File Reader + OCR

- Khi đọc Excel/CSV/Word/PDF, không được giới hạn dữ liệu về 6 trường cố định.
- Với file dạng bảng, phải giữ đầy đủ tên cột và giá trị của tất cả cột đọc được.
- Nếu file có 15 cột, output reader phải bảo toàn đủ 15 cột ở mức dữ liệu thô nếu đọc được.
- Không tự loại bỏ các cột lạ như Dự án, Kỹ năng, Ngày vào làm, Trình độ, Ghi chú...
- Reader không chịu trách nhiệm quyết định field nào ngoài `ho_ten` là quan trọng; nhiệm vụ chính là không làm mất dữ liệu.
- Với PDF scan, OCR phải trả text/cấu trúc càng đầy đủ càng tốt để bước extraction có thể tìm `ho_ten` và các field còn lại.
- Output phải cho bước sau biết tên file, loại file, dữ liệu đọc được, PDF text/scan và trạng thái OCR.
- Nếu phát hiện dữ liệu có header tương đương Họ tên thì giữ nguyên; không tự đổi schema ngoài contract chung.

## CK1-03 — Search Engine

- Search Engine chỉ sử dụng `ho_ten`/`ho_ten_chuan` làm trường chính để tìm kiếm trong MVP.
- Không phụ thuộc các field cố định như ma_nhan_vien, don_vi, chuc_vu.
- Kết quả tìm kiếm phải trả nguyên record gồm `ho_ten`, `do_khop` và toàn bộ `thong_tin_mo_rong`.
- Nếu record A có 3 field và record B có 15 field, Search Engine vẫn phải trả đúng toàn bộ extra fields tương ứng từng record.
- Giữ các yêu cầu Exact Match, Partial Match, không dấu, hoa/thường, Fuzzy Search và Ranking như mô tả cũ.

## CK1-04 — SQLite + Backend

- Thay thiết kế database 6 cột cố định bằng schema động:

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

- `ma_nhan_vien` không còn là PRIMARY KEY bắt buộc; nếu nguồn có mã nhân viên thì mã đó nằm trong `thong_tin_mo_rong`.
- Import phải chấp nhận record chỉ có `ho_ten` + bất kỳ số lượng field mở rộng nào.
- `thong_tin_mo_rong` phải được lưu dưới dạng JSON text và giải mã lại khi trả API.
- Backend API không được hard-code 6 field.
- `/search` và `/employees/{id}` phải có khả năng trả toàn bộ extra fields.
- Record thiếu `ho_ten` không được nhập vào bảng phục vụ search.

## CK1-05 — UI + Server

- UI không được thiết kế kết quả với 4/6 cột cố định.
- `ho_ten` luôn được hiển thị; các field còn lại phải render động từ `thong_tin_mo_rong`.
- Nếu file có 3 field, UI hiển thị được 3 field; nếu file có 15 field, UI phải có cách hiển thị đủ các field đó.
- Nên ưu tiên card/detail view hoặc bảng động để tránh phụ thuộc số cột cố định.
- Khi upload, UI nên hiển thị tên field họ tên đã nhận diện (khi backend có chức năng này), số record hợp lệ/lỗi và trạng thái OCR nếu là PDF scan.
- UI cần có thông báo rõ khi file không có trường họ tên: file đọc được nhưng chưa thể dùng để tìm kiếm theo tên.
