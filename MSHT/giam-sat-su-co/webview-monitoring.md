# Webview Monitoring — tài liệu nghiệp vụ

**Đối tượng đọc**: nội bộ team web-webview và quản lý trực tiếp
**Cập nhật**: 2026-09-14 · **Trạng thái hệ thống**: đã hiện thực xong, **chưa bật trên production**

> Tài liệu này chỉ ghi **kết luận hiện hành**. Lịch sử tranh luận, các quyết định đã bị lật
> và vết review nằm ở `docs/business/webview-monitoring/` và `docs/features/` — xem §10.

> ---
>
> **Ghi chú khi đưa vào repo tài liệu** *(thêm bởi PM, không thuộc nội dung gốc)*:
> Đây là **cấu phần M4** của [Hệ giám sát và quản lý sự cố MSHT](./tai-lieu-du-an.md).
> Tài liệu do **đội web-webview soạn và sở hữu**; bản ở đây là bản sao để tiện đối chiếu.
> Các đường dẫn ở §10 trỏ vào **repo mã nguồn**, không phải repo này. Nhập ngày 2026-09-14.

---

## 1. Tóm tắt

Webview cashback nhúng trong app VPBank là **điểm chạm duy nhất** giữa sản phẩm hoàn tiền và
khách hàng của bank. Mỗi ngày có hàng chục nghìn lượt mở. Một phần trong số đó không bao giờ
vào được màn Home — kẹt ở loading hoặc rơi ra màn lỗi.

Trước khi có hệ này, team **không biết con số đó là bao nhiêu**, và khi có phàn nàn thì không
có cách nào tra ngược về phiên cụ thể của khách.

Hệ monitoring biến tình trạng đó thành: mỗi lượt mở webview là một **phiên có định danh**,
đo được đi tới bước nào, mất bao lâu, hỏng ở đâu, và tra cứu lại được trong 15 ngày.

---

## 2. Vấn đề

### 2.1. Ba việc không làm được

| Không làm được | Hệ quả thực tế |
|---|---|
| **Không đếm được** có bao nhiêu phiên hỏng mỗi ngày | Không biết vấn đề lớn cỡ nào, nên không biết có đáng đầu tư sửa không. Mọi tranh luận về chất lượng đều là cảm tính |
| **Không biết kẹt ở bước nào** | Chuỗi khởi tạo có 6 bước nối tiếp (đổi token → các lệnh gọi cấu hình → render Home). Telemetry cũ chỉ phủ bước đổi token; các bước sau **nuốt lỗi hoàn toàn**. Loading gate không phân biệt được "đang chậm" với "đã chết" |
| **Không tra được phiên cụ thể** | Khi có phàn nàn, không nối được từ lời kể của khách về một bản ghi nào. Chỉ còn cách suy đoán, hoặc trả lời "anh/chị thử lại sau ạ" |

### 2.2. Vì sao đây là vấn đề đáng tiền

Với lượng truy cập hàng chục nghìn phiên/ngày, **một tỉ lệ hỏng rất nhỏ vẫn là hàng chục tới
hàng trăm khách hàng bank mỗi ngày không dùng được sản phẩm**. Đây là khách của đối tác, mở
tính năng từ trong app của họ — trải nghiệm hỏng ảnh hưởng trực tiếp tới quan hệ hợp tác.

Điểm đau riêng của bối cảnh này: khách hàng cuối **hầu như không phàn nàn**. Không có màn
đăng nhập nên không có cách "thử lại bằng cách login lại"; họ bỏ luôn ý định mua và đi ra.
Im lặng không có nghĩa là không có lỗi — nó chỉ có nghĩa là ta không nhìn thấy.

---

## 3. Hệ này giải quyết được gì

Bảng dưới là ruột của tài liệu: **câu hỏi nghiệp vụ** → hệ trả lời được tới đâu.

### 3.1. Trả lời được đầy đủ

