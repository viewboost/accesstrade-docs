# Tích hợp Gen-Green & Scalef — Đề xuất Hợp nhất Tài khoản

> **Dành cho:** Ban quản lý Vin, Team Gen-Green, Team Scalef
> **Ngày:** 2026-04-07
> **Người soạn:** AccessTrade (đơn vị vận hành chung)
> **Trạng thái:** Đề xuất — cần phê duyệt

---

## 1. Bối cảnh

### Gen-Green là gì?

Gen-Green là nền tảng sáng tạo nội dung của Vin. **~150.000 creators** đăng video, bài viết cho các thương hiệu thuộc hệ sinh thái Vin (VinPearl, Vincom, VinHome...) và nhận thu nhập dựa trên hiệu suất nội dung (lượt xem, tương tác).

### Scalef là gì?

Scalef là nền tảng affiliate (tiếp thị liên kết) riêng của Vin. **~1.000 publishers** chia sẻ link sản phẩm → khi có người mua hàng qua link → publisher nhận hoa hồng.

### AccessTrade đóng vai trò gì?

AccessTrade là đơn vị **vận hành chung** cho cả Gen-Green và Scalef:
- Vận hành hàng ngày cho cả 2 nền tảng
- **Chi trả thu nhập** cho creator/publisher trên cả 2 bên
- **Kê khai thuế TNCN** hộ creator/publisher trên cả 2 bên

### Cơ hội: Phát triển chéo giữa 2 nền tảng

Hai nền tảng đang hoạt động tách biệt, nhưng phục vụ **cùng một nhóm đối tượng** — những người muốn kiếm thu nhập online trong hệ sinh thái Vin. Tích hợp = mở ra cơ hội phát triển chéo cho cả 2 bên.

**Gen-Green → Scalef (lớn nhất):**
- 150.000 creators đang chỉ kiếm tiền từ nội dung. Nếu affiliate xuất hiện ngay trong Gen-Green, creator có thêm **nguồn thu nhập thứ 2 — hoa hồng bán hàng** — mà không cần rời khỏi nền tảng.
- Scalef hiện chỉ có 1.000 publishers và phải **tự thu hút** từng người. Tích hợp = mở cửa cho **150.000 creators tiềm năng** trở thành publisher — **tăng 150 lần** quy mô publisher pool mà Scalef không tốn chi phí acquisition.
- Creator Gen-Green đã có audience (người theo dõi trên TikTok, YouTube, Facebook). Khi creator chia sẻ link affiliate, link đó tiếp cận audience có sẵn — **tỷ lệ chuyển đổi cao hơn** so với publisher Scalef thông thường.
- Nội dung creator tạo cho chiến dịch Gen-Green (review sản phẩm, unbox, vlog) chính là ngữ cảnh tự nhiên nhất để gắn link affiliate. **Content + Affiliate kết hợp = hiệu quả nhân đôi.**

**Scalef → Gen-Green:**
- Affiliate mang lại **thêm nguồn thu nhập** cho creator → tăng lý do gắn bó với Gen-Green (retention).
- Creator thấy rõ mối liên hệ giữa nội dung hay → nhiều click → nhiều đơn → nhiều hoa hồng. **Động lực sáng tạo nội dung chất lượng hơn.**
- 1.000 publishers Scalef hiện tại (chưa dùng Gen-Green) trở thành user Gen-Green mới — có thể tham gia cả mảng nội dung.

**Tóm lại:** Gen-Green cung cấp user + audience cho Scalef. Scalef cung cấp thêm nguồn thu cho Gen-Green. Cả 2 bên đều lớn hơn khi gộp lại.

---

## 2. Vấn đề cần giải quyết

### 2.1 Hai hệ thống user hoàn toàn tách biệt

Hiện tại Gen-Green và Scalef là 2 nền tảng riêng, 2 hệ thống đăng ký/đăng nhập riêng, 2 cơ sở dữ liệu user riêng. Không có bất kỳ liên kết nào giữa 2 bên.

