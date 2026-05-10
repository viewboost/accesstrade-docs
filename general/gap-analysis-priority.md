# Gap Analysis & Priority — AccessTrade 3 Products

> **Generated**: 2026-05-07
> **Perspective**: Business (revenue, retention, compliance, UX)
> **Source**: Tổng hợp gap từ 8 file [semantic-diff-*.md](./)

---

## Framework scoring

Mỗi gap được score 4 chiều (1-5/chiều, tổng 4-20):

| Chiều | Câu hỏi | Score 1 | Score 5 |
|---|---|---|---|
| **Business value** | Resolve gap có tăng revenue/UX/compliance/retention không? | Cosmetic | Critical compliance hoặc revenue blocker |
| **Risk if unresolved** | Để gap tồn tại có gây hại gì? | Không sao | Bug production / data loss / mất uy tín |
| **Effort (đảo)** | Tốn bao nhiêu để fix? (đảo: 5=easy, 1=hard) | >1 quý | <1 ngày |
| **Cross-product impact** | Resolve có lợi cho mấy sản phẩm? | 1 dự án | Cả 3 |

**Phân loại priority**:
- 🔴 **P0 (≥16)**: Làm ngay tuần này — critical bug, compliance, easy win với impact cao
- 🟠 **P1 (12-15)**: Sprint tới — strategic ưu tiên cao
- 🟡 **P2 (8-11)**: Backlog — nice-to-have, làm khi có resource
- ⚪ **P3 (<8)**: Chưa cần — defer hoặc bỏ

---

## Bảng gap chính (sorted by total score, business perspective)

