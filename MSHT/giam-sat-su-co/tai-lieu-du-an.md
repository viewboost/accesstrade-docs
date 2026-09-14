# Hệ giám sát và quản lý sự cố MSHT — tài liệu dự án

> **Trạng thái:** đề xuất dự án, chờ chốt chủ sở hữu và các quyết định ở Phần VI.
> **Ngày:** 2026-09-14 · **Bản:** 2 · **Vai trò soạn:** Project Manager
> **Phạm vi:** toàn bộ trải nghiệm MSHT — truy cập, đăng nhập, tiền hoàn, điều kiện rút —
> trên **mọi tenant ngân hàng** mà MSHT đang phục vụ.
>
> **Thay đổi ở bản 2:** bổ sung chiều đa tenant (mục 1.5) · ghi nhận cấu phần **M4 đã được
> hiện thực** và chuyển sang dạng kế thừa · thêm ràng buộc bắt buộc về dữ liệu (mục 3.4) ·
> giao lớp ③ cho M5 · thêm điều kiện áp dụng cho thứ tự giai đoạn.
>
> ⚠️ **Giới hạn:** tài liệu mô tả **bài toán và phương án**. Xem Phần VII mục 7.3 — danh sách
> điều còn phải kiểm chứng trước khi chốt phạm vi và ước lượng.

---

# PHẦN I — BỐI CẢNH

## 1.1 Hôm nay, khách hàng chính là hệ giám sát

Khi MSHT hỏng, thứ đầu tiên phát hiện ra không phải là biểu đồ, không phải cảnh báo, mà là **một
khách hàng gọi lên tổng đài**.

Điều đó có nghĩa là:

- Mọi sự cố đều được biết tới **muộn** — sau khi đã có người bị ảnh hưởng.
- Quy mô sự cố **luôn bị đánh giá thấp** — ta chỉ đếm được người chịu khó gọi.
- Sự cố chỉ **im lặng** khi người ta thôi gọi, không phải khi nó được sửa.

## 1.2 Và không có chỗ nào để ghi lại điều khách vừa nói

Đây mới là vấn đề gốc. Hôm nay một lỗi khách báo đi qua đường này:

```
Khách kêu  →  CSKH nghe  →  nhắn vào một nhóm chat  →  ai đó đọc  →  (có thể) hỏi kỹ sư
                                      │
                                      └──►  trôi khỏi màn hình sau 200 tin nhắn
```

Không có bước nào tạo ra **dữ liệu**. Kết quả là ba câu dưới đây, hôm nay **không ai trả lời được
bằng số**:

| Câu hỏi | Trả lời được không |
| --- | --- |
| Tuần này có bao nhiêu khách không rút được tiền? | ❌ |
| Lỗi "không vào được" tháng trước đã hết chưa, hay chỉ hết người kêu? | ❌ |
| Ba vấn đề khách kêu nhiều nhất là gì? | ❌ |

⇒ Không có số thì không ưu tiên được, không chứng minh được đã sửa xong, và **cùng một lỗi được báo
lại lần thứ ba vẫn bị xử lý như lần đầu**.

## 1.3 Hai loại "lỗi" khách báo, khác nhau về bản chất

Hai ví dụ được nêu khi mở dự án này thực ra **thuộc hai thế giới khác nhau**, và gộp chúng lại là
sai lầm đầu tiên cần tránh:

| | **"Vào web không được"** | **"Rút tiền bị chặn"** |
| --- | --- | --- |
| Bản chất | Hệ thống **hỏng** | Hệ thống **chạy đúng** |
| Nguyên nhân | Lỗi kỹ thuật, hạ tầng, webview, phiên đăng nhập | Một quy tắc nghiệp vụ đang chặn — và **không ai biết quy tắc nào** |
| Ai sửa được | Kỹ thuật | Vận hành, **nếu** họ biết lý do |
| Cách phát hiện | Đo từ bên ngoài, bắt lỗi phía khách | Đếm số lần quy tắc được kích hoạt |
| Hôm nay | Đã có công cụ đo *(xem M4)* | **Không ghi lại** |

> 🔴 **Loại thứ hai là loại nguy hiểm hơn**, vì nó không xuất hiện trong bất kỳ log lỗi nào. Hệ thống
> tự thấy mình khoẻ mạnh. Chỉ có khách là thấy mình không rút được tiền.
>
> Và nó **không thể** được phát hiện bằng công cụ đo phiên: một phiên "rút tiền bị chặn" là phiên
> vào được màn hình bình thường, khách bấm rút, một quy tắc từ chối, hệ thống chạy đúng như thiết
> kế. Trong mọi hệ đo kỹ thuật, phiên đó được ghi là **thành công**.

## 1.4 Vì sao là bây giờ

Ba lý do, và cả ba đều đắt thêm theo từng tháng trì hoãn:

**① Dữ liệu giám sát không hồi tố được.**
Lỗi khách báo tháng trước, nếu không ghi lại, thì **vĩnh viễn không đếm lại được**. Đây là loại dự án
mà giá trị nằm ở chuỗi số liệu tích luỹ — bắt đầu muộn một tháng không phải là trễ một tháng, mà là
mất hẳn một tháng dữ liệu nền. Và chính dữ liệu nền đó mới là thứ nói cho biết nên ưu tiên sửa gì
trước.

