# Product Requirements Document: Green Affiliate — Trang khám phá chiến dịch affiliate

**Date:** 2026-05-27
**Author:** vinhnguyen
**Version:** 1.0
**Project Type:** Frontend feature (clone layout) + Backend read API
**Project Level:** Level 2 (8-15 FRs)
**Status:** Draft

---

## Document Overview

PRD này định nghĩa functional + non-functional requirements cho **Green Affiliate** — trang khám phá chiến dịch affiliate trên Green Creator, clone giao diện trang chủ Green Creator. Mỗi FR/AC ánh xạ trực tiếp thành test case.

**Related Documents:**
- Overview: [`overview.md`](./overview.md)
- FE Creator (luồng tham gia + tạo link + báo cáo): [`../fe-display-generate-link-report-overview.md`](../fe-display-generate-link-report-overview.md)
- Admin Setup (chuẩn bị catalog): [`../admin-setup-overview.md`](../admin-setup-overview.md)
- PRD V2 affiliate (FR-T3-007 Browse chiến dịch): [`../prd-v2-2026-05-12.md`](../prd-v2-2026-05-12.md)

---

## Executive Summary

Green Creator hiện có 2 nhánh trên top switcher: **Gen Green** (đang chạy — nội dung) và **Green Seller (Coming soon)** (trống). Feature này biến nhánh thứ 2 thành **Green Affiliate** — một trang khám phá chiến dịch affiliate **clone y hệt giao diện trang chủ Green Creator**: hero giới thiệu + thanh tab partner + danh sách card bên dưới.

Đặc điểm cốt lõi: thanh tab partner dùng **thứ tự do backend quy định** (giống Green Creator hiện tại), và **chỉ hiển thị partner có chiến dịch affiliate active** — partner chưa có thì ẩn tab. Trang là **read-only**: creator browse, bấm vào card → chuyển sang trang chi tiết chiến dịch (luồng đã có ở FE Creator).

---

## Product Goals

### Business Objectives

1. **Kích hoạt nhánh Green Affiliate** đang trống, biến thành cửa vào chính thức cho nguồn thu nhập affiliate của creator.
2. **Tận dụng catalog đã chuẩn bị** (Admin Setup) — đưa chiến dịch affiliate của các partner ra trước creator.
3. **Tối thiểu hóa chi phí dev** bằng cách clone giao diện + component sẵn có của trang chủ Green Creator.

### Success Metrics

- Tỷ lệ creator vào tab Green Affiliate ít nhất 1 lần trong tháng đầu sau launch.
- Số creator bấm vào card chiến dịch (click-through từ trang khám phá → trang chi tiết).
- Bật affiliate cho 1 partner mới **không cần** thay đổi/deploy frontend (tab tự xuất hiện).

---

## Functional Requirements

---

### FR-001: Đổi tên nhánh "Green Seller" → "Green Affiliate"

**Priority:** Must Have

**Description:**
Nút nhánh thứ 2 trên top switcher của Green Creator đổi nhãn từ "Green Seller (Coming soon)" thành "Green Affiliate", bỏ badge "Coming soon", và trở thành nút điều hướng hoạt động.

**Acceptance Criteria:**
- [ ] Top switcher hiển thị 2 nút: "Gen Green" và "Green Affiliate".
- [ ] Nút "Green Affiliate" KHÔNG còn badge "Coming soon".
- [ ] Bấm "Green Affiliate" → điều hướng tới trang Green Affiliate (không còn trạng thái disabled/no-op).
- [ ] Nút "Green Affiliate" có trạng thái active (highlight) khi đang ở trang Green Affiliate; nút "Gen Green" active khi ở nhánh nội dung.
- [ ] Không còn chuỗi text "Green Seller" hay "Coming soon" nào hiển thị trên top switcher.

**Dependencies:** —

---

### FR-002: Hero giới thiệu Green Affiliate

**Priority:** Must Have

**Description:**
Phần đầu trang Green Affiliate là khối hero clone style trang chủ Green Creator: tiêu đề, tagline, đoạn mô tả ngắn về việc kiếm hoa hồng từ chia sẻ sản phẩm.

