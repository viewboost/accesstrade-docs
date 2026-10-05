# PRD: Phân quyền hệ thống quản trị Ambassador

**Ngày:** 2026-10-05
**Sản phẩm:** Ambassador — trang quản trị (admin)
**Mã nguồn tham chiếu:** `AT-Core/ambassador`, nhánh `develop`, commit `b3a91953`. Mọi trích dẫn `file:dòng` theo commit
này.
**Trạng thái:** chờ biz duyệt mục 4 và chốt các câu hỏi ở mục 12; sau đó DISO estimate.

**Cách đọc tài liệu này**

| Người đọc | Đọc |
|---|---|
| Biz (duyệt vai trò) | Mục 1, **mục 4** (viết bằng lời thường, không cần đọc phần kỹ thuật), mục 12 |
| DISO (thiết kế, estimate) | Toàn bộ; phần kỹ thuật ở mục 2, 5, 7–11 và Phụ lục A |

---

## 1. Bối cảnh và mục tiêu

### 1.1 Bối cảnh

Trang quản trị hiện chỉ có ba nhóm quyền: **Cộng tác viên (CTV)**, **Admin** và **Admin Root**. Đội vận hành chỉ
được cấp tới Admin, nhưng Admin không làm được các việc vận hành hằng ngày. Để team xử lý công việc, Manager của đội
vận hành đang được cấp tạm một tài khoản **Admin Root** — tài khoản làm được mọi thứ trên hệ thống, trên mọi ADV.

Các việc đội vận hành đang phải mượn root để làm:

| Việc | Hôm nay |
|---|---|
| **Người dùng** — liên hệ kịp thời creator bị sai video | Chi tiết người dùng chỉ root mở được |
| **Cộng thưởng cho creator** (Thưởng thêm): tạo, sửa, nhập Excel, huỷ | Admin chưa gắn ADV bấm Lưu là "Không có quyền" |
| **File đối soát** — huỷ nội dung, huỷ mốc thưởng, tải file đối soát | Mở chi tiết là trắng; Huỷ và Tải trả lỗi |
| **File rút tiền** — xem và tải | Danh sách hiện, chi tiết trả lỗi |

Lý do gốc của ba việc sau: Manager phụ trách **nhiều ADV**, nhưng bản ghi nhân sự chỉ chứa **một** ADV. Root là tài
khoản duy nhất chạm được nhiều ADV.

### 1.2 Mục tiêu

Rà soát toàn bộ danh sách quyền trong hệ thống, sắp xếp lại thành **các vai trò đúng với từng đội** đang sử dụng, và
có **phân quyền chức năng đầy đủ, cấu hình trên màn hình** thay cho bộ Role và Permission đang viết cứng trong mã
nguồn.

| Kết quả | Hôm nay | Sau đợt này |
|---|---|---|
| Đội vận hành | Mượn root để làm việc hằng ngày | Làm đủ việc **bằng tài khoản của chính mình**, đúng vai trò, trong ADV được giao |
| Tài khoản root | Có tài khoản root cấp tạm cho Manager đội vận hành | **Chỉ còn một** tài khoản root, do AT giữ. Tài khoản tạm được thu hồi |
| Đội kỹ thuật | Xin root mỗi lần hỗ trợ tra cứu | Có vai trò **Kỹ thuật hỗ trợ**, xem được mọi màn, không cần root |
| Tiền | Một tài khoản vừa lập vừa duyệt khoản chi | **Người lập khoản chi và người duyệt khoản chi là hai người** |
| Mời tài khoản qua email | Chỉ chọn được 1 trong 3 vai trò cứng, một ADV | Người được mời nhận **đúng vai trò và ADV** ngay từ lời mời |
| Đổi quyền của một đội | Sửa mã nguồn ở 3 tầng, phát hành bản mới | Root sửa trên màn **Vai trò & phân quyền**, có hiệu lực ngay |

---

## 2. Hiện trạng kỹ thuật

### 2.1 Phân quyền viết cứng ở ba tầng

| Tầng | Viết cứng ở đâu | Số đo |
|---|---|---|
| Danh sách vai trò | `StaffRoleList` / `StaffRoleNameList` (`internal/constants/staff.go`) | 3 vai trò + cờ `isRoot` |
| Cổng API | Middleware so mã vai trò: `IsRoot`, `IsAdmin`, `IsCollaborator`, `IsConfigEditor`, `IsAdminOrConfigEditor`, `HasAnyRole(...)` | 263 route; **60 endpoint** không có cổng vai trò nào, chỉ cần đăng nhập |
| Menu và nút | `admin/src/access.ts` so mã vai trò bằng mảng chuỗi | 8 khoá access |

Collection `roles` đã có trường `scopes` và API `GET /common/scopes`, nhưng danh mục là 4 nhóm mẫu
(`User`/`File`/`Staff`/`Content` × `edit/delete/view/create/full`) không khớp màn nào, và **không cổng nào đọc**.

60 endpoint chỉ cần đăng nhập gồm: 40 migration/backfill, 5 thưởng thêm, 5 `/users` (có hai endpoint duyệt creator),
5 `/partners`, 4 `/common` (có ghi cấu hình chung), 1 `/audits`.

### 2.2 Tài khoản root

Root đi qua mọi route của admin, trong đó có các nhóm không vai trò nào khác chạm tới: nhân sự, ADV, khoá người
dùng, hợp đồng điện tử, eKYC, thưởng sự kiện, xác thực tài khoản. Cấp root cho một người chỉ cần làm việc vận hành
là cấp thừa toàn bộ các nhóm đó và thừa mọi ADV ngoài phạm vi người đó phụ trách. Số endpoint chính xác lấy từ bảng
mốc ở PQ-06.

### 2.3 Phạm vi ADV — bốn luật đang cùng tồn tại

| Luật | Đọc nhân sự từ | Nhân sự chưa gắn ADV | Vị trí |
|---|---|---|---|
| Hàm `StaffInfo` (`AssignPartnerForStaff` 29 lời gọi, `IsPermissionAllPartner` 28, `IsAllowPartner` 21) | **JWT** | Toàn quyền | `internal/model/mg/staff.go:91–118` |
| So sánh thô `Staff.Partner` với `doc.Partner` (≥ 15 chỗ) | DB | Bị chặn | nhiều nhất `service/reconciliation.go`, `service/event_bonus.go` |
| `StaffCanReachPartner` trong guard `*InScope` | DB | Toàn quyền | `router/routeauth/partner_scope.go:63` |
| `CanEditAppConfig` | DB | **Từ chối (fail-closed)** | `internal/service/partner_app_config_access.go:11` |

Thêm một biến thể cho tag: nhân sự ADV thấy cả tag của mình và tag dùng chung
(`AssignPartnerWithNonExistsPartnerForStaff`).

Hệ quả: **màn danh sách mở, mọi thao tác bên trong đóng**, và tất cả trả về một câu "Không có quyền". Phân quyền
chức năng trả lời "được làm gì"; bốn luật này trả lời "trên ADV nào". Phải gom cả hai.

Phạm vi ADV đọc từ **claim `partner` trong JWT** (`router/routeauth/auth.go:201`, `:225`). Đổi ADV hôm nay có tác
dụng chỉ vì `resetToken` xoá token và người dùng phải đăng nhập lại (`service/staff.go:292`, `:360`).

### 2.4 Nền đã có sẵn

| Có sẵn | Dùng lại thế nào |
|---|---|
| Collection `roles` | Bản ghi vai trò; tập quyền lưu ở **trường mới** chỉ chứa mã quyền, không tái dùng `scopes` |
| Mời nhân sự qua email, tự đặt mật khẩu | Chọn vai trò, ADV, hạn dùng ngay trong lời mời |
| `resetToken` khi sửa hoặc tắt nhân sự | Tắt tài khoản đã có hiệu lực ngay — giữ nguyên |
| `CanEditAppConfig` | Khuôn cho luật phạm vi ADV duy nhất |
| Khung `/migration/jobs` | Chạy migration gieo quyền một lần |
| Guard `*InScope` trả 403 | Khuôn cho mã lỗi thiếu quyền |

---

## 3. Người dùng

| Người dùng | Hôm nay | Sau đợt này |
|---|---|---|
| **Trưởng nhóm vận hành** (Manager biz) | Mượn root tạm | Mốc 0: Admin gắn nhiều ADV. Mốc 2: vai trò **Quản lý vận hành**, tự mời và quản lý người trong đội |
| **Nhân viên vận hành — duyệt nội dung** | Admin, thiếu việc | Vai trò **Vận hành nội dung** |
| **Nhân viên vận hành — theo dõi hiệu suất** | Admin, thiếu việc | Vai trò **Vận hành hiệu suất** — người lập các khoản thưởng |
| **Người chốt tiền** (biz chỉ định) | Dùng Admin hoặc root | Vai trò **Duyệt chi** — người duyệt khoản chi |
| **Đội kỹ thuật** (AT và đối tác) | Xin root mỗi lần hỗ trợ | Vai trò **Kỹ thuật hỗ trợ**, chỉ xem |
| **Người dựng site ADV** | Cấu hình ứng dụng | Không đổi |
| **Cộng tác viên** | Duyệt nội dung; gọi được một số API ngoài việc của mình | **Chỉ còn duyệt nội dung** |
| **Admin hiện có** | Admin | Giữ như hôm nay để không ai mất việc; không cấp Admin cho người mới sau Mốc 2 |
| **Root (AT)** | Nhiều tài khoản root | Một tài khoản duy nhất: dựng vai trò, gán quyền, các việc chỉ root |
| **Creator** | — | Không thấy khác biệt. Video sai được liên hệ sớm hơn, thưởng và tiền rút không chờ một người có root |

---

## 4. Vai trò và quyền — phần dành cho biz duyệt

Mục này viết bằng lời thường. Phần mã quyền cho đội kỹ thuật nằm ở mục 5.

### 4.1 Nguyên tắc

1. **Mỗi người có một vai trò.** Vai trò quyết định người đó làm được việc gì.
2. **Mỗi người được giao một số ADV** và chỉ thấy dữ liệu của các ADV đó. Kỹ thuật hỗ trợ được giao mọi ADV, kể cả
   ADV mở sau này.
3. **Việc không có trong vai trò thì nút không hiện**, và hệ thống vẫn chặn kể cả khi gõ thẳng đường dẫn.
4. **Người lập khoản chi và người duyệt khoản chi luôn là hai người.** Ngoài root (và Admin cũ trong thời gian chuyển
   tiếp), không vai trò nào vừa lập khoản chi (cộng thưởng thêm, huỷ mục đối soát) vừa duyệt khoản chi (chốt đối
   soát, duyệt rút tiền).
5. **Phần lập khoản tiền giao cho Vận hành hiệu suất, không dồn cho Quản lý.** Dồn cho một người thì cả đội lại phải
   chờ một người.
6. **Việc tiền và việc xem dữ liệu cá nhân được canh chặt hơn.** Mỗi lượt xem số điện thoại, email của creator đều
   được ghi lại: ai xem, xem của ai, lúc nào.