**② Chi phí đang được trả hằng ngày, bằng thời gian của người đắt nhất.**
Mỗi ca "khách bị chặn" hôm nay không có cách nào giải quyết ngoài việc hỏi người đọc được mã nguồn.
Đây không phải chi phí một lần khi có sự cố — đây là khoản trả đều mỗi ngày, và nó lớn dần theo số
lượng khách hàng.

**③ Sản phẩm nằm trong ứng dụng ngân hàng.**
Một sự cố kéo dài ở MSHT không chỉ là sự cố của MSHT — nó là trải nghiệm xấu mang thương hiệu của
ngân hàng đối tác. Ngưỡng chịu đựng của đối tác với loại sự cố *"phát hiện muộn vì không có giám
sát"* thấp hơn nhiều so với một sản phẩm độc lập.

## 1.5 MSHT là nhiều sản phẩm, không phải một

MSHT không chỉ chạy trong một ứng dụng ngân hàng. Cùng một nền tảng phục vụ webview hoàn tiền cho
**nhiều ngân hàng** — MBBank, VPBank, TPBank, và có thể thêm nữa.

Điều này thay đổi cách đọc mọi mục còn lại:

| Hệ quả | Nghĩa là |
| --- | --- |
| **"Khách hàng" là khách của nhiều tổ chức** | Không có một tập khách hàng chung |
| **CSKH là nhiều đội ở nhiều công ty** | Không chung quy trình, không chung công cụ, không chung người quản lý. Một quyết định về M1 phải hỏi: áp cho tenant nào |
| **Một sự cố có thể chạm một tenant hoặc tất cả** | Hai tình huống này cần hai cách xử lý, hai mức độ, hai đường báo cáo khác nhau |
| **Số liệu không tách tenant là số liệu vô nghĩa** | Gộp nhiều sản phẩm vào một bảng xếp hạng thì không dùng được cho việc gì |

⇒ **Mọi báo cáo, tín hiệu và sự cố trong tài liệu này đều phải đọc kèm một câu: tenant nào.**
Yêu cầu này được ghi thành bất biến **BB-6**.

Mặt tốt: cấu phần đã hiện thực (M4) **dùng chung cho mọi tenant**, nên chi phí chia cho số ngân
hàng. Đây là lập luận nên mang theo khi xin nguồn lực.

---

# PHẦN II — VẤN ĐỀ

## 2.1 Bốn lớp sự cố

| Lớp | Khách nói gì | Hôm nay phát hiện bằng | Nhóm chức năng phụ trách | Ai sửa |
| --- | --- | --- | --- | --- |
| **① Truy cập** | "Vào không được", "trắng trang", "đăng nhập lỗi" | Khách gọi · **M4 đo được phần lớn** | M3 + M4 | Kỹ thuật |
| **② Bị chặn** | "Không rút được tiền", "báo không đủ điều kiện" | Khách gọi | **M2** | Vận hành |
| **③ Sai số liệu** | "Mua rồi mà không thấy tiền hoàn", "số dư sai" | Khách gọi | **M5** | Vận hành + Sản phẩm |
| **④ Tiền không về** | "Đã báo thành công mà chưa nhận được" | Khách gọi | M5 + M6 | Vận hành |

Cột "nhóm chức năng phụ trách" là ràng buộc thiết kế: **mỗi lớp phải có ít nhất một nhóm nhận**.
Lớp không có ai nhận là lớp sẽ mãi mãi chỉ được phát hiện bằng cách khách gọi.

> **Ranh giới cần nói rõ ngay:** dự án này **phát hiện, ghi nhận và định tuyến** cả bốn lớp. Nó
> **không sửa nguyên nhân** — việc đó thuộc đội sở hữu từng mảng. Không nói rõ điều này ngay từ đầu
> thì dự án sẽ bị kéo vào việc sửa mọi thứ nó phát hiện ra, và không bao giờ hoàn thành.

## 2.2 Năm khoảng trống

### ① Không có nơi ghi nhận báo cáo của khách
Lỗi sống trong hội thoại, không sống trong dữ liệu. Không tra lại được, không đếm được, không gom
nhóm được.

### ② Quy tắc chặn không nói lý do
Khi một khách không rút được tiền, hệ thống biết chính xác vì sao — nhưng thông tin đó **không được
ghi lại ở đâu cả**. Vận hành không đọc được, khách không đọc được. Mỗi ca trở thành một cuộc điều tra
riêng, và đích đến luôn là đội kỹ thuật.

### ③ Không đo trải nghiệm thật của khách
Máy chủ trả lời bình thường **không có nghĩa là** khách vào được. Webview trong ứng dụng ngân hàng
có thể hỏng ở phía thiết bị, một phiên bản hệ điều hành, một dòng máy — và log phía máy chủ vẫn xanh
hoàn toàn.

*Khoảng trống này đã được lấp phần lớn bởi cấu phần M4 — xem mục 3.5.*

### ④ Không đo theo nghiệp vụ
Chỉ số hạ tầng không phát hiện được sự cố nghiệp vụ. *"Số khách rút tiền thành công trong giờ này
bằng 12% so với cùng giờ tuần trước"* là một cảnh báo. *"CPU 40%"* thì không.

