# Tính năng Hồ sơ Influencer cho Ambassador — Đăng ký kênh & Làm giàu dữ liệu (Enrich)

> Mang toàn bộ luồng "creator tự đăng ký kênh mạng xã hội và để hệ thống tự làm giàu dữ liệu hồ sơ" từ Techcombank (T-Fluencers) sang nền tảng Ambassador. Tài liệu mô tả vấn đề, giải pháp, lợi ích và phạm vi của việc nhân bản này.

**Ngày:** 11/06/2026
**Trạng thái:** Đề xuất
**Đối tượng đọc:** Business, Ops, PM
**Phạm vi:** Cổng creator của Ambassador (web) — phần hồ sơ influencer; **không** bao gồm màn hình admin xem/duyệt dữ liệu trên dashboard

---

## 1. Bối cảnh & vấn đề đang gặp

Ambassador là nền tảng vận hành chương trình đại sứ thương hiệu, dùng chung nền tảng công nghệ với T-Fluencers (Techcombank). Trên Ambassador, creator có thể đăng nhập và liên kết một kênh mạng xã hội để tham gia chương trình.

**Vấn đề hiện tại:** việc liên kết kênh trên Ambassador mới dừng ở mức **cơ bản** — hệ thống lưu lại đường link/tài khoản creator khai báo, nhưng:

- **Không xác minh quyền sở hữu kênh** một cách chặt chẽ → ai cũng có thể khai một kênh không phải của mình.
- **Không có dữ liệu hồ sơ đầy đủ** (số follower thật, lượt xem trung bình, tỷ lệ tương tác, lĩnh vực nội dung, nhân khẩu học khán giả). Đội vận hành phải tự tra cứu thủ công từng kênh.
- **Không có điểm đánh giá chất lượng kênh** để biết creator nào "đáng đầu tư".
- Creator **không thấy được trạng thái** kênh của mình sau khi đăng ký (đang chờ duyệt? đã đạt? bị từ chối vì sao?).

Trong khi đó, **T-Fluencers (Techcombank) đã xây dựng đầy đủ luồng này**: creator tự đăng ký kênh, hệ thống xác minh quyền sở hữu, rồi tự động gọi sang **AT-Core** để "làm giàu" (enrich) hồ sơ với dữ liệu chuyên sâu. Ambassador chưa có phần này.

> **Yêu cầu gốc:** clone toàn bộ chức năng influencer-profile từ Techcombank sang Ambassador, bao gồm luồng đăng ký kênh (creator tự nhập thông tin) và luồng làm giàu dữ liệu hồ sơ — **không** bao gồm phần admin xem dữ liệu trên dashboard.

---

## 2. Tại sao nên nhân bản từ T-Fluencers

### Hai nền tảng dùng chung nền móng công nghệ

Ambassador và T-Fluencers **cùng một bộ mã nguồn gốc**: cùng cách tổ chức backend, cùng kho dữ liệu (collection `user-socials` đã tồn tại ở cả hai), cùng công nghệ giao diện creator. Vì vậy:

- Phần "đăng ký kênh" trên Ambassador đã có sẵn khung — chỉ cần **nâng cấp** cho ngang bằng T-Fluencers.
- Phần "làm giàu dữ liệu" là **bổ sung mới** — nhưng logic đã được chứng minh chạy ổn ở T-Fluencers, **bê nguyên** thay vì làm lại từ đầu.

### Giá trị của việc làm giàu dữ liệu

Khi một creator chỉ khai báo một đường link, hệ thống gần như không biết gì về kênh đó. Sau khi **enrich** (làm giàu qua AT-Core), hệ thống có thêm:

- Số follower thật, lượt xem trung bình, tổng lượt xem/lượt thích.
- Tỷ lệ tương tác (engagement rate), điểm đánh giá chất lượng kênh (score).
- Lĩnh vực nội dung, nhân khẩu học khán giả (độ tuổi, giới tính, khu vực...).

Đây là cơ sở để Ambassador chọn đúng creator, phân nhóm chiến dịch và báo cáo cho thương hiệu.

---

## 3. Giải pháp đề xuất

### Tóm tắt giải pháp

Nhân bản từ T-Fluencers sang Ambassador **bốn mảnh ghép** của hồ sơ influencer phía creator:

