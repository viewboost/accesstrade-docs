# Báo cáo rà soát bảo mật — Nền tảng Green Creator (vcreator-api)

- **Ngày rà soát:** 26/08/2026
- **Phạm vi:** API công khai `vcreator-api.koc.com.vn` phục vụ website `creator.gen-green.global`
- **Mức độ tổng thể:** 🔴 **NGHIÊM TRỌNG (Critical)** — cần xử lý ngay
- **Trạng thái:** Đã kiểm chứng trực tiếp trên hệ thống production ngày 26/08/2026
- **Đối tượng đọc:** Ban lãnh đạo, đội sản phẩm, đội kỹ thuật, đối tác

---

## 0. Tóm tắt cho lãnh đạo (đọc 1 phút)

Hệ thống đang **để lộ dữ liệu tài chính và thông tin cá nhân của toàn bộ creator ra Internet mà không cần đăng nhập**. Bất kỳ ai — kể cả đối thủ, nhà báo, hay người dùng tò mò — chỉ cần mở đúng địa chỉ trên trình duyệt là đọc được:

- **Thu nhập chi tiết của từng creator** (số tiền đã nhận, đang chờ, đã chuyển khoản).
- **Thông tin cá nhân**: tên thật, ảnh đại diện mạng xã hội (công khai — ảnh creator đang dùng trên Google/TikTok, không phải ảnh riêng tư do hệ thống lưu), đường dẫn kênh gốc.
- **Ngân sách hoa hồng của từng nhãn hàng** (VinFast, VinWonders, Green SM, Vinhomes, Gen Green, VEC…) — tức số liệu hợp đồng giữa nền tảng và khách hàng.
- **Lý do bài viết bị từ chối kiểm duyệt** của từng creator.

Đáng chú ý: người khai thác **có thể tra cứu dữ liệu của một creator bất kỳ** chỉ bằng cách đổi mã định danh trên đường link — không giới hạn ở dữ liệu của chính mình.

Đây không phải lỗi mới phát sinh do một thay đổi gần đây. **Vấn đề tồn tại từ ngày bàn giao mã nguồn (16/10/2024)** và chưa từng được vá trong suốt ~22 tháng.

**Tin tốt cho kinh doanh:** các con số mà trang chủ (landing) đang hiển thị — *lượt xem, số nội dung, số người tham gia* — đều là **số liệu tổng hợp, không định danh cá nhân**, nên **vẫn giữ nguyên được**. Việc vá lỗi **không làm hỏng landing**. Chỉ cần tách phần dữ liệu nhạy cảm (tiền của từng người, ngân sách từng nhãn hàng) ra khỏi kênh công khai.

---

## 1. Hiện trạng

### 1.1. Những gì đang bị lộ công khai (đã kiểm chứng ngày 26/08/2026)

Toàn bộ dữ liệu dưới đây lấy được **không cần tài khoản, không cần mật khẩu, không cần bất kỳ khóa bí mật nào** — chỉ cần truy cập địa chỉ API.

**a) Thống kê toàn nền tảng**

| Chỉ số | Giá trị đang lộ |
|---|---|
| Tổng hoa hồng đã ghi nhận | **30,4 tỷ VND** |
| Tổng số nội dung | **280.874** |
| Tổng lượt xem | **16,5 tỷ** |
| Số creator có nội dung | **26.772** |

**b) Ngân sách hoa hồng theo từng nhãn hàng** — đây là số liệu hợp đồng khách hàng

| Nhãn hàng | Hoa hồng lộ ra | Số nội dung | Số creator |
|---|---|---|---|
| VinFast | ~6,0 tỷ VND | 48.437 | 7.677 |
| *(và các nhãn khác: VinWonders, Green SM, Vinhomes, Gen Green, VEC)* | tra được tương tự | | |

> Chỉ cần đổi mã nhãn hàng trên đường link là ra số liệu của nhãn tiếp theo. Nghĩa là **đối thủ có thể đọc ngân sách marketing của nhau**.

**c) Thu nhập và danh tính của từng creator**
- Bảng xếp hạng trả về **số tiền chi tiết** của từng người: tổng, đang chờ, đã hoàn tất, **đã chuyển khoản**. (Ví dụ thực tế: một creator có tổng ~221 triệu, đã chuyển khoản ~15,9 triệu.)
- Kèm **tên thật + ảnh đại diện mạng xã hội** (ảnh công khai creator dùng trên Google/TikTok, đường dẫn trỏ thẳng URL gốc) + đường dẫn video/kênh gốc.

