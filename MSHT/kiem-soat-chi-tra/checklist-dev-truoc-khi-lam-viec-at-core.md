# Checklist cho dev — kiểm lại trước khi làm việc với AT-Core Chi hộ

> **Dùng khi nào:** cầm [`van-de-can-at-core-ho-tro.md`](./van-de-can-at-core-ho-tro.md) và chuẩn bị
> mở trao đổi với đối tác.
> **Vì sao có checklist này:** thử đóng vai đội AT-Core đọc yêu cầu của mình thì **một phần đáng kể
> là việc của mình, không phải của họ**. Đi đòi đối tác thứ mình tự gây ra thì mất uy tín và mất thời
> gian của cả hai bên.
>
> Cách dùng: mỗi dòng phải trả lời được **có / không / chưa biết**. Còn "chưa biết" thì chưa gửi gì
> cho đối tác.

---

## Mục 1 — Nền tài liệu

### Đã có

Đặc tả API của AT-Core: [`at-core-partner-bank-gateway-api.md`](./at-core-partner-bank-gateway-api.md).
Đặc tả trả lời hai câu vốn định hỏi đối tác:

- **Chống trùng:** `txn_id` phải duy nhất theo partner, trùng trả `400`. Khoá là `txn_id`, không phải
  `request_id`.
- **Bề mặt API:** 16 endpoint. Client Go bọc 7. Luồng chi trả dùng 3.

### Còn thiếu

- [ ] **Tài liệu xác thực đi kèm.** Đặc tả ghi *"xác thực qua API Gateway (xem tài liệu xác thực đi
      kèm)"* — chưa có bản đó. Cần cho câu hỏi chữ ký callback.
- [ ] **Mô tả kênh callback.** Đặc tả hiện có thuần API gọi chủ động.
- [ ] **Hợp đồng và phụ lục kỹ thuật đã ký.** Kiểm: có điều khoản nào về SLA phản hồi hay thủ tục
      tra soát – thu hồi chưa?
- [ ] **Mô hình thanh toán: nạp tiền trước hay quyết toán sau kỳ?**
      Quyết định nên đề nghị "số dư" hay "bảng kê quyết toán". Hỏi kế toán và hợp đồng.

---

## Mục 2 — Sửa lỗi phía mình trước

Những dòng dưới đây **không phải yêu cầu gửi đối tác**. Chúng là lỗi của MSHT và tự sửa được.

- [ ] **Bộ nhận callback đang trả lỗi `006` khi lệnh đã rời trạng thái chờ.**
      Bộ nhận idempotent đúng chuẩn phải trả **thành công** cho việc đã xử lý rồi. Trả lỗi khiến
      AT-Core không phân biệt được "đã nhận rồi" với "bên kia đang hỏng", và họ sẽ tiếp tục gửi lại.
      → Sửa `WithdrawUpdateStatusFromWebhook`, đừng đưa vào danh sách đòi đối tác.
- [ ] **`txn-inquiry` có trả `transfer_amount`, code đang bỏ qua.** Đọc và so với số đã yêu cầu.
      → Việc đối chiếu số tiền **không cần đối tác làm gì cả**.
- [ ] **`txn-inquiry` tra được bằng `txn_id`.** Dùng nó khi chưa có mã tham chiếu, thay vì bỏ qua
      lệnh. *(Đặc tả nhận `txn_id` hoặc `ref_txn_id`, không liệt kê `request_id`.)*
- [ ] **Hai API kiểm tra tài khoản chưa từng gọi** (`bank/account/info/check`, `bank/account/legal/check`).
      Xác định có nên bật không.
- [ ] **Xác minh đầu nhận callback có kiểm chữ ký không.** Chưa tìm thấy bước xác thực nào trong phần
      mã đọc được — cần kiểm tra tầng nhận HTTP ở communication/gateway. **Nếu thật sự không có chữ
      ký thì đây là lỗ bảo mật của mình**, và mới thành việc chung khi cần AT-Core ký.

---

## Mục 3 — Chuẩn bị số liệu trước khi xin năng lực mới

Đối tác sẽ hỏi ngay mấy con số này. Không có thì yêu cầu nằm đó.

- [ ] Số giao dịch mỗi ngày — trung bình và đỉnh.
- [ ] Tổng số tiền mỗi đợt — trung bình và đỉnh.
- [ ] Cửa sổ truy vấn cần dài bao nhiêu (một đợt? một ngày? bảy ngày?).
- [ ] Tần suất gọi dự kiến mỗi ngày.
- [ ] Có cần phân trang không, kích thước trang mong muốn.
- [ ] Định dạng mong muốn: API đồng bộ, hay file đẩy về theo lịch.
- [ ] Giờ mình cần dữ liệu sẵn sàng (ví dụ trước 03:00 để kịp chốt sổ trước đợt 07:00).