| Câu hỏi | Hệ trả lời bằng |
|---|---|
| Hôm nay có bao nhiêu lượt mở webview? | Mỗi lượt mở sinh một phiên có định danh, kể cả phiên thất bại. Đây là **mẫu số** cho mọi tỉ lệ khác — thứ trước đây không tồn tại |
| Bao nhiêu phần trăm vào được Home dưới 10s? | Chỉ số chính. Phiên chỉ tính là đạt khi Home **render xong và tải đủ dữ liệu** — không tính trường hợp khung Home hiện ra nhưng rỗng |
| Phiên hỏng thì kẹt ở bước nào? | Từng bước trong chuỗi khởi tạo có mốc thời gian và trạng thái riêng. Phân loại được: hỏng ở đổi token / lệnh gọi cấu hình / render / lỗi JS / mạng |
| Một phiên cụ thể đã xảy ra chuyện gì? | Dòng thời gian đầy đủ của phiên: các bước, các lệnh gọi mạng, thời điểm, kết quả |
| Lỗi gì đang xảy ra, ở đâu? | Loại lỗi, endpoint hỏng, mã trạng thái, vị trí trong mã nguồn. Kể cả lỗi trước đây bị nuốt ở tầng model/service |
| Bản phát hành nào đang chạy ở phiên đó? | Mỗi phiên gắn mã phiên bản thật của bản build |
| Phiên nào chạy trong trạng thái suy giảm? | Phiên vào được Home nhưng thiếu dữ liệu được đánh dấu riêng, không trộn vào nhóm "thành công" |

### 3.2. Trả lời được một phần — phải đọc kèm giới hạn

| Câu hỏi | Trả lời được tới đâu |
|---|---|
| **Bao nhiêu phần trăm lượt mở lọt khỏi tầm quan sát?** | Đo được tỉ lệ phiên ghi nhận được so với số lượt đổi partner token phía backend. **Nhưng**: phiên chết trước khi tải/chạy được mã web (mất mạng, DNS hỏng, WebView chặn) nằm ngoài **cả tử số lẫn mẫu số** ⇒ con số này **luôn cao hơn thực tế**. Nó trả lời "trong số phiên đã chạy được tới mức gọi dịch vụ, bao nhiêu được ghi nhận", **không** trả lời "bao nhiêu người mở webview được nhìn thấy" |
| Nguyên nhân hỏng có nằm trong tầm sửa không? | Phân loại được nguyên nhân, nhưng nhiều nhóm (mạng của khách, cấu hình WebView của app bank, thiết bị cũ) chỉ **nhận diện được**, không sửa được từ phía ta |

### 3.3. Chưa trả lời được

- **Tra cứu tự phục vụ cho CSKH bank** — chưa có công cụ, và quan trọng hơn: **chưa có kênh
  chuyển ticket chính thức** với CSKH bank. Dựng công cụ mà không có kênh thì không ai gửi ca vào.
- **Cảnh báo tự động khi chất lượng tụt** — cần chốt ngưỡng từ dữ liệu thật trước, chưa có dữ liệu thật.
- **Sổ known-issues và kịch bản trả lời khách** — phụ thuộc kênh CSKH ở trên.

---

## 4. Ai được lợi, lợi ra sao

| Vai | Hôm nay | Có hệ này thì |
|---|---|---|
| **Dev / Tech lead web-webview** — người duy nhất thực sự dùng hệ ở giai đoạn hiện tại | Mò trong bóng tối. Không biết mỗi ngày bao nhiêu khách không vào được | Xác định nguyên nhân **bằng bằng chứng thay vì suy đoán**; biết vấn đề lớn cỡ nào trước khi quyết định đầu tư sửa |
| **Quản lý sản phẩm / trực tiếp** | Không có số nào để đưa vào quyết định | Có một con số duy nhất theo dõi được theo tuần: tỉ lệ phiên vào Home dưới 10s |
| **CSKH của VPBank** | Hoàn toàn mù thông tin, chỉ escalate rồi chờ | **Chưa được lợi gì ở giai đoạn này.** Chân dung của vai này là suy luận, chưa từng được kiểm chứng bằng trao đổi thật. Đây là đối tượng của giai đoạn sau |
| **Khách hàng cuối** | Loading quay mãi hoặc màn lỗi khó hiểu | **Không thay đổi gì trực tiếp.** Hệ này chỉ đo. Lợi ích tới với họ gián tiếp, qua việc team sửa được nguyên nhân |
| **Phía VPBank (đối tác)** | — | Có bằng chứng định lượng khi nguyên nhân nằm ở phía họ. **Không** dùng làm số liệu SLA — xem §5 |

