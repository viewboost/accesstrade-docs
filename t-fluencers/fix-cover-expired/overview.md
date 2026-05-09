# Khắc phục lỗi mất ảnh thumbnail video TikTok ở khu vực "Nội dung nổi bật"

> Ảnh đại diện (cover) của các video nổi bật trên trang chủ partner thường xuyên bị mất, hiển thị thành ô trống/biểu tượng vỡ. Tài liệu mô tả nguyên nhân và giải pháp khắc phục.

**Ngày:** 09/05/2026
**Trạng thái:** Đề xuất
**Đối tượng đọc:** Business, Ops, PM
**Phạm vi:** Trang chủ partner T-Fluencers — khối "Nội dung nổi bật"

---

## 1. Hiện tượng người dùng đang gặp

Khi user truy cập trang chủ một partner (ví dụ Techcombank), khu vực **"Nội dung nổi bật"** hiển thị 8 video TikTok có lượt xem/lượt thích cao nhất.

**Vấn đề:** Một số video bị **mất ảnh thumbnail** — hiển thị thành ô xám trống hoặc icon ảnh vỡ. Trông không chuyên nghiệp, ảnh hưởng tới trải nghiệm và độ tin cậy của trang.

Tình trạng này xảy ra **ngẫu nhiên** — cùng một video, hôm nay xem được, mai vào đã mất ảnh.

---

## 2. Nguyên nhân

### Cơ chế hiện tại

Khi hệ thống "bắt" một video về:
1. Lấy URL ảnh thumbnail từ nền tảng gốc (TikTok, Facebook, Instagram, YouTube...)
2. Lưu URL đó vào database
3. Khi user vào trang, frontend dùng URL này để load ảnh

### Vấn đề: URL của các nền tảng đều có hạn sử dụng

URL ảnh thumbnail do các nền tảng cung cấp **không phải URL vĩnh viễn**:
- **TikTok** gắn `x-expires` — hết hạn sau ~2 ngày
- **Facebook** gắn `oe=` (expires) — hết hạn sau ~3-4 ngày
- **Instagram** tương tự Facebook (cùng hạ tầng Meta CDN)
- **YouTube** là ngoại lệ — URL ổn định theo videoId, không hết hạn → không bị lỗi này

Sau thời điểm đó: ảnh không load được, browser hiển thị ảnh vỡ.

### Vì sao hệ thống không tự refresh?

- Khi **campaign đã đóng**, hệ thống không crawl content nữa → URL cũ hết hạn nhưng không có URL mới thay thế
- **Không có job kiểm tra định kỳ** để cập nhật URL mới
- URL chết nằm trong DB mãi mãi

### Tại sao càng để lâu càng nhiều video bị lỗi?

Top 8 content nổi bật hiển thị trên trang chủ partner thường thuộc các campaign đã đóng (vì campaign đang chạy có volume thấp hơn). Theo thời gian, gần như 100% top content sẽ rơi vào trạng thái "URL hết hạn".

---

## 3. Giải pháp đề xuất

### Tóm tắt giải pháp

**Tự lưu trữ ảnh thumbnail vào hệ thống của chính chúng ta (MinIO)**, không phụ thuộc URL của TikTok.

### Cách hoạt động

1. **Khi user mở trang chủ partner** → API trả về danh sách 8 video top như cũ (không thay đổi gì với user)
2. **Phía sau (background)** → hệ thống tự động:
   - Tải ảnh thumbnail từ TikTok về
   - Upload lên MinIO (kho lưu trữ ảnh nội bộ của chúng ta)
   - Cập nhật DB: thay URL TikTok bằng URL MinIO
3. **Lần sau user mở trang** → API trả URL MinIO → ảnh không bao giờ hết hạn

### Phạm vi áp dụng

**Áp dụng cho TikTok, Facebook Reels, Instagram và các CDN có URL hết hạn**. Bất kỳ URL nào không phải của hệ thống mình thì đều tải về MinIO.

**Loại trừ YouTube** — vì URL YouTube ổn định theo videoId (không hết hạn), tải về chỉ tốn dung lượng vô ích.

