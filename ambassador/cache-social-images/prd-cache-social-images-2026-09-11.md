# Product Requirements Document: Cache ảnh mạng xã hội về MinIO trên Ambassador

**Ngày:** 11/09/2026
**Trạng thái:** Đề xuất — phần F1 đã code và đã merge vào `develop`
**Đối tượng đọc:** PM, Backend Dev, QA, Tech Lead
**Repo đích:** `AT-Core/ambassador`
**Repo tham chiếu:** `viewboost/techcombank` (T-Fluencers)
**Nhánh code:** `fix/cache-social-images-to-minio` — PR #209 đã merge `develop`, PR #208 vào `release` còn mở

---

## Document Overview

Tài liệu này mô tả yêu cầu cho việc **tự lưu trữ mọi ảnh lấy từ mạng xã hội về MinIO của hệ thống**, gồm hai mặt: ảnh đại diện của bài đăng (`cover`) và ảnh đại diện người dùng (`avatar`).

Đây là một case **port từ T-Fluencers** — [t-fluencers/fix-cover-expired/overview.md](../../t-fluencers/fix-cover-expired/overview.md) và [tech-spec.md](../../t-fluencers/fix-cover-expired/tech-spec.md). Bản gốc chỉ giải quyết `cover` cho đúng một API. Ambassador cần rộng hơn vì kiến trúc khác, và có sẵn một nửa phần `avatar` từ trước.

### Nguyên tắc

1. **Hiện trạng phải verify từng dòng trước khi viết yêu cầu** — mục 2.1 ghi rõ file và số dòng, không suy đoán.
2. **Không port nguyên xi** — chỗ nào kiến trúc Ambassador khác thì nói rõ khác ở đâu và vì sao (mục 8).
3. **Lỗi của bản gốc thì sửa, không bê sang** (mục 2.3).
4. **YAGNI** — mục 2.4 liệt kê những thứ cố tình không làm.

---

## 0. Thuật ngữ

| Thuật ngữ | Nghĩa |
|---|---|
| **cover** | Ảnh đại diện của một bài đăng (`ContentRaw.cover`). Nguồn gốc là URL trên CDN của nền tảng. |
| **thumbnail** | Ảnh thu nhỏ do crawler lấy về (`ContentRaw.thumbnail`) — **cũng là URL CDN thô**, không phải file của ta. |
| **images** | Mảng URL ảnh của bài đăng dạng ảnh (`ContentRaw.images`). Với nguồn Threads và Facebook Post, ảnh đầu đã được upload về MinIO ngay lúc tạo bài; các nguồn khác vẫn là URL CDN thô. |
| **avatar** | Ảnh đại diện người dùng đã cache về MinIO (`UserRaw.avatar`, kiểu `FilePhoto`). |
| **URL ký hạn** | URL CDN có kèm chữ ký và thời điểm hết hạn (`x-expires`, `oe=`). Hết hạn là ảnh vỡ. |
| **host về MinIO** | Tải ảnh từ CDN bên thứ ba về rồi upload lên bucket public của ta, sau đó ghi đè URL trong DB. |
| **FILE_HOST** | Biến môi trường trỏ tới host phục vụ bucket public của ta. |
| **TF** | T-Fluencers (repo `techcombank`) — hệ thống nguồn của pattern này. |

---

## 1. Executive Summary

Mọi ảnh Ambassador đang hiển thị cho người dùng — ảnh bài đăng lẫn ảnh người tham gia — đều trỏ thẳng vào CDN của TikTok, Facebook, Instagram, Google. Các URL đó **có hạn sử dụng**: TikTok ~2 ngày, Meta ~3–4 ngày. Hết hạn là ô xám, icon vỡ. Campaign đã đóng thì không còn crawl lại, nên URL chết nằm trong DB vĩnh viễn — càng để lâu tỉ lệ ảnh vỡ càng tiến tới 100%.

Kèm theo đó là vấn đề thứ hai, ít thấy hơn nhưng nặng hơn: các API công khai đang **phát nguyên đường dẫn CDN của Google/TikTok ra ngoài**, kể cả file export cho đối tác. Đây chính là lý do Gen-Green phải tắt hẳn route `user-newest` ở PR 792 — Ambassador không tắt được vì partner-app đang gọi thật.

Giải pháp: tải ảnh về MinIO ngay khi hệ thống chạm tới ảnh đó, ghi đè URL trong DB bằng URL của ta. Chạy nền, không chặn API. Làm một lần, dùng vĩnh viễn.

