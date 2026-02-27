# Brainstorming: Cải Tiến Luồng Đối Soát V2

**Date:** 2026-02-21
**Objective:** Bổ sung re-scan validation, 3-tier classification, checklist lý do, bước công bố + luồng kháng cáo vào quy trình đối soát hiện tại
**Context:**
- Hệ thống: Go (Echo) + MongoDB, admin panel React
- Luồng hiện tại: PENDING → PROCESSING → PROCESSED → RUNNING → COMPLETED/REJECTED
- Quan điểm: Giữ nguyên luồng hiện tại, chỉ bổ sung - không refactor lớn
- Mục tiêu: Giảm manual effort BTC, tăng minh bạch với creator, hỗ trợ audit

**Techniques Used:**
1. **SCAMPER** - Biến đổi luồng existing thành luồng mới
2. **Six Thinking Hats** - Phân tích đa chiều (BTC, Creator, rủi ro, lợi ích)
3. **Starbursting** - Đặt câu hỏi chi tiết cho từng bước mới

---

## Luồng Hiện Tại vs Luồng Đề Xuất

```
=== HIỆN TẠI ===
PENDING
  → [BTC click] → PROCESSING (backend lấy data)
  → [backend done] → PROCESSED
  → [BTC click "Duyệt toàn bộ"] → RUNNING
  → [backend done] → COMPLETED / REJECTED

=== ĐỀ XUẤT ===
PENDING
  → [BTC click] → PROCESSING (backend lấy data, scan lần 1)
  → [backend done] → PROCESSED

  [Day 6-10: Re-scan job tự động - 3 lần trong 72h]
  → PROCESSED_REVIEWING (có kết quả classification)
    - auto_cancel items: hủy tự động, không cần BTC
    - suggested_cancel items: queue cho BTC confirm
    - approved items: tự động pass

  → [BTC review suggested_cancels + confirm] → PUBLISHED
    - Creator nhìn thấy kết quả
    - Appeal window mở (72h)

  → [Hết appeal window hoặc BTC close early] → RUNNING
  → [backend done] → COMPLETED
```

---

## Ideas Generated

### Category 1: Re-scan & Classification Engine ⚙️

**1. Job Re-scan ngày 6-10**
- Scheduled job chạy đầu ngày 6 của tháng
- Kiểm tra lại từng ReconciliationItem đang ở trạng thái `pending/approved`
- Output: classification mới cho từng item

**2. Scan 3 lần trong 72h - Majority Vote**
- Thay vì scan 1 lần duy nhất → scan lúc 00:00 ngày 6, 00:00 ngày 7, 00:00 ngày 8
- Item pass nếu ≥ 2/3 lần scan đều pass (majority vote)
- Tránh false positive khi creator tạm ẩn video
- Log cả 3 kết quả vào `ReconciliationHistory`

**3. 3-Tier Classification**
- `auto_cancel`: Link chết/private ≥ 2/3 lần scan + không có dấu hiệu recover → hủy không cần BTC
- `suggested_cancel`: Borderline cases → đưa lên queue BTC confirm
- `approved`: Pass tất cả checks ≥ 2/3 lần → tự động approve

**4. Lưu viewAtScan2 riêng biệt**
- Giữ `viewAtScan1` (từ cut-off ngày 30-31) không đổi
- Thêm field `viewAtScan2` lưu kết quả scan ngày 6-10
- Audit trail đầy đủ: view tại 2 thời điểm

**5. Log scan events vào ReconciliationHistory**
- Mỗi scan event: `{scanRound: 1|2|3, checkedAt, results: {linkStatus, viewCount, checksPassed[]}}`
- Không bao giờ xóa history → immutable audit trail

---

### Category 2: Checklist Lý Do ✅

**6. Cancel Reason Codes (chuẩn hóa)**

| Code | Label | Trigger |
|------|-------|---------|
| `LINK_DEAD` | Link không tồn tại | HTTP 404/410 ≥ 2/3 scans |
| `LINK_PRIVATE` | Link bị ẩn/riêng tư | HTTP 403/private flag ≥ 2/3 scans |
| `LINK_DELETED` | Content bị xóa | Platform API trả về deleted |
| `VIEW_BELOW_MINIMUM` | View dưới ngưỡng tối thiểu | view < campaign minimum threshold |
| `VIEW_DROP_EXCESSIVE` | View giảm quá nhiều so với scan 1 | viewScan2 < viewScan1 × (1 - threshold%) |
| `VELOCITY_ANOMALY` | View tăng bất thường (suspected fraud) | Spike detection algorithm |
| `DUPLICATE_CLAIM` | Content đã được claim trong đợt khác | Cross-check với existing items |
| `CONTENT_FORMAT_INVALID` | Không đúng format content quy định | Manual flag bởi BTC |