| # | Gap | Source group | Direction port | BV | Risk | Effort | XProd | **Total** | **Priority** |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | **Withdraw cả 3 đều admin-driven thực tế, có dead code endpoint** — TCB/vCr có `POST /withdraw` + frontend service nhưng 0 caller pages. UI `/bank` chỉ hiển thị "Bạn chưa đến kỳ thanh toán". Đề xuất xóa endpoint sau khi verify không có client mobile/external. [Detail](./gaps/01-ambassador-withdraw-bank-validation.md) | Financial | Cleanup dead code 3 dự án | 2 | 1 | 4 | 4 | **11** | 🟡 P2 |
| 2 | **Ambassador chưa có auto-approve influencer + notification** (comment "not yet ported") — creator phải chờ admin manual approve | User & Auth | TCB → Ambassador | 5 | 4 | 3 | 2 | **14** | 🟠 P1 |
| 3 | **vCreator dùng reward V1 (naive)** — không có budget control, không có distributed lock → race condition khi nhiều creator cùng claim reward | Campaign & Event | TCB/Amb V2 → vCreator | 5 | 5 | 2 | 2 | **14** | 🟠 P1 |
| 4 | **Float precision rounding chỉ vCreator có** (`pfloat.RoundToOneDecimal`) — TCB/Amb có thể bị bug làm tròn cash. Tuy nhiên 2 sản phẩm kia chạy campaign tiền to (không có fractional cents) → risk thực tế thấp. Reclassified P0→P2 (2026-05-07) | Financial | vCreator → TCB/Amb | 2 | 2 | 5 | 2 | **11** | 🟡 P2 |
| 5 | **Audit ActorType field chỉ vCreator có** — Cả 3 dự án đều có flow dùng root account để audit, nhưng TCB/Amb không có field metadata phân biệt → query log không filter được automation vs manual. Reclassified P0→P2 (2026-05-07): không cấp bách, nice-to-have. [Detail](./gaps/05-audit-actor-type.md) | Reconciliation & Audit | vCreator → TCB/Amb | 3 | 2 | 5 | 4 | **14** | 🟡 P2 |
| 6 | **TCB Reconciliation engine** (1380 LOC, 3 services) — chỉ TCB có. vCr/Amb có model + admin page nhưng không có evaluation engine → admin page có thể là dead UI | Reconciliation & Audit | TCB → vCr/Amb (chỉ nếu cần) | 4 | 3 | 1 | 3 | **11** | 🟡 P2 |
| 7 | **TCB Analytics Dashboard** (Next.js, 2226 LOC backend) — TCB-only. vCr/Amb không có dashboard executive view | Analytics & Dashboard | TCB → vCr/Amb (strategic) | 4 | 2 | 1 | 3 | **10** | 🟡 P2 |
| 8 | **vCreator thiếu budget control system** — TCB và Ambassador GẦN NHƯ TƯƠNG ĐƯƠNG (3-level Bpe/Bpu/Bpc + block + threshold + Telegram alert), chỉ vCreator thiếu hoàn toàn → chi tiền không giới hạn. Reclassified direction port (2026-05-07) sau user catch. [Detail](./gaps/08-budget-alert-system.md) | Campaign & Event | TCB hoặc Amb → vCreator | 5 | 4 | 3 | 4 | **16** | 🔴 P0 |
| 9 | **Ambassador `RecoverRecheckInProgress`** (cron recovery sau crash) — TCB không có → TCB có thể bị stuck `RecheckInProgress` flag sau crash | Campaign & Event | Ambassador → TCB | 4 | 4 | 4 | 2 | **14** | 🟠 P1 |
| 10 | **Ambassador `isSendNotification` flag** (single-fire alert) — tránh spam Telegram khi crash loop. TCB chưa có | Campaign & Event | Ambassador → TCB | 3 | 4 | 5 | 2 | **14** | 🟠 P1 |
| 11 | **TCB email transactional** (SendGrid + SMTP) — vCr/Amb chỉ có Firebase push, không có email | Infrastructure & Misc | TCB → vCr/Amb | 4 | 3 | 2 | 4 | **13** | 🟠 P1 |
| 12 | **TCB rate limit OTP cho admin** — vCr/Amb không có → admin login có thể bị brute force | Infrastructure & Misc | TCB → vCr/Amb | 4 | 5 | 4 | 4 | **17** | 🔴 P0 |
| 13 | **TCB blacklist-keyword + content moderation tools** — vCr/Amb không có → khó kiểm soát content vi phạm | Content & Media | TCB → vCr/Amb | 4 | 4 | 3 | 4 | **15** | 🟠 P1 |
| 14 | **TCB ContentImportTracking** (admin bulk import audit) — vCr/Amb không có nếu họ có nhu cầu import bulk | Content & Media | TCB → vCr/Amb (nếu cần) | 2 | 2 | 3 | 2 | **9** | 🟡 P2 |
| 15 | **TCB ReconciliationSnapshot insert per crawl** (anti-fraud audit trail) — vCr/Amb không track | Content & Media | TCB → vCr/Amb | 3 | 4 | 2 | 4 | **13** | 🟠 P1 |
| 16 | **TCB Profile Review + Rating** (627 LOC) — vCr/Amb không có concept rating creator → brand không có signal trust | Targeting & Matching | TCB → vCr/Amb | 4 | 3 | 2 | 4 | **13** | 🟠 P1 |
| 17 | **TCB upload_avatar_social** (cache MinIO) — vCr/Amb dùng URL social trực tiếp → URL có thể expire, broken avatar | Content & Media | TCB → vCr/Amb | 3 | 4 | 3 | 4 | **14** | 🟠 P1 |
| 18 | **TCB BudgetInfo struct (vs Ambassador)** — Ambassador đã có pre-compute UsedPercent giúp dashboard query nhanh, TCB chưa | Campaign & Event | Ambassador → TCB | 2 | 2 | 4 | 1 | **9** | 🟡 P2 |
| 19 | **vCreator Extended Period mode** — feature đặc thù single-brand, TCB/Amb không có | Campaign & Event | KHÔNG port (vCreator-specific) | 2 | 1 | 1 | 1 | **5** | ⚪ P3 |
| 20 | **Ambassador Affiliate suite** (campaign + contract + links + mapping) — Ambassador-only, KHÔNG port được | Infrastructure | KHÔNG port | 5 | 1 | 1 | 1 | **8** | 🟡 P2 |
| 21 | **Ambassador Mission/WildRift gamification** — Ambassador-specific business model | Content & Media | KHÔNG port | 2 | 1 | 1 | 1 | **5** | ⚪ P3 |
| 22 | **vCreator Workplace 3-tier (Brand→Company→Unit)** — vCreator-specific B2B onboarding | User & Auth | KHÔNG port | 2 | 1 | 1 | 1 | **5** | ⚪ P3 |
| 23 | **vCreator registry_match HR engine** — vCreator-specific (B2B HR import workflow) | Targeting & Matching | KHÔNG port | 2 | 1 | 1 | 1 | **5** | ⚪ P3 |
| 24 | **TCB Campaign matching engine + filtered_campaigns** — TCB flagship feature riêng (T-Fluencers) | Campaign & Event | KHÔNG port | 4 | 1 | 1 | 1 | **7** | ⚪ P3 |
| 25 | **vCreator Staff root account** — utility cho automation flows, có thể backport | Infrastructure & Misc | vCreator → TCB/Amb | 2 | 2 | 5 | 4 | **13** | 🟠 P1 |
| 26 | **TCB transcript scoring (LLM-based)** vs vCr/Amb (Senlyzer sentiment) — không thể chia sẻ service, business model khác | Content & Media | KHÔNG port | 3 | 2 | 1 | 1 | **7** | ⚪ P3 |
| 27 | **Ambassador chưa có user_social_partner config check** (comment "not yet ported") — duplicate với gap #2 | User & Auth | (gộp với #2) | - | - | - | - | - | - |
| 28 | **Multi-tenant Partner concept khác nhau 3 sản phẩm** — TCB partner / vCr workplace / Amb Partner — long-term cần unify | User & Auth | Strategic decision | 3 | 3 | 1 | 5 | **12** | 🟠 P1 |
| 29 | **`load_data.go` synced TCB↔Ambassador chưa có process** — đang copy thủ công khi update, dễ drift | Infrastructure & Misc | Process improvement | 2 | 3 | 4 | 2 | **11** | 🟡 P2 |
| 30 | **TCB telegram alert có dùng** — Ambassador đã có nhưng label `[Ambassador]`, chưa unify infrastructure | Campaign & Event | Process improvement | 2 | 2 | 4 | 2 | **10** | 🟡 P2 |

