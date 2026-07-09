# Booking trên Ambassador — Phase 1 (Quick win)
## Scope Phase 1 (đã chốt)

**Ngày:** 2026-06-29
**Phạm vi:** Phase 1 / 4 phase của kế hoạch tổng thể
**Ước lượng:** ~2 sprint
**Đối tượng đọc:** Team AT (duyệt scope + lên kế hoạch triển khai)

---

## 1. Bối cảnh — Phase 1 nằm ở đâu trong kế hoạch tổng thể

Mô hình Booking trên Ambassador được triển khai theo **4 phase** (sơ đồ Rollout gốc):

| Phase | Tên | Nội dung chính | Trạng thái |
|-------|-----|----------------|------------|
| **1** | **Quick win** | **Import creator + Marketplace tra cứu + Shortlist** | 👉 **Tài liệu này** (~2 sprint) |
| 2 | Core flow | Brief + Booking request + E-contract | Sau |
| 3 | Automation | Payment tracking + Dashboard live + Auto-report | Sau |
| 4 | Scale | Brand self-serve + AI match + Multi-brand | Sau |

> **Phase 1 là nền móng dữ liệu + công cụ vận hành.** Nó tạo ra "kho creator có thông tin thật, tra cứu được" — điều kiện để các phase sau (mời/booking/thanh toán) hoạt động.

---

## 2. Mục tiêu Phase 1

**Mục tiêu chính:** Xây dựng một **kho creator (marketplace tra cứu)** để team vận hành AT có thể **import dữ liệu creator, làm giàu thông tin (enrich), tìm kiếm/lọc, và lập shortlist** phục vụ brand.

**Kết quả đo được sau Phase 1:**
- Import được creator từ nguồn dữ liệu cũ vào hệ thống (có kiểm soát lỗi).
- Mỗi creator có thông tin được làm giàu tự động: follower, engagement, category, tier...
- Team vận hành tìm/lọc creator theo nhiều tiêu chí (platform, tier, ngành, follower, quốc gia).
- Lập được shortlist creator cho từng brand và xuất file gửi brand.

**Giá trị mang lại:** Thay thế việc quản lý creator bằng Excel rời rạc → tập trung hóa thành kho dữ liệu có thể tra cứu, làm bằng chứng năng lực khi pitch brand ("kho creator có engagement thật").

---

## 3. User Story (Phase 1)

> Người dùng Phase 1 = **team ops/AM của AT** (chưa mở cho brand/creator).

**Nhóm Import & làm giàu dữ liệu (Ops):**
- *Là Ops*, tôi muốn **upload file creator (CSV/Excel)** và xem trước + báo lỗi từng dòng trước khi ghi, để dữ liệu vào kho không bị rác.
- *Là Ops*, tôi muốn hệ thống **tự làm giàu thông tin creator** (follower, engagement) sau import, để không phải nhập tay.
- *Là Ops*, tôi muốn **theo dõi tiến trình enrich và bấm retry** những creator lỗi, để kho không bị thủng dữ liệu.
- *Là Ops*, tôi muốn **thấy chi phí/quota của vendor crawl** trước khi chạy hàng loạt, để không đốt tiền ngoài kiểm soát.

**Nhóm Tra cứu & Shortlist (AM):**
- *Là AM*, tôi muốn **tìm/lọc creator** theo platform, tier, ngành, follower, quốc gia, để chọn creator phù hợp cho brand.
- *Là AM*, tôi muốn **xem hồ sơ chi tiết một creator** (số liệu + lịch sử) để đánh giá.
- *Là AM*, tôi muốn **so sánh nhiều creator cạnh nhau** để chọn ra danh sách tốt nhất.
- *Là AM*, tôi muốn **lập shortlist gắn với một brand/chiến dịch** và **xuất file/link gửi brand**, để brand xem và phản hồi.
- *Là AM*, tôi muốn **xem và nhập giá tham khảo (rate-card) của creator** trên hồ sơ, để tư vấn brand về ngân sách phù hợp.

**Nhóm Quản trị (Admin/Quản lý):**
- *Là Quản lý AT*, tôi muốn **dashboard về sức khỏe kho creator** (số lượng, % enrich thành công, chi phí vendor) để biết hệ thống chạy tốt không.
- *Là Admin*, tôi muốn **xử lý creator trùng** và **sửa thông tin sai**, để dữ liệu sạch.

---

## 4. Tận dụng Ambassador vs Phát triển mới

> **Lợi thế lớn:** phần lớn xương sống backend đã có sẵn trong Ambassador → Phase 1 chủ yếu là **xây giao diện vận hành** trên nền đã chạy.

