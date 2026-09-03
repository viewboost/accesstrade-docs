# Product Requirements Document: Luồng mã nhân viên trên site đa đối tác (`frontend/`)

**Date:** 2026-09-03
**Author:** Nguyễn Đăng Định
**Version:** 1.4
**Reviewer:** _chưa có_
**Project Level:** Level 2
**Status:** Draft — phạm vi đã chốt đủ, chờ review
**Mức độ:** **P1 — lỗi đang sống trên production**, xem mục 1
**Phạm vi:** **Chỉ `frontend/`.** `parasola/`, `fecredit/` và 12 folder partner còn lại không bị ảnh hưởng.

---

## Document Overview

PRD này là **task riêng**, không phải bản mở rộng của [prd-employee-code-2026-08-06.md](./prd-employee-code-2026-08-06.md) (v5.1, Final). PRD đó đã đóng và mục 8 của nó ghi rõ *"Không đụng `frontend/`"* — ràng buộc đó đúng tại thời điểm viết và **không sửa lại**.

Lý do phải tách chứ không nối vào: PRD v5.1 giả định **một đối tác = một app**. Toàn bộ đặc tả frontend của nó (FR-009, FR-010) dựng trên giả định đó. `frontend/` là app **đa đối tác duy nhất** trong repo, nên các yêu cầu này không áp thẳng được — phải đặc tả lại từ đầu, với ngữ cảnh khác.

### Nguyên tắc

**Backend và admin đã xong, không đụng vào.** API, gate chặn nộp bài, cờ bật/tắt theo đối tác đều đã dùng chung và đã có trên `release`. PRD này thuần frontend.

**Bám bản `fecredit/` đang chạy production làm chuẩn UX**, vì đó là bản đã qua QA. Chỉ đi khác ở những chỗ **kiến trúc bắt buộc phải khác**, mỗi chỗ ghi rõ lý do tại chỗ.

**Về giao diện — chốt 03/09:** không chờ bản thiết kế riêng. Bám **style sẵn có của `frontend/`** (`components/app/modal`, `components/app/toast`, `components/common/form-field`, bộ class hiện hành), làm cho tương đối hợp với phần còn lại của web. Ràng buộc cứng: **không được lỗi UI** — vỡ layout, tràn chữ, chồng modal, lệch trên mobile đều tính là chưa xong. Mỗi modal phải được xem tận mắt trên cả desktop lẫn mobile trước khi báo hoàn thành, không chỉ đọc code.

**Tên đối tác phải hiện đúng ở mọi chỗ có chữ.** Bản `fecredit` hard-code "FE CREDIT AMBASSADOR" trong nội dung modal (`modal-staff-code.tsx:145`) vì chỉ phục vụ một đối tác. Trên site đa đối tác, mọi câu chữ nhắc tới đối tác phải lấy tên động theo ngữ cảnh đang xem. Đây là ràng buộc xuyên suốt FE-003, FE-004, FE-005 — không nhắc lại ở từng mục.

**Đánh số riêng bằng tiền tố `FE-`** để không lẫn với `FR-0xx` của PRD v5.1. Mục 11 map hai bên.

**Related Documents:**
- PRD gốc (backend + admin + app white-label): [./prd-employee-code-2026-08-06.md](./prd-employee-code-2026-08-06.md)
- Dossier phân tích code T-Fluencers: [./tf-reference-employee-code-flow.md](./tf-reference-employee-code-flow.md)
- Khảo sát code cho task này: `ambassador/plans/260903-1706-ma-nhan-vien-cho-frontend/analysis.md` (repo code)

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Site đa đối tác** | `frontend/` — một app hiển thị nhiều đối tác, mỗi đối tác là một nhánh route `/:partner/…` |
| **App white-label** | `fecredit/`, `parasola/`, `vpbank/`… — mỗi folder phục vụ đúng một đối tác |
| **Trạng thái nhân viên** (`statusStaff`) | Thuộc tính trên `user-partners`: `employee` \| `not_employee` \| `not_verify`. **Gắn theo từng cặp user × đối tác**, không phải toàn hệ thống |
| **Đối tác hiện tại** | Đối tác dùng để hỏi/khai trạng thái nhân viên ở trang đang xem. Trên app white-label luôn xác định được; trên site đa đối tác thì không |
| **Điểm mở form nộp bài** | Mỗi nút/handler đặt `openPostContentModal: true` |
| **Gate nhân viên** | Khối kiểm tra ở `content.go:132`, chạy mỗi lần nộp bài, trước `JoinEvent` |

---

## 1. Executive Summary

Gate chặn nộp bài nằm ở backend dùng chung và **không biết người dùng đang đứng ở app nào**. Trên `frontend/` người dùng gặp gate mà không có bất kỳ giao diện nào để thoả nó.

```
Marketing bật "chỉ dành cho nhân viên" cho một chiến dịch
  → người dùng trên fecredit/parasola: thấy modal, nhập mã, nộp bài được
  → người dùng trên frontend/:        mở form, gõ link, ăn lỗi trần, hết đường
```

| Người dùng làm gì | `fecredit/` | `frontend/` hôm nay |
|---|---|---|
| Nộp bài vào chiến dịch chỉ dành cho nhân viên | Modal chặn **trước khi** mở form | Mở form, gõ link, **bị backend từ chối bằng lỗi trần** |
| Chiến dịch có mã tham gia riêng | Modal nhập mã → nạp lại → mở form | Không có đường nào, nộp bài luôn thất bại |
| Muốn khai / sửa nhãn nhân viên | Mục "Thông tin nhân viên" ở trang Hồ sơ | Không có đường nào |

**Không phải chuyện parity cho đẹp.** Đây là đường cụt: người dùng không tự thoát ra được, và Ops cũng không có gì để hướng dẫn họ.

### ⚠️ Đây không phải rủi ro giả định — đã xảy ra trên production

