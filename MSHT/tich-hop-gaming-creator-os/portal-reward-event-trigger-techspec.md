# Tech Spec — Trigger sự kiện mini_game_v2 sang Portal Reward

- Ngày: 2026-08-28
- PRD kèm theo: `2026-08-28-portal-reward-event-trigger-prd.md`
- Trạng thái: draft, chờ review

Tài liệu này là bản dịch PRD sang mã nguồn: đường dẫn file, chữ ký hàm, hợp đồng,
migration, thứ tự triển khai. Quyết định *vì sao* nằm ở PRD, không lặp lại ở đây.

---

## 1. Bản đồ thay đổi

| Repo / service | File | Việc |
|---|---|---|
| `event` | `internal/model/system_event.go` | **mới** — model bảng dấu vết |
| `event` | `internal/model/portal_reward.go` | **mới** — kiểu `RawEvent`, hằng số trạng thái/kênh |
| `event` | `internal/module/mongodb/col.go` | +1 hằng số collection |
| `event` | `internal/module/mongodb/index.go` | +1 khối index |
| `event` | `internal/dao/system_event.go` | **mới** — DAO |
| `event` | `internal/module/redisdb/key.go` | +1 khoá con trỏ (có `partnerId`) |
| `event` | `internal/grpc/tracking/{client.go,request.go}` | **mới** — client gRPC tracking |
| `event` | `internal/config/env_keys.go` | +`GRPC_ADDRESS_TRACKING`, +cấu hình job |
| `event` | `internal/service/portalreward/dispatcher.go` | **mới** — deep module |
| `event` | `internal/service/portalreward/codec.go` | **mới** — sinh `code`, ánh xạ trạng thái |
| `event` | `app/service/portal_reward_collector_order.go` | **mới** |
| `event` | `app/service/portal_reward_collector_click.go` | **mới** |
| `event` | `app/service/portal_reward_trigger.go` | **mới** — điều phối |
| `event` | `app/schedule/schedule.go` | +1 dòng đăng ký cron |
| `event` | `external/natsio/transaction_group.go` | mở rộng req/res |
| `event` | `external/proto/grpc/proto/tracking/tracking.proto` | +RPC `ListClicks` |
| `event` | `admin/model/event.go` | +`CondTracking`, validate `eventCodes` |
| `event` | `admin/service/event.go` | map `CondTracking` vào response |
| `tracking` | `external/proto/grpc/proto/tracking/tracking.proto` | +RPC `ListClicks` |
| `tracking` | `pkg/grpc/node/{node.go,handler.go,click.go}` | +handler |
| `tracking` | `internal/dao/click.go` | +`FindByCondition` |
| `tracking` | `internal/module/database/index.go` | +index `{createdAt, _id}` |
| `transaction` (mỗi bank) | `external/natsio/transaction_group.go` | mở rộng req/res |
| `transaction` (mỗi bank) | subscriber `GetListTransactionGroup` | map điều kiện mới |

---

## 2. Hợp đồng liên service

### 2.1 NATS — `TransactionGroupGetListReq` / `Res`

`event/external/natsio/transaction_group.go` và bản gốc trong repo transaction từng bank.
Mọi trường mới đều `omitempty` để gamification không đổi hành vi.