**Trạng thái hiện tại:** phần `cover` (F1) đã code xong, đã merge `develop`. Phần `avatar` (F2) mới có một nửa — thiếu Facebook, thiếu luồng liên kết tài khoản, chưa có backfill, và đang chạy đồng bộ trong luồng đăng nhập. Phần bịt lộ URL (F3) mới bịt được 2 trong ~14 điểm.

---

## 2. Bối cảnh

### 2.1 Hiện trạng Ambassador — đã verify từng dòng

**Ảnh cover — đã có (nhánh `fix/cache-social-images-to-minio`):**

| Hạng mục | Vị trí | Ghi chú |
|---|---|---|
| Helper | `backend/internal/module/social/content_catcher/cover_host.go` | Bản sao **từng byte** của TF, gồm cả unit test |
| Hàm dùng chung | `backend/pkg/public/service/content_cover_host.go` | `hostCoversAsync(contents, source)` |
| Điểm gắn 1 | `partner.go:201` — `GetContentFeature` | `GET /partners/content-features` |
| Điểm gắn 2 | `event.go:543` — `GetListContentByEvent` | `GET /events/{id}/content` |
| Điểm gắn 3 | `event.go:634` — `GetListContentByMe` | `GET /events/{id}/content/me` |
| Điểm gắn 4 | `mission.go:541` — `GetListContentByMe` | `GET /missions/{id}/content/me` |

Bốn điểm này là **toàn bộ** các hàm trả `ContentAllResponse` của Ambassador — không đường nào bị sót.

**Ảnh avatar — có sẵn từ trước, chưa đủ:**

| Hạng mục | Vị trí | Trạng thái |
|---|---|---|
| Service host avatar | `backend/internal/service/upload_avatar_social.go` | Có. Resize sm 150×150 / md 300×300, upload bucket public, ghi `UserRaw.avatar` |
| Chặn host lại | cùng file, đầu hàm | Có — `user.Avatar != nil` thì trả về ngay |
| Gọi khi đăng nhập TikTok | `user.go:1634` | Có |
| Gọi khi đăng nhập Google | `user.go:1758` | Có |
| Gọi khi đăng nhập Facebook | `LoginWithFacebook`, `user.go:613` | **KHÔNG có** |
| Gọi khi liên kết tài khoản social | `user.go:430-504` | **KHÔNG có** |
| Cách chạy | `user.go:1634`, `:1758` | **Đồng bộ** trong luồng đăng nhập |
| Timeout HTTP khi tải ảnh | `internal/util/request.go:161` `HttpClient()` | **Không set `Timeout`** — CDN treo thì đăng nhập treo |
| Script backfill user cũ | — | **Không tồn tại** (repo chỉ có backfill event-reward và withdraw-draft) |

**Điểm còn phát URL CDN bên thứ ba** (chỉ rơi vào nhánh này khi user chưa có avatar cache — mà chưa backfill thì phần lớn user cũ đúng là chưa có):

- Public: `user_statistic.go:203-207`, `user.go:153/157`, `user.go:2068/2072`, `mission.go:662`, `mission.go:728`, `mission.go:561`, `event.go:566`, `event.go:652`, `partner.go:224`
- Admin: `user.go:382/386`, `user_segment.go:278/282` (**đường đi vào file export**), `partner.go:113`, `staff_statistic.go:203-206`

Hai điểm đã được bịt ở commit `8282e42c7`: `event.go:86-93` (`GetListUserNewest`) và `event.go:1146` (`buildUserShortInfo`, dùng bởi cả hai đường bảng xếp hạng).

**Một chi tiết quan trọng về nấc dự phòng:** khi `cover` rỗng, Ambassador rơi về `Thumbnail.Medium.URL`, rồi rơi tiếp về `Images[0]` (`partner.go:248-251`, `event.go:589-594`, `event.go:681-684`, `mission.go:591`). Hai nấc này không giống nhau về mức độ an toàn:

- **`Thumbnail` là URL CDN thô, và hở ở cả hai repo.** `ContentRaw.Thumbnail` là `contentcatcher.Thumbnail` — struct chỉ chứa URL từ crawler, không phải `FilePhoto` trên MinIO. Không có chỗ nào trong repo host thumbnail lên MinIO, kể cả bên T-Fluencers. Content có `cover` rỗng vẫn vỡ ảnh sau vài ngày, chỉ là vỡ ở đường khác.
- **`Images[0]` phần lớn đã an toàn sẵn.** `content.go:383` đã upload ảnh đầu về MinIO ngay lúc tạo bài, cho nguồn Threads và Facebook Post. Chỉ còn hở ba trường hợp: nguồn ảnh khác hai nguồn đó; upload lúc tạo bài thất bại nên rơi về `b.Images = contentInfo.Images`; và content cũ tạo trước khi có cơ chế này. Đây là chỗ Ambassador **làm tốt hơn** bản gốc — T-Fluencers lưu thẳng URL thô ở `content.go:378`.

### 2.2 Nguyên nhân gốc

URL ảnh của các nền tảng không vĩnh viễn:

| Nền tảng | Dấu hiệu | Hạn |
|---|---|---|
| TikTok | `tiktokcdn.com/...?x-expires=&x-signature=` | ~2 ngày |
| Facebook | `fbcdn.net/...?oe=&oh=` | ~3–4 ngày |
| Instagram / Threads | `cdninstagram.com/...?oe=` | ~3–4 ngày |
| Google | `lh3.googleusercontent.com/...` | không cố định, có thể đổi/thu hồi |
| YouTube | `i.ytimg.com/vi/{videoId}/...` | **ổn định, không hết hạn** |

Hệ thống không có job re-crawl. Campaign đóng → không crawl mới → URL chết nằm lại.

### 2.3 Khác biệt bắt buộc do kiến trúc

| | T-Fluencers | Ambassador | Vì sao |
|---|---|---|---|
| Số điểm gắn | 4 (partner ×2, event ×2) | 4 (partner ×1, event ×2, mission ×1) | Ambassador không có `GetListContentLeaderboard`; đổi lại có luồng mission và luồng "bài đăng của tôi" |
| Tổ chức mã | mỗi impl một bản copy | **một hàm dùng chung** | Ambassador cần tới 3 impl (event/partner/mission), copy 3 lần là nợ |
| Invalidate cache Redis | Có — cache `content-features` TTL 4h | **Bỏ** | Ambassador **không cache** `content-features`. `redis/key.go` không có key nào cho luồng này; chỗ duy nhất cache ở `partner.go:45` là *danh sách partner theo domain*. Không có cache thì không có gì để xoá |
| Nội dung log | `partner=<id>` | `source=<tên call site>` | Có 4 luồng gọi nên cần biết luồng nào, còn partner suy ra được từ log tầng trên |
| Ảnh trên bảng xếp hạng | BXH là bảng xếp hạng **nội dung**, có cover | BXH là bảng xếp hạng **người**, chỉ có avatar | Mọi kiểm thử cover phải làm ở màn danh sách bài đăng, không phải màn BXH |

### 2.4 Lỗi của T-Fluencers — sửa, không port

1. **Overview TF hứa "retry 1 lần" nhưng code TF không hề retry.** Không port lời hứa đó. Cơ chế thật là: lỗi thì bỏ qua, lượt gọi sau thử lại — và phải ghi vào tài liệu đúng như vậy (FR-09).
2. **TF coi `Thumbnail.Medium.URL` là "nấc dự phòng an toàn".** Không đúng — thumbnail cũng là URL ký hạn, và không repo nào host nó lên MinIO. Đây là giả định sai của bản gốc chứ không phải điểm mạnh; PRD TF không lộ ra lỗi này chỉ vì phạm vi của nó tự cắt hẹp ở 8 video trang chủ, nơi `cover` luôn có nên nấc dự phòng không bao giờ chạy tới. Ambassador chạy ở 4 luồng, chạm ngay vào vùng đó, nên phải xử lý ở FR-07 thay vì bê nguyên giả định.
3. **TF lưu thẳng URL CDN thô cho bài đăng dạng ảnh** (`content.go:378`). Ambassador đã đi trước một bước ở `content.go:383` — upload ảnh về MinIO ngay lúc tạo bài. Giữ nguyên hướng của Ambassador, không port cách của TF.
4. **TF giải bài toán lộ URL bằng cách tắt hẳn route công khai** (commit `d07bf984`, cùng hướng với Gen-Green PR 792). Ambassador không tắt được vì partner-app gọi thật, nên phải thôi lộ URL — cùng mục tiêu bảo mật, không vỡ giao diện (FR-16).