**Acceptance Criteria:**
- [ ] Hero hiển thị tiêu đề "Green Affiliate".
- [ ] Hero có tagline + đoạn mô tả ngắn (nội dung do content cung cấp, qua i18n, không hardcode).
- [ ] Layout, typography, màu sắc, hình trang trí khớp với hero trang chủ Green Creator (cùng design system).
- [ ] Hero responsive: hiển thị đúng trên desktop và tablet.

**Dependencies:** FR-001

---

### FR-003: Thanh tab partner — thứ tự do backend quy định

**Priority:** Must Have

**Description:**
Dưới hero là thanh tab partner, clone cơ chế thanh tab của nhánh Gen Green. Thứ tự các tab lấy **đúng theo thứ tự backend trả về** — frontend không tự sắp xếp lại.

**Acceptance Criteria:**
- [ ] Thanh tab hiển thị danh sách partner theo đúng thứ tự trong response của backend.
- [ ] Frontend KHÔNG sắp xếp lại (không alphabetize, không sort theo số campaign).
- [ ] Style thanh tab (font, khoảng cách, gạch chân tab active) khớp thanh tab nhánh Gen Green.
- [ ] Tab đầu tiên trong danh sách được chọn (active) mặc định khi mở trang.
- [ ] Tab active được highlight; bấm tab khác → chuyển nội dung danh sách bên dưới sang partner đó.

**Dependencies:** FR-002

---

### FR-004: Ẩn tab của partner chưa có chiến dịch affiliate active

**Priority:** Must Have

**Description:**
Chỉ partner có **ít nhất 1 chiến dịch affiliate active** (đã bật, chưa hết hạn) mới hiện tab. Partner không có chiến dịch active nào thì ẩn tab hoàn toàn.

**Acceptance Criteria:**
- [ ] Partner có ≥1 chiến dịch affiliate active → hiện tab.
- [ ] Partner có 0 chiến dịch affiliate active → KHÔNG hiện tab.
- [ ] Khi tất cả chiến dịch của một partner hết hạn/bị tắt → tab partner đó biến mất ở lần load kế tiếp.
- [ ] Khi backend bật affiliate cho partner mới → tab partner đó xuất hiện mà KHÔNG cần thay đổi/deploy frontend.
- [ ] Việc ẩn tab giữ nguyên thứ tự tương đối của các tab còn lại (FR-003).

**Dependencies:** FR-003

---

### FR-005: Danh sách chiến dịch affiliate trong tab

**Priority:** Must Have

**Description:**
Chọn một tab partner → bên dưới hiển thị danh sách card chiến dịch affiliate active của partner đó, bày phẳng theo style danh sách trang chủ Green Creator.

**Acceptance Criteria:**
- [ ] Mỗi chiến dịch hiển thị dạng card: banner/thumbnail, tên chiến dịch, mức hoa hồng, thưởng thêm (nếu có), thời gian chạy.
- [ ] Chỉ hiển thị chiến dịch active (đã bật, chưa hết hạn) của partner đang chọn.
- [ ] Danh sách scope đúng partner đang chọn — không lẫn chiến dịch của partner khác.
- [ ] Layout grid responsive (số cột theo breakpoint) khớp danh sách trang chủ Green Creator.
- [ ] Có skeleton/loading khi đang tải danh sách.

**Dependencies:** FR-004

---

### FR-006: Điều hướng từ card sang trang chi tiết chiến dịch

**Priority:** Must Have

**Description:**
Bấm vào một card chiến dịch → điều hướng sang trang chi tiết chiến dịch affiliate (luồng tham gia + tạo link đã định nghĩa ở FE Creator).

**Acceptance Criteria:**
- [ ] Bấm card → điều hướng tới trang chi tiết của đúng chiến dịch đó.
- [ ] Trang chi tiết nhận đúng định danh chiến dịch (campaign ID) từ card được bấm.
- [ ] Trang khám phá KHÔNG tự thực hiện tham gia/tạo link — chỉ điều hướng (read-only).

**Dependencies:** FR-005; FE Creator (trang chi tiết chiến dịch — đã có)

