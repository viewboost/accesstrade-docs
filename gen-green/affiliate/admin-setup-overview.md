# Affiliate — Admin Setup — Overview

> **Ngày:** 2026-05-04
> **Trạng thái:** Đang thiết kế
> **PRD chi tiết:** [prd-admin-setup-2026-05-04.md](prd-admin-setup-2026-05-04.md)
> **Đối tượng:** Product, Operations, Stakeholders (non-tech)

---

## Đây là gì?

**Admin Setup** là phần "back-office" của tích hợp affiliate trên Gen-Green. Đội admin dùng để **chuẩn bị danh sách chiến dịch affiliate** trước khi creator nhìn thấy.

Hiểu đơn giản: nếu affiliate là một "cửa hàng", thì Admin Setup là nơi nhân viên **xếp hàng lên kệ** trước giờ mở cửa.

---

## Tại sao cần?

Hệ thống affiliate gốc (Scalef) có **hàng nghìn chiến dịch**. Không phải chiến dịch nào cũng phù hợp với creator Gen-Green:
- Có chiến dịch của đối thủ trực tiếp với partner Gen-Green → cần loại bỏ
- Có chiến dịch ngách không liên quan đến khán giả → bỏ qua
- Mô tả gốc thường bằng tiếng Anh / quá kỹ thuật → cần Việt hóa

→ **Đội admin phải duyệt thủ công** từng chiến dịch trước khi hiển thị cho creator. Đây là vai trò "gác cổng chất lượng".

---

## Admin làm gì?

### 1. Tạo chiến dịch affiliate

Admin nhập:
- **Tên** + **mô tả ngắn** + **mô tả dài** (Việt hóa)
- **Banner** (ảnh thumbnail)
- **Hoa hồng** (VD: "Tới 8%/đơn") + **thưởng thêm** (VD: "+100K đơn đầu")
- **Mã Scalef** (ID + URL gốc của chiến dịch ở Scalef)
- **Thời gian** chạy (ngày bắt đầu / kết thúc)
- **Partner** (chọn 1 lần, không sửa được sau)

Sau khi tạo, chiến dịch ở trạng thái **"chưa bật"** — admin review xong mới bật.

### 2. Liên kết chiến dịch với Event

Affiliate **không đứng riêng lẻ** — phải gắn vào Event hiện có.

> Ví dụ: Event "Review xe VinFast VF8" → admin liên kết với chiến dịch affiliate "Bán xe VinFast trên Showroom Online". Khi creator vào Event này, sẽ thấy banner affiliate xuất hiện bên trong.

- 1 chiến dịch affiliate có thể link với **nhiều** Event
- 1 Event có thể có **nhiều** chiến dịch affiliate
- **Chỉ link được Event cùng partner** (không lẫn lộn brand)

### 3. Bật / tắt chiến dịch

- **Bật (active):** Creator sẽ thấy chiến dịch trong các Event đã link
- **Tắt (inactive):** Creator không thấy nữa, nhưng link affiliate đã tạo trước đó vẫn hoạt động bình thường

### 4. Chiến dịch hết hạn tự ẩn (không cần admin can thiệp)

Khi chiến dịch qua **ngày kết thúc** (`end_date`), creator **không còn thấy** trên Gen-Green nữa — dù admin chưa "tắt" thủ công. Logic hệ thống tự lọc theo ngày.

Admin vẫn thấy chiến dịch trong danh sách back-office, kèm badge **"Hết hạn"** để biết và quyết định: gia hạn (đổi `end_date`) hoặc kệ (không ảnh hưởng creator).

→ **Không có cron tự động tắt** — giữ đơn giản, admin chủ động khi cần.

---

## Phân quyền

Dùng lại 3 cấp role có sẵn của Gen-Green admin (giống Event hiện tại):

| Vai trò | Quyền |
|---------|-------|
| **Root** | Toàn quyền trên tất cả partner |
| **Admin** | Chỉ thao tác trên chiến dịch của partner mình (VD: brand manager VinFast chỉ thấy chiến dịch VinFast) |
| **Collaborator** | Chỉ xem, không sửa được |

---

## Vì sao track này quan trọng (và làm trước)?

Track này có **2 đặc điểm** khiến nó nên start sớm nhất:

1. **Không phụ thuộc gì** — không cần chờ Scalef API, không cần chờ creator linking, không cần chờ FE creator. Có thể chạy song song với mọi track khác.

2. **Chuẩn bị data sẵn cho ngày launch** — khi creator-facing flow hoàn thành và mở cho creator, **đã có sẵn 20+ chiến dịch** để creator browse ngay. Tránh tình huống "mở cửa hàng nhưng kệ trống".

→ Có thể go-live track này riêng, không cần chờ các track khác.

---

## Sau khi xong thì sao?

Track này tạo ra **kho dữ liệu** mà 2 track sau sẽ đọc:

```
Admin Setup (track này)
    ↓ tạo data
[Affiliate Campaigns] + [Mappings với Event]
    ↓ đọc data
API Integration ──→ FE Display (cho creator)
```

→ Creator sẽ thấy chiến dịch affiliate trong Event mà admin đã link, với nội dung Việt hóa admin đã chuẩn bị.

---

## Thời gian & nguồn lực

- **Effort:** ~8.5 ngày (~1.5 tuần) cho 1 BE + 1 FE
- **Output:**
  - Admin Panel page mới (list, create/edit, detail)
  - Backend APIs + database
  - Reuse: phân quyền, audit log, file upload, markdown editor — đều đã có sẵn

Chi tiết kỹ thuật: xem [PRD](prd-admin-setup-2026-05-04.md).

---

## Liên quan

- [PRD chi tiết](prd-admin-setup-2026-05-04.md) — cho dev
- [Scalef API Reference](scalef-api.md) — spec backend integration với Scalef (cho Phase 2)
- [FE Display Overview](fe-display-generate-link-report-overview.md) — track sau, hiển thị cho creator
- [Pub2 Affiliate V1 — Ambassador](../../pub2-affiliate-integration/prd-affiliate-v1-2026-03-31.md) — reference đã làm trên Ambassador
