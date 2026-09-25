# Kiểm soát chi trả MSHT — kế hoạch triển khai

> Bản này nối [`phuong-an-nang-cap-chi-tra.md`](./phuong-an-nang-cap-chi-tra.md) (phương án, dành cho
> AccessTrade) với [`lo-trinh.md`](./lo-trinh.md) (mốc UT0a–UT6, cổng G1–G4, quyết định D1–D7).
>
> Điểm khác: bản này lấy **PHẦN VII — Đánh giá mức độ thực hiện** làm đầu vào, xếp lại công việc theo
> **thứ tự gỡ chặn** thay vì theo thứ tự nhóm chức năng, và chỉ rõ hạng mục nào **bắt đầu được ngay**,
> hạng mục nào **đang bị chặn**, hạng mục nào **chưa ước lượng được**.

---

## 1. Kết luận trước khi vào chi tiết

Đánh giá ở PHẦN VII nói 6 nhóm A–F đều *"có thể làm được"*, nhưng bốn ghi chú kèm theo cho thấy **ba
nhóm B, C, E thực chất đang treo vào cùng một câu hỏi chưa có lời đáp**:

> **Khi API SERVICE-AT timeout, MSHT không nhận được field kết quả — AT có thể đã đi tiền mà MSHT
> hoàn toàn không biết.**

Hệ quả dây chuyền:

| Nhóm | Ghi chú ở PHẦN VII | Vì sao bị chặn |
|---|---|---|
| **B** — Theo dõi & tra cứu | Đối chiếu qua 1 field của AT trả về; timeout là mất dấu | Không trả lời được *"đã chi hay chưa"* thì bảng tra cứu chỉ hiển thị phỏng đoán |
| **C** — Xử lý tình huống | "Chuyển sang đợt sau" = **REJECTED** lệnh chuyển tiền để refund về ví | REJECTED nhầm một khoản **đã đi thật** = chi trùng, đúng sự cố đang muốn chặn |
| **E** — Đối soát | MSHT không nắm thông tin chuyển khoản phía PARTNER | Không có số của đối tác thì không có lớp đối soát 2 và 3 |

⇒ **Đường găng của cả dự án không nằm ở code, mà nằm ở một thỏa thuận kỹ thuật với AT-Core.** Mọi
ngày trễ ở đây đẩy lùi B, C, E tương ứng. Đây là lý do làn đối tác phải khởi động **ngày đầu tiên**.

Ngoài ra có **hai hạng mục chưa đủ thông tin để cam kết**, phải có phase đánh giá riêng trước khi đưa
vào lịch — mục §6.

---

## 2. Phân loại 6 nhóm theo mức độ sẵn sàng

| Nhóm | Đánh giá PHẦN VII | Bắt đầu được ngay? | Điều kiện để bắt đầu |
|---|---|---|---|
| **A** — Định danh & quản lý khoản chi | Có thể thực hiện được | 🟢 **Có** | Chốt **D7** (chung adapter AT-Core với `creator-os` hay không) |
| **B** — Theo dõi & tra cứu | Có 1 phần cần kiểm tra lại | 🟡 **Một phần** | Phần tra cứu nội bộ làm được ngay; phần đối chiếu với AT chờ **CT-01** |
| **C** — Xử lý tình huống vận hành | Có thể làm được, **có rủi ro** | 🟡 **Một phần** | Thao tác không đụng tiền làm ngay; "chuyển đợt sau" chờ **CT-01** |
| **D** — Kiểm soát rủi ro | Có thể làm được | 🟢 **Có** | Sau Nhóm A (cần khái niệm "đợt" để chặn) |
| **E** — Đối soát | Có thể làm được, **cần SERVICE-AT hỗ trợ** | 🔴 **Chưa** | Lớp 1 nội bộ làm được sau A; lớp 2–3 chờ AT-Core cấp dữ liệu |
| **F** — Phân quyền & truy vết | Làm được nhưng **ảnh hưởng nhiều đến hệ thống API** | 🔴 **Chưa** | Cần phase khảo sát ảnh hưởng — §6.2 |
| **(mới)** — Quản lý dòng tiền người dùng | *"CẦN 1 PHASE đánh giá cái này"* | 🔴 **Chưa** | Cần phase đánh giá — §6.1 |

