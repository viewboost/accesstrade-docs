# Tài liệu thiết kế kỹ thuật — Luồng xác thực mã nhân viên trên ứng dụng đa đối tác (`frontend/`)

| | |
|---|---|
| **Mã tài liệu** | SDD-AMB-STAFF-FE-001 |
| **Phiên bản** | 2.0 |
| **Ngày ban hành** | 2026-09-04 |
| **Người biên soạn** | Nguyễn Đăng Định |
| **Người duyệt** | _chưa phân công_ |
| **Trạng thái** | Bản thảo |
| **Tài liệu yêu cầu** | [PRD-AMB-STAFF-FE-001](./prd-staff-code-frontend-2026-09-03.md) phiên bản 2.0 |
| **Kho mã nguồn** | `AT-Core/ambassador` |
| **Nhánh tham chiếu** | `release` — mọi số hiệu dòng trong tài liệu đo trên `origin/release` ngày 2026-09-04 |

---

## Quy ước ngôn ngữ

Áp dụng quy ước động từ tình thái của tài liệu yêu cầu (PHẢI, KHÔNG ĐƯỢC, NÊN, CÓ THỂ theo RFC 2119). Mã định danh yêu cầu `FE-0xx` tham chiếu tới tài liệu yêu cầu.

---

## 1. Mục đích và phạm vi

### 1.1 Mục đích

Tài liệu mô tả phương án hiện thực hoá PRD-AMB-STAFF-FE-001 phiên bản 2.0.

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
| Hộp thoại không đủ điều kiện | `src/components/common/modal-not-employee/` | tương ứng | Tái sử dụng, điều chỉnh nội dung |
| Mục tại trang Hồ sơ | `src/pages/account/components/form-staff/` | tương ứng | Tái sử dụng, bổ sung lớp dựng danh sách |
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
 * Không suy đoán trong trường hợp không xác định: giá trị sai dẫn tới ghi
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
// Phục vụ FE-005. Không điều khiển hiển thị hộp thoại — khác bản tham chiếu.
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

`checkPartnerEmployeeStatus` chỉ được gọi từ trang Hồ sơ. Tác vụ này KHÔNG ĐƯỢC gắn vào hiệu ứng khởi tạo của thành phần đầu trang như bản tham chiếu (`fecredit/…/header/index.tsx:100-107`) — đó chính là cơ chế kích hoạt hộp thoại chủ động mà FE-006 không áp dụng.

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
  partnerName={partnerDetail?.name}
  …
/>
```

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

### 4.8 Hộp thoại không đủ điều kiện — FE-004

Tái sử dụng `fecredit/src/components/common/modal-not-employee/` (71 dòng). Hộp thoại đóng được.

Hai điều chỉnh so với bản nguồn:

| # | Điều chỉnh | Cơ sở |
|---|---|---|
| 1 | Tên đối tác lấy động từ `partnerDetail?.name` | Bản nguồn cố định chuỗi tên đối tác (`modal-staff-code.tsx:145`) do chỉ phục vụ một đối tác |
| 2 | Bổ sung lối đi tới mục "Thông tin nhân viên" | Theo FE-006, đây là điểm tiếp xúc duy nhất giữa hệ thống và nhân viên chưa khai báo |

### 4.9 Mục "Thông tin nhân viên" — FE-005

**Nguồn danh sách đối tác:** `mainState.partners`, đã nạp bởi `getListPartner` (`models/main.ts:234-247`) và đã được backend lọc theo tên miền.

Thiết kế KHÔNG ĐƯỢC sử dụng `user.partnerApproval`. Thuộc tính này thuộc thực thể `user-socials`:

| Vị trí | Tham chiếu |
|---|---|
| Định nghĩa mô hình | `backend/internal/model/mg/user_social.go:26` |
| Gán giá trị | `backend/pkg/public/service/user.go:602-603` |
| Kiểu phía giao diện | `frontend/src/interfaces/user.ts:383,403` — thuộc `IUserSocial` |

Nội dung của nó là trạng thái phê duyệt tài khoản mạng xã hội theo đối tác, khác với quan hệ người dùng × đối tác trong `user-partners` — nơi lưu `statusStaff`.

Không có API công khai trả về trực tiếp danh sách `user-partners` của người dùng: `backend/pkg/public/service/partner.go:337-341` có tính tập định danh này nhưng chỉ dùng để sắp thứ tự, không đưa vào `PartnerAppResponse`.

**Quy trình dựng danh sách:**

```
mainState.partners
  → với mỗi đối tác: GET /partners/:id/status-employee
  → giữ lại đối tác có enabled === true
  → hiển thị mỗi đối tác một dòng
