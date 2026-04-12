# VCreator Dashboard — Clone Plan từ TCB Dashboard

> **Ngày:** 2026-04-12
> **Nguồn:** Clone từ `accesstrade-projects/techcombank/dashboard` (Next.js 16)
> **Meeting reference:** [0410](../meeting-notes/0410.md)
> **PRD gốc:** [prd-vcreator-dashboard-2026-04-01.md](prd-vcreator-dashboard-2026-04-01.md)
> **Admin upgrade requirements:** [admin-dashboard-upgrade/overview.md](../admin-dashboard-upgrade/overview.md)

---

## 1. Tổng quan

Clone TCB Dashboard (Next.js 16 + TailwindCSS 4 + TanStack Query/Table + shadcn/ui + next-intl) → adapt cho Gen-Green VCreator. Giữ nguyên kiến trúc, bỏ features không cần, thêm requirements từ meeting 0410.

**TCB Dashboard có:** 16 routes, 203 files, ~1.4M source
**Gen-Green Dashboard sẽ có:** ~8 routes, ước tính ~120 files

---

## 2. Feature mapping: Giữ / Bỏ / Thêm

### A. Giữ nguyên (adapt endpoint + branding)

| Route TCB | Route Gen-Green | Mức sửa | Ghi chú |
|---|---|---|---|
| `/analytics` | `/analytics` | Trung bình | Adapt KPIs cho VCreator domain |
| `/contents` | `/contents` | Trung bình | Thêm cột + filter mới (xem C) |
| `/exports` | `/exports` | Thấp | Thêm cơ chế chọn cột |
| `/performance` | `/performance` | Thấp | Adapt cho creator performance |
| `/login` | `/login` | Thấp | Đổi branding + endpoint |
| `/settings` | `/settings` | Thấp | Đổi branding |
| Auth flow (OAuth2) | Giữ nguyên | Thấp | Đổi `ADMIN_URL` endpoint |
| i18n (vi/en) | Giữ, ẩn toggle | Thấp | Default vi, ẩn language switcher |
| Theme sáng/tối | Giữ nguyên | Không sửa | |
| Layout (sidebar, header) | Adapt | Thấp | Đổi menu + branding |
| UI components (shadcn) | Giữ nguyên | Không sửa | 23 UI components |

### B. Bỏ hoàn toàn

| Feature TCB | Lý do bỏ |
|---|---|
| `/campaigns` (CRUD, list, detail, edit, create) | Gen-Green dùng "event" quản lý ở admin cũ, không cần campaign matching/scoring |
| `/campaigns/[id]` + subpages | Không có tương đương |
| `/profiles` (influencer profiles, demographics) | Gen-Green dùng "creator" đơn giản hơn — xem tab Creator |
| `/profiles/[id]` + edit | Không cần profile detail phức tạp |
| `/influencers/[id]` | Gộp vào tab Creator |
| `/accept-invite`, `/forgot-password`, `/reset-password` | Auth qua admin cũ |
| Campaign components (17 files) | Không cần |
| Profile components (22 files) | Không cần |
| Review components (7 files) | Không cần |
| Matching session logic | Không cần |
| Feature flag `FEATURE_CAMPAIGNS` | Không cần |

### C. Thêm mới (từ meeting 0410)

| Feature | Route/Component | Mô tả | Người yêu cầu |
|---|---|---|---|
| **Tab Creator** | `/creators` | Bảng creator: Tên, Hashtag, Phân loại, Nơi LV, Tổng view, Tổng tiền, Đã rút, Số video, Ngày tham gia | Bình |
| **Filter Phân loại** | Analytics + Contents + Creators | Dropdown: Tất cả / CBNV / Bên ngoài | Bình, Hạnh |
| **Filter Cơ sở làm việc** | Analytics + Contents + Creators | Grouped dropdown (6 nhóm, 57 cơ sở) | Bình |
| **Cột Phân loại** | Contents table + Creators table | Badge: "CBNV" / "Bên ngoài" | Bình |
| **Cột Cơ sở làm việc** | Contents table + Creators table + Export | Tên cơ sở tại mỗi row | Bình |
| **Cột Hashtag cá nhân** | Contents table + Creators table + Export | Hashtag cá nhân creator | Bình |
| **Export chọn cột** | Export dialog | Checkbox list khi bấm "Xuất dữ liệu", default preset bỏ tick cột thừa | Quân đề xuất, Bình đồng ý |

---

## 3. Cấu trúc routes Gen-Green Dashboard

