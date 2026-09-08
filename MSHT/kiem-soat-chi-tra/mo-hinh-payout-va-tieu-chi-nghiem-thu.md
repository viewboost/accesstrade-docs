# Mô hình khoản chi và tiêu chí nghiệm thu

> **Mục đích:** chốt mô hình khái niệm **trước khi** đội bắt tay thiết kế dữ liệu, và biến từng mức
> ưu tiên thành **tiêu chí kiểm được**, không phải mô tả.
> **Ngày:** 2026-09-08 · **Trạng thái:** chờ chốt mục 1 trước khi thiết kế bảng.
>
> Đi kèm: [`phan-tich-va-giai-phap.md`](./phan-tich-va-giai-phap.md) ·
> [`cong-cu-cho-van-hanh-chi-tra.md`](./cong-cu-cho-van-hanh-chi-tra.md) ·
> [`van-de-can-at-core-ho-tro.md`](./van-de-can-at-core-ho-tro.md)

---

## 1. Mô hình khái niệm

### Nguyên tắc chi phối

> **Đợt là đơn vị THỰC THI. Khoản chi là đơn vị TIỀN.**
> Trộn hai thứ là dựng lại đúng con lỗi đang chữa, chỉ khác là bằng một mô hình đẹp hơn.

> Khoá chống trùng phía đối tác là **`txn_id`** — đặc tả quy định *"`txn_id` phải duy nhất theo
> partner"* và trả `400` khi trùng. `request_id` chỉ là mã lần gọi của gateway. Xem
> [`at-core-partner-bank-gateway-api.md`](./at-core-partner-bank-gateway-api.md) mục B.1.

```
Nghĩa vụ với khách
        │  (một nghĩa vụ → tối đa MỘT khoản chi đang hoạt động)
        ▼
   Khoản chi ◄──────────── txn_id gửi AT-Core nằm ở ĐÂY
        │                   ổn định suốt đời, không đổi khi dời đợt,
        │                   không đổi khi gửi lại
        ├── Lần gửi #1 ──► Giao dịch AT-Core ──► Giao dịch ngân hàng
        ├── Lần gửi #2 ──► (nếu lần #1 hỏng, đã xác nhận)
        └── ...

   Đợt ──chứa nhiều──► Khoản chi
        (khoản chi dời được sang đợt khác — danh tính KHÔNG đổi)
```

### Bốn thực thể

| Thực thể | Là gì | Danh tính đổi khi nào | Ai sở hữu |
| --- | --- | --- | --- |
| **Nghĩa vụ** | "MSHT nợ khách khoản tiền này" | Không bao giờ | Nghiệp vụ hoàn tiền |
| **Khoản chi** | Một lần trả cho một nghĩa vụ | **Không bao giờ** | Tài chính |
| **Lần gửi** | Một lượt thử thực thi khoản chi | Mỗi lần gửi lại | Kỹ thuật |
| **Đợt** | Tập khoản chi gom lại chạy cùng nhau | — | Vận hành |

### Kênh chi thuộc về KHOẢN CHI, không phải ngoại lệ

Chi tay **không phải đường lui, mà là một kênh chính thức**. Nếu coi nó là ngoại lệ thì nó sẽ không
có vòng đời, không có đối soát, và trở thành một hệ thống nằm ngoài hệ thống.

```
Khoản chi
 ├── kênh = AT_CORE
 └── kênh = CHI_TAY
```

**Cả hai kênh đi qua đúng một vòng đời:**

```
Tạo → Duyệt → Thực thi → Ghi nhận bằng chứng → Đối soát → Đóng
```

Khác nhau duy nhất là **đối soát ở lớp nào**:

| Kênh | Đối soát lớp 2 (AT-Core) | Đối soát lớp 3 (ngân hàng) |
| --- | --- | --- |
| `AT_CORE` | ✅ phải khớp | ✅ |
| `CHI_TAY` | ❌ **loại ra** — sổ AT-Core không bao giờ có | ✅ **nguồn sự thật duy nhất** |

