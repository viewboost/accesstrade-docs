# Tài liệu thiết kế kỹ thuật — Luồng xác thực mã nhân viên trên ứng dụng đa đối tác (`frontend/`)

| | |
|---|---|
| **Mã tài liệu** | SDD-AMB-STAFF-FE-001 |
| **Phiên bản** | 3.0 |
| **Ngày ban hành** | 2026-09-04 |
| **Người biên soạn** | Nguyễn Đăng Định |
| **Người rà soát** | Thành Trung |
| **Trạng thái** | Bản thảo |
| **Tài liệu yêu cầu** | [PRD-AMB-STAFF-FE-001](./prd-staff-code-frontend-2026-09-03.md) phiên bản 3.0 |
| **Kho mã nguồn** | `AT-Core/ambassador` |
| **Nhánh tham chiếu** | `release` — mọi số hiệu dòng trong tài liệu đo trên `origin/release` ngày 2026-09-04 |

---

## Quy ước ngôn ngữ

Áp dụng quy ước động từ tình thái của tài liệu yêu cầu (PHẢI, KHÔNG ĐƯỢC, NÊN, CÓ THỂ theo RFC 2119). Mã định danh yêu cầu `FE-0xx` tham chiếu tới tài liệu yêu cầu.

---

## 1. Mục đích và phạm vi

### 1.1 Mục đích

Tài liệu mô tả phương án hiện thực hoá PRD-AMB-STAFF-FE-001 phiên bản 3.0.

### 1.2 Phạm vi

Toàn bộ thay đổi nằm trong thư mục `frontend/`. Tầng dịch vụ, phân hệ quản trị, cơ sở dữ liệu và cấu hình hạ tầng không phát sinh thay đổi; các thành phần này đã hoàn thiện và hiện diện trên nhánh `release` (tài liệu yêu cầu, Mục 2.2).

### 1.3 Đối tượng đọc

Kỹ sư phát triển giao diện thực hiện hạng mục, kỹ sư rà soát mã nguồn, kỹ sư kiểm thử.

---

## 2. Nguyên tắc thiết kế

| # | Nguyên tắc | Diễn giải |
|---|---|---|
| P1 | Tái sử dụng bản cài đặt đã qua kiểm thử | Nguồn tham chiếu là `fecredit/` trên nhánh `release` |
| P2 | Không nhân bản logic nghiệp vụ | Tầng giao diện đọc lại cờ do backend trả về; không tái hiện điều kiện kiểm soát |
| P3 | Không suy đoán khi dữ liệu không xác định | Áp dụng cho việc phân giải đối tác hiện tại (Mục 3.1) |
| P4 | Tập trung điểm kiểm soát | Logic kiểm soát nằm trong một đơn vị dùng chung, không nhân bản theo điểm gọi |
| P5 | Kiểm chứng khác biệt nền tảng trước khi tái sử dụng | Mục 3 liệt kê bốn khác biệt đã xác minh |

**Lưu ý áp dụng P1.** `frontend/` không phải bản sao của `fecredit/`. Bốn khác biệt hạ tầng tại Mục 3 dẫn tới bốn dạng lỗi khác nhau nếu tái sử dụng nguyên trạng. Mục 3 cần được đọc trước khi bắt đầu hiện thực hoá.

### 2.1 Bảng đối chiếu nguồn — đích

| Chức năng | Nguồn (`fecredit/`) | Đích (`frontend/`) | Mức độ thay đổi |
|---|---|---|---|
| Tiện ích phân loại và phân giải đối tác | `src/utils/staff.ts` (100 dòng) | `src/utils/staff.ts` | Viết mới hàm phân giải đối tác |
| Kiểm thử đơn vị | `src/utils/staff.test.ts` (21 dòng) | `src/utils/staff.test.ts` | Tái sử dụng, bổ sung trường hợp |
| Cấu hình endpoint | `src/configs/api.ts` | tương ứng | Bổ sung 3 mục |
| Tầng dịch vụ | `src/services/user.ts`, `event.ts`, `partner.ts` | tương ứng | Bổ sung 3 hàm; thay đổi cách xử lý lỗi |
| Trạng thái ứng dụng | `src/models/main.ts` | tương ứng | Bổ sung 3 thuộc tính, 2 tác vụ |
| Kiểu dữ liệu | `src/interfaces/app.ts`, `event.ts` | tương ứng | Bổ sung thuộc tính |
| Hộp thoại nhập mã tham gia | `src/pages/home/components/modal-event-code/` | tương ứng | Tái sử dụng |
| Hộp thoại không đủ điều kiện | `src/components/common/modal-not-employee/` | tương ứng | Tái sử dụng khung, **bổ sung ô nhập mã và hai biến thể** |
| Mục tại trang Hồ sơ | `src/pages/account/components/form-staff/` | — | **Không thực hiện** (FE-005 gỡ ở PRD 3.0) |
| Kiểm soát tại điểm nộp bài | 3 điểm | 3 điểm khác | Gom về một đơn vị |
| Hộp thoại xác nhận chủ động | `src/…/modal-staff-code.tsx` | — | Không thực hiện (FE-006) |

### 2.2 Ràng buộc bắt buộc

