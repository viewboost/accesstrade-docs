# PRD: `creator-app` — portal chung cho ADV mới

Bối cảnh và lý do: [project-overview-creator-app-2026-09-07.md](project-overview-creator-app-2026-09-07.md)

---

## 1. Mục tiêu

Một website dùng chung cho mọi ADV mới. Mỗi ADV có domain riêng và nhận diện riêng của họ, nhưng không còn
là một bản mã nguồn riêng.

Ba kết quả phải đạt:

| | Hôm nay | Sau `creator-app` |
|---|---|---|
| Đưa một ADV mới lên sóng | Dev tạo thư mục mã nguồn, sửa quy trình phát hành, phát hành riêng | Ops nhập thông tin trên admin |
| Đổi logo, màu, nội dung của một ADV | Dev sửa mã nguồn, phát hành lại | Ops sửa trên admin, có hiệu lực ngay |
| Cho khách xem thử khi chào hàng | Designer dựng Figma, vài vòng phản hồi | BD tự dựng site demo |

`creator-app` chỉ phục vụ **ADV mới**. 14 website hiện có giữ nguyên, không đụng tới.

---

## 2. Người dùng

**BD** — dùng ở giai đoạn chào khách. Cần dựng được site demo mang thương hiệu của khách trên sandbox
trong vài phút, gửi link cho khách xem, mà không nhờ designer hay dev. Không phải kỹ sư.

**Ops** — người dùng chính. Hoàn tất toàn bộ phần cấu hình để một ADV lên sóng, và sửa về sau khi ADV đổi
yêu cầu. Diễn tập trọn một lần trên sandbox trước khi làm thật. Không phải kỹ sư, và sai thì phải khôi
phục được.

**Designer** — hôm nay nằm trên đường đi của mọi thương vụ. Sau dự án chỉ tham gia khi ADV cần thứ nằm
ngoài bộ cấu hình, hoặc để chuẩn bị bộ nhận diện gửi lên.

**Dev** — sau khi `creator-app` chạy, không tham gia vào việc đưa ADV mới lên sóng.

**ADV** — bên duyệt nhận diện của chính họ. Xem demo, phản hồi, chốt.

**Người dùng cuối** — nhà sáng tạo nội dung tham gia chiến dịch. Không được thấy khác biệt nào so với các
website hiện có.

---

## 3. Phạm vi

### 3.1 Trong phạm vi

- `creator-app` — website dùng chung, dựng trên `fecredit` sau khi bóc sạch lớp thương hiệu FE Credit
- Bản ghi cấu hình cho mỗi ADV, đọc lúc chạy
- Màn cấu hình trong admin hiện hành
- Môi trường sandbox để BD dựng demo và ops diễn tập onboard

### 3.2 Ngoài phạm vi

- 14 website hiện có — không đụng tới, kể cả sửa lỗi
- Chuyển các ADV đang chạy sang `creator-app`
- Đổi nền tảng frontend
- Trình dựng trang tự do, hoặc cho ADV tự nhập mã
- Đa ngôn ngữ
- ADV truy cập admin trực tiếp
- Bảy lỗi đang chạy trên production đã ghi nhận ở khảo sát trước

Bốn thứ dưới đây **cố ý không đưa vào**, vì hôm nay chưa tồn tại. Phạm vi đợt này chỉ chuyển sang cho ops
những việc dev đang phải làm, không thêm năng lực mới:

- Luồng nháp, xem trước, xuất bản, khôi phục phiên bản
- Trình lắp và sắp xếp khối trên trang chủ
- Đối chiếu chéo chặn khi cấu hình trùng dữ liệu của ADV khác
- Danh sách kiểm tiến độ onboard và trạng thái đang dựng

---

## 4. Yêu cầu chức năng

### CA-001 — Một website phục vụ nhiều ADV, phân giải theo domain

**Vì sao cần.** Đây là điều kiện để mọi yêu cầu còn lại tồn tại. Một bản chạy duy nhất phải phục vụ được
nhiều ADV với nhận diện khác nhau.

