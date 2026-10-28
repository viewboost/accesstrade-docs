# Tài liệu thiết kế kỹ thuật — Cập nhật giao diện Trang cá nhân Ambassador

| | |
|---|---|
| **Mã tài liệu** | SDD-AMB-PROFILE-PAGE-001 |
| **Phiên bản** | 1.1 |
| **Ngày ban hành** | 2026-10-23 |
| **Trạng thái** | Đã triển khai trên nhánh tính năng, chờ nghiệm thu |
| **PRD** | [PRD-AMB-PROFILE-PAGE-001](./PRD.md) |
| **Kho mã nguồn** | `AT-Core/ambassador` |
| **Nhánh triển khai** | `feat/profile-page-ui-from-frontend` |
| **Nhánh nền** | `release` |
| **Phạm vi mã nguồn** | `fecredit/`, `creator-app/` |
| **Đối tượng đọc** | Frontend Dev, QA, Tech Lead, người bảo trì |

---

## 1. Mục đích và phạm vi

### 1.1 Mục đích

Tài liệu mô tả thiết kế kỹ thuật để thay bố cục hai tab cũ của `/trang-ca-nhan`
bằng bố cục sidebar chiến dịch + thu nhập + thống kê theo nguồn + danh sách bài đăng.
Thiết kế sử dụng dữ liệu và effect hiện có, không thay backend hoặc hợp đồng API.

Tài liệu này là phần **how** của PRD. Yêu cầu nghiệp vụ, wording và điều kiện nghiệm
thu nằm ở [PRD.md](./PRD.md); nếu hai tài liệu mâu thuẫn thì PRD quyết định **what**,
Tech Spec quyết định **how**.

### 1.2 Trong phạm vi

- Điều phối dữ liệu của route `/trang-ca-nhan`.
- Cây component và ranh giới trách nhiệm.
- Gom chiến dịch theo ADV và quản lý trạng thái mở sidebar.
- Chuẩn hóa dữ liệu tiền và dữ liệu theo nguồn.
- Luồng Đăng bài/Gửi bạn bè và thứ tự các cổng nghiệp vụ.
- Responsive của sidebar, bảng thống kê và banner liên kết tài khoản.
- Đồng bộ cùng hành vi giữa `fecredit/` và `creator-app/`.
- Unit test, kiểm thử tích hợp, rollout và rollback.

### 1.3 Ngoài phạm vi

- Model, handler, service hoặc database backend.
- Thêm endpoint, field response, migration hoặc backfill.
- Thay đổi phép tính thống kê/đối soát ở server.
- Thiết kế lại component dùng ngoài trang cá nhân.
- Áp dụng cho các white-label khác.

## 2. Nguyên tắc và ràng buộc thiết kế

| Mã | Ràng buộc |
|---|---|
| C1 | API là nguồn sự thật của số liệu; frontend chỉ ánh xạ và trình bày. |
| C2 | Tổng tiền tạm tính phải cộng `waiting + pending + completed`; không tin field tổng có sẵn. |
| C3 | Bảng nguồn chỉ sinh dòng từ `applyForSources`; không suy nguồn từ object thống kê. |
| C4 | Không được bỏ chiến dịch chỉ vì `/partners` chưa tải xong hoặc thiếu ADV tương ứng. |
| C5 | Cổng nộp bài chạy đúng thứ tự: hồ sơ → nhân viên → mã tham gia → biểu mẫu. |
| C6 | `fecredit/` và `creator-app/` phải giữ cùng thuật toán và cùng test cho logic dùng chung. |
| C7 | Cuộn ngang chỉ nằm trong bảng; không được làm tràn toàn bộ trang. |
| C8 | Wording y hệt `frontend/`, gồm “Lần cập nhật kế tiếp” = `lastUpdatedAt` + 2 giờ. |
| C9 | Việc port từ `frontend/` phải giữ branding và hành vi riêng của FE Credit. |

### 2.1 Bảng nguồn — đích