| # | Ràng buộc |
|---|---|
| C1 | KHÔNG ĐƯỢC suy đoán đối tác hiện tại khi tuyến định tuyến không mang tham số `:partner` |
| C2 | KHÔNG ĐƯỢC suy diễn trạng thái kiểm soát tại tầng giao diện từ `user.statusStaff` |
| C3 | KHÔNG ĐƯỢC tự kích hoạt hộp thoại khi tải trang |
| C4 | KHÔNG ĐƯỢC tái sử dụng `modal-staff-code.tsx` cùng các thuộc tính trạng thái đi kèm |
| C5 | KHÔNG ĐƯỢC phát sinh thay đổi tại `backend/`, `admin/`, `parasola/`, `fecredit/` và 12 thư mục đối tác còn lại |
| C6 | Điều kiện hiển thị ô nhập mã PHẢI bám `staffGateReason`; KHÔNG ĐƯỢC bám `isOpenInputStaffCode` (Mục 4.8) |
| C7 | KHÔNG ĐƯỢC phát sinh yêu cầu mạng tỉ lệ với số đối tác của ứng dụng |

---

## 3. Phân tích khác biệt nền tảng

### 3.1 Hàm phân giải đối tác hiện tại

**Bản cài đặt tham chiếu** (`fecredit/src/utils/staff.ts:34-45`):

```ts
if (mainState?.partnerDetail?._id) return mainState.partnerDetail;
if (mainState?.isOwnerPartner && mainState?.partners?.length === 1) return mainState.partners[0];
return undefined;
```

**Phân tích.** Nhánh điều kiện thứ hai không bao giờ thoả trên `frontend/`:

| Bước | Tham chiếu |
|---|---|
| Handler lấy tên miền từ header Origin | `backend/pkg/public/handler/partner.go:203` |
| Dịch vụ lọc theo `allowDomains` | `backend/pkg/public/service/partner.go:308` |
| `AllowHeaderPartner = len(Data) > 1` | `backend/pkg/public/service/partner.go:376` |
| `isOwnerPartner = !allowHeaderPartner` | `frontend/src/models/main.ts:243` |

Ứng dụng trả về 17 đối tác (đo ngày 2026-09-03), do đó `isOwnerPartner` luôn bằng `false`.

**Hệ quả nếu tái sử dụng nguyên trạng:** suy giảm chức năng không phát sinh lỗi và không ghi nhật ký.

**Thiết kế:**

```ts
/**
 * Đối tác hiện tại của trang đang hiển thị.
 *
 * `frontend/` là ứng dụng đa đối tác: chỉ nhánh định tuyến dưới `/:partner/`
 * mang thông tin đối tác (config/routes.ts:114-155). Các tuyến dùng chung —
 * /tai-khoan, /thong-bao, /trang-ca-nhan — không gắn với đối tác nào.
 *
 * Giá trị undefined KHÔNG phải trường hợp lỗi: nó chọn biến thể rút gọn của
 * hộp thoại FE-004 (Mục 4.8). Không suy đoán, vì giá trị sai dẫn tới ghi
 * user-partners.statusStaff vào sai đối tác, ảnh hưởng điều kiện xét thưởng.
 */
export function resolveCurrentPartner(mainState: { partnerDetail?: any }): any | undefined {
  return mainState?.partnerDetail?._id ? mainState.partnerDetail : undefined;
}
```

Nhánh `isOwnerPartner` PHẢI được loại bỏ hoàn toàn thay vì giữ lại dưới dạng mã không được thực thi.

### 3.2 Xử lý cờ `skipErrorHandler` tại tầng chặn lỗi toàn cục

Đây là khác biệt có rủi ro cao nhất trong hạng mục: bản cài đặt sai vẫn hoạt động đúng ở luồng thành công và chỉ biểu hiện khi phát sinh lỗi.

**`fecredit/src/app.tsx:76-92`** — cờ chỉ vô hiệu hoá thông báo, giá trị lỗi vẫn được trả về nơi gọi:

```ts
if (!skipErrorHandler && error?.data?.message) {
  toast.error(error.data.message);
}
return error?.data;
```

**`frontend/src/app.tsx:75-94`** — cờ khiến hàm thoát sớm, giá trị trả về là `undefined`:

```ts
if (skipErrorHandler) return;
destroyLoading();
if (error?.data?.message) {
  toast.error(error.data.message);
} else if (!error?.response && isBrowser()) {
  toast.error('Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối và thử lại.');
}
return error?.data;
```

**Hệ quả nếu tái sử dụng nguyên trạng.** Hàm dịch vụ của `fecredit` (`src/services/user.ts:28-38`) đặt `skipErrorHandler: true`. Trên `frontend/`, mọi lỗi nghiệp vụ sẽ khiến tầng trạng thái nhận `undefined`, phép truy cập `response.code` ném `TypeError` tới trình xử lý lỗi toàn cục của dva, và người dùng không nhận được thông báo nào.

**Thiết kế:** các hàm dịch vụ mới trên `frontend/` KHÔNG ĐƯỢC đặt `skipErrorHandler`.

| | `fecredit` | `frontend` |
|---|---|---|
| Tham số dịch vụ | `skipErrorHandler: true` | không đặt |
| Nơi hiển thị lỗi | hàm gọi lại tự gọi `toast.error` | trình xử lý lỗi toàn cục |
| Giá trị tầng trạng thái nhận được khi lỗi | `error.data` | `error.data` |
| Yêu cầu với hàm gọi lại | hiển thị thông báo lỗi | KHÔNG hiển thị lại — sẽ phát sinh hai thông báo chồng nhau |

Phương án này còn tận dụng sẵn nhánh xử lý lỗi tầng mạng của `frontend/` (`app.tsx:85-91`), do đó không cần cờ trạng thái phụ như bản cài đặt tham chiếu (`fecredit/src/models/main.ts:229-244`).

