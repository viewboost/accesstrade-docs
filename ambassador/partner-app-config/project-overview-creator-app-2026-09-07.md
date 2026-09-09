# Project Overview: Portal chung cho ADV mới (`creator-app`)

## 1. Bối cảnh

Số liệu tài liệu này đo trực tiếp trên source code ambassador ngày 07/09/2026.

### 1.1 Mỗi ADV là một bản frontend riêng, vì thương hiệu gắn cứng trong bản build

Repo có **15 thư mục frontend** — mỗi ADV một bản, là một bản sao mã nguồn đầy đủ.

Không phải vì nền tảng chưa phục vụ được nhiều ADV. Phần đó đã chạy production: cả 15 app dùng chung cây
tuyến `/:partner/:slug/...`, backend phân giải đối tác theo domain qua `PartnerRaw.AllowDomains`, và
`frontend` (KOC Ambassador) đang phục vụ nhiều ADV cùng lúc kèm bộ chuyển đối tác.

Thứ không làm được là **đổi thương hiệu**. Cấu hình của một ADV nằm trong `config/config.prod.ts`, nạp bằng
`define:` — webpack thay giá trị vào mã nguồn **lúc biên dịch**, không phải lúc chạy:

```
'process.env.COMMON_PARTNER':     'fecredit',
'process.env.QA_ARTICLE_ID':      '6a8fb805f6aec40a65992405',
'process.env.NEXT_PUBLIC_ORIGIN': 'https://ambassador.fecredit.com.vn/',
```

Màu, font, logo, favicon, OG image, copy tĩnh cũng vậy — nằm trong `src/` và đi vào bản build.

Nên **một tiến trình đang chạy chỉ mang được đúng một bộ thương hiệu**. ADV thứ hai muốn có nhận diện riêng
thì phải có bản build thứ hai, và bản build thứ hai cần một thư mục nguồn thứ hai.

Đó là toàn bộ lý do tồn tại của 14 fork.

### 1.2 Đội hình hôm nay: 15 thư mục, bốn tầng sức khoẻ

Cột **riêng** = commit chỉ chạm đúng thư mục đó, tức việc làm riêng cho ADV đó, phân biệt với commit
quét nhiều app cùng lúc.

| Tầng | App | Tạo | Commit gần nhất | 6 tháng | riêng |
|---|---|---|---|---:|---:|
| **Nền tảng** | `frontend` | 03/01/2025 | 04/09/2026 | 129 | **65** |
| **Đang sống** | `lusso` | 18/03/2026 | 03/09/2026 | 49 | 25 |
| | `vpbank` | 03/01/2025 | 03/09/2026 | 46 | 21 |
| | `parasola` | 03/07/2026 | 03/09/2026 | 48 | 13 |
| | `fecredit` | 28/08/2026 | 03/09/2026 | 8 | 6 |
| | `hdbank` | 14/05/2025 | 03/09/2026 | 36 | 5 |
| **Chỉ ăn theo đợt quét** | `anker` | 02/06/2025 | 03/09/2026 | 18 | 2 |
| | `vng` | 11/04/2025 | 18/08/2026 | 24 | 2 |
| | `flamingo` | 31/07/2025 | 18/08/2026 | 21 | 1 |
| | `tpbank` | 03/07/2025 | 03/09/2026 | 27 | 1 |
| | `wildrift` | 25/09/2025 | 18/08/2026 | 19 | 1 |
| **Đứng yên** | `mbbank` · `turborg` · `vnpay` · `yody` | — | — | 14–26 | **0** |

Bốn app tầng cuối có commit trong 6 tháng nhưng không commit nào là việc riêng của chúng — toàn bộ là bị
quét qua trong các đợt sửa dùng chung. Chúng đã dừng phát triển nhưng vẫn phải gánh trong mọi lần sửa.

### 1.3 Quy trình onboard hôm nay tốn ở hai chỗ

