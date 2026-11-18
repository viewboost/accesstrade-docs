# Đặc tả sản phẩm và phạm vi nghiệm thu
### Chương trình **Chiến binh Vietjet Hybrid** · Phase 1

**Phiên bản:** 0.1 (nháp) · **Ngày:** 17/11/2026 · **Người soạn:** Vinh Nguyễn
**Dùng để:** nghiệm thu nội bộ (M04) và nghiệm thu với khách hàng Vietjet (M05)
**Tài liệu chi tiết đi kèm:** [README.md](./README.md) (mục lục PRD CN-01 đến CN-09 và kịch bản kiểm thử)

Tài liệu này mô tả **sản phẩm có những chức năng gì** và **gì thuộc / không thuộc phạm vi nghiệm thu**. Chỉ nói ở tầng chức năng. Quy tắc chi tiết, kịch bản kiểm thử từng bước nằm ở PRD; hạ tầng, kỹ thuật không nằm ở đây.

---

## 1. Tổng quan

### 1.1 Sản phẩm là gì

Một ứng dụng web cho **cán bộ nhân viên (CBNV) Vietjet** đăng nội dung về Vietjet lên mạng xã hội (TikTok, Facebook, Instagram), gửi đường dẫn bài về hệ thống, và **tích điểm** khi bài được Ban tổ chức (BTC) duyệt. Cuối chương trình, BTC lấy **danh sách xếp hạng theo tổng điểm** để Operation trao quà bên ngoài hệ thống.

Hệ thống chạy trên nền tảng Ambassador của AccessTrade, điều chỉnh từ chương trình thưởng bằng tiền theo lượt xem sang **chương trình thưởng bằng điểm**.

### 1.2 Cách chương trình vận hành

- **Mỗi tháng là một chương trình riêng**: có điểm riêng, bảng xếp hạng riêng, đối soát và trao thưởng riêng. Điểm không cộng dồn giữa các chương trình.
- Người tham gia đăng bài đúng hashtag, gửi link, BTC duyệt thì được điểm cố định theo loại bài.
- Cuối chương trình BTC chọn một **ngày chốt**: trước ngày chốt còn cập nhật được màn đối soát, sau ngày chốt không thay đổi gì nữa.
- Sau khi đối soát xong, BTC xuất file xếp hạng. Phần thưởng (vé SFC, voucher, tiền mặt) do **Operation và Vietjet trao bên ngoài hệ thống**.

### 1.3 Kết quả mong đợi

| Kết quả | Cách kiểm |
|---|---|
| Chỉ CBNV Vietjet tham gia được | Chỉ email thuộc tên miền công ty, có mã nhân viên hợp lệ |
| Điểm tính đúng theo thể lệ | Mỗi bài được duyệt đúng số điểm theo loại bài, không phụ thuộc lượt xem |
| Xếp hạng công bằng | Xếp theo tổng điểm; bằng điểm thì người đạt điểm đó sớm hơn xếp trên |
| BTC lấy được kết quả để trao quà | File xếp hạng cuối chương trình có đủ người và có mức đạt |
| Không còn chức năng ngoài chương trình | Không còn thanh toán tiền, thuế, hợp đồng điện tử, định danh, affiliate |

---

## 2. Đối tượng sử dụng

| Vai trò | Là ai | Làm gì |
|---|---|---|
| **Người tham gia** | CBNV Vietjet đã đăng ký | Đăng bài, gửi link, xem điểm, mức thưởng, bảng xếp hạng |
| **BTC (Admin)** | Ban tổ chức | Cấu hình chương trình, duyệt bài, đối soát, xuất file xếp hạng |
| **HR Vietjet** | Bộ phận nhân sự | Cung cấp danh sách mã nhân viên |
| **Operation** | Đội trao quà | Dùng file xếp hạng để trao quà ngoài hệ thống |

---

## 3. Phạm vi

### 3.1 Trong phạm vi nghiệm thu

