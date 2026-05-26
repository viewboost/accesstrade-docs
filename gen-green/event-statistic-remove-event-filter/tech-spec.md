# Technical Specification: Bỏ hỗ trợ lọc thống kê theo `event` ở API public `/events/statistic`

**Date:** 2026-05-26
**Author:** vinhnguyen
**Version:** 1.0
**Project:** Gen-Green (vcreator)
**Project Level:** 0 (1 story — bug-fix/security hardening)
**Status:** Draft

---

## Document Overview

Tech spec cho task **gỡ bỏ khả năng lọc thống kê theo từng `event`** trên API public `GET /events/statistic` (backend-public của vcreator). Sau thay đổi, endpoint chỉ trả về **số liệu tổng hợp toàn hệ thống (theo domain / partner)**, không cho phép public user xem thống kê của một event cụ thể.

**Related Documents:**
- Code reference (BE):
  - Router: `vcreator/backend/pkg/public/router/event.go:22`
  - Handler: `vcreator/backend/pkg/public/handler/event.go:85-107` (`GetStatistic`)
  - Service: `vcreator/backend/pkg/public/service/event.go:87-154` (`GetStatistic`)
  - Request model: `vcreator/backend/pkg/public/model/request/event.go:7-14` (`EventStatistic`)
  - Validation: `vcreator/backend/pkg/public/router/routevalidation/event.go:58-73`
  - Cache key: `vcreator/backend/internal/module/redis/key.go:40-42`
- Frontend caller:
  - `vcreator/frontend/src/services/event.ts:52-58`, `vcreator/frontend/src/configs/api.ts`
  - `vcreator/frontend-green/src/services/event.ts:52-58`, `vcreator/frontend-green/src/configs/api.ts`

---

## Problem & Solution

### Problem Statement

API public `GET /events/statistic` hiện nhận query param `event` (Event ID). Khi truyền `event`, response trả về thống kê **của riêng event đó**: số video được duyệt (`totalContent`), tổng view (`totalView`), tổng hoa hồng (`totalCommission`), số user có content (`totalUserWithContent`).

Đây là **endpoint public** (chỉ cần `ApiKeyAuth` mức app, không cần login user). Bất kỳ ai biết một `event_id` đều có thể gọi và đọc được số liệu chi tiết của event đó:

```bash
curl 'https://vcreator-api.koc.com.vn/events/statistic?event=<EVENT_ID>'
# → {"totalView":308048,"totalContent":73,"totalCommission":12300000,...}
```

**Số liệu theo từng event là thông tin nhạy cảm về business** (hoa hồng đã chi, độ phủ content của campaign) — không nên để public user biết được khi chỉ cần biết event ID.

### Proposed Solution

Bỏ hoàn toàn tác dụng của param `event` **chỉ riêng ở endpoint `/events/statistic`**:

- Handler `GetStatistic` **không gán** `param.Event` vào `CommonQuery.Event` nữa → service không filter theo event → trả về số liệu tổng hợp theo domain (và partner nếu có).
- Giữ nguyên param `partner` (đây là filter hợp lệ, dùng cho trang partner-home).
- **Không** đụng tới struct `request.EventStatistic` hay middleware validation chung, vì chúng còn được route `/events/user-newest` dùng (xem mục Risks).

Đây là cách thay đổi tối thiểu, an toàn, không phá vỡ các caller khác.

---

## Requirements

### What Needs to Be Built

1. **Backend — gỡ filter `event` ở handler `GetStatistic`**
   Trong `pkg/public/handler/event.go`, khi build `CommonQuery` cho statistic, **bỏ field `Event: param.Event`**. Cache key cũng bỏ thành phần `event` (xem mục Cache).

2. **Backend — dọn binding param `event` (optional, khuyến nghị)**
   Endpoint không còn dùng `event` → có thể bỏ tiếp nhận/đọc field này ở tầng statistic để tránh hiểu nhầm. Lưu ý struct `EventStatistic` dùng chung nên **không xóa field `Event`** khỏi struct; chỉ bỏ sử dụng nó trong luồng statistic.

3. **Cache key — bỏ chiều `event`**
   `GetKeyCacheStatisticEvent(event, partner)` đang key theo cả `event`. Sau thay đổi, statistic không phụ thuộc `event` → key chỉ nên theo `partner` (+ domain). Thêm hàm/biến cache key mới hoặc gọi với `event=""` để tránh phân mảnh cache & cache cũ trả số liệu theo event.

4. **(Verify) Frontend — đảm bảo không vỡ**
   Cả `frontend` và `frontend-green` đang gọi `getEventStatistic`. Cần xác nhận FE **không phụ thuộc** vào việc truyền `event` để hiển thị đúng (hiện FE truyền domain/partner là chính). Không bắt buộc sửa FE, nhưng phải verify response vẫn đúng dạng `EventStatisticResponse`.

### What This Does NOT Include