---

### FR-007: Empty state khi không có chiến dịch

**Priority:** Should Have

**Description:**
Xử lý trạng thái rỗng ở 2 cấp: toàn trang (không partner nào có affiliate) và trong tab (trường hợp biên).

**Acceptance Criteria:**
- [ ] Khi không có partner nào có chiến dịch active → toàn bộ thanh tab rỗng → hiển thị empty state toàn trang ("Các chiến dịch affiliate sắp ra mắt").
- [ ] Hero vẫn hiển thị bình thường kể cả khi trang ở trạng thái empty.
- [ ] (Biên) Nếu một tab được hiển thị nhưng danh sách rỗng tại thời điểm load → hiển thị empty state trong vùng danh sách thay vì màn hình trắng.

**Dependencies:** FR-004, FR-005

---

### FR-008: Đồng bộ tab đang chọn với URL

**Priority:** Should Have

**Description:**
Tab partner đang chọn được phản ánh trên URL để có thể chia sẻ/đánh dấu và giữ trạng thái khi refresh.

**Acceptance Criteria:**
- [ ] Đổi tab → URL cập nhật (param hoặc path phản ánh partner đang chọn).
- [ ] Mở URL có sẵn tham số partner → tab tương ứng được chọn khi load (nếu partner đó còn hiển thị).
- [ ] Tham số trỏ tới partner không còn hiển thị (đã ẩn tab) → fallback về tab đầu tiên.
- [ ] Refresh trang → giữ đúng tab đang chọn.

**Dependencies:** FR-003

---

## Non-Functional Requirements

---

### NFR-001: Performance — thời gian tải trang & chuyển tab

**Priority:** Must Have

**Description:**
Trang Green Affiliate tải nhanh và chuyển tab mượt.

**Acceptance Criteria:**
- [ ] Trang khám phá load và hiển thị nội dung < 3s ở điều kiện mạng thông thường.
- [ ] Chuyển tab partner phản hồi < 500ms (dùng cache nếu đã tải).

**Rationale:** Trải nghiệm khám phá phải mượt để creator không bỏ giữa chừng.

---

### NFR-002: Reuse design system Green Creator

**Priority:** Must Have

**Description:**
Toàn bộ UI dùng lại component + design tokens của trang chủ Green Creator, không tạo design ngôn ngữ mới.

**Acceptance Criteria:**
- [ ] Hero, thanh tab, card dùng cùng component/style nguồn với trang chủ Green Creator (tái sử dụng, không clone-paste lệch).
- [ ] Theme sáng/tối (nếu Green Creator hỗ trợ) hoạt động đồng nhất trên trang Green Affiliate.

**Rationale:** Giảm chi phí dev, đảm bảo nhất quán thị giác, giảm rủi ro UX.

---

### NFR-003: i18n — không hardcode text

**Priority:** Must Have

**Description:**
Mọi text hiển thị (nhãn nút, tiêu đề hero, tagline, empty state) đi qua hệ thống đa ngôn ngữ.

**Acceptance Criteria:**
- [ ] Không có chuỗi tiếng Việt/tiếng Anh hardcode trong code component.
- [ ] Có đủ key dịch cho tiếng Việt (mặc định) và tiếng Anh.

**Rationale:** Đồng bộ chuẩn i18n của Green Creator.

---

### NFR-004: Read-only & cô lập dữ liệu theo partner

**Priority:** Must Have

**Description:**
Trang chỉ đọc dữ liệu; danh sách trong mỗi tab được scope đúng partner ở backend.

**Acceptance Criteria:**
- [ ] Không có thao tác ghi (tạo/sửa/xóa/tham gia) phát sinh từ trang khám phá.
- [ ] Backend trả danh sách chiến dịch theo partner; không rò rỉ chiến dịch của partner khác trong response của tab đang chọn.
- [ ] Backend là nguồn quyết định partner nào hiển thị + thứ tự (frontend không tự suy luận từ nguồn khác).

**Rationale:** Đúng tinh thần read-only của tầng khám phá; tránh sai lệch dữ liệu.

---

### NFR-005: Compatibility — responsive desktop + tablet

