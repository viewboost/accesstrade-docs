# Tổng hợp Estimate Dự án CRM AccessTrade

> **Nguồn dữ liệu:** [tasks.csv](./tasks.csv) — 131 task chi tiết
> **Đơn vị:** giờ công (person-hours), 1 person-day = 8h
> **Phạm vi:** Toàn bộ 4 phase + Setup + QA + PM/BA/Design

---

## Tổng quan

| Chỉ số | Giá trị |
|---|---|
| Tổng số task | 131 |
| Tổng effort | **3.590 giờ** ≈ **449 person-days** |
| Quy đổi tháng người (22 ngày làm việc) | ~20.4 person-months |
| Số phase chính | 4 (Phase 0, 1A, 1B, 2) + Setup + QA + PM/BA/Design |
| Task bị block | 3 (chờ Zalo OA, ambassador API, legal) |

---

## Estimate theo Phase

| Phase | Tasks | DevOps | SA | BE | FE Creator | FE Admin | QC | Design | BA | PM | Tổng giờ | Person-days |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Setup & Infrastructure | 10 | 65 | 10 | 13 | 3 | 3 | 4 | 0 | 0 | 9 | 107 | 13 |
| Foundation (Multi-tenant + Auth) | 5 | 0 | 10 | 84 | 4 | 40 | 14 | 3 | 7 | 8 | 170 | 21 |
| Phase 0 — Event Portal | 10 | 0 | 6 | 76 | 84 | 16 | 21 | 43 | 10 | 8 | 264 | 33 |
| Phase 1A — CRM MVP | 28 | 0 | 25 | 328 | 0 | 280 | 72 | 21 | 30 | 33 | 789 | 99 |
| Phase 1B — VIP Layer | 21 | 8 | 17 | 258 | 0 | 144 | 46 | 12 | 23 | 24 | 532 | 66 |
| Phase 2 — Sourcing Engine | 34 | 6 | 31 | 440 | 4 | 164 | 69 | 12 | 34 | 38 | 798 | 100 |
| QA & Launch (toàn dự án) | 15 | 54 | 6 | 50 | 16 | 24 | 180 | 3 | 12 | 39 | 384 | 48 |
| PM / BA / Design (toàn dự án) | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 288 | 80 | 178 | 546 | 68 |
| **TỔNG** | **131** | **133** | **105** | **1.249** | **111** | **671** | **406** | **382** | **196** | **337** | **3.590** | **449** |

---

## Estimate theo Vai trò

| Vai trò | Tổng giờ | Person-days | % tổng |
|---|---:|---:|---:|
| Backend (BE) | 1.249 | 156 | 34.8% |
| FE Admin | 671 | 84 | 18.7% |
| QC | 406 | 51 | 11.3% |
| Design | 382 | 48 | 10.6% |
| PM | 337 | 42 | 9.4% |
| BA | 196 | 25 | 5.5% |
| DevOps | 133 | 17 | 3.7% |
| FE Creator | 111 | 14 | 3.1% |
| SA (Solution Architect) | 105 | 13 | 2.9% |
| **TỔNG** | **3.590** | **449** | **100%** |

---

## Chi tiết từng Phase

### 1. Setup & Infrastructure — 107h (13 pd)
**10 tasks P0** • DevOps-heavy (65h) • Mục đích: dựng nền tảng AWS, MongoDB multi-tenant, Redis, MinIO, CI/CD, monitoring trước khi bất kỳ feature nào start.

### 2. Foundation — 170h (21 pd)
**5 tasks P0** • Multi-tenant data model + Auth/RBAC + Tenant onboarding + Audit log. Đây là khối nền của toàn bộ CRM, mọi module Phase 1A/1B/2 đều phụ thuộc.

### 3. Phase 0 — Event Portal — 264h (33 pd)
**10 tasks P0** • Đặc thù: FE Creator chiếm 84h (landing + register + welcome + profile card cho event 7/5/2026). Đây là deliverable đầu tiên có hạn cứng.

### 4. Phase 1A — CRM MVP — 789h (99 pd)
**28 tasks P0** chia 7 module:
- **M1 Identity** (191h) — Creator master data, list, 360 page, import
- **M2 Lifecycle** (113h) — State machine 7 giai đoạn V2, auto-transition
- **M5 Owner** (69h) — Assignment + workload dashboard
- **M6 Task Console** (117h) — Queue tác vụ + actions
- **M7 Communication** (160h) — Zalo OA + Email + template (1 task blocked chờ Zalo approval)
- **M13 Multi-tenant UI** (75h) — Per-tenant config + brand portal
- **M14 Notification** (64h) — In-app + email + preferences

### 5. Phase 1B — VIP Layer — 532h (66 pd)
**21 tasks P1** chia 6 module:
- **M3 Tier Scoring** (100h) — 5 dimensions + tier mapping
- **M4 SLA Timer** (93h) — Engine + escalation + dashboard
- **M10 Sync** (55h) — Pull GMV từ ambassador (blocked chờ API spec)
- **M11 Care Insights** (70h) — Drop detection + plays
- **M15 Reporting** (128h) — Data warehouse + dashboard + export async
- **M16 Relationship Vault** (86h) — Anti-poach + offboarding ceremony