- **Không** thay đổi API admin `/events/statistic` (backend-admin) — admin vẫn được xem chi tiết theo event (đó là người dùng nội bộ, hợp lệ).
- **Không** xóa struct `request.EventStatistic` hay middleware `EventStatistic` validation (còn dùng cho `/events/user-newest`).
- **Không** đổi shape response `EventStatisticResponse` (vẫn `totalView`, `totalContent`, `totalCommission`, `totalEventActive`, `totalUserWithContent`).
- **Không** thêm auth/login requirement mới cho endpoint (vẫn public, chỉ bỏ chiều dữ liệu nhạy cảm).

---

## Technical Approach

### Technology Stack

- **Backend:** Go 1.24+, package `viewboost` (vcreator). Echo framework.
- **Database:** MongoDB (collections `event`, `event_analytic_daily`, `content`, `user`).
- **Cache:** Redis (key statistic TTL 30s).
- **Frontend:** Umi/DVA (`frontend`, `frontend-green`) — chỉ verify, không bắt buộc đổi.

### Hiện trạng code (trước thay đổi)

**Handler** `pkg/public/handler/event.go:85-107`:

```go
func (e eventImpl) GetStatistic(c echo.Context) error {
	var (
		cc    = echocustom.EchoGetCustomCtx(c)
		ctx   = cc.GetRequestCtx()
		s     = service.Event()
		param = cc.Get(constants.KeyQuery).(request.EventStatistic)
		query = &mgquery.CommonQuery{
			Domain:    cc.GetAppOrigin(),
			Event:     param.Event,        // ← BỎ DÒNG NÀY
			PartnerID: param.Partner,
			SortInterface: bson.D{{"_id", 1}},
		}
		key  = redis.GetKeyCacheStatisticEvent(param.Event, param.Partner) // ← bỏ event
		data response.EventStatisticResponse
	)
	if ok := redis.GetJSON(key, &data); !ok {
		data = s.GetStatistic(ctx, query)
		redis.SetKeyValue(key, data, 30*time.Second)
	}
	return cc.Response200(data, "")
}
```

**Service** `pkg/public/service/event.go:87-154` gọi `query.AssignEvent(&cond)` ở các goroutine. Vì sau thay đổi `query.Event == ""`, `AssignEvent` (xem `internal/util/mgquery/common.go:322-326`) sẽ **no-op** (không gán điều kiện `event`), nên **service không cần sửa** — số liệu tự động trở thành tổng hợp theo domain/partner.

```go
func (q *CommonQuery) AssignEvent(cond *bson.M) {
	if q.Event != "" && !util.ConvertStringToObjectID(q.Event).IsZero() {
		(*cond)["event"] = util.ConvertStringToObjectID(q.Event)
	}
}
```

> Đây là điểm mấu chốt: chỉ cần đảm bảo `query.Event` rỗng là toàn bộ pipeline tự bỏ filter event. Không phải sửa service logic.

### Thay đổi cụ thể

#### 1. Handler `pkg/public/handler/event.go` — `GetStatistic`

```go
query = &mgquery.CommonQuery{
	Domain:    cc.GetAppOrigin(),
	PartnerID: param.Partner,
	SortInterface: bson.D{{"_id", 1}},
}
// event filter đã bị gỡ bỏ vì public user không được xem thống kê theo từng event
key := redis.GetKeyCacheStatisticEventByPartner(param.Partner) // hoặc GetKeyCacheStatisticEvent("", param.Partner)
```

#### 2. Cache key `internal/module/redis/key.go`

Hai lựa chọn:

- **Tối thiểu:** gọi `GetKeyCacheStatisticEvent("", param.Partner)` — cache key cố định phần event = rỗng. Đơn giản nhất, không thêm hàm.
- **Sạch hơn (khuyến nghị):** thêm hàm mới chỉ theo partner, ví dụ:
  ```go
  func GetKeyCacheStatisticEventByPartner(partner string) string {
      return fmt.Sprintf(CacheStatisticEventByPartner, partner)
  }
  ```
  Cần lưu ý **purge cache cũ** sau deploy (hoặc đổi tên format key) để key cũ chứa số liệu theo-event không bị trả lại trong TTL.

#### 3. (Optional) Request model `pkg/public/model/request/event.go`

Giữ nguyên struct `EventStatistic` (vẫn còn field `Event` cho `/user-newest`). **Không xóa.** Chỉ cần đảm bảo handler statistic không đọc `param.Event`.

### API Design (sau thay đổi)

`GET /events/statistic`

| Query param | Trạng thái | Ghi chú |
|---|---|---|
| `event` | **Bị bỏ qua (deprecated/no-op)** | Truyền vào cũng không lọc theo event nữa |
| `partner` | Còn dùng | Lọc theo partner |

Response (không đổi shape):

```json
{
  "code": 1,
  "data": {
    "totalView": 308048,
    "totalContent": 73,
    "totalCommission": 12300000,
    "totalEventActive": 0,
    "totalUserWithContent": 94
  },
  "message": "Thành công!"
}
```

> Lưu ý: các con số sau thay đổi là **tổng hợp toàn domain** (hoặc theo partner), không còn là số của 1 event.

---

