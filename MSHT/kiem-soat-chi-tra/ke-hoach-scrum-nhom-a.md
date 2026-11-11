# Nhóm A — Kế hoạch Scrum: Định danh và quản lý khoản chi

> Epic này tương ứng **mốc UT1** trong [`lo-trinh.md`](./lo-trinh.md), **Giai đoạn 1** trong
> [`ke-hoach-trien-khai.md`](./ke-hoach-trien-khai.md), và là điều kiện để tuyên bố **cổng G1 — An toàn
> để GỬI**.
>
> Tiêu chí nghiệm thu gốc: [`mo-hinh-payout-va-tieu-chi-nghiem-thu.md`](./mo-hinh-payout-va-tieu-chi-nghiem-thu.md)
> mục 2 — *Ưu tiên 1: Danh tính và đợt* (9 tiêu chí) và các bất biến **BB-1, BB-2, BB-4, BB-6, BB-9, BB-10**.

---

## 1. Vì sao epic này đi trước

> **Nhóm A là hòn đá góc.** Năm nhóm còn lại đều treo vào nó — không có danh tính khoản chi ổn định
> thì không có gì để chặn, để đối soát, hay để gắn quyền.

Và quan trọng hơn: **qua được G1 nghĩa là sự cố chi trùng không lặp lại được nữa**, kể cả khi mọi thứ
khác chưa xong. Đây là epic duy nhất tự nó đã tạo ra giá trị bảo vệ.

**Sprint Goal tổng của epic:**

> *Một nghĩa vụ với khách chỉ có thể tồn tại tối đa một khoản chi đang hoạt động; mọi khoản chi có mã
> bất biến suốt đời; mọi lần gửi được ghi sổ; và mọi khoản chi đều thuộc về một đợt truy ngược được.*

---

## 2. Giả định về đội và nhịp — **cần xác nhận trước khi chốt lịch**

| Hạng mục | Giả định | Ghi chú |
|---|---|---|
| Độ dài sprint | **2 tuần** | Theo nhịp Scrum đang dùng của team |
| Số sprint cho epic | **2 sprint** (A1, A2) | Khớp khung "tuần 2–4" ở kế hoạch triển khai, cộng đệm |
| Đội | 2 BE · 1 QC · 1 PM (bán thời gian) | **Cần xác nhận** |
| Velocity giả định | **34 điểm/sprint** | Sprint đầu lấy 30 để trừ hao spike; hiệu chỉnh sau A1 |
| Tổng backlog epic | **71 điểm** | Chưa gồm spike |

> ⚠️ Nếu đội thực tế nhỏ hơn giả định, **không nén sprint** — cắt phạm vi theo thứ tự ưu tiên ở §5 và
> dời phần còn lại sang A3. Nén sprint ở epic này đồng nghĩa với việc bỏ bớt test bất biến, mà đó lại
> chính là thứ đang bảo vệ tiền.

---

## 3. Sprint 0 — Gỡ chặn trước khi code (3–5 ngày, chạy song song Giai đoạn 0)

Không phải sprint phát triển. Mục tiêu: **không bắt đầu A1 khi còn câu hỏi chặn mô hình dữ liệu.**

| Mã | Spike | Câu hỏi phải trả lời | Đầu ra | Ai |
|---|---|---|---|---|
| **SP-1** | Quyết định **D7** | Dùng chung adapter AT-Core với `creator-os` hay tách riêng? | Quyết định có văn bản | Founder + BE lead |
| **SP-2** | Khảo sát dữ liệu hiện trạng | Bao nhiêu khoản chi đang tồn tại? Có đủ dữ liệu để dựng lại danh tính không? Bao nhiêu khoản đang treo chưa rõ kết quả? | Báo cáo + số liệu backfill | BE + dữ liệu |
| **SP-3** | Xác minh hợp đồng `txn_id` | AT-Core trả `400` khi trùng — xác nhận trên môi trường thật; `txn-inquiry` trả gì với `txn_id` đã tồn tại? | Ghi chép kết quả thử nghiệm | BE |
| **SP-4** | Chốt quy tắc mã khoản chi | Tiền tố định danh sản phẩm là gì (BB-10)? Độ dài, ký tự cho phép, giới hạn của AT-Core? | Đặc tả 1 trang | BE lead + PM |

**Definition of Ready của epic** — A1 chỉ được bắt đầu khi cả 4 spike có đầu ra.

