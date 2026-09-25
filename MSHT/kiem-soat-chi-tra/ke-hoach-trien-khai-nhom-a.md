# Kế hoạch triển khai — Nhóm A: Định danh và quản lý khoản chi

**Dự án:** Kiểm soát chi trả MSHT · **Giai đoạn:** 1 (mốc UT1) · **Cổng:** G1 — *An toàn để GỬI*

> **Mục tiêu:** Một nghĩa vụ với khách chỉ có thể tồn tại tối đa một khoản chi đang hoạt động; mọi khoản chi có mã bất biến suốt đời; mọi lần gửi được ghi sổ; mọi khoản chi thuộc về một đợt truy ngược được.

> **Qua được cổng G1 nghĩa là sự cố chi trùng không lặp lại được nữa**, kể cả khi các giai đoạn sau chưa xong.

### Kính nhờ review ba điểm

1. **Thứ tự ưu tiên** — Nhóm A đi trước năm nhóm còn lại; Sprint 0 gỡ chặn trước khi code.
2. **Mười quyết định đang chặn** ở mục ⛔ — mỗi quyết định kèm người quyết và hạn cụ thể.
3. **Giả định về đội và lịch** ở mục cuối — đây là phần DISO chưa có dữ liệu, cần xác nhận trước khi cam kết.

**Tài liệu nền:** [`phuong-an-nang-cap-chi-tra.md`](./phuong-an-nang-cap-chi-tra.md) (PHẦN III & VII) · [`lo-trinh.md`](./lo-trinh.md) · [`mo-hinh-payout-va-tieu-chi-nghiem-thu.md`](./mo-hinh-payout-va-tieu-chi-nghiem-thu.md) (bất biến BB-1…BB-12, tiêu chí nghiệm thu)

---

## 🎯 Cổng G1 — thước đo duy nhất

Báo cáo tiến độ bằng **số tiêu chí đã đạt**, không bằng số story đã xong. Story xong mà tiêu chí chưa đạt thì cổng chưa qua.

- [ ] **TC-1** · Một nghĩa vụ không tạo được hai khoản chi đang hoạt động — *BB-1* — `A1-S3`
- [ ] **TC-2** · Gửi lại một khoản chi không sinh `txn_id` mới — *BB-2* — `A1-S2` `A2-S4`
- [ ] **TC-3** · Dời khoản chi sang đợt khác thì `txn_id` không đổi — *BB-4* — `A2-S3`
- [ ] **TC-4** · 🔴 Gặp `400 txn_id trùng` thì gọi `txn-inquiry` lấy kết quả gốc, KHÔNG coi là thất bại rồi hoàn tiền — `A1-S5`
- [ ] **TC-5** · Mọi khoản chi thuộc đúng một đợt; truy được "đợt N gồm những khoản nào" — `A2-S1`
- [ ] **TC-6** · Truy được "khoản X thuộc đợt nào, gửi mấy lần, mỗi lần nhận gì" — `A1-S4` `A2-S6`
- [ ] **TC-7** · Đợt có mã, loại, phạm vi, người tạo, thời điểm, trạng thái vòng đời — `A2-S1`
- [ ] **TC-8** · Mã khoản chi có tiền tố định danh sản phẩm — *BB-10* — `A1-S2`
- [ ] **TC-9** · Đợt tự động và đợt bù tay phân biệt được trong dữ liệu — `A2-S2`

---

## Sprint 0 · 28/09 – 02/10 — Gỡ chặn trước khi code

Không phải sprint phát triển. **Không bắt đầu A1 khi 4 spike chưa có đầu ra.**

- [ ] **SP-1** · Chốt quyết định **D7** — chung adapter AT-Core với `creator-os` hay tách riêng · *BE lead* · 2đ
- [ ] **SP-2** · Khảo sát dữ liệu hiện trạng phục vụ backfill · *BE + dữ liệu* · 3đ
    - Tổng số khoản chi đang tồn tại · tỉ lệ đủ dữ liệu dựng lại danh tính · số khoản đang treo chưa rõ kết quả
- [ ] **SP-3** · 🔴 Xác minh hợp đồng `txn_id` trên môi trường thật · *BE* · 3đ
    - AT-Core có thật sự trả `400` khi trùng? `txn-inquiry` trả gì với `txn_id` đã tồn tại?
    - **Spike quan trọng nhất** — toàn bộ A1-S5 dựng trên giả định này. Sai thì epic cộng thêm 1 sprint.
