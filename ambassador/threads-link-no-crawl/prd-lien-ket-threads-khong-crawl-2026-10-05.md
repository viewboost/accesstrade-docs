# PRD: Liên kết tài khoản Threads khi không còn dịch vụ crawl profile

Bối cảnh: từ 30/9 dịch vụ crawl profile Threads đã đóng. User mới không liên kết được tài khoản Threads.
Số liệu và trích dẫn đọc từ mã nguồn `AT-Core/ambassador`, ngày 2026-10-05.

**Bản v2 (06/10)** — sửa theo review của đội kỹ thuật trên PR #32. Thay đổi lớn nhất: §1.3 của bản đầu
lập luận sai, và hệ quả là thêm **TH-006** cùng ba yêu cầu bổ sung. Xem §6.

---

## 1. Mục tiêu

User liên kết được tài khoản Threads mà không cần dịch vụ crawl profile, **mà không mở đường cho người
khác chiếm kênh và nhận thưởng thay chủ kênh**.

| | Hôm nay | Sau đợt này |
|---|---|---|
| User mới bấm Đăng ký kênh Threads | Luôn lỗi "Liên kết tài khoản thất bại" | Liên kết thành công |
| Chứng minh quyền sở hữu | Máy kiểm hashtag trong Bio lúc liên kết — **không chạy được** | Hashtag cá nhân **trong từng bài nộp**, cho tới khi người vận hành duyệt kênh |
| Trạng thái sở hữu ghi xuống DB | `verified` | `hashtag_pending`, nâng lên `verified` khi được duyệt |
| Nộp bài Threads | Đang chạy nhờ `data.id` lấy từ crawl | Vẫn chạy, không phụ thuộc crawl |

### 1.1 Chỗ đang chặn

Luồng liên kết Threads ở `pkg/public/service/user.go:352-399` có 6 bước. Bốn bước giữa phụ thuộc vào
dịch vụ đã đóng:

| Bước | Dòng | Phụ thuộc crawl? |
|---|---|---|
| 1. Kiểm định dạng link | `:354` — regex nội bộ | Không |
| 2. Giới hạn 4 kênh / user | `:362` | Không |
| 3. **Gọi `ScrapeProfile`** | `:367` → lỗi là **dừng tại đây** | **Có** |
| 4. Chống trùng theo `data.id` = `profileData.PK` | `:373` | **Có** |
| 5. **Kiểm hashtag trong Bio** | `:388` | **Có** |
| 6. Lưu id, username, tên, ảnh, follower | `:391-399` | **Có** |

`ScrapeProfile` chỉ có **đúng một nơi gọi** là dòng `:367`. Bỏ bước 3 là gỡ sạch phụ thuộc vào dịch vụ đã
đóng. `ScrapePost` không nơi nào gọi — code chết.

**Dịch vụ crawl *nội dung* Threads vẫn sống.** Nộp bài Threads dùng `contentcatcher.GetDataV2` — một dịch
vụ khác hẳn (`pkg/public/service/content.go:295`). Chỉ profile chết, bài viết không sao.

### 1.2 Hình mẫu đã có sẵn trong hệ thống

YouTube, Instagram, Shopee **đã** liên kết theo kiểu không crawl: chỉ kiểm định dạng link và giới hạn 4
kênh, lưu mỗi `linkSocial`, gắn `OwnershipStatus = "hashtag_pending"` (`user.go:401-430` và `:507`). Đợt
này đưa Threads về đúng hình mẫu đó, cộng thêm phần chống trùng mà ba nguồn kia còn thiếu.

### 1.3 Bỏ kiểm hashtag thì mất gì

**Mất thật, không phải không.** Bước kiểm hashtag trong Bio là **lớp chứng minh quyền sở hữu duy nhất**
của kênh Threads, và nó đang gánh một việc nữa ở luồng nộp bài:

- Khi nộp bài có chọn kênh, hệ thống gọi `CheckHashTag` với `isSelf = true`
  (`pkg/public/service/content.go:345`, truyền `body.UserSocialId != ""`).