- **Gen-Green:** 150.000 creators — đăng ký riêng, đăng nhập riêng, database riêng.
- **Scalef:** 1.000 publishers — đăng ký riêng, đăng nhập riêng, database riêng.
- **Giữa 2 bên:** Không có liên kết nào.

Một người có thể có tài khoản ở cả 2 bên mà hệ thống **không biết đó là cùng 1 người**.

### 2.2 Rủi ro thuế TNCN — vấn đề pháp lý

AccessTrade kê khai thuế TNCN hộ creator/publisher ở **cả 2 nền tảng**. Theo luật, bậc thuế tính trên **tổng thu nhập từ cùng 1 người**.

**Ví dụ:** Creator Minh kiếm tiền trên cả 2 bên:

| Nguồn | Thu nhập/tháng |
|-------|---------------|
| Gen-Green (nội dung) | 5.000.000 đ |
| Scalef (hoa hồng) | 3.000.000 đ |
| **Tổng thực tế** | **8.000.000 đ** |

Nếu 2 hệ thống tách rời → AccessTrade tính thuế **riêng** cho từng nguồn → **áp sai bậc thuế** → vi phạm quy định. AccessTrade chịu trách nhiệm pháp lý.

**Để tính thuế đúng, phải nhận diện được "cùng 1 người" giữa 2 hệ thống.**

### 2.3 Trải nghiệm rời rạc cho creator

Creator muốn làm affiliate phải:
1. Biết Scalef tồn tại
2. Tự tìm đến Scalef, đăng ký tài khoản mới
3. Quản lý 2 tài khoản, 2 mật khẩu, 2 dashboard
4. Tự tổng hợp thu nhập nếu muốn biết tổng

Kết quả: trong 150.000 creators Gen-Green, chỉ ~1.000 người dùng Scalef. **Tỷ lệ chuyển đổi < 1%.**

---

## 3. Giải pháp đề xuất: Hợp nhất tài khoản

### Ý tưởng cốt lõi

> **Một người dùng = Một tài khoản.** Gen-Green là tài khoản gốc. Affiliate (Scalef) trở thành một tính năng bên trong Gen-Green, không phải một nền tảng riêng.

Thay vì duy trì 2 hệ thống user song song và tìm cách "nối" chúng lại, ta **gộp thành 1** — lấy Gen-Green (150K user) làm gốc, đưa 1K user Scalef vào.

### Đích đến

**1 tài khoản duy nhất (Gen-Green).** Creator đăng nhập 1 lần → thấy mọi thứ:

- **Thu nhập Nội dung:** lượt xem, tương tác, tiền thưởng từ chiến dịch content.
- **Thu nhập Bán hàng (affiliate):** click, đơn hàng, hoa hồng từ chiến dịch affiliate.
- **Thuế & Thanh toán:** tổng thu nhập = nội dung + bán hàng → 1 bảng kê thuế đúng bậc → 1 lần thanh toán/tháng.

### Tại sao chọn cách này?

**1. Thuế đúng luật — không cần "đối soát".**
1 tài khoản = 1 CCCD/MST = tổng thu nhập nằm cùng 1 nơi. Tính thuế trực tiếp, không cần module gộp thu nhập từ 2 nguồn, không sợ mapping sai.

**2. Chi phí vận hành = 0.**
Không còn: support ticket "không liên kết được", đối soát cross-platform hàng tháng, sync data khi user đổi thông tin, duy trì 2 hệ thống auth.

**3. Creator không cần biết Scalef tồn tại.**
Affiliate chỉ là 1 tính năng trong Gen-Green. Không cần giải thích "liên kết tài khoản", không cần SSO, không cần đăng nhập platform khác.

**4. Mở rộng tương lai dễ dàng.**
Vin thêm nền tảng mới (Booking, E-Shop, Referral...) → chỉ cần thêm module thu nhập, không cần thêm hệ thống user mới. 1 tài khoản phục vụ tất cả.

---

## 4. Lộ trình — 4 giai đoạn