1. **Đăng ký & xác minh kênh** — creator tự liên kết kênh và chứng minh quyền sở hữu.
2. **Khai báo hồ sơ (wizard)** — creator nhập thêm thông tin định tính về kênh và khán giả.
3. **Làm giàu dữ liệu (enrich)** — hệ thống tự động gọi AT-Core để lấy dữ liệu chuyên sâu.
4. **Hiển thị trạng thái** — creator theo dõi được kênh của mình đang ở bước nào.

### 3.1. Creator đăng ký & xác minh kênh

Creator vào trang hồ sơ, nhấn "Đăng ký kênh", chọn nền tảng. Mỗi nền tảng có cách xác minh quyền sở hữu riêng:

| Nền tảng | Cách creator cung cấp | Cách hệ thống xác minh |
|---|---|---|
| **TikTok** | Đăng nhập ủy quyền (OAuth) | Lấy thông tin kênh trực tiếp qua quyền creator cấp → xác minh tự động ngay |
| **YouTube** | Dán link kênh + thêm **hashtag định danh** vào mô tả kênh | Hệ thống đọc mô tả kênh, kiểm tra hashtag → xác minh ngay |
| **Facebook / Instagram** | Dán link hồ sơ + thêm hashtag định danh | Hệ thống crawl hồ sơ để kiểm tra → có thể cần chờ |

Sau khi xác minh, hệ thống lưu kênh vào hồ sơ creator với trạng thái tương ứng (chờ / đã đạt / từ chối) và ghi nhận quan hệ giữa creator – kênh – chương trình.

> **Lưu ý phạm vi nền tảng:** danh sách nền tảng hỗ trợ sẽ bám theo những gì Ambassador đang vận hành. Phần này sẽ chốt cụ thể khi làm tài liệu chi tiết — mặc định kế thừa bộ nền tảng của T-Fluencers (TikTok, YouTube, Facebook, Instagram).

### 3.2. Creator khai báo hồ sơ (wizard)

Sau khi liên kết kênh thành công, creator được mời nhập thêm thông tin **định tính** mà chỉ creator mới biết rõ:

- Lĩnh vực nội dung chính (tối đa vài hạng mục) và các lĩnh vực phụ.
- Ngôn ngữ nội dung, độ tuổi khán giả, giới tính, khu vực.
- Một vài thông tin liên hệ / hồ sơ cá nhân.

Thông tin này được lưu kèm hồ sơ influencer của creator, bổ sung cho dữ liệu hệ thống tự thu thập.

### 3.3. Hệ thống tự làm giàu dữ liệu (enrich) qua AT-Core

Đây là phần **giá trị nhất** và là điểm Ambassador đang thiếu.

**Cách hoạt động (creator không cần thao tác gì thêm):**

1. Sau khi kênh được liên kết, hệ thống **gửi kênh đó sang AT-Core** để yêu cầu làm giàu dữ liệu.
2. AT-Core xử lý **ở phía sau (bất đồng bộ)** — có thể mất từ vài giây đến vài phút.
3. Khi xong, AT-Core **gọi ngược về Ambassador** (webhook) để trả kết quả: số liệu kênh, điểm đánh giá, nhân khẩu học...
4. Ambassador lưu kết quả vào hồ sơ creator và đánh dấu kênh "đã làm giàu".

**Cơ chế an toàn:** nếu một yêu cầu bị "treo" (AT-Core không trả về sau một khoảng thời gian), hệ thống có **tác vụ định kỳ tự kiểm tra lại** và cập nhật khi có kết quả — đảm bảo không có hồ sơ nào bị kẹt vĩnh viễn.

> **Kết nối AT-Core:** Ambassador gọi AT-Core bằng **một bộ thông tin định danh đối tác dùng chung cho toàn nền tảng** (không tách riêng theo từng tenant). Đây là quyết định đã chốt ở giai đoạn này để đơn giản hóa; nếu sau này cần phân tách theo tenant thì xử lý ở bước nâng cấp riêng.

### 3.4. Creator theo dõi trạng thái kênh

Trên trang hồ sơ, creator nhìn thấy danh sách kênh đã đăng ký, nhóm theo nền tảng, kèm:

- Trạng thái xác minh (đang chờ / đã đạt / bị từ chối — kèm lý do).
- Số liệu kênh sau khi đã được làm giàu (follower, lượt xem, tương tác...).

Khi dữ liệu enrich về, trạng thái và số liệu tự cập nhật.

### 3.5. Ranh giới với luồng đăng bài (giữ y như hiện tại, không đụng tới) ⚠️