```
src/app/[locale]/
├── page.tsx                    → redirect /analytics
├── layout.tsx                  → root layout + providers
├── analytics/page.tsx          → Thống kê (KPIs + biểu đồ + filter CBNV)
├── contents/page.tsx           → Nội dung (table + filter + cột mới)
├── creators/page.tsx           → Creator (table mới)
├── performance/page.tsx        → Hiệu suất
├── exports/page.tsx            → Xuất dữ liệu
├── login/page.tsx              → Đăng nhập
├── settings/page.tsx           → Cài đặt
└── not-found.tsx               → 404
```

---

## 4. Sidebar navigation

```
┌─────────────────────────┐
│ 🟢 VCreator Dashboard  │
│                          │
│  📊 Thống kê            │ → /analytics
│  📹 Nội dung            │ → /contents
│  👥 Creator             │ → /creators (MỚI)
│  📈 Hiệu suất          │ → /performance
│  📥 Xuất dữ liệu       │ → /exports
│  ─────────────────────  │
│  ⚙️ Cài đặt            │ → /settings
│  🌙/☀️ Theme            │
│  ← Về Admin cũ         │
└─────────────────────────┘
```

---

## 5. Thay đổi Analytics (Thống kê)

### Layout tổng thể

```
┌─────────────┬──────────────────────────────────────────────┐
│ BỘ LỌC      │ VCreator Analytics                [Xuất DL] │
│              │ Dashboard phân tích hiệu quả thử thách      │
│ Thử thách   │                                              │
│ [dropdown]   │ ── Tổng quan Nền tảng ──────────────────── │
│              │ ┌────────┐┌────────┐┌────────┐┌────────┐   │
│ Khoảng TG    │ │Tổng    ││Mới     ││Tỷ lệ   ││Tỷ lệ  │   │
│ [30 ngày]    │ │Creator ││        ││hoạt    ││nghỉ   │   │
│              │ │3,256   ││847     ││động    ││       │   │
│ Từ — Đến     │ │+52.9%  ││+63.6%  ││25.0%   ││75.0%  │   │
│ [date range] │ └────────┘└────────┘└────────┘└────────┘   │
│              │                                              │
│ Phân loại 🆕│ [Tổng quan] [Influencer]                    │
│ [CBNV/ngoài]│                                              │
│              │ ── 6 KPI chính ─────────────────────────── │
│ Cơ sở LV 🆕│ ┌──────┐ ┌──────┐ ┌──────┐                  │
│ [grouped]    │ │Video ││Lượt  ││Ngân  │                  │
│              │ │104   ││xem   ││sách  │                  │
│ [ Áp dụng ] │ │      ││11.5M ││30.7% │                  │
│              │ └──────┘ └──────┘ └──────┘                  │
│              │ ┌──────┐ ┌──────┐ ┌──────┐                  │
│              │ │CPV   ││Engage││Tổng  │                  │
│              │ │3 ₫   ││2.3%  ││phí QC│                  │
│              │ └──────┘ └──────┘ └──────┘                  │
│              │                                              │
│              │ ── Thử thách (table) ──────────────────── │
│              │ ── Biểu đồ theo thời gian ────────────── │
│              │ ── Ngân sách | Tương tác ─────────────── │
│              │ ── Trạng thái duyệt ─────────────────── │
│              │ ── Phân bố NTảng | Lượt xem NTảng ───── │
│              │ ── Đối soát thanh toán ───────────────── │
└──────────────┴──────────────────────────────────────────────┘
```

### 5.1 Filter sidebar (bên trái)

| Filter | Nguồn TCB | Gen-Green | Thay đổi |
|---|---|---|---|
| Thử thách | ✅ (Campaign select) | ✅ (Event select) | Đổi tên |
| Khoảng thời gian | ✅ (Period select) | ✅ | Giữ |
| Từ ngày — Đến ngày | ✅ (Date range) | ✅ | Giữ |
| **Phân loại** | ❌ | ✅ | **MỚI** — CBNV / Bên ngoài |
| **Cơ sở làm việc** | ❌ | ✅ | **MỚI** — Grouped dropdown 57 cơ sở |

### 5.2 Tổng quan Nền tảng (4 KPI cards + trend)

| KPI | Giá trị | Trend | Nguồn TCB |
|---|---|---|---|
| Tổng số Creator | 3,256 | +52.9% ↑ | ✅ (Total Influencer) |
| Creator mới | 847 | +63.6% ↑ | ✅ (Influencer mới) |
| Tỷ lệ hoạt động | 25.0% | +13.1% ↑ | ✅ (Tỷ lệ hoạt động) |
| Tỷ lệ nghỉ | 75.0% | +3.7% ↓ | ✅ (Tỷ lệ nghỉ) |