Lộ trình được thiết kế theo nguyên tắc:
- **Mỗi giai đoạn go-live riêng**, mang lại giá trị ngay
- **Dừng được bất kỳ lúc nào** — hệ thống vẫn hoạt động tốt
- Giai đoạn sau xây trên nền giai đoạn trước, không phải xây lại

- **GĐ 1 — Ghép tài khoản** (Tháng 1, tuần 1–4)
- **GĐ 2 — 1 cửa đăng nhập** (Tháng 2, tuần 5–6)
- **GĐ 3 — Tài khoản chung (Vin Creator Portal)** (Tháng 2–3, tuần 7–12)

---

### Giai đoạn 1: Ghép tài khoản — Creator chủ động liên kết

> **Thời gian:** 4 tuần (Tuần 1–4)

**Mục tiêu:** Creator Gen-Green có thể ghép tài khoản Scalef (nếu có), tham gia chiến dịch affiliate, tạo link, xem báo cáo — tất cả ngay trong Gen-Green.

#### Creator làm gì?

1. Creator vào chiến dịch trên Gen-Green → thấy mục **"Chiến dịch Affiliate"** (bán hàng kiếm hoa hồng).
2. Bấm "Tham gia" → hệ thống yêu cầu ghép tài khoản Scalef.
   - Đã có tài khoản Scalef → đăng nhập Scalef → ghép xong.
   - Chưa có tài khoản Scalef → tạo mới (thông tin từ Gen-Green điền sẵn).
3. Tham gia chiến dịch → tạo link affiliate → chia sẻ → kiếm hoa hồng.
4. Kết quả bán hàng (click, đơn, hoa hồng) vẫn xem trên Scalef. Kết quả nội dung vẫn xem trên Gen-Green. Mỗi bên giữ report riêng.

#### ~1.000 user Scalef hiện tại xử lý thế nào?

| Tình huống | Cách xử lý |
|-----------|-----------|
| User Scalef cũng có tài khoản Gen-Green (trùng CCCD/SĐT) | Ghép tự động |
| User Scalef chưa có trên Gen-Green | Chờ user tự ghép, hoặc admin tạo tài khoản Gen-Green |
| Thông tin mâu thuẫn (CCCD khác nhau) | Admin xem xét |

#### Ai làm gì?

| Việc | Team |
|------|------|
| Cung cấp API (join campaign, tạo link) + sandbox | Scalef |
| Xây module gọi Scalef API | Gen-Green |
| Xây luồng ghép tài khoản (SSO) | Gen-Green |
| Giao diện affiliate trong chiến dịch (creator) | Gen-Green |
| Giao diện quản lý chiến dịch affiliate (admin) | Gen-Green |
| Khớp 1.000 user Scalef ↔ Gen-Green | AccessTrade |
| Test end-to-end | Cả 3 team |

#### Kết quả

- Creator tham gia affiliate và tạo link ngay trong Gen-Green
- Kết quả bán hàng vẫn xem trên Scalef, kết quả nội dung vẫn xem trên Gen-Green — mỗi bên giữ report riêng
- ~1K user Scalef hiện có được ghép vào Gen-Green
- **Hệ thống hoạt động được, nhưng vẫn tồn tại 2 hệ thống user song song**

---

### Giai đoạn 2: Một cửa đăng nhập — Bỏ auth riêng Scalef

> **Thời gian:** 2 tuần (Tuần 5–6)
> **Điều kiện:** GĐ 1 đã go-live

**Mục tiêu:** Mọi người dùng đều đăng nhập qua Gen-Green. Scalef không còn trang đăng ký/đăng nhập riêng. Dữ liệu report vẫn giữ ở 2 bên.

#### Thay đổi gì?

| Trước (GĐ 1) | Sau (GĐ 2) |
|---------------|-------------|
| Scalef có trang đăng nhập riêng | Scalef redirect về Gen-Green |
| Ai muốn dùng Scalef phải đăng ký Scalef | Đăng ký Gen-Green → dùng được Scalef |
| Một số user Scalef chưa ghép → vẫn dùng Scalef riêng | Tất cả user Scalef đều có tài khoản Gen-Green |