> **SP-3 là spike quan trọng nhất.** Toàn bộ cơ chế gửi lại dựa trên giả định *"gửi lại đúng `txn_id`
> cũ → AT-Core trả 400 → gọi `txn-inquiry` lấy kết quả gốc"*. Nếu giả định này sai trên môi trường
> thật, story **A1-S5** phải thiết kế lại và epic đội chi phí.

---

## 4. Sprint A1 — Danh tính khoản chi

**Sprint Goal:** *Một nghĩa vụ không thể sinh ra khoản chi thứ hai khi khoản thứ nhất chưa kết thúc,
và mã khoản chi không bao giờ đổi.*

**Điểm:** 39 — vượt velocity giả định, nên **A1-S6 là story tràn** (cắt trước nếu thiếu thời gian).

| Mã | User story | Tiêu chí chấp nhận | Điểm | BB |
|---|---|---|---|---|
| **A1-S1** | *Là kỹ sư, tôi cần mô hình dữ liệu tách bạch 4 thực thể để danh tính khoản chi không lẫn với lần gửi hay đợt.* | Có bảng cho **Nghĩa vụ · Khoản chi · Lần gửi · Đợt**; khoá ngoại đúng chiều; migration chạy được và lùi được; `txn_id` nằm ở **Khoản chi**, không nằm ở Lần gửi hay Đợt | 8 | BB-2 |
| **A1-S2** | *Là hệ thống, tôi cần sinh mã khoản chi bất biến có tiền tố sản phẩm để không đụng sản phẩm khác dùng chung AT-Core.* | Mã sinh đúng định dạng đã chốt ở SP-4; mã **không đổi** khi gửi lại; mã **không đổi** khi dời đợt; test sinh 10.000 mã không trùng | 5 | BB-2, BB-10 |
| **A1-S3** | *Là hệ thống, tôi cần chặn ở tầng dữ liệu việc một nghĩa vụ có hai khoản chi đang hoạt động.* | Ràng buộc **ở cả DB (unique partial index) và tầng service**; chạy đồng thời 50 request tạo khoản cho cùng nghĩa vụ → đúng 1 thành công, 49 bị từ chối kèm lý do đọc được | 5 | BB-1 |
| **A1-S4** | *Là vận hành, tôi cần biết một khoản chi đã gửi mấy lần và mỗi lần nhận kết quả gì.* | Mỗi lượt gửi sinh 1 bản ghi Lần gửi: thời điểm, payload gửi, phản hồi nhận, mã lỗi; truy được lịch sử đầy đủ theo mã khoản chi | 5 | — |
| **A1-S5** | 🔴 *Là hệ thống, khi gửi lại gặp `400 txn_id trùng`, tôi cần tra kết quả giao dịch gốc thay vì coi là thất bại.* | Gặp `400` → **bắt buộc** gọi `txn-inquiry`; **cấm** đường đi từ `400` sang hoàn tiền; có ca kiểm thử cho cả 3 kết quả inquiry (thành công / thất bại / chưa rõ); ghi audit mỗi lần inquiry | 8 | BB-3, BB-5 |
| **A1-S6** | *Là kỹ sư, tôi cần chuyển dữ liệu khoản chi đang tồn tại sang mô hình mới mà không làm sai lệch số tiền.* | Script backfill chạy được trên bản sao production; đối chiếu tổng số khoản và tổng số tiền trước/sau = 0 lệch; khoản không đủ dữ liệu được đánh dấu riêng để xử lý tay, **không đoán** | 8 | — |

**Sprint Review demo:** dựng kịch bản trực tiếp — tạo nghĩa vụ → tạo khoản chi → cố tạo khoản thứ hai
(bị chặn) → gửi lần 1 (giả lập timeout) → gửi lại (gặp 400) → hệ thống tự inquiry và hiển thị kết quả
gốc.

---

## 5. Sprint A2 — Đợt chi trả và tách thao tác

**Sprint Goal:** *Mọi khoản chi thuộc về đúng một đợt truy ngược được; dời khoản sang đợt khác không
đổi danh tính; và hệ thống phân biệt rõ "tạo khoản mới" với "gửi lại khoản đã có".*

**Điểm:** 32.

