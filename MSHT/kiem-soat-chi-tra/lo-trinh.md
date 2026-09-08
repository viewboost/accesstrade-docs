# Kiểm soát chi trả MSHT — lộ trình

> **Trang đầu của bộ tài liệu này.** Đọc file này để nắm toàn cảnh, rồi mở file chi tiết khi cần.
> **Ngày:** 2026-09-08 · **Trạng thái:** chờ founder chốt **D1** và bộ số ở mục "Đang chặn".

---

## Project này là gì

**Không phải "sửa lỗi chi trùng".** Là dựng **hệ kiểm soát chi trả** cho MSHT:

> mỗi khoản tiền có danh tính rõ ràng · mọi trạng thái phản ánh đúng thực tế giao dịch ·
> mọi hành động đụng tiền cần bằng chứng · hệ tự phát hiện và chặn sai lệch trước khi tiền chảy tiếp.

Sự cố chi trùng vừa rồi là triệu chứng. Nguyên nhân là cả một lớp kiểm soát chưa từng được dựng.

---

## Bộ tài liệu

| File | Dành cho | Nội dung |
| --- | --- | --- |
| **`lo-trinh.md`** *(đang đọc)* | Tất cả | Toàn cảnh, thứ tự làm, cái gì đang chặn |
| [`phan-tich-va-giai-phap.md`](./phan-tich-va-giai-phap.md) | Founder · lãnh đạo | Bối cảnh · 10 vấn đề · sổ rủi ro · 7 mức ưu tiên · quyết định **D1–D7** |
| [`mo-hinh-payout-va-tieu-chi-nghiem-thu.md`](./mo-hinh-payout-va-tieu-chi-nghiem-thu.md) | Kỹ thuật · QA | Mô hình khái niệm · 10 bất biến **BB-1…BB-10** · tiêu chí nghiệm thu từng mốc |
| [`cong-cu-cho-van-hanh-chi-tra.md`](./cong-cu-cho-van-hanh-chi-tra.md) | Vận hành · sản phẩm | Nhịp làm việc hằng ngày · thao tác loại A/B · xử lý ca kẹt · 12 cảnh báo |
| [`at-core-partner-bank-gateway-api.md`](./at-core-partner-bank-gateway-api.md) | Kỹ thuật | **Tài liệu API AT-Core** — 16 endpoint, chuyển từ PDF |
| [`van-de-can-at-core-ho-tro.md`](./van-de-can-at-core-ho-tro.md) | Đối tác · sản phẩm | Bảng hợp đồng tích hợp · 4 việc cần AT-Core *(việc 1 đã có đáp án)* |
| [`checklist-dev-truoc-khi-lam-viec-at-core.md`](./checklist-dev-truoc-khi-lam-viec-at-core.md) | Kỹ thuật | Kiểm lại trước khi gửi gì cho đối tác — phần lớn là việc của mình |

---

## Ba làn chạy song song

```
Làn đối tác   ├── đàm phán AT-Core ─────────────────────────────────┤  bắt đầu NGÀY ĐẦU
Làn vận hành  ├── truy vấn tạm · quy tắc bấm nút · kịch bản khách ──┤  tuần đầu, không chờ gì
Làn xây       │   UT0 → UT1 → UT2 → UT3 ─── UT4 / UT5 ─── UT6       │
```

**Chỉ UT6 thật sự chờ đối tác.** Cuộc nói chuyện với AT-Core không được thành lý do dừng mọi thứ khác.

---

## Bảy mốc

| Mốc | Làm gì | Gỡ rủi ro | Chặn bởi |
| --- | --- | --- | --- |
| **UT0a** | **Vá bảo mật** — xoá 2 cửa chi tiền không có kiểm soát truy cập | — | Không gì |
| **UT0b** | **Đổi hành vi nghiệp vụ** — chặn tạo khoản mới khi còn khoản treo | — | Không gì |
| **UT1** | **Danh tính khoản chi ổn định** + khai sinh đợt | A · Chi trùng | **D7** |
| **UT2** | Tra AT-Core · đọc số tiền · trạng thái "chưa rõ kết quả" · van xả tạm gác | A · B · C | **D1**, **D6**, UT1 |
| **UT3** | Cổng chốt sổ đợt · đối soát lớp 1 · đèn báo khói | E · Lệch âm thầm | **D3**, **D4**, UT1 |
| **UT4** | Kênh chi tay thành kênh chính thức | C · Tiền kẹt | **D5**, UT1 |
| **UT5** | Phân quyền theo bước · bảng audit · phép đo ngược | D · Không thẩm quyền | UT1 |
| **UT6** | Đối soát lớp 2 với AT-Core | E | **AT-Core**, UT1 |

