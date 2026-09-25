# PRD: Phân quyền cho biz vận hành — gỡ phụ thuộc vào Admin Root

Bối cảnh: request của đầu biz vận hành. Hiện đang phải cấp tạm cho Manager của biz một tài khoản Admin
Root để team xử lý công việc trước. Mọi số liệu và trích dẫn trong bản này đọc từ mã nguồn
`AT-Core/ambassador`, ngày 2026-09-25.

---

## 1. Mục tiêu

Biz vận hành làm được **năm việc họ đang phải mượn tài khoản root để làm**, bằng chính vai trò Admin mà
họ được phép cấp, và chỉ trong phạm vi ADV họ phụ trách.

Đây **không phải** yêu cầu thêm năng lực mới. Bốn trong năm việc đã có sẵn màn hình, sẵn API, sẵn cổng
kiểm quyền ghi là `IsAdmin`. Chúng không chạy được vì một lý do kỹ thuật duy nhất, lặp lại ở 25 chỗ trong
mã nguồn — mục 1.2.

Năm kết quả phải đạt:

| Việc biz cần | Hôm nay | Sau đợt này |
|---|---|---|
| Liên hệ creator bị sai video | Mục **Người dùng** ẩn với Admin; chi tiết người dùng nằm dưới `IsRoot` | Admin xem được thông tin liên hệ và kênh mạng xã hội của creator thuộc ADV mình |
| Cộng **Thưởng thêm** (tạo, sửa, import) | Admin không gắn ADV bấm Lưu là "Không có quyền" | Admin tạo, sửa, import thưởng trong ADV mình |
| Huỷ mục nội dung và mốc thưởng trong **Đối soát** | Vào được danh sách, mở chi tiết là trắng; nút Huỷ trả lỗi | Huỷ được, có ghi nhật ký |
| Tải **file đối soát** | Nút Tải trả "Không có quyền" | Tải được file của ADV mình |
| Xem và tải **file rút tiền** | Danh sách hiện, chi tiết trả lỗi | Xem và tải được trong phạm vi ADV |

Và một kết quả về rủi ro, là lý do thật sự của đợt này:

| | Hôm nay | Sau đợt này |
|---|---|---|
| Quyền của người làm vận hành | 1 tài khoản root dùng chung, chạm được **14 ADV**, tạo/xoá nhân sự, đổi cấu hình site đang chạy | Tài khoản riêng từng người, giới hạn trong ADV được giao |
| Truy trách nhiệm | Nhật ký ghi "tài khoản root", không phân biệt người thật | Nhật ký ghi đúng người, đúng ADV, đúng hành động |
| Thu hồi quyền | Hẹn miệng khi cấp tạm; hệ thống **không có trường hạn dùng** | Tài khoản tự hết hiệu lực đúng ngày đã hẹn |

### 1.1 Quy mô rủi ro của tài khoản root

Chừng nào Admin chưa làm được năm việc trên thì biz vẫn phải mượn root. Mỗi lần mượn là mở toàn bộ hệ
thống cho một người chỉ cần làm việc vận hành, và mở cho một tài khoản dùng chung nằm ngoài đội kỹ thuật.

Đo trên mã nguồn: tài khoản root đi qua **toàn bộ 233 endpoint** của admin, trong đó 26 endpoint không
vai trò nào khác chạm tới — gồm tạo/sửa/đổi mật khẩu **nhân sự**, tạo/sửa/ngừng hoạt động **ADV**,
ban/gỡ ban **người dùng cuối**, sinh **hợp đồng điện tử**, sửa **eKYC**. Cấp root cho một người chỉ cần
làm năm việc vận hành là cấp thừa **26 endpoint** và thừa **13 ADV**.

### 1.2 Nguyên nhân gốc — một luật phạm vi, hai cách hiểu

Hệ thống có hai cách hỏi "nhân sự này có thuộc ADV kia không", và hai cách trả lời ngược nhau cho cùng
một tài khoản:

| Cách hỏi | Dùng ở | Admin **không** gắn ADV | Admin gắn ADV |
|---|---|---|---|
| `IsPermissionAllPartner()` — coi *chưa gắn ADV* là **toàn quyền** | 50 chỗ, hầu hết là màn danh sách | Thấy hết | Thấy phần mình |
| `Staff.Partner != doc.Partner` — so sánh thô, *chưa gắn ADV* thành `000…000`, không khớp ADV nào | **25 chỗ**, hầu hết là màn chi tiết và nút bấm | **Chặn sạch** | Cho qua |

Hệ quả nhìn thấy được, đúng như biz mô tả: **màn danh sách mở, mọi thao tác bên trong đóng.** Admin của
biz vào Đối soát thấy đủ bản ghi, bấm vào một bản ghi thì trắng, bấm Huỷ thì "Không có quyền".

25 chỗ đó nằm đúng ở năm mục biz kêu:

| Tệp | Số chỗ | Mục trên admin |
|---|---|---|
| `service/reconciliation.go` | 7 | Đối soát |
| `service/transfer.go` | 6 | Xử lý rút tiền |
| `service/event_bonus.go` | 4 | Thưởng thêm |
| `service/export.go` | 1 | Tải file đối soát / rút tiền |
| `service/event.go`, `content.go`, `leaderboard_*.go`, `partner_app_config.go` | 7 | các màn khác, cùng lỗi |

Đây là **lỗi**, không phải thiết kế. Không có tài liệu nào nói Admin không gắn ADV phải bị chặn; cổng ở
tầng router vẫn ghi `IsAdmin` và vẫn cho qua. Chặn xảy ra sâu bên dưới, im lặng, và trả về đúng một câu
"Không có quyền" — nên tới giờ vẫn được hiểu nhầm thành "Admin chưa được cấp quyền này".

### 1.3 Vì sao đây là việc làm được, không phải viết lại

Đối tác **đã làm đúng việc này một lần rồi**, ngày 10/9/2026: thêm vai trò `config_editor`, kèm cổng kiểm
quyền theo ADV, kèm test. Đường đi đã có sẵn và đã được chính đội kỹ thuật ghi lại trong mã nguồn: thêm
mã vai trò vào `StaffRoleList`, nhãn vào `StaffRoleNameList`, `buildRoles()` tự sinh bản gieo xuống DB,
`staff_roles_test.go` canh ba danh sách khớp nhau, `GenerateRole()` gieo vai trò mới xuống **mọi môi
trường đang chạy**. Đợt này dùng lại đúng đường đó.

---

## 2. Người dùng

**Nhân viên vận hành biz** — người dùng chính. Mỗi ngày: liên hệ creator bị sai video, cộng thưởng thêm,
chốt đối soát, xử lý rút tiền. Phụ trách **một hoặc vài ADV**, không phải tất cả. Không phải kỹ sư.

**Manager biz** — người đang giữ tài khoản root tạm. Sau đợt này không còn cần root. Cần nhìn được phần
việc của cả nhóm trong các ADV nhóm phụ trách, và cần biết ai vừa làm gì.

**Admin hệ thống (VFDC)** — người cấp tài khoản. Hôm nay chỉ có hai nấc để chọn: Admin (thiếu việc) hoặc
Root (thừa quyền). Cần nấc ở giữa, và cần cấp được tài khoản **có hạn**.

**Cộng tác viên (CTV)** — duyệt nội dung. Đợt này **không đổi gì** với vai trò này.

**Nhân sự cấu hình ứng dụng (`config_editor`)** — vai trò mới từ 10/9. Đợt này **không đổi gì**.

**Đội kỹ thuật đối tác** — bên thực hiện. Phần lớn công việc là gộp 25 chỗ kiểm quyền rời rạc về một hàm
dùng chung, không phải dựng tính năng mới.

**Người dùng cuối (creator)** — không được thấy khác biệt nào. Nhưng đây là bên hưởng lợi thật: video sai
được liên hệ sớm hơn, thưởng và tiền rút không còn phải chờ một người duy nhất có root.

---

## 3. Phạm vi

### 3.1 Trong phạm vi

- Một luật phạm vi ADV duy nhất, thay cho 25 chỗ so sánh thô hiện tại
- Nhân sự gắn được **nhiều ADV** thay vì một
- Năm nhóm thao tác biz đang thiếu: Người dùng (chỉ phần liên hệ), Thưởng thêm, Huỷ mục đối soát, Tải file
  đối soát, Xem và tải file rút tiền