**Yêu cầu**

- Mỗi domain đăng ký cho một ADV sẽ hiện đúng nhận diện và nội dung của ADV đó
- Cấu trúc đường dẫn giữ nguyên như các website hiện có
- Domain chưa đăng ký hiện trang báo lỗi nói rõ domain chưa được cấu hình, **không tự chuyển hướng đi đâu khác**

**Nghiệm thu**

- [ ] Hai domain trên cùng một bản chạy hiện hai bộ nhận diện khác nhau
- [ ] Domain lạ hiện thông báo domain chưa đăng ký, không có chuyển hướng

---

### CA-002 — Nhận diện thương hiệu là dữ liệu

**Vì sao cần.** Đây là thứ buộc mỗi ADV phải có một bản mã nguồn riêng. Chuyển được nó thành dữ liệu thì
chuỗi fork dừng lại.

**Yêu cầu**

- Màu thương hiệu, bo góc, phông chữ, logo, favicon, ảnh chia sẻ, ảnh trang trí đều nhập trên admin
- Đổi bất kỳ giá trị nào và lưu là website đổi theo, **không cần phát hành lại**
- Bộ giá trị mặc định là bộ đang chạy hôm nay, để ADV không điền gì vẫn ra giao diện đúng

**Ràng buộc đã biết.** Hôm nay màu của **nút** được cố định lúc biên dịch, khác với màu chữ và viền vốn đổi
được lúc chạy. Yêu cầu này chỉ coi là đạt khi đổi màu thương hiệu thì **nút cũng đổi theo**. Cách làm là
việc của thiết kế kỹ thuật, nhưng nếu bỏ qua thì ops đổi màu xong sẽ thấy nút vẫn màu cũ.

**Nghiệm thu**

- [ ] Đổi màu thương hiệu, lưu, tải lại: **chữ, viền, nền và nút** đều đổi theo
- [ ] Đổi logo và phông chữ: website đổi theo, không phát hành lại
- [ ] Tải trang trên mạng chậm không thấy nhấp nháy màu mặc định trước khi đổi
- [ ] Không giá trị thương hiệu nào của một ADV còn nằm trong mã nguồn

---

### CA-003 — Asset và phông chữ tải lên qua admin

**Vì sao cần.** Mỗi ADV có bộ logo, ảnh trang trí và phông chữ riêng. Hôm nay chúng là file nằm trong mã nguồn.

**Yêu cầu**

- Ops tải lên logo, favicon, ảnh chia sẻ, ảnh trang trí và file phông chữ
- Bộ ảnh bắt buộc tối thiểu phải đủ trước khi ADV lên sóng; các ảnh còn lại là tuỳ chọn và đặt tên tự do,
  vì mỗi ADV có số lượng khác nhau
- Thiếu một ảnh tuỳ chọn thì dùng ảnh mặc định của hệ thống, **không vỡ bố cục**
- Chỉ nhận đường dẫn nội bộ hoặc đường dẫn web hợp lệ

**Nghiệm thu**

- [ ] Đổi logo và lưu: website cập nhật, không phát hành lại
- [ ] Tải lên phông chữ riêng: chỉ áp dụng cho ADV đó
- [ ] Thiếu ảnh tuỳ chọn: trang vẫn hiển thị bình thường
- [ ] Đường dẫn không hợp lệ bị từ chối ngay khi lưu

---

### CA-004 — Nội dung theo ADV

**Vì sao cần.** Hotline, email, mạng xã hội, bài điều khoản là nội dung của từng ADV, hôm nay nằm rải trong
mã nguồn và biến môi trường.

**Yêu cầu**

- Nhập trên admin: hotline, email, các liên kết mạng xã hội, liên kết website đối tác
- Chọn ba bài viết dùng chung cho ADV: Câu hỏi thường gặp, Điều khoản, Chính sách — chọn từ danh sách bài đã có
- Thể lệ và Hướng dẫn **giữ nguyên theo từng chiến dịch**, không kéo lên mức ADV, vì một ADV có thể chạy
  nhiều chiến dịch với thể lệ khác nhau