### 4.2 Các vai trò

**Root** — *một tài khoản duy nhất, do AT giữ*
- Làm được mọi việc, trên mọi ADV.
- Những việc **chỉ root** làm được (không vai trò nào khác nhận được): tạo và sửa ADV; khoá, mở khoá creator; hợp
  đồng điện tử; eKYC; tạo người dùng; xác thực tài khoản; thưởng sự kiện; tạo và sửa vai trò, phân quyền; cấp quyền
  root; giao "mọi ADV" cho một người; đặt lại mật khẩu cho người khác; các công cụ kỹ thuật (chạy lại dữ liệu, sửa
  dữ liệu hàng loạt).
- Không có hạn dùng. Mỗi lần root đăng nhập đều gửi cảnh báo.

**Quản lý vận hành** — *mới*
- **Ai dùng:** trưởng nhóm vận hành (người đang mượn root).
- **Việc hằng ngày:** mọi việc của Vận hành nội dung và Vận hành hiệu suất; xem nhật ký thao tác; mời người vào
  đội, đổi vai trò, tắt tài khoản người trong đội — chỉ gán được Vận hành nội dung và Vận hành hiệu suất, chỉ trong
  ADV mình phụ trách.
- **Không làm được:** duyệt chi.

**Vận hành nội dung** — *mới*
- **Ai dùng:** nhân viên phụ trách duyệt.
- **Việc hằng ngày:** duyệt, từ chối, ghim video, gắn cảnh báo; duyệt creator đăng ký tham gia; liên hệ creator
  khi video sai.
- **Không làm được:** việc liên quan tiền; sửa sự kiện.

**Vận hành hiệu suất** — *mới*
- **Ai dùng:** nhân viên theo dõi hiệu suất.
- **Việc hằng ngày:** theo dõi lượt xem, thống kê, bảng xếp hạng; cộng thưởng thêm (tạo, sửa, nhập Excel, huỷ);
  huỷ nội dung, mốc thưởng không hợp lệ trong đối soát; tải file đối soát; xem và tải file rút tiền.
- **Không làm được:** duyệt chi; duyệt nội dung; xem số điện thoại, email creator.

**Duyệt chi** — *mới*
- **Ai dùng:** người chốt tiền, do biz chỉ định.
- **Việc hằng ngày:** chốt đối soát để chi; duyệt, từ chối đợt rút và lệnh rút; xem các màn tiền; tải file đối
  soát, rút tiền.
- **Không làm được:** tạo, sửa, huỷ khoản thưởng; huỷ mục đối soát.

**Kỹ thuật hỗ trợ** — *mới*
- **Ai dùng:** đội kỹ thuật AT và đối tác.
- **Việc hằng ngày:** xem mọi màn nghiệp vụ của mọi ADV để tra cứu khi hỗ trợ.
- **Không làm được:** mọi thao tác ghi; xem số điện thoại, email creator; tải file đối soát, rút tiền. Việc cần chạy
  công cụ kỹ thuật vẫn nhờ root của AT, có ghi lại.

**Cấu hình ứng dụng** — *có sẵn, không đổi*
- **Ai dùng:** người dựng site ADV.
- **Việc hằng ngày:** cấu hình giao diện và tính năng site, xuất bản; tin tức, bài viết, kênh hỗ trợ, chiến dịch
  affiliate; tạo và sửa sự kiện, mẫu sự kiện.
- **Không làm được:** việc liên quan tiền; duyệt nội dung.

**Cộng tác viên (CTV)** — *có sẵn, thu hẹp*
- **Việc hằng ngày:** chỉ còn duyệt nội dung. Nhóm này gần như không hoạt động; cần thêm việc thì bổ sung sau.
- **Không làm được:** mọi việc khác.

**Admin** — *có sẵn, giữ nguyên*
- Giữ như hôm nay (Phụ lục A) để không ai mất việc. Không cấp cho người mới sau Mốc 2.
- Được thêm: xem liên hệ creator trong ADV mình (từ Mốc 0).
- Bị bớt: các việc hôm nay làm được chỉ vì hệ thống không kiểm (PQ-11); sửa tag, cấu hình chung nếu không
  được giao "mọi ADV".

### 4.3 Bảng vai trò × việc

Ký hiệu: ✔ làm được · — không làm được · *(tiền)* việc liên quan tiền · *(cá nhân)* xem dữ liệu cá nhân, mỗi lượt có
ghi lại. Admin giữ như hôm nay (Phụ lục A).

| Việc | Quản lý vận hành | Vận hành nội dung | Vận hành hiệu suất | Duyệt chi | Kỹ thuật hỗ trợ | Cấu hình ứng dụng | CTV |
|---|---|---|---|---|---|---|---|
| **Nội dung và creator** | | | | | | | |
| Xem video creator đã nộp | ✔ | ✔ | ✔ | — | ✔ | — | ✔ |
| Duyệt, từ chối, ghim video; gắn cảnh báo; thêm tay nội dung | ✔ | ✔ | — | — | — | — | ✔ |
| Duyệt creator đăng ký tham gia; duyệt người dùng vào ADV | ✔ | ✔ | — | — | — | — | — |
| Xem số điện thoại, email, kênh mạng xã hội của creator *(cá nhân)* | ✔ | ✔ | — | — | — | — | — |
| Xem hồ sơ creator, danh sách người dùng của ADV | ✔ | ✔ | ✔ | ✔ | ✔ | — | — |
| **Sự kiện và hiệu suất** | | | | | | | |
| Xem sự kiện, thống kê, biểu đồ, bảng xếp hạng | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | Chỉ danh sách sự kiện |
| Tạo, sửa sự kiện, mẫu sự kiện, ngân sách, bảng xếp hạng | — | — | — | — | — | ✔ | — |
| **Tiền** | | | | | | | |
| Xem thưởng thêm | ✔ | — | ✔ | ✔ | ✔ | — | — |
| Cộng thưởng thêm: tạo, sửa, nhập Excel, huỷ *(tiền)* | ✔ | — | ✔ | — | — | — | — |
| Xem đối soát | ✔ | — | ✔ | ✔ | ✔ | — | — |
| Huỷ nội dung, mốc thưởng không hợp lệ trong đối soát *(tiền)* | ✔ | — | ✔ | — | — | — | — |
| Xem đợt rút tiền và các lệnh rút | ✔ | — | ✔ | ✔ | ✔ | — | — |
| Tải file đối soát, file rút tiền *(tiền)* | ✔ | — | ✔ | ✔ | — | — | — |
| Chốt đối soát để chi; duyệt, từ chối đợt rút và lệnh rút *(tiền)* | — | — | — | ✔ | — | — | — |
| **Site của ADV** | | | | | | | |
| Cấu hình giao diện, tính năng site; xuất bản, khôi phục phiên bản | — | — | — | — | Chỉ xem | ✔ | — |
| Tin tức, bài viết, kênh hỗ trợ, chiến dịch affiliate | — | — | — | — | Chỉ xem | ✔ | — |
| **Dữ liệu dùng chung mọi ADV** | | | | | | | |
| Xem danh mục, tag | ✔ | ✔ | ✔ | — | ✔ | ✔ | Chỉ tag |
| Xem cấu hình chung | — | — | — | — | ✔ | — | — |
| Sửa danh mục, tag, cấu hình chung | — | — | — | — | — | — | — |
| **Việc hôm nay chỉ Admin làm** (Q7) | | | | | | | |
| Nhiệm vụ, duyệt điểm nhiệm vụ, quà, phân khúc, mã, thông báo admin | — | — | — | — | Chỉ xem | — | — |
| Sửa hồ sơ creator, trạng thái CBNV | — | — | — | — | — | — | — |
| **Quản lý đội** | | | | | | | |
| Xem nhật ký thao tác, lịch sử đăng nhập | ✔ | — | — | — | ✔ | — | — |
| Xem danh sách nhân sự trong đội | ✔ | — | — | — | — | — | — |
| Mời người vào đội, đổi vai trò, tắt tài khoản | ✔ | — | — | — | — | — | — |
| **Được giao ADV nào** | ADV mình phụ trách | ADV được giao | ADV được giao | Q6 | Mọi ADV | ADV mình dựng | ADV được giao |

Sửa danh mục, tag, cấu hình chung: chỉ Admin được giao "mọi ADV" và root.

### 4.4 Thay đổi với người đang dùng

| Người | Hôm nay | Sau đợt này |
|---|---|---|
| Trưởng nhóm vận hành | Dùng tài khoản root tạm | Mốc 0: Admin gắn các ADV mình phụ trách, root tạm bị thu hồi. Mốc 2: Quản lý vận hành — tự mời người trong đội, **không còn duyệt chi** |
| Nhân viên vận hành | Admin, thiếu việc, phải nhờ người có root | Vận hành nội dung hoặc Vận hành hiệu suất, làm đủ việc của mình |
| Người chốt tiền | Dùng Admin hoặc root | Duyệt chi; không tự lập khoản thưởng |
| Đội kỹ thuật | Xin root khi hỗ trợ | Kỹ thuật hỗ trợ, xem mọi ADV; chạy công cụ kỹ thuật vẫn nhờ root của AT |
| Cộng tác viên | Duyệt nội dung; gọi được API thưởng thêm, duyệt creator, nhật ký, cấu hình chung | Chỉ duyệt nội dung |
| Cấu hình ứng dụng | Dựng site; gọi được API thưởng thêm, duyệt creator, nhật ký, cấu hình chung | Dựng site như hôm nay; mất các API ngoài việc |
| Admin | Như Phụ lục A | Giữ nguyên; thêm xem liên hệ creator; mất các API công cụ kỹ thuật; sửa dữ liệu dùng chung cần được giao "mọi ADV" |

### 4.5 Checklist cho biz duyệt

- [ ] Danh sách vai trò ở 4.2: đủ đội, đúng tên, đúng người dùng
- [ ] Bảng 4.3 — đặc biệt các dòng *(tiền)* và *(cá nhân)*
- [ ] Nguyên tắc tách người lập và người duyệt khoản chi (4.1)
- [ ] Bảng thay đổi với người đang dùng (4.4)
- [ ] Các câu hỏi Q1, Q3, Q5, Q6, Q7 ở mục 12

---

## 5. Mô hình phân quyền — phần kỹ thuật

### 5.1 Ba khái niệm

| Khái niệm | Trả lời câu | Nằm ở đâu | Ai đổi |
|---|---|---|---|
| **Quyền** | Làm được **việc gì** — *chức năng × hành động*, vd `reconciliation.cancel_item` | Danh mục khai trong mã | Đội kỹ thuật, khi thêm chức năng |
| **Vai trò** | Một đội làm được **những việc gì** — một tập quyền | DB, cấu hình trên màn | Root |
| **Phạm vi ADV** | Làm trên **ADV nào** | Bản ghi nhân sự | Root; Quản lý vận hành trong giới hạn của mình |

