# Hệ giám sát và quản lý sự cố MSHT — tài liệu dự án

> **Trạng thái:** đề xuất dự án, chờ chốt chủ sở hữu và các quyết định ở Phần VI.
> **Ngày:** 2026-09-14 · **Vai trò soạn:** Project Manager
> **Phạm vi:** toàn bộ trải nghiệm MSHT — truy cập, đăng nhập, tiền hoàn, điều kiện rút.
>
> ⚠️ **Giới hạn của bản này:** tài liệu mô tả **bài toán và phương án**, chưa khảo sát mã nguồn MSHT
> để xác nhận hiện có công cụ ghi log / cảnh báo nào. Xem Phần VII mục 7.3 — danh sách điều cần
> kiểm chứng trước khi chốt phạm vi và ước lượng.

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
| Hôm nay | Không đo | **Không ghi lại** |

> 🔴 **Loại thứ hai là loại nguy hiểm hơn**, vì nó không xuất hiện trong bất kỳ log lỗi nào. Hệ thống
> tự thấy mình khoẻ mạnh. Chỉ có khách là thấy mình không rút được tiền.

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
Một sự cố kéo dài ở MSHT không chỉ là sự cố của MSHT — nó là trải nghiệm xấu mang thương hiệu MB.
Ngưỡng chịu đựng của đối tác với loại sự cố *"phát hiện muộn vì không có giám sát"* thấp hơn nhiều so
với một sản phẩm độc lập.

---

# PHẦN II — VẤN ĐỀ

## 2.1 Bốn lớp sự cố, không lớp nào có đường đi

| Lớp | Khách nói gì | Hôm nay phát hiện bằng cách nào | Ai sửa |
| --- | --- | --- | --- |
| **① Truy cập** | "Vào không được", "trắng trang", "đăng nhập lỗi" | Khách gọi | Kỹ thuật |
| **② Bị chặn** | "Không rút được tiền", "báo không đủ điều kiện" | Khách gọi | Vận hành |
| **③ Sai số liệu** | "Mua rồi mà không thấy tiền hoàn", "số dư sai" | Khách gọi | Vận hành + Sản phẩm |
| **④ Tiền không về** | "Đã báo thành công mà chưa nhận được" | Khách gọi | Vận hành |

Bốn lớp, một cách phát hiện duy nhất: **khách gọi**.

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
| **R4** | Tranh chấp trách nhiệm với MB khi khách không vào được | Mỗi sự cố thành một cuộc họp đổ lỗi, không ai đo được | Trung bình |
| **R5** | Lỗi lặp lại không bị nhận diện | Sửa đi sửa lại cùng một thứ | Trung bình |

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

**Một vòng đời sự cố duy nhất.** Mọi lớp sự cố đi qua cùng một quy trình, cùng một bộ trạng thái.
Hai quy trình song song là hai nơi để một sự cố lọt qua khe.

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
| **BB-3** | Sự cố chỉ đóng được khi có **kết luận nguyên nhân**, không đóng bằng lý do "hết người báo" |
| **BB-4** | Mỗi sự cố ghi lại **ai phát hiện: máy hay người** — đây là nguồn của chỉ số dẫn đường |
| **BB-5** | Mọi quy tắc chặn khách đều phát ra **mã lý do đọc được bằng máy** |

> **BB-1 là thứ biến giai thoại thành số liệu.** Không có nó thì *"năm khách kêu"* và *"một sự cố ảnh
> hưởng ba nghìn người"* trông giống hệt nhau trên báo cáo.
>
> **BB-4 là bất biến quan trọng nhất về mặt quản trị.** Không ghi lại nguồn phát hiện thì không bao
> giờ chứng minh được hệ giám sát có đang hoạt động hay không.

## 3.4 Sáu nhóm chức năng

### M1 — Nơi ghi nhận báo cáo *(đường vào)*

- **Một kênh tiếp nhận duy nhất** cho CSKH và vận hành — không ghi trong chat.
- Mỗi báo cáo bắt buộc có: **định danh khách · thời điểm · màn hình/thao tác · phân loại · mô tả**.
- **Gom báo cáo vào sự cố**, và tách ra được khi gom nhầm.
- **Tra ngược sang hồ sơ khách hàng** ngay từ báo cáo — không phải mở công cụ khác và gõ lại định danh.