### ✅ Tận dụng cái đã có (nền tảng Ambassador)
| Cái đã có | Dùng cho |
|-----------|----------|
| **Dịch vụ Profile Enrichment** (làm giàu hồ sơ creator qua vendor) đã tích hợp & chạy thật | Tự động bổ sung follower, engagement, category... cho creator |
| **Hồ sơ creator** — cấu trúc dữ liệu giàu field (follower/engagement/category/score) | Lưu hồ sơ creator |
| **API theo dõi job enrich** (trạng thái, retry, đo completeness, quota vendor) | Màn theo dõi + retry enrich |
| **API creator** + lớp xử lý backend | Marketplace list/detail |
| **Công cụ manual-review** (đã có) | Màn nhập tay khi vendor không lấy được dữ liệu — KHÔNG xây lại |

### 🆕 Phát triển mới
| Phát triển mới | Vì sao |
|----------------|--------|
| **Admin portal MỚI (Next.js)** | Frontend hoàn toàn mới (xem mục 6 — lý do không dùng admin cũ) |
| **Module Import** (wizard + mapping + preview + dedup) | Backend hiện chỉ enrich từng creator, chưa có import hàng loạt |
| **Module Marketplace** (search/filter/compare UI) | Chưa có giao diện tra cứu cho ops/AM |
| **Module Shortlist** | **Đã có bản sơ bộ, cần hoàn thiện (production-ready hóa)** — chọn creator vào danh sách gắn brand/chiến dịch, có chấm điểm |
| **Rate-card giá creator** (`priceMin/priceMax` + đơn vị) | **Hồ sơ creator chưa có field giá** — cần bổ sung. Giá là thông tin **nhập tay/import** (không tự thu thập được), gợi ý theo tier |
| **Field `Tier`** (tự tính từ follower) | Model chưa có — cần cho việc lọc |
| **Field Consent/Visibility** | Tuân thủ dữ liệu cá nhân (PDPD) khi đưa hồ sơ cho brand |

---

## 5. Các Surface / Module cần phát triển

**1 Admin portal mới (Next.js), gồm 6 cụm màn:**