- Trong `CheckHashTag` (`internal/service/content.go`), điều kiện chặn là `if !isSelf && checkHashtag`.
  Tức **chọn kênh là bài đó được miễn hashtag cá nhân**.

Logic hiện tại vì vậy là: *đã chứng minh sở hữu kênh lúc liên kết → từng bài không cần hashtag nữa.* Bỏ
vế đầu mà giữ vế sau thì ai liên kết trước `@someone` sẽ nộp được bài của `@someone` mà **không cần
hashtag ở bất kỳ đâu**.

**Bản ghi duyệt kênh không bịt được lỗ này.** `user_social_partner` chỉ được tạo và hiển thị ở admin;
không chỗ nào trong backend public đọc nó để chặn nộp bài hay chặn tham gia chiến dịch. Bản đầu của PRD
viết "bỏ lớp kiểm máy không mở thêm cửa nào" — **câu đó sai**, đã bỏ.

Đó là lý do có **TH-006**: chuyển yêu cầu hashtag từ *lúc liên kết* sang *từng bài nộp*, cho tới khi
kênh được người vận hành duyệt.

---

## 2. Phạm vi

**Trong phạm vi**

- Luồng liên kết Threads ở `LinkUserSocial` — backend
- Luồng nộp bài **nguồn Threads**: điều kiện miễn hashtag cá nhân (TH-006) và điền `data.id` (TH-003)
- Nâng trạng thái sở hữu khi người vận hành duyệt kênh (TH-004)
- Màn duyệt kênh trên admin: bổ sung thông tin để duyệt được (TH-007)
- Gỡ liên kết kênh từ phía admin (TH-007)
- **7 màn** trên 6 app: `account/management` ở cả 6 app, cộng `creator-profile` của `frontend`

**Ngoài phạm vi**

- **YouTube và Shopee**: hai nguồn này cũng đang `hashtag_pending` mà vẫn được miễn hashtag khi chọn kênh
  — cùng một lỗ với Threads, có sẵn từ trước. Đợt này **không sửa**, tách hạng mục riêng. Xem §5.2
- TikTok, Facebook, Instagram — không đụng
- Kênh Threads **đã liên kết trước 30/9** — giữ nguyên dữ liệu, không chạy lại, không hạ trạng thái
- Dựng lại dịch vụ crawl profile Threads, hoặc tìm nhà cung cấp thay thế
- Luật duyệt kênh (ai được duyệt, điều kiện duyệt) — giữ nguyên

---

## 3. Yêu cầu

### TH-001 — Liên kết Threads không gọi dịch vụ crawl profile

Bỏ bước gọi `ScrapeProfile` khỏi luồng liên kết. Giữ nguyên hai bước không phụ thuộc crawl: kiểm định dạng
link và giới hạn 4 kênh / user. Link sai định dạng vẫn bị từ chối ngay như cũ.

Không còn chỗ nào trong luồng liên kết đọc `THREADS_BASE_URL`. Dịch vụ đó tắt hẳn hay bật lại đều không
ảnh hưởng tới việc user liên kết.

### TH-002 — Vẫn chặn hai user khai cùng một tài khoản Threads, và có đường gỡ

Chống trùng hôm nay dựa vào `data.id` lấy từ crawl, nên bỏ crawl là mất luôn. Phải đổi khoá chống trùng
sang **username chuẩn hoá lấy từ chính link user nhập** — thứ không cần gọi dịch vụ nào.

- Hai user khác nhau khai cùng một tài khoản Threads: user thứ hai bị từ chối, thông báo như hiện tại
- Chuẩn hoá trước khi so: bỏ phân biệt hoa thường, bỏ `www.`, coi `threads.net` và `threads.com` là một,
  bỏ dấu `/` cuối và phần `?...`
- Chính user đó khai lại tài khoản cũ của mình: cập nhật, không báo trùng

**Đường gỡ là bắt buộc.** Trước đây chỉ chủ kênh mới liên kết được vì phải đặt hashtag vào Bio. Sau
TH-001, ai khai trước thì giữ chỗ, và chủ thật sẽ bị chính TH-002 từ chối. Phải có cách gỡ (TH-007), nếu
không thì một người gõ nhầm hoặc cố ý là khoá vĩnh viễn kênh của người khác.