> **Một sự thật phải ghi rõ**: ở giai đoạn hiện tại, hệ có **đúng một người dùng thật** là
> team dev, và người đó kiêm luôn cả vai vận hành. Không có đội ops riêng, và **không có kế
> hoạch có**. Mọi thiết kế về sau (nhất là cảnh báo) phải theo ràng buộc đó: ít cảnh báo,
> đủ ngữ cảnh để xử lý ngay, vì không có ai ngồi sàng báo động giả.

---

## 5. Cố tình không làm

Phần này quan trọng ngang phần mục tiêu. Mỗi mục dưới đây là **quyết định**, không phải việc chưa kịp làm.

| Không làm | Vì sao | Loại bỏ hay hoãn |
|---|---|---|
| **Ghi hình / tái hiện thao tác màn hình (session replay)** | Rủi ro bảo mật không chấp nhận được với ứng dụng ngân hàng, kể cả có che dữ liệu | **Loại vĩnh viễn** |
| **Đo hoặc chứng minh SLA hợp đồng** | SLA với VPBank là **99%/tháng đo trên uptime dịch vụ**, bằng nguồn độc lập. Số liệu phiên phía client không đo uptime. Đặt hai thứ cạnh nhau là sai về bản chất và tạo kỳ vọng sai | **Loại vĩnh viễn khỏi phạm vi feature.** Cấm trộn hai con số trong mọi báo cáo |
| **Sửa nguyên nhân gốc của việc chậm/hỏng** | Giai đoạn này là đo. Sửa là quyết định riêng, sau khi có số | Hoãn |
| **Đặt ngưỡng cam kết cho chất lượng phiên** | Đặt ngưỡng trước khi có dữ liệu gần như chắc chắn ra ngưỡng quá lỏng, và ngưỡng lỏng thì không bao giờ cảnh báo | Hoãn tới khi có baseline thật |
| **Cảnh báo tự động + quy trình trực sự cố** | Phụ thuộc ngưỡng ở trên | Hoãn |
| **Cải thiện màn hình lỗi cho khách hàng cuối** | Là thay đổi trải nghiệm, thuộc một feature riêng | Hoãn |
| **Hiển thị mã tra cứu phiên cho khách hàng cuối** | Trong giai đoạn này mã tra cứu **chỉ dùng nội bộ** | Hoãn |
| **Chủ động gửi danh sách sự cố sang phía bank** | Chưa có kênh làm việc chính thức; gửi bản nháp thiện chí cũng tạo kỳ vọng không đỡ được | Cấm trong giai đoạn hiện tại |

---

## 6. Ràng buộc nghiệp vụ bắt buộc

Đây là các ràng buộc **không được vi phạm để đổi lấy tiến độ**. Mỗi mục đều kiểm chứng được.

### 6.1. Bảo vệ credential của đối tác

Webview được mở bằng một credential do bank cấp, nằm ngay trên đường dẫn khởi tạo.

- Hệ giám sát **không được lưu credential dưới dạng đọc được**, theo nguyên tắc
  **mặc định-từ-chối**: chỉ những trường nằm trong danh sách trắng mới được gửi đi.
- Đường dẫn trước khi ghi nhận phải **cắt bỏ toàn bộ phần truy vấn** — credential nằm ở đó.
- **Màn hình lỗi không được phơi credential** cho khách hàng cuối dưới dạng đọc/sao chép được.
- Không thu thập bất kỳ dữ liệu nào cho phép suy ra **thông tin tài chính hoặc định danh
  nhạy cảm** của khách hàng bank (số dư, số tài khoản, số thẻ, giao dịch cụ thể).

### 6.2. Nơi dữ liệu được lưu