Một thao tác được phép khi và chỉ khi:

```
nhân sự đang hoạt động, chưa hết hạn
VÀ vai trò đang hoạt động, chứa mã quyền của thao tác
VÀ bản ghi nằm trong phạm vi ADV của nhân sự (5.2)
```

Root đứng ngoài mô hình: qua mọi quyền, mọi ADV, không có hạn dùng.

Danh mục quyền nằm trong mã (không tạo quyền tự do trên màn) vì mỗi quyền phải gắn với cổng API thật. Vai trò nằm
trong DB vì đó là thứ đổi theo tổ chức.

### 5.2 Phạm vi ADV

| Dạng | Nghĩa | Ai đặt được |
|---|---|---|
| `all` | Mọi ADV, gồm cả ADV tạo sau này | **Chỉ root** |
| `list` | Danh sách ADV cụ thể. Rỗng = không chạm ADV nào | Root; Quản lý vận hành trong phạm vi của mình |

Luật cho từng loại bản ghi:

| Bản ghi | Xem | Sửa / thao tác |
|---|---|---|
| Thuộc một ADV | ADV ∈ phạm vi | ADV ∈ phạm vi |
| Thuộc nhiều ADV (trường `partners` dạng mảng) | Có giao nhau với phạm vi | **Nằm trọn** trong phạm vi |
| Dùng chung (không ADV: tag, danh mục, cấu hình chung…) | Mọi nhân sự có quyền xem của chức năng đó | Chỉ nhân sự phạm vi `all` |

Trường `type` (`vfdc` / `partner`) trên bản ghi nhân sự hiện không chỗ nào đọc; bỏ đi khi có `all` / `list`.

### 5.3 Bảng quyền

Mỗi dòng là **một quyền** — đơn vị nhỏ nhất root tick được trên màn Vai trò & phân quyền. DISO rà lại khi dựng
registry route (PQ-09): mỗi endpoint thuộc đúng một quyền, hoặc `root`, hoặc `public`.

**Quy ước đặt mã:** `<chức năng>.<hành động>`.

| Hành động | Gồm |
|---|---|
| `view` | Xem danh sách, chi tiết, số liệu |
| `edit` | Tạo, sửa, nhân bản, bật/tắt, xoá mềm |
| `import` / `export` | Nhập hàng loạt bằng Excel / xuất và tải file |
| `approve` | Duyệt hoặc từ chối yêu cầu của bên khác |
| Hành động riêng | Thao tác liên quan tiền hoặc không đảo ngược được — luôn tách khỏi `edit` (vd `cancel_item`, `change_status`) |

Có `edit` / `import` / `export` / `approve` thì **tự có** `view` cùng chức năng (ép ở backend khi lưu vai trò).
💰 = liên quan tiền, được đánh dấu trên màn tick quyền. Xoá cứng không có mã quyền.


**Nội dung**

| # | Mã quyền | Tên hiển thị | Cho phép làm gì | Màn / API | Ghi chú |
|---|---|---|---|---|---|
| 1 | `content.view` | Xem nội dung | Xem danh sách, chi tiết, số liệu nội dung creator đã đăng | Nội dung — `GET /contents*` |  |
| 2 | `content.moderate` | Duyệt nội dung | Duyệt, từ chối (từng bài và theo lô), ghim, gắn tag cảnh báo, cập nhật số liệu một nội dung | Nội dung — `/contents/:id/status`, `/batch-status`, `/reject-by-select`, `/:id/pin`… | Route cập nhật hàng loạt: Q9 |
| 3 | `content_manual_flow.view` | Xem luồng nội dung thủ công | Xem các luồng nội dung được thêm tay | `GET /content-manual-flows` |  |
| 4 | `content_manual_flow.edit` | Tạo luồng nội dung thủ công | Thêm tay một luồng nội dung cho creator | `POST /content-manual-flows` |  |

**Người dùng và creator**

| # | Mã quyền | Tên hiển thị | Cho phép làm gì | Màn / API | Ghi chú |
|---|---|---|---|---|---|
| 5 | `user.view_contact` | Xem liên hệ creator | Mở chi tiết creator: số điện thoại, email, kênh mạng xã hội, nội dung đã đăng. **Mỗi lượt xem ghi nhật ký** | Người dùng — `GET /users/:id`, `/users/:id/socials` | *(cá nhân)* — mỗi lượt xem ghi nhật ký |
| 6 | `creator.view` | Xem hồ sơ creator | Danh sách người dùng, danh sách và chi tiết hồ sơ creator, thống kê hồ sơ, danh sách người dùng của ADV | `GET /users`, `/creator-profiles*`, `/partners/users` |  |
| 7 | `creator.edit` | Sửa hồ sơ creator | Đổi trạng thái hồ sơ, cập nhật chỉ số, cấu hình điều kiện hồ sơ | `/creator-profiles/:id/change-status`, `/update-stats`, `/conditions` |  |
| 8 | `creator.approve` | Duyệt creator | Duyệt hoặc từ chối hồ sơ đăng ký làm creator | `/users/approval-creator*` |  |
| 9 | `partner_member.approve` | Duyệt thành viên ADV | Duyệt hoặc từ chối yêu cầu tham gia ADV của người dùng | `/users/approval-partner*` |  |
| 10 | `user_partner.view` | Xem người dùng ADV | Xem người dùng thuộc ADV và trạng thái CBNV | Người dùng ADV |  |
| 11 | `user_partner.edit_staff_status` | Đổi trạng thái CBNV | Đánh dấu / bỏ đánh dấu người dùng ADV là nhân viên của thương hiệu | `PUT /user-partners/:id/staff-status` |  |
| 12 | `user.edit_partner_data` | Sửa dữ liệu người dùng ADV | Sửa dữ liệu người dùng riêng của ADV WildRift | `PUT /partners/users/wildrift` | Q10 |

**Sự kiện và thống kê**

| # | Mã quyền | Tên hiển thị | Cho phép làm gì | Màn / API | Ghi chú |
|---|---|---|---|---|---|
| 13 | `event.view` | Xem danh sách sự kiện | Danh sách sự kiện (dùng cả ở ô chọn sự kiện khi duyệt nội dung) | `GET /events` |  |
| 14 | `event.view_detail` | Xem chi tiết sự kiện | Chi tiết sự kiện, yêu cầu, ngân sách, bảng xếp hạng | `GET /events/:id`, `/:id/leaderboard*` |  |
| 15 | `event.edit` | Quản lý sự kiện | Tạo, sửa, nhân bản, bật/tắt sự kiện; yêu cầu, ngân sách, opshub; cấu hình và ghim bảng xếp hạng | `/events/*` |  |
| 16 | `event_schema.view` | Xem mẫu sự kiện | Danh sách mẫu sự kiện | `GET /event-schemas` |  |
| 17 | `event_schema.edit` | Quản lý mẫu sự kiện | Tạo, sửa, bật/tắt mẫu sự kiện dùng để dựng sự kiện | `/event-schemas*` |  |
| 18 | `statistic.view` | Xem thống kê | Dashboard, thống kê sự kiện, thống kê theo nhân sự, biểu đồ, báo cáo | Thống kê, Dashboard — `/events/statistic`, `/staff-statistic`, `/chart`, `/report-statistic` |  |

**Thưởng, nhiệm vụ, quà**

| # | Mã quyền | Tên hiển thị | Cho phép làm gì | Màn / API | Ghi chú |
|---|---|---|---|---|---|
| 19 | `bonus.view` | Xem thưởng thêm | Danh sách và chi tiết các khoản thưởng thêm | Thưởng thêm — `GET /event-bonus*` | 💰 |
| 20 | `bonus.edit` | Cộng thưởng thêm | Tạo, sửa một khoản thưởng thêm cho creator | `POST`/`PUT /event-bonus` | 💰 |
| 21 | `bonus.import` | Import thưởng thêm | Cộng thưởng hàng loạt bằng file Excel; dòng ngoài phạm vi ADV bị từ chối kèm lý do | `/event-bonus/import-excel` | 💰 |
| 22 | `bonus.cancel` | Huỷ thưởng thêm | Huỷ một khoản thưởng thêm đã tạo | `/event-bonus` | 💰 |
| 23 | `mission.view` | Xem nhiệm vụ | Danh sách và chi tiết nhiệm vụ, danh sách điểm chờ duyệt | `GET /missions*` |  |
| 24 | `mission.edit` | Quản lý nhiệm vụ | Tạo, sửa nhiệm vụ | `/missions` |  |
| 25 | `mission.approve` | Duyệt điểm nhiệm vụ | Duyệt hoặc từ chối điểm creator nhận từ nhiệm vụ | `/missions/point-approval` |  |
| 26 | `gift.view` | Xem quà | Danh sách quà, chi tiết, lịch sử đổi quà | `GET /gifts*` |  |
| 27 | `gift.edit` | Quản lý quà | Tạo, sửa, bật/tắt quà | `/gifts` |  |

**Đối soát, rút tiền, dữ liệu xuất**

| # | Mã quyền | Tên hiển thị | Cho phép làm gì | Màn / API | Ghi chú |
|---|---|---|---|---|---|
| 28 | `reconciliation.view` | Xem đối soát | Danh sách và chi tiết bản đối soát, đủ bốn tab: Tổng quan, Nội dung, Mốc thưởng, Thưởng thêm | Đối soát — `GET /reconciliations*` | 💰 |
| 29 | `reconciliation.cancel_item` | Huỷ mục đối soát | Huỷ từng mục nội dung hoặc mốc thưởng trong bản đối soát, kèm lý do | `/reconciliations/:id/item/:idItem/change-status` | 💰 |
| 30 | `reconciliation.change_status` | Đổi trạng thái đối soát | Đổi trạng thái cả bản đối soát (chốt, duyệt, huỷ) | `/reconciliations/:id/change-status` | 💰 |
| 31 | `reconciliation.export` | Tải file đối soát | Tạo yêu cầu xuất và tải file đối soát; file luôn mang ADV của bản đối soát | Đối soát, Dữ liệu xuất | 💰 |
| 32 | `transfer.view` | Xem rút tiền | Danh sách, chi tiết đợt rút và danh sách lệnh rút bên trong | Rút tiền — `GET /transfers*`, `/:id/withdraw-cashes` | 💰 |
| 33 | `transfer.export` | Tải file rút tiền | Tạo yêu cầu xuất và tải file rút tiền | Rút tiền, Dữ liệu xuất | 💰 |
| 34 | `transfer.change_status` | Xử lý rút tiền | Đổi trạng thái đợt rút, từ chối lệnh rút | `/transfers/:id/change-status`, `/change-declined` | 💰 |
| 35 | `export.view` | Xem dữ liệu xuất | Xem danh sách file đã xuất. Tải từng file cần quyền tải của loại file đó (`reconciliation.export`, `transfer.export`) | Dữ liệu xuất — `GET /data-exports` |  |

**Phân khúc, mã, thông báo, danh mục**