| Thành phần | Nguồn tham chiếu | Đích | Quyết định |
|---|---|---|---|
| Bố cục sidebar + nội dung | `frontend/src/pages/home/components/` | `fecredit/`, `creator-app/` | Port cấu trúc, không port nguyên hành vi |
| Màu sidebar | Theme Ambassador | Theme FE Credit | Dùng `#00994f`, `#e8f6f0`, gradient FE Credit |
| Nút hành động | FE Credit trước thay đổi | `PostActions` mới | Giữ cổng hồ sơ, nhân viên, mã và hết hạn |
| Thống kê nguồn | Bảng của `frontend/` | `source-rows.ts` | Bổ sung nguồn bị thiếu; nhãn giữ như `frontend/` |
| Tổng tiền | `userEventStatistic.cashTotal` | `cash-summary.ts` | Cộng đủ ba trạng thái, gồm `waiting` |
| Banner liên kết | Header hiện có | `alert-link-account.tsx` | Thêm spacer đo động, không hardcode chiều cao |

## 3. Kiến trúc hiện trạng đã xác minh

### 3.1 Route và tầng trạng thái

Route `/trang-ca-nhan` render `pages/profile/index.tsx`. Component đọc hai model Umi:

| Model | Dữ liệu dùng |
|---|---|
| `mainState` | `user`, `partners`, `openPostContentModal`, các cờ modal hệ thống |
| `homeState` | `eventList`, `eventHome`, `eventSchema`, `listByMe`, `listByMeFilter` |
| `loading` | Trạng thái effect `getEventBySlug`, `getListByMe`, `createContent` |

Query `?event=<code>` là nguồn sự thật cho chiến dịch đang chọn. Nếu URL chưa có
`event` nhưng `eventList` đã tải, route ghi code của chiến dịch đầu tiên vào query.
Mỗi lần query đổi, route tải chi tiết chiến dịch; callback sau đó tải mốc thưởng và
danh sách bài của chính chiến dịch đó.

### 3.2 Luồng dữ liệu

```text
/trang-ca-nhan
  └─ Profile
      ├─ getList() ───────────────────────────────> eventList
      ├─ query.event ─> getEventBySlug(slug) ─────> eventHome
      │                                  ├────────> getEventSchema(eventId)
      │                                  └────────> getListByMe(eventId)
      └─ LoggedInView
          ├─ PartnerSidebar <── eventList + partners + query.event
          ├─ StatisticUser  <── eventHome.userEventStatistic
          ├─ EventSchema    <── eventSchema
          ├─ PostActions    <── eventHome + user + modal state
          └─ MyPost         <── listByMe + listByMeFilter
```

Không thêm request mới. Thay đổi query tiếp tục là cơ chế chọn chiến dịch để giữ URL
có thể reload, bookmark và dùng nút Back/Forward của trình duyệt.

### 3.3 Hình dạng dữ liệu tối thiểu

Tech Spec chỉ phụ thuộc vào tập field sau; các field khác của interface hiện hữu không
được coi là điều kiện của tính năng.

```ts
interface ProfileEvent {
  _id: string;
  code?: string;
  slug?: string;
  name?: string;
  endAt?: string;
  partner?: { _id?: string; name?: string };
  options?: { applyForSources?: string[] };
  userEventStatistic?: {
    cashTotal?: Record<string, unknown>;
    cashReward?: { pending?: number; completed?: number };
    [sourceStatisticKey: string]: unknown;
  };
  lastUpdatedAt?: string;
  isMustInputProfile?: boolean;
  isRequireCode?: boolean;
}
```

Các helper thuần nhận input lỏng hơn interface UI để chịu được response cũ, field
thiếu và trạng thái model chưa tải xong.

## 4. Thiết kế chi tiết

### 4.1 Điều phối route — PP-001, PP-002, PP-008

File: `src/pages/profile/index.tsx`.

Trách nhiệm của route:

1. Tải danh sách chiến dịch đúng một lần khi mount.
2. Chuẩn hóa URL bằng chiến dịch đầu tiên khi thiếu `query.event`.
3. Khi `query.event` đổi, tải `eventHome` theo slug.
4. Chỉ sau khi có id từ callback mới tải `eventSchema` và `listByMe`.
5. Sau khi tạo bài thành công, tải lại `listByMe` của event hiện tại.
6. Truyền `partners` vào view thay cho `partnerDetail`, vì sidebar cần danh sách đầy đủ.

Route không được giữ một state `selectedEvent` thứ hai. Nếu vừa giữ state local vừa giữ
query, reload hoặc Back/Forward có thể làm sidebar và nội dung chọn hai event khác nhau.

### 4.2 Cây component — PP-001

File: `src/pages/home/components/logged-in-view/index.tsx`.

