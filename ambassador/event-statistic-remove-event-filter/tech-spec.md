# Technical Specification: Bỏ hỗ trợ lọc thống kê theo `event` ở API public `/events/statistic` (Ambassador)

**Date:** 2026-05-26
**Author:** vinhnguyen
**Version:** 1.0
**Project:** Ambassador (codename `viewboost`)
**Project Level:** 0 (1 story — security hardening)
**Status:** Draft

---

## Document Overview

Tech spec cho task **gỡ bỏ khả năng lọc thống kê theo từng `event`** trên API public `GET /events/statistic` (backend-public của Ambassador). Sau thay đổi, endpoint chỉ trả về **số liệu tổng hợp** (theo domain / partner / category), không cho phép public user xem thống kê của một event cụ thể.

> Đây là cùng một lớp vấn đề với vcreator và techcombank (3 sản phẩm fork cùng nguồn). Tech-spec gốc tham chiếu: `accesstrade-projects/docs/gen-green/event-statistic-remove-event-filter/tech-spec.md`.

**Related Documents:**
- Overview: [`overview.md`](./overview.md)
- Code reference (BE — Ambassador):
  - Router: `ambassabor/backend/pkg/public/router/event.go:22`
  - Handler: `ambassabor/backend/pkg/public/handler/event.go:88-119` (`GetStatistic`)
  - Service: `ambassabor/backend/pkg/public/service/event.go:88-175` (`GetStatistic`)
  - Request model: `ambassabor/backend/pkg/public/model/request/event.go:7-17` (`EventStatistic`)
  - Cache key: `ambassabor/backend/internal/module/redis/key.go` (`GetKeyCacheStatisticEvent`)
  - Query helper: `ambassabor/backend/internal/util/mgquery/common.go` (`AssignEvent`)

---

## Problem & Solution

### Problem Statement

API public `GET /events/statistic` nhận query params: `event`, `partner`, `category`, `fromAt`, `toAt`. Khi truyền `event`, response trả về thống kê **của riêng event đó**.

Đây là **endpoint public** (middleware `auth.Auth` chỉ parse JWT optional, không bắt buộc). Ai biết một `event_id` đều đọc được số liệu chi tiết của event đó:

```bash
curl 'https://<ambassador-host>/api/public/events/statistic?event=<EVENT_ID>&partner=<PARTNER_ID>'
# → {"totalView":...,"totalContent":...,"totalCommission":...,...}
```

**Số liệu theo từng event là thông tin nhạy cảm về business** (hoa hồng đã chi, độ phủ content) — không nên để public user biết. Tệ hơn, attacker có thể enumerate nhiều `event_id` để gom số liệu toàn bộ campaign.

### Proposed Solution

Bỏ hoàn toàn tác dụng của param `event` **chỉ riêng ở endpoint `/events/statistic`**:

- Handler `GetStatistic` **không gán** `param.Event` vào `CommonQuery.Event` nữa → service không filter theo event → trả về số liệu tổng hợp theo domain (và partner/category nếu có).
- Giữ nguyên `partner`, `category`, `fromAt/toAt` (các filter hợp lệ).
- **Không** đụng struct `request.EventStatistic` hay middleware validation chung, vì chúng còn được route `/events/user-newest` dùng (xem Risks).

---

## Requirements

### What Needs to Be Built

1. **Backend — gỡ filter `event` ở handler `GetStatistic`**
   Trong `pkg/public/handler/event.go`, khi build `CommonQuery` cho statistic, **bỏ field `Event: param.Event`**. Cache key cũng bỏ thành phần `event`.

2. **Cache key — bỏ chiều `event`**
   `GetKeyCacheStatisticEvent(event, partner, category)` (Ambassador có 3 tham số) đang key theo cả `event`. Sau thay đổi, statistic không phụ thuộc `event` → key chỉ nên theo `partner` + `category` (+ domain). Thêm hàm cache key mới hoặc gọi với `event=""` để tránh cache cũ trả số liệu theo-event.

3. **(Verify) Frontend — đảm bảo không vỡ**
   Verify FE Ambassador không phụ thuộc việc truyền `event` để render statistic. (Tham chiếu vcreator: đã verify cả 2 FE vcreator KHÔNG truyền `event` lên endpoint này; Ambassador cùng dòng FE nên nhiều khả năng tương tự — cần verify lại.)

### What This Does NOT Include

- **Không** thay đổi API admin (admin vẫn xem chi tiết theo event).
- **Không** xóa struct `request.EventStatistic` / middleware validation (còn dùng cho `/events/user-newest`).
- **Không** đổi shape response `EventStatisticResponse`.
- **Không** đụng `partner` / `category` / `fromAt` / `toAt` (filter hợp lệ).
- **Không** thêm auth/login mới (vẫn public, chỉ bỏ chiều dữ liệu nhạy cảm).

---

## Technical Approach

### Hiện trạng code (trước thay đổi)