| # | Mã quyền | Tên hiển thị | Cho phép làm gì | Màn / API | Ghi chú |
|---|---|---|---|---|---|
| 36 | `segment.view` | Xem phân khúc | Danh sách và chi tiết phân khúc | `GET /segments*` |  |
| 37 | `segment.edit` | Quản lý phân khúc | Tạo, sửa, bật/tắt phân khúc | `/segments` |  |
| 38 | `user_segment.view` | Xem người dùng trong phân khúc | Danh sách người dùng thuộc phân khúc | `GET /user-segments` |  |
| 39 | `user_segment.edit` | Sửa người dùng trong phân khúc | Thêm, xoá người dùng khỏi phân khúc | `/user-segments` |  |
| 40 | `user_segment.import` | Import người dùng vào phân khúc | Thêm hàng loạt bằng Excel | `/user-segments/import-excel` |  |
| 41 | `code.view` | Xem mã | Danh sách mã | `GET /manage-codes` |  |
| 42 | `code.edit` | Quản lý mã | Tạo, sửa mã | `/manage-codes` |  |
| 43 | `code.import` | Import mã | Nhập mã hàng loạt bằng Excel | `/manage-codes/import-excel` |  |
| 44 | `notification.view` | Xem thông báo | Danh sách và chi tiết thông báo admin | `GET /admin-notifications*` |  |
| 45 | `notification.edit` | Soạn thông báo | Tạo, sửa, nhân bản thông báo | `/admin-notifications` |  |
| 46 | `notification.approve` | Duyệt thông báo | Đánh dấu hoàn thành hoặc từ chối thông báo | `/:id/completed`, `/:id/rejected` |  |
| 47 | `category.view` | Xem danh mục | Danh sách danh mục | `GET /categories` |  |
| 48 | `category.edit` | Quản lý danh mục | Tạo, sửa danh mục | `/categories` |  |

**Cấu hình ADV và nội dung site**

| # | Mã quyền | Tên hiển thị | Cho phép làm gì | Màn / API | Ghi chú |
|---|---|---|---|---|---|
| 49 | `app_config.view` | Xem cấu hình ứng dụng | Xem cấu hình site của ADV, bản nháp, lịch sử phiên bản, trạng thái onboarding | Cấu hình ứng dụng — `/partners/:id/app-config*` |  |
| 50 | `app_config.edit` | Sửa cấu hình ứng dụng | Sửa bản nháp cấu hình site, bật/tắt tính năng của ADV | `/partners/:id/app-config`, `/:id/features` |  |
| 51 | `app_config.publish` | Xuất bản cấu hình | Xuất bản bản nháp lên site đang chạy, khôi phục phiên bản cũ | `/app-config/publish`, `/restore/:version` | Đổi ngay site công khai |
| 52 | `news.view` | Xem tin tức | Danh sách và chi tiết tin tức (gồm banner trang chủ) | `GET /news*` |  |
| 53 | `news.edit` | Quản lý tin tức | Tạo, sửa, nhân bản, bật/tắt tin tức | `/news` |  |
| 54 | `article.view` | Xem bài viết | Danh sách và chi tiết bài viết (gồm ba bài pháp lý) | `GET /articles*` |  |
| 55 | `article.edit` | Quản lý bài viết | Tạo, sửa bài viết | `/articles` |  |
| 56 | `quick_action.view` | Xem kênh hỗ trợ | Danh sách kênh hỗ trợ của ADV | `GET /quick-actions` |  |
| 57 | `quick_action.edit` | Quản lý kênh hỗ trợ | Tạo, sửa, bật/tắt kênh hỗ trợ | `/quick-actions` |  |
| 58 | `affiliate.view` | Xem chiến dịch affiliate | Danh sách, chi tiết chiến dịch và liên kết chiến dịch – sự kiện | `GET /affiliate-campaigns*`, `/campaign-affiliate-mappings*` |  |
| 59 | `affiliate.edit` | Quản lý chiến dịch affiliate | Tạo, sửa, bật/tắt chiến dịch, gắn chiến dịch vào sự kiện | `/affiliate-campaigns`, `/campaign-affiliate-mappings` |  |

**Hệ thống**

| # | Mã quyền | Tên hiển thị | Cho phép làm gì | Màn / API | Ghi chú |
|---|---|---|---|---|---|
| 60 | `tag.view` | Xem tag | Danh sách tag (gồm tag cảnh báo dùng khi duyệt nội dung) | `GET /tags` |  |
| 61 | `tag.edit` | Quản lý tag | Tạo, sửa, bật/tắt tag. Tag dùng chung cần phạm vi `all` | `/tags` | Bản ghi dùng chung |
| 62 | `common_config.view` | Xem cấu hình chung | Xem cấu hình dùng chung của hệ thống | `GET /common-configs*`, `GET /common/configurations` |  |
| 63 | `common_config.edit` | Sửa cấu hình chung | Sửa cấu hình dùng chung. Cần phạm vi `all` | `/common-configs`, `PUT /common/configurations` | Bản ghi dùng chung |
| 64 | `audit.view` | Xem nhật ký thao tác | Xem nhật ký thao tác trong phạm vi ADV của mình | `GET /audits` |  |
| 65 | `login_history.view` | Xem lịch sử đăng nhập | Xem lịch sử đăng nhập của nhân sự | `/audits/login-histories` |  |
| 66 | `staff.view` | Xem nhân sự | Danh sách và chi tiết nhân sự có phạm vi giao với phạm vi của mình; không thấy root | Nhân viên — `GET /staffs` |  |
| 67 | `staff.invite` | Mời nhân sự | Mời, mời hàng loạt, gửi lại, thu hồi lời mời — chỉ với vai trò và ADV không vượt quá mình | `/staffs/invite`, `/bulk-invite`, `/:id/resend-invite`, `/:id/revoke-invite` | Ràng buộc PQ-011 |
| 68 | `staff.edit` | Sửa nhân sự | Đổi vai trò, phạm vi, hạn dùng, thông tin; bật/tắt tài khoản — chỉ nhân sự nằm trọn trong phạm vi mình | `/staffs/:id/update-info`, `/:id/status` | Ràng buộc PQ-011 |

Tổng: **68 quyền**.

**Không có mã quyền — chỉ root:**

| Nhóm | Gồm | Vì sao |
|---|---|---|
| Vai trò & phân quyền | Tạo, sửa, ngừng vai trò; tick quyền | Ai sửa được vai trò thì tự nâng được quyền |
| ADV | Tạo, sửa, ngừng hoạt động ADV | Chạm site đang chạy của thương hiệu |
| Can thiệp tài khoản người dùng | Khoá, mở khoá, hợp đồng điện tử, eKYC, tạo người dùng | Cắt thu nhập; giấy tờ pháp lý |
| Xác thực tài khoản | `/identifications` | Ảnh hưởng xuyên ADV |
| Thưởng sự kiện | Đổi trạng thái, xoá (`/event-reward`); huỷ, chạy lại tính thưởng | 💰 |
| Nhân sự đặc biệt | Bật cờ root; đặt phạm vi `all`; đặt lại mật khẩu người khác; tạo nhân sự kiểu cũ (đặt sẵn mật khẩu) | Chống tự nâng quyền; dự phòng khi email lỗi |
| Công cụ kỹ thuật | `/migration/*`, `/migration/backfill-*`, `/common/update-event-daily`, `/events/run-analytic-daily`, `/events/migrate-category-ead`; các route cập nhật hàng loạt dưới `/contents` (Q9) | Không phải công cụ vận hành |

**`public`** (không cần quyền): đăng nhập, nhận lời mời, quên và đặt lại mật khẩu, `/staffs/me`, đổi mật khẩu của
chính mình, `GET /partners` (danh sách ADV cho ô chọn — tự lọc theo phạm vi).

Điều kiện kiểu "config_editor phải gắn ADV" là điều kiện **phạm vi**, không thành mã quyền — thay bằng luật "phạm vi
rỗng thì từ chối" ở 5.2.

### 5.4 Vai trò → mã quyền

| Vai trò | Mã | Số quyền | Phạm vi gợi ý |
|---|---|---|---|
| Quản lý vận hành | `ops_manager` | 28 | `list` — ADV mình phụ trách |
| Vận hành nội dung | `ops_content` | 13 | `list` |
| Vận hành hiệu suất | `ops_performance` | 17 | `list` |
| Duyệt chi | `payout_approver` | 12 | Q6 |
| Kỹ thuật hỗ trợ | `tech_support` | 27 | `all` |
| Cấu hình ứng dụng | `config_editor` | 19 | `list`, ít nhất 1 ADV |
| Cộng tác viên | `collaborator` | 6 | `list` |
| Admin | `admin` | 62 | `list`; `all` cho nhân sự VFDC (Q3) |

Mã vai trò mới là đề xuất; tên hiển thị root sửa được, mã thì không. Cột Admin, CTV, Cấu hình ứng dụng = hành vi hôm
nay (Phụ lục A) trừ các ô đổi hành vi có chủ đích (PQ-11).

Ký hiệu: ✔ có · M0 có từ Mốc 0 (PQ-04) · ô trống: không có · Q*n*: chờ câu hỏi ở mục 12.