> Đây là giai đoạn rẻ nhất và bị bỏ qua nhiều nhất. Làm được bằng công cụ sẵn có trong vài ngày,
> **không cần sửa một dòng mã nào trong sản phẩm**.

### M2 — Mã lý do chặn *(giải quyết lớp ②)*

- **Mọi quy tắc đang chặn khách rút tiền đều phát ra một mã lý do** — số dư không đủ, chưa đủ thời
  hạn giữ, chưa đạt điều kiện tài khoản nhận, vượt hạn mức, và các quy tắc khác.
  *(Danh sách đầy đủ phải đọc từ mã nguồn — xem mục 7.3.)*
- **Màn "vì sao khách này không rút được"**: nhập định danh khách, ra ngay danh sách điều kiện đạt
  và không đạt.
- **Bảng xếp hạng lý do chặn theo ngày** — biến gánh nặng hỗ trợ thành tín hiệu giám sát.
- *(Giai đoạn sau)* hiển thị lý do cho chính khách — xem quyết định **G4**.

> **Đây là hạng mục có tỉ lệ giá trị trên công sức cao nhất của cả dự án.** Một mã lý do vừa rút thời
> gian trả lời khách từ *"chờ kỹ sư kiểm tra"* xuống *"ba mươi giây"*, vừa tự sinh ra một biểu đồ
> giám sát mà không cần dựng thêm gì.

### M3 — Bấm thử từ bên ngoài *(giải quyết lớp ①)*

- Một tác vụ tự động **đi lại hành trình của khách** theo lịch: mở trang · đăng nhập · xem số dư ·
  mở màn rút tiền. **Không chi tiền thật.**
- Chạy từ ngoài hệ thống, để phát hiện được cả sự cố mà máy chủ không tự thấy.
- **Phân định ranh giới**: hỏng ở ứng dụng chủ, ở webview của mình, hay ở tầng dịch vụ — trả lời được
  trong vài phút thay vì vài cuộc họp *(gỡ R4)*.
- **Trang tình trạng dịch vụ nội bộ** để vận hành tự xem, không phải hỏi kỹ sư.

### M4 — Lỗi phía khách hàng

- Thu lỗi phát sinh **trên thiết bị của khách**, kèm phiên bản ứng dụng · hệ điều hành · dòng máy.
- Phát hiện lỗi **chỉ xảy ra với một nhóm** — thứ mà mọi chỉ số phía máy chủ đều bỏ sót.
- Tuân thủ: **không thu thập dữ liệu cá nhân nhạy cảm** — sản phẩm nằm trong ứng dụng ngân hàng.

### M5 — Tín hiệu nghiệp vụ và cảnh báo

- **Đo theo luồng nghiệp vụ**, mỗi luồng một chỉ số sức khoẻ: đăng nhập · xem số dư · ghi nhận đơn ·
  duyệt tiền hoàn · rút tiền.
- **So với chính mình trong quá khứ** (cùng giờ tuần trước) thay vì so với ngưỡng tuyệt đối — cách
  duy nhất phát hiện được sự cố "vẫn chạy nhưng chạy sai".
- Mỗi cảnh báo có **chủ sở hữu · ngưỡng · hành động kèm theo**.
- **Ngân sách cảnh báo**: đặt trần số lượng ngay từ đầu. Thêm một cảnh báo mới thì phải bỏ hoặc chỉnh
  một cảnh báo cũ. Danh sách không có trần sẽ tự phình tới mức không ai đọc nữa.

### M6 — Vòng đời sự cố và báo cáo

- **Trạng thái**: Mới → Đã phân loại → Đang xử lý → Đã khắc phục → Đóng có kết luận.
- **Mức độ** gắn với phạm vi ảnh hưởng, và mức nào thì báo lên cấp trên — xem **G2**.
- **Biên bản sau sự cố** cho mức nghiêm trọng: nguyên nhân, vì sao phát hiện muộn, làm gì để lần sau
  máy phát hiện trước.
- **Báo cáo tuần**: số sự cố · tỉ lệ tự phát hiện · top lý do chặn · sự cố lặp lại.

