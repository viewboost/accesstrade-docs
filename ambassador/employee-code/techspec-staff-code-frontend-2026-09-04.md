# Technical Specification: Luồng mã nhân viên trên site đa đối tác (`frontend/`)

**Date:** 2026-09-04
**Author:** Nguyễn Đăng Định
**Version:** 1.0
**Status:** Draft
**PRD:** [prd-staff-code-frontend-2026-09-03.md](./prd-staff-code-frontend-2026-09-03.md) v1.4
**Repo:** `AT-Core/ambassador`
**Nhánh nền:** `release` — mọi số hiệu dòng trong tài liệu này đo trên `origin/release` ngày 04/09/2026

---

## 1. Tổng quan

Hiện thực hoá PRD v1.4. Thuật ngữ theo mục 0 của PRD.

**Không đụng backend và admin.** API, gate chặn nộp bài, cờ theo đối tác đã đủ và đã có trên `release`. Toàn bộ công việc nằm trong `frontend/`.

### Nguyên tắc

**Nguồn để port là `fecredit/` trên `release`** — bản đã qua QA và đang chạy production.

Nhưng **`frontend/` không phải bản sao của `fecredit/`**. Bốn chỗ khác nhau về hạ tầng, mỗi chỗ port nguyên xi sẽ hỏng theo một kiểu riêng. Mục 2 liệt kê đủ bốn, kèm bằng chứng. Đọc hết mục 2 trước khi mở editor.

### 1.1 Bảng đối chiếu file nguồn ↔ file đích

| Chức năng | Nguồn (`fecredit/`) | Đích (`frontend/`) | Mức |
|---|---|---|---|
| Util phân loại + phân giải đối tác | `src/utils/staff.ts` (100 dòng) | `src/utils/staff.ts` | **Viết lại** `resolveCurrentPartner` |
| Test util | `src/utils/staff.test.ts` (21 dòng) | `src/utils/staff.test.ts` | Port + bổ sung |
| Endpoint | `src/configs/api.ts` | idem | Thêm 3 |
| Service | `src/services/user.ts`, `event.ts`, `partner.ts` | idem | Thêm 3 hàm, **đổi cách xử lý lỗi** |
| State + effect | `src/models/main.ts` | idem | Thêm 3 field, 2 effect |
| Kiểu | `src/interfaces/app.ts`, `event.ts` | idem | Thêm field |
| Modal mã tham gia | `src/pages/home/components/modal-event-code/` | idem | Port |
| Modal không đủ điều kiện | `src/components/common/modal-not-employee/` | idem | Port |
| Mục Hồ sơ | `src/pages/account/components/form-staff/` | idem | Port + **bọc lớp danh sách** |
| Chặn ở nút nộp bài | 3 điểm | **3 điểm khác** | Gom một hàm |
| Modal xác nhận nhân viên | `src/.../modal-staff-code.tsx` | — | **KHÔNG port** (FE-006) |

### 1.2 Năm ràng buộc bắt buộc

1. **Không đoán "đối tác hiện tại"** khi route không có `:partner`. Trả `undefined`, không lấy `partners[0]`, không nhớ localStorage.
2. **Không suy trạng thái gate ở FE** từ `user.statusStaff` — chỉ đọc lại `staffGateReason` backend trả.
3. **Không tự bật popup lúc tải trang** — chỉ mở khi bấm nộp bài.
4. **Không port `modal-staff-code.tsx`** cùng `visibleModalStaffCode` / `staffCodeDismissed` (FE-006).
5. **Không đụng** `backend/`, `admin/`, `parasola/`, `fecredit/` và 12 folder partner còn lại.

---

## 2. Bốn khác biệt hạ tầng phải xử lý

### 2.1 `resolveCurrentPartner` — nhánh dự phòng của `fecredit` không bao giờ đúng

**Bản nguồn** (`fecredit/src/utils/staff.ts:34-45`):

```ts
if (mainState?.partnerDetail?._id) return mainState.partnerDetail;
if (mainState?.isOwnerPartner && mainState?.partners?.length === 1) return mainState.partners[0];
return undefined;
```

**Vì sao nhánh 2 chết trên `frontend/`:**

