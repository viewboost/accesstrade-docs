# PRD: Phân quyền chức năng cấu hình được — gỡ phụ thuộc vào Admin Root

Bối cảnh: request của đầu biz vận hành. Hiện đang phải cấp tạm cho Manager của biz một tài khoản Admin
Root để team xử lý công việc trước. Mọi số liệu và trích dẫn trong bản này đọc từ mã nguồn
`AT-Core/ambassador`: bản đầu ngày 2026-09-25, phần đo lại ngày 2026-09-30 có ghi rõ.

**Cập nhật 2026-09-30 — đổi hướng.** Bản 25/9 giải bài toán bằng cách vá vai trò Admin cho đủ năm việc.
Bản này giữ nguyên năm việc đó, nhưng giải bằng **phân quyền theo chức năng, cấu hình trên màn hình**,
thay cho bộ Role và Permission đang viết cứng trong mã nguồn. Lý do ở mục 1.1.

---

## 1. Mục tiêu

Rà soát lại toàn bộ danh sách quyền trong hệ thống, sắp xếp lại thành các **nhóm quyền đúng với từng đội**
đang dùng, và cho phép **cấu hình nhóm quyền trên màn hình** thay vì sửa mã nguồn mỗi lần một đội cần thêm
việc.

Kết quả phải đạt:

| | Hôm nay | Sau đợt này |
|---|---|---|
| Đội vận hành | Admin không làm được năm việc (mục 1.3), phải mượn root | Làm đủ năm việc **bằng tài khoản của chính mình**, trong ADV được giao |
| Tài khoản root | Nhiều tài khoản root, có tài khoản cấp tạm cho Manager đội vận hành | **Chỉ còn một** tài khoản root, do AT giữ. Tài khoản root tạm được thu hồi |
| Đội kỹ thuật | Xin root mỗi lần cần hỗ trợ tra cứu | Có nhóm quyền riêng để hỗ trợ, không cần root |
| Mời tài khoản qua email | Đã chạy, nhưng người được mời chỉ chọn được 1 trong 3 vai trò cứng | Người được mời nhận **đúng nhóm quyền của đội mình** ngay từ đầu |
| Thêm/đổi quyền cho một đội | Sửa mã ở 3 tầng, phát hành bản mới | Root tick quyền trên màn **Vai trò & phân quyền**, có hiệu lực ngay |

Năm việc đội vận hành đang phải mượn root:

| Việc | Hôm nay | Sau đợt này |
|---|---|---|
| **Người dùng** — liên hệ kịp thời creator bị sai video | Mục Người dùng ẩn với Admin; chi tiết nằm dưới `IsRoot` | Xem được liên hệ và kênh MXH của creator thuộc ADV mình |
| **Cộng thưởng** cho creator | Admin không gắn ADV bấm Lưu là "Không có quyền" | Tạo, sửa, import thưởng trong ADV mình |
| **Thưởng thêm** — cộng thưởng | như trên | như trên |
| **File đối soát** — huỷ nội dung, huỷ mốc thưởng, tải file | Mở chi tiết là trắng; nút Huỷ và Tải trả lỗi | Huỷ được, tải được, có nhật ký |
| **File rút tiền** — xem và tải | Danh sách hiện, chi tiết trả lỗi | Xem và tải được trong phạm vi ADV |

### 1.1 Vì sao phải chuyển sang phân quyền cấu hình được

Hôm nay "ai được làm gì" được viết cứng ở **ba tầng**, và ba tầng phải sửa khớp nhau mỗi lần đổi:

| Tầng | Viết cứng ở đâu | Đo ngày 30/9 |
|---|---|---|
| Danh sách vai trò | `StaffRoleList` / `StaffRoleNameList` trong `internal/constants/staff.go` | 3 vai trò: `admin`, `collaborator`, `config_editor` (+ cờ `isRoot`) |
| Cổng API | Middleware so mã vai trò: `IsRoot`, `IsAdmin`, `IsCollaborator`, `IsConfigEditor`, `IsAdminOrConfigEditor`, `HasAnyRole(...)`, `RequiredLogin` | 87 chỗ gắn cổng trong `pkg/admin/router`, trong đó **42 chỗ** chỉ là `RequiredLogin` |
| Menu và nút | `admin/src/access.ts` so mã vai trò bằng mảng chuỗi (`['admin','config_editor']`…), `config/routes.ts` gắn từng menu vào một khoá access | ~35 menu gắn vào 8 khoá access |

Hệ quả:

- **Mỗi nhu cầu mới là một đợt sửa mã.** `config_editor` (10/9) là một đợt; năm việc của biz vận hành là
  đợt thứ hai trong cùng một tháng. Đội kỹ thuật hỗ trợ sẽ là đợt thứ ba.
- **Vai trò là gói cố định.** Muốn cho vận hành huỷ mục đối soát mà không cho duyệt nội dung thì không có
  cách nào — chỉ chọn được giữa Admin (thiếu) và Root (thừa).