```

**Ràng buộc thực thi:**

| # | Ràng buộc |
|---|---|
| 1 | Giới hạn số yêu cầu đồng thời; giá trị đề xuất: 4 |
| 2 | Hiển thị dần; KHÔNG chặn hiển thị toàn trang để chờ đủ dữ liệu |
| 3 | Một yêu cầu thất bại chỉ làm ẩn dòng tương ứng |
| 4 | Ngưỡng cần xem xét lại kiến trúc: khoảng 30 đối tác. Số liệu hiện tại: 17 |

**Nội dung mỗi dòng:**

| `statusStaff` | Hiển thị |
|---|---|
| `employee` | Mã ở chế độ chỉ đọc, kèm hướng dẫn liên hệ bộ phận hỗ trợ |
| Giá trị khác | Ô nhập mã và nút xác nhận |

Không hiển thị thao tác gỡ trạng thái nhân viên; backend đã từ chối thao tác này (`staff_code.go:105-116`).

**Vị trí trên trang.** Bổ sung một khối vào `src/pages/account/index.tsx` theo đúng cấu trúc hai khối hiện có: vùng chứa `.p-3c.p-md-6c.bg-white.rounded-2`, tiêu đề `.fw-bold.fs-10.fs-md-4`, `AppSpacer`, nội dung biểu mẫu.

Khối được đặt phía trên khối "Thông tin tài khoản" và phía dưới khối "Nhập mã giới thiệu", đáp ứng AC-005.7.

Sử dụng `FormField` (`components/common/form-field`) cho từng dòng và `toast` từ `@/components/app/toast/manager`.

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
| FE-004 | `components/common/modal-not-employee/`, `header/index.tsx` |
| FE-005 | `pages/account/index.tsx`, `pages/account/components/form-staff/`, `models/main.ts`, `services/partner.ts` |
| FE-006 | Không phát sinh thành phần |
| FE-007 | Toàn bộ; kiểm chứng theo Mục 7 |

---

## 6. Kế hoạch triển khai

| # | Hạng mục | Phụ thuộc |
|---|---|---|
| 1 | `utils/staff.ts` và kiểm thử đơn vị | — |
| 2 | Cấu hình endpoint, ba hàm dịch vụ, kiểu dữ liệu, trạng thái, hai tác vụ | — |
| 3 | `hooks/use-post-content-gate.ts` và tích hợp vào ba điểm khởi tạo | 1, 2 |
| 4 | Hộp thoại không đủ điều kiện, gắn tại thành phần đầu trang | 3 |
| 5 | Hộp thoại nhập mã tham gia và bước tải lại dữ liệu chiến dịch | 3 |
| 6 | Mục "Thông tin nhân viên" tại trang Hồ sơ | 1, 2 |
| 7 | Kiểm thử hồi quy đối tác chưa bật tính năng và kiểm tra trực quan | 1–6 |

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
| IT-08 | Người dùng không có đối tác nào bật tính năng | Trang Hồ sơ không hiển thị mục "Thông tin nhân viên" |
| IT-09 | Người dùng có hai đối tác bật tính năng | Hiển thị hai dòng; khai báo tại một đối tác không ảnh hưởng đối tác còn lại |
| IT-10 | Trạng thái `employee` | Không có thao tác gỡ trên giao diện |
| IT-11 | Một yêu cầu `status-employee` thất bại | Các dòng còn lại vẫn hiển thị |
| IT-12 | Mất kết nối mạng khi gửi biểu mẫu | Có thông báo lỗi; giao diện không treo (nhánh `app.tsx:85-91`) |

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

# Mục 4.9 — không sử dụng partnerApproval để dựng danh sách đối tác
grep -rn "partnerApproval" frontend/src/pages/account
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
| 1 | Xác nhận `options.enableStaffCode` của đối tác đang được bật | Backend / Vận hành |
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
| R5 | Nhân viên không tìm thấy đường khai báo | Trung bình | Lối đi tại FE-004 (Mục 4.8); vị trí hiển thị tại Mục 4.9 |
| R6 | Số yêu cầu mạng của FE-005 ảnh hưởng thời gian tải trang Hồ sơ | Thấp | Ràng buộc thực thi tại Mục 4.9 |

---

## 10. Vấn đề còn mở

| # | Nội dung | Bên xử lý |
|---|---|---|
| OI-01 | Xác nhận `options.enableStaffCode` của đối tác FE CREDIT trên production đang được bật. Endpoint yêu cầu xác thực nên không tự kiểm chứng được | Backend |
| OI-02 | Hộp thoại FE-003 có chấp nhận hiển thị đồng thời thông báo tại chỗ và thông báo nổi hay không (Mục 3.2). Trường hợp không chấp nhận, cần điều chỉnh trình xử lý lỗi toàn cục bằng một hạng mục riêng | Sản phẩm / Kỹ thuật |

---

## 11. Lịch sử sửa đổi

| Phiên bản | Ngày | Nội dung |
|---|---|---|
| 2.0 | 2026-09-04 | Chuẩn hoá toàn bộ văn phong theo khuôn tài liệu thiết kế kỹ thuật: bổ sung quy ước động từ tình thái, tách Nguyên tắc thiết kế và Ràng buộc bắt buộc thành mục riêng có mã định danh, chuyển kịch bản kiểm thử sang dạng bảng có mã, tách Phát hành & Vận hành khỏi Rủi ro. Nội dung kỹ thuật và các tham chiếu mã nguồn giữ nguyên |
| 1.0 | 2026-09-04 | Bản đầu, đo trên `origin/release`. Ghi nhận bốn khác biệt hạ tầng giữa `frontend/` và `fecredit/`. Đính chính số điểm khởi tạo biểu mẫu: 3 |