---

## Priority breakdown

### 🔴 P0 — Làm ngay (2 items, sau khi reclassify gap #4 và #5 sang P2 — 2026-05-07)
Score ≥ 16. Ưu tiên cao nhất do **easy win + cross-product impact lớn** hoặc **critical risk**.

| # | Gap | Effort | Impact |
|---|---|---|---|
| 8 | **Budget control** — port từ Ambassador → vCreator (TCB và Amb đã có) | 3-4 ngày | vCreator hiện chi tiền không giới hạn (revenue protection) |
| 12 | **Rate limit OTP admin** — port từ TCB → vCr/Amb | 2-3 ngày | Chống brute force admin login (security) |

→ **Tổng ~5-8 ngày dev** cho 2 items. Nên làm trong **wave 1 (tuần 1-2)**.

### 🟠 P1 — Sprint tới (10 items)
Score 12-15. Strategic, đáng làm trong **wave 2 (tháng 1)**.

| # | Gap | Effort | Highlights |
|---|---|---|---|
| 1 | **Fix Ambassador withdraw commented logic** | 1 tuần (cần investigate intent) | ⚠️ Có thể là **WIP intentional** — phải clarify với PM trước khi fix |
| 2 | **Port auto-approve influencer + notification từ TCB → Ambassador** | 2 tuần | Tự động hóa onboarding creator |
| 3 | **Port reward V2 → vCreator** | 2-3 tuần | Cần migration data + 4 fields mới trong EventRaw |
| 9 | **Port `RecoverRecheckInProgress` cron Amb → TCB** | 3-5 ngày | Robustness sau crash |
| 10 | **Port `isSendNotification` flag Amb → TCB** | <1 ngày | Easy win — chống spam Telegram |
| 11 | **Email transactional (SendGrid)** từ TCB → vCr/Amb | 1 tuần | Nâng cấp UX (welcome, password reset, invite) |
| 13 | **Content moderation tools** (blacklist-keyword) từ TCB → vCr/Amb | 1 tuần | Compliance + brand safety |
| 15 | **ReconciliationSnapshot per crawl** từ TCB → vCr/Amb | 1-2 tuần | Anti-fraud audit trail |
| 16 | **Profile Review + Rating** từ TCB → vCr/Amb | 2 tuần | Brand-creator trust signal |
| 17 | **Upload avatar cache (MinIO)** từ TCB → vCr/Amb | 1 tuần | Tránh broken avatar khi URL social expire |
| 25 | **Staff root account** từ vCreator → TCB/Amb | <1 ngày | Easy win — phục vụ automation audit |
| 28 | **Unify multi-tenant Partner concept** | strategic, 1+ quý | Long-term refactor — cần design doc trước |