```
1. BD tiếp xúc khách, thu thập thông tin
2. Designer dựng Figma theo ý khách        ─┐
3. BD gửi Figma, khách phản hồi             ├─ designer nằm trên đường đi của MỌI
4. Designer sửa — lặp lại vài vòng         ─┘   thương vụ, kể cả thương vụ không chốt
5. Bàn giao developer  ─────────────►  ĐIỂM RẼ
6. Developer fork một frontend mới       "chức năng này đã có sẵn,
                                          hay phải làm mới cho ADV này?"
```

**Bước 2–4 — khách chỉ nhìn được Figma, và designer bị chiếm chỗ.** BD không tự dựng được thứ gì cho khách
xem, nên mọi thương vụ đều phải xếp hàng chờ designer, kể cả thương vụ về sau không chốt. Mỗi vòng phản hồi
là một lượt qua lại giữa ba bên.

**Bước 5–6 — điểm rẽ.** Vì mỗi ADV mới là một frontend mới, câu hỏi *"đã có sẵn hay phải làm mới"* được trả
lời trong phạm vi một fork, và câu trả lời gần như luôn là "làm mới ở đây" — đó là đường ngắn nhất. Không
có chỗ nào trong quy trình bắt phải cân nhắc việc cập nhật 14 frontend còn lại.

---

## 2. Vấn đề

### 2.1 Mỗi hai tháng thêm một fork

Repo khởi tạo 03/01/2025 với 5 thư mục đầu. Sau đó là **10 fork mới trong 20 tháng**:

```
2025   vng 11/04 · hdbank 14/05 · turborg 14/05 · anker 02/06
       tpbank 03/07 · flamingo 31/07 · wildrift 25/09
2026   lusso 18/03 · parasola 03/07 · fecredit 28/08
```

Chi phí fork không phải khoản một lần. Nó lặp lại mỗi hai tháng, và nhịp chưa chậm lại.

### 2.2 ⚠️ Ba hậu quả

**A — Năng lực nền tảng bị xây bên trong fork của một ADV**

Có fork riêng nghĩa là thêm tính năng vào đó **rẻ và an toàn**: không đụng 14 app kia, không phải test hồi
quy chéo, không phải chờ ai duyệt. Nên khi ADV yêu cầu gì, "làm luôn trong fork này" là đường ngắn nhất và
gần như luôn thắng.

Vấn đề là phần lớn thứ được làm ra **không đặc thù cho ADV đó**. Đọc thẳng tiêu đề các commit riêng:

| Commit riêng của một ADV | Thực chất là |
|---|---|
| `feat(vpbank): chuyển luồng ký hợp đồng sang eKYC tập trung của ACCESSTRADE` | Năng lực nền tảng, xây bên trong fork vpbank |
| `fix(ekyc): bỏ điều kiện MST phải trùng CCCD khiến user kẹt ở bước Mã số thuế` | Lỗi nghiệp vụ chung, sửa ở một fork |
| `fix(auth): không xóa authToken khi getUserDetail lỗi tạm thời (lusso)` | Lỗi xác thực chung, sửa ở một fork |
| `feat(lusso): enable leaderboard display controlled by admin config` | Năng lực nền tảng — BXH điều khiển bằng admin |
| `feat(vpbank): thêm banner nhắc liên kết ACCESSTRADE **như parasola**` | Chép tay lại tính năng của fork khác |

eKYC tập trung và BXH điều khiển bằng admin là năng lực của nền tảng, không phải của VPBank hay Lusso.
Nhưng chúng nằm lại trong một fork; 14 app kia không có, và không ai lên kế hoạch mang sang.

Dòng cuối bảng là chữ ký của mô hình fork: lập trình viên dựng lại **bằng tay** một tính năng mà fork khác
đã có, vì không tồn tại chỗ dùng chung để lấy về.

**Mỗi lần onboard một ADV, nền tảng lại mất một mảnh năng lực vào bên trong một fork.** Cột "riêng" ở mục
1.2 vì thế đo lượng năng lực nền tảng đang nằm rải rác: lusso 25, vpbank 21, parasola 13 commit trong 6 tháng.

**B — Fork ngủ đông rồi tỉnh lại, và đã quá cũ**

