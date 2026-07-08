# PRD: Popup hiển thị đúng đối tác đã chọn

**Project:** Gen-Green (VCreator)
**Date:** 2026-07-08
**Author:** Dang Dinh
**Status:** Draft — Awaiting Approval (3 đề xuất, §7)
**Version:** 1.0
**Tài liệu kỹ thuật:** `tech-analysis-popup-partner-targeting.md` (lưu tại repo vcreator) (phân tích đầy đủ) · `tech-spec.md` (spec implement)

---

## 1. Executive Summary

Ops tạo popup cho **Green SM** và chọn đối tác trong form admin → popup **không hiển thị ở bất kỳ đâu**. Ops phải bỏ chọn đối tác để popup hiện → popup **tràn toàn website**, kể cả trang VinWonders, VinFast → rủi ro khiếu nại vì các đối tác là bộ phận độc lập. Hai hiện tượng là **một lỗi duy nhất** + hệ quả workaround.

**Nguyên nhân:** trang đối tác khi lấy popup không gửi kèm id partner → hệ thống chỉ trả popup dùng chung. Admin lưu đúng, backend lọc đúng — chỉ thiếu 1 tham số ở website. Lỗi có từ ngày bàn giao code, bộc lộ im lặng khi Ops lần đầu dùng tính năng chọn đối tác.

**Cách fix:** website gửi kèm id partner khi lấy popup — theo đúng cách banner trang đối tác đang làm. ~35 dòng code, không đổi API, không đụng dữ liệu, 1 dev ~0.5 ngày.

---

## 2. Business Objectives

| # | Objective | Success Metric |
|---|-----------|----------------|
| 1 | Popup gắn đối tác X chỉ hiện trên trang đối tác X | 0 popup hiện sai trang |
| 2 | Hết rủi ro khiếu nại chéo giữa các đối tác | 0 khiếu nại về popup nhầm đối tác |
| 3 | Ops setup đúng ngay lần đầu, không cần workaround | 0 popup dùng chung tạo ra chỉ vì workaround |

## 3. User Personas

| Persona | Nhu cầu |
|---------|---------|
| **Ops/Admin** | Chọn Green SM → popup hiện đúng trang Green SM |
| **Đối tác (Brand)** | Trang mình không hiện popup của đối tác khác |
| **Creator/Visitor** | Popup đúng ngữ cảnh trang đang xem, không bị spam |

---

## 4. Functional Requirements

### FR-001: Trang đối tác lấy popup theo id partner — **Must Have**

Gồm 3 thay đổi, tất cả ở website (frontend-green):
1. **Gửi kèm id partner khi lấy popup** (fix chính): truyền thêm tham số `partner` = id partner (`_id`, không phải slug).
2. **Đổi thời điểm gọi:** chỉ lấy popup sau khi đã xác định trang thuộc đối tác nào (chuyển vào callback `getPartnerDetail`).
3. **Reset cờ hiển thị trước mỗi lần lấy:** cờ hiện chỉ bật không tắt → user chuyển trang không reload sẽ không thấy popup dù dữ liệu đúng.

**AC:**
- [ ] Vào trang Green SM → request lấy popup có `partner=<id 24-hex>`
- [ ] Chuyển trang không reload (trang chủ → trang đối tác) popup vẫn hiện được
- [ ] Trang chủ giữ nguyên, không truyền partner

### FR-002: Hiển thị đúng theo đối tác — **Must Have**

Quy tắc: mỗi lượt vào trang chỉ hiện **1 popup**. "Popup chung" = không gắn đối tác; "popup riêng" = gắn 1 đối tác.

| Case | Popup đang chạy | Trang chủ | Trang Green SM | Trang VinWonders |
|---|---|---|---|---|
| 1 | Chỉ 1 popup riêng Green SM | — | Popup Green SM | — |
| 2 | Chỉ 1 popup chung | Popup chung | Popup chung *(đề xuất 1)* | Popup chung *(đề xuất 1)* |
| 3 | Popup chung + popup riêng Green SM | Popup chung | **Popup Green SM** *(đề xuất 2)* | Popup chung |
| 4 | 2 popup cùng riêng Green SM | — | Popup "Thứ tự" cao hơn | — |
| 5 | Popup riêng Green SM + riêng VinWonders | — | Popup Green SM | Popup VinWonders |

**AC:**
- [ ] 5 case trên đúng như bảng (case 2, 3 theo kết quả phê duyệt §7)
- [ ] Admin đổi đối tác của popup → trang cũ ngừng hiện trong ≤ 2 phút

> Lưu ý cho case 3: mỗi lượt chỉ hiện 1 popup, không có cơ chế luân phiên — khi popup riêng đang chạy thì popup chung không có suất hiện trên trang đối tác đó cho đến khi chiến dịch riêng kết thúc. Đây là hành vi có chủ đích của cách làm này.

### FR-003: Popup riêng thắng popup chung trên trang đối tác — **Should Have** *(chờ đề xuất 2)*

Backend xếp popup riêng lên trước khi trang đối tác có cả hai loại (~5 dòng).
**AC:** [ ] Case 3 hiện popup riêng bất kể "Thứ tự".

