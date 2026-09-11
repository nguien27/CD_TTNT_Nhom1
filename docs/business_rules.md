# Business Rules – Quản lý quy định chi trả

## 1. Quy tắc được đưa vào hệ thống ở đâu?
Quy tắc được đưa vào **Database**, không hard-code trong source code.

```text
Khách hàng / văn bản quy định
        ↓
Chuẩn hóa thành Business Rule
        ↓
Admin nhập rule qua UI hoặc API
        ↓
SQLite: quy_tac_tra_luong
        ↓
Rule Engine
```

Trong giai đoạn phát triển chưa có quy định thật, có thể dùng `Mock Business Rules`.

## 2. Có thể đổi trạng thái một đơn vị sau khi hệ thống hoàn thành không?
Có.

Ví dụ hiện tại `DV01 → YES`, sau này đổi thành `DV01 → NO` thì không cần sửa source code.

### Prototype nhanh
```sql
UPDATE quy_tac_tra_luong
SET ket_qua = 'NO'
WHERE ma_don_vi = 'DV01' AND dang_ap_dung = 1;
```

### Khuyến nghị
Không ghi đè lịch sử:
1. Đóng rule cũ bằng `ngay_het_hieu_luc`
2. Tạo rule mới với `ngay_hieu_luc`
3. Rule Engine lấy rule phù hợp tại thời điểm tra cứu

Ví dụ:
```text
R001 | DV01 | YES | 2026-01-01 → 2026-09-30
R010 | DV01 | NO  | 2026-10-01 → NULL
```

## 3. Rule cấp đơn vị và loại đơn vị
Ví dụ chung:
```text
LOAI_A → YES
LOAI_B → NO
```

Ngoại lệ:
```text
DV15 thuộc LOAI_B
DV15 → YES
```

Rule Engine ưu tiên rule `DON_VI` trước `LOAI_DON_VI`.

## 4. API quản lý rule đề xuất
- `GET /rules`
- `POST /rules`
- `PUT /rules/{id}`
- `PATCH /rules/{id}/disable`
- `GET /rules/{id}`

## 5. UI quản trị đề xuất
Hiển thị:
- Mã quy tắc
- Phạm vi
- Đơn vị / loại đơn vị
- Kết quả
- Căn cứ
- Ngày hiệu lực
- Ngày hết hiệu lực
- Trạng thái

Nút:
- Thêm quy tắc
- Sửa
- Ngừng áp dụng
- Xem lịch sử

## 6. Căn cứ pháp lý
Nếu dùng văn bản thật, lưu tối thiểu:
- tên văn bản
- số/ký hiệu
- điều/khoản nếu có
- ngày hiệu lực
- ghi chú

Nhóm không tự sáng tác kết luận pháp lý. Quy tắc thật phải đến từ khách hàng hoặc nguồn pháp lý được xác định rõ.