```go
type TransactionGroupGetListReq struct {
	// --- giữ nguyên ---
	UserId             string `json:"userId"`
	FromAt             string `json:"fromAt"`
	TransactionGroupId string `json:"transactionGroupId"` // cursor keyset

	// --- mới ---
	ToAt             string   `json:"toAt,omitempty"`
	OrderTimeStartAt string   `json:"orderTimeStartAt,omitempty"` // = event.StartAt
	OrderTimeEndAt   string   `json:"orderTimeEndAt,omitempty"`   // = event.EndAt
	BrandIds         []string `json:"brandIds,omitempty"`
	ShopIds          []string `json:"shopIds,omitempty"`
	OrderType        string   `json:"orderType,omitempty"`        // all|normal|brand_bonus
	MinOrderValue    float64  `json:"minOrderValue,omitempty"`
	Statuses         []string `json:"statuses,omitempty"`
	Limit            int64    `json:"limit,omitempty"`
}

type TransactionGroupInfo struct {
	TransactionGroupId string             `json:"transactionGroupId"`
	OrderId            string             `json:"orderId"`   // MỚI
	OrderTime          string             `json:"orderTime"`
	CreatedAt          string             `json:"createdAt"`
	UpdatedAt          string             `json:"updatedAt"` // MỚI — cursor nhánh order
	UserId             string             `json:"userId"`
	Status             string             `json:"status"`    // MỚI — pending|approved|cashback|rejected
	BrandRoot          primitive.ObjectID `json:"brandRoot"`
	TransactionValue   float64            `json:"transactionValue"`
	IsBonus            bool               `json:"isBonus"`
}
```

**Phía transaction service** — subscriber `GetListTransactionGroup` dựng bson qua helper
`getTransactionCondByReq` đã có (`internal/grpc/node/handler.go`). Quy tắc map:

| Field req | bson | Ghi chú |
|---|---|---|
| `OrderTimeStartAt`/`OrderTimeEndAt` | `orderTime: {$gte, $lte}` | rỗng thì bỏ |
| `FromAt`/`ToAt` | `updatedAt: {$gte, $lte}` | cursor, không phải điều kiện nghiệp vụ |
| `BrandIds` | `root: {$in}` | rỗng ⇒ không lọc (tương đương `IsAll`) |
| `ShopIds` | `shopId: {$in}` | rỗng ⇒ không lọc |
| `OrderType` | `isBonus` | `all` ⇒ không lọc; `normal` ⇒ `false`; `brand_bonus` ⇒ `true` |
| `MinOrderValue` | `transactionValue: {$gte}` | `0` ⇒ không lọc |
| `Statuses` | `status: {$in}` | rỗng ⇒ không lọc |
| `TransactionGroupId` | `_id: {$gt}` | keyset |

Sort `updatedAt:1, _id:1`. `Limit` mặc định 200, trần 500.

**Index cần có phía transaction**: `{status: 1, updatedAt: 1, _id: 1}` và
`{orderTime: 1, status: 1}`. Kiểm tra trước khi bật job — thiếu thì mỗi trang là một
collection scan trên bảng lớn nhất hệ thống.

### 2.2 gRPC — `tracking.ListClicks`

`GetTracking` cũ **giữ nguyên xi** (đọc Redis + `DelKey`, gamification đang dùng).

```proto
service Tracking {
  rpc GetTracking (GetTrackingReq) returns (GetTrackingRes);   // giữ nguyên
  rpc ListClicks  (ListClicksReq)  returns (ListClicksRes);    // MỚI
}

message ListClicksReq {
  string partner        = 1;
  int64  from_at        = 2;  // unix giây, = event.StartAt
  int64  to_at          = 3;  // unix giây, = event.EndAt
  string last_id        = 4;  // cursor, ObjectId hex, rỗng = từ đầu
  int64  limit          = 5;  // default 500, max 1000
  repeated string types = 6;  // optional
}

message ListClicksRes {
  repeated ClickItem data = 1;
}

message ClickItem {
  string id              = 1;  // _id hex — vừa là cursor vừa là refId
  string user_id         = 2;
  string type            = 3;
  string target_id       = 4;
  bool   is_first_in_day = 5;
  int64  created_at      = 6;
}
```

Sinh lại stub ở **cả hai** repo (`tracking/external/...` và `event/external/...`).

**Phía tracking** — `internal/dao/click.go` hiện chỉ có `InsertOne` + `CountByCondition`:

```go
type ClickInterface interface {
	InsertOne(ctx context.Context, raw interface{}) error
	CountByCondition(ctx context.Context, cond interface{}) int64
	FindByCondition(ctx context.Context, cond interface{},
		opts ...*options.FindOptions) ([]model.ClickRaw, error) // MỚI
}
```

