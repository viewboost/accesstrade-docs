# PRD — Menu Influencer (Danh sách & Chi tiết)

**Thời gian:** 24/05/2026
**Trạng thái:** Đã implement
**Repo:** `techcombank/dashboard` (Next.js) + `techcombank/backend` (Go)
**Branch:** `feat/influencer-management`

---

## 1. Executive Summary

Menu **Influencer** cung cấp góc nhìn theo **con người** (không phải theo kênh MXH) cho người tham gia thử thách T-Fluencers. Đơn vị dữ liệu là **`user-partner`** (cặp `user` × `partner=TCB`) — đã chứa sẵn số liệu tổng hợp (statistic, contentStatistic, socialSourceStats, statusStaff), nên list/detail đọc thẳng không phải tính lại.

Gồm 2 màn:
- **Danh sách** (`/influencers`): list user-partner + search + filter Techcomer + sort server-side + paging.
- **Chi tiết** (`/influencers/:id`): header info + thống kê tổng hợp, 3 tab (Tổng quan / Hồ sơ / Thử thách), mỗi tab data phân trang riêng.

---

## 2. Business Objectives

1. Xem đóng góp của từng influencer ở cấp con người, gộp mọi kênh.
2. Quản lý CBNV Techcombank (Techcomer) — lọc, tìm theo mã nhân viên.
3. Drill-down: từ 1 người xem hết kênh + lịch sử thử thách họ tham gia.

---

## 3. Success Metrics

- Tra cứu 1 influencer ra toàn bộ kênh + thử thách trong ≤ 2 click.
- Sort/filter đúng trên toàn dataset (không chỉ trang hiện tại).
- Không có số liệu suy đoán hiển thị sai (chỉ hiển field có thật trong DB).

---

## 4. User Personas

| Persona | Nhu cầu |
|---|---|
| Account Manager / Ops | Tra người tham gia, xem đóng góp, tìm Techcomer |
| Marketing | Đánh giá hiệu suất content/campaign theo người |

---

## 5. Phân tầng dữ liệu (quan trọng)

```
PARTNER (TCB)
  └─ USER-PARTNER  ◄── đơn vị "Influencer" (= user × partner, đã aggregate sẵn)
       └─ USER          (info cá nhân, KYC, social login)
            └─ USER-SOCIAL  (tầng con: từng kênh FB/IG/TT/YT)
```

- **Danh sách** đọc `user-partner` (qua `/partners/users`) — backend tự giới hạn theo partner của staff đang đăng nhập (`AssignPartnerForStaff`), FE không cần truyền partnerId.
- **Hồ sơ** = `user-social-partner` (kênh) của user.
- **Thử thách** = gộp `user-event-analytic-daily` theo event.

---

## 6. Scope

