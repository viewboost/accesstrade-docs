# Ảnh hưởng của việc tắt AT-Core và crawler profile Facebook

## Tóm tắt

Việc tắt AT-Core và crawler profile Facebook **không ảnh hưởng tới đếm view bài đăng, đối soát và
tính tiền thưởng**. Creator vẫn liên kết tài khoản, đăng bài và nhận thưởng bình thường.

Ảnh hưởng nằm ở **số liệu hồ sơ creator** và các tính năng dựa trên số liệu đó.

Ở **Techcombank**, hồ sơ creator liên kết mới sẽ không có số liệu kênh trên cả ba nền tảng Facebook,
TikTok và YouTube. **Toàn bộ hồ sơ mới chuyển sang duyệt tay.**

Ở **Ambassador**, hồ sơ mất số liệu trên cả bốn nền tảng, nhưng **luồng duyệt không bị ảnh hưởng** vì
luồng này vốn đã do vận hành làm tay.

---

## 1. Bối cảnh và yêu cầu

AT yêu cầu tắt hai thành phần:

- **AT-Core** — dịch vụ làm giàu hồ sơ creator (profile enrichment): lấy về số người theo dõi, lượt xem,
  số video, nhân khẩu học của kênh
- **Crawler profile Facebook** — thành phần thu thập số liệu trang/kênh Facebook

Yêu cầu áp dụng cho hai hệ thống: **Techcombank** và **Ambassador**.

Trước khi thực hiện, DISO đã rà soát trực tiếp trên mã nguồn của cả hai hệ thống để xác định đầy đủ phạm
vi ảnh hưởng. Tài liệu này là kết quả rà soát.

### Một điểm cần nắm trước khi đọc phần ảnh hưởng

**Hai hệ thống có kiến trúc làm giàu hồ sơ khác nhau**, nên cùng một thao tác tắt sẽ cho kết quả khác
nhau. Vì vậy phần ảnh hưởng được tách riêng cho từng hệ thống.

| | Techcombank | Ambassador |
|---|---|---|
| Nguồn làm giàu hồ sơ | **Hai nguồn độc lập.** Một nguồn phục vụ lúc creator liên kết tài khoản (YouTube, TikTok, Facebook). AT-Core là nguồn thứ hai, phục vụ công cụ quản trị và tính năng gợi ý creator. | **Một nguồn duy nhất** là AT-Core, phục vụ cả bốn nền tảng: TikTok, YouTube, Facebook, Instagram. |
| Duyệt hồ sơ tự động | Đang bật, dựa trên ngưỡng số liệu của từng đối tác | Không sử dụng — mọi hồ sơ đều do vận hành duyệt tay |
| Gợi ý creator cho chiến dịch | Có *(chưa triển khai thực cho đối tác)* | Không có tính năng này |

---

## 2. Các ảnh hưởng

### 2.1 Những phần BỊ ảnh hưởng — Techcombank

Dịch vụ lấy số liệu hồ sơ của Techcombank phục vụ chung cho **Facebook, TikTok và YouTube**. Sau khi
tắt, hồ sơ creator liên kết mới **không có số liệu kênh trên cả ba nền tảng**.

Creator vẫn liên kết tài khoản bình thường — chỉ phần số liệu kênh là trống.

| Hạng mục | Ảnh hưởng |
|---|---|
| **Số liệu hồ sơ hiển thị** | Hồ sơ mới của **Facebook, TikTok và YouTube** đều hiển thị giá trị 0 cho tới khi được nhập tay |
| **Duyệt hồ sơ tự động** | Hồ sơ mới của cả ba nền tảng không có số liệu để đối chiếu với ngưỡng duyệt → dừng ở trạng thái **Chờ duyệt**. **Toàn bộ hồ sơ mới chuyển sang duyệt tay.** |
| **Gợi ý creator cho chiến dịch** | Ngừng hoạt động *(chưa triển khai thực cho đối tác nên không ảnh hưởng vận hành hiện tại)* |
| **Đồng bộ nhãn hồ sơ** | Ngừng hoạt động |
| **Công cụ làm giàu hồ sơ hàng loạt trong admin** | Ngừng hoạt động |

#### Không phải đối tác nào cũng bị ảnh hưởng

Điều kiện duyệt tự động được cấu hình riêng cho từng đối tác:

- **Đối tác có đặt ngưỡng số liệu** — hồ sơ mới dồn hết vào Chờ duyệt
- **Đối tác không đặt ngưỡng** — **không thay đổi**, hồ sơ mới vẫn được duyệt tự động như trước, vì
  việc duyệt của nhóm này vốn không đối chiếu số liệu