**d) Dữ liệu cá nhân của creator bất kỳ (nghiêm trọng nhất)**
- Có một nhóm địa chỉ API cho phép **truyền vào mã của một creator bất kỳ** và nhận về: thu nhập, toàn bộ nội dung của người đó, danh sách người mà họ đã giới thiệu (mạng lưới referral), và **lý do bài bị BTC từ chối kiểm duyệt**.
- Ví dụ đã kiểm chứng: với một creator, hệ thống trả về 49 nội dung (25 bị từ chối, 10 đang chờ, 14 duyệt) kèm nguyên văn lý do từ chối — dữ liệu này lẽ ra **chỉ chính chủ mới được xem**.

### 1.2. Vì sao việc này dễ bị khai thác

- **Không giới hạn tần suất truy cập (không rate-limit):** có thể tự động tải sạch dữ liệu của cả 26.772 creator.
- **Cấu hình CORS mở toàn bộ (`*`):** bất kỳ website nào trên Internet cũng có thể đọc dữ liệu này ngay trong trình duyệt của người dùng.
- **Danh mục API công khai (swagger):** liệt kê sẵn toàn bộ địa chỉ, giúp người dò tìm rất nhanh.

---

## 2. Đối chiếu chuẩn OWASP

Tài liệu tham chiếu: **OWASP API Security Top 10 (2023)** — bộ tiêu chuẩn quốc tế phổ biến nhất để đánh giá rủi ro của API. Dưới đây là các rủi ro nền tảng đang vi phạm, diễn giải bằng ngôn ngữ dễ hiểu.

| Mã OWASP | Tên (diễn giải dễ hiểu) | Mức độ | Tình trạng của nền tảng |
|---|---|---|---|
| **API1:2023 — BOLA** | *Không kiểm soát quyền trên từng đối tượng*: đổi mã trên link là xem được dữ liệu người khác | 🔴 **Critical** | Đọc được thu nhập/nội dung/mạng lưới của **creator bất kỳ** bằng cách đổi mã định danh |
| **API2:2023 — Broken Authentication** | *Xác thực bị hỏng*: nơi lẽ ra bắt đăng nhập thì không bắt | 🔴 Critical | Cơ chế kiểm tra đăng nhập chạy ở chế độ "mềm" — không có tài khoản vẫn đi qua được |
| **API3:2023 — Excessive Data Exposure** | *Trả thừa dữ liệu*: API gửi ra nhiều hơn mức màn hình cần | 🟠 High | Trả cả số tiền và lý do kiểm duyệt dù giao diện công khai không dùng đến |
| **API4:2023 — Unrestricted Resource Consumption** | *Không giới hạn khai thác*: cho phép tải dữ liệu không giới hạn | 🟡 Medium | Không rate-limit → hút sạch toàn bộ cơ sở dữ liệu creator |
| **API5:2023 — Broken Function Level Authorization** | *Mở nhầm chức năng cho người không có quyền* | 🟡 Medium | Danh sách chiến dịch affiliate (kèm tỷ lệ hoa hồng) bị gỡ yêu cầu đăng nhập |
| **API6:2023 — Unrestricted Access to Sensitive Business Flows** | *Lộ luồng nghiệp vụ nhạy cảm* | 🟡 Medium | Ngân sách hoa hồng theo từng nhãn hàng tra được công khai |
| **API8:2023 — Security Misconfiguration** | *Cấu hình sai*: để cấu hình kiểu môi trường thử nghiệm chạy trên production | 🟠 High | CORS mở `*` trên production → mọi website đọc được dữ liệu tài chính |

**Kết luận xếp hạng:** rủi ro nặng nhất là **API1 (BOLA)** — đứng số 1 trong bảng OWASP — vì nó cho phép truy cập dữ liệu tài chính và cá nhân của **bất kỳ người dùng nào**, không cần đăng nhập, khai thác được từ xa. Theo thang điểm đánh giá tổn thương phổ biến (CVSS), mức này tương đương **~9.1/10 (Critical)**.

---

## 3. Nguyên nhân

Cần phân biệt rõ để tránh quy trách nhiệm sai:

**3.1. Nguyên nhân gốc — thiết kế từ khi bàn giao (không phải lỗi vận hành gần đây)**

Toàn bộ nhóm địa chỉ API bị lộ đã tồn tại **y nguyên từ commit bàn giao mã nguồn ngày 16/10/2024**. Đây là cách hệ thống được thiết kế ngay từ đầu, không phải do một thay đổi nào của đội hiện tại làm hỏng.

Ba lỗi thiết kế cộng hưởng:

1. **Xác thực kiểu "mềm":** hệ thống có kiểm tra đăng nhập, nhưng nếu không có tài khoản thì **vẫn cho đi tiếp** thay vì chặn lại. Chỉ một số ít màn hình được gắn "bắt buộc đăng nhập", phần còn lại vô tình để mở.

2. **Trả thẳng dữ liệu thô từ cơ sở dữ liệu ra ngoài:** thay vì chỉ gửi đúng những trường màn hình cần (tên, ảnh, lượt xem), API gói cả khối dữ liệu — bao gồm các trường tiền bạc và lý do kiểm duyệt — rồi gửi ra. Giao diện không hiển thị chúng, nhưng dữ liệu **vẫn nằm trong gói tin** và ai mở gói tin cũng đọc được.

3. **Tin vào tham số do phía gọi truyền lên:** nhóm "thống kê của tôi" lấy mã người dùng **từ đường link** thay vì lấy từ phiên đăng nhập. Vì vậy đổi mã trên link là xem được của người khác (đây chính là lỗi BOLA).

**3.2. Bằng chứng cho thấy việc lộ tiền là ngoài ý muốn**

Trên giao diện, phần hiển thị số tiền ở bảng xếp hạng công khai **đã bị chủ động ẩn đi** (comment lại trong mã nguồn frontend). Tức là **đã có người quyết định "không cho công chúng thấy tiền của creator"** — nhưng mới chỉ sửa ở phần giao diện, còn **API vẫn tiếp tục gửi số tiền ra**. Điều này khẳng định việc lộ dữ liệu là **sơ suất kỹ thuật, không phải tính năng có chủ đích**.

---

## 4. Giải pháp

Nguyên tắc chỉ đạo: **giữ nguyên trải nghiệm công khai hợp lệ (bảng xếp hạng, số liệu tổng của landing), chỉ tách phần nhạy cảm ra.** Không đóng sập API, vì bảng xếp hạng công khai là tính năng có chủ đích.

### 4.1. Landing vẫn chạy bình thường — phân định rõ giữ / bỏ

| Dữ liệu | Landing có cần? | Nhạy cảm? | Hướng xử lý |
|---|---|---|---|
| Tổng lượt xem, tổng nội dung, tổng người tham gia | ✅ Có | Không (số tổng, ẩn danh) | **Giữ công khai** — đây là số "hero" của landing |
| Tổng hoa hồng toàn nền tảng (30,4 tỷ) | ✅ (bản vcreator) | Vừa | Giữ được — nhưng là **quyết định truyền thông**: có muốn công bố hay không (xem mục cần chốt) |
| Hoa hồng **theo từng nhãn hàng** (`totalCommission`) | ❌ Không | 🔴 Cao (số liệu khách hàng) | **Bỏ trường `totalCommission`** khỏi response — GIỮ param `?partner=` (partner-home dùng để hiện view/nội dung/người tham gia) |
| Bảng xếp hạng: tên, ảnh, lượt xem, điểm/thứ hạng | ✅ Có | Thấp | Giữ, nhưng **chỉ gửi đúng các trường này** |
| Số tiền của từng creator | ❌ Không | 🔴 Cao | **Bỏ khỏi dữ liệu công khai** |
| "Thống kê của tôi" (thu nhập, nội dung, referral) | ❌ (màn hình nội bộ) | 🔴 Cao | **Bắt buộc đăng nhập** + chỉ cho xem dữ liệu của chính mình |

**Thông điệp cốt lõi:** landing chỉ dùng 3–4 con số tổng hợp, và tất cả đều nằm ở nhóm an toàn. **Không phải đánh đổi giữa marketing và bảo mật.**

### 4.2. Lộ trình xử lý theo mức ưu tiên