Đây là **khác biệt cốt lõi** giữa Ambassador và T-Fluencers, và là quyết định quan trọng nhất của tài liệu này.

**Bối cảnh:**

- Ở **T-Fluencers**, khi creator gửi bài đăng tham gia thử thách, hệ thống **bắt buộc với mọi nguồn** creator phải chọn một hồ sơ social **đã được duyệt** rồi mới cho đăng. Nói cách khác, "hồ sơ social" và "đăng bài" bị **buộc chặt vào nhau** ngay từ khâu kiểm tra đầu vào.
- Ở **Ambassador**, việc gắn hồ sơ social khi đăng bài là **có điều kiện, không đồng nhất**: với một số nguồn đặc biệt (ví dụ TikTok, Threads, Facebook post) thì **có** yêu cầu chọn tài khoản social; các nguồn còn lại thì **không**. Đây là hành vi đã có sẵn trong code Ambassador và đang chạy ổn định.

**Quyết định: giữ luồng đăng bài của Ambassador y như hiện tại — không thay đổi điều kiện gắn hồ sơ.**

Khi nhân bản influencer-profile, ta **giữ nguyên cách Ambassador đang xử lý**: nguồn nào đang require chọn social thì vẫn require, nguồn nào không require thì vẫn không. **Tuyệt đối không** thay luật này bằng ràng buộc "mọi nguồn đều phải chọn hồ sơ đã duyệt" của T-Fluencers. Lý do:

- Ràng buộc đồng loạt của T-Fluencers nằm ngay ở khâu **kiểm tra đầu vào khi đăng bài**. Nếu clone nguyên si, ta sẽ vô tình **siết toàn bộ các nguồn đang đăng bài tự do của Ambassador** — gây gãy một luồng đang chạy ổn định.
- Hồ sơ influencer và việc đăng bài là **hai lớp độc lập**: hồ sơ là "lớp dữ liệu làm giàu", còn đăng bài là "lớp hoạt động" với luật riêng đã có. Việc làm giàu hồ sơ **không** được thay đổi điều kiện đăng bài.

**Hệ quả thực tế:**

- Luồng đăng bài hiện tại của Ambassador **giữ nguyên 100%** — bao gồm cả các tình huống đang require chọn social lẫn các tình huống không require. Không thay đổi gì ở giai đoạn này.
- Hồ sơ influencer được xây như một **module song song**, không phải tiền đề bắt buộc mới của đăng bài.
- Nếu sau này muốn chuẩn hóa lại quy tắc "bài đăng ↔ hồ sơ" (ví dụ mở rộng/thu hẹp các nguồn cần chọn social, hay gán bài đăng cho đúng kênh phục vụ thống kê), đó là một **quyết định riêng ở giai đoạn sau**, cân nhắc kỹ tác động trước khi làm — **không** gộp vào lần nhân bản này.

### Luồng tổng quát

```
Creator đăng ký kênh
   → Hệ thống xác minh quyền sở hữu (OAuth / hashtag / crawl)
   → Lưu kênh vào hồ sơ creator
   → Creator khai báo thêm hồ sơ (wizard)
   → Hệ thống tự gửi kênh sang AT-Core để làm giàu
   → AT-Core xử lý phía sau → gọi webhook trả kết quả
   → Ambassador lưu dữ liệu giàu vào hồ sơ
   → Creator thấy trạng thái + số liệu cập nhật
```

---

## 4. Lợi ích kỳ vọng

### Cho creator
- ✅ Quy trình đăng ký kênh rõ ràng, biết chính xác kênh mình đang ở bước nào.
- ✅ Hồ sơ kênh được hiển thị chuyên nghiệp, có số liệu thật thay vì chỉ là một đường link.

### Cho hệ thống & dữ liệu
- ✅ Có dữ liệu hồ sơ đầy đủ, đáng tin (follower thật, tương tác, điểm chất lượng, nhân khẩu học).
- ✅ Quyền sở hữu kênh được xác minh → giảm gian lận, dữ liệu sạch hơn.
- ✅ Ambassador đạt mức ngang bằng T-Fluencers, thuận lợi cho định hướng dùng chung kho creator giữa các sản phẩm về sau.

### Cho vận hành
- ✅ Không còn phải tra cứu thủ công từng kênh — dữ liệu tự về qua AT-Core.
- ✅ Có cơ sở dữ liệu để chọn creator, phân nhóm chiến dịch và báo cáo cho thương hiệu.

---

## 5. Chi phí và rủi ro