| Bước | Bằng chứng |
|---|---|
| Handler lấy domain từ header Origin | `backend/pkg/public/handler/partner.go:203` |
| Service lọc theo `allowDomains` | `backend/pkg/public/service/partner.go:308` |
| `AllowHeaderPartner = len(Data) > 1` | `backend/pkg/public/service/partner.go:376` |
| FE đảo cờ: `isOwnerPartner = !allowHeaderPartner` | `frontend/src/models/main.ts:243` |

Site ACCESSTRADE trả **17 đối tác** (đo 03/09) ⇒ `isOwnerPartner = false` vĩnh viễn ⇒ nhánh 2 không bao giờ chạy.

**Bản đích:**

```ts
/**
 * Đối tác hiện tại của trang đang xem.
 *
 * `frontend/` là site đa đối tác: chỉ cây route dưới `/:partner/` mới có đối
 * tác (config/routes.ts:114-155). Các trang dùng chung — /tai-khoan,
 * /thong-bao, /trang-ca-nhan — không thuộc đối tác nào.
 *
 * KHÔNG đoán. Ghi trạng thái nhân viên vào nhầm đối tác là ghi vào
 * user-partners.statusStaff, thứ ảnh hưởng thẳng tới điều kiện xét thưởng.
 */
export function resolveCurrentPartner(mainState: { partnerDetail?: any }): any | undefined {
  return mainState?.partnerDetail?._id ? mainState.partnerDetail : undefined;
}
```

Bỏ hẳn nhánh `isOwnerPartner` thay vì để lại code chết.

### 2.2 ⚠️ `errorHandler` xử lý `skipErrorHandler` KHÁC NHAU — chỗ dễ hỏng nhất

Đây là bẫy nguy hiểm nhất của cả task, vì copy nguyên sẽ **chạy được lúc thành công và chỉ nổ khi có lỗi**.

**`fecredit/src/app.tsx:76-92`** — `skipErrorHandler` chỉ tắt toast, **vẫn trả body lỗi về caller**:

```ts
if (!skipErrorHandler && error?.data?.message) {
  toast.error(error.data.message);
}
return error?.data;   // ← luôn trả
```

Comment ngay trên đó đã cảnh báo: *"return rỗng sẽ làm model nhận undefined rồi nổ ở `response.code`"*.

**`frontend/src/app.tsx:75-94`** — thoát sớm, **trả `undefined`**:

```ts
if (skipErrorHandler) return;   // ← promise resolve bằng undefined
destroyLoading();
if (error?.data?.message) {
  toast.error(error.data.message);
} else if (!error?.response && isBrowser()) {
  toast.error('Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối và thử lại.');
}
return error?.data;
```

⇒ Bê nguyên service của `fecredit` (`src/services/user.ts:28-38`, có `skipErrorHandler: true`) sang `frontend/` thì mọi lỗi nghiệp vụ đều làm model nhận `undefined`, `response.code` ném `TypeError` ra `onError` toàn cục, và người dùng **không thấy thông báo nào**.

**Quy tắc cho `frontend/`: KHÔNG đặt `skipErrorHandler`.**

| | `fecredit` | `frontend` |
|---|---|---|
| Service | `skipErrorHandler: true` | **không đặt** |
| Ai hiện lỗi | callback tự gọi `toast.error` | `errorHandler` toàn cục đã toast |
| Model nhận gì khi lỗi | `error.data` (`{code, message}`) | `error.data` (`{code, message}`) |
| Callback phải làm gì | toast lỗi | **KHÔNG toast lại** — sẽ ra hai toast chồng nhau |

Kèm lợi: nhánh mất mạng đã được `frontend` xử lý sẵn (`app.tsx:85-91`), không phải tự viết cờ `isSystemError` như `fecredit/src/models/main.ts:229-244`.

**Ngoại lệ — modal nhập mã tham gia (FE-003)** cần hiện lỗi *dưới ô nhập*, không phải toast. Vẫn không dùng `skipErrorHandler`: đọc `response.message` trong callback để vẽ dòng đỏ, và chấp nhận có thêm một toast. Nếu sản phẩm thấy thừa thì sửa `errorHandler` của `frontend` về đúng khuôn `fecredit` (`return error?.data` cả hai nhánh) — **việc đó đụng toàn app, phải tách PR riêng, không nhét vào task này**.

### 2.3 Điểm mở form nộp bài — 3 điểm, và một điểm dùng lại ở hai trang

Đếm chính xác trên `release` (PRD v1.4 ghi "4+", con số đúng là **3**):