| # | Mã quyền | Quản lý vận hành | Vận hành nội dung | Vận hành hiệu suất | Duyệt chi | Kỹ thuật hỗ trợ | Cấu hình ứng dụng | Cộng tác viên | Admin |
|---|---|---|---|---|---|---|---|---|---|
| | **Nội dung** | | | | | | | | |
| 1 | `content.view` | ✔ | ✔ | ✔ |  | ✔ |  | ✔ | ✔ |
| 2 | `content.moderate` | ✔ | ✔ |  |  |  |  | ✔ | ✔ |
| 3 | `content_manual_flow.view` | ✔ | ✔ |  |  | ✔ |  | ✔ | ✔ |
| 4 | `content_manual_flow.edit` | ✔ | ✔ |  |  |  |  | ✔ | ✔ |
| | **Người dùng và creator** | | | | | | | | |
| 5 | `user.view_contact` | ✔ | ✔ |  |  |  |  |  | M0 |
| 6 | `creator.view` | ✔ | ✔ | ✔ | ✔ | ✔ |  |  | ✔ |
| 7 | `creator.edit` |  |  |  |  |  |  |  | ✔ |
| 8 | `creator.approve` | ✔ | ✔ |  |  |  |  |  | ✔ |
| 9 | `partner_member.approve` | ✔ | ✔ |  |  |  |  |  | ✔ |
| 10 | `user_partner.view` |  |  |  |  | ✔ |  |  | ✔ |
| 11 | `user_partner.edit_staff_status` |  |  |  |  |  |  |  | ✔ |
| 12 | `user.edit_partner_data` |  |  |  |  |  |  |  | Q10 |
| | **Sự kiện và thống kê** | | | | | | | | |
| 13 | `event.view` | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 14 | `event.view_detail` | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |  | ✔ |
| 15 | `event.edit` |  |  |  |  |  | ✔ |  | ✔ |
| 16 | `event_schema.view` |  |  |  |  | ✔ | ✔ |  | ✔ |
| 17 | `event_schema.edit` |  |  |  |  |  | ✔ |  | ✔ |
| 18 | `statistic.view` | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |  | ✔ |
| | **Thưởng, nhiệm vụ, quà** | | | | | | | | |
| 19 | `bonus.view` | ✔ |  | ✔ | ✔ | ✔ |  |  | ✔ |
| 20 | `bonus.edit` | ✔ |  | ✔ |  |  |  |  | ✔ |
| 21 | `bonus.import` | ✔ |  | ✔ |  |  |  |  | ✔ |
| 22 | `bonus.cancel` | ✔ |  | ✔ |  |  |  |  | ✔ |
| 23 | `mission.view` |  |  |  |  | ✔ |  |  | ✔ |
| 24 | `mission.edit` |  |  |  |  |  |  |  | ✔ |
| 25 | `mission.approve` |  |  |  |  |  |  |  | ✔ |
| 26 | `gift.view` |  |  |  |  | ✔ |  |  | ✔ |
| 27 | `gift.edit` |  |  |  |  |  |  |  | ✔ |
| | **Đối soát, rút tiền, dữ liệu xuất** | | | | | | | | |
| 28 | `reconciliation.view` | ✔ |  | ✔ | ✔ | ✔ |  |  | ✔ |
| 29 | `reconciliation.cancel_item` | ✔ |  | ✔ |  |  |  |  | ✔ |
| 30 | `reconciliation.change_status` |  |  |  | ✔ |  |  |  | ✔ |
| 31 | `reconciliation.export` | ✔ |  | ✔ | ✔ |  |  |  | ✔ |
| 32 | `transfer.view` | ✔ |  | ✔ | ✔ | ✔ |  |  | ✔ |
| 33 | `transfer.export` | ✔ |  | ✔ | ✔ |  |  |  | ✔ |
| 34 | `transfer.change_status` |  |  |  | ✔ |  |  |  | ✔ |
| 35 | `export.view` | ✔ |  | ✔ | ✔ |  |  |  | ✔ |
| | **Phân khúc, mã, thông báo, danh mục** | | | | | | | | |
| 36 | `segment.view` |  |  |  |  | ✔ |  |  | ✔ |
| 37 | `segment.edit` |  |  |  |  |  |  |  | ✔ |
| 38 | `user_segment.view` |  |  |  |  | ✔ |  |  | ✔ |
| 39 | `user_segment.edit` |  |  |  |  |  |  |  | ✔ |
| 40 | `user_segment.import` |  |  |  |  |  |  |  | ✔ |
| 41 | `code.view` |  |  |  |  | ✔ |  |  | ✔ |
| 42 | `code.edit` |  |  |  |  |  |  |  | ✔ |
| 43 | `code.import` |  |  |  |  |  |  |  | ✔ |
| 44 | `notification.view` |  |  |  |  | ✔ |  |  | ✔ |
| 45 | `notification.edit` |  |  |  |  |  |  |  | ✔ |
| 46 | `notification.approve` |  |  |  |  |  |  |  | ✔ |
| 47 | `category.view` | ✔ | ✔ | ✔ |  | ✔ | ✔ |  | ✔ |
| 48 | `category.edit` |  |  |  |  |  |  |  | ✔ |
| | **Cấu hình ADV và nội dung site** | | | | | | | | |
| 49 | `app_config.view` |  |  |  |  | ✔ | ✔ |  | ✔ |
| 50 | `app_config.edit` |  |  |  |  |  | ✔ |  | ✔ |
| 51 | `app_config.publish` |  |  |  |  |  | ✔ |  | ✔ |
| 52 | `news.view` |  |  |  |  | ✔ | ✔ |  | ✔ |
| 53 | `news.edit` |  |  |  |  |  | ✔ |  | ✔ |
| 54 | `article.view` |  |  |  |  | ✔ | ✔ |  | ✔ |
| 55 | `article.edit` |  |  |  |  |  | ✔ |  | ✔ |
| 56 | `quick_action.view` |  |  |  |  | ✔ | ✔ |  |  |
| 57 | `quick_action.edit` |  |  |  |  |  | ✔ |  |  |
| 58 | `affiliate.view` |  |  |  |  | ✔ | ✔ |  | ✔ |
| 59 | `affiliate.edit` |  |  |  |  |  | ✔ |  | ✔ |
| | **Hệ thống** | | | | | | | | |
| 60 | `tag.view` | ✔ | ✔ | ✔ |  | ✔ | ✔ | ✔ | ✔ |
| 61 | `tag.edit` |  |  |  |  |  |  |  | ✔ |
| 62 | `common_config.view` |  |  |  |  | ✔ |  |  | ✔ |
| 63 | `common_config.edit` |  |  |  |  |  |  |  | ✔ |
| 64 | `audit.view` | ✔ |  |  |  | ✔ |  |  | ✔ |
| 65 | `login_history.view` | ✔ |  |  |  | ✔ |  |  | ✔ |
| 66 | `staff.view` | ✔ |  |  |  |  |  |  |  |
| 67 | `staff.invite` | ✔ |  |  |  |  |  |  |  |
| 68 | `staff.edit` | ✔ |  |  |  |  |  |  |  |

**Kiểm tra tách lập / duyệt:** không vai trò nào ngoài Admin có cùng lúc một quyền nhóm *lập*
(`bonus.edit`, `bonus.import`, `bonus.cancel`, `reconciliation.cancel_item`) và một quyền nhóm *duyệt*
(`reconciliation.change_status`, `transfer.change_status`). Màn Vai trò & phân quyền chặn lưu vai trò vi phạm luật
này (PQ-12).

---

## 6. Phạm vi

### 6.1 Trong phạm vi

- Gỡ root tạm sớm trên vai trò Admin hiện có (Mốc 0)
- Chụp ma trận quyền hiện tại làm mốc so sánh
- Phạm vi ADV đọc từ DB; principal nạp mỗi request; token chỉ giữ `_id`
- Danh mục quyền chức năng; registry route kèm mã quyền; cổng `RequirePermission`
- Menu và nút theo danh sách quyền
- Màn **Vai trò & phân quyền**
- Gieo quyền cho ba vai trò hiện có bằng migration; gieo năm vai trò mới
- Một luật phạm vi ADV duy nhất, fail-closed, hai dạng `all` / `list`
- Lời mời chọn vai trò, phạm vi, hạn dùng
- Nhật ký đủ người, hành động, ADV; ghi lượt xem dữ liệu cá nhân và mọi thay đổi vai trò
- Đóng 60 endpoint chỉ cần đăng nhập; CI kiểm ma trận
- Còn một root; quy trình khôi phục root khẩn cấp; cảnh báo root đăng nhập

### 6.2 Ngoài phạm vi

- **External API** (`/api/admin/external-api`, 20 route, cổng `CheckKeyAuth`) — tách ticket riêng (mục 11). Mục tiêu
  "một root" trong tài liệu này là root **người dùng**
- Gán quyền lẻ cho một người; nhiều vai trò trên một người
- Vai trò khác nhau theo từng ADV: một người có một vai trò, áp như nhau cho mọi ADV trong phạm vi
- Phân quyền theo trường dữ liệu
- Tạo mã quyền mới từ màn hình — quyền mới đi cùng mã nguồn
- Đổi thời hạn token 8 giờ
- Đổi quy trình nghiệp vụ đối soát, rút tiền, thưởng. Ai được bấm thì đổi; **bấm xong ra gì thì giữ nguyên**
- Phân quyền cho app creator và các site white-label

---

## 7. Yêu cầu chức năng

Sắp theo mốc ở mục 10.

### Mốc 0 — Gỡ root tạm

#### PQ-01 — Đọc phạm vi ADV từ DB

**Vì sao cần.** PQ-02 cho nhân sự gắn nhiều ADV, nhưng phạm vi ADV đang đọc từ claim `partner` trong JWT — chỉ chứa
được một ADV.

**Yêu cầu**

- Middleware `Auth` đọc nhân sự từ DB và dựng `StaffInfo` từ đó (phạm vi `all` / `list`, `isRoot`), không từ claim
  của token
- Ba hàm `StaffInfo` (`AssignPartnerForStaff`, `IsPermissionAllPartner`, `IsAllowPartner`) sửa **bên trong** để hiểu
  phạm vi `list` (lọc `$in`); 78 chỗ gọi giữ nguyên chữ ký
- Cổng vai trò (`IsAdmin`…) giữ nguyên ở Mốc 0
- Phần còn lại (principal, token chỉ giữ `_id`) làm ở PQ-07, dựng tiếp trên phần này

**Phương án dự phòng** nếu phần này quá lớn cho Mốc 0: ghi danh sách ADV vào token thay claim `partner`, đổi phạm vi
thì gọi `resetToken` (người dùng đăng nhập lại, như hôm nay). Khi đó PQ-07 phải sửa lại phần token.

**Nghiệm thu**

- [ ] Nhân sự `list` 3 ADV: màn danh sách và màn chi tiết đều thấy đúng 3 ADV
- [ ] Sửa phạm vi trực tiếp trong DB, không xoá token: lần gọi kế tiếp áp phạm vi mới

#### PQ-02 — Nhân sự phụ trách nhiều ADV, phạm vi `all` / `list`

**Vì sao cần.** Đây là lý do thật khiến Manager phải mượn root. Bật cờ root còn xoá luôn ô ADV và ô vai trò, nên
không có "root của 2 ADV".

**Yêu cầu**

- Bản ghi nhân sự có phạm vi theo 5.2
- Màn Nhân viên và màn mời chọn được nhiều ADV; chỉ root thấy lựa chọn `all`
- Chuyển dữ liệu:
  - Nhân sự đang gắn một ADV → `list` một phần tử
  - Nhân sự không gắn ADV, không phải root (đang được hiểu là toàn quyền) → `all` hoặc `list` theo danh sách biz
    xác nhận (Q3)
- Bỏ trường `type`

**Nghiệm thu**

- [ ] Tài khoản `list` 3 ADV thao tác được đúng 3; ADV thứ tư trả "ADV ngoài phạm vi"
- [ ] Tạo ADV mới: tài khoản `all` thấy ngay, tài khoản `list` không thấy
- [ ] Nhân sự không phải root không đặt được `all`, kể cả qua API
- [ ] Đối chiếu trước/sau từng tài khoản: không ai mất hay thừa ADV ngoài danh sách biz xác nhận

#### PQ-03 — Một luật phạm vi ADV duy nhất, fail-closed

**Vì sao cần.** Mục 2.3: bốn luật, khoảng 95 chỗ gọi, trả lời ngược nhau.

**Yêu cầu**

- Một hàm duy nhất, lấy `CanEditAppConfig` làm khuôn, cài đúng luật ở 5.2 (một ADV, nhiều ADV, dùng chung)
- Đọc phạm vi từ DB: Mốc 0 qua `StaffInfo` (PQ-01); từ Mốc 1 qua principal (PQ-07)
- **Mốc 0:** áp cho service của các việc vận hành — đối soát, rút tiền, thưởng thêm, dữ liệu xuất, chi tiết người
  dùng