### ⑤ Sự cố không có vòng đời
Không có trạng thái, không có chủ, không có thời hạn, không có kết luận. Nên không phân biệt được
**"đã sửa"** với **"hết người kêu"**, và cùng một nguyên nhân quay lại nhiều lần mà không ai nhận ra.

## 2.3 Rủi ro

| Mã | Rủi ro | Hệ quả | Mức |
| --- | --- | --- | --- |
| **R1** | Sự cố diện rộng kéo dài vì không ai biết | Hàng nghìn khách ảnh hưởng, phát hiện sau nhiều giờ | Nghiêm trọng |
| **R2** | Khách bị chặn âm thầm, không ai giải thích được | Khiếu nại leo thang, uy tín sản phẩm trong ứng dụng ngân hàng | Cao |
| **R3** | Không có số liệu để ưu tiên | Nguồn lực đổ vào việc kêu to nhất, không phải việc ảnh hưởng rộng nhất | Cao |
| **R4** | Tranh chấp trách nhiệm với ngân hàng khi khách không vào được | Mỗi sự cố thành một cuộc họp đổ lỗi, không ai đo được | Trung bình |
| **R5** | Lỗi lặp lại không bị nhận diện | Sửa đi sửa lại cùng một thứ | Trung bình |
| **R6** | **Số liệu trộn giữa các tenant** | Bảng xếp hạng gộp nhiều ngân hàng không dùng được cho quyết định nào; sự cố của một tenant bị pha loãng tới mức không nhìn thấy | Cao |

---

# PHẦN III — GIẢI PHÁP

## 3.1 Mục tiêu

> **MSHT tự biết mình đang hỏng ở đâu, trước khi khách hàng nói cho biết · và khi khách có nói, lời
> của họ trở thành dữ liệu chứ không phải một tin nhắn.**

## 3.2 Bốn nguyên tắc

**Ghi trước, đo sau.** Nơi ghi nhận báo cáo của khách phải có trước mọi biểu đồ. Không có nó thì các
biểu đồ không biết phải đo cái gì cho đúng.

**Đo theo nghiệp vụ, không theo hạ tầng.** Thước đo phải là *"bao nhiêu khách làm được việc này"*,
không phải *"máy chủ có sống không"*.

**Mỗi cảnh báo có một người và một hành động.** Cảnh báo không có người nhận và không có việc phải
làm sẽ bị bỏ qua — rồi kéo theo cả những cảnh báo thật bị bỏ qua cùng.

**Một vòng đời sự cố duy nhất.** Mọi lớp sự cố, mọi tenant đi qua cùng một quy trình, cùng một bộ
trạng thái. Hai quy trình song song là hai nơi để một sự cố lọt qua khe.

## 3.3 Mô hình khái niệm

```
   Khách báo  ─┐
               ├──►  BÁO CÁO  ──gom──►  SỰ CỐ  ──►  vòng đời  ──►  kết luận
   Máy phát hiện┘     (nhiều)           (một)
```

| Thực thể | Là gì | Ai tạo |
| --- | --- | --- |
| **Báo cáo** | Một lần có người nói "cái này hỏng" | CSKH / vận hành |
| **Tín hiệu** | Một lần máy tự phát hiện bất thường | Hệ thống |
| **Sự cố** | Vấn đề có thật, có phạm vi ảnh hưởng và có chủ | Người phân loại |

**Bất biến:**

| # | Nội dung |
| --- | --- |
| **BB-1** | Một sự cố gom **nhiều** báo cáo · một báo cáo thuộc **tối đa một** sự cố |
| **BB-2** | Mọi báo cáo đều gắn với **một khách hàng cụ thể** và **một thời điểm cụ thể** — không có hai thứ này thì không tra ngược được |
| **BB-3** | Sự cố chỉ đóng được khi có **kết luận**, không đóng bằng lý do "hết người báo". Kết luận được phép là *"không tái hiện được"* — nhưng phải nói ra, không được để trống |
| **BB-4** | Mỗi sự cố ghi lại **ai phát hiện: máy hay người** — đây là nguồn của chỉ số dẫn đường |
| **BB-5** | Mọi quy tắc chặn khách đều phát ra **mã lý do đọc được bằng máy** |
| **BB-6** | Mọi báo cáo, tín hiệu và sự cố đều gắn với **một tenant ngân hàng xác định** |

> **BB-1 là thứ biến giai thoại thành số liệu.** Không có nó thì *"năm khách kêu"* và *"một sự cố ảnh
> hưởng ba nghìn người"* trông giống hệt nhau trên báo cáo.
>
> **BB-4 là bất biến quan trọng nhất về mặt quản trị.** Không ghi lại nguồn phát hiện thì không bao
> giờ chứng minh được hệ giám sát có đang hoạt động hay không.

## 3.4 Ràng buộc bắt buộc về dữ liệu

Đây là ràng buộc **không được đánh đổi lấy tiến độ**. Sản phẩm nằm trong ứng dụng ngân hàng, và
**BB-2 bắt buộc mọi báo cáo gắn định danh khách** — nghĩa là kho dữ liệu giám sát chứa dữ liệu cá
nhân ngay từ ngày đầu tiên, kể cả khi chưa viết một dòng mã nào.