- Tài khoản có hạn dùng và thu hồi được
- Nhật ký thao tác ghi đủ hành động, ADV và người thật
- Đóng các endpoint hiện chỉ cần đăng nhập là gọi được
- Bộ test ma trận quyền chạy tự động

### 3.2 Ngoài phạm vi

- Bật trường `scopes` trong bản ghi vai trò. Trường này có trong DB, có API trả về, **không nơi nào đọc**.
  Đợt này không dùng tới nó. Xử lý ở đợt sau: hoặc cài đặt thật, hoặc gỡ bỏ
- Đưa vai trò vào token đăng nhập. Hôm nay mọi cổng kiểm quyền đọc DB mỗi lần gọi. Chậm, nhưng đúng, và
  đổi cách này sẽ khiến việc thu hồi quyền trễ đúng bằng hạn token
- Đổi thời hạn token 8 giờ
- Màn tự quản trị vai trò cho người dùng cuối
- Sửa quy trình nghiệp vụ của đối soát, rút tiền, thưởng thêm. Ai được bấm nút thì đổi; **bấm xong ra gì
  thì giữ nguyên**
- 26 endpoint chỉ root mới chạm: nhân sự, ADV, ban người dùng, hợp đồng, eKYC. Giữ nguyên là root

---

## 4. Yêu cầu chức năng

### PQ-001 — Một luật phạm vi ADV duy nhất, fail-closed

**Vì sao cần.** Đây là điều kiện để mọi yêu cầu còn lại tồn tại. Chừng nào còn 25 chỗ tự viết luật phạm vi
thì sửa mục này sẽ sót mục kia, và lần sau biz lại gửi một request giống hệt request lần này.

Hai cách hỏi hiện tại còn sai theo chiều ngược lại: một Admin **chưa ai gán ADV** — tức là cấu hình còn
thiếu — được `IsPermissionAllPartner()` hiểu thành **toàn quyền mọi ADV** ở 50 chỗ. Thiếu cấu hình mà
thành mở hết là kiểu lỗi không ai phát hiện cho tới khi dữ liệu đã đi nhầm chỗ.

**Yêu cầu**

- Một hàm duy nhất trả lời "nhân sự này có được chạm bản ghi của ADV kia không". Mọi service gọi nó
- **Fail-closed**: nhân sự không phải root mà chưa gắn ADV nào thì bị từ chối, không phải được mở hết
- Root giữ nguyên: xuyên mọi ADV
- Màn danh sách và màn chi tiết dùng **chung một luật**. Không còn trường hợp thấy bản ghi trong danh sách
  mà mở ra thì trắng
- 25 chỗ so sánh thô hiện tại được thay hết, không chỗ nào còn tự viết lại

**Nghiệm thu**

- [ ] Admin chưa gắn ADV: mọi màn liệt kê **không trả bản ghi nào**, thay vì trả hết như hôm nay
- [ ] Admin gắn ADV: mọi bản ghi thấy trong danh sách đều mở được chi tiết và bấm được nút
- [ ] Không còn chỗ nào trong `pkg/admin/service` so sánh trực tiếp `Staff.Partner` với `doc.Partner`
- [ ] Root không đổi hành vi ở bất kỳ màn nào

---

### PQ-002 — Nhân sự phụ trách được nhiều ADV

**Vì sao cần.** Bản ghi nhân sự hôm nay có **đúng một** ô ADV. Một nhân viên vận hành phụ trách 3 ADV thì
không có cách nào khai. Đây là lý do thứ hai — sau PQ-001 — khiến root trở thành đường duy nhất: root là
tài khoản duy nhất chạm được quá một ADV.

Nặng hơn: khi bật cờ root cho một tài khoản, hệ thống **xoá luôn** ô ADV và ô vai trò của tài khoản đó.
Root vì vậy không thể bị giới hạn lại. Không có "root của 2 ADV".

**Yêu cầu**

- Nhân sự gắn được **một danh sách ADV**, không phải một ADV
- Danh sách rỗng = không chạm được ADV nào (nối tiếp PQ-001)
- Màn Nhân viên cho chọn nhiều ADV, sửa lại được, và hiện rõ nhân sự đang phụ trách những ADV nào
- Nhân sự đang gắn một ADV chuyển sang danh sách một phần tử, **không ai mất quyền, không ai được thêm
  quyền** sau khi chuyển