Handler dựng cond:

```go
cond := bson.M{"createdAt": bson.M{"$gte": from, "$lte": to}}
if lastID != "" { cond["_id"] = bson.M{"$gt": oid} }
if len(types) > 0 { cond["type"] = bson.M{"$in": types} }
// sort _id:1, limit
```

**Index bắt buộc**: `{createdAt: 1, _id: 1}` trên collection `click`.

### 2.3 Client gRPC tracking phía event

`event/internal/grpc/tracking/client.go` — copy khuôn `internal/grpc/transaction/client.go`
(dial + `apmgrpc.NewUnaryClientInterceptor`), đổi địa chỉ sang `env.GRPCAddresses.Tracking`.

`event/internal/grpc/tracking/request.go`:

```go
func ListClicks(req ListClicksReq) ([]ClickItem, error)
```

---

## 3. Cấu hình

`event/internal/config/env_keys.go`:

```go
GRPCAddresses struct {
	Self        string `env:"EVENT,required"`
	User        string `env:"USER,required"`
	Brand       string `env:"BRAND,required"`
	Withdraw    string `env:"WITHDRAW,required"`
	System      string `env:"SYSTEM,required"`
	Transaction string `env:"TRANSACTION,required"`
	Tracking    string `env:"TRACKING"`   // MỚI — KHÔNG required
} `env:",prefix=GRPC_ADDRESS_"`

// PortalRewardJob — job đẩy sự kiện mini_game_v2 sang partner.
PortalRewardJob struct {
	Enable       bool `env:"ENABLE,default=true"`
	MaxAttempts  int  `env:"MAX_ATTEMPTS,default=5"`
	PageSize     int  `env:"PAGE_SIZE,default=200"`
	Concurrency  int  `env:"CONCURRENCY,default=20"`
} `env:",prefix=PORTAL_REWARD_JOB_"`
```

`Tracking` **không** đặt `required`: các bank chưa deploy service tracking vẫn phải khởi
động được service event. Địa chỉ rỗng ⇒ nhánh click tự bỏ qua và ghi log, không panic.

---

## 4. Model & schema

### 4.1 `internal/module/mongodb/col.go`

```go
ColSystemEvent = "system-events"
```

### 4.2 `internal/model/system_event.go`

```go
package model

type SystemEventBSON struct {
	ID primitive.ObjectID `json:"id" bson:"_id,omitempty"`

	// --- định danh sự việc ---
	// Code là eventId gửi sang partner: định danh của SỰ VIỆC, không phải
	// của lượt gửi. Sinh lại bao nhiêu lần cũng ra cùng một giá trị.
	Code     string `json:"code"     bson:"code"`
	Type     string `json:"type"     bson:"type"`
	Provider string `json:"provider" bson:"provider"`

	// --- nguồn gốc ---
	Event   primitive.ObjectID `json:"event"   bson:"event"`
	User    primitive.ObjectID `json:"user"    bson:"user"`
	Source  string             `json:"source"  bson:"source"`  // sourceId = externalUserId
	RefId   string             `json:"refId"   bson:"refId"`   // orderId | click._id
	Channel string             `json:"channel" bson:"channel"` // order | click

	// --- nội dung đã gửi ---
	Payload    map[string]interface{} `json:"payload"    bson:"payload"`
	OccurredAt time.Time              `json:"occurredAt" bson:"occurredAt"`
	// Date = utime.StartOfDayHCM(OccurredAt) — cho job quét theo ngày bên partner.
	Date time.Time `json:"date" bson:"date"`

	// --- kết quả gửi ---
	Status       string `json:"status"       bson:"status"`
	Attempts     int    `json:"attempts"     bson:"attempts"`
	DeliveryId   string `json:"deliveryId"   bson:"deliveryId,omitempty"`
	Deduplicated bool   `json:"deduplicated" bson:"deduplicated"`
	HttpStatus   int    `json:"httpStatus"   bson:"httpStatus,omitempty"`
	ErrCode      string `json:"errCode"      bson:"errCode,omitempty"`
	ErrDetail    string `json:"errDetail"    bson:"errDetail,omitempty"`

	CreatedAt time.Time  `json:"createdAt" bson:"createdAt"`
	UpdatedAt time.Time  `json:"updatedAt" bson:"updatedAt"`
	SentAt    *time.Time `json:"sentAt"    bson:"sentAt,omitempty"`
}
```