Tra API công khai ngày 03/09/2026, từ đúng origin của `frontend/` (`https://ambassador.koc.com.vn`, xem `frontend/config/config.prod.ts:13`):

| Kiểm | Kết quả |
|---|---|
| `GET /api/public/partners` | **17 đối tác**, `allowHeaderPartner = true` — đúng là site đa đối tác |
| **FE CREDIT có trong danh sách đó không?** | **CÓ** — slug `fecredit`, id `6a8d6e38f6aec40a65991d71` |
| Chiến dịch của FE CREDIT trên site này | 2 chiến dịch; chiến dịch slug **`fecredit` có `applyForStaff = true`** |

⇒ Hôm nay, một người vào `ambassador.koc.com.vn/fecredit/fecredit` và bấm nộp bài:
- Nếu không phải nhân viên FE CREDIT → backend từ chối bằng lỗi trần
- Nếu **là** nhân viên nhưng chưa khai mã → cũng bị từ chối, và **không có bất kỳ đường nào trên site này để khai**

Cùng chiến dịch đó, cùng backend đó, vào từ app white-label `fecredit/` thì có modal, nhập mã xong nộp bài được. Khác biệt duy nhất là người dùng gõ vào domain nào.

*(Không tự kiểm được `options.enableStaffCode` của FE CREDIT vì `status-employee` yêu cầu đăng nhập — nhưng app white-label của họ đã chạy luồng này trên `release`, nên cờ gần như chắc chắn đang bật. Cần BE xác nhận một câu.)*

---

## 2. Bối cảnh

### 2.1 Hiện trạng — đã verify từng dòng

