# Chương trình thưởng tăng trưởng Creator — vCreator Philippines

| | |
|---|---|
| **Hệ thống** | vCreator Philippines |
| **Ngày** | 2026-07-12 |
| **Trạng thái** | Draft — chờ review |
| **Tài liệu liên quan** | [solution-design.md](solution-design.md) — thiết kế kỹ thuật · [BaoGia.csv](BaoGia.csv) — báo giá |

## 0. Cách đọc báo giá

**Báo giá nhóm theo chức năng.** Mỗi chức năng là một cụm trọn gói — đã bao gồm xử lý nghiệp vụ, màn hình quản trị, màn hình creator, kiểm thử, triển khai, tài liệu và nghiệm thu. **Không tách "chuyển giao" thành cụm riêng**; phần này đã tính vào từng hạng mục.

**Tổng: 1.009 giờ · $14,717**

| Cụm | Chức năng | Giờ | Tiền | Bỏ được? |
|---|---|---|---|---|
| **A** | **Nền tảng dùng chung** | 437 | **$6,426** | **Không** |
| B | Thưởng N video đầu tiên | 67 | $961 | Có |
| C | Thưởng số video duyệt/tháng | 54 | $761 | Có |
| D | Thưởng theo lượt xem (PPV) | 66 | $949 | Có |
| E | Thưởng theo mốc hiệu suất | 54 | $761 | Có |
| F | Bảng xếp hạng tháng | 170 | $2,456 | Có |
| G | Kênh X (Twitter) + Threads | 161 | $2,403 | Có |

**Muốn giảm phạm vi thì bỏ nguyên một cụm chức năng (B–G)**, không phải đi lọc từng dòng. Cụm A là nền tảng dùng chung, mọi cơ chế thưởng đều chạy trên đó nên không bỏ được.

**Nền tảng chiếm 44% chi phí ($6,426/$14,717).** Lý do: hệ thống hiện chỉ lưu **tiền** của creator, không lưu số video đã duyệt hay tổng lượt xem; và cơ chế tính thưởng hiện tại chỉ đếm được nội dung thuộc một chiến dịch cụ thể. Phải xây bảng dữ liệu thống kê và bộ tính thưởng trước, sau đó mới gắn được bất kỳ cơ chế thưởng nào. Đổi lại, **các cơ chế thưởng riêng lẻ đều rẻ** — vì phần nặng đã nằm ở nền tảng.

**Lưu ý về cụm G (kênh X + Threads):** phụ thuộc đội thu thập dữ liệu bên ngoài. Cần xác nhận nguồn dữ liệu có trả về **lượt xem** hay chỉ like/bình luận trước khi cam kết tiến độ — nếu một kênh không có lượt xem thì không áp dụng được cơ chế thưởng theo lượt xem cho kênh đó.

## 1. Hệ thống hiện đang hoạt động thế nào

vCreator là nền tảng kết nối **nhãn hàng** với **creator** (người sáng tạo nội dung).

Luồng hiện tại:

1. Nhãn hàng mở một **chiến dịch** trên nền tảng, kèm ngân sách thưởng.
2. Creator đăng ký tài khoản, chọn chiến dịch để tham gia.
3. Creator quay video, đăng lên mạng xã hội của mình (TikTok, YouTube, Facebook, Instagram), rồi nộp đường dẫn lên hệ thống.
4. Admin duyệt nội dung.
5. Hệ thống tự động thu thập số liệu (lượt xem, like, bình luận) **2 lần mỗi ngày**.
6. Hệ thống tính thưởng theo quy tắc của chiến dịch, đối soát, rồi chuyển tiền vào ví creator. Creator rút tiền về tài khoản ngân hàng.

Toàn bộ đường tiền — từ tính thưởng, đối soát, đến rút tiền — **đã vận hành ổn định**.

## 2. Vấn đề

**Mọi động lực của creator hiện đều đến từ nhãn hàng.** Nền tảng không có công cụ nào để tự thúc đẩy creator.

Hệ quả:

- **Creator mới đăng ký xong rồi bỏ đó.** Không có gì thúc đẩy họ đăng video đầu tiên. Khoảng cách từ "tạo tài khoản" đến "sản xuất nội dung thật" là chỗ rơi rụng nhiều nhất.
- **Creator đăng một hai video rồi biến mất.** Không có gì tạo thói quen đăng đều.
- **Creator giỏi không có lý do gắn bó với nền tảng.** Họ chạy chiến dịch nào có tiền, xong thì đi.