**Ngoại lệ.** Hộp thoại FE-003 yêu cầu hiển thị lỗi tại chỗ thay vì thông báo nổi. Thiết kế vẫn không dùng `skipErrorHandler`: hàm gọi lại đọc `response.message` để hiển thị tại chỗ, và chấp nhận có thêm một thông báo nổi. Trường hợp cần loại bỏ thông báo trùng, phương án là điều chỉnh trình xử lý lỗi toàn cục của `frontend/` về cùng hành vi với `fecredit`; thay đổi này ảnh hưởng toàn ứng dụng và PHẢI được tách thành hạng mục riêng.

### 3.3 Điểm khởi tạo biểu mẫu nộp bài

Kết quả đo trên `origin/release`:

| # | Trình xử lý | Thành phần kích hoạt |
|---|---|---|
| 1 | `src/components/layout/main/header/index.tsx:157` | `:374` |
| 2 | `src/pages/home/components/not-logged-in/index.tsx:42` | `:178` |
| 3 | `src/pages/home/components/logged-in-view/index.tsx:31` | `:129` |

Cả ba trình xử lý đều chỉ thực hiện một thao tác — đặt `openPostContentModal: true` — nên việc bổ sung bước kiểm tra là thay thế thân hàm.

**Điểm không thuộc phạm vi kiểm soát.** `src/pages/home/components/post-modal/index.tsx:72,89` khôi phục biểu mẫu sau khi đóng hộp thoại phụ Threads/Facebook (`handleCloseThreadsModal`, `handleCloseFacebookModal`). Bổ sung kiểm tra tại đây buộc người dùng đi qua cổng kiểm soát hai lần trong cùng một luồng.

**Tái sử dụng thành phần.** `PostContentModal` được gắn tại `src/layouts/event-detail/index.tsx:292` và `src/pages/home/components/logged-in-view/index.tsx:163`. `src/pages/profile/index.tsx:118` hiển thị lại `LoggedInView` cho tuyến `/trang-ca-nhan`. Do đó đơn vị kiểm tra PHẢI nhận dữ liệu chiến dịch qua tham số từ nơi gọi, không đọc trực tiếp `homeState.eventHome`.

**Khác biệt so với bản tham chiếu.** `src/pages/home/components/statistic/index.tsx` chỉ nhận `{ eventHome, loading }` và không chứa thành phần khởi tạo biểu mẫu; `fecredit` có. Không cần thay đổi tại tệp này.

### 3.4 Quy ước tầng cấu hình API và tầng dịch vụ

| Hạng mục | `fecredit` | `frontend` |
|---|---|---|
| Không gian tên endpoint | `user`, `events`, `partners` | `user`, `event` (số ít), `partners` |
| Cách khai báo dịch vụ | đối tượng nguyên khối | hàm đặt tên, gom tại `export default` cuối tệp |
| Truy vấn chi tiết đối tác | theo định danh | theo slug (`configs/api.ts:381`) |

Không tạo tệp dịch vụ riêng. Ba hàm mới được bổ sung vào tệp tương ứng với tài nguyên: `confirmIsStaff` vào `services/user.ts`, `getStatusEmployee` vào `services/partner.ts`, `inputCodeJoinEvent` vào `services/event.ts`.

---

## 4. Thiết kế chi tiết

### 4.1 Tầng cấu hình API — `src/configs/api.ts`

```ts
// Không gian tên `user`, cạnh acceptPrivacy (dòng 79-82)
confirmIsStaff: (): IApi => ({
  url: '/users/confirm-is-staff',
  method: methods.post,
}),

// Không gian tên `event` (dòng 316-357)
inputCodeJoinEvent: (id): IApi => ({
  url: `/events/${id}/input-code-join-event`,
  method: methods.post,
}),

// Không gian tên `partners` (dòng 373-388)
statusEmployee: (id: string): IApi => ({
  url: `/partners/${id}/status-employee`,
  method: methods.get,
}),
```

### 4.2 Tầng dịch vụ

```ts
// services/user.ts — không đặt skipErrorHandler, xem Mục 3.2
const confirmIsStaff = (data) => {
  const api = ApiConst.user.confirmIsStaff();
  return request.call(api.url, { method: api.method, data, authRequired: true });
};

// services/partner.ts
const getStatusEmployee = (id: string) => {
  const api = ApiConst.partners.statusEmployee(id);
  return request.call(api.url, { method: api.method });
};

// services/event.ts
const inputCodeJoinEvent = (id, data) => {
  const api = ApiConst.event.inputCodeJoinEvent(id);
  return request.call(api.url, { method: api.method, data });
};
```

Mỗi hàm PHẢI được bổ sung vào khối `export default` ở cuối tệp tương ứng.

### 4.3 Hợp đồng dữ liệu

**`GET /partners/:id/status-employee`** — yêu cầu xác thực (`backend/pkg/public/router/partner.go:24`). Cấu trúc phản hồi (`backend/pkg/public/model/response/partner.go:31-43`):

| Thuộc tính | Kiểu | Ý nghĩa |
|---|---|---|
| `isOpenInputStaffCode` | `boolean` | Cờ điều khiển hộp thoại xác nhận. Không sử dụng trong hạng mục này (FE-006) |
| `enabled` | `boolean` | Đối tác đã bật tính năng. **Đây là điều kiện lọc của FE-005** |
| `statusStaff` | `string?` | `employee` \| `not_employee` \| `not_verify`, hoặc vắng mặt |
| `staffCode` | `string?` | Chỉ trả về cho chính chủ tài khoản |