*Các ràng buộc dưới đây thống nhất với ràng buộc đã áp dụng ở cấu phần M4.*

### 3.4.1 Bảo vệ dữ liệu khách hàng

- **Mặc định-từ-chối**: chỉ những trường nằm trong danh sách trắng mới được thu thập.
- **Không thu bất kỳ dữ liệu nào suy ra được thông tin tài chính hoặc định danh nhạy cảm** — số dư,
  số tài khoản, số thẻ, giao dịch cụ thể.
- Đường dẫn phải **cắt bỏ toàn bộ phần truy vấn** trước khi ghi nhận — credential do ngân hàng cấp
  nằm ở đó.
- **Không bao giờ ghi mã OTP, mật khẩu, số CCCD.** Với M1 — nơi con người nhập tay — ràng buộc này
  phải in ngay trên biểu mẫu, không để trong tài liệu hướng dẫn riêng.

### 3.4.2 Nơi lưu và hạn lưu

- Dữ liệu giám sát nằm trên **hạ tầng tự vận hành**, không có bên thứ ba trên đường đi.
- Có **hạn lưu, tự động xoá**. Hạn cụ thể chốt theo từng kho.
- **Mỗi kỳ báo cáo phải chốt số tổng hợp và lưu ra ngoài kho trước khi dữ liệu gốc hết hạn.**
  Quên một kỳ là mất vĩnh viễn — nối thẳng với lý lẽ ở mục 1.4①: dữ liệu giám sát không hồi tố được.

### 3.4.3 Tính toàn vẹn của phép đo

- **Lỗi ghi 100%, không lấy mẫu.** Cần giảm tải thì giảm mức chi tiết, không giảm phạm vi phủ.
- 🔴 **Khoảng trống dữ liệu không được đọc là "ổn".** Mọi báo cáo phải phân biệt được **"không có
  lỗi"** với **"không thấy lỗi"**. Đây là ràng buộc chống lại kiểu hỏng nguy hiểm nhất của một hệ
  giám sát: tạo cảm giác an toàn giả.
- **Số đo từ ca diễn tập không trộn với số từ ca thật**, và không trình bày cạnh nhau kiểu "trước và
  sau". Diễn tập đo năng lực công cụ trong tay người đã biết trước câu trả lời.
- **Mọi chỉ số đọc kèm độ phủ.** Một tỉ lệ không kèm mẫu số là một con số không kiểm chứng được.

## 3.5 Sáu nhóm chức năng

### M1 — Nơi ghi nhận báo cáo *(đường vào)*

- **Một kênh tiếp nhận duy nhất** cho CSKH và vận hành — không ghi trong chat.
- Mỗi báo cáo bắt buộc có: **tenant ngân hàng · định danh khách · thời điểm · màn hình/thao tác ·
  phân loại · mô tả**.
- Trường **mã phiên** — lấy từ M4 khi tra được. Đây là chỗ hai hệ nối vào nhau: mã phiên biến một
  lời kể thành một bản ghi kỹ thuật tra được.
- **Gom báo cáo vào sự cố**, và tách ra được khi gom nhầm.
- **Tra ngược sang hồ sơ khách hàng** ngay từ báo cáo — không phải mở công cụ khác và gõ lại định danh.
- **Ràng buộc tốc độ:** nhập một báo cáo phải **nhanh hơn hoặc bằng việc gõ một tin nhắn chat**.
  CSKH đang nghe điện thoại khi ghi nhận; chậm hơn thì họ sẽ quay lại chat, và số liệu sẽ thiếu.

> Đây là giai đoạn rẻ nhất và bị bỏ qua nhiều nhất. Làm được bằng công cụ sẵn có trong vài ngày,
> **không cần sửa một dòng mã nào trong sản phẩm**.

### M2 — Mã lý do chặn *(giải quyết lớp ②)*

- **Mọi quy tắc đang chặn khách rút tiền đều phát ra một mã lý do** — số dư không đủ, chưa đủ thời
  hạn giữ, chưa đạt điều kiện tài khoản nhận, vượt hạn mức, và các quy tắc khác.
  *(Danh sách đầy đủ phải đọc từ mã nguồn — xem mục 7.3.)*
- **Hai người dùng, hai nhu cầu, phải nói rõ màn nào cho ai:** CSKH tra **một khách** trong lúc nghe
  điện thoại · vận hành **lọc theo lý do** để xử lý hàng loạt.
- **Yêu cầu tốc độ:** từ lúc mở màn tới lúc đọc được lý do — **không quá 3 thao tác và dưới 30 giây**.
  Đây là thứ neo tiêu chí nghiệm thu của giai đoạn 2, không phải một lời khuyên.
- 🔴 **Bắt buộc có trạng thái "không xác định được lý do"**, hiển thị rõ và phân biệt với "không bị
  chặn". Đếm số ca này như một chỉ số chất lượng của chính M2. Một màn trả về ô rỗng khiến người đọc
  kết luận sai mà vẫn tin mình đúng — **tệ hơn không có công cụ nào**.
- **Bảng xếp hạng lý do chặn theo ngày, tách theo tenant** — biến gánh nặng hỗ trợ thành tín hiệu
  giám sát.
- *(Giai đoạn sau)* hiển thị lý do cho chính khách — xem quyết định **G4**.

