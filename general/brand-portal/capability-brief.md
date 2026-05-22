# Brand Portal — Định hình chức năng & so sánh kiến trúc (3 dự án)

**Từ:** AccessTrade
**Dành cho:** Định phạm vi chức năng nội bộ — đội sản phẩm & stakeholder
**Phạm vi:** Brand portal multi-tenant cho 3 dự án — Ambassador (SaaS), Techcombank (Enterprise), VinGroup/vCreator (Enterprise)
**Cập nhật:** 2026-05-22

---

## 0. Tài liệu này dùng để làm gì

Bản định hình chức năng nội bộ, không phải tài liệu bán hàng. Hai mục tiêu:
1. Chốt **brand portal nên có gì** và **ranh giới với admin operation portal**.
2. Cân nhắc **lợi-hại của việc tách brand portal thành app riêng** so với **giữ brand dùng chung admin operation portal hiện tại** (brand đăng nhập vào chính admin đó, chỉ ẩn/hiện theo quyền).

Trạng thái mỗi năng lực ghi trung thực: **[Đã có]** / **[Đang làm]** / **[Roadmap]**.

---

## 1. Trạng thái hiện tại — 3 dự án xuất phát rất khác nhau

Đây là dữ kiện quan trọng nhất: cùng câu hỏi "tách hay không tách", nhưng điểm xuất phát mỗi nơi một khác.

| Dự án | Mô hình | Brand portal hiện tại | Brand xem báo cáo bằng cách nào |
|---|---|---|---|
| **Techcombank** (Enterprise) | 1 brand | ✅ Có `dashboard/` **tách riêng** (Next.js) | Portal độc lập, auth riêng |
| **vCreator / VinGroup** (Enterprise) | 1 brand | ❌ Chưa tách gì — brand xem **trong `admin/`** chung với operations. (`frontend/` là **creator portal**, không phải brand) | Đăng nhập thẳng admin |
| **Ambassador** (SaaS) | Nhiều brand (13 branded instances: anker, hdbank, mbbank, vng, vpbank, yody…) | ❌ Không có self-service brand | Không có; ops xem hộ qua `admin/` |

Kết luận trạng thái: **TCB đã tách rồi**, **vCreator chưa tách** (brand đang dùng chung chính admin operation portal — tức Phương án B đang chạy sẵn), **Ambassador chưa có self-service**. "Brand portal tách riêng" hiện chỉ là thực tế ở TCB.

Điểm chung kỹ thuật cả 3: backend đều có entity **`Partner`** (tenant) + cơ chế filter theo partner của staff. Hạ tầng multi-tenant **đã sẵn ở backend**, khác biệt nằm ở tầng portal.

---

## 2. Hai phương án đang cân nhắc

**Phương án A — Tách brand portal thành app riêng** (mô hình TCB `dashboard/`)
Brand đăng nhập vào một ứng dụng độc lập, codebase riêng, chỉ chứa chức năng dành cho brand (xem báo cáo, tài chính, import). Admin operation portal vẫn của riêng operations.

**Phương án B — Giữ brand dùng chung admin operation portal**
Brand đăng nhập vào chính admin portal mà operations đang dùng; phân quyền (RBAC) ẩn/hiện màn hình. Brand thấy một tập con của admin. Đây là mô hình mà cả 3 backend đã hỗ trợ sẵn (`Staff.Partner` + role).

---

## 3. So sánh lợi — hại

### Phương án A — Tách brand portal riêng

**Lợi**
- **Bảo mật theo thiết kế** — brand không bao giờ chạm vào code/route/màn hình của operations. Rò rỉ thao tác nguy hiểm (duyệt-hủy đối soát, chỉnh budget) gần như không thể vì *chúng không tồn tại trong app*. Cô lập ở tầng codebase, không chỉ tầng quyền.
- **UX đúng đối tượng** — brand thấy giao diện gọn, ngôn ngữ business, không bị ngợp bởi hàng chục menu vận hành. Việt hóa / branding theo tenant dễ.
- **Nhịp phát triển độc lập** — đổi UI brand không sợ vỡ màn hình ops và ngược lại. Hai đội/hai vòng deploy tách bạch.
- **Multi-tenant SaaS sạch** — với Ambassador (13 brand), branded instance theo tenant là tự nhiên trên một app brand riêng; nhét branding-per-tenant vào admin ops sẽ rối.
- **Giảm bề mặt rủi ro** — admin ops là công cụ quyền lực; càng ít người ngoài operations đăng nhập vào đó càng an toàn.