| Mã | User story | Tiêu chí chấp nhận | Điểm | BB |
|---|---|---|---|---|
| **A2-S1** | *Là vận hành, tôi cần mỗi đợt chi trả là một hồ sơ có danh tính để biết đợt gồm ai, bao nhiêu tiền, đang ở giai đoạn nào.* | Đợt có: mã · **loại** · phạm vi · người tạo · thời điểm · trạng thái vòng đời; truy được *"đợt N gồm những khoản nào"* | 8 | — |
| **A2-S2** | *Là kế toán, tôi cần phân biệt đợt tự động với đợt bù tay ngay trong dữ liệu.* | Trường loại có 3 giá trị: **tự động · bù tay · theo danh sách**; phân biệt được bằng truy vấn, **không chỉ khác thời điểm tạo**; báo cáo tách được theo loại | 3 | — |
| **A2-S3** | *Là vận hành, tôi cần dời một khoản chi sang đợt khác mà không làm đổi danh tính của nó.* | Dời đợt → mã khoản chi và `txn_id` **không đổi**; lịch sử Lần gửi giữ nguyên; ghi audit ai dời, lúc nào, từ đợt nào sang đợt nào | 5 | BB-4 |
| **A2-S4** | *Là hệ thống, tôi cần tách bạch hai thao tác khác bản chất: tạo khoản chi mới và gửi lại khoản đã có.* | Hai endpoint/luồng riêng, quyền riêng; **không** còn đường nào vừa tạo vừa gửi lại; gửi lại **không** sinh mã mới | 5 | BB-2 |
| **A2-S5** | *Là hệ thống, tôi cần trạng thái chỉ đi tới và mọi cập nhật đều kèm điều kiện trạng thái hiện tại.* | Mọi lệnh cập nhật mang điều kiện trạng thái; ghi đè ngược bị từ chối; **có ca kiểm thử cho tình huống callback về giữa lúc đang xử lý** | 5 | BB-6 |
| **A2-S6** | *Là vận hành, tôi cần tra được khoản X thuộc đợt nào, đã gửi mấy lần, mỗi lần nhận gì.* | Một truy vấn trả đủ: đợt · số lần gửi · kết quả từng lần · trạng thái hiện tại; phản hồi dưới 2 giây với dữ liệu thật | 3 | — |
| **A2-S7** | *Là QC, tôi cần bộ test bất biến chạy tự động để không ai phá vỡ các quy tắc này về sau.* | Test tự động cho **BB-1, BB-2, BB-4, BB-6, BB-10**; chạy trong CI; **đỏ là chặn merge** | 8 | — |

> **Thêm một trường rẻ tiền, tránh nợ về sau:** bổ sung trường **kênh** (`AT_CORE` / `CHI_TAY`) vào
> Khoản chi ngay ở A2-S1 — chi phí gần như bằng không lúc này, nhưng thiếu nó thì khoản chi tay sau
> này bị báo lệch vĩnh viễn ở đối soát lớp 2 (BB-9). Luồng chi tay vẫn thuộc Giai đoạn 3, chỉ thêm
> trường trước.

---

## 6. Definition of Ready / Definition of Done

**Definition of Ready** — story chỉ vào sprint khi:

- [ ] Có tiêu chí chấp nhận **kiểm được bằng một phép thử**, không phải bằng ý kiến.
- [ ] Đã chỉ rõ story chạm vào bất biến **BB** nào.
- [ ] Không còn phụ thuộc quyết định nào chưa chốt (D1–D7) hoặc phụ thuộc đó đã có phương án tạm.
- [ ] Ảnh hưởng tới dữ liệu đang chạy đã được đánh giá (cần backfill hay không).

**Definition of Done** — story chỉ đóng khi:

- [ ] Code + test đơn vị, CI xanh.
- [ ] **Test bất biến liên quan pass** — đây là DoD riêng của epic này, không bỏ qua được.
- [ ] Migration chạy được **và lùi được**, đã thử trên bản sao production.
- [ ] Thao tác đụng tiền có **bản ghi audit** (BB-7) — kể cả khi Nhóm F chưa làm.
- [ ] Vận hành được thông báo nếu hành vi khách cảm nhận được thay đổi.
- [ ] Tài liệu cập nhật: mô hình dữ liệu và tiêu chí nghiệm thu.

---

## 7. Nhịp làm việc

