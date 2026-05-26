# Technical Specification: Bỏ hỗ trợ lọc thống kê theo `event` ở API public `/events/statistic` (T-Fluencers)

**Date:** 2026-05-26
**Author:** vinhnguyen
**Version:** 1.0
**Project:** T-Fluencers (Techcombank)
**Project Level:** 0 (1 story — security hardening)
**Status:** Draft

---

## Document Overview

Tech spec cho task **gỡ bỏ khả năng lọc thống kê theo từng thử thách (`event`)** trên API public `GET /events/statistic` (backend-public của T-Fluencers). Sau thay đổi, endpoint chỉ trả về **số liệu tổng hợp** (theo domain / partner), không cho phép public user xem thống kê của một thử thách cụ thể.

> Cùng một lớp vấn đề với vcreator và ambassador (3 sản phẩm fork cùng nguồn). T-Fluencers fork từ vcreator nên code gần như giống hệt vcreator gốc.

**Related Documents:**
- Overview: [`overview.md`](./overview.md)
- Code reference (BE — T-Fluencers / `techcombank/backend`):
  - Router: `techcombank/backend/pkg/public/router/event.go:22`
  - Handler: `techcombank/backend/pkg/public/handler/event.go:152-174` (`GetStatistic`)
  - Service: `techcombank/backend/pkg/public/service/event.go:288-363` (`GetStatistic`)
  - Request model: `techcombank/backend/pkg/public/model/request/event.go:7-14` (`EventStatistic`)
  - Response model: `techcombank/backend/pkg/public/model/response/event.go:32-40`
  - Cache key: `techcombank/backend/internal/module/redis/key.go` (`GetKeyCacheStatisticEvent`)
  - Query helper: `techcombank/backend/internal/util/mgquery/common.go` (`AssignEvent`)

---

## Problem & Solution

### Problem Statement

API public `GET /events/statistic` nhận query params `event` (mã thử thách) và `partner`. Khi truyền `event`, response trả về thống kê **của riêng thử thách đó**: số video được duyệt (`totalContent`), tổng view (`totalView`), tổng hoa hồng (`totalCommission`), số influencer có bài đăng (`totalUserWithContent`).

Đây là **endpoint public** (route không có `a.RequiredLogin`; middleware `auth.Auth` chỉ parse JWT optional). Ai biết một `event_id` đều đọc được số liệu chi tiết:

```bash
curl 'https://<tfluencer-host>/events/statistic?event=<EVENT_ID>&partner=<PARTNER_ID>'
# → {"totalView":...,"totalContent":...,"totalCommission":...,...}
```

**Số liệu theo từng thử thách là thông tin nhạy cảm về business** — không nên để public user biết. Attacker có thể enumerate nhiều `event_id` để theo dõi/gom số liệu campaign (kể cả của đối thủ trong cùng hệ thống).

### Proposed Solution

Bỏ hoàn toàn tác dụng của param `event` **chỉ riêng ở endpoint `/events/statistic`**:

- Handler `GetStatistic` **không gán** `param.Event` vào `CommonQuery.Event` nữa → service không filter theo event → trả về số liệu tổng hợp theo domain (và partner nếu có).
- Giữ nguyên `partner` (filter hợp lệ).
- **Không** đụng struct `request.EventStatistic` hay middleware validation chung, vì chúng còn được route `/events/user-newest` dùng (xem Risks).

---

## Requirements

### What Needs to Be Built

1. **Backend — gỡ filter `event` ở handler `GetStatistic`**
   Trong `pkg/public/handler/event.go`, khi build `CommonQuery` cho statistic, **bỏ field `Event: param.Event`**. Cache key cũng bỏ thành phần `event`.

2. **Cache key — bỏ chiều `event`**
   `GetKeyCacheStatisticEvent(event, partner)` đang key theo cả `event`. Sau thay đổi, statistic không phụ thuộc `event` → key chỉ nên theo `partner` (+ domain). Thêm hàm cache key mới hoặc gọi với `event=""`.

3. **(Verify) Frontend — đảm bảo không vỡ**
   Verify FE T-Fluencers không phụ thuộc việc truyền `event` để render statistic. (Tham chiếu vcreator: cả 2 FE vcreator KHÔNG truyền `event` lên endpoint này.)

### What This Does NOT Include

- **Không** thay đổi API admin (admin vẫn xem chi tiết theo thử thách).
- **Không** xóa struct `request.EventStatistic` / middleware validation (còn dùng cho `/events/user-newest`).
- **Không** đổi shape response `EventStatisticResponse`.
- **Không** đụng `partner` (filter hợp lệ).
- **Không** thêm auth/login mới (vẫn public, chỉ bỏ chiều dữ liệu nhạy cảm).

---

## Technical Approach

### Hiện trạng code (trước thay đổi)

**Handler** `pkg/public/handler/event.go:152-174`:

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

**Service** `pkg/public/service/event.go:288-363` gọi `query.AssignEvent(&cond)` ở các goroutine. Vì sau thay đổi `query.Event == ""`, `AssignEvent` sẽ **no-op** → **service không cần sửa**. Số liệu tự động thành tổng hợp.