- Đổi danh sách ADV của một người có hiệu lực ngay ở lần thao tác kế tiếp, không chờ hết hạn token

**Nghiệm thu**

- [ ] Một tài khoản gắn 3 ADV: thấy và thao tác được đúng 3, ADV thứ tư trả "Không có quyền"
- [ ] Bỏ một ADV khỏi danh sách: người đó mất quyền với ADV đó ngay, không cần đăng nhập lại
- [ ] Toàn bộ nhân sự hiện có giữ nguyên quyền sau khi chuyển dữ liệu — đối chiếu trước/sau từng tài khoản

---

### PQ-003 — Mục Người dùng: phần thông tin liên hệ mở cho Admin

**Vì sao cần.** Creator đăng sai video thì phải gọi được cho họ trong ngày. Hôm nay mục **Người dùng** ẩn
hẳn với Admin, và chi tiết người dùng nằm dưới `IsRoot`. Không có đường nào khác để lấy số điện thoại.

Mục này có hai loại thao tác rất khác nhau đang nằm chung một cổng. Yêu cầu này **chỉ xin loại thứ nhất**:

| Nhóm | Thao tác | Đề xuất |
|---|---|---|
| Đọc để liên hệ | Xem chi tiết, xem danh sách kênh mạng xã hội | **Mở cho Admin**, trong phạm vi ADV |
| Can thiệp vào tài khoản người dùng | Ban, gỡ ban, từ chối hợp đồng, sinh hợp đồng, sửa eKYC, tạo người dùng | **Giữ nguyên root** |

Ngược đời là API **danh sách** người dùng hiện chỉ cần đăng nhập là gọi được — tức là dữ liệu vốn đã với
tới được bằng API, chỉ có màn hình là bị khoá. PQ-010 xử lý vế đó.

**Yêu cầu**

- Admin vào được mục Người dùng và mở được chi tiết creator **thuộc ADV mình phụ trách**
- Thấy: thông tin liên hệ, danh sách kênh mạng xã hội, nội dung đã đăng
- **Không** thấy và **không** bấm được: ban, gỡ ban, hợp đồng, eKYC, tạo người dùng — các nút này không
  hiện với Admin, và gọi thẳng API cũng bị chặn
- Creator của ADV khác không tra ra được, kể cả khi gõ thẳng đường dẫn có id

**Nghiệm thu**

- [ ] Admin mở được chi tiết creator trong ADV mình và đọc được thông tin liên hệ
- [ ] Admin gõ thẳng đường dẫn chi tiết một creator ADV khác: bị chặn
- [ ] Admin gọi thẳng API ban/eKYC/hợp đồng: bị chặn, kể cả với creator trong ADV mình
- [ ] Root giữ nguyên toàn bộ thao tác như hôm nay

---

### PQ-004 — Thưởng thêm: tạo, sửa, import trong phạm vi ADV

**Vì sao cần.** Đây là mục lệch nhiều nhất giữa "cổng ghi gì" và "thực tế chạy thế nào", theo cả hai
hướng cùng lúc:

- Cổng ở tầng router **chỉ yêu cầu đã đăng nhập**. Nghĩa là hôm nay một tài khoản CTV — vai trò chỉ để
  duyệt nội dung — vẫn gọi được API tạo thưởng và import thưởng hàng loạt bằng Excel
- Còn ở tầng service thì bốn chỗ kiểm phạm vi chặn sạch Admin chưa gắn ADV

Kết quả: người **cần** cộng thưởng thì không cộng được, người **không cần** thì gọi được API. Sửa mục này
vừa mở đúng việc cho biz vừa đóng một lỗ hổng chi tiền.

**Yêu cầu**

- Tạo, sửa, import Excel thưởng thêm: **chỉ Admin và root**. CTV và `config_editor` bị chặn ở tầng router,
  không phải chỉ ẩn nút
- Admin chỉ thao tác được trên ADV mình phụ trách. Import Excel có dòng thuộc ADV khác thì **dòng đó bị
  từ chối và báo rõ lý do**, các dòng hợp lệ vẫn chạy