**7. Approve Reason Codes (chuẩn hóa)**

| Code | Label |
|------|-------|
| `LINK_ACTIVE` | Link hoạt động bình thường |
| `VIEW_THRESHOLD_MET` | View đạt ngưỡng tối thiểu |
| `NO_ANOMALY_DETECTED` | Không phát hiện bất thường |
| `MANUAL_OVERRIDE_APPROVED` | BTC override thủ công (kèm reason text) |
| `APPEAL_ACCEPTED` | Kháng cáo được chấp nhận |

**8. checklistSnapshot trong ReconciliationItem**
```javascript
// Thêm vào ReconciliationItem
{
  checklistSnapshot: [
    {
      code: 'LINK_ACTIVE',
      label: 'Link hoạt động bình thường',
      result: true,         // true = pass, false = fail
      scanRound: 2,         // round nào detect
      checkedAt: Date,
      value: 'https://...'  // evidence value nếu có
    }
  ],
  classificationResult: 'auto_cancel' | 'suggested_cancel' | 'approved',
  classificationReason: 'LINK_DEAD',  // primary reason
  classificationAt: Date,
  overriddenBy: ObjectId,   // nếu BTC override
  overrideReason: string,   // free text khi override
}
```

**9. BTC có thể check/uncheck + override**
- Với `suggested_cancel`: BTC xem checklist → confirm cancel (giữ classification) hoặc override → approved (bắt buộc chọn approve reason + text)
- Với `auto_cancel`: BTC có thể override → approved (bắt buộc nhập lý do, log rõ ràng)
- Với `approved`: BTC có thể override → cancel (bắt buộc chọn cancel reason)

**10. Checklist readable cho Creator**
- Khi công bố, creator thấy lý do dưới dạng text thân thiện, không phải code kỹ thuật
- Ví dụ: "LINK_DEAD" → "Link của bạn không thể truy cập tại thời điểm kiểm tra"

---

### Category 3: Admin Review Flow 👨‍💼

**11. Queue suggested_cancel riêng biệt**
- Tab "Cần xem xét" trong reconciliation detail
- Chỉ hiển thị items có classification = `suggested_cancel`
- Count badge: "15 items cần xem xét"

**12. Dashboard overview classification**
```
Kết quả re-scan:
  ✅ 320 approved (tự động)
  ⚠️  45 cần xem xét (suggested_cancel)
  ❌  38 tự động hủy (auto_cancel)
  ────────────────
  📊 403 tổng items
```

**13. Bulk confirm suggested_cancels**
- BTC có thể chọn tất cả → "Xác nhận hủy tất cả" (nếu đồng ý với system suggestion)
- Hoặc review từng item

**14. Status PROCESSED_REVIEWING**
- Thêm sub-state sau PROCESSED: reconciliation ở trạng thái này khi re-scan đã chạy xong
- Khác với PROCESSED (chưa re-scan)
- Khi BTC confirm xong tất cả suggested_cancels → có thể publish

**15. Nút "Công bố kết quả"**
- Sau khi BTC xong review → click "Công bố cho Creator"
- Reconciliation chuyển sang PUBLISHED
- Trigger notification đến tất cả creators liên quan

---

### Category 4: Bước Công Bố (PUBLISHED) 📢

**16. Status PUBLISHED**
- Thêm status mới giữa PROCESSED_REVIEWING và RUNNING
- Creators có thể thấy kết quả của item của mình
- Appeal window bắt đầu đếm từ thời điểm này

**17. Notification Creator khi Publish**
- Email + in-app (nếu có portal)
- Nội dung:
  ```
  Tiêu đề: Kết quả đối soát [Tên Campaign] - Đợt [X]

  Xin chào [Tên Creator],

  Kết quả đối soát cho [X] nội dung của bạn đã được công bố:
  ✅ [N] nội dung được duyệt: [tổng tiền]
  ❌ [M] nội dung bị hủy

  👉 Xem chi tiết và kháng cáo (nếu có): [link]
  ⏰ Thời hạn kháng cáo: [deadline - 72h]
  ```

