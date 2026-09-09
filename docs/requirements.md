# REQUIREMENTS – Hệ thống truy xuất thông tin nhân viên doanh nghiệp

**Phiên bản:** 0.1 – CK1  
**Mục đích:** Làm tài liệu yêu cầu chung để các task CK1, CK2 và CK3 dùng cùng một ngữ cảnh.  
**Trạng thái:** Bản nền tảng; một số quyết định kỹ thuật như database và thành phần AI chưa khóa và sẽ được cập nhật sau review CK1.

---

## 1. Bối cảnh bài toán

Nhóm xây dựng một hệ thống có khả năng tiếp nhận dữ liệu nhân sự của doanh nghiệp từ nhiều loại tệp, trích xuất và chuẩn hóa thông tin nhân viên, sau đó cho phép người dùng tìm kiếm nhân viên và truy xuất các thông tin liên quan như mã nhân viên, họ tên, đơn vị, chức vụ và các trường mở rộng khác.

Ví dụ người dùng nhập:

```text
Nguyễn Văn
```

Hệ thống không chỉ tìm một tên khớp tuyệt đối mà cần trả về nhiều kết quả phù hợp, ví dụ:

```text
Nguyễn Văn A
Nguyễn Văn B
Nguyễn Văn An
```

Kết quả tìm kiếm cần hiển thị các thông tin của từng nhân viên, tối thiểu gồm mã nhân viên, họ tên, đơn vị và chức vụ.

---

## 2. Mục tiêu tổng quát

Xây dựng một sản phẩm có luồng xử lý hoàn chỉnh:

```text
File đầu vào
    ↓
Đọc file
    ↓
Trích xuất dữ liệu
    ↓
Ánh xạ và chuẩn hóa trường dữ liệu
    ↓
Lưu trữ dữ liệu
    ↓
Tìm kiếm / truy xuất
    ↓
Backend
    ↓
UI
    ↓
Người dùng
```

Sản phẩm cuối phải có thể được chạy trên một máy đóng vai trò **server (máy chủ)** và máy khác có thể truy cập, xem và sử dụng hệ thống trong điều kiện triển khai phù hợp.

---

## 3. Phạm vi dữ liệu đầu vào

### 3.1. Định dạng ưu tiên

Phiên bản đầu tiên ưu tiên hỗ trợ:

- `.xlsx` – Excel.
- `.csv` – tệp dữ liệu phân cách.
- `.docx` – Word.
- `.pdf` – PDF có lớp text có thể trích xuất.

Các định dạng khác có thể mở rộng sau khi MVP ổn định.

### 3.2. Cấu trúc file

Không giả định các file có cùng cấu trúc. Hệ thống cần hướng tới xử lý các biến thể như:

```text
File A:
Mã NV | Họ tên | Đơn vị | Chức vụ

File B:
Mã nhân viên | Tên nhân viên | Phòng ban | Vị trí

File C:
Employee ID | Full Name | Department | Position
```

Các tên cột khác nhau phải được ánh xạ về **Data Schema (cấu trúc dữ liệu chuẩn)** của hệ thống.

### 3.3. PDF scan

PDF dạng scan/ảnh có thể cần **OCR (nhận dạng ký tự quang học)**. Đây chưa phải yêu cầu bắt buộc của CK1. Trong CK1 chỉ cần xác định được giới hạn và ghi nhận nhu cầu mở rộng OCR nếu cần.

---

## 4. Thông tin nhân viên tối thiểu

Schema nền tảng gồm:

- `ma_nhan_vien`
- `ho_ten`
- `don_vi`
- `chuc_vu`
- `email`
- `so_dien_thoai`

Trong MVP, các trường quan trọng nhất để truy xuất là:

1. `ma_nhan_vien`
2. `ho_ten`
3. `don_vi`
4. `chuc_vu`

`email` và `so_dien_thoai` là trường mở rộng, có thể bị thiếu ở một số bản ghi.

Chi tiết kiểu dữ liệu, bắt buộc/không bắt buộc, quy tắc chuẩn hóa và ánh xạ được định nghĩa trong `data_schema.md`.

---

## 5. Actor và cách sử dụng

### 5.1. Người dùng cuối

Người không cần kiến thức lập trình, sử dụng hệ thống thông qua giao diện web.

### 5.2. Leader / người vận hành

Có thể:

- khởi động server;
- nạp dữ liệu;
- kiểm tra log hoặc thông báo lỗi;
- kiểm thử hệ thống;
- quản lý phiên bản mã nguồn trên GitHub.

---

## 6. Yêu cầu chức năng

### FR-01 – Upload file

Hệ thống cho phép người dùng chọn và tải file dữ liệu nhân viên lên.

**Tối thiểu:** `.xlsx`, `.csv`, `.docx`, `.pdf`.

Hệ thống phải xác định được loại file và chuyển tới bộ đọc tương ứng.

---