> Điểm mấu chốt (giống vcreator/Ambassador): chỉ cần đảm bảo `query.Event` rỗng là toàn bộ pipeline tự bỏ filter event.

### Thay đổi cụ thể

#### 1. Handler `pkg/public/handler/event.go` — `GetStatistic`

```go
query = &mgquery.CommonQuery{
	Domain:    cc.GetAppOrigin(),
	PartnerID: param.Partner,
	SortInterface: bson.D{{"_id", 1}},
}
// event filter đã bị gỡ bỏ: public user không được xem thống kê theo từng thử thách
key := redis.GetKeyCacheStatisticByPartner(param.Partner)
// (hoặc gọi GetKeyCacheStatisticEvent("", param.Partner))
```

#### 2. Cache key `internal/module/redis/key.go`

Hai lựa chọn:
- **Tối thiểu:** gọi `GetKeyCacheStatisticEvent("", param.Partner)` — cố định phần event = rỗng.
- **Sạch hơn (khuyến nghị):** thêm hàm mới chỉ theo partner, đổi format key để cache cũ chứa số liệu theo-event không bị trả lại. Cần **purge cache cũ** sau deploy (hoặc dựa vào TTL 30s).

#### 3. (Optional) Request model

Giữ nguyên struct `EventStatistic` (vẫn còn field `Event` cho `/user-newest`). **Không xóa.**

### API Design (sau thay đổi)

`GET /events/statistic`

| Query param | Trạng thái | Ghi chú |
|---|---|---|
| `event` | **Bị bỏ qua (no-op)** | Truyền vào cũng không lọc theo thử thách |
| `partner` | Còn dùng | Lọc theo partner |

Response (không đổi shape): `totalView`, `totalContent`, `totalCommission`, `totalEventActive`, `totalUserWithContent`. Số liệu là **tổng hợp**, không còn của 1 thử thách.

---

## Implementation Plan

### Stories

1. **STORY-1: Gỡ filter event + cache key + verify** (1.5h)
   - Sửa handler `GetStatistic` bỏ `Event: param.Event`.
   - Đổi cache key (bỏ chiều event).
   - Build + chạy local, gọi thử có/không param `event` để xác nhận kết quả giống nhau.
   - Verify FE T-Fluencers load trang home vẫn hiển thị số liệu (tổng hợp).
   - Verify regression `/events/user-newest` (dùng chung struct/validation).
   - Purge/đặt lại cache key cũ sau deploy.

Tổng: ~1.5-2h.

---

## Acceptance Criteria

- [ ] `GET /events/statistic?event=<bất kỳ ID>` trả về **CÙNG** kết quả với `GET /events/statistic` (không có `event`).
- [ ] Truyền `event` không thay đổi field nào trong response (5 field giữ nguyên).
- [ ] `?partner=<X>` vẫn lọc đúng theo partner.
- [ ] Cache: sau deploy, không còn key cache trả số liệu theo từng thử thách.
- [ ] Route `/events/user-newest` (dùng chung `v.EventStatistic`) vẫn chạy bình thường, lọc theo `event` đúng như cũ.
- [ ] FE T-Fluencers trang home vẫn hiển thị block thống kê bình thường.
- [ ] API admin **không bị ảnh hưởng**.

---

## Non-Functional Requirements

### Security
- Public user không suy ra được thống kê của một thử thách cụ thể từ `event_id`; không enumerate được số liệu toàn bộ campaign.

### Performance
- Bỏ filter event → query quét rộng hơn. Đã có cache Redis TTL 30s. Verify P95 < 1s.

### Backward Compatibility
- Client cũ gửi `?event=...` không bị lỗi (param ignore), không cần deploy đồng bộ FE+BE.

### Maintainability
- Thay đổi khu trú trong handler + cache key; không sửa service / struct chung.

---

## Risks & Mitigation

- **Risk:** Sửa nhầm struct/validation chung làm vỡ `/events/user-newest`.
  - **Mitigation:** Chỉ sửa trong hàm handler `GetStatistic`. Regression test `/user-newest`.

- **Risk:** Cache key cũ (chứa số liệu theo event) tiếp tục trả về trong TTL 30s sau deploy.
  - **Mitigation:** Đổi format key hoặc flush prefix statistic ngay sau deploy. TTL 30s nên tác động ngắn.

- **Risk:** FE ngầm dựa vào số liệu theo-event.
  - **Mitigation:** Verify FE T-Fluencers (cùng dòng với vcreator — vcreator đã xác nhận FE không truyền `event`). Verify staging trước prod.

---

## Approval

**Reviewed By:**
- [ ] vinhnguyen (Author)
- [ ] Tech Lead T-Fluencers

---

## Next Steps

1. Tech Lead confirm cách xử lý cache key (đổi format vs flush).
2. Implement STORY-1, test bằng curl với/không `event`.
3. Verify regression `/user-newest` + FE trên staging.
4. Deploy + purge cache statistic.
5. Đồng bộ fix tương tự cho vcreator & ambassador (cùng đợt nếu được — xem `docs/gen-green/` và `docs/ambassador/`).