### 🟡 P2 — Backlog (6 items)
Score 8-11. Làm khi có resource.

| # | Gap | Lý do P2 |
|---|---|---|
| 6 | TCB Reconciliation engine port | Effort lớn (~1380 LOC + models + admin), business value chưa rõ với vCr/Amb |
| 7 | TCB Analytics Dashboard port | Frontend + backend đều phức tạp, cần stakeholder confirm có cần không |
| 14 | ContentImportTracking | Chỉ làm nếu vCr/Amb có nhu cầu bulk import |
| 18 | BudgetInfo struct migration TCB | Cosmetic improvement, không critical |
| 20 | Affiliate (Ambassador-only) | Không port được, document để stakeholder biết |
| 29-30 | Process improvement (load_data sync, telegram unify) | Không tính năng product, là DevOps task |

### ⚪ P3 — Defer/skip (5 items)
Score < 8. Chưa cần.

- Items #19, 21, 22, 23, 24, 26: features tied chặt business model riêng, **KHÔNG port được**. Document lại để stakeholder tham khảo.

---

## Top 5 Quick Wins (effort ≤ 1 ngày, impact cao)

| # | Gap | Effort | Lý do làm ngay |
|---|---|---|---|
| 4 | pfloat.RoundToOneDecimal backport | <1 ngày | Tránh bug rounding cash |
| 10 | isSendNotification flag (Amb→TCB) | <1 ngày | Stop spam Telegram |
| 25 | Staff root account (vCr→TCB/Amb) | <1 ngày | Audit automation flows |
| 5 | Audit ActorType backport | 1-2 ngày | Compliance + trace automation |
| 12 (partial) | Rate limit constants port | 2-3 ngày | Security — chống brute force |

→ **Tổng ~5-8 ngày dev** có thể clear được 5 quick wins, tăng đáng kể quality + security cả 3 sản phẩm.

---

## Top 5 Strategic Decisions (cần stakeholder)

Những item lớn cần **PM + tech lead + business** quyết định trước khi làm:

| # | Decision | Câu hỏi cần trả lời |
|---|---|---|
| 1 | **Reconciliation engine có port sang vCr/Amb không?** | vCr/Amb có cần workflow đối chiếu phức tạp không? Hay manual review qua admin là đủ? |
| 2 | **Analytics Dashboard có cần cho vCr/Amb không?** | Stakeholder vCr/Amb có yêu cầu dashboard executive không? Hay đang dùng tool BI khác? |
| 3 | **Multi-tenant Partner concept unify thế nào?** | Long-term roadmap có muốn 1 codebase chung không? Nếu có → cần migration plan lớn |
| 4 | **Ambassador withdraw: commented logic là intentional hay bug?** | Verify với business: Ambassador có dùng bank withdraw thật, hay chỉ commission qua external? |
| 5 | **Email transactional có cần cho vCr/Amb không?** | Có flow nào (welcome, password reset, invite) hiện đang miss email? UX impact đo được không? |