**Hại**
- **Trùng lặp code & chi phí 2 lần** — list, table, filter, auth, i18n… phải dựng lại ở app brand. Một thay đổi data model có thể phải sửa 2 nơi.
- **Đồng bộ logic khó** — quy tắc hiển thị/định dạng số liệu phải khớp giữa 2 app, dễ lệch (đối soát hiện một số ở admin, số khác ở portal là thảm họa niềm tin).
- **Chi phí hạ tầng & vận hành** — thêm 1 app để build, deploy, monitor, vá bảo mật. Nhân với 3 dự án.
- **Phân mảnh khi nhân lên** — nếu mỗi dự án một brand portal riêng (như TCB hiện tại), 3 codebase brand portal lệch nhau dần, đúng vết xe fork TCB↔vCreator đang gặp.

### Phương án B — Brand dùng chung admin portal (RBAC)

**Lợi**
- **Một codebase, một nguồn sự thật** — số liệu, logic, định dạng chỉ có một chỗ; không lệch số giữa 2 app. Backend đã filter theo `Partner` sẵn → tốn ít việc nhất để bật.
- **Nhanh & rẻ trước mắt** — tái dùng toàn bộ list/table/auth có sẵn; chỉ cần thêm role brand + ẩn/hiện menu.
- **Bảo trì 1 nơi** — vá lỗi, đổi model, thêm cột chỉ làm một lần.

**Hại**
- **Bảo mật mong manh** — cô lập chỉ ở tầng RBAC. Một lỗi phân quyền, một route quên chặn, một nút render nhầm → brand chạm được thao tác nguy hiểm (duyệt-hủy đối soát, chỉnh budget). Với thứ *ghi tiền*, đây là rủi ro khó chấp nhận. Admin operation portal vốn không thiết kế cho người ngoài.
- **UX sai đối tượng** — brand đăng nhập vào công cụ vận hành đầy menu lạ; phải ẩn rất nhiều thứ, dễ sót, dễ lộ. Trải nghiệm "đây rõ ràng không phải làm cho tôi".
- **Vướng nhịp phát triển** — đổi gì cho brand cũng phải hồi quy toàn bộ admin ops; rủi ro vỡ công cụ vận hành đang chạy thật.
- **Branding-per-tenant khó** — Ambassador 13 brand mà cùng một admin thì việc tùy biến thương hiệu/màu/logo theo tenant rất gượng.
- **Audit & trách nhiệm mờ** — chung một app, khó tách bạch "ai (brand hay ops) đã làm gì".

---

## 4. Trục quyết định: rủi ro **ghi tiền** vs chi phí **trùng lặp**

Toàn bộ cân nhắc quy về một câu: *brand được phép làm gì trong app?*

- Nếu brand **chỉ đọc + 1-2 hành động không ghi tiền** (như định hướng hiện tại: xem báo cáo, import influencer) → bề mặt rủi ro của Phương án B **nhỏ lại đáng kể**, vì kể cả lộ thì cũng không có thao tác ghi tiền để lộ. Lúc này lợi thế "1 codebase" của B rất hấp dẫn.
- Nếu lộ trình sẽ **mở dần quyền ghi tiền** cho brand → Phương án A (cô lập tầng code) trở nên đáng giá, vì RBAC không đủ an toàn cho thao tác chạm tiền.

> Nguyên tắc đã chốt ở các vòng trước: brand **chỉ được làm hành động (a) không ghi tiền và (b) sai sửa được dễ**. Chính nguyên tắc này quyết định kiến trúc: giữ brand read-only → B đủ an toàn; định mở quyền ghi tiền → cần A.

---

## 5. Khuyến nghị theo từng dự án

Không nên ép một khuôn cho cả 3 vì điểm xuất phát và mô hình khác nhau:

| Dự án | Hiện trạng | Khuyến nghị | Lý do |
|---|---|---|---|
| **Techcombank** | Đã tách `dashboard/` | **Giữ tách (A)** | Đã có, đừng quay lui. TCB là nơi định mở quyền (import) → cô lập code đáng giá. Làm chuẩn để 2 dự án kia tham chiếu. |
| **vCreator** | Brand dùng chung admin (Phương án B sẵn) | **Giữ B trước mắt, tách (A) khi mở quyền** | Brand đang xem trong admin ops — nếu chỉ read-only thì B đủ an toàn tạm thời. Khi cần UX riêng hoặc mở quyền → tách, port từ TCB. |
| **Ambassador (SaaS)** | Chưa có brand self-service | **Tách riêng (A) ngay từ đầu** | SaaS 13 brand: branding-per-tenant + cô lập dữ liệu là bắt buộc. Nhét vào admin ops sẽ không scale. |

**Định hướng dài hạn:** một **brand-portal core dùng chung** (read-only + capability bật-tắt theo tenant), triển khai cho cả 3 dự án thay vì 3 codebase lệch nhau — tránh lặp lại vết fork TCB↔vCreator. TCB `dashboard/` là ứng viên làm gốc.

---

## 6. Năm trụ năng lực (áp cho cả 3, bật theo tenant)

### Trụ 1 — Minh bạch hiệu quả: analytics & báo cáo  `[TCB ~80% (portal riêng) / vCreator có trong admin / Ambassador chưa]`
Dashboard KPI, phân tích theo campaign/nền tảng/creator, xuất báo cáo. Thiếu: ROI/burn-rate, báo cáo theo kỳ đối soát.

### Trụ 2 — Minh bạch tài chính: budget, đối soát, thanh toán  `[Roadmap cả 3 — khoảng trống lớn nhất]`
Budget overview, reconciliation *viewer* (chỉ xem — chốt số do ops), payment timeline. Brand **không** xác nhận/khiếu nại đối soát, **không** tự rút tiền ở giai đoạn này.

### Trụ 3 — Nạp dữ liệu đầu vào: Import influencer / profile  `[TCB đang làm; capability theo tenant]`
Hành động write duy nhất brand được làm. Enrichment async qua `portal → at-core → influence-meter`, đối soát import, lịch sử. TCB có nhu cầu; vCreator/Ambassador hiện chưa → để tắt.

### Trụ 4 — Cô lập đa tenant: mỗi brand một không gian riêng  `[Backend cả 3 có, tầng portal khác nhau]`
Cô lập dữ liệu (Partner field), RBAC trong tenant (brand-admin vs brand-viewer), capability theo tenant. Ambassador là nơi yêu cầu khắt khe nhất (13 brand).

### Trụ 5 — Cổng mở quyền có kiểm soát  `[Khung quyết định — chưa mở]`

| Hành động | Ghi tiền? | Sai sửa được dễ? | Mở cho brand? |
|---|---|---|---|
| Xem báo cáo | Không | — | ✅ Đã mở |
| Import influencer/profile | Không | ✅ (xóa / re-import) | ✅ Mở (tenant có nhu cầu) |
| Flag content để ops xem lại | Không | ✅ (chỉ gợi ý) | 🟡 Khi có nhu cầu thật |
| Duyệt / hủy video | Không trực tiếp | ⚠️ Ảnh hưởng payout | 🔴 Giữ ở ops |
| Duyệt / hủy đối soát | **Có** | 🔴 Khó nghịch, lệch số | 🔴 Giữ ở ops |
| Yêu cầu rút tiền | **Có** | 🔴 | 🔴 Ops thực thi |

> Quy tắc: **chỉ mở cho brand hành động không ghi tiền + sai sửa được dễ.** Quy tắc này cũng là thứ quyết định chọn Phương án A hay B (mục 4).

---

## 7. Bước tiếp theo

- Chốt: brand giai đoạn này có **chỉ read-only + import** không? Nếu có → Phương án B đủ an toàn về bảo mật, cân nhắc chi phí trùng lặp; nếu định mở quyền ghi tiền → nghiêng Phương án A.
- Quyết định có làm **brand-portal core dùng chung** cho cả 3 dự án (lấy TCB `dashboard/` làm gốc) hay để mỗi dự án tự đi.
- Với vCreator: lên kế hoạch tách phần brand ra khỏi creator frontend.
- Làm rõ cơ chế import TCB (upload file vs dán link/handle để hệ tự crawl).