### 4.3 `internal/model/portal_reward.go`

```go
package model

// RawEvent là một sự việc đã chuẩn hoá, chưa biết sẽ gửi thành công hay không.
// Đây là ngôn ngữ chung giữa collector và dispatcher: dispatcher KHÔNG biết
// sự việc đến từ đơn hàng hay từ click.
type RawEvent struct {
	Event      primitive.ObjectID
	Type       string
	Channel    string
	RefID      string
	User       primitive.ObjectID
	Source     string
	Payload    map[string]interface{}
	OccurredAt time.Time
}

const (
	SystemEventStatusPending = "pending"
	SystemEventStatusSuccess = "success"
	SystemEventStatusFailed  = "failed"
	SystemEventStatusDropped = "dropped"

	SystemEventChannelOrder = "order"
	SystemEventChannelClick = "click"

	SystemEventProviderPortalReward = "portal_reward"
)
```

### 4.4 `internal/dao/system_event.go`

```go
package dao

type systemEventDAO struct {
	*shared.DAO[model.SystemEventBSON]
}

var SystemEvent = systemEventDAO{
	shared.NewDAO[model.SystemEventBSON](mongodb.ColSystemEvent),
}
```

`shared.DAO[T]` đã có `Find`, `BulkWrite`, `UpdateOne`, `Distinct` — không viết thêm method.

### 4.5 `internal/module/mongodb/index.go` — thêm vào `Index()`

```go
// system events (portal reward outbox)
{
	uniqueIndexCol(ColSystemEvent, [][]string{
		{"code"},
	})
	indexCol(ColSystemEvent, [][]string{
		{"status"},
		{"date"},
		{"date", "type"},
		{"event", "type"},
		{"channel", "refId"},
	})
}
```

`uniqueIndexCol` đã tồn tại nhưng chưa chỗ nào dùng — đây là chỗ dùng đầu tiên.

### 4.6 `internal/module/redisdb/key.go`

```go
const KeyPortalRewardCursor = "%s_portal_reward_cursor_%s_%s" // partnerId, eventId, channel

func GetKeyPortalRewardCursor(partnerId, eventId, channel string) string {
	return fmt.Sprintf(KeyPortalRewardCursor, partnerId, eventId, channel)
}
```

TTL: `event.EndAt + 7 ngày`. Event kết thúc thì khoá tự dọn.

---

## 5. Module

### 5.1 `internal/service/portalreward/codec.go` — thuần hàm, không I/O

```go
// Code sinh eventId ổn định. Không có partnerCode vì mỗi partner một database.
func Code(eventID primitive.ObjectID, evType, refID string) string {
	h := sha256.Sum256([]byte(eventID.Hex() + "|" + evType + "|" + refID))
	return hex.EncodeToString(h[:])[:32]
}

// StatusesFor suy danh sách trạng thái transaction cần truy vấn từ eventCodes.
//   ORDER_CREATED   -> pending, approved
//   ORDER_COMPLETED -> cashback
//   ORDER_CANCELLED -> rejected
func StatusesFor(eventCodes []string) []string

// TypeForStatus ánh xạ ngược: trạng thái đơn -> mã sự kiện partner.
func TypeForStatus(status string) (string, bool)

// ValidateCodes kiểm eventCodes thuộc danh mục đóng và đúng nhánh.
func ValidateOrderCodes(codes []string) error  // chỉ ORDER_*
func ValidateClickCodes(codes []string) error  // chỉ UI_ACTION
```