### 2.5 Những gì KHÔNG thêm vào

- **Không** job quét định kỳ toàn bộ DB để refresh ảnh — lazy migrate khi hệ thống chạm tới là đủ.
- **Không** job dọn file MinIO. Upload một lần, giữ vĩnh viễn.
- **Không** resize / nén / chuyển WebP cho cover ở giai đoạn này.
- **Không** worker pool, không rate limit — tải hiện tại quá nhỏ.
- **Không** đổi logic chọn top, sort, filter, phân trang (mục 3.2).
- **Không** đổi shape response, không đổi giao diện.

---

## 3. Mục tiêu và phạm vi

### 3.1 Mục tiêu

| Mã | Mục tiêu |
|---|---|
| **G1** | Ảnh bài đăng không còn vỡ theo thời gian — đã hiển thị được thì hiển thị mãi |
| **G2** | Ảnh đại diện người dùng không còn vỡ và không còn mất trắng với user đăng nhập bằng TikTok |
| **G3** | Không còn URL CDN của bên thứ ba lọt ra ngoài qua API công khai, API admin, hay file export |

### 3.2 Phạm vi KHÔNG thay đổi

Tài liệu này không đụng tới:

- Logic chọn top / sắp xếp / lọc / phân trang của mọi danh sách content và mọi bảng xếp hạng
- Shape của response — không thêm, không bớt, không đổi tên field
- Giao diện frontend — không cần sửa gì ở bất kỳ app FE nào
- Tần suất và cơ chế crawl nội dung
- TTL cache Redis của bảng xếp hạng (10 phút) và của danh sách partner (4 giờ)
- Luồng duyệt / ẩn / từ chối nội dung

### 3.3 Chỉ số đo

| Mã | Chỉ số | Ngưỡng |
|---|---|---|
| **M1** | Tỉ lệ content trong các danh sách đang hiển thị có `cover` là URL MinIO | ≥ 95% sau 1 tuần chạy |
| **M2** | Ảnh còn hiển thị được sau 72 giờ kể từ lúc host | 100% |
| **M3** | Tỉ lệ user active có avatar MinIO sau khi backfill | ≥ 95% |
| **M4** | Số lần khớp chuỗi `tiktokcdn.com` / `googleusercontent.com` / `fbcdn.net` khi quét response API công khai, API admin và file export | 0 |
| **M5** | Mức tăng thời gian phản hồi của các API bị gắn thêm việc host ảnh | ≤ 10% so với trước |

---

## 4. Đối tượng chịu ảnh hưởng

| Vai | Ảnh hưởng |
|---|---|
| **Người dùng cuối** | Thấy đủ ảnh bài đăng và ảnh người tham gia, không còn ô xám. Không phải thao tác gì khác. |
| **Người dùng đăng nhập bằng TikTok** | Hết bị mất trắng ảnh đại diện trên bảng xếp hạng. |
| **Partner / đối tác nhận file export** | File export không còn chứa đường dẫn CDN của bên thứ ba. |
| **Vận hành** | Hết khiếu nại "trang lỗi ảnh". Có log đối soát mỗi lượt host. |
| **Backend dev** | Thêm một hàm dùng chung ở tầng service; không phải sửa FE. |

---

## 5. Phạm vi kỹ thuật áp dụng

### 5.1 Nền tảng và quy tắc bỏ qua

Quy tắc: **mọi URL http(s) không trỏ về MinIO của ta đều phải host**, trừ các trường hợp dưới đây.

| Nguồn | Xử lý | Lý do |
|---|---|---|
| TikTok, Facebook, Instagram, Threads, và mọi CDN lạ khác | **Host** | URL ký hạn, chắc chắn chết |
| YouTube — `ytimg.com`, `img.youtube.com` | **Bỏ qua** | URL ổn định theo `videoId`, không hết hạn. Host chỉ tốn dung lượng |
| URL đã trỏ tới `FILE_HOST` | **Bỏ qua** | Đã host rồi |
| URL rỗng | **Bỏ qua** | Không có gì để tải |
| URL sai định dạng, hoặc scheme khác `http`/`https` | **Bỏ qua** | Chặn `file://`, `ftp://`, `javascript:` |

### 5.2 Đối tượng bị thay đổi