Bốn app có 0 commit riêng trong 6 tháng: `mbbank`, `turborg`, `vnpay`, `yody`. Chúng không bị xoá, chỉ đứng
yên. Không có gì đánh dấu chúng đã ngừng, và không có gì cản chúng được kích hoạt lại.

Kiểm bằng nội dung code — tính năng "liên kết lại TikTok khi token hết hạn" (`grep isTokenExpired|isSyncToken`):

```
CÓ     frontend(7 file) · hdbank · lusso · vpbank · parasola · fecredit
       anker · tpbank(5) · turborg · vnpay
KHÔNG  flamingo · mbbank · vng · wildrift · yody
```

**Năm app sẽ không hoạt động đúng nếu bật lại hôm nay** — chúng thiếu hẳn luồng xử lý token TikTok hết hạn.
Không ai quyết định loại chúng ra; chúng chỉ không nằm trong danh sách của người viết commit.

`frontend` có tính năng này ở 7 file, các app khác 4. Ngay cả app "có" cũng không cùng một bản.

**C — Sửa lỗi ở một frontend, các frontend khác vẫn hỏng**

Cùng tính năng TikTok, xem cách nó lan ra đội hình — 6 commit rải 8 ngày:

| Ngày | Commit | Chạm vào |
|---|---|---|
| 27/08 | `bbe8c295` | `frontend` |
| 28/08 | `8d0b3d58` | 8 app |
| 28/08 | `0db8ff09` | `fecredit` — làm riêng, đang ở nhánh khác |
| 03/09 | `01de15fc` | 9 app + backend |
| 03/09 | `8cd1ecba` | 9 app + backend — sửa lại lần nữa |
| 03/09 | `0adc1bd1` | `fecredit` — lại làm riêng |

Một tính năng, sáu lần đưa lên, hai lần chỉ để đuổi kịp một fork, và năm app cuối cùng vẫn không có.

Ca thứ hai âm thầm hơn — **fallback ID bài viết của HDBank**. ENV để trống thì app hiển thị điều khoản và
chính sách của HDBank thay vì báo lỗi. Lỗi này đã được sửa ở `vpbank` và `fecredit`. Quét lại hôm nay:

```
Còn nguyên   lusso · parasola · tpbank
Đã sạch      vpbank · fecredit · frontend · các app còn lại
             (hdbank giữ là đúng — đó là bài của chính họ)
```

Bản sửa nằm sẵn trong repo, ở hai fork khác. Ba fork kia không có ai mang sang.

### 2.3 Chi phí một lần onboard

Đo trên lần gần nhất, `fecredit` 28/08/2026:

| Hạng mục | Khối lượng |
|---|---|
| Fork thư mục | **634 file** copy từ `parasola` |
| Checklist phần dev | **11 bước** — config, asset, font, màu, copy tĩnh, social, CI, setup.md |
| Sửa CI | **7 chỗ** trong `build-and-deploy.yml` |
| Kết quả | Một Docker image riêng, một job deploy riêng |

Bước tốn công nhất không nằm trong checklist: **gỡ dấu vết của partner cũ**. `grep "parasola"` không đủ,
dấu vết nằm ở bốn dạng:

1. **Ảnh có thương hiệu bên thứ ba** — `decor-event-right.png` là ảnh chai kem chống nắng Parasola, đang
   render thật trên trang chủ. Phải quét hue toàn bộ file ảnh rồi dựng contact sheet để tìm
2. **Màu trong SVG** — `stroke="#EE5799"` ở `ic_toggle.svg`, `ic_milestone_pass.svg`
3. **Màu viết dạng `rgba()`** — `rgba(238,87,153)`, grep hex không ra
4. **Dữ liệu liên hệ** — trang Liên hệ còn email `@pvdistribution.com.vn`, nhà phân phối của Parasola

Dọn xong, `fecredit/setup.md` vẫn còn `TODO`: link Zalo OA, nhóm Zalo và group Facebook vẫn là của Parasola.