| # | Handler | Nút | Ghi chú |
|---|---|---|---|
| 1 | `src/components/layout/main/header/index.tsx:157` | `:374` | Nút trên header |
| 2 | `src/pages/home/components/not-logged-in/index.tsx:42` | `:178` | Khối CTA màn chưa đăng nhập |
| 3 | `src/pages/home/components/logged-in-view/index.tsx:31` | `:129` | Màn đã đăng nhập |

Cả ba đều là một hàm chỉ làm đúng một việc — `dispatch({type:'mainState/updateState', payload:{openPostContentModal:true}})` — nên chèn kiểm tra vào là gọn.

**KHÔNG chặn ở `src/pages/home/components/post-modal/index.tsx:72,89.** Hai dispatch đó là **mở lại** form sau khi đóng modal con Threads/Facebook (`handleCloseThreadsModal`, `handleCloseFacebookModal`), không phải điểm vào. Chặn ở đó là bắt người dùng qua gate hai lần trong một luồng.

**Điểm 3 dùng lại ở hai trang.** `PostContentModal` được mount ở `src/layouts/event-detail/index.tsx:292` **và** `src/pages/home/components/logged-in-view/index.tsx:163`; `src/pages/profile/index.tsx:118` render lại `LoggedInView` cho `/trang-ca-nhan`. Nên hàm kiểm tra phải đọc `eventHome` **từ props/state của nơi gọi**, không đọc cứng `homeState.eventHome` — ở `/trang-ca-nhan` nguồn dữ liệu khác.

`src/pages/home/components/statistic/index.tsx` chỉ nhận `{ eventHome, loading }`, **không có nút nộp bài** — khác `fecredit`. Không phải cắm gì ở đó.

### 2.4 Quy ước tầng API/service khác `fecredit`

| | `fecredit` | `frontend` |
|---|---|---|
| Namespace endpoint | `user:`, `events:`, `partners:` | `user:`, **`event:`** (số ít), `partners:` |
| Kiểu service | object literal | **named function + export default {…}** ở cuối file |
| Lấy chi tiết đối tác | theo id | `/partners/by-slug` (`configs/api.ts:381`) |

Không có `services/staff.ts` riêng: thêm `confirmIsStaff` vào `services/user.ts`, `getStatusEmployee` vào `services/partner.ts`, `inputCodeJoinEvent` vào `services/event.ts` — đúng nơi endpoint thuộc về.

---

## 3. Tầng API và service

### 3.1 `src/configs/api.ts`

```ts
// trong khối `user:` (cạnh acceptPrivacy, dòng 79-82)
confirmIsStaff: (): IApi => ({
  url: '/users/confirm-is-staff',
  method: methods.post,
}),

// trong khối `event:` (dòng 316-357)
inputCodeJoinEvent: (id): IApi => ({
  url: `/events/${id}/input-code-join-event`,
  method: methods.post,
}),

// trong khối `partners:` (dòng 373-388)
statusEmployee: (id: string): IApi => ({
  url: `/partners/${id}/status-employee`,
  method: methods.get,
}),
```

### 3.2 Service

```ts
// services/user.ts — KHÔNG skipErrorHandler, xem 2.2
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

Nhớ thêm vào `export default {...}` cuối mỗi file — `frontend` không export tự động như object literal.

### 3.3 Hình dạng response

`GET /partners/:id/status-employee` (`backend/pkg/public/model/response/partner.go:31-43`, **cần đăng nhập** — `router/partner.go:24` có `RequiredLogin`):

```ts
{
  isOpenInputStaffCode: boolean; // cờ mở modal — task này KHÔNG dùng (FE-006)
  enabled: boolean;              // đối tác có bật tính năng không — FE-005 lọc bằng cờ NÀY
  statusStaff?: string;          // 'employee' | 'not_employee' | 'not_verify' | vắng
  staffCode?: string;            // chỉ trả cho chính chủ
}
```

⚠️ **FE-005 lọc bằng `enabled`, không phải bằng sự tồn tại của object.** Backend vẫn trả object đầy đủ khi đối tác tắt tính năng (`staff_code.go:47-49`).

Event detail trả thêm (`backend/pkg/public/service/event.go:1292-1293`):

```ts
isRequireCode: boolean;
staffGateReason?: 'staff' | '';
```

---

## 4. Tầng model — `src/models/main.ts`

### 4.1 State

