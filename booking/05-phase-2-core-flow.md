# Phase 2 — Core flow (Brief · Booking request · E-contract)

> Phase 2 = luồng lõi sau khi đã có shortlist (Phase 1). Bản chất là **invite-driven**: từ shortlist → gửi lời mời → creator nhận → ký hợp đồng → vào làm nội dung.
> *(Sprint của Phase 2 chia sau khi chốt scope.)*

---

## 1. Brief là gì

**Brief = bản đặc tả công việc (job spec) brand giao cho creator** — "creator phải làm gì, ở đâu, bao nhiêu, deadline khi nào, được trả gì". Tách bạch với Job/Event (vốn là khung chứa ngân sách + điều kiện).

> Hiện hệ thống chưa có brief có cấu trúc — nội dung công việc đang nằm rải rác (tên, mô tả, hướng dẫn, hashtag…). Phase 2 nâng lên thành **một khối brief có cấu trúc**.

### Brief gồm các nhóm thông tin

| Nhóm | Gồm |
|------|-----|
| **Thông tin chung** | tiêu đề, mô tả/mục tiêu chiến dịch, thương hiệu, brand guideline (do/don't) |
| **Deliverables** | loại nội dung (video/reels/post), nền tảng, số lượng, định dạng |
| **Yêu cầu nội dung** | hashtag bắt buộc, mention, link gắn, key message, tài nguyên dùng |
| **Timeline** | ngày bắt đầu/kết thúc, deadline đăng bài, hạn phản hồi lời mời |
| **Thù lao (compensation)** | giá — Phase 2 invite-driven dùng **giá cố định per-job** (đem điền vào hợp đồng) |
| **Điều khoản (terms)** | exclusivity, quyền sử dụng nội dung, lịch thanh toán, hủy/phạt |
| **Metadata** | người tạo, thời điểm, **version** (brief có thể đổi khi thương lượng) |

### Enroll requirement — KHÁC brief

> Đây là điểm dễ nhầm, làm rõ:

| | **Enroll requirement** | **Brief** |
|---|---|---|
| Là gì | **Điều kiện THAM GIA** — creator có đủ tiêu chuẩn để được mời/tham gia không | **Nội dung công việc** — creator phải làm gì, được trả gì |
| Gồm | email/phone/social/min-follower/account-age | deliverable/hashtag/timeline/giá/điều khoản |
| Trạng thái | ✅ đã có ~80% (struct điều kiện tham gia trong hệ thống) | 🆕 build mới (chưa có cấu trúc) |

**Build thêm cho enroll requirement (SHOULD):** ngưỡng follower **đa nền tảng** (hiện chỉ Facebook) + chính sách duyệt (`auto-pass | open | review`). Với invite-driven thường **auto-pass** (đã được chọn từ shortlist, bỏ qua self-check); apply-driven thì giữ review.

---

## 2. Luồng INVITE đầy đủ (đúng insight: shortlist → mời → nhận → ký)

```
[Phase 1: Shortlist theo khách hàng]
            │
            ▼
   Admin/Brand chọn creator (đơn hoặc hàng loạt) + chọn/tạo Brief cho Job
            │ gửi lời mời
            ▼
   Tạo Invite (pending) ──► Notification + EMAIL tới creator (kèm deadline)
            │
            ▼
   Creator nhận lời mời (Email magic-link / Portal) → xem Brief + thù lao
            │
   ┌────────┼──────────┬─────────────┬────────────┐
   ▼        ▼          ▼             ▼            ▼
[ACCEPT] [REJECT] [COMMENT/      [KHÔNG       [HẾT HẠN]
   │        │      THƯƠNG LƯỢNG]  PHẢN HỒI]      │
   │     →báo     →brand sửa     →reminder    →auto close
   │     brand    offer/brief    lần 1,2       +báo brand
   │              →gửi lại        →hết hạn
   │              (version++)
   ▼
   Sinh E-CONTRACT per-job (tự điền: brief + giá + thông tin KYC creator)
            │
            ▼
   Creator ký số (OTP/eSign)
   ┌────────┴────────┐
   ▼                 ▼
[SIGNED]      [không ký / hết hạn ký]
   │                 │
   ▼              →báo brand
   Kích hoạt tham gia chính thức → Job vào luồng làm nội dung
```

### Trạng thái cần theo dõi
- **Invite:** `pending → accepted | rejected | negotiating | expired | cancelled`
- **Contract:** `pending_signature → signed | rejected | expired`
- **Tham gia (enroll):** thêm `status / invitedAt / respondedAt / invitedBy / source(invite|apply)` — *hiện chưa có, cần thêm.*

---

## 3. Các CASE (đúng các trường hợp bạn nêu)

| Case | Xử lý |
|------|-------|
| **Accept** | Invite→accepted. Tự sinh hợp đồng (điền brief + giá + KYC). Chuyển sang bước ký. Báo brand. *Chưa enroll chính thức cho tới khi ký xong* (tránh nhận job mà không ký). |
| **Reject** (từ chối) | Invite→rejected, lưu lý do (tùy chọn). Báo brand. Không tạo hợp đồng. Brand mời creator khác. Slot/ngân sách giải phóng. |
| **Comment / thương lượng** | Invite→negotiating, lưu comment (xin tăng giá / đổi deliverable / đổi deadline). Brand: chấp nhận (sửa offer/brief → version mới → gửi lại) / giữ nguyên / hủy. **Cần giới hạn số vòng** tránh loop. Lưu lịch sử thương lượng. |
| **Không phản hồi** | Invite vẫn pending. Gửi reminder (lần 1, lần 2 trước deadline). Vẫn im → rơi vào hết hạn. |
| **Hết hạn phản hồi** | Invite→expired (tự động). Báo brand. Slot giải phóng. Cho re-invite hoặc mời người khác. |
| **Accept nhưng không ký** | Hợp đồng có deadline ký riêng. Quá hạn→expired. Báo brand. Tham gia **không** kích hoạt vì chưa ký. |
| **Ký xong** | Hợp đồng→signed (lưu bằng chứng ký + PDF). Kích hoạt tham gia chính thức (source=invite). Job vào luồng nội dung. → **Đây là điểm enroll chính thức** cho luồng invite. |
| **Brand hủy lời mời** (trước khi creator phản hồi) | Invite→cancelled. Báo creator. Hủy hợp đồng nếu đã sinh. *Không* cho hủy sau khi đã ký. |
| **Creator chưa có tài khoản** (chỉ có trong shortlist/import) | Gửi mời qua **email magic-link** → click → đăng ký/đăng nhập → mới xem brief & ký. *(Đây là cầu nối Phase 1 ↔ Phase 2 — xem mục 5.)* |

---

## 4. E-contract per-job

> Engine ký số (OTP/eSign/PDF) **đã có sẵn** (đang dùng cho hợp đồng KYC creator) — tái dùng, không viết lại.

| Tái dùng (đã có) | Build mới |
|------------------|-----------|
| Toàn bộ pipeline ký (OTP + eSign + xuất PDF) | **Loại hợp đồng mới per-job** (hiện chỉ có 1 loại KYC chung) |
| Thông tin KYC creator (tên/bank/tax/ID) để điền sẵn bên creator | **Template hợp đồng động** điền theo job (tên job, giá, điều khoản) |
| Cơ chế lấy/lưu PDF | **Lớp điền template** từ brief + giá + KYC → hợp đồng |
| | **Đóng băng "brief snapshot"** vào hợp đồng (giữ đúng điều khoản lúc ký) |

> ⚠️ **Phụ thuộc ngoài:** việc ký số gọi tới một dịch vụ ký riêng. Thêm loại hợp đồng + template per-job **phụ thuộc đội sở hữu dịch vụ đó** — cần xác nhận timeline (xem câu hỏi business).

---

## 5. Creator nhận lời mời: EMAIL-first (khuyến nghị)

> Đúng như bạn nêu: "creator nhận trên portal hoặc email". Khuyến nghị Phase 2 đi **email-first**, portal đầy đủ để phase sau.

**Lý do:**
1. **Creator import (Phase 1) chưa có tài khoản** — portal đòi đăng nhập trước → chặn ngay bước nhận mời. **Email magic-link** cho phép nhận → xem brief → accept/reject mà chưa cần tài khoản đầy đủ (đăng ký khi cần ký).
2. **Nhanh** — tận dụng email + notification sẵn có, chỉ thêm template + vài endpoint nhận phản hồi.
3. **Hợp luồng invite** — lời mời là sự kiện đẩy (push), email/notification là kênh tự nhiên.

→ **Creator Portal dashboard đầy đủ** (Inbox lời mời / Bookings / Contracts) là **SHOULD — phase sau** (2.5 hoặc 3). Phase 2 dùng email-link + push notification.

---

## 6. MUST / SHOULD

**MUST:**
- Model **Brief** có cấu trúc (deliverable/timeline/giá/điều khoản/version).
- Model **Invite** (job + creator + trạng thái + offer + deadline + lịch sử comment).
- Model **Hợp đồng per-job** (tách khỏi hợp đồng KYC) + đóng băng brief snapshot.
- **Loại hợp đồng + template per-job** ở dịch vụ ký (phụ thuộc đội ngoài) — tái dùng pipeline ký.
- Thêm field trạng thái/invite vào bản ghi tham gia (phân biệt invite vs apply).
- **Email magic-link** nhận lời mời + endpoint accept/reject/comment.
- Các loại thông báo mới (mời gửi/nhận/từ chối, thương lượng, chờ ký, đã ký).
- **Tác vụ định kỳ** xử lý reminder + tự hết hạn invite/hợp đồng.
- **Chống trùng** lời mời (1 cặp job+creator chỉ 1 invite đang hoạt động) + chỉ kích hoạt tham gia **sau khi ký xong**.

**SHOULD:**
- Chính sách duyệt enroll (auto-pass cho invite-driven).
- Điều kiện tham gia đa nền tảng.
- Creator Portal dashboard đầy đủ (phase sau).
- Lịch sử/giới hạn vòng thương lượng.

---

## 7. Câu hỏi cần business chốt

| # | Câu hỏi |
|---|---------|
| 1 | Brief gắn **1-1 với job** hay **tái dùng** cho nhiều job/creator? |
| 2 | Thù lao Phase 2: **giá cố định per-job**, hay theo lượt xem (CPV…), hay cả hai? |
| 3 | Có cho phép **thương lượng** không, hay chỉ accept/reject? Nếu có: giới hạn mấy vòng? |
| 4 | **Deadline** mặc định cho (a) phản hồi lời mời, (b) ký hợp đồng? Hết hạn auto hay admin xác nhận? |
| 5 | Creator chưa có tài khoản: chấp nhận **email magic-link + đăng ký lazy**, hay bắt buộc có tài khoản trước khi mời? |
| 6 | Khi creator từ chối/hết hạn: có tự **mời người kế tiếp** trong shortlist (waterfall) hay mời tay? |
| 7 | Tham gia chính thức kích hoạt **lúc accept** hay **sau khi ký xong**? *(đề xuất: sau khi ký)* |
| 8 | Quyền sử dụng nội dung / exclusivity / lịch thanh toán — **bắt buộc mọi hợp đồng** hay tùy job? |
| 9 | Dịch vụ ký có thêm được **loại hợp đồng + template per-job** không, đội nào làm, timeline? |
| 10 | Phase 2 cần **Creator Portal** ngay, hay chấp nhận email-first (portal phase sau)? |

---

# Phase 3 — Automation (ghi nhận, sẽ đi sâu sau)

> Hai điểm định hướng đã ghi nhận:

1. **Brand portal** — bắt đầu cần để ADV xem report (hướng: **clone từ techcombank dashboard**, vốn đã có sẵn màn report/dashboard).
2. **Auto report** — gửi **link + email** cho ADV cùng xem (báo cáo định kỳ tự động).

> Phase 3 (Payment tracking · Brand dashboard live · Auto-report) phụ thuộc dữ liệu Phase 2 sinh ra (booking/content/thanh toán) — sẽ phân tích chi tiết sau khi Phase 2 chốt.

---

*Phân tích Phase 2 — verify hệ thống hiện có + thiết kế luồng. Chờ review + trả lời câu hỏi business.*