Nền cấu hình xoá bỏ hẳn hạng mục này — không phải tiết kiệm vài giờ copy file, mà loại bỏ một loại công
việc mà bản chất là không thể làm cho đúng: dò tàn dư thương hiệu của đối tác khác trong 634 file.

### 2.4 Lỗi di truyền qua chuỗi fork

Mỗi fork mới clone từ fork gần nhất, nên thừa hưởng cả lỗi của đời trước:

```
frontend ─→ … ─→ parasola (03/07/2026) ─→ fecredit (28/08/2026)
```

- **Quy ước `ORIGIN` bị lấy nhầm.** Toàn bộ mã nguồn dùng `ORIGIN` = domain API. `parasola` và `lusso` là
  ngoại lệ sai, đặt thành domain FE. `fecredit` fork từ `parasola` nên kế thừa nguyên giá trị sai; tài liệu
  onboard nay phải ghi dòng cảnh báo *"đừng copy"*
- **Cột "Ví dụ" của biểu mẫu onboard chứa ID thật của Parasola** — người điền copy nhầm sang FE Credit

Fork thêm một đời là nhân thêm một lượt rủi ro loại này.

---

## 3. Đề xuất

Dựng `creator-app` — **một website dùng chung cho mọi ADV mới**. Mỗi ADV vẫn có domain riêng và nhận diện
riêng của họ, nhưng không còn là một bản mã nguồn riêng.

Nhận diện trở thành **thông tin nhập trên admin**: logo, màu, font, nội dung, liên hệ, bài điều khoản.
Nhập xong là website hiện ra đúng như vậy — không cần lập trình viên, không cần một đợt phát hành.

Điều đó mở ra hai việc hôm nay không làm được:

- **BD tự dựng site demo cho khách xem** ngay khi chào hàng, thay vì chờ designer dựng Figma qua vài vòng
  phản hồi (mục 1.3, bước 2–4)
- **Ops tự hoàn tất một ADV mới** mà không cần dev tạo thư mục mã nguồn và không cần một đợt phát hành
  (mục 1.3, bước 5–6)

`creator-app` chỉ phục vụ **ADV mới**. **14 website hiện có giữ nguyên, không đụng tới.**

Chi phí tạo bản mã nguồn mới phát sinh tại thời điểm onboard. Chặn ở đầu nguồn thì nợ ngừng tăng ngay, mà
không đụng vào lưu lượng production của các đối tác đang chạy.

### 3.1 Phạm vi kỹ thuật

**`creator-app/` — base trên `fecredit/`, giữ `umi`**
- Mỗi domain phân giải ra một `partner_id` lúc chạy, render giao diện biệt lập của ADV đó — thay
  `COMMON_PARTNER` gán cứng lúc build bằng phân giải theo `Host`
- Bóc lớp thương hiệu ra cấu hình đọc lúc chạy: màu, font, logo, asset, SEO, liên hệ, mạng xã hội, ID bài viết
- Cờ bật tắt tính năng theo ADV
- Một image, một triển khai, nhiều domain

**`backend/` — mở rộng, không viết lại**
- Collection `creator_app_configs` + phiên bản
- Endpoint đọc cấu hình theo domain, tận dụng `AllowDomains` và cache Redis đã có
- Endpoint admin: đọc, ghi, xuất bản, khôi phục
- Kiểm tra chéo lúc xuất bản: chặn giá trị đã đăng ký cho ADV khác

**`admin/` — thêm màn, giữ nền tảng umi 3 + antd 4**
- Màn cấu hình ADV
- Nháp → xem trước → xuất bản → khôi phục
- Chẩn đoán domain + danh sách kiểm onboard

### 3.2 Ops setup những gì