#### User Scalef còn lại (chưa ghép sau GĐ 1)?

- Trùng CCCD/SĐT với user Gen-Green → ghép tự động (admin review).
- Không trùng ai → tạo tài khoản Gen-Green mới từ data Scalef.
- Trùng nhiều user → admin xử lý thủ công.

#### Ai làm gì?

| Việc | Team |
|------|------|
| Tạo tài khoản Gen-Green cho user Scalef còn lại | AccessTrade + Gen-Green |
| Redirect trang login Scalef về Gen-Green | Scalef |
| Bỏ đăng ký mới trên Scalef | Scalef |
| Scalef xác thực bằng Gen-Green token (thay vì session riêng) | Scalef + Gen-Green |

#### Kết quả

- **1 cửa đăng nhập duy nhất** — Gen-Green
- Creator không cần biết Scalef tồn tại — affiliate chỉ là tính năng
- Scalef team bỏ gánh nặng quản lý user, tập trung vào core (campaign, tracking, hoa hồng)
- Dữ liệu report vẫn ở 2 bên (chưa gộp)

---

### Giai đoạn 3: Tài khoản chung — Tách user & dòng tiền ra hệ thống dùng chung

> **Thời gian:** 6 tuần (Tuần 7–12)
> **Điều kiện:** GĐ 2 đã go-live, tất cả user đã có tài khoản Gen-Green

**Mục tiêu:** Tách hệ thống user và dòng tiền (thu nhập, thuế, thanh toán) ra thành service dùng chung — **Vin Creator Portal**. Gen-Green và Scalef trở thành 2 service độc lập, cùng dùng chung 1 hệ thống tài khoản.

**Không gộp report.** Click, transaction, lượt xem, đơn hàng chi tiết — vẫn giữ ở mỗi service riêng. Gen-Green giữ report nội dung. Scalef giữ report affiliate. Đó là dữ liệu nghiệp vụ riêng của từng bên, không cần gộp.

#### Gộp cái gì, giữ riêng cái gì?

| Dữ liệu | Gộp về Portal | Giữ riêng |
|----------|:---:|:---:|
| **User profile** (tên, CCCD, MST, SĐT, email, bank) | x | |
| **Auth** (đăng nhập, session, token) | x | |
| **Dòng tiền tổng** (tổng thu nhập, bậc thuế, thanh toán, bảng kê) | x | |
| Report nội dung (lượt xem, like, comment, bài đăng) | | x (Gen-Green) |
| Report affiliate (click, conversion, đơn hàng chi tiết) | | x (Scalef) |
| Chiến dịch nội dung (campaign, event) | | x (Gen-Green) |
| Chiến dịch affiliate (campaign, link, tracking) | | x (Scalef) |

**Nguyên tắc:** Portal quản lý **"ai là ai"** và **"tổng tiền bao nhiêu"**. Mỗi service tự quản lý **"làm gì, kết quả ra sao"**.

#### Thay đổi gì?

| Trước (GĐ 2) | Sau (GĐ 3) |
|---------------|-------------|
| User thuộc về Gen-Green | User thuộc về **Vin** — service dùng chung |
| Thuế phải gộp thu nhập từ 2 nguồn riêng | Thuế tính trên 1 profile — tự động đúng |
| 2 chu kỳ thanh toán | 1 chu kỳ, 1 bảng kê |
| Report nội dung trên Gen-Green, report affiliate trên Scalef | **Giữ nguyên** — mỗi bên vẫn giữ report riêng |

#### Dòng tiền chảy thế nào?

**Trước GĐ 3:** Gen-Green tính thu nhập nội dung riêng. Scalef tính hoa hồng riêng. Muốn tổng hợp thuế phải gộp 2 nguồn theo CCCD/MST.