```ts
const initState: IMainState = {
  // …giữ nguyên
  visibleModalEventCode: false,
  visibleModalNotEmployee: false,
  staffStatus: undefined,
};
```

**Không thêm** `visibleModalStaffCode`, `staffCodeDismissed` (FE-006).

### 4.2 Hai effect

```ts
// Chỉ dùng cho FE-005. KHÔNG mở modal nào — khác fecredit.
*checkPartnerEmployeeStatus({ payload, callback }, { call, put }) {
  const response = yield call(servicePartner.getStatusEmployee, payload.partnerId);
  if (response?.code !== AppConst.ResponseCode.success) return;
  yield put({ type: 'updateState', payload: { staffStatus: response.data?.data } });
  callback?.(response.data?.data);
},

// Dùng chung cho mọi chỗ khai mã. Backend cho ghi đè nên gọi lại nhiều lần không sao.
//
// KHÔNG bọc try/catch như bản fecredit: service không đặt skipErrorHandler nên
// errorHandler toàn cục (app.tsx:75-94) đã toast và trả error.data về đây.
// Callback chỉ xử lý nhánh thành công — toast lại là hai toast chồng nhau (2.2).
*confirmIsStaff({ payload, callback }, { call }) {
  const response = yield call(serviceUser.confirmIsStaff, payload.data);
  callback?.(response);
},
```

`checkPartnerEmployeeStatus` **chỉ gọi từ trang Hồ sơ**. Không gắn vào `useEffect` của header như `fecredit` (`header/index.tsx:100-107`) — đó chính là cơ chế bật modal chủ động mà FE-006 đã chốt không làm.

---

## 5. Tầng kiểu

```ts
// interfaces/app.ts — thêm vào IMainState (hiện kết thúc ở dòng 229)
visibleModalEventCode?: boolean;
visibleModalNotEmployee?: boolean;
staffStatus?: IStatusEmployee;

// interfaces/event.ts — thêm vào IEventHome (dòng 3-26)
isRequireCode?: boolean;
staffGateReason?: 'staff' | '';
```

Kiểu `IStatusEmployee` khai ở `interfaces/app.ts` theo đúng response mục 3.3.

`Options` của `IEventHome` (dòng 11) đã có sẵn — không cần thêm `applyForStaff` vì task này không hiển thị nhãn nhóm đối tượng trên thẻ chiến dịch (ngoài phạm vi PRD).

---

## 6. FE-002 — hàm chặn dùng chung

### 6.1 Hàm

```ts
// utils/staff.ts
export type StaffGateAction = 'blocked' | 'require-code' | 'allow';

/**
 * Quyết định bấm nộp bài thì đi đâu.
 *
 * CHỈ đọc lại cờ backend trả, KHÔNG suy từ user.statusStaff: statusStaff gắn
 * theo TỪNG đối tác (UserPartnerRaw.StatusStaff) còn FE chỉ có một giá trị
 * chung, nên so bằng nó sẽ sai ở đúng app này. Backend tính staffGateReason
 * bằng chính checkStaffGate — hàm chặn thật lúc nộp bài
 * (public/service/content.go:132).
 *
 * Thứ tự: chặn nhân viên TRƯỚC hỏi mã. Không đủ điều kiện thì hỏi mã vô nghĩa,
 * và hai popup không được chồng nhau.
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

### 6.2 Hook cắm vào ba điểm

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

Ba điểm ở 2.3 thay thân hàm bằng hook này. `eventHome` truyền từ nơi gọi (2.3, đoạn cuối) — không đọc cứng `homeState`.

### 6.3 Nơi mount hai modal

Mount ở **header** (`src/components/layout/main/header/index.tsx`), không mount trong trang chi tiết. Lý do: điểm 3 được dùng lại ở `/trang-ca-nhan` qua `pages/profile/index.tsx:118`, nơi không có layout chi tiết chiến dịch — mount trong trang là bấm nộp bài ở `/trang-ca-nhan` bị chặn im lặng, không popup nào hiện. Đây đúng là bài học đã ghi trong `fecredit/.../header/index.tsx:508-512`.

Điều kiện hiện, để không chồng modal hệ thống:

```tsx
<ModalNotEmployee
  visible={
    !!visibleModalNotEmployee &&
    !!eventHome?.staffGateReason &&   // chuyển chiến dịch khác → popup tự tắt
    !visibleModalLogin &&
    !visibleModalCompleteReg
  }
  partnerName={partnerDetail?.name}
  ...