- Toàn bộ dữ liệu giám sát nằm trên **hạ tầng do team tự vận hành**. Điểm nhận dữ liệu đi
  thẳng về nội bộ — **không có bên thứ ba nào trên đường đi**.
- **Hạn lưu 15 ngày**, tự động xoá. Kể cả số tổng hợp cũng không được giữ trong kho quá hạn này.
- Mỗi **kỳ báo cáo tuần** phải chốt số tổng hợp và lưu ra ngoài kho giám sát trước khi dữ liệu
  gốc hết hạn. Quên một kỳ là mất vĩnh viễn.

### 6.3. Tính toàn vẹn của phép đo

- **Lỗi luôn được ghi 100%, không lấy mẫu.** Khi cần giảm tải thì giảm mức chi tiết, không
  giảm phạm vi phủ.
- **Khoảng trống dữ liệu không được đọc là "ổn".** Mọi báo cáo phải phân biệt được "không có
  lỗi" với "không thấy lỗi".
- **Số đo từ ca diễn tập không được trộn với số từ ca thật**, và không được trình bày cạnh
  nhau kiểu "trước và sau". Diễn tập đo năng lực công cụ trong tay người đã biết trước câu
  trả lời — nó không đo nỗi đau thật.

### 6.4. Kiểm soát mã bên thứ ba chạy trong webview

Trang webview chạy bên trong app ngân hàng, nơi credential nằm sẵn trên đường dẫn. Bất kỳ
mã lạ nào chạy được ở đó đều đọc được credential.

- Mọi mã bên thứ ba trên trang phải **truy được chủ sở hữu và được duyệt, hoặc bị gỡ**.
- Kiểm kê đã làm: 2 mã bên thứ ba — 1 đã gỡ, 1 được **giữ có chủ đích** vì chưa xác định
  được chủ sở hữu nhưng chưa đủ cơ sở gỡ. Đây là **rủi ro tồn đọng đã được chấp nhận**, có
  chủ và có thời hạn, không phải việc bị bỏ quên.

### 6.5. Chi phí hiệu năng của chính phép đo

Công cụ đo không được làm chậm chính thứ nó đo — đặc biệt trên thiết bị yếu và mạng 3G,
vốn đúng là nhóm đang gặp vấn đề. Việc gửi dữ liệu không được chặn luồng khởi tạo; khi
mất mạng thì xếp hàng gửi lại, không chờ và không làm hỏng phiên.

---

## 7. Quy trình đổi thế nào

### 7.1. Xử lý phàn nàn của khách

| | |
|---|---|
| **Trước** | Khách báo lỗi → CSKH không xác nhận được có phải lỗi hệ thống không → escalate sang team web → team suy đoán từ mô tả của khách. Không có giới hạn trên về thời gian, và thường kết thúc bằng "không tái hiện được" |
| **Sau** | ① Nhận ca kèm thời điểm và thông tin nhận dạng khách đọc được qua điện thoại → ② tra ra **đúng phiên** trong kho → ③ đọc dòng thời gian của phiên, xác định bước hỏng → ④ kết luận: lỗi phía web / phía bank / phía mạng khách → ⑤ ghi mốc thời gian xử lý |
| **Chưa nối được** | Bước ① — **chưa có kênh chuyển ticket chính thức với CSKH bank**. Quy trình đúng trên giấy, đã kiểm chứng bằng diễn tập tự tạo, nhưng **chưa có ca thật nào chảy vào** |

### 7.2. Phát hiện và xác nhận sự cố

| | |
|---|---|
| **Trước** | Chỉ biết có sự cố khi ticket từ bank chuyển sang — tức là đã trễ hàng giờ tới hàng ngày. Không phân biệt được sự cố diện rộng với ca lẻ |
| **Sau** | Theo dõi tỉ lệ phiên vào Home theo ngày → thấy tụt bất thường thì khoanh vùng bằng dữ liệu: tụt ở bước nào, bản phát hành nào, endpoint nào → xác nhận là sự cố diện rộng hay ca lẻ → xử lý |
| **Giới hạn hiện tại** | **Việc "nhìn" vẫn là thủ công.** Chưa có cảnh báo tự động, nên phát hiện sớm phụ thuộc vào việc có người mở dashboard ra xem |

