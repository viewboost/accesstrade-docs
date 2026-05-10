# AccessTrade — Feature Inventory & Semantic Comparison

> Tài liệu so sánh chức năng giữa 3 sản phẩm: **TCB** (Techcombank), **vCreator**, **Ambassador**.
> **Generated**: 2026-05-07

---

## Mục đích

Stack tài liệu này phục vụ:
1. **Tra cứu**: feature X có ở đâu, file nào, function nào
2. **So sánh**: 3 dự án khác nhau ở chỗ nào (file-level + semantic-level)
3. **Quyết định strategic**: cần đồng bộ feature nào, port hướng nào

---

## Cấu trúc tài liệu

### 1. Inventory layer — "Có gì"
| File | Nội dung | Granularity |
|---|---|---|
| [inventory-techcombank.md](./inventory-techcombank.md) | Feature inventory TCB (29 services, 85 models, 17 dashboard routes) | File-level |
| [inventory-vcreator.md](./inventory-vcreator.md) | Feature inventory vCreator (15 services, 68 models) | File-level |
| [inventory-ambassador.md](./inventory-ambassador.md) | Feature inventory Ambassador (16 services, 66+ models) | File-level |
| [services-detailed.md](./services-detailed.md) | LOC + exported functions per service, gom theo 8 group | File-level |

### 2. Comparison layer — "Khác chỗ nào"
| File | Nội dung |
|---|---|
| [feature-comparison-matrix.md](./feature-comparison-matrix.md) | Side-by-side matrix services + admin pages + frontend pages |
| [verification-report.md](./verification-report.md) | Spot-check 20% sample, error rate 8%, corrections applied |

### 4. Action layer — "Làm gì trước"
| File | Nội dung |
|---|---|
| [gap-analysis-priority.md](./gap-analysis-priority.md) | **30 gaps scored 4-chiều (business perspective)** + roadmap 3 wave + top 5 quick wins + top 5 strategic decisions |

### 3. Semantic diff layer — "Khác biệt nghĩa là gì" (8 group)
| Group | File | Effort | Highlights |
|---|---|---|---|
| 1. User & Auth | [semantic-diff-user-auth.md](./semantic-diff-user-auth.md) | ~50 phút | Smoking gun: Ambassador comment "simplified version of TCB". vCr workplace 3-tier, Amb multi-platform 8 social. |
| 2. Content & Media | [semantic-diff-content-media.md](./semantic-diff-content-media.md) | agent | TCB LLM-based transcript scoring; vCr "Extended Period" mode; Amb mission feature. video.go 100% sync. |
| 3. Campaign & Event | [semantic-diff-campaign-event.md](./semantic-diff-campaign-event.md) | agent | Reward engine 2 generations: TCB+Amb V2, vCr V1. TCB campaign matching engine với scoring weights. |
| 4. Financial | [semantic-diff-financial.md](./semantic-diff-financial.md) | ~30 phút | Ambassador withdraw đã **comment out** bank validation. TCB-only budget alert. vCr pfloat round. |
| 5. Reconciliation & Audit | [semantic-diff-reconciliation-audit.md](./semantic-diff-reconciliation-audit.md) | ~30 phút | TCB monopoly reconciliation engine (1380 LOC). vCr audit thêm ActorType. |
| 6. Analytics & Dashboard | [semantic-diff-analytics-dashboard.md](./semantic-diff-analytics-dashboard.md) | ~25 phút | Hoàn toàn TCB-only (2226 LOC). Backend cho T-Fluencers Next.js dashboard. |
| 7. Targeting & Matching | [semantic-diff-targeting-matching.md](./semantic-diff-targeting-matching.md) | ~35 phút | Không service nào shared cả 3. vCr registry_match (B2B HR), TCB review system. |
| 8. Infrastructure & Misc | [semantic-diff-infrastructure-misc.md](./semantic-diff-infrastructure-misc.md) | ~30 phút | Notification: TCB có email (SendGrid), vCr+Amb chỉ Firebase. Affiliate engine = Ambassador-only. |

---

## Top insights cross-group

### Pattern lớn về business model

| Sản phẩm | Định hướng nghiệp vụ |
|---|---|
| **TCB** | Banking-grade B2B influencer matching. Có analytics dashboard, reconciliation engine, budget control, content moderation tools, review/rating system. Backend ~10,366 LOC services. |
| **vCreator** | B2B workplace (Brand→Company→Unit hierarchy) + employee onboarding qua HR registry import. Gọn nhất ~4,985 LOC. |
| **Ambassador** | Multi-platform creator economy (8 social platforms gồm Threads, Shopee, WildRift) + affiliate program + referrer commission MLM-style. Backend ~6,196 LOC. |