- Huỷ một khoản thưởng thêm: cùng quyền như sửa
- Mỗi lần tạo, sửa, huỷ, import đều ghi nhật ký kèm ADV và người thao tác (xem PQ-009)

**Nghiệm thu**

- [ ] Admin gắn ADV tạo, sửa, import, huỷ thưởng thêm trọn vẹn, không cần root
- [ ] CTV gọi thẳng API tạo thưởng: bị chặn
- [ ] Import file trộn hai ADV: dòng ngoài phạm vi bị từ chối kèm lý do, dòng trong phạm vi vẫn vào
- [ ] Nhật ký ghi đủ bốn loại thao tác

---

### PQ-005 — Đối soát: huỷ mục nội dung và mốc thưởng

**Vì sao cần.** Cả hai thao tác "huỷ mục nội dung" và "huỷ mốc thưởng" đi qua **cùng một API**, và API đó
**đã** nằm dưới cổng `IsAdmin`. Không cần mở thêm quyền nào. Nó không chạy chỉ vì luật phạm vi ở PQ-001.

Đây là yêu cầu rẻ nhất trong bản này: sửa PQ-001 là nó tự chạy. Đưa thành mục riêng để có mốc nghiệm thu,
vì với biz thì đây là việc chặn chốt sổ hàng tháng.

**Yêu cầu**

- Admin mở được chi tiết một bản đối soát thuộc ADV mình, đủ bốn tab: Tổng quan, Nội dung, Mốc thưởng,
  Thưởng thêm
- Huỷ được từng mục nội dung và từng mốc thưởng, kèm lý do
- Bản đối soát của ADV khác không mở được, kể cả khi gõ thẳng đường dẫn có id
- Đổi trạng thái cả bản đối soát: giữ nguyên quyền như hôm nay, chỉ sửa phần phạm vi

**Nghiệm thu**

- [ ] Admin mở chi tiết đối soát ADV mình: cả bốn tab có dữ liệu, không tab nào trắng
- [ ] Huỷ một mục nội dung và một mốc thưởng: thành công, thống kê của bản đối soát cập nhật theo
- [ ] Gõ thẳng id một bản đối soát ADV khác: bị chặn
- [ ] Mỗi lần huỷ ghi một dòng nhật ký có tên người và tên ADV

---

### PQ-006 — Tải file đối soát và file rút tiền

**Vì sao cần.** Nút Tải gọi một API riêng, và API đó kiểm phạm vi bằng đúng kiểu so sánh thô ở PQ-001.
Admin chưa gắn ADV bấm Tải là "Không có quyền" với **mọi** file có gắn ADV.

Có một hệ quả ngược cần vá cùng lúc: khi Admin chưa gắn ADV **tự tạo** một yêu cầu xuất dữ liệu, bản ghi
sinh ra không mang ADV nào — nên lúc tải lại lọt qua đúng phép so sánh đó. Tức là hôm nay Admin chưa gắn
ADV **không tải được file của một ADV cụ thể**, nhưng **tải được file trộn dữ liệu cả 14 ADV** do chính
mình tạo. PQ-001 đóng cả hai vế.

**Yêu cầu**

- Admin tải được file đối soát và file rút tiền của ADV mình phụ trách
- Yêu cầu xuất dữ liệu do Admin tạo **luôn** mang ADV của người tạo; không có bản ghi xuất nào không ADV
- File của ADV ngoài phạm vi: không tải được, kể cả khi có id của file
- Mỗi lần tải ghi một dòng nhật ký

**Nghiệm thu**

- [ ] Admin tải được file đối soát và file rút tiền trong ADV mình
- [ ] Admin không gắn ADV **không** tạo được yêu cầu xuất nào
- [ ] Không sinh được file trộn dữ liệu nhiều ADV từ tài khoản không phải root
- [ ] Đưa id file của ADV khác: bị chặn

---

### PQ-007 — Rút tiền: xem chi tiết và danh sách lệnh rút

**Vì sao cần.** Giống PQ-005: sáu chỗ kiểm phạm vi trong `transfer.go` khiến Admin thấy danh sách nhưng
không mở được chi tiết, không xem được danh sách lệnh rút bên trong, không đổi được trạng thái.