**18. Appeal Window Countdown**
- Creator thấy countdown timer rõ ràng
- Gửi reminder email 24h trước khi hết deadline
- Sau deadline → items tự động finalize theo classification hiện tại

**19. "Điểm không quay lại" cho BTC**
- Sau khi PUBLISHED, BTC không thể tự ý thay đổi kết quả
- Mọi thay đổi phải qua appeal flow (có audit trail)
- Bảo vệ cả BTC và creator

---

### Category 5: Luồng Kháng Cáo 🙋

**20. Điều kiện kháng cáo**
- Chỉ items bị cancel (dù auto_cancel hay confirmed_cancel)
- Mỗi item chỉ được appeal 1 lần duy nhất
- Phải trong appeal window (trước deadline)

**21. Appeal Form với Template Response**
- Creator chọn lý do từ dropdown (dựa trên cancel reason, system gợi ý phản hồi phù hợp):

| Cancel Reason | Template gợi ý cho Creator |
|---------------|---------------------------|
| `LINK_DEAD` | "Vui lòng upload screenshot cho thấy link hoạt động trong thời gian campaign" |
| `LINK_PRIVATE` | "Nếu bạn tạm ẩn video vì lý do kỹ thuật, vui lòng giải thích và cung cấp bằng chứng" |
| `VIEW_DROP_EXCESSIVE` | "Nếu view giảm do platform điều chỉnh thuật toán, vui lòng cung cấp screenshot analytics" |
| `VELOCITY_ANOMALY` | "Vui lòng giải thích lý do view tăng đột biến và cung cấp bằng chứng tự nhiên" |

- Upload evidence: tối đa 5 file (ảnh/PDF)
- Free text: tối đa 1000 ký tự
- Preview trước khi submit

**22. AppealTicket Model**
```javascript
{
  _id: ObjectId,
  reconciliationId: ObjectId,
  reconciliationItemId: ObjectId,
  userId: ObjectId,              // creator
  reason: string,                // dropdown selection
  explanation: string,           // free text
  evidences: [{
    type: 'image' | 'pdf' | 'link',
    url: string,
    uploadedAt: Date
  }],
  status: 'pending' | 'reviewing' | 'approved' | 'rejected',
  reviewedBy: ObjectId,          // BTC user
  reviewNote: string,
  decision: 'full_restore' | 'partial_restore' | 'rejected',
  adjustedViewCount: number,     // nếu partial restore
  createdAt: Date,
  reviewedAt: Date,
  deadline: Date                 // = publishedAt + 72h
}
```

**23. BTC Appeal Review Queue**
- Tab "Kháng cáo" trong reconciliation detail
- Danh sách appeals với: creator name, item, cancel reason, submitted evidence
- Inlined: checklist original + appeal evidence side-by-side
- Actions: Accept (full/partial) / Reject
- Nếu Accept partial: nhập adjusted view count

**24. Tiered Appeal Routing**
- Amount < 100K VND: any BTC reviewer
- Amount 100K - 1M: senior BTC
- Amount > 1M: senior BTC + manager approval

**25. Kết quả Appeal**
- `full_restore`: item về lại approved với view count gốc
- `partial_restore`: approved với view count đã điều chỉnh (BTC nhập tay)
- `rejected`: giữ cancel, creator nhận notification với lý do từ BTC

**26. Notification kết quả appeal**
- Ngay khi BTC quyết định → push notification cho creator
- Email + in-app
- Nếu rejected → creator thấy lý do từ BTC (required field)

**27. Sau khi hết appeal window**
- BTC click "Chốt và tiến hành thanh toán" → RUNNING
- Hoặc nếu chưa có appeal nào pending → có thể close early
- Reconciliation tự động chuyển RUNNING sau 96h (buffer 24h sau deadline)

---

### Category 6: Data & Audit Trail 📊

**28. auditLog trong ReconciliationItem**
```javascript
auditLog: [
  { event: 'scan_1', at: Date, result: {...} },
  { event: 'scan_2', at: Date, result: {...} },
  { event: 'scan_3', at: Date, result: {...} },
  { event: 'classification', at: Date, result: 'suggested_cancel', reason: 'VIEW_DROP_EXCESSIVE' },
  { event: 'btc_confirmed_cancel', by: userId, at: Date, note: '...' },
  { event: 'published', at: Date },
  { event: 'appeal_submitted', appealId: ObjectId, at: Date },
  { event: 'appeal_rejected', by: userId, at: Date, reason: '...' },
  { event: 'finalized', at: Date, finalStatus: 'cancelled' }
]
```