---

## 3. Đường găng — việc phải khởi động ngày đầu

### CT-01 · Thỏa thuận lại cơ chế xác định kết quả giao dịch với SERVICE-AT

**Vấn đề:** MSHT phụ thuộc một field trong response đồng bộ. Response không về (timeout, đứt mạng,
lỗi phía AT) thì MSHT mất dấu vĩnh viễn, trong khi tiền có thể đã đi.

**Cần đạt được — ít nhất một trong ba, tốt nhất là cả ba:**

| # | Nội dung | Vì sao cần |
|---|---|---|
| a | **Truy vấn kết quả giao dịch theo khoảng thời gian** (đã nêu ở PHẦN IV §4.1, *ưu tiên cao nhất*) | Cách duy nhất để tự đối chiếu lại sau khi mất dấu |
| b | **Tra cứu trạng thái theo mã tham chiếu của MSHT** | Trả lời được *"khoản này đã đi chưa"* cho từng ca |
| c | **Kênh callback / webhook báo kết quả** kèm tài liệu xác thực | Không phải hỏi mới biết; giảm cửa sổ mất dấu |

**Đầu ra:** biên bản thỏa thuận kỹ thuật có chữ ký hai bên, kèm đặc tả endpoint và môi trường thử.

**Chặn:** B (phần đối chiếu), C (chuyển đợt sau), E (lớp 2–3).

> **Nguyên tắc tạm thời trong lúc chờ:** áp **D1 — coi như đã chi** khi chưa rõ kết quả. PRD đã đề
> xuất phương án này (PHẦN VI §6.1) vì thiệt hại hai chiều không cân nhau. Cần founder chốt bằng văn
> bản **trước khi bật UT0b**, không đợi tới UT2.

### CT-02 · Xin dữ liệu chuyển khoản phía PARTNER

**Vấn đề:** MSHT chỉ giao tiếp với SERVICE-AT, không nắm thông tin chuyển khoản bên PARTNER — nên
không dựng được lớp đối soát 2 (với AT-Core) và lớp 3 (với ngân hàng).

**Cần đạt được:** định dạng và tần suất của bản kê giao dịch mà AT-Core có thể cấp cho MSHT (theo
ngày / theo đợt), tối thiểu gồm: mã tham chiếu, số tiền, thời điểm, trạng thái cuối, mã lỗi nếu có.

**Chặn:** E lớp 2 và 3, tức cổng **G4**.

---

## 4. Kế hoạch theo giai đoạn

Ước lượng dùng cỡ áo **S** (≤ 1 tuần-người) · **M** (1–2 tuần-người) · **L** (> 2 tuần-người).
**Các con số này là ước lượng ở mức PM — dev phải xác nhận lại trước khi cam kết lịch.**

### Giai đoạn 0 — Chặn máu · tuần 1

Mục tiêu: không tạo thêm khoản chi sai, và gỡ được khách bị kẹt bằng tay trong lúc chờ hệ thống.

| Mã | Việc | Đầu ra | Cỡ | Phụ thuộc | Vai trò |
|---|---|---|---|---|---|
| CT-03 | Xoá `PUT /api/withdraw/migration/withdraw/:id/approve` (không xác thực, chi tiền được) | PR + release gấp | S | — | BE |
| CT-04 | Đưa `sandbox/trigger-auto-withdraw-with-user-ids` xuống sau `if IsRelease` | PR + release gấp | S | — | BE |
| CT-05 | Chặn tạo khoản chi mới khi khách còn khoản treo | PR, bật cùng lúc CT-06→CT-08 | S | CT-06 sẵn sàng | BE |
| CT-06 | Truy vấn lưu sẵn: khoản treo quá 24h kèm mã tra cứu | Query + bảng theo dõi tay | S | — | Vận hành + dữ liệu |
| CT-07 | Văn bản 1 trang: khi nào được đổi trạng thái tay, khi nào cấm, ai duyệt | Quy trình tạm | S | — | Vận hành + PM |
| CT-08 | Kịch bản trả lời khách ca "tiền chưa về" | Kịch bản | S | — | Vận hành |
| CT-09 | Chốt số nền: **tiền đang treo chưa rõ kết quả**, quy mô một đợt, tổng chi/ngày, số khách đang chờ và chờ bao lâu | Báo cáo 1 trang | S | — | Dữ liệu + vận hành |
| **CT-01** | Khởi động thỏa thuận với AT-Core (§3) | Email + lịch họp kỹ thuật | S | — | PM + BE lead |
| **CT-02** | Khởi động xin dữ liệu PARTNER (§3) | Gửi cùng CT-01 | S | — | PM |