Điều kiện lọc PHẢI dựa trên `enabled`, không dựa trên sự tồn tại của đối tượng phản hồi: backend vẫn trả về đối tượng đầy đủ khi đối tác chưa bật tính năng (`staff_code.go:47-49`).

**API chi tiết chiến dịch** bổ sung hai thuộc tính (`backend/pkg/public/service/event.go:1292-1293`):

| Thuộc tính | Kiểu | Ý nghĩa |
|---|---|---|
| `isRequireCode` | `boolean` | Người dùng còn phải nhập mã tham gia riêng |
| `staffGateReason` | `'staff' \| ''` | Lý do bị cổng kiểm soát từ chối; chuỗi rỗng nghĩa là đủ điều kiện |

### 4.4 Tầng trạng thái — `src/models/main.ts`

**Trạng thái khởi tạo:**

```ts
const initState: IMainState = {
  // …giữ nguyên các thuộc tính hiện có
  visibleModalEventCode: false,
  visibleModalNotEmployee: false,
  staffStatus: undefined,
};
```

Không bổ sung `visibleModalStaffCode` và `staffCodeDismissed` (ràng buộc C4).

**Hai tác vụ bất đồng bộ:**

```ts
// Tiền kiểm cờ tính năng của đối tác, gọi khi hộp thoại FE-004 mở (Mục 4.8).
// Đúng MỘT đối tác, đúng MỘT lần, chỉ với người dùng đã bị chặn — ràng buộc C7.
// Không điều khiển hiển thị hộp thoại xác nhận như bản tham chiếu.
*checkPartnerEmployeeStatus({ payload, callback }, { call, put }) {
  const response = yield call(servicePartner.getStatusEmployee, payload.partnerId);
  if (response?.code !== AppConst.ResponseCode.success) return;
  yield put({ type: 'updateState', payload: { staffStatus: response.data?.data } });
  callback?.(response.data?.data);
},

// Dùng chung cho mọi điểm khai báo mã. Backend cho phép ghi đè.
//
// Không bọc try/catch như bản tham chiếu: hàm dịch vụ không đặt skipErrorHandler
// nên trình xử lý lỗi toàn cục (app.tsx:75-94) đã hiển thị thông báo và trả
// error.data về đây. Hàm gọi lại chỉ xử lý nhánh thành công (Mục 3.2).
*confirmIsStaff({ payload, callback }, { call }) {
  const response = yield call(serviceUser.confirmIsStaff, payload.data);
  callback?.(response);
},
```

`checkPartnerEmployeeStatus` chỉ được gọi tại thời điểm hộp thoại FE-004 mở. Tác vụ này KHÔNG ĐƯỢC gắn vào hiệu ứng khởi tạo của thành phần đầu trang như bản tham chiếu (`fecredit/…/header/index.tsx:100-107`) — đó chính là cơ chế kích hoạt hộp thoại chủ động mà FE-006 không áp dụng, và cũng là cách phát sinh yêu cầu mạng cho mọi người dùng thay vì cho người bị chặn.

### 4.5 Tầng kiểu dữ liệu

```ts
// interfaces/app.ts — bổ sung vào IMainState (kết thúc tại dòng 229)
visibleModalEventCode?: boolean;
visibleModalNotEmployee?: boolean;
staffStatus?: IStatusEmployee;

// interfaces/event.ts — bổ sung vào IEventHome (dòng 3-26)
isRequireCode?: boolean;
staffGateReason?: 'staff' | '';
```

Kiểu `IStatusEmployee` khai báo tại `interfaces/app.ts` theo hợp đồng dữ liệu Mục 4.3.

Thuộc tính `Options` của `IEventHome` (dòng 11) đã tồn tại. Không bổ sung `applyForStaff` vì hạng mục không hiển thị nhãn nhóm đối tượng trên thẻ chiến dịch.

### 4.6 Đơn vị kiểm soát dùng chung — FE-002

**Hàm quyết định:**

```ts
// utils/staff.ts
export type StaffGateAction = 'blocked' | 'require-code' | 'allow';

/**
 * Xác định hành vi khi người dùng thao tác nộp bài.
 *
 * Chỉ đọc lại cờ do backend trả về. statusStaff gắn theo từng cặp người dùng ×
 * đối tác (UserPartnerRaw.StatusStaff), trong khi tầng giao diện chỉ có một giá
 * trị chung — so sánh dựa trên giá trị đó cho kết quả sai trên ứng dụng đa đối
 * tác. Backend tính staffGateReason bằng chính hàm thực thi cổng kiểm soát
 * (public/service/content.go:132).
 *
 * Thứ tự: kiểm tra điều kiện nhân viên trước điều kiện mã tham gia. Người dùng
 * không đủ điều kiện thì việc hỏi mã không có ý nghĩa, và hai hộp thoại không
 * được hiển thị đồng thời.
 */
export function resolveStaffGateAction(eventHome?: {
  staffGateReason?: string;
  isRequireCode?: boolean;
}): StaffGateAction {
  if (eventHome?.staffGateReason) return 'blocked';
  if (eventHome?.isRequireCode) return 'require-code';
  return 'allow';
}
```

**Hook điều phối:**

```ts
// hooks/use-post-content-gate.ts
export function usePostContentGate(eventHome) {
  const dispatch = useDispatch();
  return () => {
    switch (resolveStaffGateAction(eventHome)) {
      case 'blocked':
        dispatch({ type: 'mainState/updateState',
          payload: { visibleModalNotEmployee: true, visibleModalEventCode: false } });
        return;
      case 'require-code':
        dispatch({ type: 'mainState/updateState', payload: { visibleModalEventCode: true } });
        return;
      default:
        dispatch({ type: 'mainState/updateState', payload: { openPostContentModal: true } });
    }
  };
}
```