---

## Mục 4 — Chốt cách sinh `txn_id`

Chống trùng của đối tác khoá theo `txn_id`. Cách sinh mã quyết định hàng rào đó có hoạt động không.

- [ ] **Mã sinh từ khoản chi**, không từ lần gửi và không từ đợt — để gửi lại và dời đợt đều không đổi mã.
- [ ] **Mã có tiền tố định danh sản phẩm chưa?** Nếu `creator-os` cũng dùng chi hộ của AT-Core
      (quyết định **D7** trong tài liệu phân tích) thì hai sản phẩm có thể sinh ra cùng một chuỗi.
- [ ] **Cam kết không tái sử dụng mã** — kể cả khi chạy lại đợt, kể cả sau khi khôi phục dữ liệu.
- [ ] **Độ dài tối đa AT-Core chấp nhận cho `txn_id` là bao nhiêu?** Kiểm đặc tả, đừng đoán.
- [ ] **Đổi cách sinh mã có phá tra cứu lệnh cũ không?** Lệnh cũ mang ObjectID; cần giữ tra được cả hai dạng.
- [ ] **Mã có suy ngược ra thông tin khách không?**
- [ ] **Xử lý `400 txn_id trùng` đã đúng chưa?** Phải gọi `txn-inquiry` lấy kết quả gốc, không coi
      là thất bại rồi hoàn tiền.

---

## Mục 5 — Câu hỏi thật sự chỉ AT-Core trả lời được

Sau khi làm xong mục 1–4, danh sách còn lại thường ngắn hơn nhiều.

- [ ] **Cửa sổ chống trùng của `txn_id` kéo dài bao lâu** — vĩnh viễn hay có hạn?
- [ ] Có môi trường test để **tự chứng minh** hành vi chống trùng không?
- [ ] Có truy vấn kết quả theo khoảng thời gian không? Nếu chưa, chi phí và thời gian làm là bao nhiêu?
- [ ] **Có cổng tra cứu cho người vận hành không** (không phải API)? Xem
      [`cong-cu-cho-van-hanh-chi-tra.md`](./cong-cu-cho-van-hanh-chi-tra.md) mục 7.
- [ ] Có trang tình trạng dịch vụ để biết bên đó đang sự cố không?
- [ ] Chính sách gửi lại callback: mấy lần, cách nhau bao lâu, dừng khi nào?
- [ ] Callback có ký không? Ký bằng gì?
- [ ] **Thủ tục tra soát và thu hồi một khoản chi sai** — có tồn tại không, ai khởi tạo, bao lâu, ai chịu phí?

> ⚠️ Chuẩn bị tinh thần cho câu trả lời: tiền đã ghi có vào tài khoản khách hàng tại ngân hàng thì
> bên chi hộ **không rút ngược được**. Nếu đúng vậy thì **chi trùng gần như là mất trắng**, và toàn bộ
> trọng số phải dồn về phòng ngừa. Cập nhật lại mục rủi ro trong tài liệu phân tích khi có câu trả lời.

---

## Mục 6 — Ranh giới: những thứ KHÔNG hỏi

| Đừng hỏi | Vì sao |
| --- | --- |
| Thêm `transfer_amount` vào payload callback | Hợp đồng callback dùng chung nhiều đối tác, đổi là đổi cho tất cả. Mà `txn-inquiry` đã trả số tiền — gọi thêm một lần sau khi nhận callback là đủ |
| Sửa việc callback bị trả mã `006` | Đó là bộ nhận của mình chưa idempotent (mục 2) |
| Đối chiếu số tiền | Trường đã có sẵn, chỉ chưa đọc (mục 2) |

---

## Mục 7 — Trước khi bấm gửi

- [ ] Danh sách yêu cầu đã bỏ hết những gì thuộc mục 2 và mục 6 chưa?
- [ ] Mỗi yêu cầu còn lại có kèm **lý do nghiệp vụ** và **con số** chưa?
- [ ] Đã nêu rõ cái nào **chặn go-live an toàn**, cái nào là mong muốn?
- [ ] Có mốc thời gian mình cần, và hệ quả nếu trễ?
- [ ] Có người phía mình được chỉ định làm đầu mối, và người thay thế?