| Hạng mục | Hôm nay | Sau dự án |
|---|---|---|
| Logo, favicon, OG image | mã nguồn → **phải deploy** | **ops trên admin** |
| Màu thương hiệu, font | mã nguồn → **phải deploy** | **ops trên admin** |
| Copy tĩnh, tên hiển thị | mã nguồn, 8 file → **phải deploy** | **ops trên admin** |
| ID bài viết, liên hệ, mạng xã hội | ENV → **phải deploy** | **ops trên admin** |
| Bật tắt tính năng theo ADV | có/không có màn trong fork | **ops bật cờ** |
| Cover/banner, slug, allow domain | ops trên admin | ops trên admin |
| Campaign, bài CMS | ops trên admin | ops trên admin |
| **Thư mục app mới** | **dev, bắt buộc** | **không còn** |
| **7 chỗ sửa CI** | **dev, bắt buộc** | **không còn** |
| **Docker image riêng** | **bắt buộc** | **không còn** |

Quy tắc hiện tại là *"đổi banner không cần deploy, đổi logo/màu phải deploy"*. Sau dự án, vế thứ hai biến mất.

Bốn việc vẫn thủ công và không nằm trong phạm vi cấu hình hoá: DNS, TLS, đăng ký Authorized JavaScript
origin bên Google Console, redirect URI bên ACCESSTRADE SSO.

### 3.3 Không làm

- Không đụng 14 fork hiện có, kể cả 5 app đang sống
- Không đổi umi sang Next.js
- Không migrate ADV nào đang chạy
- Không xây cơ chế slot override
- Không đổi nền tảng `admin/`
- Không đụng backend nghiệp vụ: gate, sổ cái, tính thưởng, đối soát
- Không xử lý 7 lỗi đang chạy trên production đã ghi nhận ở khảo sát trước — task độc lập, chủ sở hữu riêng

---

## 4. ⚠️ Điều kiện bắt buộc khi base trên `fecredit`

`fecredit` là fork mới nhất (28/08/2026), lớp thương hiệu vừa được làm sạch có hệ thống, đã gỡ fallback ID
của HDBank. 647 file trong `src/`.

**Bóc lớp thương hiệu trước, không phải sau.**

`fecredit` hôm nay là app của FE Credit: xanh `#00994F`, gradient riêng, FE Font, và link Zalo/Facebook vẫn
còn là của Parasola. Fork nó rồi bổ sung tính năng dần thì kết quả là **fork thứ 15**, không phải portal
chung — ADV thứ hai sẽ phải làm lại đúng việc gỡ vết ở mục 2.3, lần này là gỡ vết FE Credit.

Việc bóc phải xong **trước khi** viết bất kỳ tính năng nào, và phải có kiểm tra tự động chặn mọi giá trị
thương hiệu quay lại nằm trong mã nguồn. Không có kiểm tra đó thì theo thời gian sẽ có người gán cứng lại
một màu, một đường link, một cái tên — và `creator-app` trượt dần về đúng chỗ 14 fork đang đứng.

---

## 5. Roadmap

```
BƯỚC 1 — đợt này
   creator-app/ base fecredit → bóc thương hiệu → đa tenant → ADV mới lên thẳng
   14 fork cũ: KHÔNG ĐỤNG
   Nghiệm thu: một ADV thật go-live mà dev không phải fork thư mục

BƯỚC 2 — gom tính năng về một chỗ
   Đối chiếu creator-app với frontend, lấy hợp của mọi tính năng
   Thu năng lực nền tảng đang nằm rải trong các fork —
     eKYC tập trung (vpbank) · BXH điều khiển bằng admin (lusso)
   Không app nào được mất tính năng khi chuyển sang

BƯỚC 3 — sau, phạm vi riêng
   Migrate các app đang sống vào creator-app/
   Ngừng hẳn các fork đã đứng yên

BƯỚC 4 — chưa cam kết
   Đổi nền tảng umi → Next.js
   Đặt lại vấn đề khi node 14 / node-sass thành rào chắn thật
```

Bước 2 chỉ khởi động khi bước 1 đã có **ít nhất một ADV thật** chạy production qua một chu kỳ chiến dịch.

Bước 2 là **tiền đề của bước 3**: chưa gom đủ tính năng thì migrate một app đang sống sẽ làm nó mất chức năng.
`frontend` là nơi tính năng đổ vào trước — 129 commit / 6 tháng, 65 là việc riêng, `src/` 661 file so với
647 của `fecredit` — nên khoảng cách này có thật và phải đo trước khi migrate.

