# PRD: Liên kết tài khoản Threads khi không còn dịch vụ crawl profile

Bối cảnh: từ 30/9 dịch vụ crawl profile Threads đã đóng. User mới không liên kết được tài khoản Threads.
Số liệu và trích dẫn đọc từ mã nguồn `AT-Core/ambassador`, ngày 2026-10-05.

---

## 1. Mục tiêu

User liên kết được tài khoản Threads mà không cần dịch vụ crawl profile.

| | Hôm nay | Sau đợt này |
|---|---|---|
| User mới bấm Đăng ký kênh Threads | Luôn lỗi "Liên kết tài khoản thất bại" | Liên kết thành công |
| Chứng minh quyền sở hữu | Máy kiểm hashtag trong Bio — **không chạy được** | Người duyệt kiểm khi duyệt kênh |
| Trạng thái sở hữu ghi xuống DB | `verified` | `hashtag_pending` — đúng sự thật |
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

### 1.3 Bỏ kiểm hashtag thì còn gì chặn người mạo danh

Còn **cửa duyệt kênh của người vận hành**. Mỗi lần liên kết đều sinh bản ghi `user_social_partner` trạng
thái `pending` cho từng ADV, và **duyệt tự động đang tắt** — code auto-approve bị comment ở
`internal/service/creator_partner_gen.go`. Không kênh Threads nào vào được chiến dịch mà chưa có người
bấm duyệt.

Nói cách khác: hôm nay hệ thống kiểm hashtag **rồi vẫn bắt duyệt tay**. Bỏ lớp kiểm máy không mở thêm cửa
nào, chỉ chuyển việc đối chiếu sang người đang duyệt — vốn đã mở profile để xem rồi.

---

## 2. Phạm vi

**Trong phạm vi**

- Luồng liên kết Threads ở `LinkUserSocial` — backend
- Màn "Đăng ký kênh Threads" trên **6 app**: `creator-app`, `fecredit`, `frontend`, `hdbank`, `lusso`, `parasola`
- Giữ luồng nộp bài Threads chạy nguyên

**Ngoài phạm vi**

- Nguồn khác: TikTok, Facebook, YouTube, Instagram, Shopee — không đụng
- Kênh Threads **đã liên kết trước 30/9** — giữ nguyên dữ liệu, không chạy lại, không hạ trạng thái
- Dựng lại dịch vụ crawl profile Threads, hoặc tìm nhà cung cấp thay thế
- Đổi luật duyệt kênh của người vận hành
- Màn duyệt kênh trên admin

---

## 3. Yêu cầu

### TH-001 — Liên kết Threads không gọi dịch vụ crawl profile

Bỏ bước gọi `ScrapeProfile` khỏi luồng liên kết. Giữ nguyên hai bước không phụ thuộc crawl: kiểm định dạng
link và giới hạn 4 kênh / user. Link sai định dạng vẫn bị từ chối ngay như cũ.

Không còn chỗ nào trong luồng liên kết đọc `THREADS_BASE_URL`. Dịch vụ đó tắt hẳn hay bật lại đều không
ảnh hưởng tới việc user liên kết.

### TH-002 — Vẫn chặn hai user khai cùng một tài khoản Threads

Chống trùng hôm nay dựa vào `data.id` lấy từ crawl, nên bỏ crawl là mất luôn. Phải đổi khoá chống trùng
sang **username chuẩn hoá lấy từ chính link user nhập** — thứ không cần gọi dịch vụ nào.

- Hai user khác nhau khai cùng một tài khoản Threads: user thứ hai bị từ chối, thông báo như hiện tại
- Chuẩn hoá trước khi so: bỏ phân biệt hoa thường, bỏ `www.`, coi `threads.net` và `threads.com` là một,
  bỏ dấu `/` cuối và phần `?...`
- Chính user đó khai lại tài khoản cũ của mình: cập nhật, không báo trùng

### TH-003 — Nộp bài Threads không được gãy

Đây là chỗ dễ vỡ nhất. Khi nộp bài Threads kèm kênh, hệ thống đối chiếu tác giả bài viết với `data.id`
của kênh (`content.go:316`). Nếu bỏ crawl mà để `data.id` rỗng thì phép so **luôn sai** — mọi bài Threads
nộp lên đều bị "Kênh không khớp". Đổi một chỗ, gãy một luồng khác.

- Kênh Threads liên kết theo cách mới phải nộp bài được, không báo "Kênh không khớp"
- Kênh Threads liên kết **trước 30/9** cũng phải nộp bài được như cũ
- Phép đối chiếu tác giả vẫn còn tác dụng: nộp link bài của người khác vẫn bị từ chối

Cách làm là việc của thiết kế kỹ thuật. Gợi ý: lấy `authorThreadId` mà `contentcatcher` trả về ở lần nộp
bài đầu tiên để điền `data.id`, hoặc đối chiếu theo username khi `data.id` còn rỗng.

### TH-004 — Trạng thái sở hữu ghi đúng sự thật