### TH-003 — Nộp bài Threads không được gãy

Đây là chỗ dễ vỡ nhất. Khi nộp bài Threads kèm kênh, hệ thống đối chiếu tác giả bài viết với `data.id`
của kênh (`content.go:316`). Nếu bỏ crawl mà để `data.id` rỗng thì phép so **luôn sai** — mọi bài Threads
nộp lên đều bị "Kênh không khớp". Đổi một chỗ, gãy một luồng khác.

- Kênh Threads liên kết theo cách mới phải nộp bài được, không báo "Kênh không khớp"
- Kênh Threads liên kết **trước 30/9** cũng phải nộp bài được như cũ
- Phép đối chiếu tác giả vẫn còn tác dụng: nộp link bài của người khác vẫn bị từ chối

**Điền `data.id` phải có điều kiện.** Cách làm là lấy `authorThreadId` mà `contentcatcher` trả về ở lần
nộp bài đầu tiên để điền vào `data.id`. Nhưng chỉ được điền khi **username trong link bài khớp username
của kênh** — nếu không thì bài đầu tiên của người khác sẽ gắn nhầm danh tính vào kênh, và từ đó kênh
"chính danh" là của người lạ.

**Hạn chế còn lại: link dạng `/t/CODE`.** Dạng này không chứa username (xem `RegexThreadsPost` trong
`internal/module/social/threads/threads.go`), nên với kênh chưa có `data.id` thì không đối chiếu được chủ
bài. Chấp nhận: bài dạng `/t/CODE` **không** dùng để điền `data.id`, và trong lúc kênh còn
`hashtag_pending` thì bài đó vẫn phải có hashtag cá nhân theo TH-006.

### TH-004 — Trạng thái sở hữu ghi đúng sự thật, và có đường lên `verified`

Hôm nay Threads được gắn `OwnershipStatus = "verified"` vì đã qua bước kiểm hashtag. Bỏ bước kiểm mà giữ
`verified` là ghi sai vào DB — người duyệt sẽ tin vào một nhãn không ai kiểm.

- Kênh Threads liên kết theo cách mới gắn `hashtag_pending`
- Kênh liên kết trước 30/9 giữ nguyên `verified`, không hạ xuống

**Phải có luồng nâng trạng thái.** Hôm nay chỉ `LinkUserSocial` ghi trường này; không chỗ nào chuyển
`hashtag_pending` → `verified`. Với TH-006 thì điều đó có nghĩa: kênh Threads **mãi mãi** phải kèm hashtag
trong từng bài, kể cả sau khi người vận hành đã duyệt.

- Người vận hành duyệt kênh Threads → kênh chuyển sang `verified`
- Từ chối hoặc gỡ duyệt → không nâng, giữ `hashtag_pending`
- Chỉ áp cho nguồn Threads trong đợt này; YouTube, Instagram, Shopee giữ nguyên

### TH-005 — Màn đăng ký kênh nói đúng việc user phải làm

Màn hiện tại bắt user điền hashtag vào Bio rồi mới nhập link, vì bước đó quyết định liên kết được hay
không. Sau TH-001 thì bước đó không còn chặn liên kết nữa — nhưng theo TH-006, hashtag vẫn cần, chỉ là
**chuyển sang nằm trong bài đăng** cho tới khi kênh được duyệt. Màn phải nói đúng điều đó, không được để
user hiểu là đã bỏ hẳn hashtag.

- Bỏ cách diễn đạt khiến user hiểu rằng thiếu hashtag trong Bio là không liên kết được
- Nói rõ: trong lúc kênh chưa được duyệt, **bài đăng phải chứa hashtag cá nhân** thì mới nộp được
- Giữ phần hiển thị hashtag cá nhân và nút sao chép
- Sửa đồng loạt **7 màn**: `account/management` ở cả 6 app, cộng `creator-profile` của `frontend`

### TH-006 — Kênh chưa được duyệt thì bài nộp phải có hashtag cá nhân