---

## 6. Rủi ro

**R1 — Trong bước 1 có thêm một codebase, 16 thay vì 15.** Sửa lỗi dùng chung phải áp thêm một chỗ.
Mục 2.2 cho thấy các đợt quét hôm nay đã không đồng bộ: 5 app thiếu tính năng, 3 app còn lỗi đã sửa ở nơi
khác. `creator-app` không làm hỏng một cơ chế đang tốt; nó chặn nguồn sinh fork mới. Nợ cũ đứng yên thay
vì tiếp tục tăng.

**R2 — `fecredit` chưa chắc là bản đầy đủ tính năng nhất.** `creator-app` sinh ra sẽ thiếu một số tính năng
so với `frontend`. Chấp nhận được ở bước 1 vì ADV mới chưa từng có tính năng đó; xử lý ở bước 2 của roadmap,
và phải xong trước khi migrate app đang sống.

**R3 — Bóc thương hiệu làm nửa vời.** Áp lực tiến độ luôn đẩy về hướng "chạy được trước đã". Chống bằng
kiểm tra tự động ở mục 4.

**R4 — Điểm rẽ ở mục 1.3 tái sinh bên trong portal chung.** Khi ADV mới cần chức năng chưa có, câu hỏi
*"có sẵn hay làm mới"* quay lại dưới dạng "thêm cờ riêng cho ADV này" hoặc "thêm nhánh `if partner ===`".
Một codebase không tự giải quyết chuyện này. Cần quy tắc tường minh — mọi khác biệt phải nằm trong lược đồ
cấu hình, hoặc là tính năng chung cho mọi ADV, hoặc bị từ chối — kèm người có thẩm quyền quyết định và
kiểm tra tự động chặn mã nguồn rẽ nhánh theo tên ADV.

**R5 — Demo tự dựng chỉ thay được Figma khi ADV chấp nhận bố cục chuẩn.** Demo sinh từ cấu hình là bố cục
dùng chung mang thương hiệu của ADV. ADV đòi bố cục riêng thì demo không diễn đạt được, và designer quay lại
đường đi. Việc BD tự dựng demo vì thế đi kèm điều kiện: một bộ bố cục chuẩn được chốt, và ADV mua cái đang
có chứ không đặt cái chưa có. Đo lại thời gian thật sau ADV đầu tiên trước khi cam kết con số tổng.

**R6 — Bán kính ảnh hưởng.** Nhiều ADV mới trên một triển khai nghĩa là một sự cố tác động tất cả. Phạm vi
này nhẹ hơn phương án hợp nhất vì không kéo ADV đang chạy nào vào. Cần log gắn thẻ domain + ADV từ ngày
đầu, và ngưỡng số ADV tối đa trên một triển khai.

**R7 — Ops có nhận việc không.** Giá trị dự án giả định ops tự làm được khâu cấu hình ở mục 3.2. Cần xác
nhận trước khi thiết kế màn admin.

---

## 7. Chỉ số thành công

| Chỉ số | Hôm nay | Mục tiêu |
|---|---|---|
| Fork thư mục cho ADV mới | 634 file + 7 chỗ CI + 1 image | **0** |
| Deploy để đổi logo/màu/copy của ADV | bắt buộc | **0** |
| Nhịp sinh fork mới | ~1 fork / 2 tháng | **0** kể từ ADV đầu tiên lên `creator-app` |
| Thay đổi mã nguồn phục vụ riêng một ADV | thường xuyên (mục 2.2.A) | **0** — mọi khác biệt nằm trong cấu hình |
| Thời gian khâu cấu hình cho ADV mới | một đợt việc của dev + 1 deploy | ops tự làm, đo lại sau ADV đầu tiên |

Chỉ số thứ ba đo dự án có giữ được kết quả hay không. Còn fork mới ra đời nghĩa là mô hình cấu hình chưa
đủ dùng.