- **Bản ghi vai trò đã có sẵn chỗ chứa quyền nhưng không ai dùng.** Collection `roles` có trường
  `scopes`, API `GET /common/scopes` trả danh mục quyền, nhưng danh mục đó là 4 nhóm giả
  (`User`/`File`/`Staff`/`Content` × `edit/delete/view/create/full`) không khớp màn nào, và **không cổng
  kiểm quyền nào đọc** trường này. Đợt này biến nó thành thật.

### 1.2 Quy mô rủi ro của tài khoản root

Chừng nào đội vận hành chưa làm được năm việc bằng tài khoản mình thì vẫn phải mượn root. Mỗi lần mượn là
mở toàn bộ hệ thống cho một người chỉ cần làm việc vận hành.

Đo ngày 25/9: tài khoản root đi qua **toàn bộ 233 endpoint** của admin, trong đó 26 endpoint không vai trò
nào khác chạm tới — gồm tạo/sửa/đổi mật khẩu **nhân sự**, tạo/sửa/ngừng hoạt động **ADV**, ban/gỡ ban
**người dùng cuối**, sinh **hợp đồng điện tử**, sửa **eKYC**. Cấp root cho một người chỉ cần làm năm việc
vận hành là cấp thừa **26 endpoint** và thừa **13 ADV**.

### 1.3 Lỗi phạm vi ADV — phải sửa song song

Bốn trong năm việc đã có màn hình và API nằm dưới cổng `IsAdmin`. Chúng không chạy vì hệ thống có hai
cách hỏi "nhân sự này có thuộc ADV kia không", trả lời ngược nhau cho cùng một tài khoản:

| Cách hỏi | Dùng ở | Admin **không** gắn ADV | Admin gắn ADV |
|---|---|---|---|
| `IsPermissionAllPartner()` — coi *chưa gắn ADV* là **toàn quyền** | ~50 chỗ, hầu hết là màn danh sách | Thấy hết | Thấy phần mình |
| `Staff.Partner != doc.Partner` — so sánh thô | ~25 chỗ, hầu hết là màn chi tiết và nút bấm | **Chặn sạch** | Cho qua |

Hệ quả: **màn danh sách mở, mọi thao tác bên trong đóng**, và tất cả trả về một câu "Không có quyền" —
nên bị hiểu nhầm thành "chưa được cấp quyền". Phân quyền chức năng trả lời câu **"được làm gì"**; lỗi này
nằm ở câu **"trên ADV nào"**. Làm cái thứ nhất mà không sửa cái thứ hai thì tick đủ quyền vẫn bị chặn.

### 1.4 Nền đã có sẵn

