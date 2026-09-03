# Tech Spec — Siết bảo mật API công khai Green Creator (phần đã hoàn tất)

- **Ngày:** 27/08/2026
- **Hệ thống:** backend `vcreator` → API `vcreator-api.koc.com.vn` (prod), `api-dev-vcreator.diso.vn` (dev)
- **Trạng thái:** Đã triển khai + verify trên develop
- **Đối tượng đọc:** đội kỹ thuật

---

## 1. Bối cảnh & mục tiêu

Nhóm API công khai (không yêu cầu đăng nhập) đang trả kèm dữ liệu cá nhân/tài chính vào cùng gói tin dùng cho màn công khai. Nguyên nhân gốc: **tái sử dụng chung một cấu trúc dữ liệu (model mg) cho cả màn công khai lẫn màn cá nhân**, khiến các trường của màn cá nhân đi theo ra ngoài dù giao diện không dùng.

**Mục tiêu:** tách dữ liệu nhạy cảm khỏi kênh công khai mà **không phá vỡ** landing/bảng xếp hạng, theo nguyên tắc:
1. Endpoint công khai chỉ trả đúng trường giao diện cần (DTO riêng, không serialize thẳng model mg).
2. Dữ liệu cá nhân (thu nhập, nội dung theo user) chỉ truy cập được sau đăng nhập và chỉ của chính chủ.
3. Siết bề mặt tấn công: chống liệt kê diện rộng, chặn CORS, đóng endpoint chết.

---

## 2. Phạm vi

**Trong phạm vi tài liệu này (đã hoàn tất):**
- Vô hiệu hoá BOLA nhóm `/user-statistic`.
- Tách DTO công khai cho bảng xếp hạng và danh sách nội dung (bỏ trường tiền).
- Bỏ `totalCommission` và `totalEventActive` khỏi `/events/statistic` công khai.
- Giới hạn phân trang bảng xếp hạng.
- Đóng endpoint chết `/events/user-newest`.
- Cấu hình CORS theo allowlist.

**Ngoài phạm vi (còn nợ):** proxy ảnh đại diện leaderboard/content; rate-limit nhóm public. Xem Mục 7.

---

## 3. Chi tiết thay đổi

### 3.1. Vô hiệu hoá BOLA — nhóm `/user-statistic`

**Vấn đề:** `GET /user-statistic?user=<id>` (và `/contents`, `/invitees`) nhận `user_id` từ query, không có `RequiredLogin` → truyền id bất kỳ là đọc được thu nhập / nội dung (kèm lý do kiểm duyệt) / mạng lưới giới thiệu của người đó. Ghép với phân trang `/events/{id}/content` (liệt kê được user_id) → dump diện rộng.

**Giải pháp:** không đăng ký nhóm route này ở tầng public.