**Priority:** Should Have

**Description:**
Hỗ trợ trình duyệt và kích thước màn hình theo chuẩn Green Creator.

**Acceptance Criteria:**
- [ ] Hiển thị đúng trên Chrome/Safari/Firefox/Edge phiên bản hiện hành.
- [ ] Layout responsive ở desktop (≥1024px) và tablet (≥768px).

**Rationale:** Đồng bộ phạm vi tương thích của Green Creator.

---

## Epics

---

### EPIC-001: Kích hoạt nhánh Green Affiliate (switcher + hero)

**Description:**
Đổi tên nhánh "Green Seller (Coming soon)" thành "Green Affiliate", bỏ "Coming soon", và dựng khối hero giới thiệu clone trang chủ Green Creator.

**Functional Requirements:**
- FR-001
- FR-002

**Story Count Estimate:** 2-3 stories

**Priority:** Must Have

**Business Value:** Mở cửa nhánh đang trống — tạo điểm vào chính thức cho affiliate.

---

### EPIC-002: Thanh tab partner động theo backend

**Description:**
Clone thanh tab partner với thứ tự do backend quy định và quy tắc ẩn tab partner chưa có chiến dịch active. Đồng bộ tab đang chọn với URL.

**Functional Requirements:**
- FR-003
- FR-004
- FR-008

**Story Count Estimate:** 3-4 stories

**Priority:** Must Have

**Business Value:** Cho phép bật affiliate partner mới không cần đụng frontend; giữ UX quen thuộc.

---

### EPIC-003: Danh sách chiến dịch & điều hướng

**Description:**
Hiển thị danh sách card chiến dịch affiliate trong mỗi tab, xử lý empty state, và điều hướng sang trang chi tiết.

**Functional Requirements:**
- FR-005
- FR-006
- FR-007

**Story Count Estimate:** 3-4 stories

**Priority:** Must Have

**Business Value:** Đưa catalog ra trước creator và dẫn họ vào luồng kiếm hoa hồng.

---

## User Stories (High-Level)

> Chi tiết user story sẽ tạo ở sprint planning (Phase 4).

- **EPIC-001:** Là creator, tôi muốn bấm vào nhánh "Green Affiliate" và thấy phần giới thiệu rõ ràng, để hiểu đây là nơi kiếm hoa hồng từ bán hàng.
- **EPIC-002:** Là creator, tôi muốn thấy danh sách partner đang có chương trình affiliate (không thấy partner trống), để khỏi mất công bấm vào tab rỗng.
- **EPIC-002:** Là vận hành, tôi muốn bật affiliate cho một partner mới và tab tự hiện ra, để không phải nhờ dev deploy lại frontend.
- **EPIC-003:** Là creator, tôi muốn duyệt các chiến dịch của một partner và bấm vào để xem chi tiết, để chọn chiến dịch phù hợp đem đi bán.

---

## User Personas

| Persona | Mô tả | Nhu cầu chính |
|---------|-------|---------------|
| **Creator Gen-Green** | Người sáng tạo nội dung trên Green Creator | Khám phá chiến dịch affiliate phù hợp để chia sẻ và kiếm hoa hồng |
| **Vận hành / Business** | Đội quản lý catalog affiliate | Kiểm soát partner nào "lên kệ" qua bật/tắt chiến dịch, không cần can thiệp frontend |

---

## User Flows

1. **Vào Green Affiliate:** Creator ở Green Creator → bấm nút "Green Affiliate" trên top switcher → trang Green Affiliate mở với hero + thanh tab partner (tab đầu tiên active) + danh sách chiến dịch.
2. **Khám phá theo partner:** Creator bấm một tab partner khác → danh sách bên dưới đổi sang chiến dịch của partner đó.
3. **Đi vào chi tiết:** Creator bấm một card chiến dịch → chuyển sang trang chi tiết chiến dịch (tham gia + tạo link — luồng FE Creator).

---

## Dependencies

### Internal Dependencies