> Không có trường kênh thì khoản chi tay bị báo lệch vĩnh viễn ở lớp 2, và không ai nhận nó ở lớp 3.

### Bất biến — những điều không bao giờ được sai

Đây là danh sách để đội kiểm thử viết ca, và để người thiết kế bảng dữ liệu ràng buộc.

| # | Bất biến |
| --- | --- |
| **BB-1** | Một nghĩa vụ có **tối đa một** khoản chi đang hoạt động |
| **BB-2** | **`txn_id`** gửi AT-Core = mã khoản chi. **Không** sinh từ lần gửi, **không** sinh từ đợt |
| **BB-3** | Một khoản chi có **đúng một** kết cục tài chính cuối cùng — không bao giờ vừa thành công vừa bị hoàn |
| **BB-4** | Dời khoản chi sang đợt khác **không đổi** danh tính và không đổi `txn_id` |
| **BB-5** | Khoản chi ở trạng thái **chưa rõ kết quả** không gửi lại được, không hoàn tiền được, không dời đợt được |
| **BB-6** | Trạng thái chỉ đi tới, không lùi. Mọi cập nhật đều kèm **điều kiện trạng thái hiện tại** |
| **BB-7** | Mọi thao tác **loại A** (khẳng định về tiền) đều có bằng chứng và bản ghi audit |
| **BB-8** | Đợt không đóng được khi số khoản chưa rõ vượt ngưỡng **D4** |
| **BB-9** | Kênh chi thuộc khoản chi và **không đổi** sau khi đã thực thi |
| **BB-10** | Mã khoản chi mang **tiền tố định danh sản phẩm** — không đụng sản phẩm khác dùng chung AT-Core |
| **BB-11** | **Không được chi tay cho một nghĩa vụ đang có khoản chi AT-Core ở trạng thái chưa rõ.** Chi tay chỉ mở khi khoản AT-Core đã ở trạng thái kết thúc **đã xác nhận** |
| **BB-12** | Trạng thái khách nhìn thấy **không bao giờ là "thất bại"** khi trạng thái nội bộ là "chưa rõ kết quả" |

> **BB-11 bịt lỗ chi trùng qua hai kênh.** Nếu thiếu, kịch bản sau xảy ra được: khoản AT-Core đang
> chưa rõ → vận hành chi tay cho khách → sau đó AT-Core báo thành công ⇒ **khách nhận hai lần**.
> Đây là ca kiểm thử bắt buộc, không phải tình huống lý thuyết — nó chính là hình dạng của sự cố
> vừa rồi, chỉ khác là đi qua hai kênh thay vì hai lần gửi.
>
> **BB-12 là cam kết với khách, không phải lỗi hiển thị.** Nội bộ có thể không biết; nhưng nói với
> khách rằng "thất bại" trong khi tiền có thể đã chuyển là một phát biểu sai về tiền của họ.
> Trạng thái khách thấy khi nội bộ chưa rõ: *"Đang xử lý — đang xác minh với ngân hàng."*

---

## 1B. Đường xử lý khoản "chưa rõ kết quả"

**D1** *(coi như đã chi)* là **chính sách rủi ro**, không phải quy trình. Vận hành không thao tác được
với một chính sách. Nó phải thành đường đi có mốc thời gian:

```
Khoản chi ở trạng thái CHƯA RÕ KẾT QUẢ
        │
        ├─ Tra AT-Core được không?
        │     ├─ ĐƯỢC, có câu trả lời dứt khoát  ──►  chốt theo câu trả lời đó
        │     └─ ĐƯỢC, vẫn "đang xử lý"          ──►  đi tiếp xuống dưới
        │     └─ KHÔNG tra được (đối tác lỗi)    ──►  đi tiếp, ghi nhận lý do
        │
        ├─ Dưới ngưỡng D2 (đề xuất 24h)   ──►  CHỜ. Tự tra lại theo nhịp.
        │                                       Khách thấy "đang xử lý".
        │
        ├─ Quá D2 (24h)                   ──►  Cảnh báo vận hành. Vào danh sách
        │                                       quá hạn. Vận hành tra tay.
        │
        ├─ Quá ngưỡng leo thang (72h)     ──►  Leo thang: mở phiếu với AT-Core,
        │                                       báo khách chủ động, tạm gác để
        │                                       gỡ khách khỏi bị chặn.
        │
        └─ AT-Core không bao giờ trả lời  ──►  KHÔNG tự chuyển thành công hay
                                                thất bại. Chỉ đóng bằng đối soát
                                                lớp 2 hoặc lớp 3. Nếu cả hai đều
                                                không kết luận được ⇒ đây là ca
                                                cần founder quyết từng trường hợp.
```

**Ba điều đường này bảo đảm:**

- Khoản chưa rõ **không bao giờ** tự động thành "thất bại" rồi hoàn tiền *(BB-5)*.
- Khách **không bị kẹt im lặng** — quá 72h là có người chủ động liên hệ, và khoản được tạm gác nên
  họ không bị chặn nhận tiền hoàn kỳ sau.
- Nhánh cuối cùng — không ai kết luận được — là **ca hiếm nhưng phải có tên**, thay vì để nó rơi vào
  khoảng trống rồi ai đó tự quyết.

> Ngưỡng 24h/72h là **đề xuất**, chờ chốt ở **D2**. Đường đi thì không đổi theo con số.

---

## 2. Tiêu chí nghiệm thu theo từng mức ưu tiên

Mỗi dòng phải **kiểm được bằng một phép thử**, không phải bằng ý kiến.

### Ưu tiên 0 — Chặn máu

- [ ] Gọi `PUT /api/withdraw/migration/withdraw/:id/approve` trả về 404.
- [ ] Gọi đường kích hoạt chi theo danh sách user trên môi trường thật trả về 404.
- [ ] Tạo khoản chi mới cho khách đang còn khoản treo → bị từ chối, kèm lý do đọc được.
- [ ] Vận hành có truy vấn lưu sẵn: danh sách khoản treo quá 24h kèm mã tra cứu.
- [ ] Có văn bản một trang: khi nào được bấm đổi trạng thái tay, khi nào cấm, ai duyệt.
- [ ] Có kịch bản trả lời khách cho ca "tiền chưa về".

### Ưu tiên 1 — Danh tính và đợt

- [ ] Một nghĩa vụ **không tạo được** hai khoản chi đang hoạt động *(BB-1)*.
- [ ] Gửi lại một khoản chi **không sinh** `txn_id` mới *(BB-2)*.
- [ ] Dời khoản chi sang đợt khác → `txn_id` **không đổi** *(BB-4)*.
- [ ] 🔴 **Gửi lại đúng `txn_id` cũ → AT-Core trả `400 txn_id trùng` → hệ thống gọi `txn-inquiry`
      để lấy kết quả giao dịch gốc**, KHÔNG coi `400` là thất bại rồi hoàn tiền.
      *(AT-Core từ chối trùng chứ không trả lại kết quả cũ — xem tài liệu API mục B.1.)*
- [ ] Mọi khoản chi thuộc đúng một đợt; truy được "đợt N gồm những khoản nào".
- [ ] Truy được "khoản X thuộc đợt nào, đã gửi mấy lần, mỗi lần nhận gì".
- [ ] Đợt có: mã, loại *(tự động / bù tay / theo danh sách)*, phạm vi, người tạo, thời điểm, trạng thái vòng đời.
- [ ] Mã khoản chi có tiền tố định danh sản phẩm *(BB-10)*.
- [ ] Đợt tự động và đợt bù tay **phân biệt được trong dữ liệu**, không chỉ khác thời điểm tạo.

### Ưu tiên 2 — Đôi mắt cho vận hành