/>
```

---

## 7. FE-003 — modal nhập mã tham gia riêng

Port `fecredit/src/pages/home/components/modal-event-code/` (159 dòng + scss).

**Luồng:** nhập mã → `POST /events/:id/input-code-join-event` → **nạp lại event detail** (`homeState/getEventBySlug`, `pages/home/model.ts:80-93`) để backend tính lại `isRequireCode` → **mở tiếp form nộp bài**.

Không tự đoán ở FE là đã đủ điều kiện: `isRequireCodeForUser` đọc `user-events.options.codeInput` (`backend/pkg/public/service/event.go:1190-1206`).

Tham số `getEventBySlug` cần `{ slug, partner }` với `partner` là **`_id`**, không phải slug.

Chuẩn hoá mã lúc gõ bằng `normalizeStaffCode` (uppercase + trim). Backend chuẩn hoá lại, không tin FE.

Chữ trong modal **không được gọi đây là "mã nhân viên"** — nó đối chiếu thẳng `event.Options.StaffCodes`, không tra bảng `manage-codes` (`event.go:1218-1245`).

---

## 8. FE-004 — modal "chỉ dành cho nhân viên"

Port `fecredit/src/components/common/modal-not-employee/` (71 dòng). Modal **đóng được**.

Hai thay đổi bắt buộc so với nguồn:

1. **Tên đối tác lấy động** từ `partnerDetail?.name`. Bản nguồn hard-code "FE CREDIT" (`modal-staff-code.tsx:145`) vì chỉ phục vụ một đối tác.
2. **Phải chỉ đường tới FE-005.** Vì `frontend/` không có modal xác nhận chủ động (FE-006), đây là chỗ duy nhất một nhân viên chưa khai mã gặp hệ thống. Thêm lối đi tới `/tai-khoan` mục "Thông tin nhân viên", không chỉ báo "bạn không đủ điều kiện" rồi đóng.

---

## 9. FE-005 — mục "Thông tin nhân viên" ở `/tai-khoan`

### 9.1 Nguồn danh sách đối tác

**Dùng `mainState.partners`** — đã nạp sẵn bởi `getListPartner` (`models/main.ts:234-247`) và đã được backend lọc theo domain.

⚠️ **KHÔNG dùng `user.partnerApproval`.** Trường đó nằm trên `user-socials`, không trên user: `backend/internal/model/mg/user_social.go:26`, gán ở `pkg/public/service/user.go:602-603`; phía FE cũng thuộc `IUserSocial` chứ không phải `IUser` (`interfaces/user.ts:383,403`). Nó là trạng thái duyệt **tài khoản social** theo đối tác — khác hẳn quan hệ user × đối tác trong `user-partners`, nơi `statusStaff` thực sự sống.

Không có API công khai nào trả thẳng danh sách `user-partners` của user: `service/partner.go:337-341` có tính `userPartnerIds` nhưng chỉ dùng để xếp thứ tự, không đưa ra `PartnerAppResponse`.

### 9.2 Cách dựng

```
mainState.partners (17 đối tác)
  → với mỗi đối tác: GET /partners/:id/status-employee
  → giữ lại đối tác có enabled === true
  → render mỗi đối tác một dòng