### Chi phí

| Hạng mục | Ước tính |
|---|---|
| Nâng cấp luồng đăng ký kênh (cho ngang T-Fluencers) | Vừa — phần khung đã có sẵn trên Ambassador |
| Bổ sung luồng làm giàu + kết nối AT-Core (mới hoàn toàn) | Lớn hơn — thêm kho dữ liệu mới, webhook, tác vụ định kỳ |
| Giao diện creator (đăng ký kênh, wizard, xem trạng thái) | Vừa |
| *Ước tính effort chi tiết* | *Sẽ tính ở bước PRD/tech-spec* |

### Rủi ro & cách xử lý

| Rủi ro | Mức độ | Cách xử lý |
|---|---|---|
| Clone nguyên si T-Fluencers → vô tình bê ràng buộc "mọi nguồn đều phải chọn hồ sơ đã duyệt mới được đăng bài" → siết các nguồn đang đăng bài tự do của Ambassador | **Cao** | **Không** đổi luật kiểm tra đầu vào của đăng bài; giữ y như hiện tại — nguồn nào đang require thì require, không thì thôi (xem mục 3.5). Đây là điểm phải lưu ý hàng đầu khi triển khai |
| AT-Core không trả webhook (job treo) | Trung bình | Đã có tác vụ định kỳ tự kiểm tra lại và vớt job treo (kế thừa từ T-Fluencers) |
| Dữ liệu Ambassador hiện tại khác T-Fluencers ở chi tiết nhỏ → bê code không khớp 100% | Trung bình | Đối chiếu kỹ kho dữ liệu hai bên ở bước tech-spec; bổ sung trường còn thiếu thay vì copy mù |
| Phụ thuộc AT-Core (bên ngoài) cho dữ liệu cốt lõi | Trung bình | Luồng bất đồng bộ + cơ chế vớt job đảm bảo creator vẫn đăng ký được kể cả khi enrich chậm |
| Một bộ credential dùng chung cho mọi tenant → khó tách số liệu theo tenant sau này | Thấp–Trung bình | Chấp nhận ở giai đoạn này (đã chốt); nếu cần phân tách → xử lý ở bản nâng cấp riêng |
| Khác biệt nền tảng social được hỗ trợ giữa Ambassador và T-Fluencers | Thấp | Chốt danh sách nền tảng cụ thể ở bước chi tiết, bám theo thực tế Ambassador đang vận hành |

---

## 6. Phạm vi không bao gồm

Tài liệu này **không** đề cập:

- **Màn hình admin xem/duyệt dữ liệu trên dashboard** — đây là yêu cầu đã loại trừ rõ ràng. Chỉ làm phần phía creator.
- **Thay đổi luồng đăng bài hiện tại của Ambassador** — luồng đăng bài giữ **y như hiện tại**: các nguồn đang require chọn social thì vẫn require, còn lại không; **không** áp ràng buộc "mọi nguồn đều phải chọn hồ sơ đã duyệt" như T-Fluencers (xem mục 3.5). Việc chuẩn hóa lại quy tắc "bài đăng ↔ hồ sơ" để dành cho giai đoạn sau.
- **Báo cáo, thống kê tổng hợp, xếp hạng** dựa trên dữ liệu hồ sơ — nằm ngoài luồng đăng ký + enrich.
- **Thay đổi cách AT-Core tính toán/chấm điểm** — Ambassador chỉ là bên gọi và nhận kết quả, không can thiệp logic AT-Core.
- **Phân tách credential AT-Core theo từng tenant** — giai đoạn này dùng chung một bộ.
- Các luồng creator khác không liên quan tới hồ sơ (tham gia chiến dịch, hoa hồng, rút tiền...).

---

## 7. Tài liệu liên quan

- **Nguồn tham chiếu (T-Fluencers):** chức năng influencer-profile trong codebase Techcombank — luồng `LinkUserSocial`, kho dữ liệu `user-socials` / `user-social-partners` / `influencer-profiles`, webhook làm giàu từ AT-Core, và tác vụ vớt job treo.
- **Call chain:** Ambassador → AT-Core → influence-meter (giống mô hình T-Fluencers).
- **Bước kế tiếp:** xây dựng **PRD** (yêu cầu chức năng chi tiết + tiêu chí nghiệm thu → sinh test case) và **tech-spec** (đối chiếu kho dữ liệu hai bên, API contract với AT-Core, webhook, migration) trước khi triển khai.