Đây là yêu cầu bù cho lớp bảo vệ mất đi ở TH-001, theo đúng đề xuất của đội kỹ thuật ở review PR #32.

- Với **nguồn Threads**: chỉ miễn hashtag cá nhân trong bài khi kênh có `ownershipStatus = verified`
- Kênh `hashtag_pending` (tức mọi kênh Threads liên kết theo cách mới, chưa được duyệt): bài nộp **bắt
  buộc** chứa hashtag cá nhân, thông báo lỗi dùng đúng câu đang có
- Kênh Threads liên kết **trước 30/9** đang là `verified` → **không đổi hành vi**, vẫn được miễn

**Giới hạn phạm vi là bắt buộc.** `isCheckHashTag` đang bật cho TikTok, YouTube, Facebook Post, Threads,
Shopee. Nếu áp luật mới cho mọi nguồn thì **YouTube và Shopee** — vốn cũng `hashtag_pending` — sẽ đột
ngột bắt buộc hashtag trong mọi bài, tức là làm gãy creator đang chạy. Đợt này chỉ áp cho Threads.

### TH-007 — Người vận hành có đủ công cụ để làm phần việc được giao

TH-004 và TH-006 đặt quyền quyết định vào tay người duyệt kênh. Hôm nay họ **không có đủ dữ liệu** để
quyết: màn duyệt trả về `ApprovalCreatorResponse`, trong đó `UserShortInfo` không có mã user và
`UserSocialData` không có `ownershipStatus`. Người duyệt không nhìn thấy hashtag cá nhân của user nên
không đối chiếu được với Bio.

- Màn duyệt kênh hiện **hashtag cá nhân của user** và **trạng thái sở hữu** của kênh
- Có đường mở nhanh link kênh để đối chiếu
- Admin **gỡ được liên kết kênh** của một user (nối TH-002). Hôm nay chỉ chính chủ gỡ được, qua
  `DELETE /remove-user-social` ở API public; admin không có đường nào
- Gỡ liên kết ghi nhật ký: ai gỡ, kênh nào, lúc nào

---

## 4. Tiêu chí nghiệm thu

**Liên kết — việc chính**

- [ ] User mới nhập link Threads hợp lệ: liên kết **thành công**, kênh hiện trong danh sách kênh
- [ ] Tài khoản Threads **không có hashtag trong Bio**: vẫn liên kết thành công
- [ ] Tài khoản Threads để **ở chế độ riêng tư**: vẫn liên kết thành công
- [ ] Link sai định dạng: bị từ chối ngay, thông báo "Link không đúng định dạng"
- [ ] User đã có 4 kênh Threads: kênh thứ 5 bị từ chối, báo đã đạt giới hạn
- [ ] Tắt hẳn `THREADS_BASE_URL` trên môi trường kiểm thử: liên kết vẫn chạy bình thường

**Chống mạo danh — ca quan trọng nhất của bản v2**

- [ ] User A liên kết kênh Threads **của người khác**, rồi nộp bài của chính kênh đó, bài **không** chứa
      hashtag cá nhân của A: **bị từ chối**, báo thiếu hashtag cá nhân
- [ ] Vẫn user A đó, nộp bài có chứa hashtag cá nhân của A: được nhận — và đây là hành vi **cố ý chấp
      nhận**, vì chủ kênh thật không đời nào đăng hashtag của người lạ
- [ ] Sau khi người vận hành duyệt kênh: bài không cần hashtag cá nhân nữa
- [ ] Kênh Threads liên kết **trước 30/9**: nộp bài không hashtag vẫn được nhận như cũ

**Chống trùng và đường gỡ**

- [ ] User A liên kết `https://www.threads.net/@abc`; user B nhập đúng tài khoản đó: **B bị từ chối**
- [ ] B nhập biến thể `https://threads.com/@ABC/`: **vẫn bị từ chối** (chuẩn hoá đúng)
- [ ] A nhập lại chính tài khoản của mình: **không** báo trùng
- [ ] Admin gỡ liên kết kênh của A, B liên kết lại chính kênh đó: **thành công**
- [ ] Lần gỡ đó có dòng nhật ký ghi người thao tác