Request của biz chỉ xin **xem và tải**. Bản này giữ đúng vạch đó: các thao tác đổi trạng thái chi tiền
giữ nguyên ranh giới hiện tại, không nới thêm.

**Yêu cầu**

- Admin mở được chi tiết một đợt rút tiền thuộc ADV mình và xem được danh sách lệnh rút bên trong
- Tải được file rút tiền (nối với PQ-006)
- Thao tác đổi trạng thái đợt rút và từ chối lệnh rút: **giữ nguyên quyền như hiện hành**, chỉ sửa phần
  phạm vi ADV cho đúng
- Đợt rút của ADV khác không mở được

**Nghiệm thu**

- [ ] Admin mở được chi tiết đợt rút và danh sách lệnh rút trong ADV mình
- [ ] Đợt rút của ADV khác: bị chặn khi gõ thẳng id
- [ ] Không vai trò nào được thêm quyền đổi trạng thái chi tiền so với hôm nay

---

### PQ-008 — Tài khoản có hạn dùng và thu hồi được

**Vì sao cần.** Thời hạn của một tài khoản cấp tạm hôm nay là một **lời hứa**, không phải một cơ chế.
Bản ghi nhân sự không có trường hạn dùng. Quá ngày đã hẹn, tài khoản đó vẫn vào được, trừ khi có người
nhớ ra và tắt tay.

Đây là thứ khiến đợt này an toàn hơn ngay cả trước khi làm xong: có nó thì mọi lần cấp quyền tạm về sau
đều tự đóng lại đúng ngày, không phụ thuộc vào trí nhớ của ai.

**Yêu cầu**

- Bản ghi nhân sự có **ngày hết hiệu lực**, để trống là không hạn
- Quá ngày đó thì tài khoản không đăng nhập được, và **phiên đang mở bị cắt**, không chờ hết token
- Màn Nhân viên nhập, sửa, xoá được ngày này, và hiện rõ tài khoản nào sắp hết hạn
- Áp được cho **mọi** vai trò, gồm cả root
- Tắt một tài khoản có hiệu lực ngay lập tức, không chờ hết token 8 giờ

**Nghiệm thu**

- [ ] Đặt hạn vào hôm qua: tài khoản đó không đăng nhập được, phiên đang mở bị cắt
- [ ] Tắt một tài khoản đang mở màn hình: thao tác kế tiếp bị chặn ngay
- [ ] Màn Nhân viên liệt kê được các tài khoản sắp hết hạn
- [ ] Tài khoản root cấp tạm đặt được ngày hết hiệu lực và tự đóng đúng ngày đó

---

### PQ-009 — Nhật ký thao tác đủ để truy trách nhiệm

**Vì sao cần.** Lý do duy nhất khiến cấp root "rủi ro rất lớn" không phải là người dùng nó làm sai, mà là
**không dựng lại được ai làm gì**. Bản ghi nhật ký hôm nay có id người thao tác, id bản ghi đích và một
câu mô tả tự do. Nó **không có** trường hành động, **không có** trường ADV — dù danh mục hành động
(tạo, sửa, xoá, tải, duyệt, đổi trạng thái, ban, gỡ ban, từ chối) đã khai sẵn trong mã nguồn và không ai
ghi vào.

Và màn Nhật ký hiện **chỉ cần đăng nhập** là xem được, không lọc theo ADV. Nhân sự của ADV này đọc được
nhật ký thao tác của ADV khác.

**Yêu cầu**

- Mỗi dòng nhật ký ghi đủ: **ai**, **hành động gì**, **trên bản ghi nào**, **thuộc ADV nào**, **lúc nào**
- Dùng đúng danh mục hành động đã khai, không ghi câu tự do thay cho trường hành động
- Đọc nhật ký: chỉ trong phạm vi ADV của người đọc. Root xem toàn bộ
- Năm nhóm thao tác ở PQ-003 đến PQ-007 đều ghi nhật ký
- Không xoá, không sửa được nhật ký từ giao diện

**Nghiệm thu**