### 7.3. Rà soát chất lượng định kỳ

| | |
|---|---|
| **Trước** | Không tồn tại — không có số để rà |
| **Sau** | Nhịp **tuần**: chốt tỉ lệ phiên vào Home, độ phủ phép đo, phân bố nguyên nhân hỏng → lưu số tổng hợp ra ngoài kho (trước khi dữ liệu gốc hết hạn 15 ngày) → chốt hành động cho tuần sau |
| **Rủi ro thật của bước này** | Đây là nhịp việc **dễ bị bỏ trước tiên khi có áp lực phát hành** — xem §9 |

### 7.4. Kiểm soát mã bên thứ ba

| | |
|---|---|
| **Trước** | Không ai rà. Mã bên thứ ba tích tụ trên trang gốc mà không có ai chịu trách nhiệm |
| **Sau** | Kiểm kê định kỳ toàn bộ mã bên thứ ba đang nạp → mỗi mục phải truy được chủ sở hữu → mục vô chủ thì gỡ, hoặc ghi thành rủi ro chấp nhận **có chủ và có thời hạn** |

---

## 8. Đo bằng gì

**Chỉ số chính**: **tỉ lệ phiên mở webview vào được màn Home dưới 10s** — và tải đủ dữ liệu
Home, không tính khung rỗng. Một con số duy nhất phản ánh cả trải nghiệm khách hàng cuối lẫn
sức khoẻ kỹ thuật của chuỗi khởi tạo.

**Luôn đọc kèm độ phủ.** Chỉ số chính không có ý nghĩa nếu không biết nó tính trên bao nhiêu
phần trăm thực tế.

| Chỉ số | Baseline hiện tại | Mục tiêu giai đoạn này |
|---|---|---|
| Số phiên ghi nhận được mỗi ngày | Chưa có | Có số liệu liên tục ≥14 ngày, không đứt quá 1h |
| **Độ phủ của phép đo** | Chưa có | **≥80%** |
| **Tỉ lệ vào Home dưới 10s** (chỉ số chính) | Chưa có | Lập được baseline, **không** đặt mức cải thiện |
| Tỉ lệ phiên hỏng phân loại được nguyên nhân | Chưa có | Lập được baseline; nhóm "không rõ" càng nhỏ càng tốt |
| Thời gian từ nhận phàn nàn tới xác định nguyên nhân | Chưa có | Ghi nhận được cho mọi ca phát sinh |
| Chi phí hiệu năng do chính telemetry gây ra | Chưa có | Đo được, và không đáng kể |

> **Vì sao hầu hết baseline là "chưa có"**: đó không phải thiếu sót của tài liệu — **đó chính
> là lý do feature này tồn tại**. Không con số nào ở cột baseline được suy đoán. Và vì chưa
> biết điểm xuất phát, mục tiêu của giai đoạn này là **lập được baseline**, không phải một
> mức cải thiện. Đặt target cải thiện trước khi biết điểm xuất phát là bịa.

> **Giới hạn bắt buộc đọc kèm độ phủ**: mẫu số là "lượt đổi partner token", nên nhóm phiên
> chết trước khi chạy được mã web nằm ngoài cả tử số lẫn mẫu số. Con số này **luôn cao hơn
> thực tế một cách có hệ thống**. Đây là giới hạn đã biết và đã chấp nhận, không phải thiếu sót.

---

## 9. Điểm yếu và việc còn lại

### 9.1. Chặn việc có số liệu

| Việc | Trạng thái |
|---|---|
| **Bật thu thập trên production** | ⛔ **Chưa bật.** Hệ đang tắt trên mọi bản phát hành cho tới khi cấu hình điểm nhận được nối vào quy trình build production và hạ tầng thu nhận sẵn sàng. **Merge mã không làm thay đổi hành vi phát hành** |
| 14 ngày thu thập liên tục để lập baseline | Chưa bắt đầu — phụ thuộc mục trên |

### 9.2. Rủi ro đang mở