Nhãn hàng chỉ trả tiền cho nội dung thuộc chiến dịch của họ. Không ai trả tiền cho việc **creator lớn lên cùng nền tảng** — và đó chính là thứ nền tảng cần.

## 3. Đề xuất

**Nền tảng tự bỏ tiền, thưởng trực tiếp cho creator dựa trên thành tích trên toàn hệ thống.**

Điểm khác biệt cốt lõi so với thưởng chiến dịch:

| | Thưởng chiến dịch (đang có) | Thưởng tăng trưởng (đề xuất) |
|---|---|---|
| Ai trả tiền | Nhãn hàng | **Nền tảng** |
| Tính trên nội dung nào | Chỉ nội dung thuộc chiến dịch đó | **Toàn bộ nội dung của creator, ở mọi chiến dịch** |
| Ai được thưởng | Ai tham gia chiến dịch | **Nhóm creator được nhắm tới** (giai đoạn đầu: creator mới) |
| Mục tiêu | Chạy được chiến dịch | **Giữ chân và phát triển creator** |

Creator **không cần đăng ký tham gia** chương trình này. Họ cứ đăng nội dung như bình thường; hệ thống tự động ghi nhận và trả thưởng khi đủ điều kiện.

## 4. Chương trình gồm những gì

Năm cơ chế thưởng, mỗi cơ chế nhắm một điểm rơi rụng khác nhau:

| Cơ chế thưởng | Giải quyết vấn đề gì |
|---|---|
| **Thưởng N video đầu tiên được duyệt** | Creator mới đăng ký xong không sản xuất. Thưởng ngay từ video đầu để kéo họ qua vạch xuất phát. |
| **Thưởng theo số video được duyệt mỗi tháng** | Creator đăng vài video rồi biến mất. Tạo thói quen đăng đều. |
| **Thưởng theo lượt xem** | Thưởng theo giá trị thật mà creator tạo ra, không chỉ theo số lượng. |
| **Thưởng theo mốc hiệu suất** | Khuyến khích làm nội dung chất lượng, không phải nội dung số lượng. |
| **Bảng xếp hạng hàng tháng** | Tạo cạnh tranh, giữ nhóm creator dẫn đầu gắn bó với nền tảng. |

Số liệu cụ thể (bao nhiêu video, bao nhiêu tiền, bao nhiêu mốc) **do đội vận hành cấu hình**, không gắn cứng trong hệ thống. Yêu cầu ban đầu là "3 video đầu tiên" — hệ thống sẽ làm "N video đầu tiên" để tháng sau muốn đổi thành 5 thì chỉ sửa cấu hình.

**Kèm theo: mở rộng 2 kênh mới — X (Twitter) và Threads.** Hiện hệ thống chỉ hỗ trợ YouTube, TikTok, Facebook, Instagram.

## 5. Creator sẽ trải nghiệm thế nào

Ví dụ với một creator mới:

> **Ngày 1.** Maria đăng ký tài khoản vCreator. Trên trang chủ app hiện: *"Đăng 3 video đầu tiên được duyệt — nhận tới 500.000đ."*
>
> **Ngày 3.** Maria đăng video đầu tiên cho một chiến dịch mỹ phẩm. Admin duyệt. Cô nhận **100.000đ** — không phải từ ngân sách chiến dịch, mà từ nền tảng. App hiện: *"1/3 video. Còn 2 video nữa."*
>
> **Ngày 10.** Maria hoàn thành đủ 3 video. Nhận nốt phần thưởng hoàn thành. App chuyển sang mục tiêu mới: *"Đăng 10 video trong tháng này để nhận thêm 500.000đ."*
>
> **Cuối tháng.** Video của Maria đạt 200.000 lượt xem. Cô vào **top 10 bảng xếp hạng tháng**, nhận thêm thưởng xếp hạng. App hiện: *"Bạn đang hạng 8. Còn cách hạng 5 khoảng 30.000 lượt xem."*

**Điều quan trọng nhất trong ví dụ trên không phải là tiền — mà là việc Maria luôn nhìn thấy mình đang ở đâu và còn cách mục tiêu bao xa.**

Một chương trình thưởng mà creator không biết mình đang ở đâu thì tiền vẫn mất, nhưng hành vi không đổi — nó chỉ là khoản tiền bất ngờ rơi vào ví. Vì vậy phần hiển thị tiến độ trên app là **bắt buộc**, không phải tuỳ chọn.