**Điều kiện ra:** CT-03/04 đã lên production · CT-05 bật kèm đủ quy trình tay · có con số ở CT-09 ·
đã gửi yêu cầu CT-01 và CT-02 cho AT-Core.

> ⚠️ **CT-05 tự nó sinh rủi ro**: chặn khách có khoản treo, mà khoản treo hiện không bao giờ tự kết
> thúc → khách bị khoá vô hạn. **Không bật CT-05 khi chưa có CT-06/07/08.**

### Giai đoạn 1 — Danh tính khoản chi · tuần 2–4 → cổng G1

Mục tiêu: hệ thống không thể tạo khoản chi thứ hai cho cùng một nghĩa vụ. Đây là **hòn đá góc** — năm
nhóm sau đều dựa vào.

| Mã | Việc | Đầu ra | Cỡ | Phụ thuộc | Vai trò |
|---|---|---|---|---|---|
| CT-10 | Mã định danh khoản chi duy nhất, bất biến suốt vòng đời (kể cả khi gửi lại / chuyển đợt) | Migration + model | M | **D7** | BE |
| CT-11 | Sổ "từng lần gửi": gửi lúc nào, nhận kết quả gì | Bảng attempt | M | CT-10 | BE |
| CT-12 | Khai sinh **đợt chi trả** là đối tượng có hồ sơ: số người, số tiền, giai đoạn | Model + CRUD | M | CT-10 | BE |
| CT-13 | Phân biệt trong dữ liệu: đợt **tự động** ↔ đợt **bù thủ công** | Trường phân loại | S | CT-12 | BE |
| CT-14 | Tách 2 thao tác khác bản chất: **tạo khoản mới** ↔ **gửi lại khoản đã có** | Refactor API | M | CT-10, CT-11 | BE |
| CT-15 | Rà soát và siết các đường chi tiền chưa có kiểm soát còn lại | Báo cáo + PR | M | — | BE + QC |
| CT-16 | Bộ test cho bất biến BB-1…BB-12 | Test suite | M | CT-10→CT-14 | QC |

**Điều kiện ra (G1):** không thể tạo khoản chi thứ hai cho cùng nghĩa vụ · mọi khoản chi có mã bất
biến · mọi lần gửi được ghi sổ · bộ test bất biến pass.

> **Qua G1 nghĩa là sự cố vừa rồi không lặp lại được nữa**, kể cả khi các giai đoạn sau chưa xong.

### Giai đoạn 2 — Vận hành tự chủ · tuần 4–7 → cổng G2

Mục tiêu: vận hành xử lý được phần lớn tình huống mà không cần kỹ sư.

Chia làm hai khối theo tình trạng chặn:

**2A — Làm được ngay, không chờ AT-Core**

| Mã | Việc | Đầu ra | Cỡ | Phụ thuộc | Vai trò |
|---|---|---|---|---|---|
| CT-17 | Bảng theo dõi đợt: tiến độ, số lượng, số tiền, so với đợt trước | Màn hình | M | CT-12 | BE + FE |
| CT-18 | Hồ sơ đầy đủ một khoản chi để trả lời khách | Màn hình chi tiết | M | CT-10, CT-11 | BE + FE |
| CT-19 | Trạng thái thứ ba: **"đã gửi nhưng chưa rõ kết quả"** — tách khỏi *chưa chi* và *đã chi* | Enum + hiển thị | S | CT-11 | BE + FE |
| CT-20 | Thao tác **không đụng tiền** cho vận hành: tạm gác, đánh dấu ưu tiên, ghi chú | Màn hình | M | CT-12 | BE + FE |
| CT-21 | SLA khoản treo: mốc cảnh báo, mốc chủ động liên hệ khách | Cấu hình + job | S | **D2** | BE |