Hôm nay Threads được gắn `OwnershipStatus = "verified"` vì đã qua bước kiểm hashtag. Bỏ bước kiểm mà giữ
`verified` là ghi sai vào DB — người duyệt sẽ tin vào một nhãn không ai kiểm.

- Kênh Threads liên kết theo cách mới gắn `hashtag_pending`, giống YouTube, Instagram, Shopee
- Kênh liên kết trước 30/9 giữ nguyên `verified`, không hạ xuống

### TH-005 — Màn đăng ký kênh trên 6 app nói đúng việc user phải làm

Màn hiện tại bắt user điền hashtag vào Bio rồi mới nhập link, vì bước đó quyết định liên kết được hay
không. Sau TH-001 thì không còn gì kiểm, nhưng hashtag vẫn là thứ **người duyệt** dùng để đối chiếu.

- Bỏ cách diễn đạt khiến user hiểu rằng thiếu hashtag là không liên kết được
- Giữ phần hiển thị hashtag cá nhân và nút sao chép, đặt lại thành **khuyến nghị để được duyệt nhanh**
- Sửa đồng loạt **cả 6 app**, không app nào sót

---

## 4. Tiêu chí nghiệm thu

**Liên kết — việc chính**

- [ ] User mới nhập link Threads hợp lệ: liên kết **thành công**, kênh hiện trong danh sách kênh
- [ ] Tài khoản Threads **không có hashtag trong Bio**: vẫn liên kết thành công
- [ ] Tài khoản Threads để **ở chế độ riêng tư**: vẫn liên kết thành công
- [ ] Link sai định dạng: bị từ chối ngay, thông báo "Link không đúng định dạng"
- [ ] User đã có 4 kênh Threads: kênh thứ 5 bị từ chối, báo đã đạt giới hạn
- [ ] Tắt hẳn `THREADS_BASE_URL` trên môi trường kiểm thử: liên kết vẫn chạy bình thường

**Chống trùng**

- [ ] User A liên kết `https://www.threads.net/@abc`; user B nhập đúng tài khoản đó: **B bị từ chối**
- [ ] B nhập biến thể `https://threads.com/@ABC/`: **vẫn bị từ chối** (chuẩn hoá đúng)
- [ ] A nhập lại chính tài khoản của mình: **không** báo trùng

**Nộp bài — chống hồi quy**

- [ ] Kênh liên kết theo cách mới, nộp bài Threads của chính mình: **thành công**
- [ ] Kênh liên kết **trước 30/9**, nộp bài Threads: **thành công** như trước
- [ ] Nộp link bài Threads của người khác: **bị từ chối**, báo kênh không khớp

**Dữ liệu**

- [ ] Kênh mới: `ownershipStatus = hashtag_pending`, `linkSocial` lưu đúng link user nhập
- [ ] Kênh mới sinh đủ bản ghi duyệt `pending` cho từng ADV, hiện trên màn duyệt kênh của admin
- [ ] Kênh cũ trước 30/9: `ownershipStatus`, `data.id`, follower **không bị đổi**
- [ ] Người vận hành duyệt / từ chối kênh Threads mới trên admin: chạy đúng như kênh nguồn khác

**Giao diện**

- [ ] Cả **6 app** đều đã sửa, không app nào còn bắt buộc hashtag
- [ ] Màn đăng ký vẫn hiện hashtag cá nhân và nút sao chép
- [ ] Không màn nào còn hiện lỗi "Liên kết tài khoản thất bại" khi link hợp lệ

**Không đụng phần khác**

- [ ] TikTok, Facebook, YouTube, Instagram, Shopee: liên kết không đổi hành vi
- [ ] Facebook vẫn kiểm hashtag trong Bio như cũ

---

## 5. Rủi ro và phụ thuộc

1. **Chất lượng kênh Threads dồn hết lên người duyệt.** Trước đây máy lọc trước một lớp. Cần báo đội vận
   hành trước khi lên production, kèm hướng dẫn đối chiếu: mở link, xem hashtag trong Bio, đối chiếu tên.
2. **TH-003 là rủi ro hồi quy lớn nhất.** Sửa luồng liên kết nhưng chỗ gãy nằm ở luồng nộp bài. Phải test
   cả kênh cũ lẫn kênh mới, không chỉ kênh mới.
3. **Follower và ảnh đại diện của kênh mới sẽ trống lúc đầu.** Việc làm đầy do at-core enrich đảm nhiệm,
   chạy bằng chính `linkSocial` nên không phụ thuộc dịch vụ đã đóng. Cần xác nhận at-core có đọc được
   profile Threads không — nếu không, màn hồ sơ kênh Threads sẽ thiếu số liệu, và đó là hạng mục riêng.
4. **Kênh Threads liên kết trước 30/9 không được đụng tới.** Không chạy lại crawl, không hạ trạng thái,
   không xoá `data.id`.
5. **Code chết nên dọn:** `ScrapePost` không nơi nào gọi. Dọn hay giữ là quyết định của đội kỹ thuật,
   không chặn đợt này.