| | |
|---|---|
| **Content bị đụng tới** | Chỉ những content thực sự nằm trong danh sách mà API vừa trả về. Content ngoài danh sách không bị đụng. |
| **Field bị đụng tới** | Chỉ `cover`. Các field `thumbnail`, `images`, `statistic`, `status` và mọi field khác giữ nguyên tuyệt đối. |
| **User bị đụng tới** | Chỉ user vừa đăng nhập / vừa liên kết social, hoặc user nằm trong lô backfill. |
| **Field user bị đụng tới** | Chỉ `avatar` và `updatedAt`. |

---

## 6. Functional Requirements — F1: ảnh bài đăng

> Trạng thái: FR-01 đến FR-06, FR-08, FR-09 **đã code và đã merge `develop`**. FR-07 **chưa làm**.

### FR-01: Bỏ qua ảnh không cần host
Hệ thống phải bỏ qua, không tải về, các cover thuộc diện nêu ở mục 5.1. Mỗi lần bỏ qua phải được đếm vào nhóm `skipped` trong log, không được ghi nhận là lỗi.

### FR-02: Tải ảnh về kho của hệ thống
Với cover cần host, hệ thống tải ảnh từ CDN nguồn rồi upload lên bucket public của MinIO, đặt tên theo mã content để một content luôn ứng với đúng một file. URL trả ra phải mở được công khai, không cần đăng nhập, và **không được chứa khoá truy cập hay chữ ký** trong đường dẫn.

### FR-03: Ghi đè đường dẫn trong cơ sở dữ liệu
Sau khi upload thành công, hệ thống ghi đè `cover` của đúng content đó bằng URL MinIO. Không đụng tới bất kỳ field nào khác, không đụng tới content khác (mục 5.2).

### FR-04: Không làm chậm API
Toàn bộ việc tải và upload chạy nền, tách khỏi luồng trả lời API. Thời gian phản hồi của API không được tăng quá ngưỡng M5. Lượt gọi đầu tiên vẫn trả URL cũ — đây là hành vi đúng, không tính là lỗi.

### FR-05: Lượt truy cập kế tiếp đã thấy ảnh mới
Kể từ lượt gọi ngay sau khi việc host hoàn tất, API phải trả URL MinIO. Người dùng **không phải chờ hết TTL cache nào**.

### FR-06: Gọi lại nhiều lần vô hại
Chạy lại trên cùng tập content không được sinh thêm file, không được tăng dung lượng bucket, không được tải lại ảnh từ CDN nguồn. Cùng một content luôn ghi vào cùng một object.

### FR-07: Nấc dự phòng cũng phải bền — **chưa làm**
Khi `cover` rỗng, hệ thống rơi về `thumbnail` rồi `images[0]` (mục 2.1). Yêu cầu: ảnh dùng ở nấc dự phòng cũng phải là ảnh của ta.

Mức độ hở của hai nấc khác nhau, nên xử lý khác nhau:

- **`thumbnail` — hở toàn phần.** Chưa bao giờ được host, ở cả Ambassador lẫn T-Fluencers. Đây là phần chính của yêu cầu này.
- **`images[0]` — hở phần dư.** Đã có cơ chế upload lúc tạo bài cho Threads và Facebook Post. Chỉ cần bù ba trường hợp còn lại: nguồn ảnh khác, upload lúc tạo bài thất bại, và content cũ.

Hai cách đáp ứng, chọn một ở mục 12 (Q1/Q2):
- (a) Host `thumbnail`, và bù nốt phần dư của `images[0]`, theo đúng cơ chế của FR-02, hoặc
- (b) Bỏ hẳn hai nấc dự phòng này và dùng ảnh mặc định của hệ thống.

Chừng nào chưa chọn, content có `cover` rỗng vẫn vỡ ảnh sau vài ngày — phải ghi nhận là lỗi đã biết, không phải lỗi mới.

### FR-08: Giới hạn tài nguyên mỗi lượt tải
Mỗi ảnh có trần dung lượng và trần thời gian tải. Quá trần thì bỏ ảnh đó, không được để một ảnh xấu làm cạn tài nguyên tiến trình. Định dạng file lưu phải khớp loại ảnh thật do CDN trả về.

### FR-09: Một ảnh lỗi không ảnh hưởng phần còn lại
Ảnh tải lỗi, upload lỗi, hay ghi DB lỗi đều chỉ ảnh hưởng đúng content đó: giữ nguyên URL cũ, ghi một dòng log kèm mã content và nội dung lỗi, rồi đi tiếp. Response API không được vỡ. Không retry trong cùng một lượt — lượt gọi sau sẽ thử lại một cách tự nhiên.