**2B — Chờ CT-01 (thỏa thuận AT-Core)**

| Mã | Việc | Đầu ra | Cỡ | Phụ thuộc | Vai trò |
|---|---|---|---|---|---|
| CT-22 | Tra cứu tình trạng khoản chi **đối chiếu trực tiếp với AT-Core** | Tích hợp API | M | **CT-01** | BE |
| CT-23 | Đối chiếu **số tiền** thực chi với số tiền yêu cầu | Job + báo cáo lệch | M | CT-01, CT-22 | BE |
| CT-24 | **Chuyển khoản chi sang đợt sau** (REJECTED → refund về ví) | Luồng nghiệp vụ | M | **CT-01**, CT-22 | BE |

> ⚠️ **CT-24 là hạng mục rủi ro nhất giai đoạn này.** REJECTED một khoản đã đi thật = chi trùng. Chỉ
> mở CT-24 khi CT-22 đã chạy được và xác nhận được kết quả thật. Trước đó, "chuyển đợt sau" chỉ tồn
> tại dưới dạng **tạm gác** (CT-20) — không đụng tiền.

**Điều kiện ra (G2):** vận hành xử lý ca thường không cần kỹ sư · ba tình huống *chưa chi / đã chi /
chưa rõ kết quả* hiển thị tách bạch · van xả CT-20 đã hoạt động.

### Giai đoạn 3 — Không lan sự cố · tuần 7–10 → cổng G3

| Mã | Việc | Đầu ra | Cỡ | Phụ thuộc | Vai trò |
|---|---|---|---|---|---|
| CT-25 | **Cổng chốt sổ đợt**: đợt sau không chạy khi đợt trước chưa chốt | Gate + trạng thái đợt | M | CT-12, **D3** | BE |
| CT-26 | Điều chỉnh quy mô đợt (bắt đầu nhỏ, nâng dần) | Cấu hình | S | CT-12 | BE |
| CT-27 | **Công tắc dừng khẩn cấp** 2 mức: dừng một đợt · dừng toàn bộ chi tự động | Kill switch | S | CT-12 | BE |
| CT-28 | Cảnh báo tự động, mỗi cảnh báo có người chịu trách nhiệm | Bộ alert | M | CT-17, **D4** | BE + vận hành |
| CT-29 | **Đối soát lớp 1 (nội bộ)**: sổ chi trả ↔ số dư khách hàng | Job + báo cáo | M | CT-10, CT-12 | BE |
| CT-30 | Kênh **chi tay** thành kênh chính thức: cùng quy trình, có người duyệt, có đối soát | Luồng nghiệp vụ | M | CT-12, **D5** | BE + vận hành |

**Điều kiện ra (G3):** một sự cố ở đợt này không lan sang đợt sau · đối soát lớp 1 chạy định kỳ và
số lệch về 0 hoặc có hồ sơ giải thích.

### Giai đoạn 4 — Chứng minh được · tuần 10+ → cổng G4

| Mã | Việc | Đầu ra | Cỡ | Phụ thuộc | Vai trò |
|---|---|---|---|---|---|
| CT-31 | **Đối soát lớp 2** với AT-Core | Job + báo cáo | M | **CT-02** | BE + kế toán |
| CT-32 | **Đối soát lớp 3** với ngân hàng: tiền rời tài khoản ↔ tổng đã chi | Quy trình + báo cáo | M | **CT-02** | Kế toán |
| CT-33 | Phân quyền theo từng bước: tạo đợt · duyệt · chạy · chốt sổ · xử lý ngoại lệ | Phân quyền | L | **§6.2** | BE |
| CT-34 | **Nguyên tắc hai người** cho thao tác đụng tiền | Luồng duyệt | M | CT-33 | BE |
| CT-35 | Nhật ký đầy đủ: ai · lúc nào · khoản nào · đổi từ gì sang gì · **dựa trên bằng chứng nào** | Audit log | M | CT-33 | BE |

**Điều kiện ra (G4):** MSHT tự chứng minh được tiền đã đi đúng bằng số liệu · 100% thao tác đụng tiền
có bằng chứng.