**Phạm vi**: Chỉ 8 video ở khu vực "Nội dung nổi bật" của trang chủ partner.

**Không áp dụng cho:**
- Trang chi tiết partner / trang content (vì có cơ chế load ảnh khác hoặc tần suất truy cập thấp)
- Toàn bộ video trong DB (sẽ tốn storage không cần thiết)

→ Tiết kiệm chi phí lưu trữ, chỉ tập trung vào nơi user nhìn thấy nhiều nhất.

### Khi nào ảnh được "host"?

- Lần đầu một video lọt vào top 8 → ảnh được tải về MinIO (sau ~vài giây kể từ lúc API được gọi lần đầu)
- Sau khi tải xong → hệ thống tự động làm mới cache → request kế tiếp **lập tức** thấy ảnh từ kho riêng (không phải đợi)
- **Upload 1 lần, giữ vĩnh viễn** — không re-upload, không dọn dẹp

### Trường hợp video bị xóa khỏi nền tảng gốc?

- Ảnh trên MinIO **vẫn còn** — user vẫn thấy thumbnail
- Đây là tradeoff chấp nhận được: thà hiển thị ảnh "cuối cùng" còn hơn ảnh vỡ
- Video bị xóa là case hiếm, đã có flow riêng xử lý (admin có thể ẩn content)

---

## 4. Lợi ích kỳ vọng

### Cho người dùng
- ✅ Trang chủ partner luôn hiển thị đầy đủ thumbnail, không còn ô vỡ
- ✅ Trải nghiệm chuyên nghiệp, đáng tin cậy
- ✅ Ảnh load nhanh hơn (qua hạ tầng của ta, không qua CDN TikTok)

### Cho hệ thống
- ✅ Không phụ thuộc URL bên thứ 3
- ✅ Không sợ TikTok thay đổi format URL/policy bất ngờ
- ✅ Có khả năng tối ưu (resize, WebP, CDN cache) trong tương lai

### Cho vận hành
- ✅ Giảm khiếu nại "trang lỗi", "không thấy video"
- ✅ Không cần can thiệp thủ công khi gặp sự cố

---

## 5. Chi phí và rủi ro

### Chi phí

| Hạng mục | Ước tính |
|----------|----------|
| Dung lượng lưu trữ (MinIO) | Mỗi cover ~50–200KB. 4.000 video × 200KB ≈ **<1GB**, không đáng kể |
| Băng thông download từ TikTok | ~8 ảnh × 4h cache = ~50 lần/ngày/partner. Rất nhỏ |
| Effort dev | Ước tính ~2–3 ngày |

### Rủi ro & cách xử lý

| Rủi ro | Mức độ | Cách xử lý |
|--------|--------|------------|
| TikTok URL hết hạn ngay khi vừa được trả về (ảnh đầu tiên user thấy bị vỡ) | Thấp | URL từ TikTok thường còn hạn ít nhất 6–12h khi mới crawl. Lần kế tiếp đã có URL MinIO |
| Download fail (TikTok block, network error) | Trung bình | Retry 1 lần. Fail thì giữ nguyên URL TikTok cũ — không làm response API bị lỗi |
| MinIO bucket đầy | Thấp | Dung lượng ước tính rất nhỏ (<1GB cho 4K video). Cảnh báo khi dùng >80% |
| Video bị xóa khỏi TikTok nhưng ảnh vẫn hiển thị | Thấp | Chấp nhận — flow ẩn content do admin xử lý |

---

## 6. Phạm vi không ảnh hưởng

Tài liệu này **không thay đổi**:
- Logic chọn top 8 video (sort, filter, leaderboard) — giữ nguyên
- Cache Redis 4 giờ — giữ nguyên
- Giao diện frontend — không cần thay đổi gì
- Tần suất crawl video TikTok — giữ nguyên
- Trang chi tiết / trang content khác — giữ nguyên

---

## 7. Tài liệu liên quan

- **Tech Spec:** [tech-spec.md](./tech-spec.md) — chi tiết kỹ thuật cho dev
- **Test Cases:** [test-cases.csv](./test-cases.csv) — danh sách test cho QA
- **API liên quan:** `GET /partners/content-features` — API trả về top 8 content
