# Những điểm cần AT-Core Chi hộ phối hợp

> **Ngày:** 2026-09-08 · dựng từ đặc tả API của AT-Core và mã nguồn hai service `user`, `withdraw`.
>
> **Tham chiếu:** [`at-core-partner-bank-gateway-api.md`](./at-core-partner-bank-gateway-api.md) ·
> mã nguồn `msht/cb-mbbank` nhánh release · client đối tác `msht/cb-b2b/external/partnerapi/accesstrade`

---

## Tình trạng các yêu cầu

Đặc tả API của AT-Core cho thấy **phần lớn năng lực cần thiết đã có sẵn**. Chỉ ba điểm thật sự cần
đối tác phối hợp.

| Yêu cầu | Tình trạng |
| --- | --- |
| **Chống trùng khoản chi** | ✅ Đã có — `txn_id` duy nhất theo partner, trùng trả `400` |
| **Số dư tài khoản nguồn** | ✅ Đã có — `GET /v1.0/partner/balance` |
| **Chuyển tiền hàng loạt** | ✅ Đã có — `POST /v1.0/partner/fund-transfers` |
| **Kiểm tra tài khoản nhận** | ✅ Đã có — `GET .../bank/account/info/check` |
| **Kiểm tra điều khoản khách hàng** | ✅ Đã có — `GET .../bank/account/legal/check` |
| **Đối chiếu số tiền đã chi** | ✅ Đã có — `txn-inquiry` trả `transfer_amount` |
| **① Truy vấn theo khoảng thời gian** | ❗ **Cần AT-Core** |
| **② Hợp đồng callback** | ❗ **Cần AT-Core** |
| **③ Thủ tục sự cố và thu hồi** | ❗ **Cần AT-Core** |

---

## Điểm ① — Truy vấn kết quả giao dịch theo khoảng thời gian

**Ưu tiên cao nhất.** Đây là năng lực duy nhất AT-Core phải xây thêm.

### Cần gì

- Danh sách giao dịch trong khoảng `[từ, đến]` do MSHT chỉ định, mỗi dòng có `txn_id`, `ref_txn_id`,
  số tiền, trạng thái, thời điểm.
- Tổng số tiền đã chi trong khoảng đó.
- API hoặc file định kỳ đều được. Sẵn sàng trước giờ chốt sổ hằng ngày.

### Vì sao cần

Mô hình đích: **đợt sau không mở khi đợt trước chưa chốt sổ**. Muốn chốt sổ thì phải hỏi được
*"trong khoảng thời gian đó, bên anh đã chi những gì"* — chứ không phải tra từng giao dịch một.

Đây là thứ biến đối soát từ một báo cáo không ai đọc thành **cổng mở đợt kế tiếp**.

### Vì sao `txn-inquiry` không thay thế được

`txn-inquiry` chỉ tra được giao dịch mà MSHT **đã biết mã**. Nếu tồn tại một giao dịch bất thường mà
MSHT không biết là có, không câu hỏi nào phát hiện ra nó.

Truy vấn theo khoảng còn gánh thêm một vai: **phát hiện hai giao dịch cùng `txn_id`** — tức là kiểm
chứng được rằng hàng rào chống trùng của đối tác thật sự hoạt động.

### Ảnh hưởng nếu không có

Lớp đối soát với AT-Core không triển khai được. Các giai đoạn còn lại vẫn chạy bình thường.

### Số liệu cần chuẩn bị trước khi đề nghị

Đối tác sẽ hỏi ngay: số giao dịch mỗi ngày *(trung bình và đỉnh)* · độ dài cửa sổ truy vấn · tần
suất gọi · nhu cầu phân trang · giờ cần dữ liệu sẵn sàng.

---

## Điểm ② — Hợp đồng thông báo kết quả (callback)

Đặc tả API hiện có mô tả các lệnh gọi chủ động, **không mô tả kênh thông báo ngược**.

### Cần thống nhất

| Nội dung | Câu hỏi |
| --- | --- |
| Chính sách gửi lại | Gửi lại bao nhiêu lần, giãn cách bao lâu, dừng khi nào? |
| Mã xác nhận | Phản hồi nào có nghĩa là "đã nhận, đừng gửi nữa"? Phản hồi nào nghĩa là "gửi lại"? |
| Xác thực nguồn gốc | Thông báo có chữ ký không? Ký bằng gì? |
| Nội dung | Có thể bổ sung số tiền vào payload không, hay dùng `txn-inquiry` sau khi nhận? |

### Ghi chú về phía MSHT

Bộ nhận thông báo hiện trả mã lỗi khi giao dịch đã rời trạng thái chờ. Một bộ nhận đúng chuẩn phải
trả **thành công** cho việc đã xử lý rồi. **Đây là việc MSHT tự sửa**, không đưa vào danh sách đề
nghị đối tác.

