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
| 1 | **Withdraw cả 3 đều admin-driven thực tế, có dead code endpoint** — TCB/vCr có `POST /withdraw` + frontend service nhưng 0 caller pages. UI `/bank` chỉ hiển thị "Bạn chưa đến kỳ thanh toán". Đề xuất xóa endpoint sau khi verify không có client mobile/external. [Detail](./gaps/p2/01-ambassador-withdraw-bank-validation.md) | Financial | Cleanup dead code 3 dự án | 2 | 1 | 4 | 4 | **11** | 🟡 P2 |
| 2 | **Khái niệm "Influencer Profile" — Ambassador BẮT BUỘC port, vCreator ĐỀ XUẤT port (chia sẻ creator pool)** — TCB có collection riêng + brand portal mạnh; Ambassador có scaffolding simplified (đọc từ user_social) + per-partner application flow + special channels (facebook_post, threads); vCreator không có concept. Reclassified P1→P0 (2026-05-07) sau khi user confirm business intent: Ambassador bắt buộc, vCreator để long-term chia sẻ creator pool. [Detail](./gaps/p0/02-influencer-profile-concept.md) | User & Auth | TCB → Ambassador (mandatory) + TCB → vCreator (recommended) | 5 | 4 | 2 | 5 | **16** | 🔴 P0 |
| 3 | ~~**vCreator dùng reward V1 (naive)**~~ — **gộp vào gap #8** (cùng scope: budget control + reward V2 engine cần làm chung 1 task). Xem [gap #8 detail](./gaps/p0/08-budget-alert-system.md) | Campaign & Event | (gộp #8) | - | - | - | - | - | (merged → #8) |
| 4 | **Float precision rounding chỉ vCreator có** (`pfloat.RoundToOneDecimal`) — TCB/Amb có thể bị bug làm tròn cash. Tuy nhiên 2 sản phẩm kia chạy campaign tiền to (không có fractional cents) → risk thực tế thấp. Reclassified P0→P2 (2026-05-07) | Financial | vCreator → TCB/Amb | 2 | 2 | 5 | 2 | **11** | 🟡 P2 |
| 5 | **Audit ActorType field chỉ vCreator có** — Cả 3 dự án đều có flow dùng root account để audit, nhưng TCB/Amb không có field metadata phân biệt → query log không filter được automation vs manual. Reclassified P0→P2 (2026-05-07): không cấp bách, nice-to-have. [Detail](./gaps/p2/05-audit-actor-type.md) | Reconciliation & Audit | vCreator → TCB/Amb | 3 | 2 | 5 | 4 | **14** | 🟡 P2 |
| 6 | ~~**TCB Reconciliation engine**~~ — **gộp vào gap #15** (cùng scope: snapshot + engine cần làm chung 1 task lớn). User confirm "đã eval kỹ ở TCB, ảnh hưởng nhiều lắm" → port full stack. Xem [gap #15 detail](./gaps/p1/15-reconciliation-engine-and-snapshot.md) | Reconciliation & Audit | (gộp #15) | - | - | - | - | - | (merged → #15) |
| 7 | **TCB Analytics Dashboard** (Next.js, 2226 LOC backend) — TCB-only. vCr/Amb không có dashboard executive view | Analytics & Dashboard | TCB → vCr/Amb (strategic) | 4 | 2 | 1 | 3 | **10** | 🟡 P2 |
| 8 | **vCreator thiếu budget control system** — TCB và Ambassador GẦN NHƯ TƯƠNG ĐƯƠNG (3-level Bpe/Bpu/Bpc + block + threshold + Telegram alert), chỉ vCreator thiếu hoàn toàn → chi tiền không giới hạn. Reclassified direction port (2026-05-07) sau user catch. [Detail](./gaps/p0/08-budget-alert-system.md) | Campaign & Event | TCB hoặc Amb → vCreator | 5 | 4 | 3 | 4 | **16** | 🔴 P0 |
| 9 | **TCB và vCreator thiếu cơ chế bảo vệ khi tính lại reward cho content đã thay đổi trạng thái** — Ambassador có safety state + cron recovery. TCB partial implementation (field tồn tại, không dùng), vCreator không có gì. Reclassified P1→P2 (2026-05-07): risk thấp-trung bình, có workaround manual. [Detail](./gaps/p2/09-recheck-recovery-pattern.md) | Campaign & Event | Ambassador → TCB + vCreator | 3 | 3 | 3 | 4 | **13** | 🟡 P2 |
| 10 | **TCB và Ambassador dùng 2 cơ chế khác nhau để dedup Telegram alert** — TCB dùng cơ chế "khóa cứng campaign" (block toàn bộ reward calc), Ambassador dùng "khóa thông minh + cờ alert" (chỉ block submit, reward vẫn chạy). Cả 2 đều dedup OK (KHÔNG phải bug). Cần unify để 3 sản phẩm consistent — direction: TCB refactor theo pattern Ambassador. Reclassified scope (2026-05-07). [Detail](./gaps/p3/10-telegram-alert-deduplication.md) | Campaign & Event | Unify (TCB refactor theo Amb) | 2 | 2 | 3 | 4 | **11** | ⚪ P3 |
| 11 | **TCB có SendGrid legacy không dùng nữa** — initial assumption sai (nghĩ vCr/Amb thiếu email, thực ra cả 3 đều có SMTP). TCB còn SendGrid integration nhưng đã không dùng (legacy). Verified 2026-05-07: KHÔNG cần port, action đúng nếu có là xóa SendGrid khỏi TCB (cleanup). Note để dev tương lai biết, KHÔNG cần làm. | Infrastructure & Misc | (no action needed) | 1 | 1 | 5 | 1 | **8** | ⚪ P3 |
| 12 | **Security cho admin login (rate limit + audit)** — TCB có rate limit password attempts (7 lần/5 phút → block 2h) + audit log mọi login attempt + auth code exchange flow. vCr/Amb không có gì ở application layer. KHÔNG có OTP ở cả 3 (tên hàm `CheckRateLimitRequestOTP` chỉ là legacy naming). Reclassified P0→P3 (2026-05-07): vCr/Amb không phải target lớn, có thể defer | Infrastructure & Misc | TCB → vCr/Amb | 2 | 2 | 4 | 4 | **12** | ⚪ P3 |
| 13 | ~~**TCB blacklist-keyword + content moderation tools**~~ — sau verify scope thật là 4 features riêng biệt: (1) blacklist keyword check qua LLM — KHÔNG làm, đã thay bằng OpsHub. (2) auto-approve rule dựa trên score — KHÔNG làm, đã thay bằng OpsHub. (3) Sentiment analysis Senlyzer — KHÔNG làm, đã thay bằng OpsHub. (4) Bulk content import → tách thành **gap #31**. (5) Staff code validate → tách thành **gap #32**. Reduced to note only (2026-05-07). | Content & Media | (note only / split) | 1 | 1 | 5 | 1 | **8** | ⚪ P3 |
| 14 | ~~**TCB ContentImportTracking**~~ — Trùng với gap #31 (cùng concept bulk content import + tracking). Đã rescope thành **gap #31** với business overview chi tiết hơn. | Content & Media | (merged → #31) | - | - | - | - | - | (merged → #31) |
| 15 | **🔝 TOP P1 — vCreator/Ambassador thiếu hệ thống đối chiếu (reconciliation) tiền thưởng + audit trail crawl chống fraud** — Combined gap #6 + #15 (2026-05-07). vCr/Amb có 3 models cơ bản + admin page nhưng KHÔNG có 3 services chính + 3 models nâng cao + admin tools nâng cao. User confirm: "Cái này quan trọng, để ở P1 nhưng ở vị trí trên cùng luôn. Vì lúc làm TCB tôi đã đánh giá kỹ rồi, nó ảnh hưởng nhiều lắm." Port full stack 3 layers (snapshot + jobs + engine). [Detail](./gaps/p1/15-reconciliation-engine-and-snapshot.md) | Reconciliation & Audit | TCB → vCr/Amb (full stack) | 5 | 4 | 2 | 4 | **15** | 🟠 P1 (top) |
| 16 | **TCB Profile Review + Rating** (627 LOC) — vCr/Amb không có concept rating creator → brand không có signal trust | Targeting & Matching | TCB → vCr/Amb | 4 | 3 | 2 | 4 | **13** | 🟠 P1 |
| 17 | **TCB upload_avatar_social** (cache MinIO) — vCr/Amb dùng URL social trực tiếp → URL có thể expire, broken avatar | Content & Media | TCB → vCr/Amb | 3 | 4 | 3 | 4 | **14** | 🟠 P1 |
| 18 | **TCB BudgetInfo struct (vs Ambassador)** — Ambassador đã có pre-compute UsedPercent giúp dashboard query nhanh, TCB chưa | Campaign & Event | Ambassador → TCB | 2 | 2 | 4 | 1 | **9** | 🟡 P2 |
| 19 | **vCreator Extended Period mode** — feature đặc thù single-brand, TCB/Amb không có | Campaign & Event | KHÔNG port (vCreator-specific) | 2 | 1 | 1 | 1 | **5** | ⚪ P3 |
| 20 | **Ambassador Affiliate suite** (campaign + contract + links + mapping) — Ambassador-only, KHÔNG port được | Infrastructure | KHÔNG port | 5 | 1 | 1 | 1 | **8** | 🟡 P2 |
| 21 | **Ambassador Mission/WildRift gamification** — Ambassador-specific business model | Content & Media | KHÔNG port | 2 | 1 | 1 | 1 | **5** | ⚪ P3 |
| 22 | **vCreator Workplace 3-tier (Brand→Company→Unit)** — vCreator-specific B2B onboarding | User & Auth | KHÔNG port | 2 | 1 | 1 | 1 | **5** | ⚪ P3 |
| 23 | ~~**vCreator registry_match HR engine**~~ — Reclassified 2026-05-07: KHÔNG phải vCreator-specific, là pattern tốt cần port. Đã rescope thành **gap #32** với business intent rõ. | Targeting & Matching | (rescoped → #32) | - | - | - | - | - | (merged → #32) |
| 24 | **TCB Campaign matching engine + filtered_campaigns** — TCB flagship feature riêng (T-Fluencers) | Campaign & Event | KHÔNG port | 4 | 1 | 1 | 1 | **7** | ⚪ P3 |
| 25 | **vCreator Staff root account** — utility cho automation flows, có thể backport | Infrastructure & Misc | vCreator → TCB/Amb | 2 | 2 | 5 | 4 | **13** | 🟠 P1 |
| 26 | **TCB transcript scoring (LLM-based)** vs vCr/Amb (Senlyzer sentiment) — không thể chia sẻ service, business model khác | Content & Media | KHÔNG port | 3 | 2 | 1 | 1 | **7** | ⚪ P3 |
| 27 | **Ambassador chưa có user_social_partner config check** (comment "not yet ported") — duplicate với gap #2 | User & Auth | (gộp với #2) | - | - | - | - | - | - |
| 28 | **Multi-tenant Partner concept khác nhau 3 sản phẩm** — TCB partner / vCr workplace / Amb Partner — long-term cần unify | User & Auth | Strategic decision | 3 | 3 | 1 | 5 | **12** | 🟠 P1 |
| 29 | **`load_data.go` synced TCB↔Ambassador chưa có process** — đang copy thủ công khi update, dễ drift | Infrastructure & Misc | Process improvement | 2 | 3 | 4 | 2 | **11** | 🟡 P2 |
| 30 | **TCB telegram alert có dùng** — Ambassador đã có nhưng label `[Ambassador]`, chưa unify infrastructure | Campaign & Event | Process improvement | 2 | 2 | 4 | 2 | **10** | 🟡 P2 |
| 31 | **TCB cho phép admin tạo creator + import content giúp họ; vCreator/Ambassador không có** — TCB có flow 3 bước (CreateUser admin với flag IsCreateByAdmin → CreateUserSocial → ImportContent + tracking). vCr không có gì. Amb có CreateUser nhưng cho referral seed, khác mục đích. Rescoped + reclassified P2→P1 2026-05-07. [Detail](./gaps/p1/31-admin-proxy-creator-flow.md) | Content & Media | TCB → vCr/Amb (selective) | 4 | 3 | 2 | 4 | **13** | 🟠 P1 |
| 33 | **Ambassador có cơ chế "tạo user giả để reserve referral code", TCB và vCreator không có** — admin có thể reserve referral code cho campaign promotion. User thật register với code này → attach inviter relation. TCB/vCr cùng có `Referral.Codes` model nhưng không có flow admin tạo seed user. Phát hiện khi verify gap #31 (2026-05-07). [Detail](./gaps/p2/33-ambassador-referral-seed-user.md) | User & Auth | Ambassador → TCB/vCr | 3 | 2 | 4 | 4 | **13** | 🟡 P2 |
| 32 | **Concept "mã nhân viên + binding partner" — TCB đơn giản, vCreator chi tiết hơn nhiều, Ambassador chưa có** — vCreator EmployeeRegistry 18 fields + match engine 10 ChangeActions là source of truth. TCB chỉ ManageCode 9 fields. Ambassador không có. Tách từ gap #13 + revoke gap #23 P3 + reclassified P2→P1 (2026-05-07). [Detail](./gaps/p1/32-staff-code-employee-binding.md) | User & Auth | vCreator → Amb (port full) + vCreator → TCB (extend) | 4 | 3 | 3 | 5 | **15** | 🟠 P1 |