- **Mốc 1:** thay nốt toàn bộ — `AssignPartnerForStaff`, `IsPermissionAllPartner`, `IsAllowPartner`,
  `StaffCanReachPartner`, `AssignPartnerWithNonExistsPartnerForStaff`, các so sánh thô (kể cả viết qua `.Hex()` hay
  biến trung gian)
- Danh sách và chi tiết dùng chung một luật

**Nghiệm thu**

- [ ] Nhân sự `list` rỗng: mọi màn liệt kê không trả bản ghi nào
- [ ] Mọi bản ghi thấy trong danh sách đều mở được chi tiết (nếu có quyền xem)
- [ ] Hết Mốc 1: không còn năm hàm cũ và không còn so sánh `Staff.Partner` trong `pkg/admin/service`
- [ ] Root không đổi hành vi

#### PQ-04 — Mở xem liên hệ creator cho Admin

- `GET /users/:id`, `GET /users/:id/socials` chuyển từ `IsRoot` sang Admin, trong phạm vi ADV (PQ-03)
- Khoá, hợp đồng, eKYC, tạo người dùng giữ `IsRoot`
- Mỗi lượt mở chi tiết ghi nhật ký (mức tối thiểu của PQ-17)
- Từ Mốc 2, hai endpoint này chuyển sang quyền `user.view_contact`

**Nghiệm thu:** Admin mở được chi tiết creator trong ADV mình; gõ id creator ADV khác bị chặn; mỗi lượt mở có một dòng
nhật ký.

#### PQ-05 — Thu hồi root tạm, còn một root

**Yêu cầu**

- Trưởng nhóm vận hành chuyển sang tài khoản Admin gắn các ADV mình phụ trách; tài khoản root tạm bị tắt
- Root **không** bị áp hạn dùng — một root duy nhất mà có hạn thì có thể tự khoá hệ thống
- **Quy trình khôi phục root khẩn cấp** bằng văn bản: script tạo hoặc khôi phục root chạy trực tiếp trên DB; ai được
  chạy; ghi lại ở đâu; sau khi dùng phải làm gì (Q8)
- Mỗi lần root đăng nhập gửi cảnh báo về kênh AT chỉ định (Q8)
- Màn Nhân viên hiện số tài khoản root; cảnh báo khi khác 1

**Nghiệm thu**

- [ ] Số nhân sự `isRoot = true` đang hoạt động trên production: **đúng 1**
- [ ] Lịch sử đăng nhập root 7 ngày liên tiếp sau Mốc 0: **0 lượt phục vụ vận hành**; lượt nào cũng có cảnh báo và
  lý do ghi lại
- [ ] Chạy thử quy trình khôi phục trên staging: khôi phục được root trong thời gian quy trình đề ra

### Mốc 1 — Nền phân quyền (không đổi hành vi)

#### PQ-06 — Chụp ma trận quyền hiện tại làm mốc

**Vì sao cần.** Không có mốc thì không nghiệm thu được "không ô nào đổi" ở PQ-11. Đây cũng là đầu vào estimate chính
xác nhất.

**Yêu cầu**

- Bộ test gọi mọi route admin với mọi tổ hợp **(root, Admin, CTV, Cấu hình ứng dụng) × (chưa gắn ADV, gắn ADV đúng,
  gắn ADV khác)**, ghi kết quả cho phép / chặn
- Chạy trên `develop` **trước** mọi thay đổi của Mốc 1; lưu kết quả vào repo làm bảng mốc
- Là việc đầu tiên của Mốc 1; làm được ngay, không chờ câu hỏi nào

**Nghiệm thu:** bảng mốc phủ đủ route admin trừ external API, chạy lại được trong CI.

#### PQ-07 — Principal nạp mỗi request

**Vì sao cần.** Hạn dùng không có sự kiện nào xoá token đúng lúc; `Auth` không kiểm `active`; các cổng không kiểm
`role.active`.

**Yêu cầu**

- Dựng tiếp trên PQ-01
- `Auth` nạp **một principal** mỗi request: nhân sự, vai trò, tập quyền, phạm vi ADV, `active`, hạn dùng. Đặt vào
  context; mọi cổng và service đọc từ đó
- Token chỉ còn `_id` (và `exp`)
- Nhân sự `active = false`, quá hạn dùng, hoặc vai trò `active = false`: bị chặn ở `Auth`
- Gom đọc DB: hôm nay 2–3 lần `FindById` mỗi request, sau đổi còn 1. Nếu thêm cache ngắn thì xoá khi nhân sự hoặc
  vai trò thay đổi

**Nghiệm thu**

- [ ] Bỏ một ADV khỏi phạm vi: thao tác kế tiếp vào ADV đó bị chặn, **người dùng không bị đăng xuất**
- [ ] Đặt hạn dùng vào 1 phút sau: hết phút đó thao tác kế tiếp bị chặn
- [ ] Không service nào còn đọc claim `partner` / `isRoot` từ token

#### PQ-08 — Danh mục quyền chức năng

- Một danh mục duy nhất trong mã: mã, nhãn tiếng Việt, nhóm, mô tả, cờ "liên quan tiền" — đúng bảng 5.3
- `GET /common/scopes` trả danh mục mới, gom theo nhóm
- Quyền chỉ root không có trong danh mục

**Nghiệm thu:** mọi menu (trừ nhóm chỉ root) có ít nhất một quyền xem; danh mục không còn mã kiểu `user_full`.

#### PQ-09 — Registry route và cổng `RequirePermission`

**Vì sao cần.** Echo không lưu middleware trong `e.Routes()`, nên không sinh được bảng endpoint → quyền từ mã nếu mỗi
route tự gắn middleware như hôm nay.

**Yêu cầu**

- Một lớp đăng ký route: mỗi route khai **đúng một** trong ba: mã quyền, `root`, hoặc `public`
- Cổng `RequirePermission(code)` đọc principal (PQ-07)
- Thay hết `IsAdmin`, `IsCollaborator`, `IsConfigEditor`, `IsAdminOrConfigEditor`, `HasAnyRole`
- Bảng endpoint → quyền **sinh từ registry**, là tài liệu bàn giao
- CI duyệt `e.Routes()`: route không có trong registry và không thuộc `public` hay external API → đỏ

**Nghiệm thu**

- [ ] Bỏ một quyền khỏi vai trò: endpoint tương ứng bị chặn ở lần gọi kế tiếp
- [ ] `pkg/admin/router` không còn so mã vai trò
- [ ] Thêm route không khai trong registry: CI đỏ

#### PQ-10 — Menu và nút theo quyền

- `/staffs/me` trả danh sách mã quyền và phạm vi
- `access.ts`, `routes.ts` tính từ danh sách quyền; không còn chuỗi `'admin'`, `'collaborator'`, `'config_editor'`
- Nút thao tác ẩn khi thiếu quyền; trang đích là menu đầu tiên có quyền xem
- Ẩn/hiện chỉ để màn sạch; chặn thật ở PQ-09

**Nghiệm thu:** vai trò chỉ có `reconciliation.view` đăng nhập chỉ thấy Đối soát, không thấy nút Huỷ.

#### PQ-11 — Gieo quyền bằng migration; danh sách đổi hành vi có chủ đích

**Yêu cầu**

- Tập quyền lưu ở trường mới trên bản ghi vai trò, chỉ chứa mã quyền. Trường `scopes` cũ không dùng, xoá ở Mốc 3
- Gieo bằng **migration chạy một lần, có đánh dấu phiên bản** qua khung `/migration/jobs`. Không sửa `GenerateRole()`
  để ghi đè lúc khởi động — làm vậy mỗi lần deploy sẽ xoá quyền root vừa tick
- Giữ nguyên `_id` và `code` của ba vai trò hiện có
- Tập quyền gieo cho ba vai trò hiện có = bảng mốc PQ-06, **trừ** danh sách dưới đây

**Danh sách đổi hành vi có chủ đích** — nguồn duy nhất; thay đổi ngoài danh sách là lỗi:

| Thay đổi | Ai bị ảnh hưởng | Mốc | Lý do |
|---|---|---|---|
| Nhân sự không gắn ADV chuyển sang `all` hoặc `list` | Theo Q3 | 0 | PQ-02 |
| Xem liên hệ creator mở cho Admin | Admin | 0 | PQ-04 |
| Thiếu quyền trả 403 thay vì 401 | Mọi vai trò | 1 | NFR-05 |
| Sửa tag, cấu hình chung cần phạm vi `all` | Admin phạm vi `list` | 1 | Bản ghi dùng chung (5.2) |
| Thưởng thêm cần `bonus.*` | CTV, Cấu hình ứng dụng | 3 | Hôm nay ai đăng nhập cũng tạo, nhập được thưởng |
| Duyệt creator / thành viên ADV cần quyền riêng | CTV, Cấu hình ứng dụng; Admin giữ quyền | 3 | Hôm nay ai đăng nhập cũng duyệt được |
| Danh sách người dùng (`GET /users`, `/partners/users`) cần `creator.view` | CTV, Cấu hình ứng dụng | 3 | Dữ liệu người dùng |
| `PUT /common/configurations` cần `common_config.edit` + phạm vi `all` | Mọi vai trò không phải root | 3 | Ghi cấu hình xuyên ADV |
| `PUT /partners/users/wildrift` cần `user.edit_partner_data` hoặc bị gỡ | Mọi vai trò không phải root | 3 | Q10 |
| Nhật ký `/audits` cần `audit.view`, lọc theo phạm vi | CTV, Cấu hình ứng dụng; nhân sự ADV khác | 3 | PQ-17 |
| `/migration/*` và công cụ kỹ thuật (5.3) chỉ root | Mọi vai trò không phải root; Admin mất `/events/run-analytic-daily` | 3 | Không phải công cụ vận hành |

**Nghiệm thu**

- [ ] Ma trận sau Mốc 1 so với bảng mốc PQ-06: mọi ô khác đều nằm trong danh sách trên
- [ ] Deploy lại nhiều lần: quyền root đã tick trên màn không bị ghi đè

### Mốc 2 — Vai trò mới và màn phân quyền

#### PQ-12 — Màn Vai trò & phân quyền

**Phần bắt buộc** — đây là thứ thay cho Role và Permission viết cứng:

- Menu **Vai trò & phân quyền**, chỉ root
- Danh sách vai trò: tên, mô tả, số quyền, số nhân sự đang dùng, trạng thái
- Màn sửa quyền của một vai trò: bảng tick theo nhóm chức năng × hành động; quyền 💰 được đánh dấu
- `edit` / `import` / `export` / `approve` kéo theo `view` cùng nhóm — **ép ở backend khi lưu**
- **Chặn lưu** vai trò vừa có quyền nhóm *lập* vừa có quyền nhóm *duyệt* khoản chi (5.4)
- Lưu hiện tóm tắt: thêm/bớt quyền nào, ảnh hưởng bao nhiêu người; có hiệu lực ở thao tác kế tiếp
- Mọi thay đổi ghi nhật ký