### 5.3 Tabs: Tổng quan / Influencer

Giữ nguyên 2 tab từ TCB. Tab "Tổng quan" chứa tất cả widget bên dưới. Tab "Influencer" chứa bảng influencer chi tiết (link sang tab Creator ở sidebar).

### 5.4 Widget: 6 KPI chính

| KPI | Giá trị mẫu | Nguồn TCB |
|---|---|---|
| Tổng Video | 104 | ✅ (Tổng Video) |
| Lượt xem | 11.5M | ✅ (Lượt xem) |
| Ngân sách | 30.7% | ✅ (Ngân sách) |
| CPV trung bình | 3 ₫ | ✅ (CPV) |
| Engagement | 2.3% | ✅ (Engagement) |
| Tổng phí quảng cáo | 36.8Tr ₫ | ✅ (Tổng phí quảng cáo) |

### 5.5 Widget: Bảng Thử thách

Table danh sách sự kiện/thử thách:

| Cột | Mô tả |
|---|---|
| Tên thử thách | Tên sự kiện |
| Trạng thái | Active / Completed / Draft |
| Ngân sách | Đã dùng / Tổng (progress) |
| Videos | Số video đã nộp |
| Views | Tổng lượt xem |
| CPV | Chi phí / lượt xem |

### 5.6 Widget: Biểu đồ theo thời gian

- **Chart type:** Multi-line / bar chart (Chart.js)
- **Series:** Lượt xem, Video, Tỷ lệ tương tác, Khách hàng mới (toggle checkbox)
- **Time axis:** Daily / Monthly toggle
- **Nguồn TCB:** ✅ (Timeline chart giữ nguyên)

### 5.7 Widget: Ngân sách thử thách

| Thành phần | Mô tả |
|---|---|
| Progress bar | % đã sử dụng (gradient xanh) |
| 3 metrics | Đã dùng (VND) · Tổng (VND) · Còn lại (VND) |
| **Nguồn TCB:** | ✅ (Budget widget) |

### 5.8 Widget: Tương tác

| Metric | Giá trị mẫu |
|---|---|
| Lượt xem | 11.5M |
| Thích | 258K (2.2%) |
| Bình luận | 6K (0.1%) |
| Tỷ lệ tương tác | 2.29% |
| **Nguồn TCB:** | ✅ (Interaction chart) |

### 5.9 Widget: Trạng thái duyệt

| Thành phần | Mô tả |
|---|---|
| Stacked bar | Đã duyệt (xanh) / Chờ duyệt (vàng) / Từ chối (đỏ) |
| 3 stats | 82% (74 video) · 9% (8) · 9% (8) |
| Top 5 lý do từ chối | List với count |
| **Nguồn TCB:** | ✅ (Approval chart + Rejection reasons) |

**Lý do từ chối mẫu:**
1. Sai chủ đề chương trình
2. Không phù hợp hình ảnh thương hiệu
3. Link lỗi / không truy cập được
4. Thiếu/sai lời kêu gọi hành động (CTA)
5. Lý do khác

### 5.10 Widget: Phân bố theo nền tảng

| Thành phần | Mô tả |
|---|---|
| Pie chart (SVG) | YouTube vs Facebook vs TikTok... (% + count) |
| **Nguồn TCB:** | ✅ (Platform chart) |

### 5.11 Widget: Lượt xem theo Nền tảng

| Thành phần | Mô tả |
|---|---|
| Horizontal bar chart | Mỗi platform 1 bar, hiển thị lượt xem |
| **Nguồn TCB:** | ✅ (Platform views chart) |

### 5.12 Widget: Đối soát thanh toán

| Thành phần | Mô tả |
|---|---|
| 3 KPI cards | Tổng đợt · Yêu cầu thành công · Đã thanh toán (VND) |
| Table | Tên đợt, Trạng thái, Yêu cầu, Thành công, Tỷ lệ, Tổng tiền, Đã TT, Ngày |
| **Nguồn TCB:** | ✅ (Reconciliation widget) |

### 5.13 Demo link

Demo đầy đủ các widget tại: `accesstrade-projects/demo-gen-green` → route `/dashboard-moi` → tab "Thống kê"

---

## 6. Thay đổi Contents (Nội dung)

### Cột table