Bảng ánh xạ nguồn: `external/config/constant.go` (`TransactionStatus*`) và
`external/partnerapi/portalreward/const.go` (`Type*`). **Không** khai lại chuỗi literal.

### 5.2 `internal/service/portalreward/dispatcher.go` — deep module

```go
type Dispatcher struct {
	client      *pr.Client
	maxAttempts int
	concurrency int
}

// Dispatch gửi một lô sự việc và ghi dấu vết. Idempotent: gọi lại với cùng
// đầu vào không tạo thêm lượt gửi nào tới partner.
func (d Dispatcher) Dispatch(ctx context.Context, events []model.RawEvent) (Result, error)

// Retry gửi lại các bản ghi pending/failed chưa vượt ngưỡng.
func (d Dispatcher) Retry(ctx context.Context) (Result, error)

type Result struct {
	Total, Skipped, Success, Failed, Dropped int
}
```

Luồng `Dispatch`:

```
1. code := Code(...) cho từng RawEvent
2. dao.SystemEvent.Find({code: {$in: codes}, status: "success"})  ← 1 query
3. loại những cái đã success
4. upsert bản ghi pending cho phần còn lại        ← BulkWrite
5. ants.NewPoolWithFunc(concurrency) → client.SendEvent
6. phân loại kết quả → BulkWrite cập nhật trạng thái
```

Phân loại kết quả (bước 6) — **luật duy nhất**, không lặp lại ở đâu khác:

```go
switch {
case err == nil:
	status = success; deliveryId = res.DeliveryID; dedup = res.Deduplicated
case errors.As(err, &apiErr) && apiErr.IsRetryable():
	status = failed;  attempts++; deliveryId = apiErr.DeliveryID()
case errors.As(err, &apiErr):
	status = dropped; deliveryId = apiErr.DeliveryID()   // 400/409/422
default:
	status = failed;  attempts++                          // lỗi mạng
}
if attempts >= maxAttempts && status == failed { status = dropped }
```

`deliveryId` ghi ở **mọi** nhánh kể cả 422 — yêu cầu của tài liệu tích hợp.

Backoff trong `Retry`: chỉ lấy bản ghi có `updatedAt < now - 10min * 2^attempts`.

### 5.3 `app/service/portal_reward_collector_order.go`

```go
func (s portalRewardService) collectOrder(ctx context.Context,
	ev model.EventBSON, resolver *sourceResolver) ([]model.RawEvent, error)
```

```
1. statuses := codec.StatusesFor(ev.CondMiniGame.EventCodes)
2. cursor := redis.Get(GetKeyPortalRewardCursor(partner, ev.ID.Hex(), "order"))
3. for {
     req := TransactionGroupGetListReq{
       OrderTimeStartAt: ev.StartAt, OrderTimeEndAt: ev.EndAt,
       FromAt: cursor,
       BrandIds: nil nếu ApplyForBrand.IsAll ngược lại BrandIDs,
       ShopIds:  nil nếu ApplyForShopID.IsAll ngược lại ShopIDs,
       OrderType: ev.CondMiniGame.OrderType,
       MinOrderValue: ev.CondMiniGame.MinOrderValue,
       Statuses: statuses,
       Limit: pageSize,
     }
     res := natsio.Transaction.GetTransactionGroup(req)
     if len(res) == 0 { break }
     resolver.Resolve(userIds của trang)        ← 1 lượt gRPC / trang
     dựng RawEvent (bỏ user không có sourceId)
     cursor = res[last].UpdatedAt
   }
4. redis.Set(cursor)   ← CHỈ khi cả trang xử lý xong không lỗi
```

`OrderPayload`: `orderId`, `amountMinor` (`TransactionValue` × 100, làm tròn),
`currency` = `"VND"`. **Có `amountMinor` thì bắt buộc có `currency`** — partner không
mặc định VND.

### 5.4 `app/service/portal_reward_collector_click.go`