**UT1 là hòn đá góc.** Sáu mốc còn lại đều treo vào nó — không có danh tính khoản chi ổn định thì
không có gì để chặn, để đối soát, hay để gắn quyền.

> **Vì sao tách UT0a và UT0b.** Hai việc trông giống nhau nhưng khác loại: UT0a là vá bảo mật *(xoá
> đường không ai được phép gọi)* — chủ sở hữu kỹ thuật, phát hành gấp, quay lui không rủi ro.
> UT0b **đổi hành vi mà khách cảm nhận được** — cần vận hành biết trước, cần kịch bản trả lời, và
> quay lui phải cân nhắc. Gộp chung một "P0" làm chúng trông như cùng một loại việc.

### Bốn cổng phát hành

Cách founder theo dõi: **"đang ở cổng nào"**. Cổng là lát cắt nghiệp vụ chồng lên các mốc, không phải
cách chia thứ hai.

| Cổng | Nghĩa là | Gồm mốc |
| --- | --- | --- |
| **G1 · An toàn để GỬI** | Không tạo thêm khoản chi thứ hai nữa | UT0a, UT0b, UT1 |
| **G2 · An toàn để VẬN HÀNH** | Vận hành xử lý ca thường không cần kỹ sư | UT2 |
| **G3 · An toàn để CHẠY TIẾP** | Một sự cố không lan sang đợt kế | UT3 |
| **G4 · An toàn để MỞ RỘNG** | Chứng minh được tiền đã đi đúng | UT4, UT5, UT6 |

**Qua G1 nghĩa là sự cố vừa rồi không lặp lại được nữa**, kể cả khi mọi thứ khác chưa xong.

> Tiêu chí nghiệm thu từng mốc: xem
> [`mo-hinh-payout-va-tieu-chi-nghiem-thu.md`](./mo-hinh-payout-va-tieu-chi-nghiem-thu.md) mục 2.

---

## Ràng buộc quan trọng nhất về lịch

> ### 🔴 Khoảng cách UT0 → UT2 phải ngắn

UT0 chặn tạo khoản chi mới khi khách còn khoản đang treo. Nhưng khoản hỏng hiện **không bao giờ tự
kết thúc** — nên UT0 **tự nó sinh ra rủi ro C**: khách bị khoá vô hạn, tiền hoàn vẫn tích mà không
đợt nào chi được.

Van xả nằm ở UT2 *(thao tác tạm gác gỡ khách khỏi tình trạng bị chặn)*.

Càng để lâu giữa hai mốc, hàng đợi khiếu nại càng dài. Nếu không rút ngắn được thì **bắt buộc** phải
có quy trình tay tạm ở làn vận hành ngay từ tuần đầu.

---

## Tuần đầu — cụ thể

### UT0a — vá bảo mật, phát hành ngay

1. Xoá đường `PUT /api/withdraw/migration/withdraw/:id/approve` *(không xác thực, chi tiền được)*
2. Đưa `sandbox/trigger-auto-withdraw-with-user-ids` xuống **sau** `if IsRelease`

### UT0b — đổi hành vi, báo vận hành trước khi bật

3. Chặn tạo khoản chi mới khi khách còn khoản đang treo
   *(bật cùng lúc với việc 4–6 dưới đây, vì nó tạo ra rủi ro khách bị kẹt)*

### Làn vận hành — không cần một dòng mã nào ở service chi trả

4. Truy vấn lưu sẵn: danh sách khoản treo quá 24h kèm mã tra cứu
5. Văn bản một trang: khi nào được bấm đổi trạng thái tay, khi nào cấm, ai duyệt
6. Kịch bản trả lời khách cho ca "tiền chưa về"

### Làn đối tác — hai việc nền, làm trước khi gửi bất cứ gì