| # | Module | Chức năng chính | Ưu tiên |
|---|--------|-----------------|---------|
| 1 | **Import** | Upload CSV/Excel → mapping cột → preview + báo lỗi từng dòng → dedup → confirm + lịch sử import | MUST |
| 2 | **Creator Marketplace** | List + search/filter (platform/tier/**engagement rate**/ngành/follower/quốc gia/**khoảng giá**) · Detail hồ sơ (gồm **rate-card giá creator**) · So sánh · Merge trùng | MUST |
| 3 | **Enrich/Vendor Ops** | Theo dõi job enrich (đang chạy/lỗi) · Retry đơn + hàng loạt · Bảng chất lượng dữ liệu · Quota & chi phí vendor | MUST |
| 4 | **Shortlist** | Tạo/sửa shortlist gắn brand/chiến dịch · Chọn creator (có chấm điểm) · Gán PIC · Ghi chú · Export CSV/Excel · (nên có) share-link gửi brand | MUST |
| 5 | **Dashboard** | Cơ cấu kho · tiến độ enrich · completeness · chi phí vendor · coverage gap | SHOULD |
| 6 | **Settings/Audit** | Cấu hình ngưỡng + mapping-template + Audit log (ai import/sửa/export) | SHOULD |

> Chi tiết màn + checklist MUST/SHOULD: tài liệu kỹ thuật nội bộ.

---

## 6. Vì sao build Admin MỚI (không dùng admin Ambassador hiện tại)

| Lý do | Chi tiết |
|-------|----------|
| **Stack lạc hậu ~6 năm** | Admin cũ = Umi 3.5 + React 16 (2019). Khó nâng cấp, dễ vỡ. |
| **Là fork cũ** | Mang nợ kỹ thuật + code không liên quan booking. |
| **Nâng tại chỗ rủi ro cao** | Umi 3→4 và React 16→19 đều là breaking change lớn. |
| **Toàn bộ màn là mới** | Import/enrich/marketplace/shortlist không tái dùng được giao diện cũ. |
| **Đã có chuẩn mới** | `techcombank/dashboard` (Next.js 16 + React 19) đã chạy — làm mẫu. |

→ **Build mới = frontend Next.js mới đứng trên backend Go đã có** (giống cách dashboard TCB đứng trên backend TCB). Backend/API vẫn tái dùng tối đa.

---

## 7. Phase 1 KHÔNG bao gồm những gì (Out of scope)

> Quan trọng để AT không kỳ vọng nhầm. Những thứ sau thuộc Phase 2+:

- ❌ **Brand không có tài khoản đăng nhập** — Phase 1 đi concierge: AM browse hộ, gửi shortlist qua file/link. Brand portal là Phase 2+.
- ❌ **Creator không có tài khoản** — creator hoàn toàn passive (chỉ được import + crawl). Không self-register/claim.
- ❌ **Không có booking giao dịch** — không tạo job, không mời, không ký HĐ, không thanh toán. Marketplace Phase 1 chỉ **tra cứu + shortlist**, nút "mời/book" chưa hoạt động.
- ❌ **Không hiển thị đơn/GMV** — chưa có dữ liệu doanh số (cần affiliate tracking, thuộc phase sau). Profile chỉ có engagement (view/like).
- ❌ **Không có "Verified = booking thành công" tự động** — badge Verified ở Phase 1 chỉ lấy từ **lịch sử booking cũ trong dữ liệu import**, không tự sinh từ booking mới (chưa có booking mới).
- ❌ **Không AI match, không multi-brand self-serve** — Phase 4.

---

## 8. Câu hỏi cần Business (AT) giải quyết + gợi ý chuyên gia

> Cần chốt **trước khi vào sprint** vì ảnh hưởng cấu trúc dữ liệu (sửa sau tốn kém).

### 🔴 Câu chặn — phải chốt trước

| # | Câu hỏi | 💡 Gợi ý chuyên gia |
|---|---------|---------------------|
| 1 | **Nguồn "DB cũ" lấy ở đâu?** File Excel rời do AM giữ, hay dữ liệu đã nằm trong hệ thống cũ? Ai chuẩn bị/làm sạch? | Nếu là file rời → làm **import wizard**. Nếu đã trong DB → viết script migrate. **Cần biết data đang ở đâu trước khi code importer.** |
| 2 | **Kho creator dùng chung hay riêng theo từng brand/tenant?** | Nếu khách là các đơn vị cạnh tranh nhau → nên **tách shortlist theo tenant** ngay từ đầu (dù kho creator chung), tránh rò rỉ dữ liệu giữa các khách. |
| 3 | **Creator sau import hiển thị ngay hay chờ duyệt?** | Dữ liệu cũ (đã từng làm việc) → **hiển thị ngay (auto-approve)** để có kho dùng liền; có nút hạ xuống chờ-duyệt khi cần. |
| 4 | **Creator import gắn cho (các) đơn vị/khách hàng nào?** | Creator phải được gắn với ít nhất 1 đơn vị mới hiển thị trên marketplace. → Cần xác định Phase 1 import phục vụ (các) khách hàng nào để gắn đúng từ đầu. |

### 🟡 Câu ảnh hưởng thiết kế

| # | Câu hỏi | 💡 Gợi ý chuyên gia |
|---|---------|---------------------|
| 4 | **Tier (Nano/Micro/Macro) tính thế nào?** | **Tự tính từ follower** (chuẩn ngành — KHÔNG tính theo giá) + cho admin chỉnh tay. Giá là field RIÊNG, lọc ngân sách riêng. Nên thêm **engagement rate** làm bộ lọc thứ 2 (cùng tier nhưng chất lượng khác xa). |
| 5 | **Thông tin nào hiển thị cho brand, có cần creator đồng ý?** | Dữ liệu crawl đem chào brand cần cơ sở pháp lý (PDPD). Phase 1 đặt **mặc định nội bộ** + có đường gỡ qua email. |
| 6 | **Có hiển thị giá tham khảo của creator không?** | Phase 1 chưa cần (giá thuộc booking — Phase 2). Có thể để field trống. |

> Bảng câu hỏi đầy đủ + lý do thị trường: tài liệu phân tích nội bộ.

---

## 9. Thông tin quan trọng khác

- **2 luồng song song:** Phase 1 (kho creator) **độc lập** với phần booking lõi — có thể bố trí 1-2 dev làm Phase 1 song song mà không chờ phần booking giao dịch.
- **Rủi ro chi phí vendor:** import + enrich hàng loạt = phát sinh chi phí dịch vụ enrichment thật. Bắt buộc có màn quota + trần batch-size để kiểm soát (đã đưa vào MUST).
- **Tuân thủ dữ liệu:** xử lý hồ sơ creator (PII) cần cờ nguồn gốc + visibility + đường gỡ — quan trọng với khách enterprise/ngân hàng.
- **Nối tiếp Phase 2:** Shortlist được thiết kế sẵn để Phase 2 gắn luồng "gửi mời/booking" mà **không phải làm lại dữ liệu**.

---

*Tài liệu tổng quan Phase 1 — Booking trên Ambassador.*