**Nghiệm thu**

- [ ] Đổi hotline và mạng xã hội: website cập nhật, không phát hành lại
- [ ] Ba bài viết chọn được từ danh sách, thiếu bất kỳ bài nào thì không lưu được
- [ ] Form chiến dịch trong admin không thay đổi

---

### CA-005 — SEO và thẻ chia sẻ theo từng domain

**Vì sao cần.** Hôm nay dev khai các thẻ này trong mã nguồn và biến môi trường cho từng ADV. Một bản chạy
phục vụ nhiều domain thì các thẻ đó không gán cứng được nữa.

**Yêu cầu**

- Tiêu đề, mô tả, từ khoá, ảnh chia sẻ và mã đo lường nhập theo từng ADV
- Địa chỉ chuẩn hoá và địa chỉ chia sẻ sinh theo **chính domain người dùng đang truy cập**
- Không khai mã đo lường thì không chèn mã đo lường nào

**Nghiệm thu**

- [ ] Hai domain trả hai bộ thẻ chia sẻ khác nhau
- [ ] Địa chỉ chuẩn hoá trỏ về đúng domain đang truy cập
- [ ] Mã đo lường trên mỗi trang là của đúng ADV đó

---

### CA-006 — Bật tắt tính năng theo ADV

**Vì sao cần.** Hôm nay một ADV có tính năng nào là do fork của ADV đó được dựng kèm màn hình đó hay không.
Hai tính năng đang lệch giữa các ADV: **Hợp đồng điện tử** — 14/15 website có, `vpbank` không — và
**Quản lý hoa hồng affiliate**, chỉ `fecredit` có.

**Yêu cầu**

- Ops bật tắt từng tính năng cho mỗi ADV
- Tắt một tính năng thì mục đó biến khỏi thanh điều hướng **và** người dùng gõ thẳng địa chỉ cũng không vào được

**Nghiệm thu**

- [ ] Tắt Hợp đồng điện tử: mục biến khỏi điều hướng và gõ thẳng địa chỉ bị chặn
- [ ] Hai ADV trên cùng bản chạy, một bật một tắt, hoạt động độc lập

---

### CA-007 — Nội dung trang chủ theo ADV

**Vì sao cần.** Hôm nay dev sửa chữ và ảnh trên trang chủ cho từng ADV ngay trong mã nguồn, rồi phát hành lại.

**Yêu cầu**

- Bố cục trang chủ **dùng chung cho mọi ADV**, giữ đúng như các website hiện có
- Ops sửa được phần nội dung mà hôm nay dev sửa: tiêu đề, mô tả chương trình, chữ trên các khối, ảnh minh hoạ
- Khối lấy dữ liệu từ hệ thống — chiến dịch, bảng xếp hạng, thống kê — giữ nguyên cách hoạt động hiện tại,
  ops không nhập tay dữ liệu vào đó

**Nghiệm thu**

- [ ] Sửa nội dung trang chủ và lưu: website đổi theo, không phát hành lại
- [ ] Trang chủ của hai ADV khác nhau về nội dung và nhận diện, giống nhau về bố cục
- [ ] Ops không nhập được dữ liệu chiến dịch hay bảng xếp hạng bằng tay

---

### CA-008 — Sandbox để dựng thử một ADV từ đầu

**Vì sao cần.** Hai việc cần một nơi làm thật mà không chạm hệ thống đang chạy: BD cho khách xem website
mang thương hiệu của họ khi chào hàng, và ops đi trọn một lần onboard trước khi làm trên production.

**Yêu cầu**

- Sandbox là môi trường tách khỏi hệ thống đang chạy. Mọi thao tác trong đó không tạo ra thay đổi nào
  trên production
- Làm được **đúng những việc như trên production**: tạo ADV từ số không, nhập nhận diện, nội dung, cấu hình,
  lưu, rồi xem website chạy thật