> **Đây là hạng mục có tỉ lệ giá trị trên công sức cao nhất của cả dự án**, và là hạng mục duy nhất
> giải được lớp ② — lớp mà không một công cụ đo kỹ thuật nào chạm tới được.

### M3 — Bấm thử từ bên ngoài *(bổ sung cho M4 ở lớp ①)*

- Một tác vụ tự động **đi lại hành trình của khách** theo lịch: mở trang · đăng nhập · xem số dư ·
  mở màn rút tiền. **Không chi tiền thật.**
- **Tần suất tối đa 5 phút một lần.** Đích *"phát hiện dưới 15 phút"* ở Phần V chỉ đạt được nếu tần
  suất đủ dày — chạy 30 phút một lần thì đích 15 phút không thể đạt về mặt số học.
- **Chạy cho từng tenant** — mỗi ngân hàng một hành trình riêng, một kết quả riêng.
- **Chạy từ ít nhất hai điểm**, chỉ báo động khi cả hai cùng hỏng — tránh báo động giả do mạng hoặc
  CDN, thứ sẽ làm đội mất niềm tin vào cảnh báo trong hai tuần.
- **Tài khoản chuyên dụng có gắn cờ**, loại khỏi mọi thống kê nghiệp vụ, không chạm luồng chi tiền.
- **Phân định ranh giới**: hỏng ở ứng dụng chủ, ở webview của mình, hay ở tầng dịch vụ — trả lời được
  trong vài phút thay vì vài cuộc họp *(gỡ R4)*.

> **Vì sao vẫn cần M3 khi đã có M4:** M4 đo từ bên trong thiết bị khách, nên phiên chết **trước khi
> tải được mã web** thì không công cụ phía client nào ghi nhận được — và nhóm này thiên lệch về phía
> hỏng nặng. M3 chạy từ ngoài nên bắt được đúng nhóm đó. Hai nhóm **bổ sung cho nhau, không chồng lấn**.

### M4 — Lỗi phía khách hàng · **đã hiện thực, kế thừa**

Đây là nhóm duy nhất đã có. Cấu phần **[webview monitoring](./webview-monitoring.md)** do đội web-webview xây, **dùng chung cho
mọi tenant ngân hàng**. Dự án này **không đặc tả lại** — chỉ trỏ sang và bổ sung phần còn thiếu.

**Đã có:**

- Mỗi lượt mở webview là một **phiên có định danh**, kể cả phiên thất bại — đây là **mẫu số** cho mọi
  tỉ lệ, thứ trước đây không tồn tại.
- **Dòng thời gian từng bước** của chuỗi khởi tạo, mỗi bước có mốc thời gian và trạng thái riêng.
- Loại lỗi · endpoint hỏng · mã trạng thái · vị trí trong mã nguồn — kể cả lỗi trước đây bị nuốt ở
  tầng model/service.
- Gắn **mã phiên bản build** của phiên đó.
- Phân biệt phiên **thành công** với phiên **vào được nhưng thiếu dữ liệu** — không trộn vào nhau.
- Chính sách dữ liệu ở mục 3.4 đã được áp dụng.

**Trạng thái: chưa bật trên production** ⇒ chưa sinh ra dữ liệu nào. Bật thu thập là **điều kiện tiên
quyết của giai đoạn 3**.

**Việc của dự án này với M4:**

| # | Việc |
| --- | --- |
| 1 | **Bật thu thập trên production** — không có bước này thì M4 bằng 0 trên thực tế |
| 2 | Kiểm tra dữ liệu **tách được theo tenant** không *(BB-6)* |
| 3 | Kiểm tra có **phân đoạn theo thiết bị / hệ điều hành / dòng máy** không |
| 4 | Bổ sung **BB-4** — ghi lại nguồn phát hiện là máy hay người |
| 5 | Đưa **mã phiên** thành một trường trong biểu mẫu M1 |

**Giới hạn đã biết và đã chấp nhận — "lớp vô hình":** phiên chết trước khi tải được mã web nằm ngoài
**cả tử số lẫn mẫu số**, nên độ phủ của phép đo **luôn cao hơn thực tế một cách có hệ thống**. Đây
không phải thiếu sót cần sửa trong M4 — đây là lý do M3 tồn tại.

### M5 — Tín hiệu nghiệp vụ và cảnh báo *(giải quyết lớp ③ và ④)*

- **Đo theo luồng nghiệp vụ**, mỗi luồng một chỉ số sức khoẻ: đăng nhập · xem số dư · **ghi nhận
  đơn** · **duyệt tiền hoàn** · rút tiền. M4 hiện phủ luồng đầu tiên; bốn luồng còn lại chưa có gì.
- **Lớp ③ (sai số liệu) thuộc nhóm này.** "Mua rồi không thấy tiền hoàn" chỉ phát hiện được bằng tín
  hiệu nghiệp vụ — số đơn ghi nhận, số tiền hoàn được duyệt, so với chính mình kỳ trước. Không nhóm
  nào khác bắt được lớp này.
- **So với chính mình trong quá khứ** (cùng giờ tuần trước) thay vì so với ngưỡng tuyệt đối — cách
  duy nhất phát hiện được sự cố "vẫn chạy nhưng chạy sai".