| Thành phần | Trạng thái | Bằng chứng |
|---|---|---|
| Gate chặn nộp bài | ✅ Có, dùng chung mọi app | `backend/pkg/public/service/content.go:132`, gọi **trước** `JoinEvent` (`:139`) |
| Test gác vị trí gate | ✅ Có | `backend/pkg/public/service/staff_gate_test.go:34,41` |
| API `confirm-is-staff` | ✅ Có, cho ghi đè | `backend/pkg/public/service/staff_code.go` |
| API `status-employee` | ✅ Có, tự tắt theo đối tác | `staff_code.go:47` — chưa bật cờ thì trả `isOpenInputStaffCode=false` |
| API `input-code-join-event` | ✅ Có | `backend/pkg/public/service/event.go` |
| Cờ `isRequireCode`, `staffGateReason` ra FE | ✅ Có ở event detail | `backend/pkg/public/service/event.go:1292-1293` |
| Admin (quản lý mã, cột/filter, sửa trạng thái, thống kê) | ✅ Có, 23 file | `admin/src/pages/manage-code/`, `user-partner/`, `event-statistic/` |
| UI người dùng trên `fecredit/` | ✅ Có, 11 file | `origin/release` |
| UI người dùng trên `parasola/` | ⚠️ Chỉ có trên `develop` | Gỡ khỏi PR release có chủ ý (commit `22ef6d8eb`, PR #135) |
| UI người dùng trên `frontend/` | ❌ **Không có gì** | grep 0 file, cả `release` lẫn `develop` |

⇒ **Không có việc gì cho backend và admin trong task này.**

### 2.2 Khác biệt kiến trúc cốt lõi: `frontend/` không xác định được "đối tác hiện tại"

Đây là toàn bộ lý do PRD này tồn tại.

**Cơ chế:**

| Bước | Bằng chứng |
|---|---|
| Handler lấy domain từ header Origin | `backend/pkg/public/handler/partner.go:203` — `Domain: cc.GetAppOrigin()` |
| Service lọc đối tác theo domain | `backend/pkg/public/service/partner.go:308` — `cond["allowDomains"] = host` |
| Backend nói FE biết đây là site mấy đối tác | `backend/pkg/public/service/partner.go:376` — `AllowHeaderPartner = len(res.Data) > 1` |
| FE đảo cờ | `frontend/src/models/main.ts:243` — `isOwnerPartner = !allowHeaderPartner` |

⇒ App white-label chạy trên domain riêng → danh sách trả về đúng 1 đối tác → `isOwnerPartner = true`.
⇒ `frontend/` chạy trên domain ACCESSTRADE → trả nhiều đối tác → `isOwnerPartner = false`.

**Hệ quả về route:** `frontend/config/routes.ts:114-155` — chỉ cây route lồng dưới `/:partner/` mới có đối tác. Các trang dùng chung — `/tai-khoan`, `/thong-bao`, `/trang-ca-nhan`, `/ho-tro` — **không có đối tác nào**.

**Hệ quả về code:** hàm `resolveCurrentPartner` của bản white-label (`fecredit/src/utils/staff.ts:34-45`) có đúng hai nhánh — `partnerDetail._id` có sẵn, hoặc `isOwnerPartner && partners.length === 1`. Comment trong chính file đó đã ghi: *"Site nhiều đối tác thì 'đối tác hiện tại' không xác định được, trả `undefined` để giữ nguyên hành vi cũ thay vì đoán bừa một đối tác."*

Trên `frontend/` nhánh thứ hai **không bao giờ đúng**. Copy nguyên bộ `fecredit/` sang thì:
- Modal xác nhận nhân viên **không bao giờ hiện** — lúc đăng nhập người dùng đang ở `/`, chưa có `:partner`
- Mục "Thông tin nhân viên" ở `/tai-khoan` **không bao giờ render**
- Chỉ phần gate theo event là chạy, vì cờ đi theo event mà event thì mang đối tác

**Chết lặng, không lỗi, không log.** Đây là kiểu hỏng khó phát hiện nhất khi QA, nên ghi vào PRD chứ không để dev tự vấp.

### 2.3 Ba cái bẫy đã kiểm chứng ở bản `fecredit/` — sửa, không port nguyên

Đều là bài học có commit làm bằng, không phải suy đoán:

| Bẫy | Bằng chứng | `frontend/` làm gì |
|---|---|---|
| Bật modal chặn **lúc tải trang** | Commit `212f1eca0` phải sửa lại: vừa thừa popup chặn người chỉ vào xem thể lệ, vừa để lọt đúng thao tác cần chặn | Chỉ mở khi **bấm nộp bài** (FE-002) |
| **Modal xác nhận tự bật lúc tải trang** | `fecredit/.../header/index.tsx:100-107` — `useEffect` gọi `checkPartnerEmployeeStatus`, effect set `visibleModalStaffCode`. `parasola` y hệt (`:101-107`) | **Không port** — xem FE-006 |
| Suy trạng thái gate ở FE từ `user.statusStaff` | `fecredit/src/utils/staff.ts:84-92` đã ghi: `statusStaff` gắn theo từng đối tác (`UserPartnerRaw.StatusStaff`), FE chỉ có một `user.statusStaff` chung | **Chỉ đọc lại `staffGateReason` backend trả** (FE-002) |

Bẫy thứ ba là bẫy nguy hiểm nhất trên site đa đối tác: một người là nhân viên của đối tác A không phải nhân viên của đối tác B, nên so bằng `user.statusStaff` sẽ cho kết quả sai ở **đúng** app này.

### 2.4 Những gì KHÔNG thêm vào

Đã cân nhắc, loại bỏ:

- **Dòng "Dành cho nhân viên / Dành cho creator" trên thẻ chiến dịch.** `fecredit/src/pages/partner-home/components/event-active-new/event-card.tsx:43-53` có, nhưng PRD v5.1 không yêu cầu và nó không liên quan tới đường cụt đang phải vá.
- **Đưa UI `parasola/` lên `release`.** Việc riêng, PR riêng.
- Mọi thứ PRD v5.1 đã loại: ràng buộc một-mã-một-người, rate limit, validate format mã, audit trail phía FE, giới hạn số lần hiện modal, **phân nhóm nhân viên dưới mọi hình thức**.
- Sửa món nợ kế thừa "event list và event detail tính `isRequireCode` khác nhau" (PRD v5.1 §FR-011 đã ghi nhận). Port nguyên để giữ parity, không sửa trong task này.

---

## 3. User Personas

**P1. Creator trên site ACCESSTRADE, là nhân viên của một đối tác** — đang bị chặn nộp bài mà không hiểu vì sao.
**P2. Creator trên site ACCESSTRADE, không thuộc đối tác nào** — chiếm đa số. **Không được thấy bất kỳ thay đổi nào** nếu đối tác chưa bật cờ.
**P3. Ops AccessTrade** — hiện không có gì để hướng dẫn P1 tự thoát.
**P4. Marketing của đối tác** — bật chiến dịch nội bộ mà không biết một phần người dùng đang không tham gia được.
**P5. Người dùng của các app white-label** — **không được ảnh hưởng.** Ràng buộc, không phải mục tiêu.

---

## 4. Functional Requirements

### FE-001: Xác định "đối tác hiện tại" trên site đa đối tác

**Priority:** Must Have — nền tảng cho mọi FR còn lại

Viết lại `resolveCurrentPartner` cho `frontend/`, thay vì port hàm của bản white-label.

**Quy tắc:**

| Ngữ cảnh | Đối tác hiện tại |
|---|---|
| Đang ở route có `:partner` (`partnerDetail._id` có giá trị) | Chính đối tác đó |
| Trang dùng chung (`/tai-khoan`, `/thong-bao`…) | **Không có** — trả `undefined` |

**Cấm đoán bừa.** Không lấy `partners[0]`, không lấy đối tác vừa xem gần nhất, không nhớ vào localStorage. Đoán sai nghĩa là ghi trạng thái nhân viên vào nhầm đối tác, mà `user-partners.statusStaff` thì ảnh hưởng thẳng tới điều kiện xét thưởng.

**Mọi FR còn lại phải xử lý được trường hợp trả `undefined`** — hoặc không cần đối tác (FE-002, FE-003, FE-004: cờ đi theo event), hoặc tự dựng danh sách đối tác riêng (FE-005).

**AC:**
- [ ] Trên `/:partner/…` trả đúng đối tác của route
- [ ] Trên trang dùng chung trả `undefined`, không đoán
- [ ] Có unit test cho cả hai nhánh (`frontend/` đã có `jest.config.js` + `umi-test`, 9 file test đang chạy)

---

### FE-002: Chặn ở mọi điểm mở form nộp bài

**Priority:** Must Have

**Vì sao cần.** Backend chặn ở `content.go:132` mỗi lần nộp bài. FE không chặn trước thì người dùng gõ xong link mới ăn lỗi — vừa mất công, vừa không biết phải làm gì tiếp.

**Nguồn dữ liệu:** đọc lại `isRequireCode` và `staffGateReason` mà backend trả trong event detail (`event.go:1292-1293`). **Tuyệt đối không tự suy luật ở FE** — backend tính `staffGateReason` bằng chính `checkStaffGate`, tức đúng hàm chặn thật. Nhân bản luật ra FE là mở đường cho cảnh FE báo "đủ điều kiện" rồi nộp bài mới bị từ chối.

**Thứ tự kiểm khi bấm nộp bài:**
1. `staffGateReason` có giá trị → mở modal "chỉ dành cho nhân viên" (FE-004), **không** mở form
2. `isRequireCode` = true → mở modal nhập mã tham gia (FE-003), **không** mở form
3. Còn lại → mở form như cũ

**Không tự bật lúc tải trang.** Người chỉ vào xem thể lệ hay bảng xếp hạng không việc gì phải nhận popup chặn đường (bài học `212f1eca0`).

#### ⚠️ Ràng buộc bắt buộc: gom vào một hàm dùng chung

`frontend/` có **nhiều điểm mở form hơn** app white-label:

| App | Số điểm | Vị trí |
|---|---|---|
| `fecredit/` | 3 | header, khối thống kê, khối chi tiết |
| **`frontend/`** | **4+** | `src/components/layout/main/header/index.tsx:161`<br>`src/pages/home/components/not-logged-in/index.tsx:46`<br>`src/pages/home/components/logged-in-view/index.tsx:35`<br>`src/pages/home/components/post-modal/index.tsx:72,89` |

Modal nộp bài còn được mount ở **hai chỗ** (`src/layouts/event-detail/index.tsx:292` và `src/pages/home/components/logged-in-view/index.tsx:163`), và `src/pages/profile/index.tsx:118` dùng lại khối thống kê.

**Copy khối `if` bốn lần là sai.** Sót một điểm = lọt một đường nộp bài, và đó chính là đường QA ít đi nhất. Viết **một** hàm/hook kiểm tra, mọi điểm gọi nó.

**AC:**
- [ ] Cả 4+ điểm mở form đều đi qua cùng một hàm kiểm tra
- [ ] Chiến dịch không bật điều kiện nào → hành vi không đổi, không thêm request nào
- [ ] Không popup nào tự bật lúc tải trang chi tiết chiến dịch
- [ ] Người chưa đăng nhập → hành vi như cũ (backend trả `staffGateReason` rỗng khi chưa đăng nhập)
- [ ] Không suy trạng thái từ `user.statusStaff` — grep phải bằng 0

---

### FE-003: Modal nhập mã tham gia riêng của chiến dịch

**Priority:** Must Have

Port từ `fecredit/src/pages/home/components/modal-event-code/` (159 dòng + scss). Đây là đường ghi duy nhất cho `user-events.options.codeInput`, mà cổng chặn lúc nộp bài đọc lại đúng field đó.

**Hành vi:**
- Modal **đóng được**
- Nhập xong → gọi `POST /events/:id/input-code-join-event` → **nạp lại event detail** để backend tính lại `isRequireCode`, không tự đoán ở FE là đã đủ điều kiện
- Nạp lại xong → **mở tiếp form nộp bài**, vì người dùng vào đây là đang muốn nộp bài, bắt bấm lại lần nữa là thừa một bước
- Chuẩn hoá mã lúc gõ (uppercase + trim) để giá trị gửi lên khớp giá trị nhìn thấy. Backend vẫn chuẩn hoá lại, không tin FE

**Lưu ý:** mã ở đây **khác** mã nhân viên ở trang Quản lý mã — đối chiếu thẳng với `event.Options.StaffCodes`, không tra bảng `manage-codes`. Chữ trong modal không được gọi nó là "mã nhân viên".

**AC:**
- [ ] Nhập đúng mã → modal đóng, form nộp bài mở ra, không phải bấm lại
- [ ] Nhập sai → lỗi hiện tại chỗ, modal không đóng
- [ ] Gõ chữ thường vẫn nhận
- [ ] Không hiện chồng với modal đăng nhập / modal hệ thống khác

---

### FE-004: Modal "chiến dịch chỉ dành cho nhân viên"

**Priority:** Must Have

Port từ `fecredit/src/components/common/modal-not-employee/` (71 dòng).

| Trường hợp | Tiêu đề | Hành động |
|---|---|---|
| Không phải nhân viên, bấm nộp bài vào chiến dịch `applyForStaff` | Thử thách này dành riêng cho nhân viên {tên đối tác} | Đã hiểu / Khám phá thêm |

**Modal này đóng được.**

**Tên đối tác lấy động theo event đang xem**, không hard-code. Bản `fecredit` hard-code "FE CREDIT" trong chữ (`modal-staff-code.tsx:145`) vì chỉ có một đối tác — trên site đa đối tác làm vậy là hiện sai tên.

**Modal phải tự tắt khi không còn đúng:** chuyển sang chiến dịch khác, hoặc vừa khai xong mã nhân viên rồi nạp lại chi tiết → popup không được bám theo người dùng sang trang khác.

**AC:**
- [ ] Modal đóng được; "Khám phá thêm" đưa về trang chủ
- [ ] Tên đối tác đúng với chiến dịch đang xem
- [ ] Chuyển sang chiến dịch khác → modal tự tắt
- [ ] Mount ở chỗ phủ được mọi điểm nộp bài, kể cả khối thống kê dùng lại ở `/trang-ca-nhan`

---

### FE-005: Mục "Thông tin nhân viên" ở `/tai-khoan` — danh sách theo đối tác

**Priority:** Must Have

**Vì sao cần.** Ở PRD v5.1 đây là *đường sửa lỗi*: modal chỉ hỏi một lần, người đăng ký trước ngày bật cờ bị backfill thành người ngoài, không có đường sửa thì nhân viên gõ nhầm mã sẽ kẹt vĩnh viễn.

**Trên `frontend/` nó quan trọng hơn thế.** Vì FE-006 chốt không port modal chủ động, đây là **đường khai duy nhất** — nhân viên muốn nhận nhãn không còn chỗ nào khác. Kéo theo hai yêu cầu bổ sung:
- Mục này phải **dễ tìm** trên `/tai-khoan`, không giấu dưới đáy trang
- Modal FE-004 (bị chặn lúc nộp bài) phải **chỉ đường tới đây**, không chỉ báo "bạn không đủ điều kiện" rồi thôi

**Khác PRD v5.1 ở đâu và vì sao.** Bản white-label render một khối duy nhất vì chỉ có một đối tác. `/tai-khoan` của `frontend/` **không thuộc đối tác nào** (FE-001), nên phải tự dựng danh sách.

**Cách dựng danh sách:**
1. Lấy `mainState.partners` — danh sách đối tác của **chính site này**, đã được `getListPartner` nạp sẵn (`frontend/src/models/main.ts:234-247`) và đã được backend lọc theo domain (`service/partner.go:308`)
2. Gọi `GET /partners/:id/status-employee` cho từng đối tác trong danh sách đó
3. **Chỉ render đối tác trả `enabled = true`** — đối tác chưa bật cờ thì không được xuất hiện dòng nào

#### ⚠️ KHÔNG dùng `partnerApproval` — đã kiểm chứng là sai nguồn

Ứng viên đầu tiên cho danh sách này là `user.partnerApproval[]`. **Sai.** Trường đó nằm trên `user-socials`, không nằm trên user:

- `backend/internal/model/mg/user_social.go:26` — `PartnerApproval *[]PartnerApproval` là field của `UserSocialRaw`
- `backend/pkg/public/service/user.go:602-603` — gán từ từng user-social, trong vòng lặp dựng response danh sách tài khoản social
- `frontend/src/interfaces/user.ts:383,403` — phía FE cũng nằm trong `IUserSocial`, **không** trong `IUser`

Nó là trạng thái duyệt **tài khoản social** cho từng đối tác — khác hẳn quan hệ user × đối tác trong `user-partners`, là nơi `statusStaff` thực sự sống. Dùng nó sẽ vừa thiếu đối tác (user có `user-partners` mà chưa liên kết social), vừa thừa (mỗi social một mảng, phải gộp và khử trùng).

**Không có API công khai nào trả thẳng danh sách `user-partners` của user.** `service/partner.go:337-341` có tính `userPartnerIds` nhưng chỉ dùng để **xếp đối tác của user lên trước**, không đánh dấu ra response (`PartnerAppResponse` không có field nào cho việc đó). Nên `mainState.partners` là nguồn đúng và sẵn có nhất; việc lọc ai được hiện đã do `status-employee` làm ở backend.

**Mỗi dòng:**

| Trạng thái | Hiển thị |
|---|---|
| `employee` | Hiện mã, khoá, chú thích *"Bạn đang được ghi nhận là nhân viên. Cần đổi hoặc gỡ mã, vui lòng liên hệ bộ phận hỗ trợ."* |
| `not_employee` / rỗng / `not_verify` | Ô nhập mã + nút Lưu |

**Một chiều `not_employee → employee`.** User không tự gỡ nhãn được — backend đã chặn (`staff_code.go`, nhánh `IsStaff=false` gặp trạng thái đang là nhân viên → lỗi `CannotSelfRevoke`). FE không được vẽ nút gỡ. Cho tự gỡ là mở đường bật/tắt nhãn quanh thời điểm xét thưởng để lách điều kiện chiến dịch.

**Ràng buộc số lượng request.** Danh sách đối tác của một user có thể dài. Phải giới hạn số request song song và chấp nhận render dần; **không** chặn cả trang chờ đủ. Nếu một request lỗi thì chỉ dòng đó không hiện, không làm hỏng các dòng khác và không làm hỏng phần còn lại của trang Hồ sơ.

**AC:**
- [ ] Người dùng không có đối tác nào bật cờ → **không thấy mục này**, trang Hồ sơ y như cũ
- [ ] Có 2 đối tác bật cờ → thấy 2 dòng, trạng thái từng dòng độc lập
- [ ] Khai nhân viên ở đối tác A → không đổi trạng thái ở đối tác B
- [ ] Đang là nhân viên → không có đường tự gỡ trên UI
- [ ] Nhập nhầm mã → lỗi hiện rõ, không mất dữ liệu các dòng khác
- [ ] Một request `status-employee` lỗi → các dòng còn lại vẫn render
- [ ] Người bị backfill nhầm khai lại được

---

### FE-006: KHÔNG làm modal xác nhận nhân viên chủ động — khác biệt có chủ ý

**Priority:** quyết định phạm vi, không phải hạng mục thi công
**Chốt 03/09/2026.**

`frontend/` **không** port modal *"Bạn có phải nhân viên của {đối tác}?"* mà `fecredit/` và `parasola/` đang có. Đây là **khác biệt duy nhất về UX** giữa `frontend/` và hai app kia, và là khác biệt cố ý.

#### 6.1 Hai app kia làm gì — đã đọc code, không suy đoán

Trong `fecredit`/`parasola` có **hai nhóm modal**, và chỉ một nhóm đã được chuyển sang chặn-đúng-lúc:

| Modal | Hành vi hiện tại | Bằng chứng |
|---|---|---|
| "Chỉ dành cho nhân viên" | Chặn tại **nút nộp bài** | commit `212f1eca0` |
| "Nhập mã tham gia riêng" | Chặn tại **nút nộp bài** | cùng commit |
| **"Bạn có phải nhân viên?"** | **Vẫn tự bật lúc tải trang** | `fecredit/.../header/index.tsx:100-107`; `parasola` `:101-107` |

Modal thứ ba chỉ chờ modal điều khoản xong, ngoài ra không có điều kiện nào khác. Đã quét toàn bộ nhánh từ 01/08/2026: không có commit nào gỡ nó.

⇒ Nên **"làm giống fecredit" và "chỉ chặn lúc nộp bài" là hai thứ khác nhau.** PRD này chọn cái thứ hai.

#### 6.2 Vì sao `frontend/` không port

**Trên app một đối tác, hỏi chủ động là hợp lý** — ai vào site của FE CREDIT cũng là người trong phạm vi câu hỏi.

**Trên site đa đối tác thì ngược lại.** Ba dữ kiện, đều đã kiểm chứng:

1. **Đa số người vào không thuộc đối tác nào.** Site có 17 đối tác (đo 03/09). Hỏi chủ động = chặn toàn bộ người vào để lọc ra thiểu số là nhân viên.

2. **Người chưa từng tham gia đối tác nằm đúng vào nhóm bị hỏi.** Script backfill (`admin/service/migration_backfill_staff_status.go`) lọc `{partner, statusStaff: {$exists: false}}` — chỉ chạm bản ghi **đã tồn tại** trong `user-partners`. Người chưa từng tham gia không có bản ghi để backfill → `isOpenInputStaffCode = true` → bị hỏi ngay lần đầu ghé trang.

3. **Link chiến dịch cũng là trang đối tác.** `/:partner/:slug` nằm cùng cây route (`frontend/config/routes.ts:114-155`) — đây là đường vào phổ biến nhất, người ta bấm link từ mạng xã hội. Hỏi chủ động nghĩa là **modal blocking hiện trước cả nội dung chiến dịch**, và F5 lại chặn tiếp cho tới khi trả lời (`dismissed` sống trong redux — `fecredit/src/utils/staff.ts:64-72`, cố ý, vì bấm Hủy không phải một câu trả lời).

Áp vào số liệu thật: FE CREDIT đang có chiến dịch `applyForStaff` trên `ambassador.koc.com.vn`. Port modal chủ động = mọi người mở link chiến dịch đó đều bị chặn trước khi thấy nội dung. Đây là rủi ro chuyển đổi, không phải chi tiết kỹ thuật.

#### 6.3 Bù lại bằng gì

Bỏ modal chủ động thì nhân viên thật không được nhắc. Hai đường thay thế, **cả hai đều nằm trong phạm vi task này**:

| Tình huống | Đường ra |
|---|---|
| Nhân viên bấm nộp bài vào chiến dịch nội bộ | Modal FE-004 giải thích rõ, kèm lối đi tiếp |
| Nhân viên muốn khai chủ động | Mục "Thông tin nhân viên" ở `/tai-khoan` (FE-005) |

⇒ **FE-005 trở thành đường khai duy nhất trên `frontend/`**, nên nó không còn là "đường sửa lỗi" như ở PRD v5.1 mà là lối đi chính. Yêu cầu kèm theo: mục đó phải **dễ tìm**, không giấu dưới đáy trang.

#### 6.4 Vì sao quyết định này an toàn để đảo ngược

Cách làm này là **tập con** của cách có modal chủ động: modal FE-004, mục FE-005 và hàm chặn FE-002 đều cần cho cả hai hướng. Nếu sau khi chạy thật thấy nhân viên không tự tìm được đường khai, chỉ cần **thêm** modal chủ động lên trên — không phải vứt dòng code nào.

Ngược lại thì không đúng: làm modal chủ động trước, sau thấy phiền người dùng thì phải gỡ ra và xử lý đống dữ liệu `user-partners` đã sinh ra (`writeStaffStatus` dùng `SetUpsert(true)`, `staff_code.go:192-214` — người chỉ ghé xem rồi bấm "Tôi không thuộc" cũng tạo bản ghi mới).

#### 6.5 Hệ quả lên code

Không cần: `modal-staff-code.tsx`, `staffCodeDismissed`, `visibleModalStaffCode`, và bộ icon đi kèm.

**AC:**
- [ ] Không có modal nào tự bật khi vào trang đối tác hay trang chi tiết chiến dịch
- [ ] Diff không chứa `modal-staff-code`, `staffCodeDismissed`, `visibleModalStaffCode`
- [ ] Nhân viên chưa khai mã vẫn có đủ hai đường ra ở mục 6.3

---

### FE-007: Không đổi hành vi khi đối tác chưa bật cờ

**Priority:** Must Have — ràng buộc, không phải tính năng

Backend đã tự tắt theo đối tác (`staff_code.go:47`, `:99`). FE phải không thêm bất kỳ bề mặt nào cho người dùng của đối tác chưa bật.

**AC:**
- [ ] Đối tác chưa bật cờ → không modal, không mục ở Hồ sơ, không thêm request nào so với hiện tại
- [ ] Chiến dịch không bật `applyForStaff` và không có `staffCodes` → đường nộp bài không đổi một bước nào
- [ ] Tắt `enableStaffCode` của một đối tác đang bật → mọi bề mặt biến mất, dữ liệu `statusStaff` đã ghi giữ nguyên
- [ ] **Diff không chạm vào `parasola/`, `fecredit/` và 12 folder partner còn lại**

---

## 5. Non-Functional Requirements

### NFR-001: Backward Compatibility
Người dùng của đối tác chưa bật cờ không được thấy bất kỳ thay đổi nào — kể cả một request thừa.

### NFR-002: Không nhân bản luật nghiệp vụ ra FE
Mọi quyết định chặn/không chặn đều đọc lại cờ backend trả. FE chỉ quyết định **hiển thị cái gì**, không quyết định **ai đủ điều kiện**.

### NFR-003: Performance
FE-005 gọi N request theo số đối tác của user — phải giới hạn song song, render dần, và một request hỏng không kéo đổ phần còn lại.

### NFR-004: Ngôn ngữ
Chỉ tiếng Việt (`frontend/src/locales/` chỉ có `vi-VN`). Không thêm chuỗi tiếng Anh.

### NFR-005: Test
Phần logic tách được (`utils/staff.ts`) phải có unit test — `frontend/` đã có sẵn `jest.config.js` + `umi-test` và 9 file `*.test.ts` đang chạy, không có lý do bỏ qua.

Bộ test case nghiệm thu do người khác viết riêng, **không thuộc phạm vi PRD này**.

### NFR-006: Không lỗi UI
Mọi màn mới phải xem tận mắt trên desktop và mobile trước khi báo xong. Kiểm tối thiểu: modal không vỡ layout ở màn hẹp, chữ dài (tên đối tác dài) không tràn, không có hai modal chồng nhau, nút không bị bóp méo bởi class utility của app (bẫy đã gặp ở `fecredit`: `AppButton` tự chèn `rounded-2` đè lên `border-radius` của `.btn-primary`).

---

## 6. Epics và thứ tự

| # | Epic | Phụ thuộc |
|---|---|---|
| E1 | FE-001 — `resolveCurrentPartner` cho site đa đối tác + test | — |
| E2 | Hạ tầng: endpoint, interface, state, effect (`configs/api.ts`, `services/user.ts`, `interfaces/`, `models/main.ts`) | — |
| E3 | FE-002 — hàm kiểm tra dùng chung + cắm vào 4+ điểm mở form | E2 |
| E4 | FE-003 + FE-004 — hai modal chặn | E3 |
| E5 | FE-005 — mục Hồ sơ dạng danh sách | E1, E2 |
| E7 | FE-007 — hồi quy: kiểm đối tác chưa bật cờ không đổi gì | E3, E4, E5 |

Cả 6 epic đều làm được ngay, không còn hạng mục chờ.

---

## 7. Kiến trúc

```
users/me ──> user.partnerApproval[]
                    │
                    ├─ (FE-005) với mỗi đối tác: GET /partners/:id/status-employee
                    │     └─ enabled=true ──> render 1 dòng ở /tai-khoan
                    │            └─ Lưu mã ──> POST /users/confirm-is-staff
                    │
route /:partner/:slug ──> event detail ──> { isRequireCode, staffGateReason }
                                                │
                          bấm "Nộp bài" ────────┤ (FE-002, một hàm dùng chung)
                                                │
                    staffGateReason ──> modal "chỉ dành cho nhân viên" (FE-004)
                    isRequireCode ────> modal nhập mã tham gia (FE-003)
                                          └─ POST /events/:id/input-code-join-event
                                             └─ nạp lại event detail ──> mở form
                    còn lại ──────────> mở form nộp bài
```

Ba endpoint dùng, đều đã có: `POST /users/confirm-is-staff`, `GET /partners/:id/status-employee`, `POST /events/:id/input-code-join-event`.

---

## 8. Implementation Scope

`frontend/` đã có sẵn hạ tầng cần dùng: `components/app/modal` (đủ prop `closeButton` / `keyboard` / `hideFooter`), `components/app/toast`, `components/common/form-field`, và bộ test chạy được. Phần lớn là port cơ học; chỗ phải nghĩ là FE-001 và FE-005.

### Thay đổi cần làm — tất cả trong `frontend/`

| Vùng | File | Nội dung |
|---|---|---|
| Util | `src/utils/staff.ts` | **Viết lại** `resolveCurrentPartner`; port `isStaff`, `normalizeStaffCode`, `isBlockedByStaffGate` |
| Test | `src/utils/staff.test.ts` | Port + bổ sung case đa đối tác |
| API | `src/configs/api.ts` | +3 endpoint |
| Service | `src/services/user.ts` | +hàm gọi |
| Interface | `src/interfaces/app.ts` | +`visibleModalEventCode`, `visibleModalNotEmployee`, `staffStatus`. **Không** thêm `visibleModalStaffCode`/`staffCodeDismissed` (FE-006) |
| Interface | `src/interfaces/event.ts` | +`isRequireCode`, `staffGateReason` |
| Model | `src/models/main.ts` | +`checkPartnerEmployeeStatus`, `confirmIsStaff` — **giữ nguyên phần bắt lỗi hệ thống** của bản `fecredit` (`models/main.ts:229-244`), đó là cái chống treo modal |
| Component | `src/components/common/modal-not-employee/` | File mới (port, 71 dòng) |
| Component | `src/pages/home/components/modal-event-code/` | File mới (port, 159 dòng + scss) |
| Component | `src/pages/account/components/form-staff/` | Port 79 dòng + **bọc thêm lớp danh sách theo đối tác** |
| Trang | `src/pages/account/index.tsx` | Gắn mục "Thông tin nhân viên" |
| Layout | `src/components/layout/main/header/index.tsx` | Mount modal + cắm hàm kiểm tra |
| Trang | `src/pages/home/_desktop.tsx` | Nối modal nhập mã |
| Điểm nộp bài | `not-logged-in/index.tsx`, `logged-in-view/index.tsx`, `post-modal/index.tsx` | Cắm hàm kiểm tra dùng chung |

### KHÔNG làm

- Không đụng `backend/`, `admin/`
- Không đụng `parasola/`, `fecredit/`, và 12 folder partner còn lại
- Không thêm dòng "Dành cho nhân viên" trên thẻ chiến dịch
- Không sửa món nợ "event list vs event detail tính `isRequireCode` khác nhau"
- Không copy `resolveCurrentPartner` nguyên xi
- Không suy trạng thái gate từ `user.statusStaff`
- Không tự bật modal chặn lúc tải trang
- Không đoán "đối tác hiện tại" khi không xác định được
- Không phân nhóm nhân viên dưới mọi hình thức (segment đã gỡ ở PRD v5.0)

---

## 9. Assumptions

1. Số đối tác hiển thị trên site đủ nhỏ để gọi `status-employee` lần lượt mà không cần endpoint gộp. Nếu sai thì bổ sung một endpoint trả trạng thái nhiều đối tác trong một request (hiện đang Out of Scope)
3. `frontend/` tiếp tục dùng Umi + dva
4. Trạng thái nhân viên gắn theo đối tác, không phải toàn hệ thống (đã verify ở backend)

---

## 10. Out of Scope

- **Modal xác nhận nhân viên chủ động** — quyết định không làm, lý do ở FE-006
- Đổi hành vi modal chủ động của `fecredit`/`parasola`
- Endpoint gộp trả trạng thái nhân viên của nhiều đối tác trong một request — chỉ làm nếu Assumption #1 sai
- UI `parasola/` lên `release`
- 12 folder partner còn lại
- Dòng "Dành cho nhân viên" trên thẻ chiến dịch
- Sửa món nợ `isRequireCode` giữa hai màn
- Phân nhóm nhân viên

---

## 11. Traceability — map sang PRD v5.1

| PRD v5.1 | PRD này | Quan hệ |
|---|---|---|
| FR-001…FR-008 (model, API, gate) | — | Đã xong, dùng lại nguyên |
| FR-009 (modal xác nhận trên FE) | **FE-006** | **Cố ý KHÔNG port** — khác biệt UX duy nhất so với 2 app white-label, lý do ở FE-006.2 |
| FR-010 (mục Thông tin nhân viên) | **FE-005** | **Đặc tả lại** — từ một khối thành danh sách theo đối tác |
| FR-011 (cờ `isRequireCode` ra FE) | **FE-003** | Áp thẳng |
| FR-012 (modal không đủ điều kiện) | **FE-004** | Áp thẳng, thêm yêu cầu tên đối tác động |
| FR-013 (bật/tắt theo đối tác) | **FE-007** | Không cần code, nhưng **ý nghĩa cờ đã đổi** — xem dưới |
| FR-014…FR-017 (admin, thống kê, backfill) | — | Đã xong |
| — | **FE-001** | **Mới hoàn toàn** — PRD v5.1 không có khái niệm này vì giả định 1 đối tác = 1 app |
| — | **FE-002** | **Mới** — PRD v5.1 không lường app có nhiều điểm mở form |

**Ghi chú về FR-013:** `options.enableStaffCode` là cờ theo **đối tác**, không theo app. Trước task này, "bật cờ cho đối tác X" thực tế = "bật trên app white-label của X". Sau task này, bật cờ sẽ ảnh hưởng **cả app white-label lẫn `frontend/`**, nếu đối tác đó xuất hiện trên domain ACCESSTRADE. Ops cần biết điều này trước khi bật thêm đối tác nào.

---

## 12. Resolved Questions

| Câu hỏi | Chốt (03/09/2026) |
|---|---|
| Sửa PRD v5.1 lên v6 hay viết addendum? | **Cả hai đều không** — task riêng, PRD riêng. v5.1 giữ nguyên Final |
| Mục "Thông tin nhân viên" đặt ở đâu? | **Danh sách theo đối tác ở `/tai-khoan`** (FE-005) |
| Có port dòng "Dành cho nhân viên" trên thẻ chiến dịch? | **Không** |
| Có đưa UI `parasola/` lên `release` cùng đợt? | **Không**, task riêng |
| Phạm vi bắt buộc của task? | **Gate nộp bài + 2 modal chặn** (FE-002, FE-003, FE-004) + FE-005 |
| Giao diện lấy từ đâu? | **Bám style sẵn có của `frontend/`**, không chờ thiết kế riêng. Ràng buộc: không được lỗi UI (NFR-006) |
| Câu chữ trong modal? | Chỉ cần **hiện đúng tên đối tác**; không cần bản copy riêng |
| Bộ test case nghiệm thu? | **Có người viết riêng**, ngoài phạm vi PRD |
| Đối tác nào bật cờ và có trên `frontend/`? | **FE CREDIT** — đã xác nhận bằng API công khai 03/09, kèm một chiến dịch đang bật `applyForStaff`. Task lên **P1** |
| Có port modal xác nhận nhân viên chủ động không? | **KHÔNG** — chỉ chặn lúc bấm nộp bài + mục khai ở Hồ sơ. Khác biệt có chủ ý so với `fecredit`/`parasola`, lý do ở FE-006 |

---

## 13. Open Questions

1. ~~Đối tác nào vừa bật cờ vừa có mặt trên `frontend/`?~~ → **Đã trả lời: FE CREDIT.** Còn lại một câu cần BE xác nhận: `options.enableStaffCode` của FE CREDIT trên prod đang là `true` đúng không? (`status-employee` yêu cầu đăng nhập nên không tự tra được.)
2. Có nên đưa `fecredit`/`parasola` về cùng hành vi với `frontend/` (bỏ modal chủ động) không? **Ngoài phạm vi task này**, nhưng nếu sản phẩm thấy lập luận ở FE-006.2 cũng đúng với app white-label thì mở task riêng. Hiện hai app đó giữ nguyên.
3. ~~`user.partnerApproval[]` có đủ để dựng danh sách ở FE-005 không?~~ → **Đã tra code 03/09: sai nguồn, trường này nằm trên `user-socials`.** FE-005 dùng `mainState.partners`. Xem khối cảnh báo trong FE-005.
4. ~~Site ACCESSTRADE hiển thị bao nhiêu đối tác?~~ → **17** (đo 03/09). Với 17 request `status-employee` thì FE-005 phải giới hạn song song và render dần — vẫn chấp nhận được, chưa cần endpoint gộp. Ngưỡng cần xem lại: khoảng 30.

---

## 14. Revision History

| Version | Date | Thay đổi |
|---|---|---|
| 1.0 | 2026-09-03 | Bản đầu. Tách khỏi PRD employee-code v5.1 thành task riêng. Chốt phạm vi: FE-002 → FE-005 + FE-007. FE-006 để treo |
| 1.1 | 2026-09-03 | Sửa nguồn dữ liệu của FE-005: `partnerApproval` là sai nguồn (nằm trên `user-socials`), đổi sang `mainState.partners`. Gỡ Assumption tương ứng |
| 1.4 | 2026-09-03 | **Chốt FE-006: không port modal xác nhận chủ động.** Ghi rõ hai app white-label vẫn còn modal đó (đã đọc code, không suy đoán) nên đây là khác biệt có chủ ý chứ không phải parity. Gỡ epic E6, gỡ 2 field state và bộ icon khỏi scope. FE-005 nâng thành đường khai duy nhất |
| 1.3 | 2026-09-03 | Phân tích sâu FE-006: cơ chế bật/tắt modal đọc từ backend, ba hệ quả thật của phương án A (backfill không phủ người chưa tham gia, link chiến dịch cũng bị chặn, upsert tạo bản ghi), biến thể A′ bất khả thi với API hiện tại, A″ khả thi. Đổi khuyến nghị từ A sang **B trước** |
| 1.2 | 2026-09-03 | Xác nhận bằng API công khai: FE CREDIT có trên site ACCESSTRADE và đang có chiến dịch `applyForStaff` → nâng lên **P1**. Chốt hướng giao diện (bám style sẵn có, NFR-006), tên đối tác động, bộ test case ngoài phạm vi. Đo được 17 đối tác trên site |