- [ ] **SP-4** · Chốt quy tắc sinh mã khoản chi · *BE lead* · 2đ
    - Tiền tố định danh sản phẩm · độ dài · ký tự cho phép · giới hạn phía AT-Core

### Chạy song song — không nằm trong sprint phát triển

- [ ] **CT-01** · 🔴 Thỏa thuận cơ chế xác định kết quả giao dịch với SERVICE-AT · *PM* — **chặn cả Nhóm B, C, E**
- [ ] **CT-02** · Xin bản kê giao dịch phía PARTNER từ AT-Core · *PM*
- [ ] **CT-03** · Xoá endpoint `approve` không xác thực chi tiền được · *BE*
- [ ] **CT-04** · Đưa đường kích hoạt chi theo danh sách user xuống sau `IsRelease` · *BE*
- [ ] **CT-05** · Chặn tạo khoản chi mới khi khách còn khoản treo · *BE* — ⚠️ **chỉ bật khi CT-06/07/08 đã sẵn sàng**
- [ ] **CT-06** · Truy vấn lưu sẵn: khoản treo quá 24h kèm mã tra cứu · *Vận hành*
- [ ] **CT-07** · Văn bản 1 trang: khi nào được đổi trạng thái tay, khi nào cấm, ai duyệt · *PM*
- [ ] **CT-08** · Kịch bản trả lời khách ca "tiền chưa về" · *Vận hành*
- [ ] **CT-09** · Chốt bộ số nền để báo cáo · *Dữ liệu*

---

## Sprint A1 · 05/10 – 16/10 — Danh tính khoản chi

> **Sprint Goal:** Một nghĩa vụ không thể sinh ra khoản chi thứ hai khi khoản thứ nhất chưa kết thúc, và mã khoản chi không bao giờ đổi.

**39 điểm** — vượt velocity giả định 34, nên **A1-S6 là story tràn**, cắt trước nếu thiếu thời gian.

| Mã | Story | Điểm | Bất biến | Rủi ro |
| --- | --- | --- | --- | --- |
| A1-S1 | Mô hình dữ liệu tách bạch 4 thực thể | 8 | BB-2 | TB |
| A1-S2 | Sinh mã khoản chi bất biến có tiền tố sản phẩm | 5 | BB-2, BB-10 | TB |
| A1-S3 | Chặn một nghĩa vụ có hai khoản chi đang hoạt động | 5 | BB-1 | Cao |
| A1-S4 | Sổ lần gửi: ghi mỗi lượt gửi và kết quả nhận được | 5 | — | TB |
| A1-S5 | 🔴 Gặp `400` trùng thì tra kết quả giao dịch gốc | 8 | BB-3, BB-5 | Cao |
| A1-S6 | Backfill dữ liệu khoản chi đang tồn tại | 8 | — | Cao |

### Tiêu chí chấp nhận

- [ ] **A1-S1** — Có bảng cho Nghĩa vụ · Khoản chi · Lần gửi · Đợt; khoá ngoại đúng chiều; migration chạy được **và lùi được**; `txn_id` nằm ở **Khoản chi**, không nằm ở Lần gửi hay Đợt
- [ ] **A1-S2** — Mã đúng định dạng đã chốt; **không đổi** khi gửi lại; **không đổi** khi dời đợt; test sinh 10.000 mã không trùng
- [ ] **A1-S3** — Ràng buộc ở **cả DB và tầng service**; chạy đồng thời 50 request tạo khoản cho cùng nghĩa vụ → đúng 1 thành công, 49 bị từ chối kèm lý do đọc được
- [ ] **A1-S4** — Mỗi lượt gửi sinh 1 bản ghi: thời điểm, payload gửi, phản hồi nhận, mã lỗi; truy được lịch sử đầy đủ theo mã khoản chi
- [ ] **A1-S5** — Gặp `400` thì **bắt buộc** gọi `txn-inquiry`; **cấm** đường đi từ `400` sang hoàn tiền; có ca kiểm thử cho cả 3 kết quả inquiry; ghi audit mỗi lần inquiry
- [ ] **A1-S6** — Script chạy được trên bản sao production; tổng số khoản và tổng số tiền trước/sau **lệch = 0**; khoản không đủ dữ liệu đánh dấu riêng để xử lý tay, **không đoán**

