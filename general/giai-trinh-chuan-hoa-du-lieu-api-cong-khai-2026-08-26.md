# [NỘI BỘ] Xử lý phản ánh bảo mật API công khai — Green Creator (vcreator)

> ⚠️ **TÀI LIỆU NỘI BỘ DISO — KHÔNG gửi nguyên bản cho khách hàng (ACCESSTRADE).**
> Chỉ **Mục 5** được phép dùng làm nội dung trả lời khách. Mục 2 (khách chưa phát hiện) tuyệt đối không tiết lộ ra ngoài — dùng để đội tự vá trước.

- **Ngày:** 26/08/2026
- **Bối cảnh:** ACCESSTRADE (khách hàng) gửi phản ánh mức Critical, yêu cầu giải trình trong 4h làm việc, khắc phục trong 24h kể từ khi chốt phương án.
- **Hệ thống:** API `vcreator-api.koc.com.vn` phục vụ `creator.gen-green.global`.

---

## 0. Tóm tắt nội bộ (đọc trước khi trả lời khách)

- Phản ánh của khách **có cơ sở** ở 4 endpoint họ nêu — cần thừa nhận đúng mực, không chối.
- **Lá bài giảm nhẹ mạnh nhất, và là sự thật:** các dữ liệu định danh nhạy cảm nhất — **số điện thoại, CCCD, hợp đồng, tài khoản ngân hàng, email — KHÔNG bị lộ** (đều nằm sau đăng nhập). Đây là điểm cần nêu rõ đầu tiên.
- **Không được nói với khách những câu có thể bị demo ngược:** cụ thể là câu "không lấy được hết dữ liệu". Nội bộ đã xác nhận id có thể liệt kê qua phân trang → xem Mục 2. Trả lời khách theo hướng "đang siết", không theo hướng "không khai thác được".
- Còn một nhóm vấn đề **khách chưa nêu** (Mục 2). Ưu tiên vá nhóm này **trước hoặc song song** để nếu khách có dò tiếp thì đã kín.

---

## 1. Phần khách hàng ĐÃ phát hiện

**Endpoint khách nêu** (đều không yêu cầu đăng nhập):
- `/events/{id}/leaderboards`
- `/events/{id}/content`
- `/events/user-newest`
- `/events/statistic`

**Dữ liệu khách dẫn ra:** thu nhập của từng creator, thu nhập từng bài kèm link video gốc, ảnh profile Google/TikTok, và số liệu tổng nền tảng (~30,36 tỷ hoa hồng, ~280.644 nội dung, ~16,5 tỷ lượt xem).

**Đánh giá nội bộ — đúng tới đâu:**
- Số liệu tổng và bảng xếp hạng: **đúng là đang public** — nhưng phần lớn là **có chủ đích** (xem Mục 3).
- Con số tiền của từng creator / từng bài: **đúng là đang đi kèm trong gói tin** — đây là phần **phải tách**, và giao diện thực tế **đã ẩn** phần này từ trước (thiện chí, xem Mục 3).
- Ảnh đại diện: đúng là đang trỏ URL Google/TikTok, nhưng đây là ảnh **công khai** creator dùng trên MXH (không phải ảnh riêng tư do hệ thống lưu) → mức nhẹ; vẫn nên đưa qua ảnh hệ thống để không phát tán URL tài khoản gốc.

**Điểm giảm nhẹ đúng cho nhóm này:** các endpoint khách phát hiện là **endpoint danh sách theo sự kiện (event)**, **không nhận user_id tùy ý** — tức **không cho phép "tra cứu đích danh thông tin của một cá nhân cụ thể" qua các endpoint này**. Chúng trả về danh sách theo bảng xếp hạng/nội dung của sự kiện.

---

## 2. Phần khách hàng CHƯA phát hiện — 🔒 NỘI BỘ, VÁ TRƯỚC

Đây là các điểm **cần tự khắc phục trước**, **không đưa vào văn bản gửi khách**:

1. **Nhóm `/user-statistic` nhận `user_id`** (`/user-statistic`, `/contents`, `/invitees`): truyền một user_id vào là trả thu nhập, nội dung (kèm lý do kiểm duyệt), mạng lưới giới thiệu của người đó. **Đây mới là endpoint "tra theo user_id"** — và khách chưa nêu.
2. **user_id có thể liệt kê được** qua phân trang chính endpoint khách đã có (`/events/{id}/content`) → ghép với (1) sẽ thành truy xuất diện rộng. **Vì vậy tuyệt đối không khẳng định với khách rằng "không lấy được hết".**
3. **Số liệu hoa hồng theo từng nhãn hàng** (thêm tham số nhãn vào `/events/statistic`): là số liệu hợp đồng khách hàng của khách hàng — nhạy cảm về quan hệ đối tác.
4. **CORS mở rộng + chưa giới hạn tần suất truy cập** (rate-limit): cần siết cấu hình.
5. **Danh sách chiến dịch affiliate** đang để công khai: rà lại phạm vi.

→ Nguyên tắc: **vá Mục 2 lặng lẽ, nhanh, trước khi khách dò tới.**

---

## 3. Các điểm giảm nhẹ — CÓ CĂN CỨ (dùng được với khách)

**3.1. Dữ liệu định danh nhạy cảm nhất KHÔNG bị lộ.**
Đã rà toàn bộ endpoint không đăng nhập: **số điện thoại, số CCCD, thông tin hợp đồng, tài khoản ngân hàng, email, ngày sinh, địa chỉ đều KHÔNG bị lộ** — tất cả nằm sau lớp đăng nhập bắt buộc. Phần công khai chỉ gồm: tên hiển thị, ảnh đại diện, và số liệu hoạt động/thu nhập.

**3.2. Phần lớn dữ liệu công khai là có chủ đích, phục vụ kinh doanh.**
Số liệu tổng cho landing (bằng chứng quy mô để hút creator & nhãn hàng), bảng xếp hạng (thi đua), và tiến độ ngân sách chiến dịch (động lực để creator tăng tốc trước khi hết hạn mức) — đều là tính năng được thiết kế có mục đích.

**3.3. Đội đã chủ động xử lý một phần từ trước.**
Phần hiển thị tiền của từng creator **đã được chủ động ẩn ở giao diện**; ở bản Techcombank đã tách cấu trúc trả về riêng để loại bỏ hẳn. Cho thấy hướng đi đúng — việc còn lại là áp dụng đồng bộ.

**3.4. Không nhận diện đích danh cá nhân qua endpoint khách nêu.**
Như Mục 1: các endpoint khách phát hiện không nhận user_id tùy ý.

> Lưu ý dùng từ: tránh câu "không lộ PII" (thu nhập vẫn là dữ liệu cá nhân nhạy cảm theo NĐ13/2023). Dùng câu chính xác: *"Không lộ số điện thoại, CCCD, hợp đồng, tài khoản ngân hàng; phần cần siết là tên hiển thị, ảnh và số liệu thu nhập."*

---

## 4. Phương án tách & timeline (đáp ứng yêu cầu 24h)

**Nguyên tắc:** giữ nguyên trải nghiệm công khai hợp lệ (landing, bảng xếp hạng, tiến độ ngân sách), chỉ tách các trường cá nhân về sau đăng nhập.

| Dữ liệu | Giữ public | Chuyển private (cần đăng nhập) |
|---|---|---|
| Tổng lượt xem / nội dung / người tham gia | ✅ | |
| Bảng xếp hạng: tên, ảnh, lượt xem, thứ hạng | ✅ | |
| Tiến độ ngân sách chiến dịch | ✅ (cho creator đã đăng nhập) | |
| Con số tiền của từng creator / từng bài | | ✅ tách khỏi gói tin công khai |
| Trường `totalCommission` theo nhãn | | ✅ bỏ field khỏi response công khai (GIỮ `?partner=` — partner-home dùng) |
| Nhóm `/user-statistic` | | ✅ đăng nhập + chỉ xem của chính mình |