- Có link chia sẻ để khách hoặc người duyệt tự mở xem, không cần tài khoản
- Quyền vào sandbox **mở theo nhu cầu và đóng lại khi xong**, không để mở thường trực
- Bộ nhận diện đã nhập trong sandbox **chuyển sang hồ sơ thật được, không nhập lại từ đầu**

**Nghiệm thu**

- [ ] BD tạo và xem được site demo mang thương hiệu khách mà không nhờ designer hay dev
- [ ] Ops đi trọn một lần setup ADV mới trong sandbox, các bước giống hệt production
- [ ] Khách mở link xem được, không cần đăng nhập
- [ ] Thao tác trong sandbox không tạo thay đổi nào trên hệ thống đang chạy
- [ ] Đóng quyền sau khi xong: người vừa dùng không còn vào được
- [ ] Bộ nhận diện từ sandbox chuyển sang hồ sơ thật, giữ nguyên dữ liệu đã nhập

---

### CA-009 — Không kế thừa dữ liệu của ADV khác

**Vì sao cần.** Vì mỗi ADV mới sao chép từ ADV trước, website đối tác này đang hiện hotline, email, kênh
mạng xã hội và bài điều khoản của đối tác khác. Sang mô hình cấu hình, lỗi đó không được phép đi theo.

**Yêu cầu**

- ADV mới bắt đầu với **mọi trường rỗng** — không giá trị nào mượn từ ADV trước, không giá trị mặc định
  ẩn nào thay thế khi bỏ trống
- Thiếu trường bắt buộc thì không lưu được, và thông báo liệt kê **đủ** các chỗ còn thiếu

**Nghiệm thu**

- [ ] Tạo ADV mới: mọi trường bắt buộc đều rỗng
- [ ] Bỏ trống trường bắt buộc: bị chặn, thông báo liệt kê đủ các trường thiếu
- [ ] Không màn nào của một ADV hiển thị giá trị của ADV khác

---

### CA-010 — Bộ trường đủ để đưa một ADV lên sóng

**Vì sao cần.** Ops chỉ tự làm được nếu bộ trường trên admin phủ hết những gì hôm nay dev phải sửa. Thiếu
một trường là việc quay về tay dev.

**Yêu cầu**

- Bộ trường trên admin phủ **toàn bộ** những gì dev đang sửa trong mã nguồn và biến môi trường cho mỗi ADV
- Có mẫu thông tin để BD gửi ADV thu thập, khớp đúng các trường cần nhập

**Nghiệm thu**

- [ ] Đối chiếu với việc dev đã làm ở lần onboard gần nhất: không hạng mục nào thiếu chỗ nhập
- [ ] Ops hoàn tất một ADV mới từ đầu đến cuối mà không cần hỏi ai

---

### CA-011 — Màn cấu hình cho người không phải kỹ sư

**Vì sao cần.** BD và ops là người dùng, không phải dev. Màn khó dùng thì việc quay về tay dev.

**Yêu cầu**

- Dựng trong admin hiện hành, đặt cạnh màn quản lý đối tác
- Nhãn tiếng Việt rõ nghĩa; chọn màu bằng bảng màu chứ không gõ mã màu
- Thông báo lỗi nói **sai gì và sửa thế nào**, không hiện tên trường kỹ thuật
- Mọi kiểm tra phía máy chủ đều có thông báo tương ứng trên biểu mẫu
- Nghiệm thu bằng một buổi thao tác thật, không phải bằng đọc mã nguồn

**Nghiệm thu**

- [ ] Ops tạo xong một ADV từ đầu đến cuối, không cần hỗ trợ
- [ ] BD dựng một demo từ đầu đến cuối, không cần hỗ trợ
- [ ] Không có lỗi kỹ thuật thô nào lọt lên màn hình

---

### CA-012 — Phân quyền theo ADV

**Vì sao cần.** Giao màn cấu hình cho BD và ops mà không mở cho họ quyền quản trị toàn hệ thống.

**Yêu cầu**

- Vai trò riêng cho người làm cấu hình, tách khỏi vai trò quản trị cao nhất
- Người làm cấu hình của một ADV chỉ đọc và sửa được ADV đó
- Vai trò này **không** tạo, xoá hay đổi trạng thái hoạt động của ADV nào
- Không đổi hành vi của bất kỳ quyền nào đang chạy