**Demo cuối sprint:** tạo nghĩa vụ → tạo khoản chi → cố tạo khoản thứ hai (bị chặn) → gửi lần 1 giả lập timeout → gửi lại gặp `400` → hệ thống tự inquiry và hiển thị kết quả gốc.

---

## Sprint A2 · 19/10 – 30/10 — Đợt chi trả và tách thao tác

> **Sprint Goal:** Mọi khoản chi thuộc về đúng một đợt truy ngược được; dời khoản sang đợt khác không đổi danh tính; hệ thống phân biệt rõ "tạo khoản mới" với "gửi lại khoản đã có".

**32 điểm.**

| Mã | Story | Điểm | Bất biến | Rủi ro |
| --- | --- | --- | --- | --- |
| A2-S1 | Đợt chi trả là hồ sơ có danh tính | 8 | BB-9 | TB |
| A2-S2 | Phân biệt đợt tự động với đợt bù tay trong dữ liệu | 3 | — | Thấp |
| A2-S3 | Dời khoản chi sang đợt khác không đổi danh tính | 5 | BB-4 | TB |
| A2-S4 | Tách thao tác tạo khoản mới và gửi lại khoản đã có | 5 | BB-2 | Cao |
| A2-S5 | Trạng thái chỉ đi tới, cập nhật có điều kiện | 5 | BB-6 | Cao |
| A2-S6 | Truy vấn hồ sơ một khoản chi | 3 | — | Thấp |
| A2-S7 | Bộ test bất biến chạy tự động trong CI | 8 | BB-1,2,4,6,10 | Cao |

### Tiêu chí chấp nhận

- [ ] **A2-S1** — Đợt có mã, loại, phạm vi, người tạo, thời điểm, trạng thái vòng đời; truy được "đợt N gồm khoản nào"; **bổ sung trường kênh** `AT_CORE` / `CHI_TAY`
- [ ] **A2-S2** — Trường loại có 3 giá trị: tự động · bù tay · theo danh sách; phân biệt bằng truy vấn, **không chỉ khác thời điểm tạo**
- [ ] **A2-S3** — Dời đợt → mã khoản chi và `txn_id` **không đổi**; lịch sử lần gửi giữ nguyên; ghi audit ai dời, lúc nào, từ đợt nào sang đợt nào
- [ ] **A2-S4** — Hai luồng riêng, quyền riêng; **không** còn đường nào vừa tạo vừa gửi lại; gửi lại không sinh mã mới
- [ ] **A2-S5** — Mọi lệnh cập nhật mang điều kiện trạng thái hiện tại; ghi đè ngược bị từ chối; **có ca kiểm thử cho callback về giữa lúc đang xử lý**
- [ ] **A2-S6** — Một truy vấn trả đủ: đợt, số lần gửi, kết quả từng lần, trạng thái hiện tại; phản hồi dưới 2 giây với dữ liệu thật
- [ ] **A2-S7** — Test tự động cho BB-1, BB-2, BB-4, BB-6, BB-10; chạy trong CI; **đỏ là chặn merge**

> 💡 **Thêm một trường rẻ tiền, tránh nợ về sau:** bổ sung trường **kênh** (`AT_CORE` / `CHI_TAY`) ngay ở A2-S1. Chi phí gần như bằng không lúc này, nhưng thiếu nó thì khoản chi tay sau này bị báo lệch vĩnh viễn ở đối soát lớp 2.

---

## ⛔ Quyết định đang chặn