Cùng khuôn, nguồn là `tracking.ListClicks`, cursor là `_id`, payload là
`UIActionPayload{ActionKey: click.Type}`, `refID` là `click.ID`.

### 5.5 `app/service/portal_reward_trigger.go`

```go
func (s portalRewardService) Run(ctx context.Context)
```

```
0. if !cfg.Enable { return }
1. dispatcher.Retry(ctx)                    ← xử lý tồn đọng trước
2. events := dao.Event.Find({
     type: "mini_game_v2", status: "active",
     startAt: {$lte: now}, endAt: {$gte: now},
     partnerCode: env.PartnerID,
   })
3. tách orderEvents / clickEvents; rỗng cả hai → return
4. errgroup 2 nhánh song song:
     nhánh order: for each event → collectOrder → dispatcher.Dispatch
     nhánh click: for each event → collectClick → dispatcher.Dispatch
   Một nhánh lỗi KHÔNG huỷ nhánh kia (dùng WaitGroup + gom lỗi, không
   dùng errgroup.WithContext vì nó cancel chéo).
5. log tổng hợp Result
```

Guard chạy chồng: biến `isRunning atomic.Bool` như các job hiện hữu.

### 5.6 `sourceResolver` — phân giải `userId` → `sourceId`

```go
type sourceResolver struct {
	cache map[string]string // userId -> sourceId
}

// Resolve nạp các userId chưa có trong cache. Trả lỗi khi gọi gRPC thất bại —
// KHÔNG nuốt lỗi như grpcuser.GetUserInfo đang làm.
func (r *sourceResolver) Resolve(userIDs []string) error

// Get trả sourceId; ok=false khi user không tồn tại hoặc chưa có sourceId.
func (r *sourceResolver) Get(userID string) (string, bool)
```

`grpcuser.GetUserInfo([]string) []model.UserInfo` đã có sẵn và trả về `SourceID` —
không đổi proto. Nhưng nó **trả slice rỗng khi gRPC lỗi**, không phân biệt được với
"không có user nào". `Resolve` phải xử lý: gọi với N userId mà nhận về 0 kết quả thì
coi là lỗi, không coi là "không user nào tồn tại".

Cache sống trong một lượt `Run`, dùng chung cả hai nhánh.

### 5.7 `app/schedule/schedule.go`

```go
// đẩy sự kiện mini_game_v2 sang Portal Reward, 2 tiếng một lần
c.AddFunc("10 */2 * * *", func() {
	service.PortalReward.Run(context.Background())
})
```

Phút 10 để tránh đụng `45 */2` và `25 */2` đang có.

---

## 6. Thay đổi CRM

`admin/model/event.go`:

```go
CondTracking *EventCondTracking `json:"condTracking,omitempty"` // MỚI
```

Trong cả hai chỗ đang gọi `sanitizeEventCodes` (dòng ~145 và ~228), thêm nhánh
`CondMiniGame` và `CondTracking`, rồi validate:

```go
if p.CondMiniGame != nil {
	p.CondMiniGame.EventCodes = sanitizeEventCodes(p.CondMiniGame.EventCodes)
	if err := codec.ValidateOrderCodes(p.CondMiniGame.EventCodes); err != nil { return err }
}
if p.CondTracking != nil {
	p.CondTracking.EventCodes = sanitizeEventCodes(p.CondTracking.EventCodes)
	if err := codec.ValidateClickCodes(p.CondTracking.EventCodes); err != nil { return err }
}
```

`admin/service/event.go` — map `CondTracking` vào response detail (cạnh chỗ đang map
`Options.EventCodes`, dòng ~543).

---

## 7. Migration & triển khai

### Thứ tự bắt buộc

```
① transaction: mở rộng req/res + index      ─┐
② tracking:   RPC ListClicks + dao + index  ─┤ độc lập, chạy song song được
③ CRM:        CondTracking + validate       ─┘
                     ↓
④ event: model + dao + index + client tracking
                     ↓
⑤ event: dispatcher + collectors + trigger (cron TẮT)
                     ↓
⑥ bật PORTAL_REWARD_JOB_ENABLE trên 1 partner
```