Ba điểm khởi tạo tại Mục 3.3 thay thế thân hàm bằng hook này, với `eventHome` truyền từ nơi gọi.

**Vị trí gắn hai hộp thoại.** Hai hộp thoại PHẢI được gắn tại thành phần đầu trang (`src/components/layout/main/header/index.tsx`), không gắn trong trang chi tiết chiến dịch. Cơ sở: điểm khởi tạo số 3 được tái sử dụng trên tuyến `/trang-ca-nhan` (Mục 3.3), nơi không có bố cục chi tiết chiến dịch — gắn trong trang dẫn tới trường hợp thao tác bị chặn mà không hiển thị hộp thoại nào. Ràng buộc này đã được ghi nhận tại bản tham chiếu (`fecredit/…/header/index.tsx:508-512`).

**Điều kiện hiển thị:**

```tsx
<ModalNotEmployee
  visible={
    !!visibleModalNotEmployee &&
    !!eventHome?.staffGateReason &&   // chuyển chiến dịch khác: hộp thoại tự ẩn
    !visibleModalLogin &&
    !visibleModalCompleteReg
  }
  partner={resolveCurrentPartner(mainState)}   // undefined ⇒ biến thể rút gọn
  …
/>
```

Điều kiện hiển thị đọc `staffGateReason`, KHÔNG đọc `isOpenInputStaffCode` — ràng buộc C6, cơ sở tại Mục 4.8.3.

### 4.7 Hộp thoại nhập mã tham gia riêng — FE-003

Tái sử dụng `fecredit/src/pages/home/components/modal-event-code/` (159 dòng cùng tệp định kiểu).

**Luồng xử lý:**

1. Người dùng nhập mã
2. Gọi `POST /events/:id/input-code-join-event`
3. Tải lại dữ liệu chi tiết chiến dịch qua `homeState/getEventBySlug` (`pages/home/model.ts:80-93`)
4. Mở biểu mẫu nộp bài

Tham số của bước 3 là `{ slug, partner }`, trong đó `partner` là **định danh**, không phải slug.

Giá trị `isRequireCode` được backend tính từ `user-events.options.codeInput` (`backend/pkg/public/service/event.go:1190-1206`); tầng giao diện KHÔNG ĐƯỢC tự suy diễn kết quả sau khi gửi mã.

Mã nhập vào được chuẩn hoá tại thời điểm nhập bằng `normalizeStaffCode` (viết hoa, loại bỏ khoảng trắng hai đầu).

Nội dung hiển thị KHÔNG ĐƯỢC gọi đối tượng này là "mã nhân viên": mã được đối chiếu trực tiếp với `event.Options.StaffCodes` và không tra cứu bảng `manage-codes` (`event.go:1218-1245`).

### 4.8 Hộp thoại chặn kèm khai báo — FE-004

Tái sử dụng khung của `fecredit/src/components/common/modal-not-employee/` (71 dòng), bổ sung ô nhập mã. Đây là **đường khai báo duy nhất** của `frontend/`.

#### 4.8.1 Hai biến thể

| Biến thể | Điều kiện | Nội dung |
|---|---|---|
| Đầy đủ | `resolveCurrentPartner()` trả về đối tác **và** `enabled === true` | Giải thích + ô nhập mã + nút xác nhận |
| Rút gọn | Không xác định được đối tác, **hoặc** `enabled === false` | Chỉ giải thích, kèm lối đi phù hợp |

Trên `/trang-ca-nhan` luôn là biến thể rút gọn: tuyến này có thao tác nộp bài nhưng không mang đối tác trong trạng thái ứng dụng (Mục 3.3). Lối đi dẫn tới trang chiến dịch, nơi biến thể đầy đủ khả dụng.

Quyết định không bổ sung trường `partner` vào `EventDetailResponse` để nhập được ở mọi nơi — xem PRD, DEC-13.

#### 4.8.2 Tiền kiểm cờ tính năng

Khi hộp thoại mở và đã xác định được đối tác, gọi `checkPartnerEmployeeStatus` với định danh đối tác đó và đọc cờ `enabled`.

Cơ sở: `checkStaffGate` không kiểm `PartnerOpts.EnableStaffCode` (`backend/pkg/public/service/staff_gate.go:23-46`) trong khi `ConfirmIsStaff` có kiểm (`staff_code.go:99`), nên tồn tại cấu hình mà người dùng bị chặn nhưng không khai báo được. Tiền kiểm tránh việc hiển thị một ô nhập chắc chắn thất bại.

Chi phí: một yêu cầu, một đối tác, chỉ với người dùng đã bị chặn. Đây là ranh giới của ràng buộc C7.

Lớp phòng vệ thứ hai: khi `ConfirmIsStaff` trả mã lỗi tương ứng, hiển thị thông báo hướng dẫn liên hệ bộ phận hỗ trợ, KHÔNG hiển thị nguyên văn thông báo backend.

#### 4.8.3 ⚠️ Điều kiện hiển thị PHẢI bám `staffGateReason`

Ràng buộc C6. Đây là chỗ dễ cài đặt sai nhất của yêu cầu này.

| Cờ | Hành vi sau khi người dùng đã trả lời | Dùng được làm điều kiện hiển thị? |
|---|---|---|
| `staffGateReason` | Chỉ rỗng khi trạng thái là `employee` | **Có** |
| `isOpenInputStaffCode` | `false` vĩnh viễn, kể cả khi trả lời "không thuộc đối tác" (`staff_code.go:61-66`) | **Không** |