| # | Nhóm | Chức năng |
|---|---|---|
| A | **Tài khoản** | A1 Đăng ký và đăng nhập bằng email Vietjet · A2 Mã nhân viên · A3 Quên mật khẩu, đăng nhập không mật khẩu |
| B | **Gửi bài và tích điểm** | B1 Gửi link bài đăng · B2 Điểm cố định mỗi bài · B3 Duyệt và từ chối bài |
| C | **Người tham gia xem** | C1 Trang cá nhân và điểm từng bài · C2 Mức thưởng · C3 Bảng xếp hạng · C4 Số liệu tổng quan và thông báo |
| D | **Đối soát** | D1 Đối soát thưởng theo bài (tab riêng) · D2 Thưởng thêm TOP hàng tháng |
| E | **Xếp hạng và kết quả** | E1 Bảng xếp hạng và file TOP · E2 Tiêu chí phụ khi bằng điểm · E3 File kết quả cuối chương trình |
| F | **Hiển thị điểm** | F1 Chữ "điểm" thay cho "đ" ở mọi màn hình và file xuất · F2 Ẩn các màn thanh toán |
| G | **Cấu hình chương trình** | G1 Tạo chương trình tháng, nhiệm vụ điểm, thời hạn · G2 Tên miền email và danh sách mã nhân viên |

### 3.2 Ngoài phạm vi

| # | Hạng mục | Lý do |
|---|---|---|
| 1 | Trao quà, theo dõi đã trao hay chưa | Operation làm bên ngoài hệ thống |
| 2 | Chi tiền, thuế, rút tiền về ngân hàng | Thưởng tiền mặt chuyển thẳng vào lương bên Vietjet; hệ thống không chi trả |
| 3 | Hợp đồng điện tử, định danh, mã số thuế, hoa hồng affiliate | Không dùng cho chương trình này, đã gỡ khỏi giao diện |
| 4 | Đăng nhập bằng TikTok, Facebook, Google | Không xác nhận được email công ty; chỉ đăng nhập bằng email |
| 5 | Trừ điểm sau khi đã đối soát | Gian lận phát hiện trước đối soát thì từ chối bài, điểm tự mất |
| 6 | Giới hạn số bài mỗi người mỗi ngày | Thể lệ không có |
| 7 | Kiểm tra bài bị gỡ hoặc ẩn trước đối soát | BTC kiểm tay theo thể lệ |
| 8 | Kiểm tra trùng nội dung đăng lại ở nền tảng khác | Chờ AT-Core, tạm hoãn |
| 9 | Đổi điểm thành tiền hoặc quà trong hệ thống | Không có trong thể lệ |
| 10 | Ứng dụng di động riêng | Chỉ dùng web, hiển thị tốt trên điện thoại |

---

## 4. Mô tả chức năng và tiêu chí nghiệm thu

Mỗi chức năng gồm: mô tả ngắn, rồi các tiêu chí nghiệm thu. Chi tiết quy tắc xem PRD tương ứng.

### A. Tài khoản · PRD [CN-09](./prd-cn09-dang-nhap-email-vietjet.md)

**A1. Đăng ký và đăng nhập bằng email Vietjet.** Nhân viên đăng ký bằng email công ty. Hệ thống gửi một **mã xác thực kèm đường dẫn** vào email: nhập mã hoặc bấm đường dẫn đều được, hiệu lực 5 phút, dùng một lần. Xác thực xong mới đặt mật khẩu.
- [ ] Email thuộc tên miền Vietjet đăng ký và đăng nhập được
- [ ] Email ngoài tên miền (ví dụ Gmail) bị từ chối, báo phải dùng email công ty
- [ ] Chưa xác thực email thì chưa có mật khẩu và chưa đăng nhập được
- [ ] Gửi lại mã phải cách nhau ít nhất 1 phút; nhập sai nhiều lần thì phải xin mã mới
- [ ] Người khác biết email của nhân viên cũng không đặt trước được mật khẩu thay họ
- [ ] Không có nút đăng nhập TikTok, Facebook, Google