```text
LoggedInView
├─ AppBreadcrumb
├─ PartnerSidebar
└─ content panel
   ├─ heading + lastUpdatedAt (gần nhất / kế tiếp)
   ├─ PostActions
   ├─ StatisticUser
   │  ├─ cash summary card
   │  └─ TableStatisticView
   └─ EventSchema (có điều kiện)
└─ MyPost
```

`LoggedInView` chỉ composition và wording. Phép tính phải ở helper thuần; nghiệp vụ
nộp bài phải ở `PostActions`; thuật toán gom nhóm phải ở module sidebar.

Cột nội dung đặt `minWidth: 0`. Trong flexbox, thiếu thuộc tính này làm intrinsic width
của bảng đẩy cột vượt khỏi container dù bảng đã cấu hình scroll.

### 4.3 Gom chiến dịch theo ADV — PP-002

Files:

- `partner-sidebar/group-events-by-partner.ts`
- `partner-sidebar/index.tsx`
- `partner-sidebar/index.scss`

#### 4.3.1 Thuật toán

```text
groups = partners.map(partner => group rỗng)     // giữ thứ tự API
byId   = Map(groups._id -> group)

for event of events:                             // giữ thứ tự event API
  partnerId = event.partner._id || ''
  group = byId[partnerId]
  if group chưa tồn tại:
    tạo group từ event.partner
    fallback id = 'khac', name = 'Chiến dịch'
  group.events.push(event)
```

Độ phức tạp `O(P + E)`, với `P` là số ADV và `E` là số chiến dịch. Không dùng vòng lặp
lồng `partners × events`, và không filter làm mất event chưa khớp danh sách ADV.

#### 4.3.2 Trạng thái hiển thị

- Một group: render thẳng event, không render hàng ADV và không thụt lề 44px.
- Nhiều group: render hàng ADV có logo/tên/nút thu gọn.
- `expanded` là `Set<string>` local trong sidebar.
- Effect chỉ **thêm** group duy nhất hoặc group đang active vào `expanded`; không thay
  toàn bộ Set để tránh đóng group người dùng vừa tự mở.
- Event active khi `currentEventCode` khớp `event.code` hoặc `event._id`.
- Nút ADV dùng `aria-expanded`; event active dùng `aria-current="true"`.

### 4.4 Chuẩn hóa tiền — PP-003

File: `statistic/cash-summary.ts`.

```ts
waiting   = Number(cashTotal?.waiting)   || 0;
pending   = Number(cashTotal?.pending)   || 0;
completed = Number(cashTotal?.completed) || 0;
total     = waiting + pending + completed;
```

Không đọc `cashTotal.total`: field này có thể không tồn tại hoặc không cùng định nghĩa
với “tạm tính” của màn hình. `Number(...) || 0` bảo vệ `undefined`, `null`, chuỗi rỗng
và `NaN`; số âm nếu backend trả về vẫn được giữ để không âm thầm che sai lệch dữ liệu.

UI luôn render `completed` và `pending`. `waiting` chỉ render khi lớn hơn 0. Tất cả số
tiền đi qua `formatter.currency`.

### 4.5 Chuẩn hóa thống kê nguồn — PP-004

Files:

- `statistic/source-rows.ts`
- `statistic/table.tsx`
- `statistic/style.scss`

#### 4.5.1 Ánh xạ source → statistic key

| `applyForSources` | Field trong `userEventStatistic` | Nhãn |
|---|---|---|
| `tiktok` | `tiktok` | Tiktok |
| `youtube` | `youtube` | Youtube |
| `youtube_shorts` | `youtubeShort` | Youtube Shorts |
| `facebook` | `facebook` | Facebook |
| `facebook_reels` | `facebookReels` | Facebook Reels |
| `facebook_post` | `facebookPost` | Facebook Post |
| `instagram` | `instagram` | Instagram |
| `instagram_reels` | `instagramReels` | Instagram Reels |
| `threads` | `threads` | Threads |
| `shopee` | `shopeeVideo` | Shopee |

Nhãn của mọi source (kể cả source chưa khai báo) là `snake_case` viết hoa chữ đầu từng
từ, giống `frontend/`. Source chưa khai báo dùng chính source làm statistic key; đây là
forward-compatible fallback, không cam kết backend đã có số.

#### 4.5.2 Field hiển thị

```text
view                  = stat.view.completed              ?? 0
viewRewardedSettled   = stat.viewRewarded.cashback       ?? 0
viewRewardedPending   = stat.viewRewarded.completed      ?? 0
```