- **Frontend Green Creator (React):** component hero, thanh tab partner, card danh sách của trang chủ để clone/tái sử dụng.
- **Admin Setup:** catalog chiến dịch affiliate + trạng thái active/expired ([`../admin-setup-overview.md`](../admin-setup-overview.md)).
- **FE Creator:** trang chi tiết chiến dịch (đích điều hướng của FR-006) ([`../fe-display-generate-link-report-overview.md`](../fe-display-generate-link-report-overview.md)).

### External Dependencies

- **at-core (Go middleware):** endpoint trả danh sách partner (có thứ tự) + chiến dịch affiliate active theo partner; at-core proxy tới nguồn dữ liệu Scalef nếu cần.

---

## Assumptions

- Hệ thống đã có sẵn nhiều partner đang chạy trên Green Creator (VinFast, VinWonders, Green SM, VEC, Vinhomes...).
- Backend có (hoặc sẽ có) khả năng trả danh sách partner kèm thứ tự + cờ "có chiến dịch affiliate active".
- Trang chi tiết chiến dịch (tham gia + tạo link) đã/đang được làm ở FE Creator — feature này chỉ là cửa khám phá dẫn vào.
- "Active" = chiến dịch đã bật và chưa qua `end_date` (theo logic Admin Setup hiện tại).

---

## Out of Scope

- Nhánh **Gen Green** (nội dung) — không thay đổi.
- Tạo/sửa/bật-tắt chiến dịch affiliate (thuộc **Admin Setup**).
- Luồng **tham gia chiến dịch + tạo link + báo cáo hoa hồng** (thuộc **FE Creator**).
- **Liên kết tài khoản Scalef** (thuộc **Account Linking**).
- Tìm kiếm / sắp xếp / lọc nâng cao trong tab (chưa làm ở giai đoạn đầu — xem Open Questions).
- Gợi ý chiến dịch theo nội dung creator (future, cần ML).

---

## Open Questions

1. Tên hiển thị nhánh chốt là **"Green Affiliate"** — có cần đồng bộ lại các tài liệu cũ đang dùng từ "Green Seller" không?
2. Hero Green Affiliate có hiển thị các con số tổng quan như trang chủ Green Creator (tổng chiến dịch, hoa hồng đã trả...) không, hay chỉ phần giới thiệu?
3. Trong một tab partner, giai đoạn đầu có cần tìm kiếm / sắp xếp danh sách không, hay bày phẳng là đủ?
4. Backend đã có endpoint trả partner kèm cờ "có affiliate active" chưa, hay cần bổ sung mới ở at-core?

---

## Approval & Sign-off

### Stakeholders

| Vai trò | Người | Trách nhiệm |
|---------|-------|-------------|
| Product Owner | vinhnguyen | Chốt scope + tên gọi |
| Engineering Lead | TBD | Clone frontend + endpoint backend |
| Design Lead | TBD | Xác nhận reuse design system |
| QA Lead | TBD | Sinh test case từ FR/AC |

### Approval Status

- [ ] Product Owner
- [ ] Engineering Lead
- [ ] Design Lead
- [ ] QA Lead

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-27 | vinhnguyen | Initial PRD — 8 FRs (6 Must, 2 Should), 5 NFRs, 3 epics. Clone trang chủ Green Creator cho nhánh Green Affiliate, tab partner do backend quy định + ẩn tab rỗng, read-only. |

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) |
|---------|-----------|-------------------------|-------------------|
| EPIC-001 | Kích hoạt nhánh Green Affiliate | FR-001, FR-002 | 2-3 |
| EPIC-002 | Thanh tab partner động theo backend | FR-003, FR-004, FR-008 | 3-4 |
| EPIC-003 | Danh sách chiến dịch & điều hướng | FR-005, FR-006, FR-007 | 3-4 |

---

## Appendix B: Prioritization Details

**Functional Requirements (8):**
- Must Have (6): FR-001, FR-002, FR-003, FR-004, FR-005, FR-006
- Should Have (2): FR-007, FR-008
- Could Have (0): —

**Non-Functional Requirements (5):**
- Must Have (4): NFR-001, NFR-002, NFR-003, NFR-004
- Should Have (1): NFR-005

**Tổng:** 13 requirements. Estimated stories: 8-11.
