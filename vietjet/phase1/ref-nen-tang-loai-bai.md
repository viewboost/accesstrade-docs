# Tham chiếu · Nền tảng, loại bài và hashtag chương trình

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

Tài liệu mô tả **hành vi có sẵn** của hệ thống, không phải chức năng mới. [CN-01](./prd-cn01-diem-co-dinh-moi-bai.md) dựa vào đây để đặt mức điểm theo nguồn.

## REF.1 Nền tảng và loại bài hệ thống nhận

| Nền tảng | Loại bài (nguồn) | Ghi chú |
|---|---|---|
| TikTok | Video | |
| YouTube | Video thường | |
| YouTube | Shorts (video ngắn) | Nguồn riêng, đặt mức điểm riêng |
| Facebook | Video | Tự chuyển sang Reels nếu link khớp mẫu Reels (REF-BR03) |
| Facebook | Reels | Nguồn riêng |
| Facebook | Bài post (ảnh, chữ) | Nguồn riêng |
| Instagram | Bài ảnh và Reels | **Gộp chung một nguồn**, chỉ đặt được một mức điểm cho cả hai |
| Threads | Bài viết | |
| Shopee | Video | |

## REF.2 Đặt điểm bài post và video theo thể lệ

Thể lệ có hai mức: **bài post** và **video TikTok/Reels**. Hệ thống đặt điểm theo nguồn, không có ô "post" hay "video", nên nhập mức của loại nào vào đúng nguồn thuộc loại đó. Cả hai loại dùng **một** nhiệm vụ Cố định mỗi bài được duyệt. Hai nhiệm vụ cùng áp một nguồn sẽ cộng điểm hai lần cho một bài.

| Loại theo thể lệ | Nguồn | Mức nhập | Ví dụ (bảng 25/50) |
|---|---|---|---|
| Bài post | Facebook Post | Mức post | 25 |
| Video TikTok / Reels | TikTok, Facebook Reels | Mức video | 50 |
| Video Facebook thường | Facebook | Mức video | 50 |
| Bài ảnh và Reels Instagram | Instagram | Một mức duy nhất, chọn mức post hoặc video | |
| Nền tảng khác (YouTube, YouTube Shorts, Threads, Shopee) | Từng nguồn | Chỉ nhập khi BTC chấp thuận nền tảng đó; để trống thì không được thưởng | |

Các bước: Admin › Sự kiện › tab Nhiệm vụ › Tạo nhiệm vụ Cố định mỗi bài được duyệt › chọn nguồn ở ô "Áp dụng cho các source" › nhập mức từng nguồn. Sự kiện cần nhận **cả Facebook và Facebook Reels** (REF-BR04).

## REF.3 Cách hệ thống nhận biết loại bài

| Mã | Quy tắc |
|---|---|
| **REF-BR01** | Người tham gia chọn **nguồn** của bài khi gửi, trong danh sách nguồn mà sự kiện nhận, rồi dán link. Hệ thống không đoán loại bài từ nội dung |
| **REF-BR02** | Hệ thống kiểm link khớp với nguồn đã chọn. Mỗi nguồn có mẫu link riêng; link không khớp thì bị từ chối |
| **REF-BR03** | Facebook: người tham gia chọn nguồn Facebook mà link cũng khớp mẫu Reels thì bài được lưu là **Facebook Reels** và tính điểm theo nguồn Reels. Đây là chỗ duy nhất hệ thống tự đổi nguồn |
| **REF-BR04** | Sự kiện nhận Facebook mà không nhận Facebook Reels thì link rơi vào trường hợp REF-BR03 bị từ chối với thông báo "Chương trình chỉ chấp nhận bài đăng …". Sự kiện Vietjet cần nhận cả hai nguồn |
| **REF-BR05** | YouTube: chọn nguồn YouTube mà link là Shorts thì bị từ chối, phải gửi bằng nguồn YouTube Shorts. Hệ thống hỏi YouTube để biết link có phải Shorts; hỏi không được thì báo thử lại, không coi là video thường |
| **REF-BR06** | Facebook Post: không tự chuyển, chỉ kiểm link đúng mẫu bài post (bài đăng, ảnh, permalink, chia sẻ) |
| **REF-BR07** | Instagram: một nguồn nhận cả link bài ảnh và link Reels, không phân biệt hai loại |
| **REF-BR08** | Nguồn mà sự kiện không nhận thì người tham gia không chọn được |

## REF.4 Hashtag chương trình

| Mã | Quy tắc |
|---|---|
| **REF-BR09** | Hashtag chương trình do BTC điền ở ô **Hashtag** trong cấu hình sự kiện |
| **REF-BR10** | Khi gửi bài, hệ thống kiểm bài có đủ các hashtag đó. Thiếu thì từ chối và nêu hashtag còn thiếu: "Nội dung không có chứa đầy đủ hashtag của chương trình: …" |
| **REF-BR11** | Kiểm không phân biệt chữ hoa, chữ thường |

## REF.5 Kịch bản kiểm thử

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| REF-TC01 | Mỗi nguồn một mức | Nhiệm vụ cố định: TikTok 50, Facebook Reels 50, Facebook Post 25. Duyệt một bài mỗi nguồn | 50, 50, 25 | REF.2 |
| REF-TC02 | Facebook tự chuyển Reels | Sự kiện nhận Facebook và Facebook Reels. Chọn nguồn Facebook, dán link `facebook.com/watch/?v=…` | Bài lưu ở nguồn Facebook Reels, thưởng theo mức Reels | BR03 |
| REF-TC03 | Sự kiện không nhận Reels | Sự kiện nhận Facebook, không nhận Facebook Reels. Làm như TC02 | Bị từ chối "Chương trình chỉ chấp nhận bài đăng …" | BR04 |
| REF-TC04 | YouTube Shorts | Chọn nguồn YouTube, dán link Shorts | Bị từ chối, yêu cầu gửi bằng nguồn YouTube Shorts | BR05 |
| REF-TC05 | Instagram gộp | Gửi một bài ảnh và một Reels Instagram, duyệt cả hai | Cả hai cùng một mức điểm | BR07 |
| REF-TC06 | Link không khớp nguồn | Chọn nguồn TikTok, dán link YouTube | Bị từ chối, không tạo bài | BR02 |
| REF-TC07 | Nguồn sự kiện không nhận | Sự kiện chỉ nhận TikTok và Facebook Post | Không chọn được nguồn khác | BR08 |
| REF-TC08 | Nguồn chưa có mức | Nhận Instagram, nhiệm vụ không nhập mức Instagram. Duyệt một bài Instagram | Bài được duyệt, không có khoản thưởng | REF.2 |
| REF-TC09 | Thiếu hashtag chương trình | Sự kiện điền #Vietjet và #ChienBinhVietjetHybrid. Gửi bài chỉ có #Vietjet | Bị từ chối, thông báo nêu thiếu #ChienBinhVietjetHybrid | BR10 |
| REF-TC10 | Hashtag khác hoa thường | Gửi bài có #CHIENBINHVIETJETHYBRID và #vietjet | Được chấp nhận | BR11 |