---

## 7. Functional Requirements — F2: ảnh đại diện, F3: bịt lộ URL

### FR-10: Host ảnh đại diện khi có nguồn social — **thiếu Facebook và luồng liên kết**
Hệ thống phải host ảnh đại diện về MinIO ở **mọi** thời điểm biết được ảnh social của user:
- Đăng nhập bằng Google — *đã có*
- Đăng nhập bằng TikTok — *đã có*
- Đăng nhập bằng Facebook — **chưa có, phải bổ sung**
- Liên kết tài khoản social vào user đang tồn tại — **chưa có, phải bổ sung**

### FR-11: Không host lại ảnh đại diện đã có
User đã có `avatar` thì mọi lần đăng nhập sau không được tải lại, không được sinh file mới. *Đã đáp ứng.*

### FR-12: Đủ hai kích thước
Mỗi avatar phải có đủ bản nhỏ và bản vừa, cả hai mở được công khai, bản vừa lớn hơn bản nhỏ. *Đã đáp ứng — 150×150 và 300×300.*

### FR-13: Lỗi host ảnh không được chặn đăng nhập
Ảnh social hỏng, bị xoá, hay CDN trả lỗi đều không được làm hỏng việc đăng nhập. Người dùng vẫn vào được, hệ thống ghi cảnh báo và tạm dùng URL social. *Đã đáp ứng ở phần bắt lỗi.*

### FR-14: Host ảnh đại diện phải chạy nền và có trần thời gian — **chưa làm**
Hiện việc tải + resize + upload chạy **đồng bộ ngay trong luồng đăng nhập**, và HTTP client dùng để tải **không đặt timeout** (`internal/util/request.go:161`). CDN phản hồi chậm hoặc treo thì đăng nhập treo theo — FR-13 chỉ chống được lỗi trả về nhanh, không chống được treo.

Yêu cầu: chuyển sang chạy nền như F1, và đặt trần thời gian cho mỗi lượt tải.

### FR-15: Backfill người dùng cũ — **chưa làm**
Cần script chạy một lần, quét user đang thiếu `avatar` nhưng có tài khoản social, host ảnh về MinIO theo lô, có log tiến độ. Script phải **chạy lại được nhiều lần mà không nhân bản dữ liệu**: lần chạy thứ hai không sinh thêm file, không tăng dung lượng bucket. Đạt ngưỡng M3.

### FR-16: Không phát URL bên thứ ba ra ngoài — **mới bịt 2/15 điểm**
Không API công khai, API admin, hay file export nào được trả về đường dẫn CDN của Google, TikTok, Facebook, Instagram.

- Đã bịt: `GetListUserNewest` và đường dựng thông tin bảng xếp hạng.
- Còn hở: 9 điểm ở tầng public và 4 điểm ở tầng admin, liệt kê đầy đủ ở mục 2.1 — **trong đó có đường đi vào file export gửi đối tác**.
- Nguyên tắc bịt: đã có avatar MinIO thì phát URL MinIO; chưa có thì mới rơi về ảnh social. Kết hợp với FR-15, sau backfill sẽ không còn trường hợp rơi về.

Ở các đường này còn một lỗi cùng loại với lỗi đã sửa ở bảng xếp hạng: **nhiều đường chỉ có nhánh Google, thiếu hẳn nhánh TikTok** (`event.go:566`, `event.go:652`, `partner.go:224`, `mission.go:561`) — user TikTok chưa cache avatar sẽ mất trắng ảnh. Sửa cùng lúc.

### FR-17: Không làm chậm đăng nhập
Thời gian đăng nhập không được chênh lệch đáng kể so với trước, kể cả khi ảnh social hỏng hoặc CDN chậm. Phụ thuộc FR-14.

---

## 8. Những điểm Ambassador khác T-Fluencers

### 8.1 Không có cache Redis ở luồng content — đã bỏ phần invalidate
TF phải xoá cache sau khi host vì `content-features` của họ cache 4 giờ. Ambassador **không cache** luồng này: `redis/key.go` không có key tương ứng, chỗ cache duy nhất trong `partner.go` là danh sách partner theo domain. Vì vậy bản port **cố ý bỏ** phần invalidate — đây là quyết định, không phải thiếu sót. Hệ quả cho kiểm thử: không cần xoá cache trước khi test, và nếu lượt gọi thứ hai vẫn ra URL social thì nguyên nhân nằm ở chỗ khác chứ không phải cache.