**29. Cancel Reason Analytics**
- Report: bao nhiêu items bị cancel theo từng reason code
- Phân tích theo platform (TikTok vs YouTube vs Facebook)
- Trend theo tháng → cải thiện campaign rules

**30. Appeal Analytics**
- Win rate theo reason code
- Xử lý appeal trong bao lâu (SLA)
- Creator nào appeal nhiều nhất → fraud signal

---

## Statistics

- **Total ideas generated:** 30
- **Categories:** 6
- **Key insights:** 5
- **Techniques applied:** 3 (SCAMPER, Six Thinking Hats, Starbursting)

---

## Key Insights

### 🎯 Insight 1: 3-Tier Classification Giảm BTC Workload 70-80%

**Mô tả:** Thay vì BTC review 100% items, hệ thống tự phân loại. BTC chỉ xử lý `suggested_cancel` (~20-30% items borderline).

**Source:** SCAMPER (Eliminate) + Six Thinking Hats (Yellow)

**Impact:** 🔥 **High** | **Effort:** 🟡 **Medium**

**Tại sao quan trọng:**
- Auto_cancel (link chết rõ ràng) không cần BTC xem
- Approved (pass hết checks) không cần BTC xem
- Chỉ borderline cases mới cần judgment của con người

**Implementation:**
```
auto_cancel: link 404/private ≥ 2/3 scans → cancel ngay, no BTC needed
suggested_cancel: view drop > threshold, anomaly nhẹ → BTC confirm
approved: pass all checks ≥ 2/3 scans → approve ngay, no BTC needed
```

---

### 🎯 Insight 2: Scan 3 Lần / 72h - Majority Vote Chống False Positive

**Mô tả:** Scan 1 lần duy nhất dễ hủy oan khi creator tạm ẩn video. Scan 3 lần lấy 2/3 majority là cân bằng tốt.

**Source:** Six Thinking Hats (Black - risk) + Starbursting (How)

**Impact:** 🔥 **High** | **Effort:** 🟢 **Low**

**Tại sao quan trọng:**
- Creator có thể ẩn video vì lý do kỹ thuật (re-edit, platform issue) rồi restore
- 1 scan sai = tiền bị hủy oan = creator complaint
- 3 scans trong 72h: chỉ thêm 2 cron jobs đơn giản, không phức tạp

**Scan schedule:**
```
Ngày 6 00:00 → Scan 1
Ngày 7 00:00 → Scan 2
Ngày 8 00:00 → Scan 3 → Classification chạy
```

---

### 🎯 Insight 3: PUBLISHED State Là "Điểm Không Thể Quay Lại" Cho BTC

**Mô tả:** Một khi đã publish cho creator, BTC không tự ý thay đổi kết quả. Mọi modification phải qua appeal flow có audit trail.

**Source:** SCAMPER (Reverse) + Six Thinking Hats (Blue)

**Impact:** 🔥 **High** | **Effort:** 🟢 **Low**

**Tại sao quan trọng:**
- Bảo vệ BTC: không thể bị blame "tự ý đổi sau khi công bố"
- Bảo vệ creator: kết quả chính thức có record rõ ràng
- Tăng trust: creator tin rằng kết quả minh bạch và nhất quán

---

### 🎯 Insight 4: Template Response Theo Cancel Reason Giảm Thời Gian Xử Lý Appeal

**Mô tả:** Khi creator kháng cáo, system gợi ý loại evidence phù hợp dựa trên lý do bị cancel. Creator biết cần nộp gì → appeal quality tốt hơn → BTC xử lý nhanh hơn.

**Source:** Six Thinking Hats (Green) + Starbursting (What)

**Impact:** 🟡 **Medium** | **Effort:** 🟢 **Low**

**Ví dụ:**
- `LINK_DEAD` → "Upload screenshot cho thấy link hoạt động trong thời gian campaign"
- `VELOCITY_ANOMALY` → "Giải thích lý do view tăng đột biến, ví dụ: được featured, viral organically"

---

### 🎯 Insight 5: Tiered Appeal Routing Theo Amount