### Smoking guns phát hiện được trong code

1. **Ambassador `user_social_partner.go`** comment thẳng: *"This is a simplified version of TCB's implementation. TCB additionally checks PartnerInfluencerConfig auto-approve conditions... Both are not yet ported to Ambassador..."*
2. **Ambassador `withdraw.go`** đã **comment out** logic `checkUserBankCardValid` — feature WIP hoặc business model khác
3. **vCreator `registry_match.go`** comment giải thích lý do move package: *"Move sang internal để tránh public import admin — vi phạm layer..."*
4. **TCB `transcript`** dùng LLM-based scoring (CriteriaScores, BlacklistMatches) trong khi vCr+Amb dùng Senlyzer sentiment 3-tier → KHÔNG thể chia sẻ service.

### Files synced 100% (md5 identical)

Có thể coi là **stable shared code** giữa các dự án:
- `service/otp.go` — synced cả 3 (md5 = `19f454d9f7cb8503321a6dd14cd23e27`)
- `service/video.go` — synced cả 3 (50 LOC)
- `service/load_data.go` — synced TCB ↔ Ambassador (md5 = `93a5b3af5499e12fd0002cfad61a5bf2`)
- `service/audit.go` — synced TCB ↔ Ambassador (vCr divergent với ActorType)

→ Total ~5 services có thể coi là "đã đồng bộ". Phần còn lại (~27 services) đều có khác biệt nghiệp vụ thật.

### Direction port khả thi (theo từng group)

**TCB → vCr/Amb** (các feature TCB-led):
- Reconciliation engine (group 5) — 1380 LOC, model + service + admin handler
- Analytics dashboard (group 6) — 2226 LOC backend + Next.js frontend riêng
- Review/rating system (group 7) — 627 LOC + 2 models
- Budget alert (group 4) — 188 LOC + 2 models
- Content moderation tools — blacklist-keyword, manage-code, content-import
- Notification email channel (SendGrid) — TCB-led

**vCreator → TCB/Amb** (vCreator-led innovation):
- Audit ActorType (group 5) — ~20 LOC, cải tiến đơn giản
- pfloat.RoundToOneDecimal (group 4) — ~10 LOC, chống float precision bug
- Staff root account (group 8) — ~62 LOC

**Ambassador → các sản phẩm khác**:
- Multi-platform social support (Threads, Shopee, WildRift) — đặc thù business, không port được
- Affiliate program — đặc thù business, không port được

### Feature KHÔNG port được (do khác business model)

- vCreator workplace 3-tier (Brand→Company→Unit) → tied chặt với HR registry
- Ambassador affiliate suite → tied với Accesstrade SSO + pub2 module
- TCB partner-influencer config + reconciliation → tied với banking partner workflow

---

## Cách dùng tài liệu

### Use case 1: "Tôi muốn biết feature X có ở đâu"
→ Đọc [feature-comparison-matrix.md](./feature-comparison-matrix.md) (matrix side-by-side)

### Use case 2: "Function/method X có gì khác giữa 3 dự án"
→ Đọc [services-detailed.md](./services-detailed.md) (LOC + function names per service grouped)

### Use case 3: "Tôi muốn hiểu khác biệt VỀ NGHĨA của feature group X"
→ Đọc [semantic-diff-{group}.md](./) tương ứng (8 file)

### Use case 4: "Quyết định port feature X từ A sang B"
→ Đọc semantic diff của group chứa feature X, xem section "Direction port" cuối file. Sau đó quyết định strategic.

---

## Caveats & methodology

1. **Spot-check verified**: 20% sample, 100% existence pass. Matrix 8% error rate (corrections applied). Xem [verification-report.md](./verification-report.md).
2. **Semantic diff dựa trên đọc code thực tế** — không trust tên function. Mỗi file ~30-50 phút (group nhẹ) đến ~2-3h (group nặng).
3. **Limitations**:
   - Không cover frontend/admin pages (chỉ backend services + models).
   - Description trong inventory có thể chưa hoàn toàn chính xác — verify thêm nếu cần.
   - Câu hỏi business mở (mỗi semantic diff đều có) cần PM verify để confirm intent.
4. **Files trong scope**: chỉ `backend/internal/service/*.go` + models liên quan. Handlers (`pkg/admin/handler`, `pkg/public/handler`) chưa cover — có thể add sau nếu cần.

---

## Statistics

| Metric | Số liệu |
|---|---|
| Tổng inventory files | 4 |
| Tổng semantic diff files | 8 |
| Tổng services analyzed | 32 (across 3 projects) |
| Tổng models referenced | ~50 |
| Tổng LOC service đọc | ~21,500 |
| Effort | ~5 giờ wall-clock (mix manual + 2 agent parallel) |