**Sau GĐ 3:** Gen-Green báo về Portal: "Creator A được 5 triệu từ nội dung tháng này." Scalef báo về Portal: "Creator A được 3 triệu hoa hồng tháng này." Portal tổng hợp: 8 triệu → tính thuế → thanh toán 1 lần. Mỗi service chỉ cần báo **số tiền**, không cần gửi chi tiết click hay transaction.

#### Vin Creator Portal gồm gì?

- **User & Auth:** Profile, CCCD/MST, thông tin ngân hàng — dùng chung cho mọi sản phẩm.
- **Dòng tiền tổng:** Mỗi service báo về tổng thu nhập theo kỳ. Portal gộp lại.
- **Thuế & Thanh toán:** Tính thuế trên tổng thu nhập 1 profile, 1 chu kỳ thanh toán, 1 bảng kê.

Gen-Green và Scalef vẫn là 2 service độc lập, giữ toàn bộ report nghiệp vụ riêng. Chỉ khác: đọc user từ Portal thay vì DB riêng, và báo dòng tiền về Portal thay vì tự xử lý thanh toán.

#### Ai làm gì?

| Việc | Team |
|------|------|
| Xây Vin Creator Portal (user service + income aggregation) | Gen-Green + Scalef |
| Migration user data từ Gen-Green sang Portal | Gen-Green + AccessTrade |
| Gen-Green đọc user từ Portal, báo thu nhập nội dung về Portal | Gen-Green |
| Scalef đọc user từ Portal, báo thu nhập affiliate về Portal | Scalef |
| Thanh toán hợp nhất: 1 chu kỳ, 1 bảng kê thuế | AccessTrade |
| Chạy thử trước (dry-run), so sánh tổng trước/sau | Cả 3 team |

#### Kết quả

- **Thuế TNCN tính trực tiếp trên 1 profile** — không cần module tổng hợp cross-platform, đúng luật 100%
- **1 chu kỳ thanh toán, 1 bảng kê** — giảm chi phí vận hành
- **User = tài sản của Vin** — không phụ thuộc bất kỳ platform nào
- **Mỗi service giữ nguyên report riêng** — không ảnh hưởng nghiệp vụ hiện tại
- **Mở rộng tương lai:** thêm sản phẩm mới (Booking, E-Shop...) = đăng ký vào Portal, không cần hệ thống user riêng
- Gen-Green trở về đúng vai trò: nền tảng nội dung
- Scalef trở về đúng vai trò: affiliate engine

---

## 5. Tổng hợp lộ trình

| | GĐ 1 | GĐ 2 | GĐ 3 |
|--|------|------|------|
| **Tên** | Ghép tài khoản | 1 cửa đăng nhập | Tài khoản chung (Vin Creator Portal) |
| **Thời gian** | 4 tuần | 2 tuần | 6 tuần |
| **Tổng cộng** | Tuần 1–4 | Tuần 5–6 | Tuần 7–12 |
| **Thay đổi chính** | Creator ghép tài khoản Scalef trong Gen-Green | Bỏ auth riêng Scalef | Tách user & dòng tiền ra Portal. Report giữ riêng ở mỗi service |
| **Creator thấy gì** | Affiliate xuất hiện trong chiến dịch | Không thấy khác biệt | 1 bảng kê thuế, 1 thanh toán |
| **Bài toán thuế** | Cần gộp thu nhập từ 2 nguồn | Như GĐ 1 | **Giải quyết triệt để** |
| **Dừng được không?** | Dừng được | Dừng được | Dừng được |
| **Bắt buộc?** | Có | Nên | Nên |

**Tổng thời gian: ~12 tuần (~3 tháng).** Mỗi giai đoạn go-live riêng.

---

## 6. Lợi ích theo từng đối tượng

### Cho Creator (150.000 người)

| Vấn đề hiện tại | Sau khi hoàn thành |
|-----------------|-------------------|
| Chỉ kiếm tiền từ nội dung | **Thêm nguồn thu từ hoa hồng bán hàng** |
| Muốn làm affiliate → phải biết và đăng ký Scalef | **Bấm "Tham gia" ngay trong Gen-Green** |
| 2 tài khoản, 2 mật khẩu, 2 dashboard | **1 tài khoản, 1 dashboard** |
| Có thể bị tính thuế sai bậc | **1 bảng kê thuế, đúng bậc** |
| 2 lần thanh toán/tháng | **1 lần thanh toán gộp** |

