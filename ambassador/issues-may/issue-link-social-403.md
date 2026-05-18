# Issue: Liên kết tài khoản TikTok → văng đăng nhập (403 / 401 dây chuyền)

**Ngày phát hiện:** 2026-05-17
**Trạng thái:** Đã fix — chờ merge
**Project:** Ambassador (accesstrade-projects/ambassabor)
**Mức độ:** Nghiêm trọng (user mất phiên đăng nhập)
**PR:** [#1 — fix/issue](https://github.com/AT-Core/ambassador/pull/1)

---

## 1. Tóm tắt

Khi user liên kết tài khoản TikTok, sau khi popup OAuth đóng lại thì `authToken` bị xóa khỏi `localStorage`. User bị văng khỏi phiên đăng nhập, kéo theo hàng loạt request trả về `401` và bị điều hướng về trang chủ.

---

## 2. Hiện tượng

- User vào trang Liên kết tài khoản, bấm liên kết TikTok.
- Popup OAuth TikTok mở, user xác thực xong, popup đóng lại.
- Ngay khi popup đóng: `authToken` biến mất khỏi `localStorage` của tab chính.
- Mọi API sau đó trả `401` → bị đẩy về `/`, phải đăng nhập lại.

---

## 3. Nguyên nhân gốc

### Chuỗi nhân quả

1. Popup OAuth TikTok redirect về `localhost:8000/lien-ket-tiktok` (hoặc domain tương ứng). Đây là **app đầy đủ**, không phải trang trắng.
2. Tab popup boot app → chạy effect `mainState/initApp`.
3. `initApp` gọi `getUserDetail`. Vì popup đang đóng / redirect, request bị **abort** → trả về `response` rỗng → `code = undefined`.
4. `initApp` có điều kiện `code !== success` → hiểu nhầm là token hỏng → gọi `storage.clearUserToken()` → **xóa `authToken`**.
5. Popup và tab chính **cùng origin** → tab chính mất token theo (qua sự kiện `storage` của trình duyệt).
6. Tab chính: mọi request → `401` → `responseInterceptors` gọi `clearUserData` → vòng lặp văng đăng nhập.

### Vì sao bản cũ không bị

Ở phiên bản cũ, `initApp` destructure thẳng `getUserDetail()`:

```js
const { data, code } = yield call(serviceUser.getUserDetail);   // không có "|| {}"
```

Khi `getUserDetail` trả `undefined` (request bị abort), việc destructure `undefined` ném `TypeError` → effect `initApp` **crash ngay**, chưa kịp chạy tới `clearUserToken`. Token sống sót — nhưng đây là **tác dụng phụ của một crash**, không phải logic đúng.

### Commit gây regression

Một commit thêm guard `const { data, code } = response || {}` vào `initApp`. Mục đích "tránh crash" là chính đáng, nhưng tác dụng phụ: `initApp` không còn crash → chạy mượt tới nhánh `clearUserToken` → **xóa token oan**. Một thay đổi phòng thủ đã biến crash-vô-hại thành bug-xóa-token.

---

## 4. Cách fix

`initApp` chỉ xóa token khi backend **xác nhận** token không hợp lệ (`code === ResponseCode.permission`). Các lỗi khác (response rỗng / lỗi mạng / 5xx / abort) → **giữ token**, chỉ coi như chưa init xong.

| Trường hợp | Trước | Sau |
|---|---|---|
| `code === permission` (token thật hỏng) | xóa token | xóa token |
| `code !== success` — rỗng / mạng / abort | **xóa token** ❌ | **giữ token** ✅ |
| `success` + có data | đăng nhập | đăng nhập |

Không revert guard `|| {}` (giữ để tránh crash); chỉ sửa đúng điều kiện xóa token → không phụ thuộc crash, không tái phát.

### File thay đổi

- `frontend/src/models/main.ts` — effect `initApp`: tách điều kiện, chỉ `clearUserToken` khi `code === permission`.

---

## 5. Kết quả

- Liên kết TikTok → popup đóng → `authToken` vẫn còn, không văng đăng nhập.
- Cắt đứt mắt xích gốc → không còn chuỗi `401` thứ cấp.
