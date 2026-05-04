# Liên kết Tài khoản Scalef — Overview

> **Ngày:** 2026-05-04
> **Trạng thái:** Đang thiết kế
> **PRD chi tiết:** [../scalef-integration/prd-scalef-integration-v1-2026-04-12.md](../scalef-integration/prd-scalef-integration-v1-2026-04-12.md)
> **Demo live:** https://demo-ambassador.accesstrade.click/lien-ket-scalef
> **Mockup source:** [`demo-gen-green`](../../../demo-gen-green/) → trang `/lien-ket-scalef`
> **Đối tượng:** Product, Operations, Stakeholders (non-tech)

---

## Đây là gì?

**Liên kết tài khoản Scalef** là bước đầu tiên (và bắt buộc) để creator Gen-Green có thể tham gia chương trình affiliate.

Hiểu đơn giản: Creator dùng **1 tài khoản** để làm cả 2 việc — sáng tạo nội dung trên Gen-Green **và** kiếm hoa hồng affiliate trên Scalef. Không phải nhớ 2 mật khẩu, không phải làm thuế 2 nơi.

---

## Tại sao cần?

Gen-Green và Scalef là 2 nền tảng riêng (cùng do AccessTrade vận hành):

- **Gen-Green** (~150K creators) — đăng video, kiếm tiền theo lượt xem
- **Scalef** (~1K publishers) — chia sẻ link, kiếm hoa hồng theo đơn hàng

Tích hợp = creator Gen-Green có **thêm nguồn thu nhập thứ 2** mà không cần rời nền tảng. Đồng thời giải bài toán **thuế TNCN**: AccessTrade chi trả cho cả 2 bên, hệ thống cần biết "đây là cùng 1 người" để tính thuế đúng.

**Mục tiêu:** 1.000 creator generate doanh thu affiliate, 50 tỷ/năm.

---

## Nguyên tắc cốt lõi

| Nguyên tắc | Ý nghĩa |
|------------|---------|
| **1 đối 1** | 1 creator Gen-Green ↔ 1 publisher Scalef. Không liên kết chéo. |
| **CCCD là khóa identity** | CCCD trùng = "cùng 1 người". CCCD khác → từ chối liên kết (không phải nhầm hay bug). |
| **Không bên nào "đúng" hơn** | Khi SĐT/Email lệch, **user chọn** giữ thông tin bên nào. Không tự động override. |
| **Bên nào trống thì lấy bên có** | Nếu 1 bên thiếu thông tin, auto-fill từ bên có data, không bắt user chọn. |
| **OTP khi đổi data** | Chọn data từ bên kia → phải xác thực OTP trước khi update sang bên mình. |
| **Update 2 chiều** | Sau khi user chọn, hệ thống sync data sang cả 2 bên. |
| **Data nhạy cảm không qua browser** | CCCD, SĐT, Email truyền backend-to-backend. Trình duyệt chỉ thấy mã ngẫu nhiên. |

---

## Creator trải qua những bước nào?

**Xem demo live:** https://demo-ambassador.accesstrade.click/lien-ket-scalef — có **2 kịch bản** để stakeholder click trực tiếp (chuyển kịch bản ở Hub page).

### Kịch bản A — Không xung đột (3 bước, ~30 giây)

Khi thông tin 2 bên khớp hoàn toàn (CCCD, SĐT, Email):

```
1. Đăng nhập Scalef    →    2. Đồng ý chia sẻ    →    3. Hoàn tất
```

Skip luôn bước "xác nhận" và "bổ sung" → liên kết thành công ngay.

### Kịch bản B — Có xung đột (5 bước, ~2 phút)

Khi SĐT hoặc Email 2 bên khác nhau:

```
1. Đăng nhập Scalef    →    2. Đồng ý chia sẻ    →    3. Xác nhận so khớp
                                                            ↓
                              5. Hoàn tất    ←    4. Bổ sung (chọn + OTP)
```

**Chi tiết từng bước:**

1. **Đăng nhập Scalef** — Creator bấm nút trên Gen-Green → redirect sang Scalef → đăng nhập (nếu chưa có thì đăng ký bên Scalef trước).

2. **Đồng ý chia sẻ thông tin** — Hiển thị rõ: Họ tên, CCCD, SĐT, Email sẽ được share giữa 2 bên. Bấm Đồng ý / Từ chối.

3. **Xác nhận so khớp** — Bảng so sánh từng trường giữa Gen-Green và Scalef:
   - Trùng → badge xanh "Khớp"
   - Khác → badge vàng "Lệch"
   - 1 bên trống → badge xám "Bổ sung"
   - CCCD masked (chỉ hiện 4 số cuối)

4. **Bổ sung (chỉ hiện khi có lệch)** — Mỗi trường lệch hiển thị 2 thẻ chọn (Gen-Green vs Scalef value). Nếu user chọn data từ Scalef → cần update Gen-Green → **OTP gửi về SĐT/Email mới** để xác thực.

5. **Hoàn tất** — Hiển thị profile hợp nhất + danh sách chiến dịch affiliate sẵn sàng tham gia.

---

## Khi nào liên kết bị từ chối?

Tất cả case từ chối hiển thị **cùng 1 màn hình** kèm nút "Gửi yêu cầu hỗ trợ" (auto-tạo ticket, hẹn 3 ngày phản hồi):

