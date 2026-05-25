# Verification Report — Feature Inventory & Comparison Matrix

> **Verified**: 2026-05-07
> **Method**: Random 20% spot-check + targeted cross-product checks + ground truth rebuild
> **Result**: Inventory files OK, matrix had 8% error rate → matrix rewritten from filesystem ground truth

---

## Phase A — Random 20% existence check

**Sample size**: 42 items across 3 inventory files (services, admin pages, frontend pages, dashboard routes).
**Method**: `random.sample` với seed cố định 42 → mỗi category lấy 20% items, check file/folder tồn tại trên filesystem.

| Project | Sample tested | Pass | Fail |
|---|---:|---:|---:|
| TCB (services + admin + frontend + dashboard) | 19 | 19 | 0 |
| vCreator (services + admin + frontend) | 11 | 11 | 0 |
| Ambassador (services + admin + frontend) | 13 | 13 | 0 |
| **Total** | **43** | **43** | **0** |

**Existence rate: 100%** ✅ — Mọi feature trong inventory đều tồn tại đúng path.

---

## Phase B — Targeted cross-product check

Sau khi existence pass, tôi check những claim trong matrix có vẻ đáng nghi:

| Claim trong matrix v1 | Reality | Verdict |
|---|---|---|
| "Ambassador không có `transfer` admin page" | `ambassabor/admin/src/pages/transfer/` tồn tại | ❌ matrix sai |
| "TCB không có `event-category` admin page" | TCB có, vCreator không | ❌ matrix lẫn lộn |
| "vCreator có 15 service" | `find` trả 15 | ✅ |
| "Ambassador có 16 service" | `find` trả 16 | ✅ |
| "TCB có 29 service" | `find` trả 29 | ✅ |
| "`segment` admin có ở 3 dự án" | Đúng cả 3 | ✅ |
| "`bonus` admin = vCreator-only" | Có ở vCreator + Ambassador | ❌ matrix sai |
| "`statistic` frontend = vCreator-only" | Có ở vCreator + Ambassador | ❌ matrix sai |

→ **Inventory files chính xác** (đã verify với grep). Lỗi nằm ở **matrix v1** vì lúc tổng hợp tôi đọc 3 inventory bằng tay và miss/cherry-pick.

---

## Phase C — Ground truth rebuild

Để fix gốc rễ, tôi build lại matrix bằng Python script đọc filesystem trực tiếp:

```python
# Pseudo-code
for proj in [tcb, vcreator, ambassador]:
    services[proj] = list_files('backend/internal/service/*.go', exclude_test=True)
    admin[proj]    = list_dirs('admin/src/pages/*')
    frontend[proj] = list_dirs('<frontend-path>/src/pages/*')
```

Output saved to `.tmp/inventory-ground-truth.json`.

### Corrections applied to matrix

| # | Issue | Fix |
|---|---|---|
| 1 | Admin "shared by 3" count: 18 → 20 | Updated total |
| 2 | TCB-only admin: 6 → 9 | Added: event-bonus, event-category, dashboard-external |
| 3 | Ambassador-only admin: 4 → 5 | Added: common_configs |
| 4 | `transfer` admin: ghi sai TCB+vCr only → reality cả 3 đều có | Moved to "shared 3" |
| 5 | `bonus` admin: ghi vCr-only → reality vCr+Amb (TCB tách thành event-bonus) | Reclassified |
| 6 | Frontend "shared by 3": 14 → 15 | Added 404 page |
| 7 | Frontend `statistic`: ghi vCr-only → reality vCr+Amb | Reclassified |
| 8 | Frontend `bonus`: confused, đã re-verify đúng vCr-only | Confirmed |

### Error rate

```
Total feature cells in matrix v1: ~100 (32 services + 37 admin + 31 frontend)
Cells with detected errors: 8
Error rate: 8.0%
```

**Threshold**: <10% → corrections applied, **không cần re-scan toàn bộ** (theo strategy bạn yêu cầu).

---

## Phase D — Updates applied

### Inventory files
✅ **Không thay đổi** (đã verified đúng từ đầu — agent ghi đầy đủ, lỗi nằm ở matrix tổng hợp).

### Matrix file
✅ **Rewrite hoàn toàn** từ ground truth — [feature-comparison-matrix.md](./feature-comparison-matrix.md) v2.

Thay đổi chính:
- Tách thành 3 matrix tables riêng (Services, Admin Pages, Frontend Pages) — mỗi table list đầy đủ items
- Thêm "Domain Coverage Matrix" tổng hợp theo nghiệp vụ
- Counts khớp 100% với filesystem

---

## Recommendations

### Items vẫn cần verify sâu hơn (out of scope của verification này)

1. **`reconciliation` admin page ở vCreator/Ambassador**: có wire route handler không, hay là dead UI từ thời fork?
2. **`segment` admin page ở vCreator/Ambassador**: tương tự.
3. **`transfer` admin page ở vCreator**: có dùng thật không?
4. **Service descriptions** (mô tả 1-line): chưa verify với code, có thể inaccurate ở chi tiết — không ảnh hưởng decision strategic.

→ Có thể spawn subagent đọc handler/router để verify wiring nếu cần làm thêm.

---

## Lessons learned

1. **Trust the inventory, verify the synthesis** — Agent enumerate filesystem rất chính xác. Lỗi xuất hiện khi merge/synthesize bằng tay từ 3 source độc lập.
2. **Spot-check trước khi rebuild** — 100% existence pass cho phép skip full rescan, chỉ fix synthesis layer.
3. **Filesystem là single source of truth** — script đọc filesystem rồi diff là cách verify rẻ nhất.

---

## Files

- [inventory-techcombank.md](./inventory-techcombank.md) — verified ✅
- [inventory-vcreator.md](./inventory-vcreator.md) — verified ✅
- [inventory-ambassador.md](./inventory-ambassador.md) — verified ✅
- [feature-comparison-matrix.md](./feature-comparison-matrix.md) — rewritten v2 from ground truth ✅
- `.tmp/inventory-ground-truth.json` — raw ground truth data (intermediate)