- [ ] Vận hành tra được AT-Core từ giao diện, **không cần kỹ sư**.
- [ ] Kết quả tra hiện đủ: trạng thái, **số tiền**, mã tham chiếu.
- [ ] Số tiền AT-Core trả về được so với số đã yêu cầu; lệch thì báo, không âm thầm bỏ qua.
- [ ] Trạng thái **"chưa rõ kết quả"** tồn tại và tách khỏi "chưa gửi".
- [ ] Khoản chưa rõ: hệ thống **tự chặn** gửi lại, hoàn tiền, dời đợt *(BB-5)* — không dựa vào người dùng nhớ.
- [ ] Đổi trạng thái tay chỉ chọn được đúng giá trị AT-Core vừa trả về.
- [ ] Ghi đè ngược trạng thái bị chặn *(BB-6)* — có ca kiểm thử cho tình huống callback về giữa lúc đang xử lý.
- [ ] Thao tác **tạm gác** gỡ khách khỏi tình trạng bị chặn tạo khoản mới.
- [ ] Thông báo gửi khách đúng với trạng thái thật; khoản chi qua mọi kênh đều có thông báo.
- [ ] **Trạng thái khách nhìn thấy tách khỏi trạng thái nội bộ** *(BB-12)*. Nội bộ "chưa rõ kết quả"
      → khách thấy *"Đang xử lý — đang xác minh với ngân hàng"*, **không bao giờ thấy "thất bại"**.
- [ ] Có bảng ánh xạ trạng thái nội bộ → trạng thái khách thấy, và bảng đó được duyệt như một
      cam kết với khách, không phải chuỗi hiển thị.

### Ưu tiên 3 — Cổng chốt sổ

- [ ] Đợt có trạng thái chốt sổ, đọc được từ giao diện.
- [ ] Đợt mới **không tự chạy** khi cổng đỏ.
- [ ] Cổng đỏ **nêu được lý do** cụ thể, không chỉ báo đỏ.
- [ ] Có đường mở cổng bằng tay; mở cổng bắt buộc **duyệt + lý do + audit + cảnh báo**.
- [ ] Cổng phân biệt lỗi lẻ với lỗi hệ thống theo ngưỡng **D4**.
- [ ] Đối soát lớp 1 chạy hằng ngày, ra được **số tiền lệch** cụ thể.
- [ ] Đèn báo khói chạy hằng ngày và có người nhận kết quả.
- [ ] Giới hạn kích thước đợt điều chỉnh được mà không cần đổi mã.
- [ ] **Công tắc dừng toàn hệ** tồn tại và có hai mức: *dừng một đợt* và *dừng mọi đường chi tự động*.
- [ ] Bật công tắc mức hai → **mọi cửa chi tiền đều dừng**, không còn đường nào chạy được.
      *(Có 4 cửa — dừng một đợt mà cửa khác vẫn chi thì không phải kiểm soát toàn hệ.)*
- [ ] Bật/tắt công tắc không cần triển khai lại mã, và mỗi lần bật đều sinh cảnh báo + audit.

### Ưu tiên 4 — Kênh chi tay

- [ ] Khoản chi có trường **kênh**, hai giá trị *(BB-9)*.
- [ ] Khoản chi tay đi qua **đúng vòng đời** như khoản AT-Core: tạo → duyệt → thực thi → bằng chứng → đối soát → đóng.
- [ ] Khoản chi tay bắt buộc có **bằng chứng ngoài** (mã giao dịch ngân hàng) mới đóng được.
- [ ] Đối soát lớp 2 **loại** khoản chi tay ra; đối soát lớp 3 **nhận** vào.
- [ ] Nộp lại cùng file kết quả lần thứ hai **không đổi gì** và báo rõ dòng nào đã xử lý.
- [ ] Bật/tắt chế độ chi tay không cần triển khai lại mã.
- [ ] Job đối soát tự động **loại trừ tường minh** khoản chi tay — không dựa vào việc job đang tắt.
- [ ] 🔴 **Ca kiểm thử bắt buộc cho BB-11:** nghĩa vụ đang có khoản AT-Core ở trạng thái *chưa rõ*
      → thử tạo khoản chi tay cho cùng nghĩa vụ đó → **hệ thống từ chối**, nêu lý do.