| Tình huống | Lý do |
|------------|-------|
| Creator Gen-Green đã liên kết publisher Scalef khác | "Tài khoản Gen-Green đã liên kết Scalef khác" |
| Publisher Scalef đã liên kết creator Gen-Green khác | "Tài khoản Scalef này đã liên kết Gen-Green khác" |
| **CCCD 2 bên khác nhau** | "Thông tin CCCD không khớp" — không phải cùng 1 người |
| SĐT/Email mới (sau khi user chọn) đã thuộc user khác | "SĐT/Email này đã được dùng" |

Creator không cần điền form — ticket tự gửi kèm Gen-Green User ID + Scalef User ID + lý do.

---

## Điểm chạm trên Gen-Green

Creator thấy nút "Liên kết Scalef" ở các vị trí (đều dẫn về cùng 1 flow):

| Vị trí | Loại |
|--------|------|
| Trang đăng nhập / đăng ký Gen-Green | Nút SSO ("Đăng nhập bằng Scalef") |
| Settings → Tài khoản liên kết | Trạng thái + nút "Liên kết" |
| Tab Affiliate trong dashboard | Banner giới thiệu |
| Chi tiết Event có affiliate | Banner "Liên kết để tham gia" |
| Bấm "Tham gia chiến dịch" khi chưa link | Popup chặn |
| Bấm "Tạo link affiliate" khi chưa link | Popup chặn |

Sau khi liên kết: hiển thị "Đã liên kết — username Scalef" + ngày liên kết. **Không có nút gỡ** (chỉ admin gỡ được, để bảo vệ data history).

---

## Edge cases đã tính tới

| Tình huống | Cách xử lý |
|------------|------------|
| User refresh browser giữa flow | Pending state TTL 15 phút — quay lại trong 15' resume từ bước dở. Hết 15' bắt đầu lại. |
| Scalef API timeout | Báo "Thử lại sau" + auto-retry 3 lần. Không kẹt user ở trạng thái trung gian. |
| User đổi format CCCD/SĐT (khoảng trắng, dấu, +84 vs 0xxx) | Hệ thống chuẩn hóa trước khi compare |
| 2 user cùng dùng SĐT đăng ký 1 lúc | Lock unique → user thứ 2 bị reject |
| Tên 2 bên Unicode vs ASCII (Hùng vs Hung) | Tên không dùng để matching — chỉ CCCD/SĐT/Email |

---

## Migration cho 1.000 publisher Scalef cũ

Scalef sắp **chặn đăng ký mới** → 1.000 publisher hiện có cần đường vào Gen-Green:

| Tình huống publisher | Hướng xử lý |
|----------------------|-------------|
| Đã có tài khoản Gen-Green (cùng CCCD/SĐT) | Tự link qua flow chuẩn |
| Chưa có Gen-Green | Đăng ký Gen-Green trước, hoặc admin batch tạo account + gửi email set password |
| Thông tin mâu thuẫn | Admin review thủ công |

---

## Vai trò trong hệ thống tổng

Liên kết tài khoản là **Phase 1** của lộ trình tích hợp 3 phase:

| Phase | Nội dung | Trạng thái |
|-------|----------|-----------|
| **1. Liên kết tài khoản** (track này) | OAuth, matching, conflict resolution, OTP | Đang thiết kế |
| 2. Affiliate trong Gen-Green | Browse chiến dịch, tạo link, dashboard hoa hồng | Chờ Phase 1 |
| 3. Hợp nhất tài khoản | 1 cửa đăng nhập, thanh toán hợp nhất | Chờ Phase 2 |

Mỗi phase go-live riêng được, dừng được bất kỳ lúc nào.

---

## Thời gian & nguồn lực

- **Effort:** ~2.5 tuần cho 1 BE + 1 FE
- **Output chính:**
  - OAuth flow Gen-Green ↔ Scalef
  - 5 màn UI (login, consent, confirm, resolve, done)
  - Logic matching CCCD/SĐT/Email + check 1-1
  - OTP service cho update SĐT/Email
  - Bảng `pending_link` (resumable) + `link_history` (audit)
  - Auto-tạo ticket khi reject

Chi tiết kỹ thuật: xem [PRD](../scalef-integration/prd-scalef-integration-v1-2026-04-12.md).

---

## Phụ thuộc bên Scalef

Cần Scalef cung cấp (đã có spec ở [`scalef-api.md`](scalef-api.md) — đang verify thêm chi tiết):

- SSO OAuth2 endpoint (đăng nhập + redirect)
- API trả thông tin user (CCCD, SĐT, Email, tên)
- API update profile (cho luồng 2 chiều)
- Sandbox/staging environment để test

---

## Liên quan

- [PRD Phase 1 chi tiết](../scalef-integration/prd-scalef-integration-v1-2026-04-12.md) — cho dev
- **Demo live:** https://demo-ambassador.accesstrade.click/lien-ket-scalef — cho stakeholder click trực tiếp 2 kịch bản
- [Mockup source code](../../../demo-gen-green/) — cho dev tham khảo cách triển khai UI
- [Scalef API Reference](scalef-api.md) — đã có spec SSO OAuth + integration APIs
- [Phía Gen-Green: account-linking detail](../scalef-integration/gengreen-scalef-account-linking.md) — bản đặc tả phía Gen-Green
- [Roadmap hợp nhất tài khoản](../scalef-integration/unified-account-roadmap.md) — Phase 3
- **Trong cùng folder `affiliate/`:**
  - [Admin Setup Overview](admin-setup-overview.md) — back-office tạo affiliate campaign (track độc lập, chạy song song)
  - [Scalef API Reference](scalef-api.md) — technical spec (SSO + integration APIs)
  - [FE Display + Generate Link + Report Overview](fe-display-generate-link-report-overview.md) — creator UX (Phase 2)