**Mô tả:** Appeal amount nhỏ xử lý nhanh (any BTC), amount lớn cần senior approval. Tránh bottleneck khi BTC junior phải escalate manually.

**Source:** Six Thinking Hats (Green) + Starbursting (Who)

**Impact:** 🟡 **Medium** | **Effort:** 🟡 **Medium**

**Tiers đề xuất:**
| Amount | Reviewer Required |
|--------|------------------|
| < 100K VND | Any BTC |
| 100K - 1M VND | BTC Senior |
| > 1M VND | BTC Senior + Manager confirm |

---

## Luồng Status Đầy Đủ Đề Xuất

```
PENDING
  → PROCESSING          [BTC trigger]
  → PROCESSED           [Backend done, scan 1 xong]

  [Day 6-8: Re-scan job - 3 rounds]
  → PROCESSED_REVIEWING [Re-scan xong, BTC cần review suggested_cancels]
  → PUBLISHED           [BTC confirm xong, công bố cho creators]
                        [Appeal window: 72h]

  → RUNNING             [BTC close appeals / hết window → finalize]
  → COMPLETED           [Backend done]

  Possible: REJECTED    [BTC hủy toàn bộ đối soát, giữ nguyên]
```

**ReconciliationItem sub-status:**

```
pending → (scan) → [auto_cancel | suggested_cancel | approved]
                          ↓              ↓
                    auto canceled    btc_confirmed_cancel
                                          ↓
                              (if creator appeals)
                                     appeal_pending
                                          ↓
                              appeal_approved / appeal_rejected
```

---

## Database Changes

### ReconciliationItem - thêm fields
```javascript
{
  // Scan data
  viewAtScan1: number,           // view tại cut-off (day 30-31)
  viewAtScan2: number,           // view tại re-scan (day 6-10), = median của 3 rounds

  // Classification
  classificationResult: 'auto_cancel' | 'suggested_cancel' | 'approved',
  classificationReason: CancelReasonCode,
  classificationAt: Date,

  // Checklist
  checklistSnapshot: [{
    code: string,
    label: string,
    result: boolean,
    scanRound: number,
    checkedAt: Date,
    value: any
  }],

  // BTC Override
  overriddenBy: ObjectId,
  overrideReason: string,
  overrideAt: Date,

  // Audit log
  auditLog: [AuditEvent],
}
```

### New Collection: appeal_tickets
```javascript
{
  _id: ObjectId,
  reconciliationId: ObjectId,
  reconciliationItemId: ObjectId,
  userId: ObjectId,
  reason: string,
  explanation: string,
  evidences: [{type, url, uploadedAt}],
  status: 'pending' | 'reviewing' | 'approved' | 'rejected',
  reviewedBy: ObjectId,
  reviewNote: string,
  decision: 'full_restore' | 'partial_restore' | 'rejected',
  adjustedViewCount: number,
  deadline: Date,
  createdAt: Date,
  reviewedAt: Date
}
```

### Reconciliation - thêm fields
```javascript
{
  publishedAt: Date,              // thời điểm BTC publish
  appealDeadline: Date,           // publishedAt + 72h
  appealStats: {
    total: number,
    pending: number,
    resolved: number,
    approved: number,
    rejected: number
  }
}
```

---

## Recommended Next Steps

1. **Tech Spec**: Định nghĩa API contracts cho:
   - Re-scan trigger endpoint
   - Classification result endpoint
   - Publish endpoint (chuyển PUBLISHED)
   - Appeal CRUD endpoints
   - BTC appeal review endpoints

2. **Database Migration**: Schema changes cho ReconciliationItem + new collection appeal_tickets

3. **Backend**: Implement re-scan scheduler + classification engine

4. **Admin UI**:
   - Tab "Cần xem xét" (suggested_cancel queue)
   - Dashboard overview classification stats
   - Nút "Công bố kết quả"
   - Tab "Kháng cáo" với appeal review UI

5. **Creator Portal** (nếu chưa có): Trang xem kết quả đối soát + form kháng cáo

---

*Generated by BMAD Method v6 - Creative Intelligence*
*Session duration: ~30 minutes*
*Techniques: SCAMPER, Six Thinking Hats, Starbursting*
*Document: accesstrade-projects/docs/operation-optimize/brainstorming-reconciliation-v2-enhancement-20260221.md*
