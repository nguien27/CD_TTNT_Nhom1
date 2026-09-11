# Requirements

## 1. Mục tiêu
Hệ thống hỗ trợ người dùng tra cứu cá nhân hoặc đơn vị và xác định trạng thái thuộc diện được trả lương hay không.

## 2. Đối tượng tra cứu
### Cá nhân
- `ma_nhan_vien`
- `ho_ten`
- một phần `ho_ten`

### Đơn vị
- `ten_don_vi`
- một phần `ten_don_vi`
- `ma_don_vi` nếu có

## 3. Kết quả nghiệp vụ
- `YES`: thuộc diện được trả lương
- `NO`: không thuộc diện được trả lương
- `CHUA_XAC_DINH`: chưa đủ dữ liệu hoặc không có quy tắc phù hợp

Kết quả có khả năng kèm quy tắc được áp dụng, căn cứ và ghi chú.

## 4. Nguồn quyết định YES/NO
YES/NO được xác định bởi Rule Engine dựa trên:
- quy tắc dành riêng cho đơn vị
- quy tắc theo loại đơn vị
- chính sách khách hàng
- văn bản pháp lý/nghị định nếu được xác định là áp dụng
- ngoại lệ cá nhân nếu bổ sung sau

AI không tự quyết định YES/NO.

## 5. Input
- XLSX
- CSV
- DOCX
- PDF text
- PDF scan

PDF scan phải hỗ trợ OCR.

## 6. AI
AI dùng cho Schema Mapping.

Các class ban đầu:
- `MA_NHAN_VIEN`
- `HO_TEN`
- `MA_DON_VI`
- `TEN_DON_VI`
- `LOAI_DON_VI`
- `OTHER`

## 7. Search
- Exact Match
- Partial Match
- không phân biệt hoa/thường
- chuẩn hóa khoảng trắng
- tìm không dấu
- Fuzzy Search
- Ranking
- trả nhiều kết quả

## 8. Database
- SQLite
- SQL
- không hard-code YES/NO trong source code
- business rule lưu trong database để có thể thay đổi mà không sửa code

## 9. Backend và UI
Backend cung cấp API cho upload, search, xem chi tiết, kiểm tra trạng thái trả lương và quản lý rule.

UI hỗ trợ upload, tìm kiếm, xem YES/NO/CHUA_XAC_DINH, xem căn cứ và màn hình quản lý rule cho admin.

## 10. Server
- máy leader chạy hệ thống
- bind `0.0.0.0`
- máy khác cùng LAN truy cập bằng trình duyệt

## 11. Quản lý source
- GitHub
- các module dùng chung Data Schema và Integration Rules