**A2. Mã nhân viên.** Màn đăng ký bắt buộc nhập mã nhân viên. Mã được kiểm theo danh sách do HR cung cấp, và một mã chỉ gắn với một tài khoản.
- [ ] Không nhập mã thì không hoàn tất đăng ký
- [ ] Mã không có trong danh sách HR bị từ chối
- [ ] Mã đã gắn với tài khoản khác bị từ chối
- [ ] Người chưa xác thực email công ty không tham gia được chương trình

**A3. Quên mật khẩu và đăng nhập không mật khẩu.** Nhân viên lấy lại mật khẩu bằng mã/đường dẫn gửi qua email, hoặc đăng nhập thẳng bằng mã/đường dẫn.
- [ ] Quên mật khẩu đặt được mật khẩu mới; các phiên đăng nhập cũ bị đăng xuất
- [ ] Đăng nhập không mật khẩu chỉ cho tài khoản đã có, không tạo tài khoản mới
- [ ] Thông báo giống nhau dù email có tài khoản hay không (không dò được email nào đã đăng ký)
- [ ] Gửi quá nhiều thư hoặc nhập sai mã quá nhiều thì bị chặn tạm, tài khoản không bị khóa

### B. Gửi bài và tích điểm · PRD [CN-01](./prd-cn01-diem-co-dinh-moi-bai.md), [REF](./ref-nen-tang-loai-bai.md)

**B1. Gửi link bài đăng.** Người tham gia dán link bài TikTok, Facebook (Post hoặc Reels) hoặc Instagram. Hệ thống kiểm hashtag bắt buộc **#Vietjet** và **#ChienBinhVietjetHybrid** (không phân biệt hoa thường). Bài phải để chế độ công khai.
- [ ] Gửi được link của từng nền tảng được tính
- [ ] Thiếu hashtag bắt buộc thì từ chối và nêu hashtag còn thiếu
- [ ] Màn gửi bài hiện hashtag bắt buộc, nhắc để chế độ công khai, báo bài chờ BTC duyệt
- [ ] Bài chỉ tính nếu ngày đăng nằm trong thời hạn của chương trình
- [ ] Bài TikTok chỉ gửi được khi thuộc tài khoản TikTok đã liên kết của chính người gửi

**B2. Điểm cố định mỗi bài.** Mỗi bài được duyệt nhận điểm cố định theo loại bài, không phụ thuộc lượt xem. Mức điểm do BTC nhập khi cấu hình (ví dụ bài post 25 hoặc 50, video 50 hoặc 100, theo bảng thể lệ chốt). Instagram (ảnh và Reels) tính theo mức video.
- [ ] Duyệt một bài thì có đúng một khoản điểm, đúng mức của loại bài
- [ ] Số điểm không đổi dù bài có 10 hay 10.000 lượt xem
- [ ] Đổi bảng điểm chỉ áp cho bài gửi sau đó
- [ ] Mọi bài của một người đều được tính (không giới hạn số bài)

**B3. Duyệt và từ chối bài.** BTC duyệt hoặc từ chối bài, từ chối kèm lý do. Điểm chờ duyệt hiện riêng, chỉ thành điểm hợp lệ sau khi duyệt.
- [ ] Bài chờ duyệt hiện điểm chờ duyệt; bài được duyệt hiện điểm của bài
- [ ] Bài bị từ chối không có điểm và hiện lý do
- [ ] Từ chối rồi duyệt lại thì điểm trở lại, không bị tính hai lần
- [ ] Hết ngân sách của chương trình thì khoản mới ghi 0 điểm, không tính âm

### C. Người tham gia xem · PRD [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md), [CN-03](./prd-cn03-hien-thi-diem.md)

**C1. Trang cá nhân và điểm từng bài.** Hiện tổng điểm, điểm chờ duyệt, số bài đã duyệt, chờ duyệt, từ chối; mỗi bài hiện điểm của bài. Không còn hiện lượt xem, thích, bình luận làm chỉ số thưởng.
- [ ] Số điểm khớp với các bài đã duyệt
- [ ] Mỗi bài hiện đúng điểm hoặc lý do từ chối
- [ ] Không hiện điểm cộng dồn qua các chương trình khác