**🔴 P0 — Khẩn cấp (xử lý ngay trong ngày):**
1. **Khóa BOLA:** nhóm "thống kê của tôi" phải bắt buộc đăng nhập và **chỉ trả dữ liệu của chính người đang đăng nhập** (lấy danh tính từ phiên, bỏ qua mã truyền trên link).
2. **Cắt trường nhạy cảm:** với bảng xếp hạng và danh sách nội dung công khai, chỉ gửi ra tên/ảnh/lượt xem/điểm; **loại bỏ toàn bộ trường tiền và lý do kiểm duyệt.**
3. **Bỏ trường `totalCommission`** khỏi response `/events/statistic` công khai. **KHÔNG chặn param `?partner=`** — `partner-home` (trang `/:partner/`) dùng nó để hiện view/nội dung/người tham gia theo nhãn; chỉ riêng field commission mới là chỗ lộ ngân sách.
   - **frontend-green: không đọc `totalCommission`** → bỏ field an toàn, không vỡ gì.
   - `frontend-vcreator` đã ngừng sử dụng → không cần cân nhắc. Bỏ field `totalCommission` là an toàn tuyệt đối với FE hiện hành.

**🟠 P1 — Trong tuần:**
4. Cấu hình CORS đúng (chỉ cho phép các tên miền của nền tảng), thay vì mở `*` trên production.
5. Thêm giới hạn tần suất truy cập (rate-limit) cho nhóm API công khai.
6. Che/proxy ảnh đại diện thay vì trả thẳng đường dẫn Google/TikTok.
7. **Thêm "hàng rào tự động" chống tái diễn:** một bài kiểm thử liệt kê danh sách trắng các địa chỉ được phép công khai — bất kỳ địa chỉ mới nào lọt ra ngoài danh sách sẽ khiến hệ thống kiểm thử báo đỏ, chặn ngay từ khâu duyệt mã. Đây là biện pháp bền vững nhất để lỗi này không quay lại.

**🟡 P2 — Chính sách & hậu kiểm:**
8. Rà lại quyết định mở danh sách chiến dịch affiliate (23/05/2026).
9. Ban hành quy định thành văn: bảng xếp hạng công khai được phép hiển thị những gì.
10. **Hậu kiểm nhật ký truy cập (access log)** của các địa chỉ bị lộ để xác định dữ liệu đã thực sự bị thu thập ở quy mô nào — kết quả này quyết định việc **có cần thông báo cho creator và cho nhãn hàng hay không** (đây là vấn đề pháp lý/PR, không chỉ kỹ thuật).

---

## 5. Phụ lục — Map API lỗi ↔ Màn hình (cho đội vá)

Frontend tham chiếu: `frontend-green` (creator.gen-green.global). Backend: `vcreator`.

### 5.1. Nhóm 🔴 BOLA — nặng nhất

| API | Màn hình | Route | Dữ liệu trả ra |
|---|---|---|---|
| `/user-statistic`, `/user-statistic/contents`, `/user-statistic/invitees`, `/user-statistic/invitees/statistic` | Trang thống kê cá nhân (`pages/statistic`) | `/statistics?code=<referralCode>` — **không** bọc auth ở FE | Thu nhập (cash), nội dung + lý do kiểm duyệt, mạng lưới giới thiệu |

- **Luồng FE:** `?code=` → `getInfoByReferralCode` → lấy `userInfo._id` → gọi `/user-statistic?user=<_id>` (`frontend-green/src/pages/statistic/model.ts:277`).
- **Lỗ thật:** backend nhận thẳng `?user=<id>`, không cần `code`.
- **Vá backend:** `backend/pkg/public/router/user_statistic.go` thêm `RequiredLogin`; `backend/pkg/public/handler/user_statistic.go` lấy `user` từ token, bỏ tham số.

### 5.2. Nhóm 🟠 khách đã phát hiện — `/events/*`

| API | Màn hình | Route | Dữ liệu / vấn đề |
|---|---|---|---|
| `/events/{id}/leaderboards` | Chi tiết sự kiện — bảng xếp hạng (`pages/home/_desktop`) | `/:partner/:slug/chi-tiet` | name, avatar, statistic **kèm cash** → cắt cash |
| `/events/{id}/content` | Chi tiết sự kiện + Bài đăng (`pages/content`) + landing | `/:partner/:slug/chi-tiet`, `/:partner/:slug/bai-dang`, `/` | name, link, `statistic.cash` → cắt cash |
| `/events/user-newest` | Chi tiết sự kiện — carousel creator mới | `/:partner/:slug/chi-tiet` | name, avatar Google/TikTok → proxy ảnh |
| `/events/statistic` | Landing (`main-home`) + Trang nhãn hàng (`partner-home`) | `/`, `/:partner/` | Số tổng (giữ); field `totalCommission` theo nhãn lộ ngân sách → **bỏ field**, GIỮ `?partner=` (partner-home cần view/nội dung/người tham gia) |