### FR-004: Sang trang đối tác thấy ngay popup của đối tác — **Should Have** *(chờ đề xuất 3)*

Tách bộ nhớ "đã xem popup" theo từng trang thay vì dùng chung toàn site (~10 dòng).
**AC:** [ ] Vừa thấy popup trang chủ → vào trang Green SM vẫn thấy popup Green SM. [ ] Cùng 1 trang không hiện lặp trong cùng khung giờ.

## 5. Non-Functional Requirements

- **NFR-001:** Không đổi API, không migration dữ liệu — popup đã tạo chạy đúng ngay sau deploy.
- **NFR-002:** Thay đổi từ admin phản ánh ra website ≤ 2 phút (cache hiện có).
- **NFR-003:** Không regression: banner đối tác, popup hoàn thiện hồ sơ, thông báo trang chủ hoạt động như cũ; build FE + BE pass.

---

## 6. Epics & Prioritization

| Epic | FRs | Priority | Effort |
|------|-----|----------|--------|
| EPIC-001: Fix targeting popup theo đối tác | FR-001, FR-002 | Must | ~0.5 ngày |
| EPIC-002: Ưu tiên hiển thị + bộ nhớ theo trang | FR-003, FR-004 | Should (chờ §7) | ~0.25 ngày |

## 7. Đề xuất cần Sếp phê duyệt

| # | Nội dung cần quyết định | Đề xuất | Nếu không duyệt | Quyết định |
|---|------------------------|---------|-----------------|------------|
| 1 | Popup **chung** có được hiện trên trang đối tác không? | **Có** — giữ kênh thông báo toàn hệ thống | Popup chung chỉ hiện trang chủ. **Phạm vi sửa tăng đáng kể** (đổi logic dùng chung với banner) — team báo lại effort | ☐ Duyệt ☐ Không |
| 2 | Trang đối tác có cả popup chung + riêng → **ưu tiên popup riêng**? (FR-003) | **Có** — tránh popup chung đè popup chiến dịch của đối tác | Hiện theo "Thứ tự" Ops tự đặt — popup chung có thể đè popup riêng nếu đặt nhầm | ☐ Duyệt ☐ Không |
| 3 | User vừa thấy popup trang chủ → sang trang đối tác **thấy ngay** popup đối tác? (FR-004) | **Có** — hiện tại phải chờ sang khung giờ mới | Giữ hiện tại: mỗi khung giờ chỉ 1 popup toàn site, popup đối tác dễ bị bỏ lỡ | ☐ Duyệt ☐ Không |

**Đồng ý cả 3 → phản hồi "OK theo đề xuất", team triển khai luôn.** Mục 2/3 không duyệt không ảnh hưởng fix chính; mục 1 không duyệt cần báo lại effort trước khi làm.

## 8. Out of Scope

- Popup trên trang chi tiết sự kiện (hiện không có — là chủ đích)
- Lỗi tương tự tiềm ẩn ở loại tin "thông báo trang chủ"/"danh sách trang chủ" (ghi nhận, xử lý riêng nếu cần)
- Đổi tần suất hiện popup, nhiều popup cùng lúc, sửa form admin
- **Luân phiên popup chung/riêng** (bộ nhớ theo từng popup): không làm — cách làm dừng ở tách bộ nhớ theo trang (FR-004)

## 9. Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| QA test lại tưởng "chưa fix" (popup chỉ hiện lại mỗi khung giờ) | Test bằng tab ẩn danh / xóa bộ nhớ trình duyệt mỗi lượt |
| Bỏ sót thay đổi 3 của FR-001 → fix "lúc được lúc không" tùy đường vào trang | Đã đưa vào scope bắt buộc + AC riêng |
| Sau deploy Ops vẫn để popup theo kiểu workaround cũ | Thông báo Ops gắn lại đúng đối tác cho popup đang chạy |

## 10. Nghiệm thu

- [ ] Popup gắn Green SM chỉ hiện trang Green SM; không hiện trang chủ/đối tác khác
- [ ] Popup chung hiện đúng theo kết quả phê duyệt §7
- [ ] 5 case ở FR-002 pass trên desktop + mobile
- [ ] Regression NFR-003 pass

---

## Appendix: Code Impact

| File | Thay đổi | FR | Effort |
|------|----------|----|--------|
| `frontend-green/src/pages/partner-home/index.tsx` | Truyền `partner` + chuyển thời điểm gọi + reset cờ (~15 dòng) | FR-001 | S |
| `frontend-green/src/pages/main-home/index.tsx` | Reset cờ đồng bộ (~3 dòng) | FR-001 | S |
| `backend/pkg/public/service/news.go` | Xếp popup riêng lên trước (~5 dòng) | FR-003 | S |
| `frontend-green/src/utils/storage.ts` + 2 trang | Bộ nhớ "đã xem" theo trang (~10 dòng) | FR-004 | S |

*Theo format PRD BMAD Method v6 — chi tiết root cause, phương án so sánh, flow diagram, edge cases: `tech-analysis-popup-partner-targeting.md` (lưu tại repo vcreator)*