**Timeline:**
- **0–24h:** tách trường tiền khỏi các endpoint công khai (Mục 1); siết nhóm `/user-statistic` về chính chủ (Mục 2.1); chặn tham số nhãn hàng.
- **Trong tuần:** siết CORS theo tên miền chính thức; thêm rate-limit; proxy ảnh đại diện; rà endpoint affiliate.
- **Củng cố:** thêm kiểm thử tự động (danh sách trắng endpoint công khai) để không tái diễn.

---

## 5. ✅ Nội dung được phép trả lời khách (trích từ đây)

> Phần dưới là bản gọn để đưa vào thư trả lời ACCESSTRADE. Không đính kèm Mục 2.

**Về nhóm dữ liệu công khai:** gồm số liệu tổng của nền tảng, bảng xếp hạng và tiến độ chiến dịch — được thiết kế công khai có chủ đích để phục vụ trưng bày quy mô, tạo thi đua và động lực cho creator. Nhóm này được giữ nguyên.

**Về nhóm cần tách:** một số trường số liệu thu nhập của cá nhân đang đi kèm trong gói tin công khai (dù giao diện không hiển thị). Chúng tôi sẽ tách các trường này về sau lớp đăng nhập, và đưa màn số liệu cá nhân về nguyên tắc "mỗi người chỉ xem dữ liệu của chính mình". Việc tách không ảnh hưởng tới landing và trải nghiệm hiện tại.

**Về dữ liệu định danh nhạy cảm:** đã rà soát và xác nhận **số điện thoại, CCCD, thông tin hợp đồng, tài khoản ngân hàng không bị lộ** — các dữ liệu này nằm sau lớp đăng nhập bắt buộc.

**Cam kết:** hoàn tất tách các trường trọng yếu trong vòng 24h kể từ khi chốt phương án; các hạng mục củng cố (cấu hình, giới hạn truy cập, kiểm thử tự động) hoàn tất trong tuần. Có đầu mối chịu trách nhiệm xử lý xuyên suốt.

---

## 6. Trạng thái sau release (27/08/2026)

Đã release và kiểm chứng trực tiếp trên production.

**✅ Xong phần trọng yếu (nhóm khách đã phát hiện + BOLA nội bộ):**
- BOLA `/user-statistic/*` → 404 (đã tắt).
- Leaderboard + content: đã bỏ sạch trường thu nhập cá nhân.
- Bỏ `totalEventActive`; chuỗi enumerate → BOLA đã đứt.

**🟠 Còn phải làm trước khi báo khách "hoàn tất":**
- **Ảnh đại diện (URL mạng xã hội, công khai)** — là ảnh creator dùng trên Google/TikTok, không phải ảnh riêng tư → **mức nhẹ**, nhưng **khách đã nêu đích danh** nên vẫn phải xử lý (tránh phát tán URL tài khoản gốc). Nguồn thật là **leaderboard + content** (FE render qua fallback khi avatar null); còn `/events/user-newest` đã có PR tắt (#143). Vá leaderboard/content: bỏ `socialInfo.photo` (hiện ảnh mặc định) hoặc proxy.
- Ngân sách theo nhãn vẫn lộ — vá bằng cách **bỏ field `totalCommission`** khỏi response, **KHÔNG chặn `?partner=`** (partner-home dùng param này cho view/nội dung/người tham gia). Nhóm khách chưa nêu, vá lặng.
- CORS `*` — nhóm khách chưa nêu.

→ **Chưa gửi xác nhận hoàn tất cho ACCESSTRADE** cho tới khi ít nhất phần ảnh profile được vá (vì họ mở `/events/user-newest` là thấy ngay).

---

*Bản rà soát kỹ thuật chi tiết (đầy đủ endpoint + cách khắc phục) lưu riêng cho đội kỹ thuật: `security-audit-green-creator-2026-08-26.md`.*