## 3.5 Bốn giai đoạn

| GĐ | Đạt khi | Gồm | Gỡ |
| --- | --- | --- | --- |
| **1 · Có chỗ ghi** | Mọi lỗi khách báo nằm trong một nơi, ba tháng sau vẫn tra lại và đếm được | M1 | ① R3 |
| **2 · Trả lời được "vì sao"** | Vận hành tự trả lời ca "bị chặn" trong 30 giây, không cần kỹ sư | M2 | ② R2 |
| **3 · Biết trước khách** | Sự cố diện rộng được hệ phát hiện **trước** khi khách đầu tiên gọi | M3, M4, M5 | ③ ④ R1 R4 |
| **4 · Đóng vòng** | Sự cố có kết luận, có xu hướng, lỗi lặp lại bị nhận diện | M6 | ⑤ R5 |

> **Thứ tự này không đảo được.** Làm M5 trước M1 sẽ cho ra một màn hình đầy biểu đồ mà vẫn không ai
> biết khách đang kêu gì — và biểu đồ sẽ đo nhầm thứ, vì chưa có dữ liệu nào nói cho biết nên đo gì.

---

# PHẦN IV — RANH GIỚI

| Với | Ranh giới |
| --- | --- |
| **CSKH** | Người dùng chính của M1. Nếu đã có công cụ ticket thì tích hợp, không dựng song song — xem **G3** |
| **Ứng dụng MBBank** | Lỗi trong ứng dụng chủ không thuộc phạm vi sửa, nhưng **phải phân định được**. M3 là công cụ phân định |
| **Đội kỹ thuật MSHT** | Sở hữu tín hiệu (M3, M4, M5). **Không** sở hữu vòng đời sự cố |
| **Các đội sở hữu nghiệp vụ** | Nhận sự cố đã phân loại. Dự án này đảm bảo sự cố đến đúng người, không đảm bảo nó được sửa |

**Ngoài phạm vi, nói rõ để không bị kéo vào:** sửa nguyên nhân gốc của các sự cố phát hiện được ·
thay đổi quy tắc nghiệp vụ đang chặn khách · công cụ vận hành cho từng mảng nghiệp vụ cụ thể.

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

| Nhóm | Thước đo | Đích |
| --- | --- | --- |
| **Phát hiện** | Tỉ lệ sự cố máy phát hiện trước khách | tăng dần → **80%** |
| | Thời gian từ lúc sự cố bắt đầu tới lúc có người biết | **< 15 phút** cho lớp ① |
| **Khách hàng** | Thời gian từ lúc khách báo tới lúc nhận được câu trả lời có nội dung | trong cam kết |
| | Số khách bị ảnh hưởng trung bình mỗi sự cố | giảm |
| **Vận hành** | % ca "bị chặn" xử lý xong không cần kỹ sư | → **95%** |
| | % báo cáo của khách được gắn vào một sự cố | **100%** |
| **Chất lượng** | Số sự cố lặp lại cùng nguyên nhân | → **0** |
| | % sự cố nghiêm trọng có biên bản kết luận | **100%** |

---

# PHẦN VI — QUYẾT ĐỊNH CẦN CHỐT

| Mã | Quyết định | Đề xuất | Người quyết | Hạn |
| --- | --- | --- | --- | --- |
| **G1** | **Ai sở hữu hệ giám sát?** | Vận hành sở hữu vòng đời sự cố, kỹ thuật sở hữu tín hiệu. **Phải có một cái tên**, không phải một phòng ban | Founder | Trước GĐ1 |
| **G2** | Định nghĩa mức độ sự cố, và mức nào thì báo lên cấp trên | Ba mức theo phạm vi ảnh hưởng; mức cao nhất báo trong 30 phút | Founder | Trước GĐ1 |
| **G3** | Dựng công cụ mới hay dùng công cụ CSKH đang có? | **Dùng cái đang có** nếu đáp ứng được BB-1 và BB-2 | PM + CSKH | Trước GĐ1 |
| **G4** | Có hiển thị lý do bị chặn cho chính khách không? | Có, với các lý do khách tự xử lý được — cần pháp chế duyệt câu chữ | Founder + pháp chế | Trước GĐ2 |
| **G5** | Có trực ngoài giờ không? | Không có người trực thì **không đặt cảnh báo đêm** — cảnh báo không ai nhận làm hỏng cả hệ | Founder + vận hành | Trước GĐ3 |
| **G6** | Ranh giới trách nhiệm với MB khi khách không vào được | Cần thoả thuận đầu mối và thời hạn phản hồi hai chiều | Founder | Trước GĐ3 |