- **Không đặt ngưỡng trước khi có đường cơ sở.** Ngưỡng đặt trên nền không biết gần như chắc chắn quá
  lỏng, và ngưỡng lỏng thì không bao giờ kêu.
- Mỗi cảnh báo có **chủ sở hữu · ngưỡng · hành động kèm theo · tenant áp dụng**.
- **Ngân sách cảnh báo**: đặt trần số lượng ngay từ đầu. Thêm một cảnh báo mới thì phải bỏ hoặc chỉnh
  một cảnh báo cũ. Danh sách không có trần sẽ tự phình tới mức không ai đọc nữa.

### M6 — Vòng đời sự cố và báo cáo

- **Trạng thái**: Mới → Đã phân loại → Đang xử lý → Đã khắc phục → Đóng có kết luận.
- **Ma trận trạng thái** phải nói rõ: ai chuyển được trạng thái nào, lùi được không, SLA từng trạng
  thái, cái gì tự động cái gì thủ công.
- **Mức độ** gắn với phạm vi ảnh hưởng **và số tenant bị chạm** — xem **G2**.
- 🔴 **Một sự cố không được rời trạng thái "Đã phân loại" nếu chưa gán chủ sở hữu nằm ngoài đội giám
  sát.** Đây là ranh giới "phát hiện, không sửa" được biến thành ràng buộc của công cụ thay vì một
  thoả thuận miệng.
- **Biên bản sau sự cố** cho mức nghiêm trọng: nguyên nhân, vì sao phát hiện muộn, làm gì để lần sau
  máy phát hiện trước.
- **Báo cáo định kỳ, tách theo tenant**: số sự cố · tỉ lệ tự phát hiện · top lý do chặn · sự cố lặp lại.

## 3.6 Bốn giai đoạn

| GĐ | Đạt khi | Gồm | Gỡ |
| --- | --- | --- | --- |
| **1 · Có chỗ ghi** | Mọi lỗi khách báo nằm trong một nơi, ba tháng sau vẫn tra lại và đếm được, tách được theo tenant | M1 | ① R3 R6 |
| **2 · Trả lời được "vì sao"** | Vận hành tự trả lời ca "bị chặn" trong 30 giây, không cần kỹ sư | M2 | ② R2 |
| **3 · Biết trước khách** | Sự cố diện rộng được hệ phát hiện **trước** khi khách đầu tiên gọi | **M4 bật production** + M3 + M5 | ③ ④ R1 R4 |
| **4 · Đóng vòng** | Sự cố có kết luận, có xu hướng, lỗi lặp lại bị nhận diện | M6 | ⑤ R5 |

> **Thứ tự này không đảo được — với MSHT.** Làm M5 trước M1 sẽ cho ra một màn hình đầy biểu đồ mà vẫn
> không ai biết khách đang kêu gì, và biểu đồ sẽ đo nhầm thứ vì chưa có dữ liệu nào nói cho biết nên
> đo gì.
>
> **Nhưng đây là điều kiện áp dụng, không phải quy luật phổ quát.** Thứ tự này đúng vì khách hàng
> MSHT **có gọi tổng đài**. Ở một bối cảnh mà khách gần như không phàn nàn — họ im lặng bỏ đi — thì
> M1 sẽ là một cái thùng rỗng, và đo thụ động mới là đường vào duy nhất. Cấu phần M4 được làm trước
> chính vì lý do đó, và **với phạm vi của nó thì đó là lựa chọn đúng**.

---

# PHẦN IV — RANH GIỚI

| Với | Ranh giới |
| --- | --- |
| **Đội web-webview** | **Sở hữu cấu phần M4.** Dự án này không đặc tả lại, chỉ trỏ sang và bổ sung mục 3.5/M4 việc 1–5 |
| **CSKH của từng ngân hàng** | Người dùng chính của M1. **Mỗi tenant là một tổ chức khác nhau** — nếu đã có công cụ ticket thì tích hợp, không dựng song song. Xem **G3**, **G7** |
| **Ứng dụng của ngân hàng đối tác** | Lỗi trong ứng dụng chủ không thuộc phạm vi sửa, nhưng **phải phân định được**. M3 là công cụ phân định |
| **Đội kỹ thuật MSHT** | Sở hữu tín hiệu (M3, M5). **Không** sở hữu vòng đời sự cố |
| **Các đội sở hữu nghiệp vụ** | Nhận sự cố đã phân loại. Dự án này đảm bảo sự cố đến đúng người, không đảm bảo nó được sửa |

**Ngoài phạm vi, nói rõ để không bị kéo vào:** sửa nguyên nhân gốc của các sự cố phát hiện được ·
thay đổi quy tắc nghiệp vụ đang chặn khách · cải thiện màn hình lỗi cho khách hàng cuối · công cụ
vận hành cho từng mảng nghiệp vụ cụ thể · **đo hoặc chứng minh SLA hợp đồng với ngân hàng** — số liệu
giám sát phía client không đo uptime dịch vụ, đặt hai thứ cạnh nhau là sai về bản chất.

---

# PHẦN V — KẾT QUẢ ĐO ĐƯỢC

### Chỉ số dẫn đường

```
Tỉ lệ sự cố do hệ thống phát hiện trước khi khách hàng báo
```