① và ② phải **deploy xong và chạy ổn** trước ⑤. Cả hai đều tương thích ngược nên
không cần deploy đồng thời với event.

### Index

Ba index mới, tạo **trước** khi bật job:

| Collection | Index | Service |
|---|---|---|
| `system-events` | `{code}` **unique** | event |
| `click` | `{createdAt, _id}` | tracking |
| transaction group | `{status, updatedAt, _id}` | transaction |

`system-events` là bảng mới nên tạo index tức thì. `click` và transaction group là
bảng có sẵn dữ liệu — tạo bằng `background: true`, và với transaction group nên làm
ngoài giờ cao điểm.

### Bật dần

1. Deploy với `PORTAL_REWARD_JOB_ENABLE=false`.
2. Bật trên môi trường dev, dựng một event `mini_game_v2` có kỳ hạn ngắn.
3. Kiểm bảng `system-events`: đủ bản ghi, `status=success`, có `deliveryId`.
4. Chạy job lần hai, xác nhận `Skipped` = số bản ghi lượt một, `Total` mới = 0.
5. Bật production trên **một** partner trước, theo dõi một chu kỳ (2 tiếng).
6. Mở rộng các partner còn lại.

### Rollback

`PORTAL_REWARD_JOB_ENABLE=false` — job dừng, không cần deploy lại. Dữ liệu đã gửi sang
partner không thu hồi được, nhưng `system-events` giữ nguyên nên bật lại không gửi trùng.

---

## 8. Rủi ro & cách chặn

| Rủi ro | Hậu quả | Cách chặn |
|---|---|---|
| `sourceId` lệch giữa kênh EVENT và LAUNCH | Partner trả 200, user không được cộng lượt, **không lỗi nào được báo** | Dùng chung đúng `user.SourceID`; test riêng cho `sourceResolver`; đối chiếu thủ công vài bản ghi ở bước bật dần |
| `GetUserInfo` nuốt lỗi gRPC | Cả trang bị bỏ qua, cursor vẫn nhích ⇒ **mất vĩnh viễn** | `Resolve` trả lỗi; cursor chỉ ghi khi trang xử lý xong sạch |
| Thiếu index transaction group | Job 2h kéo tải lên bảng lớn nhất hệ thống | Tạo index trước, kiểm bằng `explain` |
| Hai instance chạy chồng | Gửi trùng | Unique index `{code}` + guard `isRunning` |
| Partner đổi danh mục mã sự kiện | Gói tin bị từ chối hàng loạt | `ValidateCodes` chặn từ CRM; `dropped` không retry nên không đốt hạn mức |
| `amountMinor` thiếu `currency` | 422 hàng loạt | Client đã chặn hai lớp; collector luôn điền `"VND"` |
| Event kỳ hạn dài, Redis mất cursor | Quét lại từ `StartAt`, chậm | Chấp nhận — unique index chặn gửi trùng; **chậm chứ không sai** |

---

## 9. Định nghĩa hoàn thành

- [ ] Hợp đồng NATS transaction mở rộng, deploy, gamification chạy nguyên trạng
- [ ] RPC `ListClicks` deploy, `GetTracking` cũ không đổi hành vi
- [ ] Ba index đã tạo và kiểm bằng `explain`
- [ ] `CondTracking` nhập được từ CRM, `eventCodes` sai bị từ chối
- [ ] Chạy job hai lần liên tiếp: lượt hai `Total` mới = 0, không có lượt gọi partner nào
- [ ] Bảng `system-events` có `deliveryId` ở cả bản ghi `success` lẫn bản ghi 422
- [ ] Tắt job bằng env, không cần deploy
- [ ] Test cho `Dispatcher`, `codec`, `sourceResolver`, tính `date` — theo mục Testing của PRD