### FR-02 – Đọc nội dung file

Hệ thống có bộ đọc phù hợp cho từng loại file.

Kết quả đọc phải được chuyển thành dạng dữ liệu trung gian có cấu trúc để bước tiếp theo có thể xử lý.

---

### FR-03 – Kiểm tra file và xử lý lỗi

Hệ thống phải phản hồi hợp lý khi:

- file rỗng;
- file hỏng;
- phần mở rộng chưa hỗ trợ;
- file không chứa dữ liệu có thể sử dụng;
- không trích xuất được text từ PDF.

Một file lỗi không được làm toàn bộ ứng dụng dừng đột ngột.

---

### FR-04 – Nhận diện và ánh xạ trường dữ liệu

Các tên cột/nhãn khác nhau phải hướng tới được ánh xạ về trường chuẩn.

Ví dụ:

```text
Mã NV
Mã nhân viên
Mã cán bộ
Employee ID
      ↓
ma_nhan_vien
```

Quy tắc ánh xạ ban đầu được mô tả trong `data_schema.md`.

---

### FR-05 – Chuẩn hóa dữ liệu

Dữ liệu sau trích xuất phải được chuẩn hóa trước khi lưu, bao gồm tối thiểu:

- loại bỏ khoảng trắng thừa;
- chuẩn hóa tên trường;
- chuẩn hóa giá trị rỗng;
- kiểm tra trường bắt buộc;
- giữ Unicode tiếng Việt đúng;
- phát hiện mã nhân viên trùng khi cần.

---

### FR-06 – Lưu trữ dữ liệu

Hệ thống cần có một lớp **Storage (lưu trữ)** để lưu dữ liệu nhân viên sau chuẩn hóa.

Công nghệ lưu trữ chưa khóa tại thời điểm lập tài liệu. CK1-04 phải khảo sát và đề xuất dựa trên:

- độ đơn giản;
- khả năng truy vấn;
- khả năng chạy server;
- độ ổn định;
- thời gian thực hiện dự án.

Không được để UI phụ thuộc trực tiếp vào một file Excel duy nhất trong phiên bản tích hợp cuối.

---

### FR-07 – Tìm kiếm chính xác

Người dùng có thể tìm bằng họ tên đầy đủ hoặc mã nhân viên.

Ví dụ:

```text
NV001
Nguyễn Văn A
```

---

### FR-08 – Tìm kiếm một phần tên

Người dùng không cần nhập toàn bộ tên.

Ví dụ:

```text
Query: Nguyễn Văn
```

phải có khả năng trả nhiều nhân viên phù hợp.

---

### FR-09 – Không phân biệt hoa/thường

Các truy vấn sau phải được xử lý tương đương ở mức tìm kiếm tên:

```text
Nguyễn Văn
nguyễn văn
NGUYỄN VĂN
```

---

### FR-10 – Hỗ trợ tìm kiếm không dấu

Hệ thống nên hỗ trợ:

```text
Nguyen Van
```

để tìm các tên:

```text
Nguyễn Văn ...
```

Đây là yêu cầu ưu tiên cao cho Search Engine.

---

### FR-11 – Fuzzy Search

**Fuzzy Search (tìm kiếm gần đúng)** cần được thử nghiệm để xử lý lỗi gõ nhỏ.

Ví dụ:

```text
Nguyne Van A
```

có thể gợi ý:

```text
Nguyễn Văn A
```

Phương pháp và ngưỡng độ khớp chưa khóa trong CK1; CK1-03 phải thử nghiệm và báo cáo.

---

### FR-12 – Xếp hạng kết quả

Khi có nhiều kết quả, hệ thống cần sắp xếp kết quả phù hợp hơn lên trước.

Có thể sử dụng **similarity score (điểm tương đồng)** nếu phương pháp tìm kiếm hỗ trợ.

---

### FR-13 – Hiển thị thông tin nhân viên

Mỗi kết quả phải hiển thị tối thiểu:

- mã nhân viên;
- họ tên;
- đơn vị;
- chức vụ.

Có thể hiển thị email và số điện thoại nếu dữ liệu có.

---

### FR-14 – Giao diện người dùng

UI tối thiểu cần có:

1. khu vực upload file;
2. trạng thái xử lý file;
3. ô nhập truy vấn tìm kiếm;
4. nút tìm;
5. khu vực hiển thị nhiều kết quả;
6. thông báo khi không tìm thấy hoặc input không hợp lệ.

---

### FR-15 – Chạy theo mô hình server-client

Máy leader đóng vai trò server:

```text
Máy leader
    ↓
Server
    ↓
Máy khác / trình duyệt
```

CK3 phải kiểm thử việc máy khác truy cập hệ thống trong môi trường demo.

---

## 7. Yêu cầu phi chức năng

### NFR-01 – Dễ sử dụng

Người không chuyên phải có thể sử dụng hệ thống thông qua User Guide.