## 6. Hệ thống cần bổ sung gì

Tóm tắt (chi tiết kỹ thuật ở [solution-design.md](solution-design.md)):

| Hạng mục | Tình trạng |
|---|---|
| **Bảng thống kê thành tích creator** | Chưa có. Hệ thống hiện chỉ lưu **tiền** của creator, không lưu số video đã duyệt hay tổng lượt xem. Đây là nền móng của cả chương trình — mọi cơ chế thưởng và bảng xếp hạng đều đọc từ đây. |
| **Cơ chế thưởng xuyên chiến dịch** | Chưa có. Toàn bộ logic tính thưởng hiện tại chỉ đếm được nội dung **thuộc một chiến dịch cụ thể**. Chương trình tăng trưởng cần đếm nội dung của creator **trên toàn hệ thống**. |
| **Nhắm nhóm creator** | Chưa có. Hiện không có cách nào giới hạn "chỉ áp dụng cho creator mới". |
| **Bảng xếp hạng** | Chưa có. |
| **Kênh X và Threads** | Chưa có cả hai. |
| **Giao diện tiến độ cho creator** | Chưa có. |
| **Đối soát, ví, rút tiền** | Đã có đầy đủ — **dùng lại nguyên, không sửa.** Đây là phần phức tạp nhất của mọi hệ thống thưởng, và nó vẫn còn nguyên giá trị. |

## 7. Ngoài phạm vi: cơ chế ngân sách

**vCreator-PH hiện không có cơ chế giới hạn ngân sách.** Hệ thống không có trần chi ở bất kỳ cấp nào — an toàn hoàn toàn dựa vào việc admin cấu hình đúng số tiền và số suất.

**Xây cơ chế ngân sách nằm ngoài phạm vi dự án này. Nếu cần, sẽ báo giá riêng.**

Tuy nhiên cần nói rõ một điều: **rủi ro chi vượt sẽ tăng lên chứ không giữ nguyên.**

Thưởng chiến dịch có người duyệt từng bước. Thưởng tăng trưởng thì **tự động** — creator đủ điều kiện là hệ thống trả, đến kỳ xếp hạng là hệ thống trả — và áp cho **toàn bộ creator** thuộc nhóm được nhắm tới. Tự động, phạm vi rộng, không có trần chi: một lỗi cấu hình có thể gây chi vượt rất nhanh mà không có gì chặn lại.

**Ba cơ chế kiểm soát nằm trong phạm vi dự án:**

| # | Cơ chế | Tình trạng |
|---|---|---|
| 1 | **Giới hạn số suất** cho mỗi gói thưởng — bắt buộc đặt, không cho phép để "không giới hạn" | Tận dụng cấu hình **đã có sẵn** |
| 2 | **Giới hạn thời gian** — mỗi gói phải có ngày bắt đầu và kết thúc | Tận dụng cấu hình **đã có sẵn** |
| 3 | **Bảng theo dõi chi** — đã chi bao nhiêu, còn bao nhiêu suất, chi theo thời gian. Admin tự theo dõi và quyết định dừng gói thưởng khi cần | **Xây mới** (đã tính phí, trong cụm A) |

Cộng thêm biện pháp vận hành: **chạy thử phạm vi hẹp** — bật cho một nhóm creator nhỏ, đối chiếu tiền thủ công tháng đầu, rồi mới mở rộng.

Ba cơ chế trên giới hạn *số lần trả*, **không giới hạn *tổng tiền***. Cụ thể, hệ thống **không có ngưỡng theo số tiền** — không chặn chi, và cũng không cảnh báo khi chi vượt một mức tiền nào đó, vì đặt được ngưỡng tiền tức là đã có ngân sách. Muốn trần chi và cảnh báo theo số tiền thì phải làm dự án ngân sách riêng.

## 8. Những gì không nằm trong dự án này

- **Cơ chế ngân sách** (trần chi theo số tiền) — báo giá riêng nếu cần. Xem mục 7.
- **Thu hồi thưởng đã chi** — hệ thống hiện không thu hồi được khoản tiền đã đối soát xong và đã vào ví creator. Dự án này không thay đổi điều đó.
- **Hệ thống Ambassador** — chương trình này chạy cho Philippines trước; Ambassador sẽ xem xét sau.