7. Tìm bản `api_gateway.md` của AT-Core — **có thể đã trả lời sẵn câu hỏi chống trùng**
8. Chốt mô hình thanh toán: nạp tiền trước, hay AT-Core ứng rồi quyết toán cuối kỳ

### Số liệu — lấy được ngay từ dữ liệu đang có

9. **Số tiền đang treo chưa rõ kết quả tại thời điểm này** *(con số quan trọng nhất để báo cáo)*
10. Quy mô một đợt · tổng chi mỗi ngày · số khách đang chờ và chờ bao lâu

---

## Đang chặn

| Chặn gì | Cần ai quyết | Hạn |
| --- | --- | --- |
| **D1** — khi chưa rõ đã chi hay chưa, mặc định là gì | **Founder** | Trước UT2 |
| **D2**, **D3**, **D4** — SLA treo · chốt sổ nghĩa là gì · ngưỡng chặn đợt sau | **Founder + vận hành + kế toán** | Trước UT3 |
| **D5** — đợt bù có chịu cùng cổng không | Founder + vận hành | Trước UT4 |
| **D6** — hạn mức 1,9 triệu/tháng còn hiệu lực không | Founder + pháp chế | Trước UT2 |
| **D7** — chung adapter AT-Core với `creator-os` không | **Founder** | Trước UT1 |
| Bộ số ở mục "Tuần đầu" | Vận hành + dữ liệu | Tuần này |
| **Thu hồi khoản chi sai có được không** | AT-Core trả lời | Hỏi sớm |
| Truy vấn giao dịch theo khoảng thời gian | AT-Core | **Yêu cầu DUY NHẤT còn lại** |

### D1 là câu gốc

Mọi thứ khác suy ra từ nó.

**Đề xuất của PO: coi như đã chi.** Thiệt hại hai chiều không cân nhau — chọn sai theo hướng đó thì
khách chờ thêm, có thể xin lỗi và bù. Chọn sai theo hướng kia thì mất tiền mặt, và **nhiều khả năng
không đòi lại được** vì tiền đã vào tài khoản khách tại ngân hàng.

Hệ hiện tại đang chọn *"coi như đã chi"* ở phần lõi nhưng chọn *"coi như chưa chi"* ở phần con người
đọc log. **Chính mâu thuẫn đó gây ra sự cố.**

### Và một câu có thể đảo toàn bộ khẩu vị rủi ro

Nếu AT-Core trả lời **không thu hồi được** khoản chi sai, thì chi trùng ≈ **mất trắng**. Khi đó mọi
trọng số dồn về phòng ngừa, và D1 gần như tự trả lời. Vì vậy hỏi câu này cùng lúc với câu chống trùng.

---

## Biết đã xong bằng năm số

| Nhóm | Số | Đích |
| --- | --- | --- |
| An toàn tài chính | Số khoản chi trùng | **0** |
| Độc lập vận hành | % ca xử lý xong không cần kỹ sư | → **95%** |
| Đối soát | Số tiền chưa đối soát | → **0** |
| Khách hàng | Tuổi khoản treo lâu nhất | Trong ngưỡng **D2** |
| Quản trị | % thao tác tiền có bằng chứng + audit | **100%** |

Chỉ số `Engineering intervention required for operational workflow = 0` *(mượn từ `creator-os` M1.7)*
giữ làm **dẫn đường**, nhưng **không dùng một mình** — nó đạt được bằng cách không cho ai làm gì cả.

---

## Lập luận mang theo khi xin nguồn lực

Chặng ngay **trước** chi trả — job thả tiền sau 60 ngày — **đã chống trùng đúng** bằng unique index
trên `transactionId`. Cùng pipeline, cùng đội. Chặng chi trả, chặng duy nhất tiêu tiền thật, thì không.

Và bước *"reconcile toàn bộ user cuối ngày"* **có trong PRD mà không được làm**.

⇒ Cả hai thứ đang gây mất tiền đều **từng được viết ra và bị bỏ qua**, không phải chưa ai nghĩ tới.
Đây là sự thiếu nhất quán, không phải giới hạn năng lực — và là lý do nên đóng dứt điểm lần này thay
vì lại ghi vào tài liệu rồi để đó.