Hôm nay con số này gần như bằng **0**. Đây là chỉ số duy nhất nói được dự án có đang tạo ra giá trị
hay không.

> ⚠️ **Không dùng một mình.** Nó tăng được bằng cách dựng thật nhiều cảnh báo nhạy rồi tự đếm. Phải
> đi kèm nhóm khách hàng ở dưới.
>
> ⚠️ **Mẫu số phải định nghĩa trước khi đo.** Lớp ② về bản chất không phải "sự cố" — nó là trạng thái
> bình thường của hệ thống. Chốt rõ chỉ số này tính trên lớp nào, nếu không nó không tính được.

**Mọi chỉ số dưới đây tách theo tenant, và đọc kèm độ phủ.**

| Nhóm | Thước đo | Đích |
| --- | --- | --- |
| **Phát hiện** | Tỉ lệ sự cố máy phát hiện trước khách | tăng dần → **80%** |
| | Thời gian từ lúc sự cố bắt đầu tới lúc có người biết *(lớp ①)* | **< 15 phút** — phụ thuộc tần suất M3 |
| | **Độ phủ của phép đo** | lập được đường cơ sở, rồi mới đặt đích |
| **Khách hàng** | Thời gian từ lúc khách báo tới lúc nhận được câu trả lời có nội dung | trong cam kết |
| | Số khách bị ảnh hưởng trung bình mỗi sự cố | giảm |
| **Vận hành** | % ca "bị chặn" xử lý xong không cần kỹ sư | → **95%** |
| | % báo cáo của khách được gắn vào một sự cố | **100%** |
| | Số ca M2 trả về "không xác định được lý do" | → **0** |
| **Chất lượng** | Số sự cố lặp lại cùng nguyên nhân | → **0** |
| | % sự cố nghiêm trọng có biên bản kết luận | **100%** |

> **Các đích ở trên đang đặt trên nền chưa biết.** Phải lập đường cơ sở trước — xem Phụ lục. Đặt mức
> cải thiện trước khi biết điểm xuất phát là bịa.

---

# PHẦN VI — QUYẾT ĐỊNH CẦN CHỐT

| Mã | Quyết định | Đề xuất | Người quyết | Hạn |
| --- | --- | --- | --- | --- |
| **G1** | **Ai sở hữu hệ giám sát?** | Vận hành sở hữu vòng đời sự cố, kỹ thuật sở hữu tín hiệu. **Phải có một cái tên**, không phải một phòng ban — và không nên là người đang kiêm cả dev lẫn vận hành cho M4 | Founder | Trước GĐ1 |
| **G2** | Định nghĩa mức độ sự cố, và mức nào thì báo lên — **báo lên ngân hàng nào** | Ba mức theo phạm vi ảnh hưởng **và số tenant bị chạm**; mức cao nhất báo trong 30 phút. *Hạn đặt trước GĐ1 vì việc gom báo cáo thành sự cố bắt đầu ngay từ GĐ1 — không có mức độ thì không định tuyến được* | Founder | Trước GĐ1 |
| **G3** | Dựng công cụ mới hay dùng công cụ CSKH đang có? | **Dùng cái đang có** nếu đáp ứng được BB-1, BB-2 và BB-6 | PM + CSKH | Trước GĐ1 |
| **G4** | Có hiển thị lý do bị chặn cho chính khách không? | Có, với các lý do khách tự xử lý được — cần pháp chế duyệt câu chữ, và duyệt riêng cho từng ngân hàng | Founder + pháp chế | Trước GĐ2 |
| **G5** | Có trực ngoài giờ không? | Không có người trực thì **không đặt cảnh báo đêm** — cảnh báo không ai nhận làm hỏng cả hệ | Founder + vận hành | Trước GĐ3 |
| **G6** | Ranh giới trách nhiệm với ngân hàng khi khách không vào được | **Một thoả thuận cho mỗi tenant**, không phải một thoả thuận chung. Cần đầu mối và thời hạn phản hồi hai chiều | Founder | Trước GĐ3 |
| **G7** | **Một biểu mẫu M1 chung cho mọi tenant, hay mỗi tenant một bản?** | **Một biểu mẫu chung có cột tenant** — số liệu gộp lại được khi cần, tách ra được khi cần; nhiều bản thì không bao giờ gộp lại được | PM + CSKH | Trước GĐ1 |

> **G1 là câu gốc.** Mọi dự án giám sát đều thất bại theo cùng một cách: dựng xong, không ai sở hữu,
> hai tuần sau không ai mở. Chốt được G1 thì các quyết định còn lại chỉ là chi tiết.

---

# PHẦN VII — RỦI RO CỦA CHÍNH DỰ ÁN NÀY

## 7.1 Cách dự án này thất bại