---

## Priority breakdown

### 🔴 P0 — Làm ngay (2 items, sau khi reclassify 2026-05-07)
Score ≥ 16. Ưu tiên cao nhất do **easy win + cross-product impact lớn** hoặc **critical risk** hoặc **business intent rõ ràng**.

| # | Gap | Effort | Impact |
|---|---|---|---|
| 8 | **Budget control + Reward V2 engine** — port từ Ambassador → vCreator (TCB và Amb đã có) | 2-3 tuần | vCreator hiện chi tiền không giới hạn + race condition khi nhiều creator submit (revenue protection) |
| 2 | **InfluencerProfile concept** — port TCB → Ambassador (mandatory) + TCB → vCreator (recommended) | 6-8 tuần (2 phases) | Ambassador feature parity TCB; long-term chia sẻ creator pool 3 sản phẩm |

→ **Tổng effort**: gap #8 nhỏ (1 sprint), gap #2 lớn (>1 quý) — chia phases triển khai.

**Note**:
- Gap #12 (Security cho admin login) ban đầu là P0 — sau khi verify hết picture (KHÔNG có OTP ở 3 dự án, chỉ rate limit password attempts) → reclassified P3 vì vCr/Amb không phải target tấn công lớn.
- Gap #2 ban đầu P1 (auto-approve influencer + notification) → rescoped thành gap kiến trúc → reclassified P0 sau khi user confirm business intent "creator pool unification".

### 🟠 P1 — Sprint tới (7 items, sau khi gộp #3→#8, #6→#15, reclassify #9→P2, #10→P3, #11→P3, #13→note, #15 top P1, #31+#32 lên P1 — 2026-05-07)

**🔝 Top P1**: Gap #15 (Reconciliation engine + snapshot) — user confirm là quan trọng nhất, port full stack (~5-7 tuần mỗi sản phẩm).
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
- ~~Audit ActorType backport (P0 #5)~~ → **reclassified P2** 2026-05-07: gap thật nhưng không cấp bách (TCB/Amb đã dùng root account audit, chỉ thiếu field metadata phân biệt). [Detail](./gaps/p2/05-audit-actor-type.md)
- ✅ isSendNotification flag (P1 #10)
- ✅ Staff root account port (P1 #25)
- ~~⚠️ Investigate Ambassador withdraw bug (P1 #1)~~ — **đã verify 2026-05-07**: 3 dự án đều admin-driven runtime, có dead code endpoint. Reclassified P2 cleanup. [Detail](./gaps/p2/01-ambassador-withdraw-bank-validation.md).

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