### 8.2 Một lượt host, bốn luồng cùng hưởng
Vì URL mới được ghi thẳng vào DB nên chỉ cần một luồng bất kỳ chạm tới content là cả bốn luồng đều thấy URL mới. Không cần kích hoạt riêng từng luồng.

### 8.3 Content dạng ảnh và nấc dự phòng
Với bài đăng dạng ảnh, ảnh hiển thị có thể lấy từ `images[]` chứ không phải `cover`. Hai hệ xử lý nhánh này khác hẳn nhau, và ở đây **Ambassador làm tốt hơn bản gốc**:

| | T-Fluencers | Ambassador |
|---|---|---|
| Lúc tạo bài, nguồn dạng ảnh | `content.go:378` — lưu thẳng URL CDN thô | `content.go:383` — upload ảnh về MinIO trước, rồi mới lưu (nguồn Threads, Facebook Post) |

Vì vậy phần lớn content dạng ảnh của Ambassador đã an toàn sẵn từ lúc tạo. Phần còn hở chỉ là dư: nguồn ảnh ngoài hai nguồn trên, ca upload lúc tạo bài thất bại, và content cũ — xem FR-07 và Q2.

Ngược lại, nấc `thumbnail` thì **cả hai hệ cùng hở** và bản gốc chưa nhận ra: tech spec TF mô tả nó như đường dự phòng an toàn, trong khi thực tế nó cũng là URL ký hạn. Xem mục 2.4.

### 8.4 Ảnh đại diện có hai kích thước
Khác cover (một file một content), avatar sinh hai file sm/md. Mọi kiểm thử và mọi đường phát URL phải dùng bản md.

### 8.5 Backfill là bắt buộc, không phải tuỳ chọn
TF xếp backfill vào "phase sau, tuỳ chọn" vì họ chỉ cần 8 ảnh trên trang chủ. Ambassador thì khác: chừng nào user cũ còn `avatar` rỗng thì FR-16 còn hở, vì các đường fallback vẫn phải rơi về ảnh social. Backfill là điều kiện để đạt M4.

### 8.6 File export của admin
Điểm mà rà soát gốc bỏ sót: dữ liệu user xuất ra file cho đối tác bên ngoài đi qua `user_segment.go:278`, cũng rơi về URL Google/TikTok. File export rời khỏi hệ thống và không thu hồi được, nên đây là điểm ưu tiên cao nhất trong FR-16.

---

## 9. Yêu cầu phi chức năng

**Bảo mật**
- URL công khai của MinIO không được chứa khoá truy cập hay chữ ký.
- Ảnh phục vụ công khai, mở được không cần đăng nhập — đúng như bản chất ảnh bài đăng và ảnh đại diện.
- Khi tải ảnh từ CDN, dùng User-Agent trình duyệt thông thường. **Không giả mạo bot của Meta/TikTok** để tránh vùng xám điều khoản.
- Chỉ chấp nhận `http`/`https`.

**Quan sát được**
- Mỗi lượt host ghi một dòng tổng kết gồm: số thành công, số bỏ qua, số thất bại, thời lượng, và nguồn gọi.
- Mỗi thất bại ghi một dòng riêng gồm mã đối tượng và nội dung lỗi.
- Không được có panic thoát ra ngoài làm chết tiến trình.

**Hiệu năng**
- Đáp ứng M5 cho API, và FR-17 cho đăng nhập.
- Ước tính dung lượng: mỗi ảnh 50–200KB. Với phạm vi bốn luồng của Ambassador, hãy tính lại theo số content thực tế đang hiển thị thay vì dùng con số "<1GB" của TF — phạm vi hai bên khác nhau.

**Rollback**
- Tắt tính năng = gỡ lời gọi, không cần xoá file MinIO, không cần hoàn nguyên dữ liệu.
- Ảnh đã host vẫn hiển thị bình thường sau khi tắt, vì URL nằm trong DB và file vẫn còn.

---

## 10. Kế hoạch triển khai

