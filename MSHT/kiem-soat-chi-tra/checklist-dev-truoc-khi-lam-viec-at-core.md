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

## Mục 1 — Tìm lại tài liệu và hợp đồng

Làm trước tất cả. Có thể một nửa câu hỏi đã có sẵn đáp án.

- [x] ~~**Tìm tài liệu API của AT-Core.**~~ ✅ **XONG 08/09/2026** — founder cung cấp bản PDF
      *"[Tech] Partner Bank Gateway API Documentation and Functionality Overview"* (Confluence, 20/08/2026).
      Bản `.md`: [`at-core-partner-bank-gateway-api.md`](./at-core-partner-bank-gateway-api.md).
- [x] ~~**Đọc mục idempotency.**~~ ✅ **CÓ ĐÁP ÁN** — *"`txn_id` phải duy nhất theo partner"*, trùng
      trả `400`. Khoá là **`txn_id`**, không phải `request_id`. **Không cần hỏi đối tác nữa.**
- [x] ~~**Có endpoint nào client chưa bọc không?**~~ ✅ **CÓ — 16 endpoint, client bọc 7, luồng chi
      trả dùng 3.** Ba cái đáng chú ý: chuyển tiền hàng loạt *(B.2)* · kiểm tra số dư *(B.7)* ·
      kiểm tra TOS *(A.8)*. Xem bảng "MSHT dùng?" trong bản `.md`.
- [ ] **Vẫn thiếu: tài liệu xác thực đi kèm.** Bản này ghi *"Xác thực qua API Gateway (xem tài liệu
      xác thực đi kèm)"* — chưa có bản đó. Cần cho câu hỏi chữ ký callback.
- [ ] **Vẫn thiếu: mô tả callback/webhook.** Tài liệu này thuần API kéo, không nói gì về callback.
- [ ] **Lấy hợp đồng / phụ lục kỹ thuật đã ký.** Kiểm: có điều khoản nào về chống trùng, SLA phản hồi, hay thủ tục tra soát – thu hồi chưa?
- [ ] **Chốt mô hình thanh toán giữa hai bên: nạp tiền trước hay AT-Core ứng rồi quyết toán cuối kỳ?**
      Câu này quyết định "số dư tài khoản chi hộ" có phải khái niệm đúng không. Hỏi kế toán và hợp đồng, **không hỏi mã nguồn**.

> ⚠️ Nếu mô hình là quyết toán sau kỳ thì thứ cần xin là **bảng kê quyết toán**, không phải "số dư" —
> và yêu cầu số 2 phải viết lại theo đó.

---

## Mục 2 — Sửa lỗi phía mình trước

Những dòng dưới đây **không phải yêu cầu gửi đối tác**. Chúng là lỗi của MSHT và tự sửa được.

- [ ] **Bộ nhận callback đang trả lỗi `006` khi lệnh đã rời trạng thái chờ.**
      Bộ nhận idempotent đúng chuẩn phải trả **thành công** cho việc đã xử lý rồi. Trả lỗi khiến
      AT-Core không phân biệt được "đã nhận rồi" với "bên kia đang hỏng", và họ sẽ tiếp tục gửi lại.
      → Sửa `WithdrawUpdateStatusFromWebhook`, đừng đưa vào danh sách đòi đối tác.
- [ ] **`txn-inquiry` có trả `transfer_amount`, code đang bỏ qua.** Đọc và so với số đã yêu cầu.
      → Việc đối chiếu số tiền **không cần đối tác làm gì cả**.
- [ ] **`txn-inquiry` nhận cả `request_id`.** Dùng nó khi chưa có mã tham chiếu, thay vì bỏ qua lệnh.
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

## Mục 4 — Chốt cách sinh mã lệnh trước khi xin chống trùng

Nếu xin đối tác chống trùng theo mã của mình thì mã đó phải chịu được yêu cầu của họ.

- [ ] **Mã có tiền tố định danh sản phẩm chưa?** Nếu `creator-os` cũng dùng chi hộ của AT-Core
      (quyết định **D7** trong tài liệu phân tích) thì hai sản phẩm có thể sinh ra cùng một chuỗi.
- [ ] **Cam kết không tái sử dụng mã** — kể cả khi chạy lại đợt, kể cả sau khi khôi phục dữ liệu.
- [ ] **Độ dài tối đa AT-Core chấp nhận cho `request_id` là bao nhiêu?** Kiểm tài liệu, đừng đoán.
- [ ] **Đổi cách sinh mã có phá tra cứu lệnh cũ không?** Lệnh cũ mang ObjectID; cần giữ tra được cả hai dạng.
- [ ] **Mã có suy ngược ra thông tin khách không?** Nếu băm từ `(mã đợt, user)` thì cần chắc không lộ gì.

---

## Mục 5 — Câu hỏi thật sự chỉ AT-Core trả lời được

Sau khi làm xong mục 1–4, danh sách còn lại thường ngắn hơn nhiều.

- [ ] Nhận `fund-transfer` với `request_id` đã dùng → trả kết quả cũ hay tạo giao dịch mới?
- [ ] Nếu có chống trùng: theo `request_id` hay `txn_id`? Cửa sổ thời gian bao lâu?
- [ ] Có môi trường test để mình **tự chứng minh** điều đó không?
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

Ghi ra để khỏi đưa vào và bị bật lại.

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
