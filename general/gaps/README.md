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

(Gap #2 đã reclassify P0 — xem section P0 ở trên)

Các gap P1 từ [../gap-analysis-priority.md](../gap-analysis-priority.md) chưa có file detail:
- Gap #3 — Reward V2 cho vCreator
- Gap #9 — `RecoverRecheckInProgress` cron (Amb → TCB)
- Gap #10 — `isSendNotification` flag (Amb → TCB)
- Gap #11 — Email transactional (TCB → vCr/Amb)
- Gap #13 — Content moderation tools (TCB → vCr/Amb)
- Gap #15 — ReconciliationSnapshot per crawl
- Gap #16 — Profile Review + Rating
- Gap #17 — Upload avatar cache MinIO
- Gap #25 — Staff root account port
- Gap #28 — Multi-tenant Partner unify

---

## P2 — Backlog

| # | Gap | File |
|---|---|---|
| 1 | Withdraw — 3 dự án đều admin-driven, dead code endpoint | [p2/01-ambassador-withdraw-bank-validation.md](./p2/01-ambassador-withdraw-bank-validation.md) |
| 4 | Float precision rounding (reclassified) | _(không cần file riêng — chỉ là 10 LOC backport)_ |
| 5 | Audit ActorType field metadata | [p2/05-audit-actor-type.md](./p2/05-audit-actor-type.md) |
| 6 | Reconciliation engine port (chưa viết) | _(pending)_ |
| 7 | Analytics Dashboard port (chưa viết) | _(pending)_ |

---

## P3 — Defer/skip

| # | Gap | File |
|---|---|---|
| 10 | TCB gửi cảnh báo Telegram lặp khi campaign vượt ngân sách (alert fatigue) | [p3/10-telegram-alert-deduplication.md](./p3/10-telegram-alert-deduplication.md) |
| 12 | vCreator/Ambassador thiếu lớp bảo vệ cho admin login | [p3/12-admin-login-security.md](./p3/12-admin-login-security.md) |

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