---

## Điểm ③ — Thủ tục tra soát và xử lý khoản chi sai

### Cần xác định

- Có thủ tục thu hồi một khoản chi sai hay không.
- Nếu có: ai khởi tạo, thủ tục ra sao, thời gian xử lý, ai chịu chi phí.
- Đầu mối liên hệ hai bên và thời hạn phản hồi theo mức nghiêm trọng.
- AT-Core chủ động thông báo MSHT trong những trường hợp nào.
- Lịch bảo trì báo trước, để không trùng giờ chạy đợt.

### Vì sao đây là câu hỏi nghiệp vụ

Với mô hình chi hộ, khi tiền đã ghi có vào tài khoản khách hàng tại ngân hàng thì bên chi hộ không
có quyền rút ngược tài khoản người thụ hưởng.

Nếu câu trả lời là **không thu hồi được**, thì chi trùng tương đương mất trắng — và khẩu vị rủi ro
của cả hệ thống thay đổi: mọi trọng số dồn về phòng ngừa.

Vì vậy hỏi câu này **sớm**, cùng lúc với các câu kỹ thuật.

---

## Điểm ④ — Mong muốn thêm: cổng tra cứu cho đội vận hành

Mọi tra cứu sang AT-Core hiện đều đi qua hệ thống, tức là qua kỹ sư. Một cổng tra cứu dành cho người
vận hành sẽ giảm phụ thuộc kỹ thuật ở cả hai phía.

Mong muốn: tài khoản riêng cho vận hành *(không dùng chung tài khoản kỹ thuật)* · tra giao dịch theo
mã, theo khoảng thời gian, theo số tài khoản · xem trạng thái thật và lý do hỏng · tải file đối soát
theo kỳ · trang tình trạng dịch vụ · kênh báo sự cố có mã theo dõi.

---

## Bảng hợp đồng tích hợp

| Hạng mục | Hiện tại | Cần đạt | Ai làm |
| --- | --- | --- | --- |
| **Gửi lệnh** | | | |
| Ngữ nghĩa mã giao dịch | `txn_id` sinh mới mỗi lần gửi | Ổn định theo khoản chi, có tiền tố định danh sản phẩm | **MSHT** |
| Chống trùng | Đã có ở phía đối tác, MSHT chưa kích hoạt | Kích hoạt bằng mã ổn định | **MSHT** |
| Xử lý `400 txn_id trùng` | Coi là thất bại | Gọi `txn-inquiry` lấy kết quả gốc | **MSHT** |
| **Tra cứu** | | | |
| Đọc số tiền từ `txn-inquiry` | Bỏ qua trường `transfer_amount` | Đọc và đối chiếu | **MSHT** |
| Kiểm tra số dư trước đợt | Chưa gọi | Gọi trước mỗi đợt | **MSHT** |
| Truy vấn theo khoảng thời gian | Không có | Có | **AT-Core** |
| Cổng tra cứu cho vận hành | Không có | Có | **AT-Core** |
| **Callback** | | | |
| Bộ nhận idempotent | Trả lỗi khi đã xử lý | Trả thành công | **MSHT** |
| Chính sách gửi lại | Chưa thống nhất | Có văn bản | **AT-Core** |
| Chữ ký | Chưa xác minh | Xác định có hay không | Cả hai |
| **Sự cố** | | | |
| Đầu mối và thời hạn phản hồi | Không có | Có cam kết | Cả hai |
| Thủ tục thu hồi | Không rõ | Xác định có tồn tại hay không | **AT-Core** |

---

## Nền — chốt trước khi đề nghị

| Hạng mục | Tình trạng | Vì sao quan trọng |
| --- | --- | --- |
| **Mô hình thanh toán** — nạp trước hay quyết toán sau kỳ | Chưa xác định | Quyết định nên đề nghị "số dư" hay "bảng kê quyết toán" |
| **Tài liệu xác thực đi kèm** | Chưa có | Cần cho câu hỏi chữ ký callback |

Hai mục này chốt trước, vì chúng đổi nội dung của các đề nghị phía trên.

---

## Bối cảnh: câu hỏi chống trùng từng bị bỏ ngỏ

Tài liệu `MSHT/RASI/test_case_integration_transfer_for_at.md` mục 9, viết trước khi lên production,
đã nêu:

> *"Idempotency của refNumber/RequestID: nên có test partner nhận trùng RequestID (retry) không tạo
> giao dịch kép — cần partner/mock hỗ trợ."*

Mục này được đánh dấu cần đối tác hỗ trợ và không được đóng lại. Đặc tả API cho thấy hàng rào đã tồn
tại từ đầu — khoá là `txn_id`, và trùng thì bị từ chối.

Bài học cho quy trình: **đọc đặc tả của đối tác trước khi mở đề nghị thay đổi.**