| Sự kiện | Khi nào | Bao lâu | Ai | Lưu ý riêng của epic này |
|---|---|---|---|---|
| Sprint Planning | Thứ 2 đầu sprint | 2h | Cả đội | Rà lại D1–D7 còn chặn gì trước khi cam kết |
| Daily | Hằng ngày | 15' | Đội phát triển | Nêu rõ story nào đang chạm bất biến nào |
| Refinement | Giữa sprint | 1h | Đội + PM | Chuẩn bị story sprint sau đạt DoR |
| Sprint Review | Thứ 6 cuối sprint | 1h | Đội + vận hành + kế toán | **Demo bằng kịch bản thật**, không demo bằng màn hình tĩnh |
| Retrospective | Sau Review | 45' | Đội | |
| **Điểm đồng bộ AT-Core** | Hằng tuần | 30' | PM + BE lead | Riêng epic này: theo dõi tiến độ CT-01/CT-02 vì chúng chặn epic sau |

---

## 8. Theo dõi tiến độ

Không theo dõi bằng số story đã xong, mà bằng **số tiêu chí nghiệm thu Ưu tiên 1 đã đạt** — 9 tiêu chí:

| # | Tiêu chí | Story | Trạng thái |
|---|---|---|---|
| 1 | Một nghĩa vụ không tạo được hai khoản chi đang hoạt động *(BB-1)* | A1-S3 | ⬜ |
| 2 | Gửi lại không sinh `txn_id` mới *(BB-2)* | A1-S2, A2-S4 | ⬜ |
| 3 | Dời đợt → `txn_id` không đổi *(BB-4)* | A2-S3 | ⬜ |
| 4 | 🔴 Gặp `400` trùng → gọi `txn-inquiry`, **không** hoàn tiền | A1-S5 | ⬜ |
| 5 | Mọi khoản chi thuộc đúng một đợt; truy được đợt gồm khoản nào | A2-S1 | ⬜ |
| 6 | Truy được khoản X thuộc đợt nào, gửi mấy lần, nhận gì | A1-S4, A2-S6 | ⬜ |
| 7 | Đợt có mã, loại, phạm vi, người tạo, thời điểm, trạng thái | A2-S1 | ⬜ |
| 8 | Mã khoản chi có tiền tố định danh sản phẩm *(BB-10)* | A1-S2 | ⬜ |
| 9 | Đợt tự động và bù tay phân biệt được trong dữ liệu | A2-S2 | ⬜ |

**Tuyên bố G1** khi cả 9 ô xanh **và** Ưu tiên 0 (Giai đoạn 0) đã xong.

---

## 9. Rủi ro của epic

| Rủi ro | Dấu hiệu sớm | Cách giảm |
|---|---|---|
| **SP-3 cho kết quả khác giả định** — AT-Core không trả kết quả gốc qua `txn-inquiry` | Thử nghiệm ở Sprint 0 không ra kết quả mong đợi | Làm SP-3 **trước** khi lập kế hoạch A1; nếu sai, A1-S5 thiết kế lại và epic cộng thêm 1 sprint |
| **D7 chốt muộn** | Hết Sprint 0 chưa có quyết định | A1-S1 vẫn làm được (mô hình dữ liệu không phụ thuộc D7); chỉ A1-S2 phải chờ |
| **Backfill lộ ra dữ liệu không đủ** để dựng lại danh tính | SP-2 báo tỉ lệ thiếu cao | Đánh dấu riêng nhóm không đủ dữ liệu, xử lý tay — **không đoán**; báo cáo quy mô cho founder |
| **Đội bị kéo sang việc chữa cháy** | Velocity sprint A1 thấp hơn 70% cam kết | Giai đoạn 0 đã có quy trình tay (CT-06→CT-08) để vận hành tự xử lý; PM giữ hàng rào |
| Nén phạm vi để kịp lịch, cắt A2-S7 | Đề xuất "test sau cũng được" | **Không cắt A2-S7.** Bộ test bất biến chính là thứ giữ cho G1 không bị phá về sau; thà cắt A2-S6 |

---

## 10. Việc chạy song song, không thuộc sprint

| Làn | Việc | Vì sao không đưa vào sprint |
|---|---|---|
| Đối tác | **CT-01** (thỏa thuận cơ chế xác định kết quả) · **CT-02** (dữ liệu PARTNER) | Phụ thuộc bên thứ ba, không kiểm soát được thời gian — nhưng **chặn epic sau**, nên PM theo dõi hằng tuần |
| Vận hành | CT-06 → CT-08 (quy trình tay, kịch bản trả lời khách) | Không cần một dòng mã nào ở service chi trả |
| Kỹ thuật | CT-03, CT-04 (vá bảo mật) | Đã phát hành ở Giai đoạn 0 trước khi epic bắt đầu |
