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
| 1 | **Withdraw cả 3 đều admin-driven thực tế, có dead code endpoint** — TCB/vCr có `POST /withdraw` + frontend service nhưng 0 caller pages. UI `/bank` chỉ hiển thị "Bạn chưa đến kỳ thanh toán". Đề xuất xóa endpoint sau khi verify không có client mobile/external. Reclassified P2→P3 (2026-05-10): user confirm "không cần làm, mà là dọn dẹp để tránh bug". [Detail](./gaps/p3/01-ambassador-withdraw-bank-validation.md) | Financial | Cleanup dead code 3 dự án | 2 | 1 | 4 | 4 | **11** | ⚪ P3 |
| 2 | **Khái niệm "Influencer Profile" — Ambassador BẮT BUỘC port, vCreator ĐỀ XUẤT port (chia sẻ creator pool)** — TCB có collection riêng + brand portal mạnh; Ambassador có scaffolding simplified (đọc từ user_social) + per-partner application flow + special channels (facebook_post, threads); vCreator không có concept. Reclassified P1→P0 (2026-05-07) sau khi user confirm business intent: Ambassador bắt buộc, vCreator để long-term chia sẻ creator pool. [Detail](./gaps/p0/02-influencer-profile-concept.md) | User & Auth | TCB → Ambassador (mandatory) + TCB → vCreator (recommended) | 5 | 4 | 2 | 5 | **16** | 🔴 P0 |
| 3 | ~~**vCreator dùng reward V1 (naive)**~~ — **gộp vào gap #8** (cùng scope: budget control + reward V2 engine cần làm chung 1 task). Xem [gap #8 detail](./gaps/p0/08-budget-alert-system.md) | Campaign & Event | (gộp #8) | - | - | - | - | - | (merged → #8) |
| 4 | **Float precision rounding chỉ vCreator có** (`pfloat.RoundToOneDecimal`) — TCB/Amb có thể bị bug làm tròn cash. Tuy nhiên 2 sản phẩm kia chạy campaign tiền to (không có fractional cents) → risk thực tế thấp. Reclassified P0→P2 (2026-05-07). User reconfirm P2 (2026-05-10): "cần làm nhưng chưa quá gấp". | Financial | vCreator → TCB/Amb | 2 | 2 | 5 | 2 | **11** | 🟡 P2 |
| 5 | **Audit ActorType field chỉ vCreator có** — Cả 3 dự án đều có flow dùng root account để audit, nhưng TCB/Amb không có field metadata phân biệt → query log không filter được automation vs manual. Reclassified P0→P2 (2026-05-07): không cấp bách, nice-to-have. User reconfirm P2 (2026-05-10): "cần làm nhưng chưa quá gấp" (tương tự #4). [Detail](./gaps/p2/05-audit-actor-type.md) | Reconciliation & Audit | vCreator → TCB/Amb | 3 | 2 | 5 | 4 | **14** | 🟡 P2 |
| 6 | ~~**TCB Reconciliation engine**~~ — **gộp vào gap #15** (cùng scope: snapshot + engine cần làm chung 1 task lớn). User confirm "đã eval kỹ ở TCB, ảnh hưởng nhiều lắm" → port full stack. Xem [gap #15 detail](./gaps/p1/15-reconciliation-engine-and-snapshot.md) | Reconciliation & Audit | (gộp #15) | - | - | - | - | - | (merged → #15) |
| 7 | **TCB Next.js Analytics Dashboard executive** (standalone app + 2855 LOC backend, ~10 sections) — TCB-only. vCr/Amb chỉ có dashboard cũ admin Umi (basic, vCr có filter 3 tầng workplace cải tiến hơn). Reclassified P2→P1 (2026-05-10) — user confirm strategic value sau khi clarify scope. [Detail](./gaps/p1/07-analytics-dashboard-port.md) | Analytics & Dashboard | TCB → vCr/Amb (strategic) | 4 | 3 | 1 | 4 | **12** | 🟠 P1 |
| 8 | **vCreator thiếu budget control system** — TCB và Ambassador GẦN NHƯ TƯƠNG ĐƯƠNG (3-level Bpe/Bpu/Bpc + block + threshold + Telegram alert), chỉ vCreator thiếu hoàn toàn → chi tiền không giới hạn. Reclassified direction port (2026-05-07) sau user catch. [Detail](./gaps/p0/08-budget-alert-system.md) | Campaign & Event | TCB hoặc Amb → vCreator | 5 | 4 | 3 | 4 | **16** | 🔴 P0 |
| 9 | **TCB và vCreator thiếu cơ chế bảo vệ khi tính lại reward cho content đã thay đổi trạng thái** — Ambassador có safety state + cron recovery. TCB partial implementation (field tồn tại, không dùng), vCreator không có gì. Reclassified P1→P2 (2026-05-07): risk thấp-trung bình, có workaround manual. [Detail](./gaps/p2/09-recheck-recovery-pattern.md) | Campaign & Event | Ambassador → TCB + vCreator | 3 | 3 | 3 | 4 | **13** | 🟡 P2 |
| 10 | **TCB và Ambassador dùng 2 cơ chế khác nhau để dedup Telegram alert** — TCB dùng cơ chế "khóa cứng campaign" (block toàn bộ reward calc), Ambassador dùng "khóa thông minh + cờ alert" (chỉ block submit, reward vẫn chạy). Cả 2 đều dedup OK (KHÔNG phải bug). Cần unify để 3 sản phẩm consistent — direction: TCB refactor theo pattern Ambassador. Reclassified scope (2026-05-07). [Detail](./gaps/p3/10-telegram-alert-deduplication.md) | Campaign & Event | Unify (TCB refactor theo Amb) | 2 | 2 | 3 | 4 | **11** | ⚪ P3 |
| 11 | **TCB có SendGrid legacy không dùng nữa** — initial assumption sai (nghĩ vCr/Amb thiếu email, thực ra cả 3 đều có SMTP). TCB còn SendGrid integration nhưng đã không dùng (legacy). Verified 2026-05-07: KHÔNG cần port, action đúng nếu có là xóa SendGrid khỏi TCB (cleanup). Note để dev tương lai biết, KHÔNG cần làm. | Infrastructure & Misc | (no action needed) | 1 | 1 | 5 | 1 | **8** | ⚪ P3 |
| 12 | **Security cho admin login (rate limit + audit)** — TCB có rate limit password attempts (7 lần/5 phút → block 2h) + audit log mọi login attempt + auth code exchange flow. vCr/Amb không có gì ở application layer. KHÔNG có OTP ở cả 3 (tên hàm `CheckRateLimitRequestOTP` chỉ là legacy naming). Reclassified P0→P3 (2026-05-07): vCr/Amb không phải target lớn, có thể defer | Infrastructure & Misc | TCB → vCr/Amb | 2 | 2 | 4 | 4 | **12** | ⚪ P3 |
| 13 | ~~**TCB blacklist-keyword + content moderation tools**~~ — sau verify scope thật là 4 features riêng biệt: (1) blacklist keyword check qua LLM — KHÔNG làm, đã thay bằng OpsHub. (2) auto-approve rule dựa trên score — KHÔNG làm, đã thay bằng OpsHub. (3) Sentiment analysis Senlyzer — KHÔNG làm, đã thay bằng OpsHub. (4) Bulk content import → tách thành **gap #31**. (5) Staff code validate → tách thành **gap #32**. Reduced to note only (2026-05-07). | Content & Media | (note only / split) | 1 | 1 | 5 | 1 | **8** | ⚪ P3 |
| 14 | ~~**TCB ContentImportTracking**~~ — Trùng với gap #31 (cùng concept bulk content import + tracking). Đã rescope thành **gap #31** với business overview chi tiết hơn. | Content & Media | (merged → #31) | - | - | - | - | - | (merged → #31) |
| 15 | **🔝 TOP P1 — vCreator/Ambassador thiếu hệ thống đối chiếu (reconciliation) tiền thưởng + audit trail crawl chống fraud** — Combined gap #6 + #15 (2026-05-07). vCr/Amb có 3 models cơ bản + admin page nhưng KHÔNG có 3 services chính + 3 models nâng cao + admin tools nâng cao. User confirm: "Cái này quan trọng, để ở P1 nhưng ở vị trí trên cùng luôn. Vì lúc làm TCB tôi đã đánh giá kỹ rồi, nó ảnh hưởng nhiều lắm." Port full stack 3 layers (snapshot + jobs + engine). [Detail](./gaps/p1/15-reconciliation-engine-and-snapshot.md) | Reconciliation & Audit | TCB → vCr/Amb (full stack) | 5 | 4 | 2 | 4 | **15** | 🟠 P1 (top) |
| 16 | **vCreator/Ambassador thiếu hệ thống đánh giá creator (review + rating)** — TCB có ProfileReview (5 tiêu chí) + RatingCache aggregate per-creator. vCr/Amb không có gì. **Phần tiếp nối của gap #2** — phải có InfluencerProfile trước để reference profile_id. Position: sau #15, trước #31. [Detail](./gaps/p1/16-profile-review-rating.md) | Targeting & Matching | TCB → vCr/Amb (sau gap #2) | 4 | 3 | 2 | 4 | **13** | 🟠 P1 |
| 17 | **vCreator/Ambassador có thể bị broken avatar khi URL social expire** — TCB cache về MinIO permanent + resize 3 sizes. vCr/Amb dùng URL social trực tiếp (TikTok/Google/FB có expire). Infrastructure (MinIO + resizeimage) đã có sẵn ở vCr/Amb, chỉ thiếu service layer. Reclassified P1→P2 (2026-05-07): risk theory chứ không phải bug active. [Detail](./gaps/p2/17-upload-avatar-cache.md) | Content & Media | TCB → vCr/Amb | 3 | 3 | 4 | 4 | **14** | 🟡 P2 |
| 18 | **TCB BudgetInfo struct (vs Ambassador) — pre-compute UsedPercent** — Ambassador có `BudgetInfo{Total,Used,Remain,UsedPercent}` pre-compute sẵn, TCB rải flat fields phải tính % mỗi request, vCr không có budget. Reclassified P2→P1 (2026-05-10): **liên quan #8** — làm chung lúc port budget control system sang vCr (cùng refactor BudgetInfo cho cả 3 sản phẩm consistent). | Campaign & Event | Ambassador → TCB + vCr (gắn theo #8) | 2 | 2 | 4 | 4 | **12** | 🟠 P1 |
| 19 | **vCreator Extended Period mode** — cho phép content post sau event endAt được ghi nhận với ngày map về kỳ kế toán cũ. TCB/Amb không có. Reclassified P3→P2 (2026-05-10): user confirm cần giữ trong backlog, feature có business value rõ (kỳ kế toán linh hoạt). [Detail](./gaps/p2/19-vcreator-extended-period-mode.md) | Campaign & Event | vCreator → TCB/Amb (selective, cần product confirm) | 3 | 2 | 4 | 4 | **13** | 🟡 P2 |
| 20 | **Affiliate suite (campaign + contract + links + tracking)** — Ambassador có (~1275 LOC mature, pub2). vCreator **đang làm** (~951 LOC active dev, Scalef API — verified bằng git log). TCB chưa có, **chờ chốt sale**. Reclassified P2→P1 (2026-05-10): có active development + sales-driven blocker. [Detail](./gaps/p1/20-ambassador-affiliate-suite.md) | Infrastructure | Amb → vCr (đang làm) → TCB (sau chốt sale) | 5 | 3 | 1 | 5 | **14** | 🟠 P1 |
| 21 | **Ambassador Mission/Gamification system** — Hệ thống nhiệm vụ + thưởng + level (~1327 LOC, hashtag check + view threshold + time window). Tên gốc "WildRift" từ partner Wild Rift game. TCB/vCr không có. Reclassified P3→P2 (2026-05-10): user confirm giữ trong backlog cho khi có khách hàng gamification/loyalty. [Detail](./gaps/p2/21-ambassador-mission-gamification.md) | Content & Media | Ambassador → vCr/TCB (selective, cần product confirm) | 3 | 2 | 3 | 4 | **12** | 🟡 P2 |
| 22 | ~~**vCreator Workplace 3-tier (Brand→Company→Unit)**~~ — Trùng scope với gap #32 (mã nhân viên + binding partner cần workplace để bind). Workplace là dependency/component của #32. Reclassified 2026-05-10: gộp vào gap #32. | User & Auth | (merged → #32) | - | - | - | - | - | (merged → #32) |
| 23 | ~~**vCreator registry_match HR engine**~~ — Reclassified 2026-05-07: KHÔNG phải vCreator-specific, là pattern tốt cần port. Đã rescope thành **gap #32** với business intent rõ. | Targeting & Matching | (rescoped → #32) | - | - | - | - | - | (merged → #32) |
| 24 | **TCB Campaign matching engine + filtered_campaigns** — AI-assisted creator selection (multi-dim scoring + AT-Core integration). TCB **đang phát triển dang dở** (~786 LOC active dev). vCr/Amb không có. Reclassified P3→P1 (2026-05-10): TCB chưa hoàn thiện nhưng làm xong cần port ngay sang vCr/Amb (strategic priority). [Detail](./gaps/p1/24-tcb-campaign-matching-engine.md) | Campaign & Event | TCB (đang dang dở) → vCr/Amb (port sau khi stable) | 4 | 3 | 2 | 5 | **14** | 🟠 P1 |
| 25 | **TCB/Ambassador không có helper `GetRoot()` cho staff root account** — vCreator có helper với filter active + warning multi-root + sort. TCB/Amb dùng raw bson query inline ở `opshub_webhook.go`. Reclassified P1→P3 (2026-05-07): tech debt cleanup, không có business impact. [Detail](./gaps/p3/25-staff-root-account-helper.md) | Infrastructure & Misc | vCreator → TCB/Amb | 1 | 1 | 5 | 4 | **11** | ⚪ P3 |
| 26 | **TCB transcript scoring (LLM)** vs vCr/Amb — Có khác biệt nhưng không cần gộp/port: cả 3 sản phẩm đã có **OpsHub** thay thế cho content scoring/moderation. Note only. | Content & Media | (note only — OpsHub đã thay) | - | - | - | - | - | ⚪ P3 |
| 27 | **Ambassador chưa có user_social_partner config check** (comment "not yet ported") — duplicate với gap #2 | User & Auth | (gộp với #2) | - | - | - | - | - | - |
| 28 | **Multi-tenant Partner concept khác nhau 3 sản phẩm** — Architectural debt, không port. Note only. | User & Auth | (note only — không port) | - | - | - | - | - | ⚪ P3 |
| 29 | ~~**`load_data.go` synced TCB↔Ambassador chưa có process**~~ — Dropped 2026-05-10: chỉ là master reference data (file JSON tĩnh demographic.json để dropdown UI), KHÔNG liên quan gì đến features chính. Không gộp được với #2 (InfluencerProfile audience demographic là feature khác hoàn toàn). | Infrastructure & Misc | (dropped — invalid gap) | - | - | - | - | - | (removed) |
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

### 🟠 P1 — Sprint tới (8 items, sau khi reclassify #25→P3, #28→P3, #07 P2→P1, #18 P2→P1, #20 P2→P1, #24 P3→P1 — 2026-05-10)

**🔝 Top P1**: Gap #15 (Reconciliation engine + snapshot, gộp #6+#15) — user confirm là quan trọng nhất, port full stack (~5-7 tuần mỗi sản phẩm).
Score 12-15. Strategic, đáng làm trong **wave 2 (tháng 1)**.

| # | Gap | Effort | Highlights |
|---|---|---|---|
| 15 | **Reconciliation engine + snapshot per crawl** từ TCB → vCr/Amb (gộp #6+#15) | 5-7 tuần mỗi sản phẩm | 🔝 Top P1 — anti-fraud + audit trail full stack |
| 16 | **Profile Review + Rating** từ TCB → vCr/Amb | 2 tuần | Brand-creator trust signal — phần tiếp nối #2 |
| 31 | **Admin proxy creator flow** TCB → vCr/Amb (selective) | 2-3 tuần | Admin tạo creator + import content giúp họ |
| 32 | **Mã nhân viên + binding partner** vCreator → Amb (full) + vCr → TCB (extend) | 3-4 tuần | EmployeeRegistry 18 fields + match engine |
| 7 | **TCB Next.js Dashboard executive** → vCr/Amb | 4-6 tuần mỗi sản phẩm | Executive view ~10 sections, cần stakeholder confirm. Note: dashboard cũ admin Umi vCr có filter 3 tầng workplace cải tiến hơn |
| 18 | **BudgetInfo struct unify** Amb → TCB + vCr | <1 ngày backend | **Liên quan #8** — làm chung lúc port budget sang vCr. Pre-compute UsedPercent cho dashboard nhanh + 3 sản phẩm consistent |
| 20 | **Affiliate suite** Amb (mature) → vCr (đang làm) → TCB (chờ chốt sale) | 6-8 tuần TCB sau khi chốt sale | vCr active dev với Scalef API, TCB blocker ở sales |
| 24 | **Campaign matching engine** TCB (dang dở) → vCr/Amb (sau khi TCB stable) | TCB stable 2-3 tuần + vCr/Amb mỗi cái 3-4 tuần | AI-assisted creator selection, AT-Core integration |

### 🟡 P2 — Backlog (8 items, sau khi #7 #18 #20 lên P1, #1 xuống P3, #19 #21 P3→P2, #29 dropped)
Score 8-11. Làm khi có resource.

| # | Gap | Lý do P2 |
|---|---|---|
| 6 | TCB Reconciliation engine port | Effort lớn (~1380 LOC + models + admin), business value chưa rõ với vCr/Amb |
| 14 | ContentImportTracking | Chỉ làm nếu vCr/Amb có nhu cầu bulk import |
| 30 | Telegram alert infrastructure unify | Không tính năng product, là DevOps task |

### ⚪ P3 — Defer/skip

Score < 8 hoặc note-only.

**Note-only (không port — features đặc thù business hoặc đã được thay thế)**:
- #11 SendGrid legacy (TCB cleanup, không port)
- #13 blacklist-keyword + content moderation (OpsHub đã thay)
- #26 TCB transcript scoring LLM (OpsHub đã thay)
- #28 Multi-tenant Partner concept (architectural debt, không port)

**Có file detail (defer port)**:
- #1 Withdraw dead code cleanup
- #10 Telegram alert dedup
- #12 Admin login security
- #25 Staff root account helper

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
