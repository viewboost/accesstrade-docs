# Gap Detail Files — Organized by Priority

> Mỗi gap được phân tích chi tiết trong 1 file riêng theo format chuẩn (TL;DR → 5-layer verify → action items → lịch sử phân loại).
> Source overview: [../gap-analysis-priority.md](../gap-analysis-priority.md)

## Cấu trúc folder

```
gaps/
├── README.md           ← bạn đang ở đây
├── p0/                 ← Làm ngay (score ≥16)
├── p1/                 ← Sprint tới (score 12-15)
├── p2/                 ← Backlog (score 8-11)
└── p3/                 ← Defer/skip (score <8)
```

Khi reclassify priority, **move file** sang folder mới và update [../gap-analysis-priority.md](../gap-analysis-priority.md).

---

## P0 — Làm ngay

| # | Gap | File |
|---|---|---|
| 2 | InfluencerProfile concept — Ambassador mandatory + vCreator recommended (creator pool) | [p0/02-influencer-profile-concept.md](./p0/02-influencer-profile-concept.md) |
| 8 | vCreator thiếu hệ thống kiểm soát ngân sách campaign + tính thưởng có cap | [p0/08-budget-alert-system.md](./p0/08-budget-alert-system.md) |

---

## P1 — Sprint tới

| # | Gap | File |
|---|---|---|
| **15** ⭐ | **🔝 TOP P1** — vCreator/Ambassador thiếu hệ thống đối chiếu (reconciliation) + audit trail crawl chống fraud (combined #6 + #15) | [p1/15-reconciliation-engine-and-snapshot.md](./p1/15-reconciliation-engine-and-snapshot.md) |
| 16 | vCreator/Ambassador thiếu hệ thống đánh giá creator (review + rating) — phần tiếp nối của gap #2 | [p1/16-profile-review-rating.md](./p1/16-profile-review-rating.md) |
| 31 | TCB cho phép admin tạo creator + import content giúp họ; vCr/Amb không có | [p1/31-admin-proxy-creator-flow.md](./p1/31-admin-proxy-creator-flow.md) |
| 32 | Concept "mã nhân viên + binding partner" — TCB đơn giản, vCreator chi tiết hơn | [p1/32-staff-code-employee-binding.md](./p1/32-staff-code-employee-binding.md) |

Các gap P1 từ [../gap-analysis-priority.md](../gap-analysis-priority.md) chưa có file detail:
- Gap #28 — Multi-tenant Partner unify

---

## P2 — Backlog

| # | Gap | File |
|---|---|---|
| 1 | Withdraw — 3 dự án đều admin-driven, dead code endpoint | [p2/01-ambassador-withdraw-bank-validation.md](./p2/01-ambassador-withdraw-bank-validation.md) |
| 4 | Float precision rounding (reclassified) | _(không cần file riêng — chỉ là 10 LOC backport)_ |
| 5 | Audit ActorType field metadata | [p2/05-audit-actor-type.md](./p2/05-audit-actor-type.md) |
| ~~6~~ | ~~Reconciliation engine port~~ — **gộp vào gap #15** (P1 top) | (merged → #15) |
| 7 | Analytics Dashboard port (chưa viết) | _(pending)_ |
| 9 | TCB và vCreator thiếu cơ chế bảo vệ khi tính lại reward cho content đã thay đổi trạng thái | [p2/09-recheck-recovery-pattern.md](./p2/09-recheck-recovery-pattern.md) |
| 17 | vCreator/Ambassador có thể bị broken avatar khi URL social expire | [p2/17-upload-avatar-cache.md](./p2/17-upload-avatar-cache.md) |
| 33 | Ambassador có cơ chế "tạo user giả để reserve referral code", TCB và vCreator không có | [p2/33-ambassador-referral-seed-user.md](./p2/33-ambassador-referral-seed-user.md) |

---

## P3 — Defer/skip

| # | Gap | File |
|---|---|---|
| 10 | TCB gửi cảnh báo Telegram lặp khi campaign vượt ngân sách (alert fatigue) | [p3/10-telegram-alert-deduplication.md](./p3/10-telegram-alert-deduplication.md) |
| 12 | vCreator/Ambassador thiếu lớp bảo vệ cho admin login | [p3/12-admin-login-security.md](./p3/12-admin-login-security.md) |
| 25 | TCB/Ambassador không có helper `GetRoot()` cho staff root account (vCreator có) | [p3/25-staff-root-account-helper.md](./p3/25-staff-root-account-helper.md) |

Các gap P3 từ [../gap-analysis-priority.md](../gap-analysis-priority.md) chưa có file detail:
- Gap #19 — vCreator Extended Period mode
- Gap #20 — Ambassador Affiliate suite
- Gap #21 — Ambassador Mission/WildRift gamification
- Gap #22 — vCreator Workplace 3-tier
- Gap #23 — vCreator registry_match HR engine
- Gap #24 — TCB Campaign matching engine
- Gap #26 — TCB transcript scoring (LLM)

---

## Format chuẩn của 1 file gap

Mỗi file chia làm 2 phần lớn:

```markdown
# Gap #NN — <title business-friendly>

> Priority badge + source links + last verified

# 📋 BUSINESS OVERVIEW
## Vấn đề là gì?
## Bảng so sánh 3 sản phẩm (góc nhìn business)
## Rủi ro nếu không sửa
## Đề xuất giải pháp (góc nhìn business)
   - Khuyến nghị (1 sentence)
   - Effort dự kiến
   - Cần product/business confirm (3-5 câu)

# 🔧 TECHNICAL SPECIFICATION
(Phần này giữ nguyên hiện trạng — diff code, schema, action items, lịch sử phân loại)
```

**Phần Business Overview** dùng ngôn ngữ stakeholder hiểu được (PM, ops, finance):
- KHÔNG dùng tên file/path/struct/method
- Mô tả flow nghiệp vụ tự nhiên (vd: "user tự rút tiền", "campaign vượt budget")
- Highlight risk + recommendation rõ ràng

**Phần Technical Specification** giữ chi tiết kỹ thuật cho dev:
- Diff code 3-way
- Schema migration
- 5-layer verification
- Action items + effort estimate
- Lịch sử phân loại (giữ trace nếu reclassify)

## Cách thêm gap mới

1. Tạo file `pX/NN-tên-gap.md` (X là priority, NN là số gap từ gap-analysis-priority.md)
2. Follow format chuẩn ở trên (xem 3 file mẫu hiện có: [p0/08](./p0/08-budget-alert-system.md), [p2/01](./p2/01-ambassador-withdraw-bank-validation.md), [p2/05](./p2/05-audit-actor-type.md))
3. Áp dụng **5-layer verification** trước khi classify priority:
   - Layer 1: Code tồn tại ở source
   - Layer 2: Code được gọi ở source
   - Layer 3: Runtime business dùng ở source
   - Layer 4: Target có flow tương đương không (HỎI USER)
   - Layer 5: Direction port hợp lý
4. Update README này (thêm row vào bảng priority tương ứng)
5. Update [../gap-analysis-priority.md](../gap-analysis-priority.md) link đường dẫn mới

## Cách reclassify gap

Khi priority thay đổi (vd: P1 → P2 sau khi user clarify):

```bash
# Move file sang folder mới
mv gaps/p1/NN-foo.md gaps/p2/NN-foo.md
```

Sau đó:
1. Update header file: `> **Priority**: 🟡 P2 (reclassified ngày XXX vì...)`
2. Update bảng trong README này
3. Update path trong [../gap-analysis-priority.md](../gap-analysis-priority.md)
4. Update section "Lịch sử phân loại" trong file gap (giữ trace lý do thay đổi)
