# **PLAYBOOK — Onboard đối tác lên Landing page**

*Playbook vận hành: mô tả toàn bộ quy trình từ lúc nhận yêu cầu đến khi landing của đối tác sẵn sàng chạy thật (go-live). Dùng cho đội Sale, Admin vận hành và QA.*

**Mục lục:**

1. Khi nào chạy Playbook này (Trigger)  
2. Vai trò & trách nhiệm (RACI)  
3. Đầu vào cần chuẩn bị  
4. Quy trình onboard (từng bước, có điều kiện)  
5. Xử lý sự cố (Troubleshooting)  
6. Định nghĩa Hoàn thành (Definition of Done)  
7. Phụ lục tham chiếu — Giải thích kỹ Slug & Allow domains

## **1\. Khi nào chạy Playbook này (Trigger)**

Bắt đầu chạy playbook khi **một trong các sự kiện** sau xảy ra:

* Sale đã **chốt hợp đồng / thỏa thuận** với đối tác mới và cần lên landing chương trình.  
* Đối tác đã **cung cấp domain** sẽ dùng để chạy landing (domain trỏ về).  
* Đối tác hiện hữu **mở chiến dịch mới** cần cấu hình lại thông tin/ngân sách.

Nếu **chưa có domain thật** của đối tác → vẫn chạy được playbook ở chế độ "demo trước" (xem Bước 4 — nhánh điều kiện).

## **2\. Vai trò & trách nhiệm (RACI)**

| Bước | SALE | ADMIN | QA | ĐỐI TÁC |
| :---- | :---- | :---- | :---- | :---- |
| Thu thập thông tin, domain, logo, cover | R (chịu trách nhiệm) | C (tư vấn) | \- | R (cung cấp) |
| Setup đối tác trên hệ thống | C | R | \- | \- |
| Cấu hình Slug & Allow domains | \- | R | \- | C (xác nhận domain) |
| Kiểm thử landing (test) | \- | C | R | \- |
| Bàn giao / Go-live | R | C | A | A (nghiệm thu) |

*R \= Responsible (người làm) · A \= Accountable (người duyệt/chịu trách nhiệm cuối) · C \= Consulted (tư vấn) · I \= Informed (được thông báo)*

## **3\. Đầu vào cần chuẩn bị (trước khi setup)**

Admin chỉ bắt đầu setup khi Sale/đối tác đã cung cấp đủ:

| Hạng mục | Yêu cầu | Bắt buộc? |
| :---- | :---- | :---- |
| Tên đối tác | Tên hiển thị (VD: Parasola) | ✅ |
| **Domain trỏ về** | Domain đối tác dùng chạy landing (VD: parasola.demo.accesstrade.click) — **không kèm https://** | ✅ |
| Logo | File PNG nền trong suốt, tỷ lệ vuông | ✅ |
| Cover (Tiêu chuẩn \+ Stretch) | Banner đúng tỷ lệ | ✅ |
| Mô tả chương trình | Tên chiến dịch, thời gian, đối tượng, điểm nổi bật | ✅ |
| Ngân sách / ADV | Tổng ngân sách (VND) | ✅ |
| Website đối tác | Link ra ngoài (VD: https://naris.vn/) | ◻ Nên có |
| Yêu cầu cấu hình | Có hiển thị BXH không? Hiện số tiền không? Cho gửi lại bài bị từ chối không? | ◻ Theo thỏa thuận |

**Nguyên tắc:** Thiếu **Domain trỏ về** hoặc **Tên** thì KHÔNG setup production. Dừng lại và yêu cầu Sale bổ sung.

## **4\. Quy trình onboard — từng bước**

**GIAI ĐOẠN A — SETUP ADMIN**

### **1 Tạo mới / Mở form Cập nhật đối tác**

Vào trang quản trị → tạo đối tác mới (hoặc mở đối tác có sẵn để cập nhật). Form "Cập nhật" hiện ra.

### **2 Điền thông tin nhận diện**

* **Logo**: upload logo đối tác.  
* **Cover**: upload bản *Tiêu chuẩn* và *Stretch* (bấm \+ Thêm nếu nhiều cover).  
* **Tên**: nhập tên hiển thị (có dấu, viết hoa bình thường).

### **3 Cấu hình Slug — ⚠️ điểm dễ sai**

* Nhập slug theo chuẩn: **chữ thường, không dấu, không khoảng trắng**, nối từ bằng gạch ngang. VD: parasola.  
* **Kiểm tra không trùng** với đối tác khác.

**ĐIỀU KIỆN:** Slug đã công bố thì **KHÔNG đổi**. Nếu buộc phải đổi → coi như tạo đường dẫn mới, phải báo Sale để đối tác phát lại link (link cũ sẽ 404). → Chi tiết ở Phụ lục.

### **4 Cấu hình Allow domains — ⚠️ điểm dễ sai nhất**

* Nhập **domain trỏ về** của đối tác, mỗi domain Enter một lần thành 1 thẻ.  
* **TUYỆT ĐỐI không nhập https:// / http://, không dấu / cuối.**

**NHÁNH ĐIỀU KIỆN:**

* **Nếu đã có domain thật** → nhập đúng domain đó (VD parasola.demo.accesstrade.click).  
* **Nếu chưa có domain thật (demo trước)** → dùng domain demo/localhost để test (VD localhost:3000, localhost:8000), **ghi note "chờ domain thật"** và báo Sale. Khi có domain thật phải quay lại cập nhật.  
* **Khi lên production** → **xóa hết domain localhost/test**, chỉ giữ domain thật. (Đối chiếu: bản test nhiều domain → bản prod chỉ còn 1 domain.)

### **5 Điền thông tin nội dung & ngân sách**

* **Website**: link đối tác — **ô này ĐƯỢC có https://** (khác Allow domains).  
* **Mô tả**: dán nội dung chương trình.  
* **Ngân sách / ADV**: nhập số tiền (VND).

### **6 Bật/tắt cấu hình theo thỏa thuận**

| Cấu hình | Quy tắc quyết định |
| :---- | :---- |
| Hiển thị BXH | Bật nếu chương trình có bảng xếp hạng. Mặc định: Bật. |
| Hiển thị số tiền trong BXH | Bật/tắt theo yêu cầu bảo mật của đối tác. |
| Cho phép gửi lại nội dung bị từ chối | Bật nếu đối tác muốn user được sửa & nộp lại bài. Mặc định: Tắt. |

### **7 Lưu**

Bấm **Cập nhật**. Nếu sai → **Hủy bỏ** và làm lại. Sau khi lưu → chuyển QA.

**GIAI ĐOẠN B — KIỂM THỬ QA**

### **8 Test landing trên domain đã khai báo**

* Truy cập landing qua domain trong Allow domains → phải hiển thị đúng thiết kế.  
* Đối chiếu bộ test case chuẩn (giao diện chưa login, đăng nhập, trang chủ, chi tiết chương trình, đăng bài, thông báo...).  
* Nếu có bug → trả lại Admin (Giai đoạn A), ghi rõ lỗi.

**GIAI ĐOẠN C — GO-LIVE SALE / ĐỐI TÁC**

### **9 Bàn giao & nghiệm thu**

* QA xác nhận Pass toàn bộ → Sale bàn giao link landing cho đối tác.  
* Đối tác nghiệm thu trên domain thật.  
* Thông báo go-live cho các bên liên quan (Informed).

## **5\. Xử lý sự cố (Troubleshooting)**

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
| :---- | :---- | :---- |
| Landing **bị chặn / trắng trang / báo không được phép** trên domain đối tác | Domain chưa có trong Allow domains, hoặc nhập sai (thừa https://, thừa /, sai subdomain/cổng) | Mở lại Allow domains, nhập **đúng domain, không https://, không / cuối**. Kiểm tra từng ký tự. |
| Vào link đối tác ra **landing của đối tác khác** / 404 | Slug bị trùng hoặc slug đã bị đổi sau khi công bố | Kiểm tra slug duy nhất. Nếu đã đổi slug → khôi phục slug cũ hoặc phát lại link mới cho đối tác. |
| Link "Về Parasola by Naris" không mở được | Ô Website để trống hoặc nhập thiếu https:// | Nhập lại Website đầy đủ dạng https://naris.vn/. |
| BXH không hiển thị / lộ số tiền ngoài ý muốn | Cấu hình BXH bật/tắt sai | Chỉnh lại 2 toggle "Hiển thị BXH" và "Hiển thị số tiền trong BXH". |
| User không nộp lại được bài bị từ chối (hoặc ngược lại) | Toggle "Cho phép gửi lại nội dung bị từ chối" sai với thỏa thuận | Bật/tắt lại theo yêu cầu đối tác. |
| Font tiếng Việt / tên hiển thị lỗi | Ảnh/nội dung mô tả sai encoding hoặc dán từ nguồn lỗi | Nhập lại Mô tả, kiểm tra hiển thị. |

## **6\. Định nghĩa Hoàn thành (Definition of Done)**

Onboard chỉ được coi là **HOÀN TẤT** khi tất cả điều kiện sau đều đạt:

* ☑ Đối tác đã được tạo/cập nhật và **lưu thành công**.  
* ☑ **Slug** đúng chuẩn, duy nhất, đã chốt (không đổi về sau).  
* ☑ **Allow domains** chứa đúng domain thật của đối tác, **không có https://**, không dấu / cuối; đã dọn domain test.  
* ☑ Logo, Cover, Tên, Mô tả, Ngân sách, Website đã điền đầy đủ & đúng.  
* ☑ Các toggle BXH & nội dung đúng theo thỏa thuận.  
* ☑ **QA đã test Pass** landing trên domain thật (đối chiếu bộ test case).  
* ☑ Sale đã **bàn giao** và đối tác đã **nghiệm thu**.  
* ☑ Các bên liên quan đã được thông báo go-live.

---

## **7\. Phụ lục tham chiếu — Giải thích kỹ Slug & Allow domains**

*(Giữ nguyên phần giải thích chi tiết để tra cứu khi cần.)*

### **7.1 Slug là gì?**

Slug là phần **đường dẫn (URL) định danh** cho đối tác — "mã đường dẫn" duy nhất để hệ thống nhận ra đây là landing của đối tác nào.

Ví dụ slug \= parasola → hệ thống ánh xạ landing của đối tác này qua đường dẫn chứa parasola. Khi user truy cập, hệ thống dựa vào slug để load đúng cấu hình, logo, cover, chương trình.

| ✅ ĐÚNG | ❌ SAI |
| :---- | :---- |
| Chữ thường không dấu: parasola Số: parasola2026 Gạch ngang nối từ: parasola-summer | Có dấu: **pàrasola** Khoảng trắng: **para sola** Viết hoa: **Parasola** Ký tự đặc biệt: **para\_sola, parasola@\!** |

* **Slug phải DUY NHẤT** — trùng sẽ xung đột, load sai landing.  
* **KHÔNG đổi Slug sau khi onboard/công bố** — slug nằm trong URL, đổi là làm **hỏng toàn bộ link cũ (404)**.  
* Đặt ngắn gọn, dễ nhớ, gắn với tên thương hiệu.

### **7.2 Allow domains là gì?**

Là **danh sách domain được phép truy cập / được hệ thống tin tưởng** để phục vụ landing — chính là **(các) domain trỏ về** mà đối tác dùng cho người dùng vào xem chương trình.

👉 Domain trong ô này **chính là "domain trỏ về" ghi trong file thông tin đối tác**. Domain truy cập không nằm trong danh sách → hệ thống **chặn**, không hiển thị landing.

**Chỉ nhập phần TÊN MIỀN. KHÔNG https:// / http://, không dấu / cuối.**

| ✅ ĐÚNG | ❌ SAI |
| :---- | :---- |
| parasola.demo.accesstrade.click  | **https://parasola.demo.accesstrade.click http://ambassador.diso.vn parasola.demo.accesstrade.click/ www...** (thừa/thiếu prefix so với domain thật) |

**Phân biệt rõ:** **Allow domains** \= domain trỏ về → **KHÔNG https://**.   **Website** \= link ra ngoài → **CÓ https://** đầy đủ.