**Handler** `pkg/public/handler/event.go:88-119`:

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
			Category:  param.Category,
			SortInterface: bson.D{{"_id", 1}},
		}
		key  = redis.GetKeyCacheStatisticEvent(param.Event, param.Partner, param.Category) // ← bỏ event
		data response.EventStatisticResponse
	)
	if param.FromAt != "" { query.FromAt = ... }
	if param.ToAt != "" { query.ToAt = ... }
	if ok := redis.GetJSON(key, &data); !ok {
		data = s.GetStatistic(ctx, query)
		redis.SetKeyValue(key, data, 60*time.Second)
	}
	return cc.Response200(data, "")
}
```

**Service** `pkg/public/service/event.go:88-175` gọi `query.AssignEvent(&cond)` ở các goroutine. Vì sau thay đổi `query.Event == ""`, `AssignEvent` sẽ **no-op** → **service không cần sửa**. Số liệu tự động thành tổng hợp.

> Điểm mấu chốt (giống vcreator/TCB): chỉ cần đảm bảo `query.Event` rỗng là toàn bộ pipeline tự bỏ filter event. Không sửa service.

### Thay đổi cụ thể

#### 1. Handler `pkg/public/handler/event.go` — `GetStatistic`

```go
query = &mgquery.CommonQuery{
	Domain:    cc.GetAppOrigin(),
	PartnerID: param.Partner,
	Category:  param.Category,
	SortInterface: bson.D{{"_id", 1}},
}
// event filter đã bị gỡ bỏ: public user không được xem thống kê theo từng event
key := redis.GetKeyCacheStatisticByPartnerCategory(param.Partner, param.Category)
// (hoặc gọi GetKeyCacheStatisticEvent("", param.Partner, param.Category))
```

#### 2. Cache key `internal/module/redis/key.go`

Hai lựa chọn:
- **Tối thiểu:** gọi `GetKeyCacheStatisticEvent("", param.Partner, param.Category)` — cố định phần event = rỗng.
- **Sạch hơn (khuyến nghị):** thêm hàm mới chỉ theo partner+category, đổi format key để cache cũ chứa số liệu theo-event không bị trả lại. Cần **purge cache cũ** sau deploy (hoặc dựa vào TTL 60s).

#### 3. (Optional) Request model

Giữ nguyên struct `EventStatistic` (vẫn còn field `Event` cho `/user-newest`). **Không xóa.** Chỉ cần handler statistic không đọc `param.Event`.

### API Design (sau thay đổi)

`GET /events/statistic`

| Query param | Trạng thái | Ghi chú |
|---|---|---|
| `event` | **Bị bỏ qua (no-op)** | Truyền vào cũng không lọc theo event |
| `partner` | Còn dùng | Lọc theo partner |
| `category` | Còn dùng | Lọc theo category |
| `fromAt` / `toAt` | Còn dùng | Lọc theo khoảng thời gian |

Response (không đổi shape): `totalView`, `totalContent`, `totalCommission`, `totalEventActive`, `totalUserWithContent`. Số liệu là **tổng hợp**, không còn của 1 event.

---

## Implementation Plan

### Stories

1. **STORY-1: Gỡ filter event + cache key + verify** (1.5h)
   - Sửa handler `GetStatistic` bỏ `Event: param.Event`.
   - Đổi cache key (bỏ chiều event).
   - Build + chạy local, gọi thử có/không param `event` để xác nhận kết quả giống nhau.
   - Verify FE Ambassador load trang home vẫn hiển thị số liệu (tổng hợp).
   - Verify regression `/events/user-newest` (dùng chung struct/validation).
   - Purge/đặt lại cache key cũ sau deploy.

Tổng: ~1.5-2h.

---

## Acceptance Criteria

- [ ] `GET /events/statistic?event=<bất kỳ ID>` trả về **CÙNG** kết quả với `GET /events/statistic` (không có `event`).
- [ ] Truyền `event` không thay đổi field nào trong response (5 field giữ nguyên).
- [ ] `?partner=<X>`, `?category=<Y>`, `?fromAt/toAt` vẫn lọc đúng (các filter hợp lệ còn tác dụng).
- [ ] Cache: sau deploy, không còn key cache trả số liệu theo từng event.
- [ ] Route `/events/user-newest` (dùng chung `v.EventStatistic`) vẫn chạy bình thường, lọc theo `event` đúng như cũ.
- [ ] FE Ambassador trang home vẫn hiển thị block thống kê bình thường.
- [ ] API admin **không bị ảnh hưởng**.

---

## Non-Functional Requirements

### Security
- Public user không suy ra được thống kê của một event cụ thể từ `event_id`; không enumerate được số liệu toàn bộ campaign.

### Performance
- Bỏ filter event → query quét rộng hơn. Đã có cache Redis TTL 60s. Verify P95 < 1s.

### Backward Compatibility
- Client cũ gửi `?event=...` không bị lỗi (param ignore), không cần deploy đồng bộ FE+BE.

### Maintainability
- Thay đổi khu trú trong handler + cache key; không sửa service / struct chung.

---

## Risks & Mitigation

- **Risk:** Sửa nhầm struct/validation chung làm vỡ `/events/user-newest`.
  - **Mitigation:** Chỉ sửa trong hàm handler `GetStatistic`. Regression test `/user-newest`.

- **Risk:** Cache key cũ (chứa số liệu theo event) tiếp tục trả về trong TTL 60s sau deploy.
  - **Mitigation:** Đổi format key hoặc flush prefix statistic ngay sau deploy. TTL 60s nên tác động ngắn.

- **Risk:** FE ngầm dựa vào số liệu theo-event.
  - **Mitigation:** Verify FE Ambassador (cùng dòng với vcreator — vcreator đã xác nhận FE không truyền `event`). Verify staging trước prod.

---

## Approval

**Reviewed By:**
- [ ] vinhnguyen (Author)
- [ ] Tech Lead Ambassador

---

## Next Steps

1. Tech Lead confirm cách xử lý cache key (đổi format vs flush).
2. Implement STORY-1, test bằng curl với/không `event`.
3. Verify regression `/user-newest` + FE trên staging.
4. Deploy + purge cache statistic.
5. Đồng bộ fix tương tự cho techcombank (xem `docs/t-fluencers/event-statistic-remove-event-filter/`).