- **Vá cash:** `backend/pkg/public/service/event.go` (leaderboard + content) — tách DTO công khai, bỏ trường `cash*`.

### 5.3. Nhóm 🟡 khách chưa nêu

| API | Màn hình | Route |
|---|---|---|
| `/affiliate/campaigns` + `/:id` | Danh sách / chi tiết chiến dịch affiliate | `/affiliate/campaign/:id`, `/:partner/:slug/campaign/:id` |

### 5.4. Điểm sản phẩm cần quyết (không thuần kỹ thuật)

Màn `/statistics?code=` hiện là **trang chia sẻ hồ sơ qua link giới thiệu**, cố ý không login. Phải chọn một trong hai, vì hướng vá khác nhau:
- Nếu là **trang cá nhân** → bắt login + chỉ xem của mình (an toàn nhất).
- Nếu muốn giữ **share công khai** → giữ public nhưng bỏ sạch cash / lý do kiểm duyệt / mạng lưới, chỉ để lại thành tích.

---

## 6. Trạng thái sau release (kiểm chứng sống 27/08/2026)

Đã gọi trực tiếp production `vcreator-api.koc.com.vn` (read-only) để đối chiếu.

**✅ Đã fix:**
- **BOLA `/user-statistic/*` → HTTP 404** (endpoint đã tắt). Điểm P0 nặng nhất đóng.
- **Leaderboard `/events/{id}/leaderboards`:** bỏ sạch cash — top-level không còn `cashReward/cashTotal/cashBonus`; tầng lồng `tiktok/youtube` chỉ còn `view/like/comment`.
- **Content `/events/{id}/content`:** bỏ `statistic.cash` — chỉ còn `point/view/like/comment`.
- **`/events/statistic`:** đã bỏ `totalEventActive`.
- **Chuỗi enumerate → BOLA: đã đứt** — content vẫn phân trang ra user id, nhưng id không còn kèm tiền, và `/user-statistic` đã chết → không ghép thành dump được nữa.

**🟠 Còn vi phạm (chưa fix):**
- **Ngân sách theo nhãn:** `/events/statistic?partner=<id>` vẫn trả `totalCommission` theo nhãn (đo được VinFast = 6.006.440.129). Vá bằng cách **bỏ field `totalCommission`**, **KHÔNG chặn `?partner=`** (partner-home dùng param này cho các số khác).
- **Ảnh đại diện (URL mạng xã hội):** đây là ảnh **công khai** creator đang dùng trên Google/TikTok (không phải ảnh riêng tư do hệ thống lưu) → mức độ nhẹ. Vẫn nên đưa qua ảnh hệ thống để không phát tán URL tài khoản gốc (tránh tái định danh). Khách nêu đích danh. Cần phân biệt nguồn:
  - `/events/user-newest`: vẫn lộ `socialInfo.photo` nhưng **là endpoint chết ở mọi FE** (không nơi nào gọi/render) → tắt endpoint hoặc bỏ field, khỏi proxy.
  - `/events/{id}/leaderboards` + `/events/{id}/content`: đây mới là chỗ FE **thực sự render** ảnh thật — `getPhotoUser` fallback về `socialInfo.photo` khi `avatar` null (live: leaderboard 17/20 avatar null). Vá: (a) bỏ `socialInfo.photo` → user null-avatar hiện ảnh mặc định (rẻ, đủ đóng leak); hoặc (b) proxy giữ ảnh thật. Product quyết.
- **CORS:** vẫn `access-control-allow-origin: *` trên production.

**Để ngỏ (quyết định truyền thông):** `totalCommission` tổng (~30,4 tỷ) vẫn public — không phải lỗi, là mục cần chốt có công bố hay không.

---

*Tài liệu nội bộ. Chứa thông tin nhạy cảm về lỗ hổng đang tồn tại trên hệ thống production — hạn chế phát tán ngoài phạm vi xử lý sự cố cho đến khi các mục P0/P1 được vá.*