| Rủi ro | Mức | Trạng thái |
|---|---|---|
| **Có dữ liệu nhưng không ai nhìn** — dashboard dựng xong rồi bỏ đó, vì chưa có cảnh báo tự động và người duy nhất dùng đang kiêm nhiệm cả dev lẫn vận hành | **Cao** | Mở. Điều kiện dừng: hai kỳ rà soát liên tiếp bị bỏ ⇒ phải xử lý, không được tiếp tục như cũ |
| **Phụ thuộc một người** — cùng một người vừa sở hữu phạm vi, vừa hiện thực, vừa vận hành, vừa báo cáo | Cao | Mở, và là **tình trạng thường trực**, không phải tạm thời chờ tuyển người |
| **Chỉ có môi trường thật, không có môi trường thử** — mọi thay đổi phép đo chạm thẳng khách hàng | Cao | Mở |
| **Đo xong phát hiện phần lớn nguyên nhân nằm ngoài tầm sửa** (mạng khách, cấu hình WebView của app bank, thiết bị cũ) | Cao | Mở. Nếu chạm ngưỡng này thì kết luận của giai đoạn không phải "sửa gì", mà "phải mở lại việc cải thiện màn lỗi cho khách" |
| **Lớp vô hình** — phiên không tải được mã web thì không công cụ phía client nào ghi nhận được, và nhóm này thiên lệch về phía hỏng nặng | Cao | Mở, đã ghi rõ trong cách đọc độ phủ |
| **Mã bên thứ ba vô chủ** vẫn chạy trong webview ngân hàng | Cao | **Đã chấp nhận có chủ**, có thời hạn |
| **Baseline thời gian xử lý phàn nàn có thể kết thúc rỗng** — không có kênh ticket thì không có ca thật nào chảy vào | Trung bình | **Đã chấp nhận.** Thu dưới 3 ca thật ⇒ mục tiêu này coi như **chưa đạt**, phải mở lại giai đoạn sau. Không được ghi là "đã hoàn thành" |
| **Việc gỡ dịch vụ biểu mẫu bên thứ ba làm mất một chức năng đang chạy** trên trang hỗ trợ khách hàng | Cao | **Đã chấp nhận có chủ.** Mô tả đúng là "gỡ mã làm mất một chức năng đang chạy", **không phải** "dọn mã thừa". Nếu đó là kênh khách dùng để phàn nàn thì rủi ro baseline rỗng ở trên nặng thêm |

### 9.3. Ba câu nói thật, để không ai đọc tài liệu này rồi hiểu sai

1. **Hệ chưa chạy trên production.** Mọi con số trong tài liệu này là mục tiêu, không phải kết quả.
2. **Chân dung CSKH bank là suy luận, chưa phải phỏng vấn.** Không được dùng nó như bằng chứng đã tìm hiểu người dùng.
3. **Việc gỡ mã bên thứ ba được làm trước khi kịp đo**, nên không bao giờ chứng minh được nó có
   đúng là nguyên nhân của "loading quay mãi" hay không.

---

## 10. Bản đồ tài liệu

| Cần gì | Đọc ở đâu |
|---|---|
| **Nghiệp vụ — bản kết luận** | Chính tài liệu này |
| Lịch sử nghiệp vụ đầy đủ: từng quyết định, từng lần bị lật, lý do | `docs/business/webview-monitoring/` (7 file aspect) |
| Yêu cầu chi tiết, thiết kế kỹ thuật, kế hoạch test, changelog | `docs/features/webview-monitoring.md` · `webview-session-logs.md` · `webview-error-capture.md` |
| Dựng và vận hành hạ tầng thu nhận | `docs/features/webview-session-logs/runbook-*.md` |
| Tra cứu lỗi/phiên bằng công cụ truy vấn | `docs/features/webview-session-logs/setup-mcp-trace-session.md` |
| Mã nguồn phần thu thập | `src/utils/monitor/` |

> Ba file trong `docs/features/` là **hồ sơ quy trình** (yêu cầu → thiết kế → review → changelog),
> không phải tài liệu để đọc hiểu hệ thống. Chúng dài ~9.000 dòng và chứa cả các phương án đã bị bác.