**C2. Mức thưởng.** Hiện bốn mức theo thể lệ (trên 200, 400, 600, 1.500 điểm) kèm phần thưởng và số lượng, cạnh tổng điểm hiện tại của người xem. Đây chỉ là thông tin: không có nhãn đã đạt hay chưa đạt, vì mức thưởng do BTC xét sau khi đối soát.
- [ ] Hiện đủ bốn mức với mốc, phần thưởng, số lượng
- [ ] Trang cá nhân hiện tổng điểm hiện tại cạnh bảng mức; không có nhãn đã đạt hay chưa đạt
- [ ] Hiện ở trang chi tiết chương trình và ở trang cá nhân

**C3. Bảng xếp hạng.** Xếp theo điểm của chương trình đang xem, TOP 1, 2, 3 có nhãn kèm điểm thưởng 500, 200, 100.
- [ ] Bảng đúng thứ tự điểm, hiện cột Điểm
- [ ] Nhãn TOP đúng: hạng 1; hạng 2 đến 3; hạng 4 đến 6

**C4. Số liệu tổng quan và thông báo.** Trang chủ hiện số bài được duyệt và tổng điểm; người tham gia nhận thông báo trong ứng dụng khi bài được duyệt.
- [ ] Không còn ô "Lượt xem", "Tiền thưởng" của sản phẩm cũ
- [ ] Thông báo bài được duyệt hiện đúng

### D. Đối soát · PRD [CN-02](./prd-cn02-doi-soat-thuong-theo-bai.md), [CN-05](./prd-cn05-bang-xep-hang-thang.md)

**D1. Đối soát thưởng theo bài.** Màn đối soát có tab riêng **Thưởng theo bài**, mỗi bài một dòng (người tham gia, link bài, điểm). BTC lấy danh sách, duyệt hoặc từ chối từng dòng hoặc cả kỳ. Duyệt xong khoản chuyển **Đã hoàn thành**.
- [ ] Chỉ các bài đã duyệt và còn hợp lệ vào danh sách
- [ ] Mỗi khoản chỉ nằm trong một kỳ đối soát
- [ ] Từ chối dòng thì dòng đó không tính điểm
- [ ] Xuất được file Excel của kỳ đối soát

**D2. Thưởng thêm TOP hàng tháng.** BTC xuất file TOP, xác nhận danh sách, rồi cộng điểm thưởng **500, 200, 100** cho các hạng bằng chức năng Thưởng thêm có sẵn; khoản này đối soát như các khoản khác.
- [ ] Cộng được điểm TOP cho từng người, nhập tay hoặc từ Excel
- [ ] Điểm TOP đã hoàn thành nằm trong file kết quả cuối chương trình

### E. Xếp hạng và kết quả · PRD [CN-05](./prd-cn05-bang-xep-hang-thang.md), [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md)

**E1. Bảng xếp hạng và file TOP.** Tab Bảng xếp hạng của chương trình có nút **Tải file**: file đủ toàn bộ danh sách, cùng thứ tự với bảng. Có tùy chọn cộng điểm Thưởng thêm vào bảng (mặc định tắt: tắt khi chọn TOP bằng điểm bài, bật sau khi đã cộng điểm TOP).
- [ ] File có đủ người, đúng thứ tự bảng
- [ ] Bật tùy chọn thì điểm TOP đã hoàn thành được cộng vào bảng và file
- [ ] Nhân sự của đối tác khác không tải được

**E2. Tiêu chí phụ khi bằng điểm.** Hai người cùng điểm thì người **đạt điểm đó sớm hơn** xếp trên, tính theo **giờ đăng bài lên mạng xã hội** của bài hợp lệ gần nhất; vẫn bằng thì theo mã người dùng để thứ tự cố định.
- [ ] Cùng điểm, giờ đăng khác nhau: người đăng sớm hơn xếp trên, không phụ thuộc thứ tự BTC duyệt
- [ ] Bài bị từ chối trước đối soát thì không tính vào điểm và giờ đạt
- [ ] Thứ tự ổn định giữa các lần xem, kể cả khi chia trang