| Cột | TCB | Gen-Green | Thay đổi |
|---|---|---|---|
| Thumbnail | ✅ | ✅ | Giữ |
| Tiêu đề | ✅ | ✅ | Giữ |
| Creator | ✅ (Created By) | ✅ | Giữ |
| **Phân loại** | ❌ | ✅ | **MỚI** — Badge CBNV/Bên ngoài |
| **Cơ sở làm việc** | ❌ | ✅ | **MỚI** |
| **Hashtag cá nhân** | ❌ | ✅ | **MỚI** |
| Nguồn | ✅ | ✅ | Giữ (TikTok/YouTube/Facebook/Instagram) |
| Sự kiện | ✅ (Event) | ✅ | Giữ |
| Lượt xem | ✅ | ✅ | Giữ, sortable |
| Trạng thái | ✅ | ✅ | Giữ (Duyệt/Chờ/Từ chối) |
| Warning Tags | ✅ | ✅ | Giữ |
| Ngày đăng | ✅ | ✅ | Giữ |

### Filter

| Filter | TCB | Gen-Green | Thay đổi |
|---|---|---|---|
| Search | ✅ | ✅ | Giữ |
| Date Range | ✅ | ✅ | Giữ |
| Source | ✅ | ✅ | Giữ |
| Event | ✅ | ✅ | Giữ |
| Status | ✅ | ✅ | Giữ |
| Created By | ✅ | ✅ | Giữ |
| Warning Tag | ✅ | ✅ | Giữ |
| **Phân loại** | ❌ | ✅ | **MỚI** |
| **Cơ sở làm việc** | ❌ | ✅ | **MỚI** |

---

## 7. Tab Creator (MỚI — thay thế Profiles)

| Cột | Ghi chú |
|---|---|
| Avatar | |
| Tên | |
| Hashtag cá nhân | **MỚI** |
| Phân loại | **MỚI** — Badge CBNV/Bên ngoài |
| Nơi làm việc | **MỚI** |
| Tổng view | |
| Tổng tiền | |
| Tổng tiền đã rút | |
| Số video | |
| Ngày tham gia | Giữ (bỏ Ngày tạo) |

Filter: Search + Phân loại + Cơ sở làm việc

---

## 8. Export chọn cột

Khi bấm "Xuất dữ liệu" ở bất kỳ tab nào → dialog checkbox list:
- Mặc định tick tất cả cột đang hiển thị
- Bỏ tick sẵn cột thừa (ID video, Thumbnail, Sentiment, Đối tác VinWonders, Ngày tạo)
- Cột mới (Phân loại, Cơ sở, Hashtag) đánh dấu badge "MỚI"
- Bấm "Xuất" → file chỉ chứa cột đã chọn

---

## 9. Tech stack (giữ nguyên từ TCB)

| Layer | Technology |
|---|---|
| Framework | Next.js 16.1.6 (App Router, Turbopack) |
| UI | TailwindCSS 4 + shadcn/ui + Radix UI |
| Data | TanStack Query v5 + TanStack Table v8 |
| HTTP | Axios + interceptors |
| Charts | Chart.js + react-chartjs-2 |
| i18n | next-intl v4 (vi/en, ẩn toggle) |
| Theme | next-themes (sáng/tối) |
| Icons | lucide-react |
| Animation | framer-motion |
| Auth | OAuth2 code flow + localStorage token |
| Build | Standalone output, Docker-ready |

---

## 10. Ước tính effort

| Hạng mục | Files sửa/tạo | Effort |
|---|---|---|
| Clone + strip (bỏ campaigns, profiles, reviews) | ~80 files xóa | 2h |
| Rebrand (logo, sidebar, titles, translations) | ~15 files | 2h |
| Adapt Analytics (KPIs, filter CBNV, biểu đồ) | ~10 files | 4h |
| Adapt Contents (cột mới, filter mới) | ~8 files | 3h |
| Tạo Tab Creator (table, filter, columns) | ~6 files | 3h |
| Export chọn cột (dialog component) | ~3 files | 2h |
| Adapt API layer (endpoints, types) | ~10 files | 3h |
| Test + fix | — | 3h |
| **Tổng** | | **~22h (~3 ngày)** |

---

## 11. Phụ thuộc

| Phụ thuộc | Trạng thái |
|---|---|
| Backend API VCreator: endpoint analytics, contents, creators, exports | Đang có (admin cũ đã dùng) |
| Backend API: field `account_type`, `workplace_name` trên user/content | Cần bổ sung (phụ thuộc feature phân loại CBNV) |
| Backend API: endpoint export với `columns[]` param | Cần bổ sung |
| Form đăng ký CBNV (thu thập workplace data) | Đang thiết kế |