### NFR-02 – Không phụ thuộc đường dẫn máy cá nhân

Source code cuối không được chứa các đường dẫn tuyệt đối kiểu:

```text
C:\Users\TenThanhVien\Desktop\...
```

### NFR-03 – Khả năng chạy lại

Leader phải có thể clone/pull source, cài dependency và chạy theo README.

### NFR-04 – Khả năng truy vết công việc

Task, commit, branch và kết quả phải có khả năng truy vết thông qua Jira và GitHub.

### NFR-05 – Xử lý lỗi cơ bản

Ứng dụng cần trả thông báo lỗi có ý nghĩa thay vì crash trong các tình huống đầu vào phổ biến.

### NFR-06 – Dữ liệu tiếng Việt

Phải giữ đúng Unicode và dấu tiếng Việt trong dữ liệu nhân viên.

### NFR-07 – Tính nhất quán

Mọi module phải sử dụng Data Schema và Integration Rules chung.

---

## 8. MVP – Sản phẩm tối thiểu phải demo được

MVP được coi là đạt khi luồng sau chạy được:

```text
1. Người dùng mở UI
2. Upload một file được hỗ trợ
3. Hệ thống đọc file
4. Dữ liệu được chuẩn hóa
5. Dữ liệu được lưu
6. Người dùng nhập một phần tên
7. Hệ thống trả nhiều kết quả phù hợp
8. Hiển thị mã NV, họ tên, đơn vị, chức vụ
9. Một máy khác có thể truy cập server trong buổi kiểm thử/demo
```

---

## 9. Phạm vi chưa bắt buộc trong MVP

Các chức năng sau chỉ thực hiện khi phần lõi đã ổn định:

- OCR hoàn chỉnh cho mọi PDF scan.
- Chatbot hội thoại nhiều lượt.
- LLM.
- RAG.
- Semantic Search nâng cao.
- Phân quyền người dùng phức tạp.
- Đồng bộ hệ thống HR thật.
- Cloud deployment bắt buộc.

---

## 10. Vị trí AI – Chưa khóa

Đề tài thuộc môn Chuyên đề Trí tuệ nhân tạo nhưng tại thời điểm CK1 chưa chốt thành phần AI chính.

Các hướng có thể khảo sát:

1. **Fuzzy Matching (so khớp gần đúng)** cho tên nhân viên.
2. **Semantic Similarity (tương đồng ngữ nghĩa)**.
3. **Column Mapping (ánh xạ cột)** bằng mô hình/embedding khi tên trường rất khác nhau.
4. **Natural Language Query (truy vấn ngôn ngữ tự nhiên)**, ví dụ “Nguyễn Văn A làm ở đơn vị nào?”.
5. OCR hoặc mô hình trích xuất thông tin nếu dữ liệu đầu vào yêu cầu.

Nguyên tắc: không đưa AI vào chỉ để có tên AI; thành phần được chọn phải giải quyết một vấn đề thực tế và không làm hỏng MVP.

---

## 11. Sản phẩm cuối của nhóm

Theo yêu cầu dự án, nhóm cần chuẩn bị tối thiểu:

- hệ thống chạy được;
- bảng theo dõi task;
- báo cáo công việc của từng thành viên;
- báo cáo kỹ thuật;
- sản phẩm được đóng gói để máy khác có thể truy cập/chạy;
- User Guide;
- source code trên GitHub;
- dữ liệu demo và kịch bản demo.

---

## 12. Mốc thời gian

| Chu kỳ | Thời gian | Mục tiêu |
|---|---|---|
| CK1 | 08/09–15/09 | Phân tích, thiết kế, prototype các module |
| CK2 | 15/09–18/09 | Hoàn thiện module và tích hợp end-to-end |
| CK3 | 18/09–22/09 | Test, sửa lỗi, deploy, tài liệu, rehearsal |
| Báo cáo | 22/09 | Demo và báo cáo giảng viên |

Deadline nội bộ nên sớm hơn ngày review chính thức để leader có thời gian kiểm tra.

---

## 13. Các quyết định đang mở

Các mục sau chưa được xem là quyết định cuối cùng:

- loại database;
- framework backend;
- framework UI;
- thành phần AI chính;
- phương pháp fuzzy/ranking cuối cùng;
- có sử dụng Docker hay không;
- mức hỗ trợ PDF scan/OCR.

Sau review CK1, các quyết định được khóa phải cập nhật vào tài liệu này và `architecture.md` / `integration_rules.md`.

---

## 14. Quy tắc thay đổi yêu cầu

Nếu có yêu cầu mới từ giảng viên:

1. ghi lại yêu cầu mới;
2. đánh giá ảnh hưởng đến Data Schema và kiến trúc;
3. cập nhật tài liệu liên quan;
4. thông báo cho các task bị ảnh hưởng;
5. không để từng thành viên tự thay đổi schema/interface riêng.