**E3. File kết quả cuối chương trình.** Nút **Xuất kết quả cuối chương trình**: BTC nhập số người cần lấy (mặc định 2.200), hệ thống tạo file xếp hạng theo tổng điểm của các khoản **đã hoàn thành**. Các cột: hạng, mã người dùng, tên, mã nhân viên, email, tổng điểm, thời điểm đạt tổng điểm, số bài hợp lệ, **mức đạt** (theo mốc điểm), **mức được suất** (theo số suất 2.000, 500, 100, 10) và ghi chú.
- [ ] Xếp đúng tổng điểm, bằng điểm thì theo tiêu chí phụ
- [ ] Người bằng cả điểm lẫn giờ ở ranh giới được lấy cả nhóm và có ghi chú để BTC xét tay
- [ ] Dòng đầu cảnh báo số khoản chưa đối soát; chỉ tính khoản đã hoàn thành
- [ ] Mức đạt và mức được suất đúng với mốc 200, 400, 600, 1.500 và số suất
- [ ] Chỉ người có quyền xuất mới tải được; email được che theo quyền; không có cột tiền, hợp đồng, mã số thuế

### F. Hiển thị điểm · PRD [CN-03](./prd-cn03-hien-thi-diem.md)

**F1. Chữ "điểm".** Mọi số thưởng của chương trình hiện **"điểm"** thay cho "đ" ở giao diện người tham gia, trang quản trị và file Excel xuất.
- [ ] Không còn "đ" hoặc "VNĐ" ở các màn và file của chương trình

**F2. Ẩn màn thanh toán.** Các màn không thuộc chương trình (thông tin thanh toán, hợp đồng điện tử, mã số thuế, định danh, hoa hồng affiliate, rút tiền) được ẩn khỏi menu; vào thẳng đường dẫn thì về trang chủ.
- [ ] Menu không còn các mục trên; đường dẫn cũ đưa về trang chủ

### G. Cấu hình chương trình · PRD [CN-01](./prd-cn01-diem-co-dinh-moi-bai.md), [CN-09](./prd-cn09-dang-nhap-email-vietjet.md)

**G1. Tạo chương trình tháng.** BTC tạo một sự kiện cho mỗi tháng: nhiệm vụ điểm cố định theo từng nền tảng, thời hạn (tính theo ngày đăng bài), hashtag, ngân sách, cách xếp hạng (theo điểm thưởng, kỳ cả chương trình).
- [ ] Kích hoạt được chương trình chỉ có nhiệm vụ điểm cố định
- [ ] Bài đăng ngoài thời hạn không được thưởng
- [ ] Bảng xếp hạng của chương trình xếp theo điểm thưởng

**G2. Tên miền email và danh sách mã nhân viên.** BTC khai báo tên miền email công ty được phép; HR nhập danh sách mã nhân viên bằng file Excel ở trang quản trị.
- [ ] Để trống danh sách tên miền thì không email nào đăng ký được
- [ ] Nhập được danh sách mã từ Excel; mã gắn nhầm tài khoản thì Admin gỡ được

---

## 5. Quy tắc nghiệp vụ chính của thể lệ