`ConfirmIsStaff` cho phép ghi đè theo chiều `not_employee → employee`, nên người đã lỡ chọn "không thuộc" và người bị gán trạng thái bởi tiến trình backfill vẫn PHẢI được mời nhập lại, không giới hạn số lần.

Dùng nhầm `isOpenInputStaffCode` sẽ chặn đúng nhóm cần khai lại. Khiếm khuyết chỉ biểu hiện với người đã từng trả lời, nên không lộ ra trong kiểm thử bằng tài khoản mới. Kịch bản IT-13 và điều kiện rà soát tại Mục 7.3 gác điểm này.

#### 4.8.4 Luồng xác nhận

1. Người dùng nhập mã, chuẩn hoá tại thời điểm nhập bằng `normalizeStaffCode`
2. Gọi `POST /users/confirm-is-staff` với `{ partner, isStaff: true, code }`
3. Tải lại dữ liệu chi tiết chiến dịch để backend tính lại `staffGateReason`
4. Mở biểu mẫu nộp bài

Tầng giao diện KHÔNG ĐƯỢC tự suy diễn rằng điều kiện đã thoả sau khi gọi thành công.

#### 4.8.5 Nội dung hiển thị

Tên đối tác lấy động từ `partnerDetail?.name`. Bản nguồn cố định chuỗi tên đối tác (`modal-staff-code.tsx:145`) do chỉ phục vụ một đối tác.

#### 4.8.6 Trường hợp không xử lý được bằng giao diện

Người dùng đã mang trạng thái `employee` nhưng mã đã khai không đúng: họ qua được cổng kiểm soát nên không gặp hộp thoại này, và không tự gỡ nhãn được (`staff_code.go:105-116`). Xử lý qua bộ phận hỗ trợ hoặc phân hệ quản trị.

### 4.9 Mục "Thông tin nhân viên" — FE-005: không thực hiện

Gỡ khỏi phạm vi ở PRD phiên bản 3.0. Không thay đổi `src/pages/account/`.

Chức năng khai báo và khai báo lại chuyển vào Mục 4.8. Cơ sở đầy đủ tại PRD, FE-005.

Hệ quả tới thiết kế: không còn bước dựng danh sách đối tác, không còn ràng buộc giới hạn yêu cầu đồng thời, không còn nhu cầu endpoint gộp. `GET /partners/:id/status-employee` vẫn được dùng, nhưng cho một đối tác tại Mục 4.8.2.

### 4.10 Hạng mục không thực hiện — FE-006

Không tạo `modal-staff-code.tsx`. Không bổ sung `visibleModalStaffCode` và `staffCodeDismissed`. Không bổ sung bộ biểu tượng đi kèm. Không gắn `checkPartnerEmployeeStatus` vào hiệu ứng khởi tạo của thành phần đầu trang.

Cơ chế kiểm chứng nêu tại Mục 7.3.

---

## 5. Ánh xạ yêu cầu — thành phần

| Yêu cầu | Thành phần |
|---|---|
| FE-001 | `utils/staff.ts`, `utils/staff.test.ts` |
| FE-002 | `utils/staff.ts`, `hooks/use-post-content-gate.ts`, `header/index.tsx:157`, `not-logged-in/index.tsx:42`, `logged-in-view/index.tsx:31` |
| FE-003 | `pages/home/components/modal-event-code/`, `configs/api.ts`, `services/event.ts` |
| FE-004 | `components/common/modal-not-employee/`, `header/index.tsx`, `models/main.ts`, `services/partner.ts`, `services/user.ts` |
| FE-005 | Không thực hiện — không phát sinh thành phần |
| FE-006 | Không phát sinh thành phần |
| FE-007 | Toàn bộ; kiểm chứng theo Mục 7 |

---

## 6. Kế hoạch triển khai

| # | Hạng mục | Phụ thuộc |
|---|---|---|
| 1 | `utils/staff.ts` và kiểm thử đơn vị | — |
| 2 | Cấu hình endpoint, ba hàm dịch vụ, kiểu dữ liệu, trạng thái, hai tác vụ | — |
| 3 | `hooks/use-post-content-gate.ts` và tích hợp vào ba điểm khởi tạo | 1, 2 |
| 4 | Hộp thoại chặn kèm ô nhập mã và tiền kiểm cờ, gắn tại thành phần đầu trang | 3 |
| 5 | Hộp thoại nhập mã tham gia và bước tải lại dữ liệu chiến dịch | 3 |
| 6 | Kiểm thử hồi quy đối tác chưa bật tính năng và kiểm tra trực quan | 1–5 |

---

## 7. Chiến lược kiểm thử

Bộ ca kiểm thử nghiệm thu do bộ phận kiểm thử phụ trách (PRD, Mục 9.2, phụ thuộc D3). Mục này quy định phần thuộc trách nhiệm nhóm phát triển.

### 7.1 Kiểm thử đơn vị

Hạ tầng sẵn có: `frontend/jest.config.js` (khai báo bí danh `@/`) cùng `umi-test`; hiện có 9 tệp kiểm thử đang vận hành.