### Cho Ban quản lý / AccessTrade

| Vấn đề hiện tại | Sau khi hoàn thành |
|-----------------|-------------------|
| Rủi ro sai bậc thuế TNCN (vi phạm pháp luật) | **Thuế tính trên 1 profile — không thể sai** |
| 2 chu kỳ thanh toán, đối soát phức tạp | **1 chu kỳ, giảm chi phí vận hành** |
| Creator income = chỉ nội dung | **Creator income = nội dung + bán hàng** (tăng giá trị platform) |
| Thêm platform mới = thêm hệ thống liên kết | **Thêm platform mới = thêm module thu nhập** |

### Cho Team Scalef

| Vấn đề hiện tại | Sau khi hoàn thành |
|-----------------|-------------------|
| Chỉ 1.000 publishers, tự thu hút | **Tiếp cận 150.000 creators có sẵn** |
| Phải duy trì hệ thống user, auth, profile | **Tập trung 100% vào core: campaign, tracking, commission** |
| Publisher đăng ký rời rạc | **User có sẵn, không cần onboarding** |

### Cho Team Gen-Green

| Vấn đề hiện tại | Sau khi hoàn thành |
|-----------------|-------------------|
| Creator chỉ có 1 lý do ở lại (nội dung) | **Thêm affiliate = thêm lý do gắn bó** |
| Không biết creator nào làm affiliate | **Thấy toàn bộ hoạt động affiliate trong dashboard** |

---

## 7. Rủi ro & Biện pháp

| # | Rủi ro | Mức | GĐ | Biện pháp |
|---|--------|-----|-----|-----------|
| 1 | Scalef API chưa sẵn sàng | Cao | 1 | **Điều kiện tiên quyết** — không có API = không bắt đầu |
| 2 | Khớp sai user (CCCD/SĐT mâu thuẫn) | Trung bình | 1 | Check 3 bước (CCCD → SĐT → Email), ticket tự động khi reject, admin xử lý |
| 3 | Team Scalef không đồng ý bỏ auth riêng | Cao | 2 | Trình bày lợi ích: bỏ gánh nặng user management, tập trung core. Đây là quyết định cần Ban quản lý align |
| 4 | Mất/sai dữ liệu khi migration | Cao | 3 | Chạy thử trước (dry-run), cả 2 bên giữ data gốc làm backup, so sánh tổng trước/sau |
| 5 | Gián đoạn dịch vụ khi chuyển đổi | Trung bình | 3 | Chạy song song 2 nguồn (dual-write) trước khi cắt hẳn |
| 6 | GĐ 3 phức tạp (vừa merge data vừa tách service) | Trung bình | 3 | Chia nhỏ thành 2 phase nội bộ: xây Portal trước (tuần 7–9), migration data sau (tuần 10–12) |

---

## 8. Câu hỏi cho từng bên

### Cho Ban quản lý

1. Đồng ý hướng đi "1 tài khoản chung, Gen-Green làm gốc"?
2. Xác nhận AccessTrade tiếp tục là đơn vị chi trả và kê khai thuế cho cả 2 nền tảng?
3. Chu kỳ thanh toán hiện tại của 2 bên có giống nhau không?

### Cho Team Scalef

1. API specs đã sẵn sàng chưa? Gồm những API nào?
2. Có sandbox/staging để Gen-Green test không?
3. Cơ chế xác thực API: HMAC, API key, hay OAuth?
4. Sẵn sàng chuyển sang xác thực bằng Gen-Green token từ GĐ 2?

### Cho Team Gen-Green

1. Timeline dev team available?
2. Có sẵn module HTTP client tái sử dụng (retry, timeout, circuit breaker)?
3. Campaign/event model hiện tại cần bổ sung gì?

