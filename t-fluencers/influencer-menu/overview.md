# Menu Influencer — Danh sách & Chi tiết người tham gia

**Thời gian:** 24/05/2026
**Trạng thái:** Đã triển khai
**Đối tượng:** Account Manager, Marketing, Ops — người dùng dashboard cần tra cứu người tham gia thử thách T-Fluencers.

---

## Tại sao cần menu này?

Dashboard T-Fluencers trước đây có trang **Hồ sơ** (Profiles) — mỗi dòng là **một kênh mạng xã hội** (Facebook, TikTok, YouTube...). Nhưng một người thường có nhiều kênh. Khi sếp hỏi *"Anh A đóng góp gì cho chương trình?"*, ta phải tự gom 3-4 dòng kênh của anh A lại để cộng số — mất công và dễ sai.

Thiếu một chỗ nhìn **theo con người**: mỗi người là một dòng, gộp sẵn toàn bộ kênh và đóng góp của họ.

→ Menu **Influencer** giải quyết đúng việc đó.

---

## Có gì?

### 1. Trang Danh sách Influencer

Mỗi dòng = **một người tham gia** chương trình (không phải một kênh). Bảng hiển thị:

- **Tên** + email / hashtag.
- **Bài đăng** — số bài đã duyệt.
- **Lượt xem** — tổng lượt xem nội dung.
- **Cash** — tiền nội dung đã ghi nhận (không tính bài bị từ chối).
- **Techcomer** — badge xanh nếu là CBNV Techcombank (kèm mã nhân viên), gạch "—" nếu không.
- **Tham gia** — ngày bắt đầu tham gia.

**Tìm kiếm:** gõ vào ô tìm là ra theo tên, email, **mã nhân viên Techcomer**, **hashtag**, số điện thoại, hoặc tên/username TikTok.

**Lọc nhanh:** lọc theo nhóm Techcomer (Là Techcomer / Không phải / Chưa xác minh) và theo **tỉnh/thành** (chọn từ danh sách 63 tỉnh, có ô tìm nhanh).

**Sắp xếp:** bấm vào tiêu đề cột (Bài đăng, Lượt xem, Cash, Techcomer, Tham gia) để sắp xếp tăng/giảm. Sắp xếp áp dụng trên **toàn bộ** danh sách, không chỉ trang đang xem.

### 2. Trang Chi tiết Influencer

Bấm vào một người → mở trang chi tiết, gồm phần đầu (tên, badge Techcomer, ngày tham gia, các con số tổng) và **3 tab**:

- **Tổng quan** — thông tin cá nhân đầy đủ (tên, email, SĐT, hashtag, giới tính, ngày sinh, tỉnh/thành, nghề nghiệp, Techcomer) + 4 con số tổng hợp (người theo dõi, bài đăng, lượt xem, cash) + danh sách nền tảng họ có.
- **Hồ sơ** — bảng tất cả kênh mạng xã hội của người này (nền tảng, tài khoản, người theo dõi, tỷ lệ tương tác, video, trạng thái duyệt, link xem kênh). Có phân trang.
- **Thử thách** — bảng các thử thách (campaign) người này đã tham gia, kèm số video / lượt xem / phí mỗi thử thách. Có phân trang.

---

## Lợi ích kỳ vọng

**Cho người dùng (Ops / AM / Marketing):**
- Nhìn theo con người, không phải gom thủ công từng kênh.
- Tra một người ra ngay mọi kênh + mọi thử thách họ tham gia.
- Tìm CBNV Techcombank theo mã nhân viên dễ dàng.

**Cho hệ thống:**
- Dữ liệu tổng hợp lấy thẳng từ tầng dữ liệu có sẵn — không tính lại, không lệch số.
- Sắp xếp & lọc chạy ở phía máy chủ → đúng trên toàn bộ dữ liệu, nhanh với danh sách lớn.

---

## Chi phí và rủi ro

| Vấn đề | Cách xử lý |
|---|---|
| Một người có thể có nhiều bản ghi (do dữ liệu seed/test) → hiển thị trùng tên | Là hiện tượng ở dữ liệu test; cần theo dõi trên production. Đã ghi nhận. |
| Thử thách đã bị xóa khỏi hệ thống nhưng người vẫn từng tham gia | Hiển thị nhãn **"[Thử thách đã xóa]"** thay vì để trống/lỗi. |
| Tìm mã nhân viên cần dữ liệu cũ được cập nhật | Ô tìm kiếm khớp trực tiếp mã ở tầng dữ liệu hiện tại — không cần migration. |

---

## Phạm vi không ảnh hưởng

- **Trang Hồ sơ (Profiles) cũ** giữ nguyên — vẫn làm việc ở mức từng kênh. Menu Influencer là tầng cao hơn (theo con người), không thay thế.
- Các trang Analytics, Thử thách, Nội dung không đổi.

---

## Tài liệu liên quan

- [prd.md](prd.md) — chi tiết kỹ thuật, API, yêu cầu cho dev/PM.
- [Phân loại Techcomer vs Mass](../dashboard-wiki-and-techcomer/overview.md) — khái niệm Techcomer dùng chung.