```

**Ràng buộc:**
- Giới hạn số request song song (đề xuất 4), render dần, **không** chặn cả trang chờ đủ
- Một request lỗi → chỉ dòng đó không hiện; không làm hỏng dòng khác và không hỏng phần còn lại của trang Hồ sơ
- Ngưỡng cần xem lại kiến trúc: ~30 đối tác. Hiện 17

### 9.3 Mỗi dòng

| `statusStaff` | Hiển thị |
|---|---|
| `employee` | Hiện mã, ô khoá, chú thích liên hệ hỗ trợ |
| còn lại | Ô nhập mã + nút Lưu |

Một chiều `not_employee → employee`. **Không vẽ nút gỡ** — backend đã chặn (`staff_code.go:105-116`, lỗi `CannotSelfRevoke`).

### 9.4 Vị trí trên trang

Chèn khối mới vào `src/pages/account/index.tsx` theo đúng khuôn hai khối đang có (`.p-3c.p-md-6c.bg-white.rounded-2` + tiêu đề `.fw-bold.fs-10.fs-md-4` + `AppSpacer` + form).

Đặt **trên** khối "Thông tin tài khoản", dưới "Nhập mã giới thiệu". PRD yêu cầu mục này dễ tìm — đây là đường khai duy nhất trên `frontend/`.

Dùng `FormField` (`components/common/form-field`) cho từng dòng, `toast` từ `@/components/app/toast/manager`.

---

## 10. FE-006 — không làm, và cách chứng minh là không làm

Không tạo `modal-staff-code.tsx`; không thêm `visibleModalStaffCode`, `staffCodeDismissed`; không thêm icon `StaffBuildingIcon` / `StaffHouseIcon`; không gắn `checkPartnerEmployeeStatus` vào `useEffect` của header.

Lệnh gác trước khi merge ở mục 13.

---

## 11. Ánh xạ FR → file

| FR | File |
|---|---|
| FE-001 | `utils/staff.ts`, `utils/staff.test.ts` |
| FE-002 | `utils/staff.ts`, `hooks/use-post-content-gate.ts`, `header/index.tsx:157`, `not-logged-in/index.tsx:42`, `logged-in-view/index.tsx:31` |
| FE-003 | `pages/home/components/modal-event-code/`, `configs/api.ts`, `services/event.ts` |
| FE-004 | `components/common/modal-not-employee/`, `header/index.tsx` (mount) |
| FE-005 | `pages/account/index.tsx`, `pages/account/components/form-staff/`, `models/main.ts`, `services/partner.ts` |
| FE-006 | — (không file nào) |
| FE-007 | Toàn bộ, kiểm bằng mục 13 |

---

## 12. Thứ tự triển khai

| # | Việc | Phụ thuộc |
|---|---|---|
| 1 | `utils/staff.ts` + test | — |
| 2 | `configs/api.ts`, 3 service, interface, state, 2 effect | — |
| 3 | `hooks/use-post-content-gate.ts` + cắm 3 điểm | 1, 2 |
| 4 | `modal-not-employee` + mount ở header | 3 |
| 5 | `modal-event-code` + nạp lại event detail | 3 |
| 6 | Mục "Thông tin nhân viên" ở `/tai-khoan` | 1, 2 |
| 7 | Hồi quy đối tác chưa bật cờ + kiểm UI | tất cả |

---

## 13. Test plan

### 13.1 Unit test bắt buộc — `src/utils/staff.test.ts`

`frontend/` đã có `jest.config.js` (alias `@/`) và 9 file `*.test.ts` đang chạy bằng `umi-test`.

| Hàm | Case |
|---|---|
| `resolveCurrentPartner` | có `partnerDetail._id` → trả đúng; không có → `undefined`; **có `isOwnerPartner=true` + 1 partner vẫn phải trả `undefined`** (chốt chặn hồi quy nhánh của `fecredit`) |
| `resolveStaffGateAction` | `staffGateReason` có → `blocked`; chỉ `isRequireCode` → `require-code`; cả hai → `blocked` (thứ tự ưu tiên); rỗng → `allow` |
| `isStaff` | `employee` → true; `not_employee` / `not_verify` / rỗng / `undefined` → false |
| `normalizeStaffCode` | thường → hoa; có khoảng trắng hai đầu → trim; `undefined` → `''` |

### 13.2 Kịch bản tích hợp

1. Chiến dịch không bật điều kiện nào → bấm nộp bài ở **cả 3 điểm** đều mở form, không thêm request nào
2. Chiến dịch `applyForStaff`, user không phải nhân viên → cả 3 điểm đều hiện modal FE-004, form **không** mở
3. Từ modal FE-004 đi tới `/tai-khoan`, nhập mã đúng → quay lại nộp bài được
4. Chiến dịch có `staffCodes`, user chưa nhập → modal FE-003; nhập đúng → tự mở form
5. Nhập sai mã → lỗi hiện, modal không đóng
6. `/trang-ca-nhan` → bấm nộp bài → vẫn bị chặn đúng (điểm 3 dùng lại, mục 2.3)
7. Đang mở modal con Threads/Facebook rồi đóng → form mở lại, **không** bị hỏi gate lần hai
8. User không có đối tác nào bật cờ → `/tai-khoan` không có mục "Thông tin nhân viên"
9. User có 2 đối tác bật cờ → 2 dòng, khai ở A không đổi trạng thái B
10. Đang là nhân viên → không có đường tự gỡ
11. Một request `status-employee` lỗi → các dòng khác vẫn render
12. **Mất mạng lúc bấm Lưu** → có toast báo, không treo, không im lặng (kiểm nhánh `app.tsx:85-91`)

### 13.3 Kiểm tra trước khi merge

```bash
# FE-006: không được có modal xác nhận chủ động
git diff origin/release --  frontend/ | grep -iE "modal-staff-code|visibleModalStaffCode|staffCodeDismissed"
# → phải rỗng