Không lấy `view - viewRewarded`. Hai nhóm số đến từ pipeline khác nhau và phép trừ ở
client có thể tạo số sai hoặc âm.

#### 4.5.3 Table

- Ant Design `Table`, không phân trang.
- `rowKey="name"`; nguồn trong một event phải là duy nhất.
- Mỗi sorter đọc đúng field của chính cột đó.
- `scroll={{ x: 'max-content' }}` giữ tiêu đề một dòng và cuộn trong table.
- Header `white-space: nowrap`, cỡ 13px, padding ngang 12px.
- `showSorterTooltip={false}` để tooltip giải thích nghiệp vụ không xung đột tooltip sorter.

### 4.6 Mốc thưởng — PP-005

`EventSchema` chỉ render khi mảng có phần tử. Dòng “Thưởng:” dùng:

```text
cashReward.completed + cashReward.pending
```

Không cộng `waiting`, vì một mốc chưa duyệt chưa phải mốc đã đạt. Khối dùng biến thể
`plain`; không thay đổi logic dựng mốc của component dùng chung.

### 4.7 Luồng hành động — PP-006, PP-007

File: `logged-in-view/components/post-actions/index.tsx`.

#### 4.7.1 State và modal

| State | Nguồn | Vai trò |
|---|---|---|
| `openPostContentModal` | `mainState` | Hiện form nộp bài |
| `visibleModalEventCode` | `mainState` | Hiện form mã tham gia |
| `visibleModalStaffCode` | `mainState` | Modal hệ thống, chặn modal mã |
| `visibleModalLogin` | `mainState` | Modal hệ thống, chặn modal mã |
| `visibleModalCompleteReg` | `mainState` | Modal hệ thống, chặn modal mã |

`ModalEventCode` phải mount ngay trong `PostActions`. Trước thay đổi, modal chỉ mount ở
trang chi tiết chiến dịch, nên set `visibleModalEventCode` từ trang cá nhân không tạo UI.

#### 4.7.2 Thứ tự cổng

```text
click Đăng bài
  ├─ event hết hạn ───────────────> button disabled
  ├─ isMustInputProfile ──────────> confirm → /tai-khoan?returnEvent=<slug>
  ├─ isBlockedByStaffGate(event) ─> visibleModalNotEmployee = true
  ├─ isRequireCode ───────────────> visibleModalEventCode = true
  └─ đủ điều kiện ────────────────> openPostContentModal = true
```

Cổng nhân viên đứng trước mã tham gia để không hỏi mã của người vốn chưa đủ điều kiện.
Một modal mã chỉ hiện khi có user và không modal hệ thống nào đang mở.

Sau khi nhập mã thành công:

1. đóng modal mã;
2. đặt `openPostContentModal = true`;
3. tải lại `eventHome` theo slug để server tính lại `isRequireCode`.

Nút Gửi bạn bè dùng `getEventShareUrl(eventHome.slug, partnerDetail.slug)`. Không dùng
`window.location`, vì URL hiện tại là trang riêng tư `/trang-ca-nhan`.

### 4.8 Danh sách bài đăng — PP-008

`MyPost` tiếp tục nhận `listByMe`, `listByMeFilter`, `getListByMe` và loading effect cũ.
Thay đổi chỉ là vị trí trong layout và spacing. Không đổi filter, pagination, quyền sửa/
xóa hoặc request. Token `fs-3c` không tồn tại được thay bằng token font hợp lệ `fs-6`.

### 4.9 Điều hướng và banner — PP-009

#### 4.9.1 Wording

Menu account đổi nhãn từ “Thử thách của tôi” thành “Trang cá nhân”; path giữ nguyên
`/trang-ca-nhan`.

#### 4.9.2 Spacer động cho banner fixed

`AlertLinkAccount` giữ `ref` tới banner và dùng `ResizeObserver` để cập nhật
`chieuCao = element.offsetHeight`. Trước banner fixed render một spacer:

```tsx
<div aria-hidden style={{ height: chieuCao, flexShrink: 0, width: '100%' }} />
```

Banner đổi chiều cao khi text wrap hoặc viewport đổi thì observer cập nhật spacer.
Khi animation đóng hoàn tất và `visible=false`, component trả `null`, gỡ cả banner lẫn
spacer. Observer được disconnect trong cleanup.