**Nộp bài — chống hồi quy**

- [ ] Kênh liên kết theo cách mới, nộp bài Threads của chính mình (có hashtag): **thành công**
- [ ] Kênh liên kết **trước 30/9**, nộp bài Threads: **thành công** như trước
- [ ] Nộp link bài Threads của người khác: **bị từ chối**, báo kênh không khớp
- [ ] `data.id` chỉ được điền khi username trong link bài khớp username kênh — thử nộp bài của kênh khác
      làm bài đầu tiên: `data.id` **không** bị ghi
- [ ] Link dạng `/t/CODE` làm bài đầu tiên: `data.id` **không** bị ghi, bài vẫn xử lý theo TH-006
- [ ] **YouTube và Shopee**: nộp bài có chọn kênh, **không** hashtag cá nhân → vẫn được nhận **như trước
      đợt này**. Đây là ca chặn hồi quy quan trọng nhất của TH-006

**Dữ liệu và trạng thái**

- [ ] Kênh mới: `ownershipStatus = hashtag_pending`, `linkSocial` lưu đúng link user nhập
- [ ] Kênh mới sinh đủ bản ghi duyệt `pending` cho từng ADV, hiện trên màn duyệt kênh của admin
- [ ] Người vận hành duyệt → `ownershipStatus` chuyển `verified`
- [ ] Từ chối → giữ `hashtag_pending`
- [ ] Kênh cũ trước 30/9: `ownershipStatus`, `data.id`, follower **không bị đổi**

**Màn duyệt trên admin**

- [ ] Màn duyệt hiện **hashtag cá nhân của user** và **trạng thái sở hữu** của kênh
- [ ] Mở được link kênh từ màn duyệt để đối chiếu
- [ ] Người vận hành duyệt / từ chối kênh Threads mới: chạy đúng như kênh nguồn khác

**Giao diện người dùng**

- [ ] Cả **7 màn** đều đã sửa, không màn nào còn bắt buộc hashtag trong Bio để liên kết
- [ ] 7 màn đều nói rõ: kênh chưa duyệt thì bài đăng phải có hashtag cá nhân
- [ ] Màn đăng ký vẫn hiện hashtag cá nhân và nút sao chép
- [ ] Không màn nào còn hiện lỗi "Liên kết tài khoản thất bại" khi link hợp lệ

**Không đụng phần khác**

- [ ] TikTok, Facebook, YouTube, Instagram, Shopee: **liên kết** không đổi hành vi
- [ ] TikTok, Facebook Post, YouTube, Shopee: **nộp bài** không đổi hành vi
- [ ] Facebook vẫn kiểm hashtag trong Bio lúc liên kết như cũ

---

## 5. Rủi ro và phụ thuộc

### 5.1 Rủi ro được chấp nhận

**Người lạ vẫn liên kết được kênh của người khác.** TH-006 không chặn việc *liên kết*, chỉ chặn việc *ăn
thưởng*: muốn nộp bài thì phải có hashtag cá nhân nằm trong bài, mà chủ kênh thật sẽ không đăng hashtag
của người lạ. Hai hệ quả còn lại:

- Kênh bị **giữ chỗ**: chủ thật không liên kết được cho tới khi admin gỡ (TH-007 là đường gỡ)
- Nếu người vận hành **duyệt nhầm** một kênh mạo danh thì lớp TH-006 mất tác dụng cho kênh đó

Mốc chặn cuối vì vậy nằm ở **thao tác duyệt kênh**. Cần thống nhất với đội vận hành ai chịu trách nhiệm
và đối chiếu bằng gì, trước khi lên production.

### 5.2 Lỗ cùng kiểu đang có sẵn ở YouTube và Shopee

Hai nguồn này cũng `hashtag_pending` mà vẫn được miễn hashtag khi nộp bài có chọn kênh — tức là lỗ hổng
y hệt, tồn tại từ trước đợt này. Cố tình **không** sửa trong đợt này để không làm gãy creator đang chạy
(xem TH-006). Cần tách thành hạng mục riêng và có người nhận.