1. **Đã xong** — F1 cover: code, unit test, merge `develop` (PR #209).
2. **Đang chờ** — F1 lên `release` (PR #208).
3. **Kế tiếp** — F2: bổ sung Facebook + luồng liên kết (FR-10), chuyển sang chạy nền và đặt timeout (FR-14).
4. **Sau đó** — F3: bịt các điểm còn hở, ưu tiên file export admin trước (FR-16, mục 8.6).
5. **Cuối** — viết script backfill, chạy thử trên lô nhỏ, chạy hai lần để chứng minh không nhân bản, rồi chạy toàn bộ (FR-15).
6. **Nghiệm thu** — quét chuỗi theo M4 trên cả response API lẫn file export; đối chiếu ảnh sau 72 giờ theo M2.

Việc quyết FR-07 (Q1/Q2) có thể làm song song, không chặn các bước trên.

---

## 11. Rủi ro

| Rủi ro | Mức | Xử lý |
|---|---|---|
| URL nguồn đã hết hạn ngay lúc định host → không tải được | Trung bình | Chấp nhận. Ghi log, content đó giữ nguyên. Với content cũ, đây là trạng thái không cứu được — ảnh đã mất từ trước |
| Ảnh đúng là của bài đăng đã bị xoá khỏi nền tảng | Thấp | Chấp nhận: thà hiển thị ảnh cuối cùng còn hơn ô vỡ. Admin vẫn ẩn được nội dung |
| Backfill chạy vào giờ cao điểm gây tải | Trung bình | Chạy theo lô, ngoài giờ cao điểm, có log tiến độ để dừng giữa chừng được |
| Dung lượng bucket tăng ngoài dự tính do phạm vi rộng hơn TF | Thấp | Đo thật sau một tuần, cảnh báo khi vượt 80% |
| Sửa các điểm ở mục 2.1 làm hỏng màn đang chạy | Trung bình | Mỗi điểm sửa phải kèm kiểm thử hồi quy ở mục 14 |

---

## 12. Câu hỏi còn treo

- **Q1 — Có host `thumbnail` không?** Nếu không, content có `cover` rỗng vẫn vỡ ảnh. Ảnh hưởng FR-07.
- **Q2 — Có bù nốt phần dư của `images[]` không?** Threads và Facebook Post đã an toàn sẵn nhờ cơ chế upload lúc tạo bài; câu hỏi chỉ còn cho nguồn ảnh khác, ca upload lúc tạo bài thất bại, và content cũ. Nếu chọn "không làm", phải ghi nhận là lỗi đã biết và QA không tính fail.
- **Q3 — Backfill chạy lô bao nhiêu và trong khung giờ nào?** Cần Ops chốt để ước lượng thời gian chạy.
- **Q4 — Có cần cảnh báo khi tỉ lệ host thất bại vượt ngưỡng không**, hay chỉ đọc log thủ công trong giai đoạn đầu?

---

## 13. Tài liệu liên quan

- Bản gốc T-Fluencers: [overview.md](../../t-fluencers/fix-cover-expired/overview.md), [tech-spec.md](../../t-fluencers/fix-cover-expired/tech-spec.md), [test-cases.csv](../../t-fluencers/fix-cover-expired/test-cases.csv)
- Nhánh code: `fix/cache-social-images-to-minio` (`AT-Core/ambassador`) — PR #209 vào `develop`, PR #208 vào `release`
- Tech spec cho tài liệu này: sẽ viết sau khi PRD được duyệt

---

## 14. Kiểm thử hồi quy và rollback

**Hồi quy bắt buộc** — phải chứng minh những thứ ở mục 3.2 không đổi:

1. Trước và sau khi triển khai, gọi cùng một API với cùng tham số: số lượng, danh sách mã, và **thứ tự** phải trùng khớp tuyệt đối.
2. Content nằm ngoài danh sách được trả về không bị đụng tới.
3. Với content đã host, các field ngoài `cover` giữ nguyên từng giá trị.
4. Các màn đang hiển thị ảnh — danh sách bài đăng, bài đăng của tôi, bảng xếp hạng, trang cá nhân, admin — đều còn ảnh, không màn nào trắng.
5. Thời gian đăng nhập và thời gian phản hồi API nằm trong ngưỡng M5 / FR-17.

**Rollback** — gỡ lời gọi và triển khai lại. Kết quả phải đạt:

- API trả về bình thường.
- Content và user đã chuyển đổi **vẫn** trả URL MinIO, ảnh vẫn hiển thị đầy đủ.
- Không phải xoá file MinIO, không phải hoàn nguyên dữ liệu.