- [ ] 🔴 **Ca kiểm thử ngược:** chi tay xong, sau đó AT-Core báo khoản cũ thành công → hệ thống
      **báo động chi trùng**, không âm thầm ghi nhận cả hai.

### Ưu tiên 5 — Phân quyền và dấu vết

- [ ] Người duyệt khác người tạo — **hệ thống tự chặn**, không dựa vào quy trình giấy.
- [ ] Có đường dự phòng khi thiếu người duyệt, và đường đó được ghi lại.
- [ ] **100%** thao tác loại A có bản ghi audit *(BB-7)*.
- [ ] Bản ghi audit trả lời được: ai · lúc nào · đối tượng nào · từ trạng thái gì sang gì · **dựa trên bằng chứng nào**.
- [ ] Phép đo ngược chạy được: liệt kê được mọi khoản chi đổi trạng thái **mà không có** audit của người vận hành đứng sau.
- [ ] Kết quả phép đo đó hiển thị được theo tuần.

### Ưu tiên 6 — Đối soát lớp 2

- [ ] Lấy được kết quả AT-Core theo khoảng thời gian do mình chỉ định.
- [ ] Đối soát lớp 2 ra bảng lệch **có phân loại**, không phải danh sách phẳng.
- [ ] Phát hiện được hai giao dịch cùng `request_id` ở phía AT-Core.
- [ ] Có nút "chấp nhận lệch có lý do" kèm audit.
- [ ] Đợt **không chốt được** khi lệch vượt ngưỡng *(BB-8)*.
- [ ] Số tiền chưa đối soát hiển thị được theo ngày và theo tuổi.

---

## 3. Năm số cho bảng điều khiển của founder

Không phải bộ thước đo đầy đủ — đây là năm số **founder nhìn để biết hệ có an toàn hơn thật không**.

| Nhóm | Số | Đích |
| --- | --- | --- |
| An toàn tài chính | **Số khoản chi trùng đã xác nhận** *(xem định nghĩa dưới)* | **0** |
| Độc lập vận hành | % ca xử lý xong không cần kỹ sư | tăng → 95% |
| Đối soát | Số tiền chưa đối soát | → 0 |
| Khách hàng | % khoản chi trong SLA · tuổi khoản treo lâu nhất | trong ngưỡng **D2** |
| Quản trị | % thao tác tiền có bằng chứng + audit đầy đủ | **100%** |

> Bộ thước đo đầy đủ 14 chỉ số nằm ở mục 5 của
> [`phan-tich-va-giai-phap.md`](./phan-tich-va-giai-phap.md). Năm số này là lát cắt để báo cáo,
> không thay thế bộ kia.

### "Chi trùng" phải tách làm hai số

Gộp một số là cách nhanh nhất để bảng điều khiển nói dối.

| | **Số nghi ngờ** *(phát hiện)* | **Số đã xác nhận** *(sự thật tài chính)* |
| --- | --- | --- |
| Định nghĩa | Cùng người, cùng số tiền, hai khoản thành công cách nhau < 48h | **Một nghĩa vụ** có **từ hai kết cục chi thành công trở lên** — xác nhận bằng sổ AT-Core hoặc sao kê ngân hàng |
| Nguồn | Truy vấn nội bộ *(đèn báo khói)* | Đối soát lớp 2 hoặc lớp 3 |
| Có ngay không | Có, từ tuần đầu | Chỉ có sau UT6 hoặc qua đối soát ngân hàng |
| Dùng để | Báo động, đi tra | **Báo cáo, đo đích = 0** |
| Sai số | Có dương tính giả *(một người rút hai lần hợp lệ)* | Không |

Đích **= 0** áp cho cột phải. Cột trái là công cụ săn, không phải con số báo cáo — nếu lẫn hai cột,
một tháng có ba ca dương tính giả sẽ bị đọc thành "mất tiền ba lần".