| Hàm | Trường hợp |
|---|---|
| `resolveCurrentPartner` | Có `partnerDetail._id`: trả về đúng đối tác. Không có: trả về không xác định. **Có `isOwnerPartner = true` và đúng một đối tác: vẫn trả về không xác định** — chốt chặn hồi quy nhánh của bản tham chiếu |
| `resolveStaffGateAction` | Có `staffGateReason`: `blocked`. Chỉ có `isRequireCode`: `require-code`. Có cả hai: `blocked`. Không có gì: `allow` |
| `isStaff` | `employee`: đúng. `not_employee`, `not_verify`, chuỗi rỗng, không xác định: sai |
| `normalizeStaffCode` | Chữ thường chuyển thành chữ hoa. Khoảng trắng hai đầu bị loại bỏ. Giá trị không xác định trả về chuỗi rỗng |
| Chọn biến thể hộp thoại | Có đối tác và `enabled = true`: biến thể đầy đủ. Không có đối tác: biến thể rút gọn. Có đối tác nhưng `enabled = false`: biến thể rút gọn |

### 7.2 Kiểm thử tích hợp

| # | Kịch bản | Kết quả kỳ vọng |
|---|---|---|
| IT-01 | Chiến dịch không bật điều kiện nào, thao tác tại cả ba điểm khởi tạo | Biểu mẫu mở; không phát sinh yêu cầu mạng bổ sung |
| IT-02 | Chiến dịch có `applyForStaff`, người dùng không phải nhân viên | Cả ba điểm hiển thị hộp thoại FE-004; biểu mẫu không mở |
| IT-03 | Từ hộp thoại FE-004 chuyển tới trang Hồ sơ, khai báo mã hợp lệ | Quay lại thao tác nộp bài thành công |
| IT-04 | Chiến dịch có `staffCodes`, người dùng chưa nhập mã | Hộp thoại FE-003 hiển thị; nhập mã hợp lệ thì biểu mẫu mở tự động |
| IT-05 | Nhập mã không hợp lệ | Thông báo lỗi hiển thị; hộp thoại không đóng |
| IT-06 | Thao tác nộp bài tại `/trang-ca-nhan` | Được kiểm soát đúng |
| IT-07 | Đóng hộp thoại phụ Threads/Facebook rồi quay lại biểu mẫu | Biểu mẫu mở lại; không kiểm soát lần thứ hai |
| IT-08 | Trên `/:partner/:slug`, nhập mã nhân viên hợp lệ trong hộp thoại chặn | Hộp thoại đóng, biểu mẫu nộp bài mở, không cần thao tác bổ sung |
| IT-09 | Trên `/trang-ca-nhan`, bị chặn | Biến thể rút gọn: không có ô nhập, có lối đi tới trang chiến dịch |
| IT-10 | Đối tác có chiến dịch `applyForStaff` nhưng chưa bật `EnableStaffCode` | Biến thể rút gọn kèm hướng dẫn liên hệ hỗ trợ; không hiển thị ô nhập |
| IT-11 | Trang `/tai-khoan` | Không phát sinh yêu cầu `status-employee`; giao diện không đổi so với hiện trạng |
| IT-12 | Mất kết nối mạng khi gửi biểu mẫu | Có thông báo lỗi; giao diện không treo (nhánh `app.tsx:85-91`) |
| **IT-13** | **Người dùng đã từng chọn "không thuộc đối tác" (`statusStaff = not_employee`), sau đó thao tác nộp bài vào chiến dịch nội bộ** | **Vẫn nhận được hộp thoại kèm ô nhập mã; nhập đúng thì khai báo thành công.** Gác ràng buộc C6 |
| IT-14 | Người dùng bị gán trạng thái bởi tiến trình backfill | Như IT-13 |
| IT-15 | Lặp lại IT-13 nhiều lần trong cùng phiên | Không giới hạn số lần mời nhập |

### 7.3 Điều kiện thông qua rà soát mã nguồn

```bash
# C4 — không tái sử dụng hộp thoại xác nhận chủ động
git diff origin/release -- frontend/ | grep -iE "modal-staff-code|visibleModalStaffCode|staffCodeDismissed"
# Kỳ vọng: không có kết quả

# C5 — không phát sinh thay đổi ngoài phạm vi
git diff --stat origin/release -- backend admin parasola fecredit anker flamingo hdbank \
  lusso mbbank tpbank turborg vng vnpay vpbank wildrift yody
# Kỳ vọng: không có kết quả

# C2 — không suy diễn trạng thái kiểm soát từ giá trị chung
grep -rn "user\.statusStaff\|user?.statusStaff" frontend/src
# Kỳ vọng: không có kết quả

# Mục 3.2 — không sử dụng skipErrorHandler trong các hàm dịch vụ mới
git diff origin/release -- frontend/src/services | grep -n "skipErrorHandler"
# Kỳ vọng: không có kết quả

# C6 — không dùng isOpenInputStaffCode làm điều kiện hiển thị
grep -rn "isOpenInputStaffCode" frontend/src
# Kỳ vọng: không có kết quả

# FE-005 đã gỡ — không đụng trang Hồ sơ
git diff --stat origin/release -- frontend/src/pages/account
# Kỳ vọng: không có kết quả

# C7 — status-employee không được gọi theo vòng lặp danh sách đối tác
grep -rn "getStatusEmployee\|status-employee" frontend/src | grep -iE "map|forEach|Promise.all"
# Kỳ vọng: không có kết quả

# Không tái xuất hiện lớp phân nhóm đã loại bỏ tại PRD-AMB-STAFF-001 v5.0
grep -rniE "conditionForAutomatic|resync|SEGMENT_TYPE_|applyForSegment" frontend/src
# Kỳ vọng: không có kết quả

npx umi-test src/utils/staff.test.ts
```

### 7.4 Kiểm tra trực quan (NFR-006)