---

## 5. Ba làn chạy song song

| Làn | Bắt đầu | Nội dung | Ai |
|---|---|---|---|
| **Phát triển** | Tuần 1 | Giai đoạn 0 → 4 ở §4 | BE · FE · QC |
| **Phối hợp AT-Core** | **Ngày 1** | CT-01, CT-02 — thời gian phản hồi của bên thứ ba dài nhất trong toàn kế hoạch | PM · BE lead |
| **Vận hành** | **Ngày 1** | CT-06→CT-08: quy trình tay, kịch bản trả lời khách, danh sách theo dõi thủ công — dùng trong lúc chờ hệ thống | Vận hành · PM |

> **Ràng buộc lịch quan trọng nhất:** khoảng cách từ **CT-05** (chặn tạo khoản mới) đến **CT-20** (van
> xả tạm gác) phải ngắn. CT-05 khoá khách có khoản treo, mà khoản treo hiện không tự kết thúc — càng
> để lâu, hàng đợi khiếu nại càng dài. Không rút ngắn được thì **bắt buộc** phải có quy trình tay
> CT-06→CT-08 ngay từ tuần đầu.

---

## 6. Hai hạng mục cần phase đánh giá trước khi cam kết

### 6.1 Quản lý dòng tiền người dùng

PHẦN VII ghi hai lần và ghi rõ *"CẦN 1 PHASE đánh giá cái này"*:

- Hệ thống **chưa có cơ chế quản lý dòng tiền người dùng** → không đối chiếu được một khoản chi xuất
  phát từ nguồn tiền nào để giải trình với khách.
- Kèm theo đó là **thời điểm tiền được chi**.

**Đề xuất phase đánh giá — 1 tuần, trước khi vào Giai đoạn 3:**

| Câu hỏi phải trả lời | Đầu ra |
|---|---|
| Hiện có những nguồn tiền nào vào ví khách (thưởng, hoàn, điều chỉnh tay…)? | Bảng liệt kê nguồn |
| Dữ liệu hiện tại có đủ dựng lại lịch sử dòng tiền không, hay phải ghi mới từ đây? | Kết luận có/không + phạm vi dữ liệu quá khứ |
| Cần thêm bảng/trường gì, ảnh hưởng tới luồng nào đang chạy? | Thiết kế sơ bộ + đánh giá ảnh hưởng |
| Chi phí ước lượng và vị trí trong lộ trình | Estimate + đề xuất mốc |

**Không đưa hạng mục này vào cam kết lịch khi chưa có đầu ra của phase đánh giá.**

### 6.2 Phân quyền và truy vết (Nhóm F)

PHẦN VII: *"có thể làm nhưng sẽ ảnh hưởng khá nhiều đến hệ thống API"*.

**Đề xuất phase khảo sát ảnh hưởng — 3–5 ngày, trước khi vào Giai đoạn 4:**

- Liệt kê toàn bộ endpoint đụng tiền và endpoint đọc dữ liệu chi trả.
- Với mỗi endpoint: ai đang gọi, đổi phân quyền thì hỏng gì.
- Phương án triển khai dần (bật theo vai trò / theo endpoint) thay vì đổi một lần.
- Estimate thật cho CT-33→CT-35.

> Ghi chú: MSHT không phải hệ đầu tiên làm việc này — PRD phân quyền của Ambassador
> (`ambassador/phan-quyen-van-hanh/`) đã xử lý đúng bài toán *"một luật phạm vi, fail-closed, nhật ký
> đủ để truy trách nhiệm"*. Nên tham khảo để khỏi thiết kế lại từ đầu.

---

## 7. Quyết định đang chặn

Lấy từ `lo-trinh.md` và PHẦN VI của PRD, bổ sung mốc theo kế hoạch này:

| Mã | Nội dung | Ai quyết | Chặn việc gì | Cần trước |
|---|---|---|---|---|
| **D7** | Chung adapter AT-Core với `creator-os` hay không | Founder | CT-10 | **Tuần 1** |
| **D1** | Khi chưa rõ đã chi hay chưa, mặc định là gì (*PRD đề xuất: coi như đã chi*) | Founder | CT-05, CT-19, CT-24 | **Trước khi bật CT-05** |
| **D6** | Hạn mức 1,9 triệu/tháng còn hiệu lực không | Founder + pháp chế | CT-22 | Trước Giai đoạn 2 |
| **D2** | Khoản chi được phép chờ tối đa bao lâu trước khi cảnh báo / liên hệ khách | Founder + vận hành | CT-21 | Trước Giai đoạn 2 |
| **D3** | "Chốt sổ đợt" nghĩa là gì | Founder + vận hành + kế toán | CT-25 | Trước Giai đoạn 3 |
| **D4** | Ngưỡng chặn đợt sau | Founder + vận hành + kế toán | CT-28 | Trước Giai đoạn 3 |
| **D5** | Đợt bù thủ công có chịu cùng cổng kiểm soát không | Founder + vận hành | CT-30 | Trước Giai đoạn 3 |
| **AT-1** | Thu hồi khoản chi sai có được không | AT-Core trả lời | Ảnh hưởng toàn bộ trọng số phòng ngừa | **Hỏi sớm** |
| **AT-2** | Truy vấn giao dịch theo khoảng thời gian | AT-Core | CT-22, CT-23, CT-24 | **Sớm nhất có thể** |
| **AT-3** | Bản kê giao dịch phía PARTNER | AT-Core | CT-31, CT-32 | Trước Giai đoạn 4 |

---

## 8. Rủi ro triển khai

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| AT-Core phản hồi chậm về CT-01 | B, C, E đứng; G2 và G4 trượt | Khởi động ngày 1; có phương án tạm D1 "coi như đã chi"; leo thang nếu quá 2 tuần không phản hồi |
| Bật CT-05 khi chưa có van xả | Khách bị khoá vô hạn, hàng đợi khiếu nại phình | Ràng buộc cứng: CT-05 chỉ bật cùng CT-06→CT-08 |
| Mở CT-24 khi chưa xác định được kết quả thật | **Chi trùng** — đúng sự cố đang muốn chặn | CT-24 phụ thuộc cứng vào CT-22; trước đó chỉ có tạm gác |
| Ước lượng Nhóm F sai vì chưa khảo sát | Vỡ lịch Giai đoạn 4 | Phase khảo sát §6.2 trước khi cam kết |
| Quản lý dòng tiền phát sinh ngoài dự kiến | Đội chi phí, đẩy lùi đối soát | Phase đánh giá §6.1; không cam kết khi chưa có đầu ra |
| Quyết định D1–D7 kéo dài | Mốc trượt dây chuyền | Mỗi quyết định gắn một mốc chặn cụ thể ở §7 |

---

## 9. Bảng theo dõi

Theo dõi theo **cổng**, không theo số lượng task hoàn thành:

| Cổng | Nghĩa là | Gồm | Điều kiện tuyên bố đạt |
|---|---|---|---|
| **G1 · An toàn để GỬI** | Không tạo thêm khoản chi thứ hai | CT-03→CT-05, CT-10→CT-16 | Bộ test bất biến pass; không còn đường chi tiền không kiểm soát |
| **G2 · An toàn để VẬN HÀNH** | Vận hành xử lý ca thường không cần kỹ sư | CT-17→CT-24 | Tỉ lệ ca cần kỹ sư giảm dưới ngưỡng thống nhất |
| **G3 · An toàn để CHẠY TIẾP** | Sự cố không lan sang đợt kế | CT-25→CT-30 | Đối soát lớp 1 chạy định kỳ, số lệch = 0 hoặc có hồ sơ |
| **G4 · An toàn để MỞ RỘNG** | Chứng minh được tiền đã đi đúng | CT-31→CT-35 | 100% thao tác đụng tiền có bằng chứng; đối soát 3 lớp đủ |

Chỉ số đo kết quả: xem PHẦN V của [`phuong-an-nang-cap-chi-tra.md`](./phuong-an-nang-cap-chi-tra.md).
Tiêu chí nghiệm thu từng mốc: xem [`mo-hinh-payout-va-tieu-chi-nghiem-thu.md`](./mo-hinh-payout-va-tieu-chi-nghiem-thu.md) mục 2.