| Nội dung | Quy tắc |
|---|---|
| Đối tượng | CBNV Vietjet đã đăng ký, có email công ty và mã nhân viên |
| Hashtag bắt buộc | #Vietjet và #ChienBinhVietjetHybrid |
| Nền tảng tính điểm | Facebook (Post, Reels), TikTok, Instagram (tính theo mức video) |
| Điểm bài | Cố định theo loại bài, BTC nhập mức điểm khi cấu hình |
| Thưởng TOP hàng tháng | TOP 1: 500 điểm (1 người) · TOP 2: 200 điểm (2 người) · TOP 3: 100 điểm (3 người) |
| Mức thưởng cuối chương trình | Mức 1 trên 200 (2.000 suất) · Mức 2 trên 400 (500 suất) · Mức 3 trên 600 (100 suất) · Mức 4 trên 1.500 (10 suất); nhận cộng dồn |
| Khi nào xét thưởng | Một lần, theo tổng điểm tại ngày chốt, sau khi BTC đối soát |
| Bằng điểm | Người đạt điểm đó sớm hơn (giờ đăng bài) xếp trên |
| Gian lận | Bài vi phạm bị từ chối trước ngày chốt thì mất điểm |

---

## 6. Điều kiện để nghiệm thu

Việc nghiệm thu chạy được khi đã có:

1. **Mẫu email** của ba luồng (đăng ký, đặt lại mật khẩu, đăng nhập không mật khẩu) do AccessTrade tạo; chưa có thì người dùng thật chưa nhận được thư.
2. **Danh sách mã nhân viên** của HR đã nhập vào hệ thống.
3. **Cấu hình đối tác Vietjet**: tên miền email công ty, chế độ chỉ đăng nhập bằng email, kiểm mã nhân viên theo danh sách.
4. **Chương trình tháng** đã tạo với bảng điểm đã chốt (25/50 hay 50/100), hashtag, thời hạn, ngân sách đủ lớn, xếp hạng theo điểm thưởng.
5. **Ngày bắt đầu, kết thúc và ngày chốt** của từng chương trình do BTC thông báo.

## 7. Hạng mục còn chờ chốt

| # | Hạng mục | Tình trạng |
|---|---|---|
| 2 | Nền tảng khác (YouTube Shorts, Threads) có tính điểm không | Chờ BTC và Vietjet |
| 3 | Giao diện người tham gia theo thiết kế mới | Chờ thiết kế |
| 4 | Ẩn số điểm cộng dồn qua các chương trình ở trang quản trị (tab Thống kê người dùng) | Chờ xác nhận phạm vi |
| 5 | Kiểm tra trùng nội dung đăng lại | Tạm hoãn, chờ AT-Core |
| 6 | Thông báo qua email khi đạt mức; màn xem tiến độ tới mức kế tiếp | Chưa quyết định |

## 8. Tiêu chí chấp nhận tổng thể

Sản phẩm được nghiệm thu khi:

- [ ] Một người tham gia đi trọn luồng: đăng ký bằng email Vietjet và mã nhân viên → gửi bài → được duyệt → có điểm → thấy mức thưởng và bảng xếp hạng
- [ ] BTC đi trọn luồng: tạo chương trình → duyệt bài → đối soát → xuất file TOP → cộng điểm TOP → xuất file kết quả cuối chương trình
- [ ] Tất cả tiêu chí nghiệm thu ở mục 4 đạt, trừ các hạng mục ở mục 7
- [ ] Không còn chức năng thanh toán tiền, thuế, hợp đồng điện tử, định danh, affiliate hiện ra cho người tham gia
- [ ] Các luồng tài khoản (email, mã nhân viên, quên mật khẩu) chạy được với hộp thư thật của Vietjet

---

## Phụ lục: thuật ngữ

| Từ | Nghĩa |
|---|---|
| BTC | Ban tổ chức chương trình |
| CBNV | Cán bộ nhân viên Vietjet |
| Chương trình | Một sự kiện trong hệ thống; mỗi tháng một chương trình |
| Đối soát | Bước BTC kiểm và xác nhận các khoản điểm; khoản xác nhận xong thành **Đã hoàn thành** |
| Thưởng thêm | Chức năng BTC cộng điểm thủ công, dùng cho điểm TOP hàng tháng |
| Ngày chốt | Ngày BTC chọn để dừng cập nhật điểm và lấy kết quả |
| Mức đạt | Mức thưởng người đó đạt theo mốc điểm |
| Mức được suất | Mức thưởng người đó được nhận sau khi tính số suất giới hạn |