| Có sẵn | Dùng lại thế nào |
|---|---|
| Collection `roles` có `code`, `name`, `scopes`, `active` | Thành bản ghi nhóm quyền, `scopes` giữ danh sách mã quyền |
| `GET /common/scopes`, `GET /roles` (root) | Mở rộng thành API danh mục quyền và CRUD vai trò |
| `GenerateRole()` gieo vai trò còn thiếu xuống mọi môi trường | Gieo vai trò mẫu và danh mục quyền ban đầu |
| Mời nhân sự qua email, tự đặt mật khẩu (PR #253) | Chọn nhóm quyền + ADV ngay trong lời mời |
| `HasAnyRole(codes...)`, các guard `*InScope` | Khuôn cho cổng `RequirePermission(code)` và kiểm phạm vi `/:id` |
| Mọi cổng đọc nhân sự + vai trò từ DB ở **mỗi** lần gọi | Đổi quyền có hiệu lực ngay, không chờ token |

---

## 2. Mô hình phân quyền

Ba khái niệm, tách bạch:

| Khái niệm | Trả lời câu | Nằm ở đâu | Ai đổi |
|---|---|---|---|
| **Quyền** (permission) | Làm được **việc gì** — một cặp *chức năng × hành động*, vd `reconciliation.cancel_item` | Danh mục khai trong mã nguồn | Đội kỹ thuật, khi thêm chức năng mới |
| **Vai trò** (role / nhóm quyền) | Một đội được làm **những việc gì** — một tập quyền | DB, cấu hình trên màn **Vai trò & phân quyền** | Root |
| **Phạm vi ADV** | Làm trên **ADV nào** | Bản ghi nhân sự, danh sách ADV | Root (và người có quyền quản lý nhân sự, xem PQ-011) |

Một thao tác được phép khi và chỉ khi:

```
nhân sự đang hoạt động, chưa hết hạn
VÀ mã quyền của thao tác ∈ quyền của vai trò nhân sự
VÀ ADV của bản ghi ∈ danh sách ADV của nhân sự
```

**Root** đứng ngoài mô hình: qua mọi quyền, mọi ADV. Chỉ còn một tài khoản, do AT giữ.

Danh mục quyền nằm trong mã (không cho tạo quyền tự do trên màn) vì mỗi quyền phải gắn với một cổng API
thật. Vai trò thì nằm trong DB vì đó là thứ đổi theo tổ chức, không theo mã.

### 2.1 Danh mục quyền — bản dự thảo

Dựng theo menu admin hiện có. DISO rà lại với danh sách endpoint khi estimate; mỗi endpoint phải thuộc
đúng một quyền.

| Nhóm (menu) | Quyền | Ghi chú |
|---|---|---|
| Nội dung | `content.view`, `content.moderate` | Duyệt, từ chối nội dung |
| Người dùng | `user.view_contact` | Xem chi tiết, liên hệ, kênh MXH, nội dung đã đăng |
| | `user.ban`, `user.contract`, `user.ekyc`, `user.create` | **Khoá root** |
| Hồ sơ creator, Người dùng ADV | `creator.view` | |
| Thống kê, Dashboard | `statistic.view` | |
| Sự kiện | `event.view`, `event.edit` | |
| Thưởng thêm | `bonus.view`, `bonus.edit`, `bonus.import`, `bonus.cancel` | Tiền — không gộp vào `event.edit` |
| Nhiệm vụ, Quà | `mission.view`, `mission.edit`, `gift.view`, `gift.edit` | |
| Đối soát | `reconciliation.view`, `reconciliation.cancel_item`, `reconciliation.change_status`, `reconciliation.export` | Huỷ nội dung và huỷ mốc thưởng dùng chung `cancel_item` |
| Rút tiền | `transfer.view`, `transfer.export`, `transfer.change_status` | `change_status` gồm cả từ chối lệnh rút |
| Dữ liệu xuất | `export.view`, `export.download` | |
| Phân khúc, Mã, Thông báo, Danh mục | `segment.*`, `code.*`, `notification.*`, `category.*` (`view`/`edit`) | |
| Cấu hình ứng dụng, Tin tức, Bài viết, Kênh hỗ trợ, Affiliate | `app_config.*`, `news.*`, `article.*`, `quick_action.*`, `affiliate.*` (`view`/`edit`) | |
| Cấu hình chung | `common_config.view` | Sửa: **khoá root** |
| Nhật ký | `audit.view`, `login_history.view` | |
| Nhân sự | `staff.view`, `staff.invite`, `staff.edit` | Xem PQ-011 |
| Vai trò & phân quyền, ADV, Tag, Xác thực tài khoản, `/migration/*` | — | **Khoá root**, không có mã quyền để gán |

"Khoá root" nghĩa là không tồn tại mã quyền để tick — không vai trò nào nhận được, kể cả khi root muốn.

### 2.2 Vai trò mẫu gieo sẵn

Ba vai trò hiện có được gieo lại **đúng bằng hành vi hôm nay** (PQ-005). Hai vai trò mới cho hai đội đang
phải mượn root. Tên và tập quyền cuối cùng do biz và AT chốt; bảng dưới là điểm xuất phát.

| Nhóm quyền | Admin (giữ nguyên) | CTV (giữ nguyên) | Cấu hình ứng dụng (giữ nguyên) | **Vận hành** (mới) | **Kỹ thuật hỗ trợ** (mới) |
|---|---|---|---|---|---|
| Nội dung | xem, duyệt | xem, duyệt | — | xem | xem |
| Người dùng — liên hệ | — | — | — | ✔ | ✔ |
| Thưởng thêm | *như hôm nay* | — | — | xem, sửa, import, huỷ | xem |
| Đối soát | *như hôm nay* | — | — | xem, huỷ mục, tải file | xem |
| Rút tiền | *như hôm nay* | — | — | xem, tải file | xem |
| Sự kiện, Nhiệm vụ, Quà | *như hôm nay* | — | sự kiện: *như hôm nay* | xem | xem |
| Cấu hình ứng dụng, Tin tức, Bài viết | *như hôm nay* | — | *như hôm nay* | — | xem |
| Nhật ký | *như hôm nay* | — | — | xem | xem |
| Tiền: đổi trạng thái đối soát, rút tiền | *như hôm nay* | — | — | — | — |

Vận hành không nhận quyền đổi trạng thái chi tiền: request chỉ xin xem, tải, huỷ mục. Kỹ thuật hỗ trợ chỉ
đọc, gán nhiều ADV để tra cứu chéo.

---

## 3. Người dùng

**Root (AT)** — người giữ tài khoản root duy nhất. Dựng và sửa nhóm quyền, mời nhân sự, gán ADV.

**Nhân viên vận hành biz** — người dùng chính. Mỗi ngày: liên hệ creator bị sai video, cộng thưởng, chốt
đối soát, xử lý rút tiền. Phụ trách **một hoặc vài ADV**. Không phải kỹ sư.

**Manager biz** — đang giữ tài khoản root tạm. Sau đợt này dùng vai trò Vận hành (hoặc một biến thể có
thêm quyền mời người trong đội, xem PQ-011), tài khoản root tạm bị thu hồi.

**Đội kỹ thuật (AT và đối tác)** — hôm nay xin root mỗi lần hỗ trợ. Sau đợt này dùng vai trò Kỹ thuật hỗ
trợ, chỉ đọc.

**CTV**, **Cấu hình ứng dụng** — không đổi hành vi.

**Đội kỹ thuật đối tác (DISO)** — bên thực hiện.

**Creator** — không thấy khác biệt. Bên hưởng lợi: video sai được liên hệ sớm, thưởng và tiền rút không
còn chờ một người có root.

---

## 4. Phạm vi

### 4.1 Trong phạm vi

- Danh mục quyền chức năng khai trong mã, thay danh mục `scopes` giả hiện tại
- Cổng API kiểm theo **mã quyền**, thay các cổng so mã vai trò
- Menu và nút trên admin hiện/ẩn theo **danh sách quyền** của người đăng nhập
- Màn **Vai trò & phân quyền**: tạo, sửa, nhân bản, ngừng dùng vai trò; tick quyền theo nhóm
- Chuyển ba vai trò hiện có sang mô hình mới **không đổi hành vi**; gieo hai vai trò mẫu mới
- Một luật phạm vi ADV fail-closed; nhân sự gắn được nhiều ADV
- Vai trò Vận hành làm đủ năm việc
- Lời mời qua email chọn nhóm quyền, ADV, hạn dùng; tài khoản có hạn dùng
- Nhật ký thao tác ghi đủ người, hành động, ADV; ghi cả thay đổi vai trò
- Không endpoint nào còn ở mức "chỉ cần đăng nhập"
- Thu hồi tài khoản root tạm, còn một root
- Test ma trận quyền tự động trong CI

### 4.2 Ngoài phạm vi

- Gán quyền lẻ trực tiếp cho một người (ngoài vai trò). Mỗi nhân sự **một** vai trò; cần khác thì nhân
  bản vai trò
- Nhiều vai trò trên một nhân sự
- Phân quyền theo trường dữ liệu (vd ẩn số điện thoại nhưng hiện email)
- Tạo mã quyền mới từ màn hình — quyền mới đi cùng mã nguồn
- Đưa quyền vào token đăng nhập; đổi thời hạn token 8 giờ
- Đổi quy trình nghiệp vụ của đối soát, rút tiền, thưởng. Ai được bấm nút thì đổi; **bấm xong ra gì thì
  giữ nguyên**
- Phân quyền cho app creator và các site white-label

---

## 5. Yêu cầu chức năng

Thứ tự: PQ-001 → PQ-005 là **nền** (không đổi hành vi ai), PQ-006 → PQ-008 **mở việc cho vận hành**,
PQ-009 → PQ-012 **đóng rủi ro**.

### PQ-001 — Danh mục quyền chức năng

**Vì sao cần.** Không có danh mục thật thì màn phân quyền không có gì để tick, và cổng API không có gì để
kiểm. Danh mục `scopes` hiện tại không khớp màn nào.

**Yêu cầu**

- Một danh mục duy nhất trong mã nguồn: mỗi quyền có mã, nhãn tiếng Việt, nhóm (menu), mô tả ngắn
- Theo bản dự thảo mục 2.1; DISO rà lại với danh sách endpoint và đề xuất chỉnh
- `GET /common/scopes` trả danh mục mới, gom theo nhóm
- Quyền khoá root **không có trong danh mục**
- Thêm quyền mới chỉ bằng một chỗ khai, không sửa ở nơi khác

**Nghiệm thu**

- [ ] Mọi menu trên admin (trừ nhóm khoá root) có ít nhất một quyền `view`
- [ ] Danh mục không còn mã quyền kiểu `user_full`, `file_edit`

---

### PQ-002 — Cổng API kiểm theo mã quyền

**Vì sao cần.** Đây là chỗ biến việc tick trên màn thành việc chặn thật. Hôm nay 87 chỗ gắn cổng so mã vai
trò; đổi vai trò nào làm được gì là phải sửa từng chỗ.

**Yêu cầu**

- Một cổng dùng chung, dạng `RequirePermission("bonus.import")`, gắn cho **từng endpoint**
- Cổng đọc nhân sự và vai trò từ DB ở mỗi lần gọi (như hôm nay) để đổi quyền có hiệu lực ngay
- Root qua mọi cổng; nhóm khoá root dùng cổng `IsRoot` như cũ
- Thay hết `IsAdmin`, `IsCollaborator`, `IsConfigEditor`, `IsAdminOrConfigEditor`, `HasAnyRole` và
  `RequiredLogin` đơn lẻ trên endpoint nghiệp vụ. Không còn endpoint nào kiểm bằng mã vai trò
- Vai trò ngừng dùng hoặc nhân sự không có vai trò: bị chặn mọi endpoint nghiệp vụ
- Bảng **endpoint → mã quyền** sinh ra từ mã nguồn, là tài liệu bàn giao

**Nghiệm thu**

- [ ] Bỏ tick một quyền khỏi vai trò: người mang vai trò đó bị chặn endpoint tương ứng ở lần gọi kế tiếp,
  không cần đăng nhập lại
- [ ] `git grep` trong `pkg/admin/router` không còn `IsAdmin` / `HasAnyRole` / so mã vai trò
- [ ] Thêm endpoint không khai quyền: CI báo đỏ (xem PQ-010)

---

### PQ-003 — Menu và nút theo quyền

**Vì sao cần.** `access.ts` hôm nay so mã vai trò bằng mảng chuỗi. Vai trò mới tạo trên màn sẽ không thấy
menu nào nếu tầng này vẫn viết cứng.

**Yêu cầu**

- API thông tin người đăng nhập trả kèm **danh sách mã quyền** và danh sách ADV
- Mọi khoá access trong `access.ts` và `routes.ts` tính từ danh sách quyền, không so mã vai trò
- Nút thao tác (Huỷ, Tải, Import, Đổi trạng thái…) ẩn khi thiếu quyền tương ứng
- Trang đích sau đăng nhập là menu đầu tiên người đó có quyền xem (thay logic riêng cho `config_editor`
  trong `landing-route.ts`)
- Ẩn/hiện chỉ để màn hình sạch; chặn thật nằm ở PQ-002

**Nghiệm thu**

- [ ] Tạo một vai trò chỉ có `reconciliation.view`: đăng nhập chỉ thấy menu Đối soát, không thấy nút Huỷ
- [ ] Không còn chuỗi `'admin'`, `'collaborator'`, `'config_editor'` trong `admin/src/access.ts`

---

### PQ-004 — Màn Vai trò & phân quyền

**Vì sao cần.** Đây là outcome chính: đổi quyền của một đội mà không cần phát hành bản mới.

**Yêu cầu**

- Menu mới **Vai trò & phân quyền**, chỉ root
- Danh sách vai trò: tên, mô tả, số quyền, số nhân sự đang dùng, trạng thái
- Tạo, sửa tên/mô tả, **nhân bản** từ vai trò có sẵn, ngừng dùng
- Màn sửa quyền: bảng theo nhóm menu × hành động, tick từng ô hoặc cả nhóm; `edit` tự kéo theo `view`
  của cùng nhóm
- Quyền liên quan tiền (thưởng, đối soát, rút tiền) được đánh dấu để người tick biết
- Không xoá được vai trò đang có nhân sự dùng; ngừng dùng thì phải chuyển nhân sự sang vai trò khác trước
- Lưu thay đổi hiện tóm tắt: thêm/bớt quyền nào, ảnh hưởng bao nhiêu người
- Mọi thay đổi vai trò ghi nhật ký (ai, lúc nào, quyền nào thêm/bớt)

**Nghiệm thu**

- [ ] Root tạo vai trò mới, tick quyền, gán cho một nhân sự: người đó dùng được ngay, không cần kỹ thuật
- [ ] Bỏ quyền khỏi vai trò đang dùng: có hiệu lực ở thao tác kế tiếp của mọi người mang vai trò
- [ ] Nhân sự không phải root không vào được màn này và không gọi được API của nó
- [ ] Nhật ký hiện đúng từng lần thêm/bớt quyền

---

### PQ-005 — Chuyển đổi không đổi hành vi

**Vì sao cần.** Đổi mô hình phân quyền trên hệ thống đang chạy 14 ADV. Nếu bước chuyển làm ai mất hay thừa
quyền thì mọi thứ phía sau đều mất tin cậy.

**Yêu cầu**

- Gieo tập quyền cho Admin, CTV, Cấu hình ứng dụng **đúng bằng** những gì cổng hiện tại cho qua
- Giữ nguyên `_id` và `code` của ba vai trò; nhân sự không phải đổi gì
- Làm và phát hành phần nền (PQ-001 → PQ-005) **trước** khi mở quyền mới cho ai
- Riêng các endpoint `RequiredLogin` mà vai trò nào cũng gọi được: chuyển đổi xong mới đóng ở PQ-010,
  không đóng lẫn trong bước này

**Nghiệm thu**

- [ ] Ma trận (vai trò × endpoint) trước và sau khi chuyển: **không ô nào đổi**, chạy bằng test chứ không
  đọc tay
- [ ] Đăng nhập bằng từng vai trò: menu thấy được trước và sau giống nhau

---

### PQ-006 — Một luật phạm vi ADV duy nhất, fail-closed

**Vì sao cần.** Mục 1.3. Không sửa thì vai trò Vận hành tick đủ quyền vẫn bị chặn ở màn chi tiết.

**Yêu cầu**

- Một hàm duy nhất trả lời "nhân sự này có được chạm bản ghi của ADV kia không". Mọi service gọi nó
- **Fail-closed**: nhân sự không phải root mà chưa gắn ADV thì bị từ chối, không phải được mở hết
- Màn danh sách và màn chi tiết dùng chung một luật
- Thay hết các chỗ so sánh thô `Staff.Partner` với `doc.Partner` và các chỗ dùng `IsPermissionAllPartner()`

**Nghiệm thu**

- [ ] Nhân sự chưa gắn ADV: mọi màn liệt kê không trả bản ghi nào
- [ ] Nhân sự gắn ADV: mọi bản ghi thấy trong danh sách đều mở được chi tiết và bấm được nút (nếu có quyền)
- [ ] Không còn chỗ nào trong `pkg/admin/service` so sánh trực tiếp `Staff.Partner` với `doc.Partner`
- [ ] Root không đổi hành vi

---

### PQ-007 — Nhân sự phụ trách được nhiều ADV

**Vì sao cần.** Bản ghi nhân sự có **đúng một** ô ADV. Nhân viên vận hành phụ trách 3 ADV, hay kỹ thuật
hỗ trợ tra cả 14 ADV, không có cách nào khai — root thành đường duy nhất. Bật cờ root còn **xoá luôn** ô
ADV và ô vai trò, nên không có "root của 2 ADV".

**Yêu cầu**

- Nhân sự gắn **một danh sách ADV**; rỗng = không chạm ADV nào
- Màn Nhân viên và màn mời chọn nhiều ADV, hiện rõ ai phụ trách ADV nào
- Nhân sự đang gắn một ADV chuyển sang danh sách một phần tử, không ai mất hay được thêm quyền
- Nhân sự VFDC hôm nay không gắn ADV (đang được hiểu là toàn quyền): **chuyển sang gắn đủ danh sách ADV
  hiện có**, để PQ-006 không cắt quyền của họ. Biz xác nhận danh sách này
- Đổi danh sách ADV có hiệu lực ở thao tác kế tiếp

**Nghiệm thu**

- [ ] Tài khoản gắn 3 ADV thao tác được đúng 3, ADV thứ tư trả "ADV ngoài phạm vi"
- [ ] Bỏ một ADV: mất quyền với ADV đó ngay, không cần đăng nhập lại
- [ ] Toàn bộ nhân sự hiện có giữ nguyên quyền sau khi chuyển — đối chiếu từng tài khoản

---

### PQ-008 — Vai trò Vận hành làm đủ năm việc

**Vì sao cần.** Đây là kết quả biz nhìn thấy. Sau PQ-001 → PQ-007, mỗi việc chỉ còn là gán đúng quyền và
đảm bảo endpoint tương ứng đi qua đúng cổng và đúng luật phạm vi.

| Việc | Quyền | Yêu cầu riêng | Nghiệm thu |
|---|---|---|---|
| Người dùng — liên hệ creator | `user.view_contact` | Mở mục Người dùng và chi tiết creator thuộc ADV mình: liên hệ, kênh MXH, nội dung đã đăng. Ban, hợp đồng, eKYC, tạo người dùng **không hiện và API chặn** | Gõ thẳng id creator ADV khác: bị chặn. Gọi thẳng API ban/eKYC: bị chặn |
| Cộng thưởng / Thưởng thêm | `bonus.edit`, `bonus.import`, `bonus.cancel` | Import Excel có dòng thuộc ADV khác: **dòng đó bị từ chối kèm lý do**, dòng hợp lệ vẫn vào. CTV và Cấu hình ứng dụng bị chặn ở cổng (hôm nay gọi được) | Tạo, sửa, import, huỷ trọn vẹn không cần root. File trộn hai ADV xử lý đúng |
| Đối soát — huỷ nội dung, huỷ mốc thưởng | `reconciliation.cancel_item` | Mở chi tiết đủ bốn tab: Tổng quan, Nội dung, Mốc thưởng, Thưởng thêm. Huỷ kèm lý do. Đổi trạng thái cả bản đối soát **không** thuộc quyền này | Không tab nào trắng. Huỷ xong thống kê bản đối soát cập nhật |
| Tải file đối soát | `reconciliation.export` | Yêu cầu xuất do nhân sự tạo **luôn mang ADV**; không sinh được file trộn nhiều ADV từ tài khoản không phải root (hôm nay sinh được) | Tải được file ADV mình; đưa id file ADV khác: bị chặn |
| File rút tiền — xem và tải | `transfer.view`, `transfer.export` | Mở chi tiết đợt rút và danh sách lệnh rút bên trong. Đổi trạng thái, từ chối lệnh rút **không** thuộc vai trò này | Xem, tải được trong ADV mình. Đợt rút ADV khác: bị chặn |

Chung cho cả năm việc: mỗi thao tác ghi nhật ký (PQ-012).

---

### PQ-009 — Mời nhân sự đúng nhóm quyền, có hạn dùng

**Vì sao cần.** Mời qua email đã chạy (PR #253) nhưng chỉ chọn được 1 trong 3 vai trò cứng và một ADV. Có
nhóm quyền rõ ràng thì người được mời nhận đúng quyền ngay từ lời mời. Còn hạn dùng: thời hạn của tài
khoản cấp tạm hôm nay là một **lời hứa** — bản ghi nhân sự không có trường hạn dùng.

**Yêu cầu**

- Lời mời chọn: **vai trò** (danh sách vai trò đang dùng, lấy từ DB), **danh sách ADV**, **ngày hết hiệu
  lực** (để trống là không hạn)
- Quá ngày hết hiệu lực: không đăng nhập được, **phiên đang mở bị cắt** ở thao tác kế tiếp
- Màn Nhân viên nhập, sửa, xoá ngày này và lọc được tài khoản sắp hết hạn
- Áp được cho mọi vai trò, gồm cả root
- Tắt một tài khoản có hiệu lực ngay, không chờ hết token 8 giờ

**Nghiệm thu**

- [ ] Mời một người với vai trò Vận hành + 2 ADV: nhận lời mời xong dùng được ngay đúng 2 ADV đó
- [ ] Đặt hạn vào hôm qua: không đăng nhập được, phiên đang mở bị cắt
- [ ] Tắt tài khoản đang mở màn hình: thao tác kế tiếp bị chặn

---

### PQ-010 — Không endpoint nào "chỉ cần đăng nhập"

**Vì sao cần.** Đo ngày 25/9: **60 endpoint không kiểm vai trò** — CTV hay Cấu hình ứng dụng cũng gọi
được. Gồm 39 endpoint `/migration/*` (xoá luồng nội dung, từ chối hàng loạt, chạy lại tính thưởng), 5
endpoint thưởng thêm, ghi cấu hình dùng chung, đọc nhật ký mọi ADV. Đo lại 30/9 còn 42 chỗ gắn
`RequiredLogin` trong router — DISO đo lại số endpoint khi estimate.

**Yêu cầu**

- Mỗi endpoint trong số đó được gán một mã quyền, hoặc khoá root
- `/migration/*` khoá root, hoặc đưa hẳn ra khỏi API công khai
- Một bài kiểm trong CI **liệt kê mọi endpoint và quyền của nó**. Endpoint mới không khai quyền thì CI đỏ

**Nghiệm thu**

- [ ] Đăng nhập bằng CTV, gọi lần lượt các endpoint trên: chỉ qua những endpoint cố ý mở cho CTV
- [ ] Không endpoint `/migration/*` nào gọi được bằng tài khoản không phải root
- [ ] Thêm endpoint mới không khai quyền: CI báo đỏ

---

### PQ-011 — Quyền khoá root và chống tự nâng quyền

**Vì sao cần.** Phân quyền cấu hình được chỉ an toàn khi có những thứ **không cấu hình được**. Ai sửa được
vai trò thì tự cấp được mọi quyền cho mình.

**Yêu cầu**

Giữ **chỉ root**, không có mã quyền để gán:

| Nhóm | Vì sao |
|---|---|
| Vai trò & phân quyền | Ai sửa được vai trò thì tự nâng được quyền |
| Tạo, sửa, ngừng hoạt động **ADV** | Chạm site đang chạy của một thương hiệu |
| **Ban / gỡ ban** người dùng cuối | Cắt thu nhập của creator |
| **Hợp đồng điện tử**, **eKYC**, tạo người dùng | Giấy tờ pháp lý |
| Xác thực tài khoản, Tag, sửa Cấu hình chung | Ảnh hưởng xuyên ADV |
| `/migration/*` | Công cụ kỹ thuật, không phải công cụ vận hành |
| Bật cờ root cho tài khoản khác | Mục tiêu còn đúng một root |

Quản lý nhân sự (`staff.invite`, `staff.edit`) **được phép gán** — để Manager vận hành tự mời người trong
đội — nhưng với ràng buộc:

- Chỉ gán được vai trò có tập quyền **nằm trong** tập quyền của chính mình
- Chỉ gán được ADV **nằm trong** danh sách ADV của chính mình
- Không sửa được tài khoản của chính mình, không sửa được root

**Nghiệm thu**

- [ ] Không có mã quyền nào trong danh mục ứng với các nhóm ở bảng trên
- [ ] Manager có `staff.invite` mời người với vai trò rộng hơn mình, hoặc ADV ngoài phạm vi mình: bị chặn
- [ ] Chỉ root bật được cờ root

---

### PQ-012 — Nhật ký thao tác đủ để truy trách nhiệm

**Vì sao cần.** Cấp root rủi ro vì **không dựng lại được ai làm gì**. Nhật ký hôm nay có id người, id bản
ghi và một câu mô tả tự do; **không có** trường hành động, **không có** trường ADV — dù danh mục hành động
đã khai sẵn trong mã và không ai ghi vào. Màn Nhật ký chỉ cần đăng nhập là xem, không lọc theo ADV.

**Yêu cầu**

- Mỗi dòng ghi đủ: **ai**, **hành động** (dùng danh mục có sẵn), **bản ghi nào**, **ADV nào**, **lúc nào**
- Năm việc ở PQ-008 và mọi thay đổi vai trò, quyền, ADV, hạn dùng của nhân sự đều ghi nhật ký
- Đọc nhật ký cần `audit.view`, chỉ trong phạm vi ADV của người đọc; root xem toàn bộ
- Không xoá, không sửa nhật ký từ giao diện

**Nghiệm thu**

- [ ] Mỗi việc ở PQ-008 và mỗi lần sửa vai trò: nhật ký ghi đủ năm trường
- [ ] Nhân sự ADV A không đọc được nhật ký ADV B
- [ ] Lọc theo người, hành động, ADV đều ra đúng

---

### PQ-013 — Thu hồi root tạm, còn một root

**Vì sao cần.** Đây là kết quả rủi ro của cả đợt. Làm xong mà vẫn còn tài khoản root tạm thì chưa đạt.

**Yêu cầu**

- Sau khi PQ-008 nghiệm thu: Manager đội vận hành chuyển sang tài khoản riêng với vai trò Vận hành, tài
  khoản root tạm bị tắt
- Đội kỹ thuật dùng vai trò Kỹ thuật hỗ trợ, không cấp root cho hỗ trợ thường ngày
- Màn Nhân viên hiện rõ số tài khoản root; có cảnh báo khi nhiều hơn một

**Nghiệm thu**

- [ ] Đếm nhân sự `isRoot = true` đang hoạt động trên production: **đúng 1**, do AT giữ
- [ ] Đội vận hành làm năm việc trong một tuần mà không phải xin root lần nào

---

## 6. Yêu cầu phi chức năng

**NFR-001 — Không làm hỏng cái đang chạy.** Chuyển đổi (PQ-005, PQ-007) không làm ai mất hay thừa quyền.
Nghiệm thu bằng đối chiếu trước/sau từng tài khoản và từng endpoint, không bằng đọc mã.

**NFR-002 — Thiếu cấu hình thì từ chối.** Không vai trò, vai trò ngừng dùng, không ADV, hết hạn — đều bị
chặn. Không có đường nào để "chưa cấu hình" thành "toàn quyền".

**NFR-003 — Không rò dữ liệu chéo ADV.** Mọi màn liệt kê, chi tiết, file xuất, dòng nhật ký nằm trong phạm
vi ADV của người xem. Có bài kiểm tự động cho từng loại.

**NFR-004 — Chặn nằm ở backend.** Nghiệm thu bằng gọi API trực tiếp, không bằng bấm giao diện.

**NFR-005 — Thông báo nói rõ thiếu gì.** Phân biệt *thiếu quyền* (kèm tên quyền) với *ADV ngoài phạm vi*,
bằng tiếng Việt. Thiếu quyền trả **403**, không trả 401 — 401 hôm nay làm admin tự đăng xuất người dùng.

**NFR-006 — Đổi quyền có hiệu lực ngay.** Sửa vai trò, gỡ ADV, tắt tài khoản, hết hạn — chặn được thao tác
kế tiếp, không chờ token 8 giờ. Nếu thêm cache vai trò để giảm tải DB thì phải xoá cache khi vai trò đổi.

**NFR-007 — Ma trận quyền có test tự động.** Bộ test chạy qua mọi (vai trò mẫu × endpoint) và đối chiếu bảng
khai báo. Thêm endpoint mà quên khai quyền thì CI đỏ.

**NFR-008 — Tài liệu bàn giao.** Bảng endpoint → quyền và bảng vai trò mẫu → quyền sinh từ mã nguồn, cập
nhật cùng mã.

---

## 7. Gợi ý chia mốc để estimate

| Mốc | Gồm | Ai thấy khác biệt | Điều kiện xong |
|---|---|---|---|
| **1. Nền phân quyền** | PQ-001 → PQ-005 | Root thấy màn Vai trò & phân quyền. Người khác **không thấy gì đổi** | Ma trận trước/sau không ô nào đổi |
| **2. Mở việc cho vận hành** | PQ-006 → PQ-009 | Đội vận hành dùng tài khoản riêng, làm đủ năm việc | Nghiệm thu PQ-008 với biz |
| **3. Đóng rủi ro** | PQ-010 → PQ-013 | Chỉ còn một root; CTV mất các endpoint không được phép | Đếm root = 1; CI kiểm ma trận |

Mốc 1 và mốc 2 nối tiếp nhau; PQ-006 và PQ-007 có thể làm song song với mốc 1 vì không đụng phần phân
quyền chức năng. Nếu cần gỡ root tạm sớm nhất, thứ tự tối thiểu là PQ-006 + PQ-007 + PQ-008 chạy trên vai
trò Admin hiện có, rồi mới chuyển sang mô hình mới — nhưng như vậy phải sửa cổng hai lần.

---

## 8. Phụ thuộc và giả định

1. Biz xác nhận **danh sách nhân sự, vai trò và ADV từng người** trước mốc 2. Không có danh sách này thì
   PQ-007 và PQ-013 không nghiệm thu được.
2. Biz và AT chốt **tập quyền của vai trò Vận hành và Kỹ thuật hỗ trợ** (mục 2.2) trước mốc 2.
3. Mọi cổng tiếp tục đọc nhân sự và vai trò từ DB ở mỗi lần gọi; đây là thứ khiến NFR-006 khả thi.
4. Đổi bản ghi nhân sự (danh sách ADV, hạn dùng) và bản ghi vai trò (tập quyền) cần chuyển dữ liệu trên
   production, ngoài giờ vận hành, có bản lùi.
5. Số ADV hiện là 14 và còn tăng. Thêm ADV không cần sửa mã; thêm chức năng mới thì phải thêm mã quyền cùng
   lúc (PQ-010 canh việc này).
6. Số liệu mục 1.2, 1.3, PQ-010 đo ngày 25/9. Mã nguồn đã đổi từ đó (thêm `HasAnyRole`, các guard
   `*InScope`, mời nhân sự qua email) — DISO đo lại khi estimate.

---

## 9. Câu hỏi cần chốt trước khi estimate

1. Manager vận hành có được **tự mời người trong đội** (PQ-011, `staff.invite` có ràng buộc) hay mời nhân
   sự giữ chỉ root?
2. Vai trò Admin hiện có: giữ nguyên làm vai trò riêng, hay gộp vào Vận hành sau khi chuyển?
3. Kỹ thuật hỗ trợ có cần xem **thông tin liên hệ creator** không, hay chỉ xem dữ liệu nghiệp vụ?
4. Nhân sự VFDC không gắn ADV hôm nay (đang được hiểu là toàn quyền): gắn đủ 14 ADV, hay rà lại từng người?