Không hardcode chiều cao vì banner có thể cao 78–150px tùy viewport, font và wrapping.

### 4.10 Đồng bộ `fecredit/` và `creator-app/`

Hai ứng dụng chưa dùng package component chung. Trong phạm vi task, các file logic thuần
được giữ giống byte-for-byte:

- `statistic/cash-summary.ts`
- `statistic/source-rows.ts`
- `partner-sidebar/group-events-by-partner.ts`

UI được phép khác import asset hoặc hạ tầng build, nhưng hành vi PP-001–PP-009 không
được khác. Mỗi thay đổi sau này phải sửa và chạy test ở cả hai thư mục trong cùng PR.

## 5. Ánh xạ yêu cầu — thành phần

| PRD | Component/module | Test/bằng chứng |
|---|---|---|
| PP-001 | `profile/index.tsx`, `logged-in-view/index.tsx` | Visual desktop/mobile |
| PP-002 | `partner-sidebar/*` | `group-events-by-partner.test.ts` |
| PP-003 | `statistic/cash-summary.ts`, `statistic/index.tsx` | `cash-summary.test.ts` |
| PP-004 | `statistic/source-rows.ts`, `table.tsx`, `style.scss` | `source-rows.test.ts` + visual table |
| PP-005 | `logged-in-view/index.tsx`, `EventSchema` | Payload có/không có schema |
| PP-006 | `post-actions/index.tsx` | Integration/manual matrix |
| PP-007 | `post-actions/index.tsx`, `event-share-url.ts` | URL theo slug event/ADV |
| PP-008 | `my-post/index.tsx`, `profile/index.tsx` | Pagination/filter regression |
| PP-009 | header `profile.tsx`, `alert-link-account.tsx` | Resize/close banner |

Mọi đường dẫn trong bảng tính từ `fecredit/src/` và có bản tương ứng dưới
`creator-app/src/`.

## 6. Kế hoạch và trạng thái triển khai

### 6.1 Thứ tự phụ thuộc

1. Tách helper thuần cho tiền, nguồn và grouping; viết unit test.
2. Dựng sidebar và khối thống kê độc lập.
3. Thay composition của `LoggedInView`.
4. Di chuyển luồng action vào `PostActions`, mount đủ modal.
5. Nối route với `partners` và query event.
6. Hoàn thiện responsive, wording và banner spacer.
7. Đồng bộ sang ứng dụng còn lại, chạy test hai phía.

### 6.2 Trạng thái tại thời điểm ban hành

| Hạng mục | Trạng thái |
|---|---|
| Helper + unit test | Đã triển khai |
| Sidebar + thống kê + layout | Đã triển khai |
| Cổng Đăng bài + modal mã | Đã triển khai |
| Responsive + banner spacer | Đã triển khai |
| Đồng bộ `fecredit/` / `creator-app/` | Đã triển khai |
| Nghiệm thu visual đầy đủ | Chưa có bằng chứng trong repo |

## 7. Chiến lược kiểm thử

### 7.1 Unit test

Ba module bắt buộc có test ở cả hai ứng dụng:

| Module | Case tối thiểu |
|---|---|
| `cash-summary` | đủ ba khoản; chỉ waiting; input thiếu |
| `source-rows` | ánh xạ phổ biến; Facebook Post/Threads/Shopee; input thiếu; source lạ |
| `group-events-by-partner` | giữ thứ tự; ADV rỗng; event lệch ADV; partners chưa tải; active theo code/id |

Lệnh:

```bash
cd fecredit
yarn test --runInBand

cd ../creator-app
yarn test --runInBand \
  src/pages/home/components/statistic/cash-summary.test.ts \
  src/pages/home/components/statistic/source-rows.test.ts \
  src/pages/home/components/partner-sidebar/group-events-by-partner.test.ts
```

Kết quả đã xác minh ngày 2026-10-23: ba suite liên quan pass ở cả hai ứng dụng, tổng
30 test liên quan pass. Lần chạy toàn bộ `fecredit` tại thời điểm đó có 61 test pass.

### 7.2 Integration test

| Case | Kỳ vọng |
|---|---|
| URL thiếu `event`, danh sách có dữ liệu | Query được điền bằng code event đầu; tải đủ detail/schema/posts |
| Click event khác | Query đổi; bốn khối tên, tiền, schema và bài cùng đổi |
| Tạo bài thành công | Modal đóng, toast hiện, danh sách bài tải lại |
| Event cần mã | Hiện đúng modal mã; hoàn tất thì reload event và mở form bài |
| Event bị staff gate | Chỉ hiện modal điều kiện nhân viên |
| Event hết hạn | Nút disabled; không dispatch mở modal |