> **G1 là câu gốc.** Mọi dự án giám sát đều thất bại theo cùng một cách: dựng xong, không ai sở hữu,
> hai tuần sau không ai mở. Chốt được G1 thì các quyết định còn lại chỉ là chi tiết.

---

# PHẦN VII — RỦI RO CỦA CHÍNH DỰ ÁN NÀY

## 7.1 Ba cách dự án này thất bại

| Cách thất bại | Dấu hiệu sớm | Phòng bằng |
| --- | --- | --- |
| **Cảnh báo mọc như cỏ, không ai đọc** | Cảnh báo không có tên người kèm theo | Ngân sách cảnh báo ở M5 · rà soát hằng tháng, xoá cảnh báo không ai xử lý |
| **Hai nơi ghi nhận song song** | CSKH vẫn nhắn trong chat "cho nhanh" | Quyết định **G3** · đóng hẳn đường cũ, không để hai đường cùng mở |
| **Đo hạ tầng thay vì đo nghiệp vụ** | Bảng điều khiển toàn xanh trong lúc khách kêu | Mọi chỉ số phải trả lời được câu "bao nhiêu khách làm được việc này" |

## 7.2 Một đánh đổi phải nói trước

Giai đoạn 1 và 2 **làm tăng số liệu khiếu nại**, vì lần đầu tiên chúng được đếm. Con số sẽ xấu đi
trên báo cáo trong khi sản phẩm thực ra đang tốt lên.

⇒ Cần thống nhất trước với lãnh đạo: **đường cong đi lên ở tháng đầu là dấu hiệu dự án đang chạy
đúng**, không phải dấu hiệu sản phẩm xuống cấp. Không nói trước điều này thì dự án bị hiểu sai ngay
ở kỳ báo cáo đầu tiên.

## 7.3 Những điều tài liệu này chưa kiểm chứng

Bản này viết từ mô tả bài toán, **chưa khảo sát hệ thống**. Phải xác nhận bốn điều sau trước khi chốt
phạm vi và ước lượng:

1. MSHT hiện đang ghi log gì, lưu ở đâu, giữ bao lâu, ai truy cập được.
2. Đã có công cụ theo dõi nào đang chạy chưa, kể cả công cụ của phía đối tác.
3. CSKH đang dùng công cụ ticket nào, có đáp ứng **BB-1** và **BB-2** không.
4. Các quy tắc chặn rút tiền hiện nằm ở đâu trong mã nguồn, và có bao nhiêu quy tắc.

**Việc 4 nên làm trước tiên** — nó quyết định toàn bộ khối lượng của M2, hạng mục có giá trị cao nhất.

---

## Phụ lục — Việc làm được ngay trong tuần này

Không hạng mục nào dưới đây cần sửa mã sản phẩm:

| # | Việc | Ai |
| --- | --- | --- |
| 1 | Mở một nơi ghi nhận báo cáo — bảng tính cũng được — với đủ 5 trường của **BB-2** | PM + CSKH |
| 2 | Thông báo cho CSKH: từ nay mọi lỗi khách báo ghi vào đó, **không ghi trong chat** | PM |
| 3 | Liệt kê các quy tắc đang chặn khách rút tiền, đọc từ mã nguồn *(đầu vào của M2)* | Kỹ thuật |
| 4 | Rà soát: hôm nay có công cụ theo dõi nào đang chạy không | Kỹ thuật |
| 5 | Chốt **G1** — một cái tên sở hữu hệ giám sát | Founder |

> Sau hai tuần, việc 1 tự sinh ra thứ hôm nay chưa có: **danh sách các vấn đề khách gặp nhiều nhất,
> xếp theo số lượng.** Đó là đầu vào để ưu tiên toàn bộ phần còn lại của dự án — và nó không tốn một
> dòng mã nào.