**Code:** [`router/router.go:34`](../vcreator/backend/pkg/public/router/router.go#L34) — `// userStatistic(r)` (comment out).

**Hệ quả:** cả 4 route `/user-statistic*` trả `404`. Màn `/statistics` của frontend-green (route mồ côi, không có điều hướng in-app) mất nguồn dữ liệu — chấp nhận được vì màn này đã không còn dùng.

**Verify:** SEC-01, SEC-05 (Pass — 404).

### 3.2. Tách DTO công khai cho bảng xếp hạng — bỏ trường tiền

**Vấn đề:** `GetLeaderBoard` map `Statistic: sf.Statistic` (kiểu `modelmg.UserEventStatistic`) → serialize cả `cashReward`, `cashTotal`, `cashBonus` ra ngoài.

**Giải pháp:** DTO riêng `LeaderBoardStatistic`, chỉ giữ các trường đếm/điểm/lượt tương tác, không có nhánh cash.

```go
// backend/pkg/public/model/response/event.go
type LeaderBoardStatistic struct {
    TotalContent int64                      `json:"totalContent"`
    PointTotal   PublicMetric               `json:"pointTotal"`
    Tiktok       LeaderBoardSourceStatistic `json:"tiktok"`   // view/like/comment
    Youtube      LeaderBoardSourceStatistic `json:"youtube"`
    // ... youtubeShort, facebook, facebookReels, instagram, instagramReels, threads
}
```

`UserEventResponse.Statistic` đổi từ `modelmg.UserEventStatistic` → `LeaderBoardStatistic`. Mỗi `LeaderBoardSourceStatistic` chỉ có `view/like/comment` (không `cash`).

**Verify:** SEC-02 (Pass — không còn cash ở cả top-level lẫn tầng nền tảng con).

### 3.3. Tách DTO công khai cho danh sách nội dung — bỏ trường tiền

**Vấn đề:** `ContentResponse.Statistic` serialize `modelmg.UserContentStatistic` → kèm `cash` (thu nhập từng bài).

**Giải pháp:** DTO `ContentStatisticPublic` + hàm map `NewContentStatisticPublic` bỏ nhánh Cash.

```go
type ContentStatisticPublic struct {
    Point   PublicMetric `json:"point"`
    View    PublicMetric `json:"view"`
    Like    PublicMetric `json:"like"`
    Comment PublicMetric `json:"comment"`
}
// NewContentStatisticPublic(s modelmg.UserContentStatistic) — map, bỏ Cash
```

**Verify:** SEC-03 (Pass — statistic không còn `cash`).

### 3.4. Bỏ `totalCommission` khỏi `/events/statistic` công khai

**Vấn đề:** `/events/statistic?partner=<id>` trả `totalCommission = cashPending + cashCompleted` theo từng nhãn → lộ ngân sách hoa hồng (số liệu hợp đồng khách hàng).

**Giải pháp:** bỏ hẳn field khỏi `EventStatisticResponse` và ngừng tính trong service. **Giữ nguyên param `?partner=`** vì `partner-home` cần nó cho các số khác (view/nội dung/người tham gia).

**Code:**
- [`response/event.go`](../vcreator/backend/pkg/public/model/response/event.go) — comment field `TotalCommission`.
- [`service/event.go` `GetStatistic`](../vcreator/backend/pkg/public/service/event.go) — bỏ init + bỏ gán `res.TotalCommission`.

**Tương thích:** `frontend-green` (FE đang dùng duy nhất) **không** đọc `totalCommission` ở đâu → bỏ field **không ảnh hưởng UI**. (`frontend-vcreator` đã ngừng sử dụng nên không tính.)

**Verify:** SEC-08 (Pass — không còn `totalCommission`).

### 3.5. Bỏ `totalEventActive` khỏi `/events/statistic`

Field FE app không dùng, trước đây tính bằng một goroutine đếm event active. Bỏ field + bỏ goroutine trong `GetStatistic`. **Verify:** SEC-04 (Pass).

### 3.6. Giới hạn phân trang bảng xếp hạng (chống liệt kê)

**Vấn đề:** phân trang không giới hạn → hút toàn bộ.

**Giải pháp:** cap tổng số item.

```go
// backend/internal/constants/event.go
EventLeaderBoardLimit    = 20   // item/trang
EventLeaderBoardMaxItems = 100  // tổng tối đa
```

Handler `GetLeaderBoard`: nếu `page*limit >= MaxItems` → trả rỗng, không query DB; chỉ cấp `nextPageToken` khi trang kế còn trong giới hạn. **Verify:** SEC-06 (Pass — bảng xếp hạng vẫn chạy).

### 3.7. Đóng endpoint chết `/events/user-newest`

**Vấn đề:** endpoint không được FE nào (green/vcreator/frontend) gọi/render, nhưng vẫn public trả `socialInfo.photo` (URL Google/TikTok) nếu gọi trực tiếp.

**Giải pháp:** comment out route.

**Code:** [`router/event.go:23`](../vcreator/backend/pkg/public/router/event.go#L23) — `// g.GET("/user-newest", ...)`.

**Verify:** SEC-11 (Pass — 404).

### 3.8. CORS theo allowlist

**Vấn đề:** production trả `access-control-allow-origin: *` (do biến env `CORS` rỗng → fallback `*`).

**Giải pháp:** cấu hình biến env `CORS` = danh sách tên miền chính thức (comma-separated). Middleware đã hỗ trợ sẵn: `AllowOrigins` đọc từ env, `AllowCredentials: false`.

**Code:** [`internal/middleware/cors.go`](../vcreator/backend/internal/middleware/cors.go) — không đổi logic; fix nằm ở **cấu hình env khi deploy**.

**Verify:** SEC-12 (Pass — origin lạ không được cấp ACAO; origin hợp lệ nhận đúng tên miền, không còn `*`).

---

## 4. Kiểm thử

Bộ test case: `test-cases-bao-mat-api-green-2026-08-27.csv`. Chạy trên develop 27/08/2026 — **SEC-01→08, SEC-11, SEC-12 đều Pass** (toàn bộ nội dung trong phạm vi).

Test tự động trong repo:
- `backend/pkg/public/model/response/statistic_shape_test.go` — chốt shape response (`totalCommission`, `totalEventActive` phải vắng; `userStatistic` bị drop).
- `backend/pkg/public/handler/leaderboard_pagination_test.go` — chốt giới hạn phân trang.
- `backend/pkg/public/router/router_test.go` — thứ tự middleware.

---

## 5. Rollout

- Tách trường tiền leaderboard/content, disable BOLA, cap phân trang, trim field thừa: đã lên `release` (các PR "remove field response not use" + fix security cash).
- Bỏ `totalCommission` + đóng `user-newest`: PR #143 (`fix/security-hide-commission-and-disable-usernewest`), đã có trên develop.
- CORS allowlist: cấu hình env khi deploy.

---

## 6. Ngoài phạm vi / còn nợ

1. **Ảnh đại diện Google/TikTok** trên `/events/{id}/leaderboards` và `/content`: FE render qua `getPhotoUser` fallback về `socialInfo.photo` khi `avatar` null (đa số). Phương án: (a) bỏ `socialInfo.photo` → hiện ảnh mặc định; hoặc (b) proxy qua ảnh hệ thống. **Chưa làm.**
2. **Rate-limit** nhóm API công khai (OWASP API4): chưa có. Ngoài yêu cầu khách.
3. **Hàng rào tự động chống tái diễn:** đề xuất bổ sung test danh sách trắng route công khai — route mới ngoài danh sách thì CI đỏ.

---

## 7. Rủi ro & lưu ý

- Bỏ `totalCommission`: không tác động UI — `frontend-green` (FE duy nhất đang dùng) không đọc field này; `frontend-vcreator` đã ngừng sử dụng.
- Handler/service `GetListUserNewest` trở thành dead-code sau khi tắt route — vô hại, có thể dọn sau.
- Màn `/statistics` (frontend-green) sẽ 404 khi gọi `/user-statistic` — màn này là route mồ côi, không ảnh hưởng luồng in-app; nên gỡ hẳn ở FE để sạch.