**Nghiệm thu**

- [ ] Người làm cấu hình của một ADV không truy cập được ADV khác
- [ ] Vai trò này không tạo hay xoá được ADV
- [ ] Các vai trò hiện có giữ nguyên quyền như trước

---

## 5. Yêu cầu phi chức năng

**NFR-001 — Không phát hành để đổi cấu hình.** Mọi giá trị trong bộ cấu hình phải đổi được và có hiệu lực
mà không cần phát hành phần mềm.

**NFR-002 — Không làm hỏng cái đang chạy.** 14 website hiện có không thay đổi hành vi. Người dùng cuối
không mất phiên đăng nhập, không đứt liên kết.

**NFR-003 — Chịu lỗi.** Cấu hình lỗi hoặc chậm thì dùng bản gần nhất còn dùng được. Không bao giờ trả trang trắng.

**NFR-004 — Chất lượng hiển thị.** Vỡ bố cục, tràn chữ, sai lệch trên điện thoại là lỗi chặn nghiệm thu.
Mỗi màn kiểm trên cả máy tính và điện thoại, với ít nhất hai bộ nhận diện tương phản nhau.

**NFR-005 — Ngôn ngữ.** Toàn bộ giao diện và thông báo bằng tiếng Việt.

**NFR-006 — Một bản giao diện dùng chung.** ADV không được yêu cầu thay đổi ngoài các trường đã có trong bộ
cấu hình. Một yêu cầu riêng chỉ có hai đường: trở thành cấu hình cho mọi ADV, hoặc bị từ chối. Không có
đường tách bản riêng. Điều này cần một dòng tương ứng trong hợp đồng vận hành.

**NFR-007 — Không cho thương hiệu quay lại nằm trong mã nguồn.** Phải có kiểm tra tự động chặn việc gán
cứng màu, đường link, số điện thoại, địa chỉ thư hay tên ADV vào mã nguồn. Vi phạm thì không cho phát hành.

**NFR-008 — Bán kính ảnh hưởng.** Một sự cố tác động mọi ADV trên cùng bản chạy. Mọi bản ghi nhật ký phải
gắn tên ADV và domain ngay từ đầu, nếu không thì không lần được sự cố thuộc về ADV nào.

---

## 6. Phụ thuộc và giả định

1. `creator-app` dựng trên `fecredit` sau khi bóc sạch lớp thương hiệu FE Credit. Việc bóc phải xong trước
   khi thêm bất kỳ tính năng nào
2. Ops nhận việc cấu hình, BD nhận việc dựng demo — cần xác nhận với hai bộ phận trước khi thiết kế màn
3. ADV chấp nhận bộ bố cục dùng chung. Nếu ADV đòi bố cục riêng thì designer quay lại đường đi và CA-008
   không đạt mục tiêu
4. Backend giữ nguyên nền tảng và luật nghiệp vụ; chỉ bổ sung phần lưu và đọc cấu hình
5. Mỗi domain mới vẫn cần thao tác thủ công ngoài hệ thống: trỏ tên miền, chứng chỉ bảo mật, và đăng ký
   địa chỉ trả về cho hai nhà cung cấp đăng nhập
6. Số ADV trên `creator-app` trong năm đầu ở mức dưới hai chục

---

## 7. Nghiệm thu dự án

Trước khi đụng production, ops phải **đi trọn một lần setup ADV mới trên sandbox** mà không cần hỗ trợ.
Chưa qua được mốc này thì chưa đưa ADV thật lên.

Dự án coi là xong khi **một ADV thật lên sóng trên `creator-app`** với:

- Không ai tạo thư mục mã nguồn mới
- Không lần phát hành phần mềm nào phục vụ riêng ADV đó
- BD đã dùng demo trong quá trình chào khách
- Ops tự hoàn tất phần cấu hình
- ADV chạy hết một chu kỳ chiến dịch không có sự cố liên quan tới nền cấu hình