Thực hiện trên cả desktop và mobile. Nội dung kiểm tra: bố cục hộp thoại ở khung hẹp; chuỗi tên đối tác dài; không có hai hộp thoại hiển thị đồng thời; kiểu dáng thành phần nút — bản tham chiếu đã ghi nhận trường hợp `AppButton` bổ sung lớp `rounded-2` và ghi đè `border-radius` của `.btn-primary`.

---

## 8. Phát hành và vận hành

### 8.1 Chiến lược nhánh

`frontend/` hiện diện trên cả `release` và `develop`. Hạng mục sử dụng **một nhánh cắt từ `release`** và hai yêu cầu hợp nhất: vào `release` và vào `develop`. KHÔNG hợp nhất `develop` ngược vào nhánh nguồn.

### 8.2 Tích hợp liên tục

Tác vụ `build-frontend` chỉ kích hoạt khi có thay đổi trong `frontend/**` (`.github/workflows/build-and-deploy.yml:111-112`), phù hợp với phạm vi hạng mục.

### 8.3 Điều kiện tiên quyết trước khi phát hành

| # | Điều kiện | Bên chịu trách nhiệm |
|---|---|---|
| 1 | Xác nhận `options.enableStaffCode` của đối tác đang được bật. Bắt buộc **trước khi** bất kỳ chiến dịch nào của đối tác bật `applyForStaff` — xem Mục 4.8.2 | Backend / Vận hành |
| 2 | Tiến trình backfill `statusStaff` đã chạy cho đối tác (`admin/service/migration_backfill_staff_status.go`) | Backend |

Hạng mục không phát sinh thay đổi tại backend và phân hệ quản trị, do đó không cần đồng bộ thời điểm phát hành và không có bước di trú dữ liệu.

---

## 9. Rủi ro và biện pháp kiểm soát

| Mã | Rủi ro | Mức độ | Biện pháp |
|---|---|---|---|
| R1 | Tái sử dụng hàm dịch vụ kèm `skipErrorHandler`, dẫn tới lỗi không hiển thị thông báo | Cao | Mục 3.2; điều kiện rà soát tại Mục 7.3 |
| R2 | Tái sử dụng hàm phân giải đối tác nguyên trạng, dẫn tới suy giảm chức năng không phát sinh lỗi | Cao | Mục 3.1; kiểm thử đơn vị tại Mục 7.1 |
| R3 | Bỏ sót một điểm khởi tạo biểu mẫu | Trung bình | Tập trung vào một đơn vị (P4); kịch bản IT-01, IT-02 kiểm cả ba điểm |
| R4 | Gắn hộp thoại trong trang thay vì thành phần đầu trang, dẫn tới thao tác tại `/trang-ca-nhan` bị chặn mà không hiển thị | Trung bình | Mục 4.6; kịch bản IT-06 |
| R5 | **Dùng `isOpenInputStaffCode` làm điều kiện hiển thị**, khiến người đã trả lời "không thuộc đối tác" không khai lại được. Chỉ biểu hiện với tài khoản đã từng trả lời | **Cao** | Ràng buộc C6; Mục 4.8.3; kịch bản IT-13, IT-14; điều kiện rà soát tại Mục 7.3 |
| R6 | Đối tác bật `applyForStaff` nhưng chưa bật `EnableStaffCode`, người dùng bị chặn mà không khai báo được | Trung bình | Tiền kiểm tại Mục 4.8.2; điều kiện tiên quyết tại Mục 8.3; kịch bản IT-10 |
| R7 | Nhân viên không tham gia chiến dịch nội bộ nào sẽ giữ trạng thái `not_employee`, làm giảm độ phủ báo cáo | Thấp | Hạn chế đã chấp nhận; xem PRD, FE-005 và OI-02 |

---

## 10. Vấn đề còn mở

| # | Nội dung | Bên xử lý |
|---|---|---|
| OI-01 | Xác nhận `options.enableStaffCode` của đối tác FE CREDIT trên production đang được bật. Endpoint yêu cầu xác thực nên không tự kiểm chứng được | Backend |
| OI-02 | Hộp thoại FE-003 và FE-004 có chấp nhận hiển thị đồng thời thông báo tại chỗ và thông báo nổi hay không (Mục 3.2). Trường hợp không chấp nhận, cần điều chỉnh trình xử lý lỗi toàn cục bằng một hạng mục riêng | Sản phẩm / Kỹ thuật |

---

## 11. Lịch sử sửa đổi

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 3.0 | 2026-09-04 | Đồng bộ với PRD 3.0 sau rà soát của Thành Trung: gỡ thiết kế mục tại trang Hồ sơ, chuyển khai báo vào hộp thoại chặn với hai biến thể; bổ sung tiền kiểm cờ tính năng cho đúng một đối tác; bổ sung ràng buộc C6 (bám `staffGateReason`) và C7 (không phát sinh yêu cầu tỉ lệ số đối tác); bổ sung kịch bản IT-13…IT-15 và rủi ro R5…R7 |
| 2.0 | 2026-09-04 | Chuẩn hoá toàn bộ văn phong theo khuôn tài liệu thiết kế kỹ thuật: bổ sung quy ước động từ tình thái, tách Nguyên tắc thiết kế và Ràng buộc bắt buộc thành mục riêng có mã định danh, chuyển kịch bản kiểm thử sang dạng bảng có mã, tách Phát hành & Vận hành khỏi Rủi ro. Nội dung kỹ thuật và các tham chiếu mã nguồn giữ nguyên |
| 1.0 | 2026-09-04 | Bản đầu, đo trên `origin/release`. Ghi nhận bốn khác biệt hạ tầng giữa `frontend/` và `fecredit/`. Đính chính số điểm khởi tạo biểu mẫu: 3 |