**Phần tuỳ Q4** — tạo vai trò mới trên màn:

- Tạo, **nhân bản**, ngừng dùng vai trò; tên không trùng (so không phân biệt hoa thường, bỏ dấu); `code` sinh tự
  động, không sửa được
- Không xoá được vai trò đang có người dùng; ngừng dùng thì phải chuyển hết nhân sự sang vai trò khác trước
- Vai trò có sẵn không xoá được, chỉ sửa quyền
- Nếu Q4 chốt "chưa": vai trò mới do DISO thêm bằng migration khi cần; root vẫn sửa được tập quyền của mọi vai trò

**Nghiệm thu**

- [ ] Root bỏ một quyền khỏi vai trò đang dùng: mọi người mang vai trò đó bị chặn ở thao tác kế tiếp
- [ ] Gọi API lưu vai trò có `edit` mà thiếu `view`: backend tự thêm `view` hoặc từ chối
- [ ] Lưu vai trò có cả `bonus.edit` và `transfer.change_status`: bị từ chối
- [ ] Nhân sự không phải root không gọi được API sửa vai trò
- [ ] *(nếu Q4 đồng ý)* Tạo vai trò trùng tên khác hoa thường hoặc dấu: bị từ chối

#### PQ-13 — Năm vai trò mới làm đúng việc

Các việc vận hành và vai trò làm:

| Việc | Vai trò | Quyền | Yêu cầu riêng | Nghiệm thu |
|---|---|---|---|---|
| Liên hệ creator | Vận hành nội dung, Quản lý vận hành | `user.view_contact` | Khoá, hợp đồng, eKYC không hiện và API chặn | Gõ id creator ngoài phạm vi: bị chặn. Mỗi lượt xem có nhật ký |
| Cộng thưởng cho creator (Thưởng thêm) | Vận hành hiệu suất, Quản lý vận hành | `bonus.edit`, `bonus.import`, `bonus.cancel` | Nhập Excel có dòng ngoài phạm vi: dòng đó bị từ chối kèm lý do, dòng hợp lệ vẫn vào | File trộn hai ADV xử lý đúng |
| Huỷ nội dung, mốc thưởng trong đối soát | Vận hành hiệu suất, Quản lý vận hành | `reconciliation.cancel_item` | Đủ bốn tab chi tiết; huỷ kèm lý do | Không tab nào trắng; thống kê bản đối soát cập nhật sau huỷ |
| Tải file đối soát, file rút tiền | Vận hành hiệu suất, Quản lý vận hành, Duyệt chi | `reconciliation.export`, `transfer.export` | Yêu cầu xuất luôn mang ADV; không sinh được file trộn nhiều ADV từ tài khoản không phải `all` | Id file ngoài phạm vi: bị chặn |
| Xem file rút tiền | Vận hành hiệu suất, Quản lý vận hành, Duyệt chi | `transfer.view` | Chi tiết đợt rút và danh sách lệnh rút bên trong | Đợt rút ngoài phạm vi: bị chặn |
| Chốt đối soát; duyệt, từ chối rút tiền | Duyệt chi | `reconciliation.change_status`, `transfer.change_status` | — | Thực hiện được trong phạm vi ADV được giao |

**Nghiệm thu theo vai trò**

- [ ] **Vận hành nội dung** gọi thẳng bất kỳ API tiền nào (thưởng thêm, đối soát, rút tiền): bị chặn
- [ ] **Vận hành hiệu suất** gọi API duyệt nội dung, duyệt creator, xem liên hệ creator: bị chặn
- [ ] **Quản lý vận hành** chỉ mời hoặc đổi người sang Vận hành nội dung, Vận hành hiệu suất; gọi API duyệt chi: bị chặn
- [ ] **Duyệt chi** gọi API tạo, sửa, huỷ thưởng hoặc huỷ mục đối soát: bị chặn
- [ ] **Kỹ thuật hỗ trợ** gọi lần lượt mọi API ghi (theo registry): tất cả bị chặn; API tải file và xem liên hệ
  creator: bị chặn; đọc được dữ liệu mọi ADV, gồm ADV tạo sau khi gán vai trò
- [ ] Ngoài root và Admin, **không tài khoản nào** vừa có quyền lập vừa có quyền duyệt khoản chi — kiểm bằng truy vấn
  trên production sau khi gán vai trò

#### PQ-14 — Mời nhân sự đúng vai trò, có hạn dùng

- Lời mời chọn: vai trò, phạm vi, **ngày hết hiệu lực** (trống = không hạn)
- Hạn dùng áp cho mọi vai trò **trừ root**
- Quá hạn: không đăng nhập được; phiên đang mở bị chặn ở thao tác kế tiếp (nhờ PQ-07)
- Màn Nhân viên sửa được ngày này, lọc tài khoản sắp hết hạn
- Tắt tài khoản: giữ nguyên cơ chế `resetToken` hiện có — đã có hiệu lực ngay
- Không cấp vai trò Admin cho người mới (ô chọn vai trò khi mời không có Admin; root vẫn đổi được cho người cũ)

**Nghiệm thu**

- [ ] Mời một người với vai trò Vận hành hiệu suất + 2 ADV: nhận lời mời xong dùng được đúng 2 ADV
- [ ] Đặt hạn vào hôm qua: không đăng nhập được, phiên đang mở bị chặn
- [ ] Không đặt được hạn dùng cho root

### Mốc 3 — Đóng rủi ro

#### PQ-15 — Không endpoint nào "chỉ cần đăng nhập"

- Mỗi endpoint trong 60 endpoint ở 2.1 được khai trong registry (PQ-09) với mã quyền hoặc `root`
- `/migration/*` và backfill: `root`, hoặc đưa ra khỏi API công khai
- Thay đổi hành vi đi theo danh sách ở PQ-11

**Nghiệm thu**

- [ ] Đăng nhập CTV, gọi 60 endpoint: chỉ qua những endpoint có trong vai trò CTV
- [ ] Không endpoint `/migration/*` nào gọi được bằng tài khoản không phải root

#### PQ-16 — Chỉ root và chống tự nâng quyền

- Các nhóm chỉ root ở 5.3 không có mã quyền
- Tag và cấu hình chung **không** chỉ root: dùng `tag.edit`, `common_config.edit` kèm phạm vi `all`

**Quyền nhân sự:**

| Quyền | Làm được | Không làm được |
|---|---|---|
| `staff.view` | Xem nhân sự có phạm vi giao với phạm vi của mình | Xem root |
| `staff.invite` | Mời, mời hàng loạt, gửi lại, thu hồi lời mời | Mời với vai trò hoặc ADV vượt quá mình |
| `staff.edit` | Đổi vai trò, phạm vi, hạn dùng, thông tin; bật/tắt tài khoản | Đặt lại mật khẩu người khác; sửa root; sửa chính mình |

Ràng buộc gán vai trò:

- **Quản lý vận hành** chỉ gán được danh sách cố định: **Vận hành nội dung**, **Vận hành hiệu suất**
- Vai trò khác nếu được cấp `staff.invite` / `staff.edit` (qua màn phân quyền): chỉ gán vai trò có tập quyền nằm trong
  tập quyền của mình
- Chỉ gán ADV nằm trong phạm vi của mình; không gán `all`
- Chỉ sửa nhân sự có phạm vi nằm trọn trong phạm vi của mình; không sửa chính mình, không sửa root

**Nghiệm thu**

- [ ] Không có mã quyền nào cho các nhóm chỉ root
- [ ] Quản lý vận hành mở ô chọn vai trò: chỉ thấy Vận hành nội dung và Vận hành hiệu suất
- [ ] Quản lý vận hành mời người với vai trò Duyệt chi, hoặc ADV ngoài phạm vi: bị chặn

#### PQ-17 — Nhật ký thao tác

`AuditRaw` hôm nay chỉ có `targetId`, `data`, `message`, `staff`, `createdAt`, `batchId`.

**Yêu cầu**

- Thêm trường **hành động** (danh mục có sẵn) và **ADV**
- Index phục vụ lọc theo người, hành động, ADV, thời gian
- Ghi: các việc ở PQ-13, **mỗi lượt xem** liên hệ creator, mọi thay đổi vai trò / quyền / phạm vi / hạn dùng
- Dòng cũ không có ADV: hiển thị "không rõ ADV"; không bắt buộc backfill
- Đọc nhật ký cần `audit.view`, trong phạm vi ADV; root xem toàn bộ
- Không xoá, không sửa nhật ký từ giao diện

**Nghiệm thu**

- [ ] Mỗi việc ở PQ-13 và mỗi lần sửa vai trò: đủ người, hành động, bản ghi, ADV, thời gian
- [ ] Nhân sự ADV A không đọc được nhật ký ADV B
- [ ] Lọc theo người, hành động, ADV ra đúng trên dữ liệu cỡ production trong thời gian chấp nhận được

---

## 8. Yêu cầu phi chức năng

**NFR-01 — Không làm hỏng cái đang chạy.** Ma trận sau mỗi mốc so với bảng mốc PQ-06; mọi ô khác phải nằm trong danh
sách đổi hành vi có chủ đích (PQ-11).

**NFR-02 — Thiếu cấu hình thì từ chối.** Không vai trò, vai trò ngừng dùng, phạm vi `list` rỗng, hết hạn — đều bị
chặn. `all` chỉ root đặt được.

**NFR-03 — Không rò dữ liệu chéo ADV.** Mọi màn liệt kê, chi tiết, file xuất, dòng nhật ký nằm trong phạm vi.

**NFR-04 — Chặn nằm ở backend.** Nghiệm thu bằng gọi API trực tiếp, không bằng bấm giao diện.

**NFR-05 — Mã lỗi và thông báo.** Thiếu quyền hoặc ngoài phạm vi trả **403**, kèm thông báo tiếng Việt phân biệt
*thiếu quyền* (tên quyền) với *ADV ngoài phạm vi*. **Giữ 401** cho token hỏng, hết hạn, tài khoản bị tắt. Frontend
(`admin/src/utils/request.ts`) hiển thị thông báo 403 và **không** đăng xuất người dùng.

**NFR-06 — Đổi quyền có hiệu lực ngay, không đăng xuất.** Nhờ PQ-07. Có cache thì xoá khi nhân sự hoặc vai trò đổi.

**NFR-07 — CI kiểm ma trận.** Registry route và test ma trận chạy mỗi PR.

**NFR-08 — Tài liệu bàn giao sinh từ mã.** Bảng endpoint → quyền và vai trò → quyền.

---

## 9. Phụ thuộc và giả định