# 12 folder partner + parasola + fecredit + backend + admin KHÔNG được đổi
git diff --stat origin/release -- backend admin parasola fecredit anker flamingo hdbank \
  lusso mbbank tpbank turborg vng vnpay vpbank wildrift yody
# → phải rỗng

# Không suy trạng thái gate từ user.statusStaff
grep -rn "user\.statusStaff\|user?.statusStaff" frontend/src
# → phải rỗng

# Không dùng skipErrorHandler ở luồng mới (xem 2.2)
git diff origin/release -- frontend/src/services | grep -n "skipErrorHandler"
# → phải rỗng

# Không dùng partnerApproval để dựng danh sách đối tác (xem 9.1)
grep -rn "partnerApproval" frontend/src/pages/account
# → phải rỗng

# Không có segment (đã gỡ ở PRD v5.0)
grep -rniE "conditionForAutomatic|resync|SEGMENT_TYPE_|applyForSegment" frontend/src
# → phải rỗng

npx umi-test src/utils/staff.test.ts
```

### 13.4 Kiểm UI (NFR-006)

Xem tận mắt trên desktop và mobile: modal không vỡ layout ở màn hẹp; tên đối tác dài không tràn; không hai modal chồng nhau; nút không bị `AppButton` chèn `rounded-2` bóp `border-radius` (bẫy đã gặp ở `fecredit`).

---

## 14. Rollout

Không có thay đổi backend/admin ⇒ không cần đồng bộ deploy, không cần migration.

`frontend/` có trên **cả** `release` lẫn `develop` ⇒ **một nhánh cắt từ `release`**, hai PR: `→ release` và `→ develop`. Không kéo `develop` ngược vào nhánh nguồn.

CI: `build-frontend` chỉ chạy khi `frontend/**` đổi (`.github/workflows/build-and-deploy.yml:111-112`) — đúng phạm vi task, không kéo theo app nào khác.

**Trước khi lên production:** nhờ BE xác nhận `options.enableStaffCode` của FE CREDIT đang bật, và đã chạy backfill `statusStaff` cho đối tác đó (`admin/service/migration_backfill_staff_status.go`).

---

## 15. Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Copy service kèm `skipErrorHandler` → lỗi im lặng | **Cao** | Mục 2.2 + lệnh grep 13.3 |
| Copy `resolveCurrentPartner` → tính năng chết lặng | **Cao** | Mục 2.1 + unit test 13.1 |
| Sót một điểm mở form | Trung bình | Gom một hook, kịch bản 1–2 kiểm cả 3 điểm |
| Mount modal trong trang thay vì header → `/trang-ca-nhan` chặn im lặng | Trung bình | Mục 6.3 + kịch bản 6 |
| 17 request `status-employee` làm chậm trang Hồ sơ | Thấp | Giới hạn song song, render dần (9.2) |
| Nhân viên không tự tìm được mục khai mã | Trung bình | FE-004 chỉ đường (mục 8.2); đặt mục lên cao (9.4) |

---

## 16. Câu hỏi cần chốt trước khi code

1. Nhờ BE xác nhận `options.enableStaffCode` của FE CREDIT trên prod đang bật (endpoint yêu cầu đăng nhập nên không tự tra được).
2. Modal FE-003 có chấp nhận vừa hiện lỗi dưới ô nhập vừa có toast không (mục 2.2)? Nếu không thì phải sửa `errorHandler` toàn cục — **PR riêng**.

---

## 17. Revision History

| Version | Date | Thay đổi |
|---|---|---|
| 1.0 | 2026-09-04 | Bản đầu, đo trên `origin/release`. Ghi nhận 4 khác biệt hạ tầng giữa `frontend/` và `fecredit/`, trong đó `errorHandler` xử lý `skipErrorHandler` ngược nhau là bẫy nặng nhất. Đính chính số điểm mở form: **3**, không phải "4+" như PRD v1.4 |