- [ ] Làm một thao tác ở mỗi mục PQ-003…PQ-007, nhật ký ghi đủ năm trường
- [ ] Nhân sự ADV A không đọc được nhật ký của ADV B
- [ ] Lọc nhật ký theo người, theo hành động, theo ADV đều ra đúng
- [ ] Không có đường nào xoá hay sửa một dòng nhật ký từ admin

---

### PQ-010 — Đóng các endpoint chỉ cần đăng nhập là gọi được

**Vì sao cần.** Trong 233 endpoint của admin, **60 endpoint không kiểm vai trò** — cứ đăng nhập là gọi
được, bất kể là CTV, `config_editor` hay Admin. Trong đó:

| Nhóm | Số endpoint | Gọi được thì làm gì |
|---|---|---|
| `/migration/*` | 39 | Xoá luồng nội dung, tự động từ chối hàng loạt nội dung, chạy lại tính thưởng, ghi đè dữ liệu người dùng |
| `/event-bonus/*` | 5 | Tạo, sửa, import thưởng tiền (xem PQ-004) |
| `/common/configurations` | 2 | Đọc và **ghi** cấu hình dùng chung |
| `/audits` | 1 | Đọc nhật ký mọi ADV (xem PQ-009) |
| `/users`, `/partners`, duyệt creator | 13 | Danh sách người dùng, danh sách ADV, duyệt hồ sơ |

Mục này là lý lẽ thẳng thắn nhất để đối tác nhận việc: **request của biz không làm hệ thống mở thêm ra —
nó là dịp đóng lại 60 cánh cửa đang mở.** Tài khoản root mà biz đang được cấp tạm không hề nguy hiểm hơn
một tài khoản CTV bất kỳ ở 60 endpoint này.

**Yêu cầu**

- Mỗi endpoint trong 60 endpoint đó được gán đúng một vai trò tối thiểu. Không endpoint nào còn ở mức
  "chỉ cần đăng nhập"
- Nhóm `/migration/*` là công cụ kỹ thuật, **đóng hoàn toàn với mọi vai trò vận hành** — chỉ root, hoặc
  đưa hẳn ra khỏi API công khai
- Có một bài kiểm tự động **liệt kê mọi endpoint và vai trò tối thiểu của nó**, chạy trong CI. Thêm
  endpoint mới mà quên gán vai trò thì **không phát hành được**
- Danh sách endpoint–vai trò là tài liệu bàn giao, không nằm trong đầu ai

**Nghiệm thu**

- [ ] Đăng nhập bằng CTV, gọi lần lượt 60 endpoint: tất cả bị chặn trừ những endpoint cố ý mở cho CTV
- [ ] Không endpoint `/migration/*` nào gọi được bằng tài khoản không phải root
- [ ] Thêm một endpoint mới không khai vai trò: CI báo đỏ
- [ ] Bảng endpoint–vai trò khớp đúng thực tế chạy, kiểm bằng máy chứ không đọc tay

---

### PQ-011 — Ranh giới giữ nguyên: những gì đợt này **không** mở

**Vì sao cần.** Một request nới quyền chỉ được duyệt khi nói rõ cả phần **không** nới. Mục này để đối tác
và bộ phận bảo mật đọc một chỗ là biết đợt này dừng ở đâu.

**Yêu cầu**

Các nhóm sau **giữ nguyên chỉ root**, không vai trò nào khác chạm tới sau đợt này:

| Nhóm | Vì sao giữ |
|---|---|
| Tạo, sửa, đổi mật khẩu, bật tắt **nhân sự** | Ai cấp được quyền thì tự cấp được quyền cho mình |
| Tạo, sửa, ngừng hoạt động **ADV** | Chạm vào site đang chạy của một thương hiệu |
| **Ban / gỡ ban** người dùng cuối | Cắt thu nhập của một creator |
| **Hợp đồng điện tử**, **eKYC** | Giấy tờ pháp lý |
| **Xác thực tài khoản**, **Tag**, **Vai trò** | Ảnh hưởng xuyên ADV |
| Toàn bộ `/migration/*` | Công cụ kỹ thuật, không phải công cụ vận hành |

- CTV và `config_editor` **không được thêm một quyền nào** trong đợt này
- Admin **không** nhận thêm quyền nào ngoài năm nhóm ở PQ-003 đến PQ-007

**Nghiệm thu**