### 7.3 Visual test bắt buộc

Kiểm tra tối thiểu ở 375px, 768px, 1280px:

- sidebar một ADV và nhiều ADV;
- tên event dài hai dòng;
- đủ bốn cột thống kê với font FE Credit và font ADV rộng;
- bảng cuộn bên trong nhưng body không tràn ngang;
- banner một dòng và nhiều dòng; resize khi banner đang mở; đóng banner;
- trạng thái loading, thống kê rỗng và không có mốc thưởng.

### 7.4 Static review gate

```bash
# Không được thêm thay đổi backend trong task UI này
git diff --name-only release...HEAD -- backend admin

# Ba helper phải đồng nhất giữa hai app
cmp fecredit/src/pages/home/components/statistic/cash-summary.ts \
    creator-app/src/pages/home/components/statistic/cash-summary.ts
cmp fecredit/src/pages/home/components/statistic/source-rows.ts \
    creator-app/src/pages/home/components/statistic/source-rows.ts
cmp fecredit/src/pages/home/components/partner-sidebar/group-events-by-partner.ts \
    creator-app/src/pages/home/components/partner-sidebar/group-events-by-partner.ts

git diff --check
```

## 8. Phát hành và rollback

### 8.1 Phát hành

1. Gộp nhánh feature vào nhánh tích hợp tương ứng.
2. Build riêng `fecredit/` và `creator-app/` theo pipeline hiện có.
3. Smoke test `/trang-ca-nhan` với user có ít nhất hai event và một bài đăng.
4. Kiểm tra thêm user có `cashTotal.waiting > 0` và event yêu cầu mã.
5. Theo dõi lỗi client, lỗi tải `events/by-slug` và phản hồi sai số sau phát hành.

Không có migration, feature flag hoặc thứ tự deploy backend/frontend.

### 8.2 Rollback

Rollback bằng revert năm commit của feature theo thứ tự ngược hoặc redeploy artifact
frontend trước thay đổi. Không cần rollback dữ liệu vì task không ghi schema mới và
không thay dữ liệu server. Bài đăng tạo qua UI mới vẫn là bài hợp lệ của luồng cũ.

## 9. Rủi ro và kiểm soát

| Rủi ro | Kiểm soát |
|---|---|
| Hai app lệch logic sau một lần sửa | Helper giống byte-for-byte + test ở cả hai app |
| Query event và content hiển thị lệch nhau | Chỉ dùng query làm source of truth, không giữ selected state thứ hai |
| Modal chồng nhau | `showEventCode` kiểm tra user và ba modal hệ thống |
| Sai số tiền do dùng field tổng cũ | Tự cộng ba bucket trong helper có unit test |
| Nguồn mới ra nhãn trống | Fallback key + Title Case |
| Bảng làm tràn trang | `minWidth: 0` ở flex child + scroll tại Ant Table |
| Trình duyệt không có `ResizeObserver` | Các browser mục tiêu hiện đại hỗ trợ; nếu mở rộng support cần polyfill |
| Event code hoặc tên nguồn trùng | `rowKey=name` và query bằng code dựa trên giả định uniqueness hiện tại; backend phải giữ ràng buộc |

## 10. Vấn đề còn mở

Không có vấn đề kỹ thuật chặn việc nghiệm thu. Hai việc vận hành còn thiếu bằng chứng:

1. Chưa lưu bộ ảnh/video visual QA cho ba breakpoint nêu ở Mục 7.3.
2. Chưa có integration test tự động cho chuỗi bốn cổng trong `PostActions`; hiện phải
   nghiệm thu thủ công theo ma trận PRD Mục 10.1.

Hai mục này không thay đổi thiết kế nhưng phải được ghi nhận trong kết quả nghiệm thu.

## 11. Lịch sử sửa đổi

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 1.0 | 2026-10-23 | Lập thiết kế hồi cứu từ nhánh `feat/profile-page-ui-from-frontend`, liên kết PP-001–PP-009 |
| 1.1 | 2026-10-28 | Wording y hệt `frontend/` (commit `0a0c6cef5`): nhãn nguồn, “Thưởng:”, hiện lần cập nhật kế tiếp |