### 6. Phase 2 — Sourcing Engine — 798h (100 pd)
**34 tasks P2** chia 7 lớp:
- **L1 Ingestion** (92h) — Tích hợp Metric POC + Threads scraper + filter
- **L2 Enrichment** (61h) — Influence-meter enrich + brand-safety
- **L3 Scoring** (133h) — Score 5 tiêu chí + classifier + ML retrain
- **L4 Sourcing Inbox** (100h) — Approval cascade UI
- **L5 Outreach** (157h) — Zalo OA throttling + warm-up + suppression + A/B
- **L6 BD Request** (118h) — Form + AI suggest + cross-BD coord
- **L7 Attribution** (137h) — UTM + funnel + analytics + brand report + ML feedback

### 7. QA & Launch — 384h (48 pd)
**15 tasks** • QC chiếm 180h • Bao gồm smoke test 4 phase, multi-tenant security test, Zalo spam-flag test (blocked), load test, accessibility, UAT, deploy 4 lần, post-launch monitoring 4 tuần.

### 8. PM / BA / Design — 546h (68 pd)
**8 tasks xuyên suốt:**
- Discovery + requirements (BA, 40h)
- Mockup design system + 4 phase mockups (Design, 288h)
- Sprint planning + standup + report (PM, 96h)
- Stakeholder communication AT (PM, 48h)

---

## Phân bổ theo độ ưu tiên

| Priority | Tasks | Tổng giờ | Person-days | Khi nào |
|---|---:|---:|---:|---|
| P0 (must-have, MVP) | 71 | ~1.879h | ~235 pd | Setup + Foundation + Phase 0 + Phase 1A + QA core |
| P1 (VIP, hậu MVP) | 19 | ~620h | ~78 pd | Phase 1B (sau khi MVP go-live) |
| P2 (Sourcing) | 34 | ~798h | ~100 pd | Phase 2 (giai đoạn cuối) |
| Cross-phase (PM/Design/QA shared) | 7 | ~293h | ~36 pd | Xuyên suốt 4 phase |

---

## Timeline gợi ý theo phase

Giả định team chuẩn (1 PM, 1 BA, 1-2 SA, 3-4 BE, 2 FE, 1 DevOps, 2 QC, 1 Design):

| Phase | Effort (pd) | Thời gian (tuần) | Mốc deliverable |
|---|---:|---:|---|
| Setup + Foundation | 34 | Tuần 1-3 | Hạ tầng + multi-tenant ready |
| Phase 0 Event | 33 | Tuần 3-5 | **Sự kiện 7/5/2026** |
| Phase 1A CRM MVP | 99 | Tuần 5-10 | CRM go-live cho TCB |
| Phase 1B VIP | 66 | Tuần 10-13 | VIP layer + reporting |
| Phase 2 Sourcing | 100 | Tuần 13-17 | Outbound creator pipeline |
| QA + UAT + Launch | 48 (chia đều) | Xuyên suốt | 4 lần deploy prod |
| PM/BA/Design | 68 (chia đều) | Xuyên suốt | Discovery → mockup → ceremonies |

**Tổng thời gian:** 16-17 tuần (4 tháng) trùng với roadmap đã pitched.

---

## Rủi ro effort cần lưu ý

1. **M7-02 Zalo OA integration (42h)** — Blocked chờ Zalo OA Business approval, có thể delay 2-4 tuần. Ảnh hưởng dây chuyền tới L5 Outreach (157h Phase 2).
2. **L3 Scoring + ML retrain (32h)** — Phụ thuộc chất lượng dữ liệu Metric POC, có thể cần thêm effort tinh chỉnh.
3. **Contract/Legal Phase 1B** — Chưa estimate riêng (phụ thuộc legal partner cung cấp template). Có thể phát sinh 30-50h.
4. **Multi-tenant data isolation (FOUND-01 + M13-02)** — Critical security, nếu fail tests có thể phát sinh 20-40h refactor.
5. **PM/BA/Design effort (546h)** — Estimate dựa trên dự án cùng quy mô; có thể overshoot 20-30% nếu requirements thay đổi liên tục.

---

## Buffer khuyến nghị

- **Contingency 15%** cho unknown unknowns: ~540h thêm → tổng ~4.130h ≈ 516 person-days
- **Bug fix post-launch:** đã include trong QA-15 (66h), có thể cần thêm cho từng phase
- **Knowledge transfer + documentation:** chưa estimate riêng, có thể add ~80h cuối dự án

---

## Tài liệu liên quan

- [tasks.csv](./tasks.csv) — chi tiết 131 task theo từng vai trò
- [README.md](./README.md) — overview dự án + 4 phase
- [phase-0-event/](./phase-0-event/) — module docs Event Portal
- [phase-1a-crm-mvp/](./phase-1a-crm-mvp/) — module docs CRM MVP
- [phase-1b-vip/](./phase-1b-vip/) — module docs VIP Layer
- [phase-2-sourcing/](./phase-2-sourcing/) — layer docs Sourcing Engine