1. Biz gửi **danh sách nhân sự, vai trò, ADV từng người** trước Mốc 0 — đặc biệt nhân sự không gắn ADV hôm nay (Q3).
2. Biz duyệt mục 4 và chốt Q5, Q6, Q7 trước Mốc 2.
3. Đổi bản ghi nhân sự và vai trò cần migration trên production, ngoài giờ vận hành, có bản lùi.
4. Số ADV hiện là 14 và còn tăng; phạm vi `all` đảm bảo ADV mới không cần gán tay cho đội kỹ thuật và nhân sự VFDC.
5. AT chỉ định kênh nhận cảnh báo root đăng nhập và người được chạy quy trình khôi phục root (Q8).

---

## 10. Mốc giao hàng

| Mốc | Gồm | Kết quả | Điều kiện xong |
|---|---|---|---|
| **0. Gỡ root tạm** | PQ-01, PQ-02, PQ-03 (phần việc vận hành), PQ-04, PQ-05, nhật ký tối thiểu | Trưởng nhóm vận hành dùng Admin gắn nhiều ADV; root tạm bị tắt | Số root = 1; 7 ngày không dùng root cho vận hành |
| **1. Nền** | PQ-06 (đầu tiên), PQ-07, PQ-08, PQ-09, PQ-10, PQ-11, PQ-03 (phần còn lại) | Không đổi hành vi ngoài danh sách có chủ đích | Ma trận khớp bảng mốc |
| **2. Vai trò mới** | PQ-12, PQ-13, PQ-14 | Năm vai trò mới chạy; trưởng nhóm chuyển sang Quản lý vận hành | Biz nghiệm thu PQ-13 |
| **3. Đóng rủi ro** | PQ-15, PQ-16, PQ-17 đầy đủ, xoá trường `scopes` cũ | Không còn endpoint chỉ cần đăng nhập | CI kiểm ma trận |

**Mốc 0 cấp thừa gì:** Admin có quyền chốt đối soát và duyệt rút tiền — trưởng nhóm vận hành không xin, và trái
nguyên tắc tách lập / duyệt. Phần thừa này nhỏ hơn root nhiều (không có các việc chỉ root, không chạm ADV ngoài phạm
vi) và kết thúc ở Mốc 2 khi chuyển sang Quản lý vận hành. Nếu biz không chấp nhận (Q1): Mốc 0 gộp vào Mốc 2, root tạm
giữ tới hết Mốc 2.

**Đề xuất cho tuần tới:** PQ-06 (không chờ câu hỏi nào) và Mốc 0 (cần Q1, Q2, Q3).

---

## 11. Ticket tách riêng

**External API — ký và phân quyền.** 20 route `/api/admin/external-api` dùng một cặp client-id/secret chung cho mọi
ADV, gồm tạo và đổi trạng thái đối soát, tạo và đổi trạng thái đợt rút. Chữ ký HMAC chỉ phủ `clientID|traceNo|time`
(`router/routeauth/external_auth.go:90`), không phủ body; không kiểm trace-no đã dùng. Cần: chữ ký phủ body, chống gửi
lại, key theo từng client hoặc ADV, nhật ký ghi `client:<id>`. Phải thống nhất với AT Core vì backend dùng cùng kiểu
ký khi gọi sang AT (`internal/module/core/client.go:42`).

---

## 12. Quyết định cần chốt

| # | Câu hỏi | Đề xuất | Ai chốt | Chặn |
|---|---|---|---|---|
| Q1 | Chấp nhận Mốc 0 (trưởng nhóm dùng Admin gắn nhiều ADV, tạm có quyền duyệt chi tới hết Mốc 2) để gỡ root tạm sớm? | Đồng ý | Biz | Mốc 0 |
| Q2 | Tài khoản root tạm đã quá hạn hẹn 30/9. Gia hạn bằng văn bản tới khi Mốc 0 nghiệm thu, hay tắt ngay và các việc cần root nhờ root của AT làm hộ? | Gia hạn có văn bản, kèm cảnh báo đăng nhập | AT | Ngay |
| Q3 | Nhân sự không gắn ADV hôm nay: ai được giao "mọi ADV", ai giao danh sách cụ thể? | Rà từng người | Biz | Mốc 0 |
| Q4 | Root có tự tạo vai trò mới trên màn hình không, hay khi cần vai trò mới thì DISO thêm bằng migration? | Chưa cần ở đợt này; root vẫn sửa được tập quyền của mọi vai trò | AT | Mốc 2 (phạm vi PQ-12) |
| Q5 | Vận hành hiệu suất có làm phần lập khoản tiền (cộng thưởng, huỷ mục đối soát, tải file) không? | Có | Biz | Mốc 2 |
| Q6 | Ai giữ vai trò Duyệt chi? Giao theo từng ADV hay mọi ADV? | — | Biz | Mốc 2 |
| Q7 | Nhiệm vụ, duyệt điểm nhiệm vụ, quà, phân khúc, mã, thông báo admin, sửa hồ sơ creator, trạng thái CBNV, sửa danh mục, tag, cấu hình chung: hôm nay chỉ Admin làm. Sau này đội nào làm? | Giữ ở Admin tới khi biz chỉ định | Biz | Không |
| Q8 | Kênh nhận cảnh báo root đăng nhập; người được chạy quy trình khôi phục root | — | AT | Mốc 0 |
| Q9 | Các route cập nhật hàng loạt dưới `/contents` (`/update-status-data-contents`, `/update-warning-tags-content`): công cụ vận hành hay công cụ kỹ thuật? | DISO phân loại khi dựng registry | DISO | Mốc 1 |
| Q10 | `PUT /partners/users/wildrift` còn dùng không? | Không dùng thì gỡ | DISO | Mốc 3 |

---

## Phụ lục A — Hiện trạng quyền của ba vai trò

Đọc từ middleware tầng router, `develop` `b3a91953`, theo nhóm chức năng. Đây là thứ PQ-11 giữ nguyên khi gieo quyền,
trừ các ô trong danh sách đổi hành vi có chủ đích. Ma trận chính xác theo endpoint và trạng thái ADV lấy từ PQ-06.

Ký hiệu: ✔ gọi được · — bị chặn · **∀** chỉ cần đăng nhập (mọi vai trò gọi được — sẽ đóng ở PQ-15) · **ADV** chỉ khi
nhân sự gắn ADV và bản ghi thuộc ADV đó

| Nhóm chức năng | Route | Admin | CTV | Cấu hình ứng dụng | Root |
|---|---|---|---|---|---|
| Nội dung — xem, duyệt, ghim, gắn tag | `/contents` | ✔ | ✔ | — | ✔ |
| Luồng nội dung thủ công | `/content-manual-flows` | ✔ | ✔ | — | ✔ |
| Người dùng — danh sách | `GET /users` | ∀ | ∀ | ∀ | ✔ |
| Người dùng — chi tiết, kênh MXH | `/users/:id`, `/:id/socials` | — | — | — | ✔ |
| Người dùng — khoá, hợp đồng, eKYC, tạo | `/users/*` | — | — | — | ✔ |
| Duyệt creator / thành viên ADV | `/users/approval-*` | ∀ | ∀ | ∀ | ✔ |
| Người dùng ADV — trạng thái CBNV | `/user-partners` | ✔ | — | — | ✔ |
| Hồ sơ creator — xem, sửa, điều kiện | `/creator-profiles` | ✔ | — | — | ✔ |
| Sự kiện — danh sách | `GET /events` | ✔ | ✔ | ✔ | ✔ |
| Sự kiện — chi tiết, tạo, sửa, ngân sách, bảng xếp hạng, thống kê | `/events/*` | ✔ ADV | — | ✔ ADV | ✔ |
| Sự kiện — chạy lại thống kê ngày | `/events/run-analytic-daily` | ✔ | — | — | ✔ |
| Sự kiện — huỷ / chạy lại thưởng | `/events/reject-reward-event`… | — | — | — | ✔ |
| Thưởng sự kiện — đổi trạng thái, xoá | `/event-reward` | — | — | — | ✔ |
| Mẫu sự kiện | `/event-schemas` | ✔ | — | ✔ | ✔ |
| Thưởng thêm — xem, tạo, sửa, nhập Excel | `/event-bonus` | ∀ | ∀ | ∀ | ✔ |
| Nhiệm vụ, duyệt điểm | `/missions` | ✔ | — | — | ✔ |
| Quà | `/gifts` | ✔ | — | — | ✔ |
| Đối soát — mọi thao tác | `/reconciliations` | ✔ | — | — | ✔ |
| Rút tiền — mọi thao tác | `/transfers` | ✔ | — | — | ✔ |
| Dữ liệu xuất | `/data-exports` | ✔ | — | — | ✔ |
| Phân khúc, phân khúc người dùng, mã, thông báo admin | `/segments`, `/user-segments`, `/manage-codes`, `/admin-notifications` | ✔ | — | — | ✔ |
| Danh mục — xem | `GET /categories` | ✔ | — | ✔ | ✔ |
| Danh mục — sửa | `/categories` | ✔ | — | — | ✔ |
| Tin tức, bài viết | `/news`, `/articles` | ✔ | — | ✔ | ✔ |
| Chiến dịch affiliate | `/affiliate-campaigns`, `/campaign-affiliate-mappings` | ✔ ADV | — | ✔ ADV | ✔ |
| Kênh hỗ trợ | `/quick-actions` | — | — | ✔ ADV | ✔ |
| Cấu hình ứng dụng ADV | `/partners/:id/app-config`, `/:id/features` | ✔ ADV | — | ✔ ADV | ✔ |
| ADV — danh sách | `GET /partners` | ∀ | ∀ | ∀ | ✔ |
| ADV — tạo, sửa, ngừng | `/partners` | — | — | — | ✔ |
| Dữ liệu người dùng WildRift | `PUT /partners/users/wildrift` | ∀ | ∀ | ∀ | ✔ |
| Tag — danh sách | `GET /tags` | ✔ | ✔ | ✔ | ✔ |
| Tag — tạo, sửa | `/tags` | ✔ | — | — | ✔ |
| Cấu hình chung | `/common-configs` | ✔ | — | — | ✔ |
| Cấu hình chung — đọc, **ghi** | `/common/configurations` | ∀ | ∀ | ∀ | ✔ |
| Nhật ký thao tác | `/audits` | ∀ | ∀ | ∀ | ✔ |
| Lịch sử đăng nhập | `/audits/login-histories` | ✔ | — | — | ✔ |
| Xác thực tài khoản | `/identifications` | — | — | — | ✔ |
| Nhân sự, vai trò | `/staffs`, `/roles` | — | — | — | ✔ |
| Công cụ kỹ thuật | `/migration/*`, `/migration/backfill-*` | ∀ | ∀ | ∀ | ✔ |

- Ô **∀** sẽ đổi ở Mốc 3 (PQ-15); mỗi ô có dòng tương ứng trong danh sách đổi hành vi có chủ đích.
- Ô **ADV** của Admin chỉ đúng khi Admin gắn ADV; Admin chưa gắn ADV hôm nay bị các phép so sánh thô chặn ở tầng
  service (2.3) dù cổng router cho qua.
- Cấu hình ứng dụng chỉ qua được khi có gắn ADV (điều kiện nằm trong cổng).