| Mã | Cần quyết | Ai | Chặn | Hạn |
| --- | --- | --- | --- | --- |
| **D7** | Chung adapter AT-Core với `creator-os` hay tách riêng | Founder | A1-S2 | 02/10 |
| **D1** | Chưa rõ đã chi hay chưa thì mặc định là gì — *đề xuất: coi như đã chi* | Founder | CT-05, A1-S5 | 30/09 |
| **AT-1** | Thu hồi khoản chi sai có được không | AT-Core | Trọng số phòng ngừa | 02/10 |
| **AT-2** | Truy vấn giao dịch theo khoảng thời gian | AT-Core | Nhóm B, C | 16/10 |
| **D6** | Hạn mức rút tiền theo tháng còn hiệu lực không | Founder + pháp chế | Giai đoạn 2 | 16/10 |
| **D2** | Khoản chi được chờ tối đa bao lâu | Founder + vận hành | Giai đoạn 2 | 16/10 |
| **D3** | "Chốt sổ đợt" nghĩa là gì | Founder + VH + KT | Giai đoạn 3 | 13/11 |
| **D4** | Ngưỡng chặn đợt sau | Founder + VH + KT | Giai đoạn 3 | 13/11 |
| **D5** | Đợt bù tay có chịu cùng cổng không | Founder + vận hành | Giai đoạn 3 | 13/11 |
| **AT-3** | Bản kê giao dịch phía PARTNER | AT-Core | Giai đoạn 4 | 27/11 |

---

## Definition of Ready / Done

**Ready** — story chỉ vào sprint khi:

- [ ] Tiêu chí chấp nhận **kiểm được bằng một phép thử**, không bằng ý kiến
- [ ] Đã chỉ rõ chạm vào bất biến **BB** nào
- [ ] Không còn phụ thuộc quyết định chưa chốt, hoặc đã có phương án tạm
- [ ] Đã đánh giá ảnh hưởng tới dữ liệu đang chạy

**Done** — story chỉ đóng khi:

- [ ] Code + test đơn vị, CI xanh
- [ ] **Test bất biến liên quan pass** — DoD riêng của epic này, không bỏ qua được
- [ ] Migration chạy được **và lùi được**, đã thử trên bản sao production
- [ ] Thao tác đụng tiền có bản ghi audit
- [ ] Vận hành được báo nếu hành vi khách cảm nhận được thay đổi
- [ ] Tài liệu cập nhật

---

## Nhịp làm việc

| Sự kiện | Khi nào | Bao lâu | Lưu ý riêng của epic |
| --- | --- | --- | --- |
| Planning | Thứ 2 đầu sprint | 2h | Rà lại D1–D7 còn chặn gì trước khi cam kết |
| Daily | Hằng ngày | 15' | Nêu rõ story nào đang chạm bất biến nào |
| Refinement | Giữa sprint | 1h | Chuẩn bị story sprint sau đạt DoR |
| Review | Thứ 6 cuối sprint | 1h | **Demo bằng kịch bản thật**, không demo màn hình tĩnh |
| Retro | Sau Review | 45' | |
| Đồng bộ AT-Core | Hằng tuần | 30' | Theo dõi CT-01 / CT-02 vì chúng chặn epic sau |

---

## ⚠️ Rủi ro

| Rủi ro | Dấu hiệu sớm | Cách giảm |
| --- | --- | --- |
| SP-3 cho kết quả khác giả định | Thử nghiệm Sprint 0 không ra kết quả mong đợi | Làm SP-3 **trước** khi lập kế hoạch A1; nếu sai, cộng 1 sprint |
| D7 chốt muộn | Hết Sprint 0 chưa có quyết định | A1-S1 vẫn làm được; chỉ A1-S2 phải chờ |
| Backfill lộ ra dữ liệu không đủ | SP-2 báo tỉ lệ thiếu cao | Đánh dấu riêng, xử lý tay — **không đoán** |
| Đội bị kéo sang chữa cháy | Velocity A1 dưới 70% cam kết | Quy trình tay CT-06→CT-08 để vận hành tự xử lý |
| Nén phạm vi, cắt A2-S7 | Có đề xuất "test sau cũng được" | **Không cắt A2-S7.** Thà cắt A2-S6 |

---

## Giả định cần xác nhận

| Hạng mục | Giả định | |
| --- | --- | --- |
| Sprint | 2 tuần | cần xác nhận |
| Đội | 2 BE · 1 QC · 1 PM bán thời gian | **cần xác nhận** |
| Velocity | 34 điểm/sprint | hiệu chỉnh sau A1 |
| Ngày bắt đầu | Sprint 0 từ 28/09/2026 | sửa lại nếu khác |

> Nếu đội thực tế nhỏ hơn giả định, **không nén sprint** — cắt phạm vi theo thứ tự ưu tiên. Nén ở epic này đồng nghĩa với bỏ bớt test bất biến, mà đó chính là thứ đang bảo vệ tiền.