| Cách thất bại | Mức | Dấu hiệu sớm | Phòng bằng |
| --- | --- | --- | --- |
| **CSKH không đổi thói quen, vẫn nhắn chat** | Nghiêm trọng | Tuần thứ hai số dòng nhập tụt | Ràng buộc tốc độ ở M1 · đóng hẳn đường cũ · đo tỉ lệ tuân thủ 4 tuần đầu |
| **Có dữ liệu nhưng không ai nhìn** | Cao | Cảnh báo không có tên người kèm theo · một kỳ rà soát bị bỏ | Ngân sách cảnh báo ở M5 · **điều kiện dừng: bỏ hai kỳ rà soát liên tiếp là phải xử lý, không được tiếp tục như cũ** |
| **Hai nơi ghi nhận song song** | Cao | CSKH vẫn nhắn trong chat "cho nhanh" | **G3**, **G7** · đóng hẳn đường cũ |
| **Mã lý do không đầy đủ → an toàn giả** | Cao | Màn M2 trả về ô rỗng mà không nói vì sao | Trạng thái "không xác định được lý do" ở M2 · đếm nó như chỉ số chất lượng |
| **Đo hạ tầng thay vì đo nghiệp vụ** | Cao | Bảng điều khiển toàn xanh trong lúc khách kêu | Mọi chỉ số phải trả lời được câu "bao nhiêu khách làm được việc này" |
| **Dự án bị kéo vào việc sửa** | Cao | Đội giám sát bắt đầu nhận việc vá lỗi | Ràng buộc ở M6: không rời "Đã phân loại" nếu chưa có chủ ngoài đội |
| **Số liệu bị dùng để quy trách nhiệm cá nhân** | Nghiêm trọng | Báo cáo bắt đầu nêu tên người | **Cam kết trước khi bật**: số liệu dùng để ưu tiên, không dùng để đánh giá cá nhân. Nếu vi phạm, người ta sẽ học cách **không ghi nhận** — và hệ đo bị bóp méo bởi chính cách nó được dùng, không phát hiện được từ bên trong số liệu |
| **Phụ thuộc một người** | Cao | Cùng một người vừa hiện thực vừa vận hành vừa báo cáo | **G1** · đây là tình trạng đang có ở M4, không được mặc định kéo dài sang cả dự án |

*Rủi ro dữ liệu cá nhân đã được xử lý bằng ràng buộc ở mục 3.4, không còn để mở.*

## 7.2 Một đánh đổi phải nói trước

Giai đoạn 1 và 2 **làm tăng số liệu khiếu nại**, vì lần đầu tiên chúng được đếm. Con số sẽ xấu đi
trên báo cáo trong khi sản phẩm thực ra đang tốt lên.

⇒ Cần thống nhất trước với lãnh đạo: **đường cong đi lên ở tháng đầu là dấu hiệu dự án đang chạy
đúng**, không phải dấu hiệu sản phẩm xuống cấp. Không nói trước điều này thì dự án bị hiểu sai ngay
ở kỳ báo cáo đầu tiên.

## 7.3 Những điều còn phải kiểm chứng

Phải xác nhận trước khi chốt phạm vi và ước lượng:

| # | Cần biết | Trạng thái |
| --- | --- | --- |
| 1 | **Các quy tắc chặn rút tiền nằm ở đâu trong mã nguồn, và có bao nhiêu quy tắc** | ❓ Chưa biết — **làm trước tiên**, nó quyết định toàn bộ khối lượng M2 |
| 2 | Đã có công cụ theo dõi nào đang chạy chưa | ✅ Đã trả lời: cấu phần M4, dùng chung mọi tenant, **chưa bật production** |
| 3 | MSHT ghi log gì, lưu ở đâu, giữ bao lâu, ai truy cập được | ❓ Chưa biết |
| 4 | CSKH từng ngân hàng đang dùng công cụ ticket nào, có đáp ứng BB-1, BB-2, BB-6 không | ❓ Chưa biết — và là **nhiều tổ chức**, phải hỏi riêng từng bên |
| 5 | Dữ liệu M4 có tách được theo tenant và phân đoạn theo thiết bị không | ❓ Chưa biết |

---

## Phụ lục — Việc làm được ngay

| # | Việc | Ai | Trạng thái |
| --- | --- | --- | --- |
| 1 | Nơi ghi nhận báo cáo, đủ các trường của **BB-2** và **BB-6** | PM + CSKH | ✅ Đã dựng — bảng tính có tab ghi nhận, sổ sự cố, báo cáo tự động |
| 2 | Thông báo cho CSKH: mọi lỗi khách báo ghi vào đó, **không ghi trong chat** | PM | ⬜ |
| 3 | **Liệt kê các quy tắc đang chặn khách rút tiền, đọc từ mã nguồn** *(đầu vào của M2)* | Kỹ thuật | ⬜ |
| 4 | **Bật thu thập M4 trên production** *(điều kiện tiên quyết của GĐ3)* | Kỹ thuật | ⬜ |
| 5 | Rà M4: tách theo tenant chưa · phân đoạn thiết bị chưa · có BB-4 chưa | Kỹ thuật | ⬜ |
| 6 | Chốt **G1** — một cái tên sở hữu hệ giám sát | Founder | ⬜ |
| 7 | Chốt **G7** — một biểu mẫu chung hay mỗi tenant một bản | PM + CSKH | ⬜ |

> Sau bốn tuần, việc 1 và việc 4 cùng sinh ra thứ hôm nay chưa có: **đường cơ sở**. Ba con số cần
> chốt — số ca "bị chặn" mỗi tuần · số sự cố mỗi tháng · ba màn hình bị báo lỗi nhiều nhất, tách
> theo tenant. Đó là đầu vào để đặt mọi đích ở Phần V, và để ưu tiên phần còn lại của dự án.