### In scope (đã implement)
- Trang danh sách: search (tên/email/mã NV/đt/tiktok/**hashtag**), filter Techcomer + **tỉnh thành**, sort server-side (gồm **Techcomer**), paging.
- Trang chi tiết: header + thống kê tổng hợp + 3 tab paging riêng; tab Tổng quan show **profile cá nhân đầy đủ** (sđt/giới tính/ngày sinh/tỉnh thành/nghề nghiệp).
- Backend: filter `statusStaff` + `cityCode`, sort các field (gồm `statusStaff`, `contentStatistic.approved`), endpoint campaigns mới, mở rộng detail trả statistic + `user.info`.

### Out of scope (chưa làm)
- Filter theo nền tảng (`source`) và trạng thái duyệt ở danh sách (cần join `user-social-partners`).
- Tab Nhân khẩu học / Lịch sử kiểm duyệt (đã thiết kế, chưa build).
- Dedup influencer trùng bản ghi.
- Matching/tuyển chọn influencer cho campaign.

---

## 7. Functional Requirements

### 7.1 Danh sách Influencer

#### FR-001: List theo user-partner (Must)
- Endpoint `GET /partners/users?page=&limit=&keyword=&statusStaff=&sort=`.
- Response `{ data: UserPartner[], total }`. Mỗi dòng có `user{_id,name,hashtag,email}`, `statusStaff`, `companyCode`, `statistic`, `contentStatistic`, `socialSourceStats`, `joinedAt`.
- **Avatar không có** ở list response → hiển tên + email/hashtag.

#### FR-002: Cột bảng (Must)
| Cột | Field | Sort |
|---|---|---|
| Influencer | `user.name` + email/hashtag dòng phụ | — |
| Bài đăng | `contentStatistic.approved` | ✅ `contentStatistic.approved` |
| Lượt xem | `contentStatistic.view.completed` | ✅ `contentStatistic.view.completed` |
| Cash | `contentStatistic.cash.notRejected` | ✅ `contentStatistic.cash.notRejected` |
| Techcomer | `statusStaff` + `companyCode` | ✅ `statusStaff` |
| Tham gia | `joinedAt` | ✅ `joinedAt` |

- **Hiển thị Cash dùng `formatCurrency`** (số đầy đủ `1.200.000 ₫`), KHÔNG dùng rút gọn (`1.2Tr`) — tránh nhầm đơn vị khi so sánh/sort.
- **Cột hiển thị và field sort PHẢI cùng field** (Cash hiển + sort đều `contentStatistic.cash.notRejected`).

#### FR-003: Search (Must)
- Param `keyword` → backend `$or` match: `user.searchString` (tên/email/mã user/đt/tiktok), `code` (mã NV cấp user-partner — ưu tiên), `user.staffCode` (fallback), `user.hashtag`.
- Regex case-insensitive, non-accent (`format.SearchString`).
- Debounce 300ms ở FE, đẩy lên URL param.

#### FR-004: Filter Techcomer (Must)
- Param `statusStaff` ∈ {employee, not_employee, not_verify}, exact match field `statusStaff` (`AssignStatusStaff`).
- Single-select dropdown, đẩy URL.

#### FR-004b: Filter Tỉnh/Thành (Must)
- Param `cityCode` (int) → exact match field `user.info.cityCode` (`AssignCityCode`).
- Dropdown **searchable** (~63 tỉnh), options lấy từ `GET /provinces` (hook `useProvinces` gom hết qua `nextPageToken`). Đẩy URL `cityCode`.
- ⚠️ Vì filter trên `user.*` (cần `$lookup users` trong pipeline), count phải đi nhánh aggregation — `cityCode > 0` đã được thêm vào điều kiện count.

#### FR-005: Sort server-side (Must)
- Param `sort=<field>:<dir>` (vd `contentStatistic.cash.notRejected:desc`).
- Field phải nằm trong `constants.UserPartnerSortAllow`. Hiện cho: `joinedAt, createdAt, statistic.cashRemaining, statistic.cashWithdrawSuccess, contentStatistic.view.completed, contentStatistic.cash.notRejected, contentStatistic.approved, statusStaff`.
- FE toggle 3 trạng thái: chưa sort → desc → asc → bỏ sort. Đẩy URL.

#### FR-006: Paging (Must — CRITICAL)
- **Backend `user-partner` pipeline dùng page 0-based** (`$skip = page * limit`).
- **FE UI dùng 1-based**, phải gửi `page - 1` khi gọi `/partners/users`.
- ⚠️ Lỗi off-by-one nếu gửi 1-based trực tiếp → trang 1 skip mất 1 trang đầu (mất các giá trị cao nhất khi sort). Đã fix tại `fetchInfluencers`.

### 7.2 Chi tiết Influencer

#### FR-007: Detail info + profile cá nhân + thống kê (Must)
- `GET /influencers/:id` trả:
  - Info + **profile cá nhân** (từ `user.info` + `user.phone`): `name, avatar, email, hashtag, phone, gender, birthDay, cityCode, cityName, occupation`. `cityName` lookup từ collection `provinces` theo `cityCode`.
  - Thống kê tổng hợp từ user-partner: `statusStaff, companyCode, joinedAt, statistic, contentStatistic, socialSourceStats`.
- **KHÔNG trả profiles/campaigns** — chúng có endpoint paging riêng.
- Resolve partner theo staff đang login (không cần partnerId từ FE).

#### FR-008: Tab Tổng quan (Must)
- 4 thẻ: tổng follower (`sum socialSourceStats.*.subscribers`), bài đăng (`contentStatistic.approved`), lượt xem (`view.completed`), cash (`statistic.cashTotal` — thẻ tóm tắt dùng `formatBudget`).
- Thẻ thông tin **đầy đủ** (giống form user tự cập nhật): tên, email, SĐT, hashtag, giới tính, ngày sinh, tỉnh/thành, nghề nghiệp, trạng thái Techcomer, mã NV, danh sách nền tảng có data.

#### FR-009: Tab Hồ sơ — paging (Must)
- `GET /influencers/:id/profiles?page=&limit=` → `{ data: InfluencerProfile[], total }`.
- **page 1-based** (service tự `(page-1)*limit`).
- Trả **mọi trạng thái** (approved/pending/rejected) — KHÔNG lọc `status=approved` (trang quản lý cần thấy hết). Cột Trạng thái hiển thị status thật.
- Cột: nền tảng, tài khoản, follower, engagement, video, trạng thái, link kênh.

#### FR-010: Tab Thử thách — paging (Must)
- `GET /influencers/:id/campaigns?page=&limit=` → `{ data: InfluencerCampaign[], total }`.
- Aggregation `user-event-analytic-daily` match `{user, partner}`, group theo event, `$facet` (data + count), `$lookup` events lấy `name`/`code`.
- Sum loại bỏ rejected: views = `view.total - view.rejected`, videos = `totalContent - totalContentRejected`, cash = `cash.total - cash.rejected`.
- **Event đã xóa** (`$lookup` rỗng) → `eventName`/`eventCode` rỗng → FE hiển **"[Thử thách đã xóa]"**.
- Cash hiển `formatCurrency`.

---

## 8. Non-Functional Requirements

### NFR-001: i18n nhất quán (Must)
- Namespace `influencers` (vi + en). User-facing dùng "Influencer", "Thử thách", "Hồ sơ", "Techcomer". Không hardcode text.
- Key gồm: `filter.staff`, `filter.province`, `staffStatus.*`, `gender.*`, `detail.{phone,hashtag,gender,birthDay,city,occupation,...}`, `detail.deletedCampaign`. Đủ cả vi + en.

### NFR-002: Không hiển số suy đoán (Must)
- Chỉ hiển field có thật lưu sẵn. Đã **bỏ cột "Số hồ sơ"** (suy từ `socialSourceStats`, không phải count thật) và **KPI sum theo trang** (lệch khi paging). Tổng số thật chỉ hiển ở pagination (`total` từ API).

### NFR-003: Hiển thị = sort cùng field (Must)
- Mọi cột sortable: giá trị hiển thị và field sort phải trùng, tránh ảo giác sort sai.

### NFR-004: Paging convention rõ ràng (Must)
- `/partners/users`: 0-based (FE trừ 1). `/influencers/:id/profiles|campaigns`: 1-based (service tự trừ). Ghi rõ trong code comment.

---

## 9. API Summary

| Method | Path | Mục đích | Paging |
|---|---|---|---|
| GET | `/partners/users` | List influencer (user-partner); params: keyword, statusStaff, cityCode, sort | 0-based |
| GET | `/influencers/:id` | Detail: info + profile cá nhân + thống kê tổng hợp | — |
| GET | `/influencers/:id/profiles` | Hồ sơ (user-social) | 1-based |
| GET | `/influencers/:id/campaigns` | Thử thách (gộp event) | 1-based |
| GET | `/provinces` | Danh sách tỉnh/thành cho filter (dùng lại API public) | nextPageToken |

---

## 10. Files chính

**Backend (Go):**
- `internal/constants/sort.go` — `UserPartnerSortAllow` (gồm `statusStaff`, `contentStatistic.approved`)
- `internal/util/mgquery/common.go` — `AssignStatusStaff`, `AssignCityCode`
- `pkg/admin/model/request/user.go` — param `statusStaff`, `cityCode`
- `pkg/admin/model/request/analytics.go` — param `userIds` (creator leaderboard)
- `pkg/admin/handler/influencer_profiles.go` — `GetInfluencerProfiles` (paging), `GetInfluencerCampaigns`
- `pkg/admin/service/influencer_profiles.go` — detail (statistic + user.info + lookup province), profiles paging, campaigns aggregation
- `pkg/admin/service/partner.go` — `GetListUser` search `$or` (keyword + code + staffCode + hashtag), filter cityCode, count-by-aggregation khi filter user.*
- `pkg/admin/model/response/influencer_profiles.go` — `InfluencerCampaign(List)`, `Influencer` (profile + statistic fields)
- `pkg/admin/router/influencer_profiles.go` — route `/influencers/:id/campaigns`

**Frontend (Next.js):**
- `src/app/[locale]/influencers/page.tsx` — danh sách
- `src/app/[locale]/influencers/[id]/page.tsx` — chi tiết + tabs
- `src/components/influencers/` — filter, table, columns
- `src/components/influencers/detail/` — header, overview/profiles/campaigns tab
- `src/hooks/use-influencers.ts` — hooks (list page 0-based, detail/profiles/campaigns, `useProvinces`)
- `src/lib/influencer-stats.ts` — helper tính follower/views/cash
- `src/types/influencers.ts` — types (gồm `Province`, profile fields)
- `src/components/influencers/influencer-filter.tsx` — filter Techcomer + dropdown tỉnh searchable
- `src/messages/{vi,en}/influencers.json` — i18n

---

## 11. Epics

### EPIC-001: Danh sách Influencer (Done)
FR-001 → FR-006 + FR-004b. List + search (gồm hashtag) + filter Techcomer + filter tỉnh thành + sort server-side (gồm Techcomer) + paging.

### EPIC-002: Chi tiết Influencer (Done)
FR-007 → FR-010. Header + thống kê + profile cá nhân đầy đủ + 3 tab paging riêng.

### EPIC-003 (Next): mở rộng
- Filter nền tảng (`source`) + trạng thái duyệt ở danh sách (cần join `user-social-partners`).
- Tab Nhân khẩu học + Lịch sử kiểm duyệt.
- Dedup influencer trùng bản ghi.