### 5.3 Rủi ro triển khai

1. **TH-003 là rủi ro hồi quy lớn nhất.** Sửa luồng liên kết nhưng chỗ gãy nằm ở luồng nộp bài. Phải test
   cả kênh cũ lẫn kênh mới, không chỉ kênh mới.
2. **TH-006 dễ gây hồi quy chéo.** Nếu áp nhầm cho mọi nguồn thì YouTube và Shopee gãy ngay. Ca nghiệm thu
   cho hai nguồn đó là bắt buộc, không phải tuỳ chọn.
3. **Kênh Threads liên kết trước 30/9 không được đụng tới.** Không chạy lại crawl, không hạ trạng thái,
   không xoá `data.id`.

### 5.4 Phụ thuộc cần xác nhận trước khi nghiệm thu

1. **at-core có đọc được profile Threads không.** Follower và ảnh kênh mới sẽ trống lúc đầu; việc làm đầy
   do at-core enrich đảm nhiệm, chạy bằng chính `linkSocial`. Nếu at-core không hỗ trợ Threads thì số liệu
   kênh Threads trống vĩnh viễn — cần người xác nhận, và đó là hạng mục riêng.
2. **Đội vận hành nhận thêm việc đối chiếu khi duyệt kênh.** Cần báo trước, kèm hướng dẫn: mở link, xem
   hashtag trong Bio, đối chiếu tên.
3. **Code chết nên dọn:** `ScrapePost` không nơi nào gọi. Dọn hay giữ là quyết định của đội kỹ thuật,
   không chặn đợt này.

---

## 6. Thay đổi so với bản đầu (05/10)

Sửa theo review của đội kỹ thuật trên PR #32.

| Điểm review | Xử lý |
|---|---|
| §1.3 lập luận sai: bản ghi duyệt không chặn nộp bài; `isSelf = true` miễn hashtag trong bài | **Nhận.** Viết lại §1.3, bỏ câu "không mở thêm cửa nào" |
| Đề xuất: chỉ miễn hashtag khi kênh `verified` | **Nhận**, thành **TH-006** — nhưng **giới hạn cho nguồn Threads**, vì áp cho mọi nguồn sẽ làm gãy YouTube và Shopee đang chạy (điểm này review chưa nêu) |
| §4 thiếu ca nghiệm thu cho lỗ hổng | **Nhận.** Thêm nhóm "Chống mạo danh" |
| TH-002 không có đường gỡ khi bị chiếm tên kênh | **Nhận.** Thêm vế gỡ vào TH-002, dựng thành **TH-007** |
| TH-004: `hashtag_pending` không có luồng lên `verified` | **Nhận.** Thêm luồng nâng khi duyệt vào TH-004 |
| Màn duyệt không hiện hashtag / `ownershipStatus` | **Nhận**, đã kiểm: `ApprovalCreatorResponse` và `UserShortInfo` đều không có. Thành **TH-007** |
| 7 màn chứ không 6 app | **Nhận.** Đã kiểm: chỉ `frontend` có thêm `creator-profile` |
| `/t/CODE` không đối chiếu được chủ bài; chỉ điền `data.id` khi username khớp | **Nhận.** Thêm vào TH-003 |
| at-core Threads chưa xác nhận | **Nhận**, giữ ở §5.4 |
| "`CheckHashTag` trả về ngay ở develop (`config.IsEnvDevelop()`)" | **Không đưa vào.** Đã kiểm: `IsEnvDevelop()` chỉ dùng ở ba chỗ `cmd/*/main.go` để bật Swagger, không liên quan tới `CheckHashTag`. QC **kiểm được** hành vi này trên develop |
| "Kênh `hashtag_pending` ẩn số liệu ở creator-profile" | **Không đưa vào theo nguyên nhân đó.** Đã kiểm `social-account-card`: số liệu ẩn khi `social.stats` rỗng, tức khi at-core chưa enrich — `ownershipStatus` chỉ đổi nhãn một dòng CTA. Phần số liệu trống đã nằm ở §5.4 |