## Implementation Plan

### Stories

1. **STORY-1: Gỡ filter event + cache key + verify** (1.5h)
   - Sửa handler `GetStatistic` bỏ `Event: param.Event`.
   - Đổi cache key (bỏ chiều event hoặc thêm hàm by-partner).
   - Build + chạy local, gọi thử endpoint có/không param `event` để xác nhận kết quả giống nhau (event bị bỏ qua).
   - Verify FE (`frontend`, `frontend-green`) load trang home vẫn hiển thị số liệu (tổng hợp).
   - Purge/đặt lại cache key cũ trên môi trường deploy.

### Development Phases

**Phase 1 (BE):** ~1.5h — sửa handler + cache, test bằng curl.
**Phase 2 (Verify):** ~0.5h — xác nhận FE không vỡ + regression `/user-newest`.

Tổng: ~2h.

---

## Acceptance Criteria

- [ ] `GET /events/statistic?event=<bất kỳ ID>` trả về **CÙNG** kết quả với `GET /events/statistic` (không có `event`) → chứng minh `event` đã bị bỏ qua hoàn toàn.
- [ ] Response vẫn đúng shape `EventStatisticResponse` (đủ 5 field), không lỗi 400/500.
- [ ] `GET /events/statistic?partner=<X>` vẫn lọc đúng theo partner (param `partner` còn tác dụng).
- [ ] Cache: sau deploy, không còn key cache trả số liệu theo từng event (đã purge/đổi format key).
- [ ] Route `/events/user-newest` (dùng chung struct + validation `EventStatistic`) vẫn chạy bình thường, vẫn lọc theo `event` đúng như cũ (không bị ảnh hưởng).
- [ ] Trang home của `frontend` và `frontend-green` (creator.gen-green.global) vẫn hiển thị block thống kê bình thường.
- [ ] API admin `/events/statistic` (backend-admin) **không bị ảnh hưởng** — admin vẫn xem được thống kê theo event.

---

## Non-Functional Requirements

### Security
- Mục tiêu chính của task: **không leak số liệu theo từng event qua API public.** Sau thay đổi, public user không thể suy ra thống kê của một event cụ thể từ `event_id`.

### Performance
- Bỏ filter event → query có thể quét rộng hơn (toàn domain). Đã có cache Redis TTL 30s nên không lo P95. Verify thời gian response vẫn <1s sau khi bỏ filter.

### Other
- **Backward compatibility:** Client cũ vẫn gửi `?event=...` sẽ không lỗi (param bị ignore), đảm bảo không phải deploy đồng bộ FE+BE.

---

## Dependencies

- **Code coupling:** Struct `request.EventStatistic` + middleware validation `EventStatistic` dùng chung giữa `/statistic` và `/user-newest`. **Không** được xóa/sửa struct này.
- **Cache:** Redis key `CacheStatisticEvent` — cần purge sau deploy.
- **Team:** Không có dependency external.

---

## Risks & Mitigation

- **Risk:** Sửa nhầm struct/validation chung làm vỡ `/events/user-newest`.
  - **Mitigation:** Chỉ sửa trong hàm handler `GetStatistic`, **không** đụng `request.EventStatistic` / `routevalidation`. Regression test `/user-newest` có/không `event`.

- **Risk:** Cache key cũ (đã chứa số liệu theo event) tiếp tục được trả về trong TTL 30s sau deploy.
  - **Mitigation:** Đổi format key (thêm hàm by-partner) hoặc flush key prefix statistic ngay sau deploy. TTL chỉ 30s nên tác động ngắn dù không purge.

- **Risk (ĐÃ LOẠI BỎ — verify 2026-05-26):** FE ngầm dựa vào số liệu theo-event để render.
  - **Kết luận:** Đã trace đầy đủ cả 2 FE (`frontend`, `frontend-green`): KHÔNG page nào truyền `event` lên `/events/statistic`. Các page chỉ dispatch query `{}` (home-primary, main-home) hoặc `{ partner }` (partner-home) — `pages/*/index.tsx` → `services/event.ts` → `configs/api.ts` (url `/events/statistic`, không gắn event). Param `event` ở endpoint này thực chất đã là dead param từ phía FE; chỉ client gọi thủ công (curl/test) mới dùng. → Thay đổi backend không ảnh hưởng FE production, không cần sửa FE.

- **Risk:** Có client/đối tác bên ngoài đang gọi với `event` và kỳ vọng số liệu theo event.
  - **Mitigation:** Đây chính là hành vi cần chặn (lý do bảo mật). Nếu có nhu cầu hợp lệ → chuyển sang API admin có auth. Thông báo nội bộ trước khi deploy.

---

## Approval

**Reviewed By:**
- [ ] vinhnguyen (Author)
- [ ] Tech Lead Gen-Green

---

## Next Steps

1. Tech Lead confirm cách xử lý cache key (đổi format vs flush).
2. Implement STORY-1, test bằng curl với/không `event`.
3. Verify regression `/user-newest` + 2 FE trên staging.
4. Deploy + purge cache statistic.