- [ ] Đối chiếu ma trận quyền trước và sau: mọi ô thay đổi đều nằm trong PQ-003…PQ-007
- [ ] CTV và `config_editor`: không ô nào đổi
- [ ] Sáu nhóm trong bảng trên: chỉ root gọi được

---

## 5. Yêu cầu phi chức năng

**NFR-001 — Không làm hỏng cái đang chạy.** CTV, `config_editor` và root giữ nguyên hành vi. Nhân sự đang
gắn một ADV không mất quyền nào sau khi chuyển sang danh sách nhiều ADV. Nghiệm thu bằng đối chiếu
trước/sau từng tài khoản, không bằng đọc mã nguồn.

**NFR-002 — Thiếu cấu hình thì từ chối.** Nhân sự không phải root mà chưa gắn ADV nào thì mọi màn đều
rỗng và mọi nút đều bị chặn. Không có đường nào để "chưa cấu hình" thành "toàn quyền".

**NFR-003 — Không rò dữ liệu chéo ADV.** Mọi màn liệt kê, mọi màn chi tiết, mọi file xuất và mọi dòng
nhật ký đều nằm trong phạm vi ADV của người xem. Có bài kiểm riêng cho từng loại, chạy tự động.

**NFR-004 — Chặn nằm ở backend.** Ẩn/hiện menu chỉ để màn hình sạch. Mọi thao tác phải bị chặn cả khi gọi
thẳng API. Nghiệm thu bằng gọi API trực tiếp, không bằng bấm trên giao diện.

**NFR-005 — Thông báo nói rõ thiếu gì.** Hôm nay mọi trường hợp đều trả đúng một câu "Không có quyền" —
đó là lý do lỗi phạm vi bị hiểu nhầm thành thiếu quyền suốt ba tháng. Thông báo mới phải phân biệt được
*vai trò không đủ* với *ADV ngoài phạm vi*, bằng tiếng Việt.

**NFR-006 — Ma trận quyền có test tự động.** Một bộ test chạy qua mọi cặp (vai trò × endpoint) và đối
chiếu với bảng khai báo. Thêm endpoint hay thêm vai trò mà quên khai thì CI báo đỏ. Đây là điều kiện để
lần sau không phải làm lại đợt này.

**NFR-007 — Đổi quyền có hiệu lực ngay.** Gỡ một ADV, đổi vai trò, tắt tài khoản, hết hạn dùng — tất cả
phải chặn được thao tác kế tiếp, không chờ hết token 8 giờ.

**NFR-008 — Tài liệu bàn giao.** Bảng endpoint–vai trò và bảng "vai trò nào làm được gì trên màn nào" là
sản phẩm bàn giao, cập nhật cùng mã nguồn. Đợt này tồn tại một phần vì bảng đó chưa từng có.

---

## 6. Phụ thuộc và giả định

1. Biz xác nhận **danh sách nhân sự và ADV từng người phụ trách** trước khi thiết kế màn Nhân viên. Không
   có danh sách này thì PQ-002 không nghiệm thu được.
2. PQ-001 là **điều kiện tiên quyết**. PQ-005, PQ-006, PQ-007 phần lớn tự chạy sau khi PQ-001 xong; làm
   ngược thứ tự sẽ vá từng mục rồi vẫn sót.
3. Thêm vai trò hoặc đổi ranh giới vai trò phải đi qua `StaffRoleList` → `StaffRoleNameList` →
   `buildRoles()` → `GenerateRole()`. Quên một bước thì vai trò không có bản ghi dưới DB và cổng kiểm
   quyền **im lặng không cho ai qua** — đã có test canh, giữ nguyên test đó.
4. Mọi cổng kiểm quyền đọc bản ghi nhân sự và vai trò từ DB ở **mỗi** lần gọi API. Giữ nguyên cách này
   trong đợt này; nó chậm nhưng là thứ khiến NFR-007 khả thi.
5. Đổi bản ghi nhân sự (danh sách ADV, hạn dùng) cần một lần chuyển dữ liệu trên production, làm ngoài
   giờ vận hành, có bản lùi.
6. Số ADV hiện tại là 14 và còn tăng. Mọi thứ trong bản này phải đúng khi thêm ADV mà không sửa mã nguồn.