### 2.2 Những phần BỊ ảnh hưởng — Ambassador

| Hạng mục | Ảnh hưởng |
|---|---|
| **Số liệu hồ sơ hiển thị** | Mất số liệu của **cả bốn nền tảng** — TikTok, YouTube, Facebook, Instagram |
| **Nhân khẩu học của kênh** | Không có dữ liệu mới |

**Luồng duyệt hồ sơ không bị ảnh hưởng.** Ambassador không sử dụng duyệt tự động — mọi hồ sơ đều do vận
hành duyệt tay và không phụ thuộc vào số liệu. Vì vậy vận hành **không phát sinh thêm việc duyệt** so với
hiện tại; chỉ là màn hình hồ sơ sẽ hiển thị số liệu trống.

Ambassador cũng không có tính năng gợi ý creator cho chiến dịch nên không mất gì ở phần này.

### 2.3 Những phần KHÔNG bị ảnh hưởng — cả hai hệ thống

| Nghiệp vụ | Ghi chú |
|---|---|
| **Đếm view của bài đăng** | Dùng hệ thống thu thập nội dung riêng, độc lập hoàn toàn với AT-Core và crawler profile |
| **Đối soát và tính tiền thưởng** | Không có thành phần nào trong luồng này phụ thuộc AT-Core hay crawler profile |
| **Creator liên kết tài khoản** | Vẫn liên kết được bình thường, không bị chặn |
| **Đăng bài và duyệt bài** | Không ảnh hưởng |
| **Chiến dịch đang chạy** | Không ảnh hưởng |

Nói cách khác: **dòng tiền và dòng nội dung không bị đụng tới.** Ảnh hưởng chỉ nằm ở lớp thông tin hồ sơ
creator.

### 2.4 Hai rủi ro theo thời điểm — áp dụng cho cả hai hệ thống

**Rủi ro 1 — Hồ sơ liên kết trong thời gian tắt sẽ không tự có số liệu khi bật lại.**

Việc làm giàu hồ sơ chỉ chạy tại thời điểm creator liên kết tài khoản lần đầu. Các hồ sơ liên kết trong
khoảng thời gian tắt sẽ **không được làm giàu tự động** khi hệ thống bật lại — nhóm này vĩnh viễn không có
số liệu nếu không có bước bổ sung dữ liệu chủ động.

⇒ Cần chốt kế hoạch bổ sung dữ liệu (backfill) **trước khi tắt**, không phải sau.

**Rủi ro 2 — Yêu cầu đang xử lý dở tại thời điểm cắt.**

Các yêu cầu làm giàu đã gửi đi trước thời điểm tắt có thể trả kết quả về sau đó. Cần thống nhất cách xử
lý: nhận nốt kết quả của các yêu cầu này, hay bỏ qua toàn bộ.

---

## 3. Next action

| # | Việc cần làm | Mục đích | Thời điểm |
|---|---|---|---|
| 1 | **Thống nhất quy trình vận hành duyệt tay** cho hồ sơ mới ở Techcombank (cả ba nền tảng) | Hồ sơ mới không bị treo ở Chờ duyệt vô thời hạn | Trước khi tắt |
| 2 | **Rà cấu hình điều kiện duyệt tự động của từng đối tác Techcombank** | Biết trước đối tác nào bị dồn hồ sơ vào Chờ duyệt, để ước lượng khối lượng duyệt tay | Trước khi tắt |
| 3 | **Thống kê số hồ sơ đang chờ làm giàu** tại thời điểm dự kiến cắt | Xác định tập hồ sơ cần bổ sung dữ liệu về sau (Rủi ro 1) | Trước khi tắt |
| 4 | **Chốt cách xử lý các yêu cầu đang chạy dở** tại thời điểm cắt | Rủi ro 2 | Trước khi tắt |
| 5 | **Xác nhận thời điểm tắt và thời gian dự kiến duy trì trạng thái tắt** | Ước lượng khối lượng hồ sơ cần bổ sung dữ liệu và khối lượng việc tay của vận hành | Trước khi tắt |
| 6 | **DISO bổ sung chốt chặn ở Ambassador** để đảm bảo tắt triệt để, không còn kết nối phát sinh ngoài ý muốn | Việc tắt sạch và có thể kiểm chứng | Song song hoặc ngay sau khi tắt |
| 7 | **Lập kế hoạch bổ sung dữ liệu khi bật lại** | Rủi ro 1 | Chốt trước khi tắt, thực hiện khi bật lại |