---

## Roadmap đề xuất (3 wave)

### Wave 1 — Tuần 1-2: Quick wins + critical fixes
- ~~pfloat.RoundToOneDecimal (P0 #4)~~ → **reclassified P2** 2026-05-07: campaign 2 sản phẩm khác chạy tiền to, không có case fractional
- ~~Audit ActorType backport (P0 #5)~~ → **reclassified P2** 2026-05-07: gap thật nhưng không cấp bách (TCB/Amb đã dùng root account audit, chỉ thiếu field metadata phân biệt). [Detail](./gaps/05-audit-actor-type.md)
- ✅ isSendNotification flag (P1 #10)
- ✅ Staff root account port (P1 #25)
- ~~⚠️ Investigate Ambassador withdraw bug (P1 #1)~~ — **đã verify 2026-05-07**: 3 dự án đều admin-driven runtime, có dead code endpoint. Reclassified P2 cleanup. [Detail](./gaps/01-ambassador-withdraw-bank-validation.md).

→ **Output**: 2 PR nhỏ, ~1-2 ngày dev tổng cộng. Cả 3 sản phẩm benefit.

### Wave 2 — Tháng 1: Security + audit trail
- 🔴 Rate limit OTP admin (P0 #12)
- 🔴 Budget alert system (P0 #8)
- 🟠 Email transactional (P1 #11)
- 🟠 RecoverRecheckInProgress cron (P1 #9)
- 🟠 ReconciliationSnapshot per crawl (P1 #15)

→ **Output**: 5 PR medium, ~3-4 tuần dev.

### Wave 3 — Quý 1: Strategic features
- 🟠 Auto-approve influencer + notification (P1 #2)
- 🟠 Profile Review + Rating port (P1 #16)
- 🟠 Reward V2 cho vCreator (P1 #3) — cần migration plan
- 🟠 Content moderation tools (P1 #13)
- 🟠 Upload avatar cache (P1 #17)

→ **Output**: 5 features lớn, ~2-3 tháng dev. Cần product roadmap align.

### Wave 4 — Strategic decisions (cần stakeholder)
- ❓ Reconciliation engine port (P2 #6)
- ❓ Analytics Dashboard port (P2 #7)
- ❓ Multi-tenant Partner unify (P1 #28)

→ Các item này **cần meeting + design doc** trước khi quyết định effort.

---

## Caveats

1. **Effort estimate** dựa trên LOC + complexity từ semantic diff, **chưa tính**:
   - Migration data (vd: reward V1→V2 cần migrate `EventRewardRaw` records)
   - Frontend impact (admin/dashboard UI changes)
   - Testing & QA
   - Stakeholder review cycles
   → Effort thực tế có thể **+50-100%**.

2. **Score subjective**: Business value và Risk score dựa trên đoán từ code analysis. Khuyên review với PM/business để align.

3. **Caveat lớn nhất — gap #1 Ambassador withdraw**: code đã commented, nhưng KHÔNG biết là **WIP đang phát triển** hay **intentional skip** (vì Ambassador dùng affiliate flow, commission qua external). Trước khi mark là bug → phải verify với business.

4. **Items "KHÔNG port được"** vẫn nằm trong roadmap để document — không phải để làm, mà để stakeholder biết lý do và chấp nhận difference vĩnh viễn.

---

## Liên kết với các tài liệu

- [README.md](./README.md) — index toàn bộ tài liệu
- [feature-comparison-matrix.md](./feature-comparison-matrix.md) — matrix file-level
- [services-detailed.md](./services-detailed.md) — LOC + functions per service
- 8 file [semantic-diff-*.md](./) — phân tích chi tiết từng group
