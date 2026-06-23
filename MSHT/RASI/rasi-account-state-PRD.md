# PRD: Kiểm tra trạng thái tài khoản RASI ở màn rút tiền

- **Ngày**: 2026-06-23
- **Trạng thái**: ready-for-agent
- **Service liên quan**: `user` (SSO Auth, gRPC server), `withdraw` (API mới), submodule `external` (proto gRPC)

## Problem Statement

Để rút tiền, người dùng cần có **tài khoản RASI**. Hiện tại màn rút tiền không biết người dùng đã có tài khoản RASI hay chưa, nên không thể dẫn người dùng làm đúng bước tiếp theo. Có ba tình huống khác nhau cần xử lý khác nhau:

1. Người dùng **chưa cập nhật app** lên phiên bản hỗ trợ RASI → cần đưa họ ra App Store / Google Play để update.
2. Người dùng **đã có app mới nhưng chưa đăng ký tài khoản RASI** → cần đưa họ vào màn đăng ký RASI.
3. Người dùng **đã có tài khoản RASI** → cho phép rút tiền bình thường, không làm phiền.

Nếu màn rút tiền không phân biệt được ba tình huống này, người dùng sẽ bị kẹt, không biết vì sao không rút được tiền.

## Solution

Bổ sung dữ liệu RASI vào luồng SSO Auth và cung cấp một **API kiểm tra trạng thái tài khoản** ở service `withdraw` để client gọi khi mở màn rút tiền.

Khi xác thực SSO, server MBBank trả thêm hai trường: `rasiAccountNumber` (số tài khoản RASI) và `rasiDeeplink` (deeplink mở màn đăng ký RASI trong app). Service `user` lưu hai trường này vào hồ sơ người dùng cùng với các trường đã có.

Ở màn rút tiền, client gọi `GET /api/withdraw/account-state`. Service `withdraw` lấy `userID` từ JWT (middleware sẵn có), gọi gRPC sang `user` để **đọc trạng thái mới nhất từ DB** (không đọc từ JWT vì JWT sống 6 tháng và dễ lỗi thời sau khi người dùng đăng ký RASI), rồi áp quy tắc trạng thái và trả về cho client `state` cùng toàn bộ deeplink cần thiết. Client tự switch theo `state` để điều hướng.

### Quy tắc trạng thái (state machine)

| Điều kiện | `state` | Ý nghĩa client |
|---|---|---|
| `rasiAccountNumber` khác rỗng | `OK` | Đã có tài khoản RASI, cho rút bình thường |
| `rasiAccountNumber` rỗng **và** `rasiDeeplink` khác rỗng | `NEED_REGISTER_RASI` | Mở `rasiDeeplink` để đăng ký RASI |
| `rasiAccountNumber` rỗng **và** `rasiDeeplink` rỗng | `NEED_UPDATE_APP` | Mở store để cập nhật app |

`rasiAccountNumber` được ưu tiên kiểm tra trước: chỉ cần có số tài khoản thì luôn là `OK`, bất kể `rasiDeeplink`.

### Hợp đồng API

`GET /api/withdraw/account-state` (yêu cầu đăng nhập — `RequireLogin`)

Response:

```json
{
  "data": {
    "state": "OK | NEED_REGISTER_RASI | NEED_UPDATE_APP",
    "rasiDeeplink": "",
    "appleStoreDeeplink": "",
    "googlePlayStoreDeeplink": ""
  },
  "message": "Success",
  "code": 0
}
```

- `state`: một trong ba giá trị theo bảng trên.
- `rasiDeeplink`: deeplink đăng ký RASI lấy từ SSO (qua gRPC). Rỗng nếu không có.
- `appleStoreDeeplink`, `googlePlayStoreDeeplink`: lấy từ `common.env` (mọi service đọc được).

Backend trả về **tất cả deeplink** trong mọi trường hợp; client tự switch theo `state` để chọn deeplink cần dùng. Backend không cần biết nền tảng (iOS/Android), nên không có tham số `platform`.

### Sơ đồ data flow

```
[1] SSO Auth (service user)
    MBBank /userInfo  ──►  trả thêm rasiAccountNumber, rasiDeeplink
                          map: MBBank UserInfo → MBUser → UserBSON → lưu MongoDB

[2] Màn rút tiền (client → service withdraw)
    GET /api/withdraw/account-state  (RequireLogin)
        │  lấy userID từ JWT (middleware sẵn có)
        ├─► gRPC GetUserInfo(userID) → service user đọc DB
        │       trả rasiAccountNumber, rasiDeeplink (luôn tươi)
        ├─► đọc appleStoreDeeplink, googlePlayStoreDeeplink từ common.env
        └─► AccountStateResolver → { state, deeplinks } → client
```

## User Stories

1. Là người dùng đã có tài khoản RASI, tôi muốn mở màn rút tiền và rút được ngay, để không bị làm phiền bởi bước thừa.
2. Là người dùng chưa đăng ký RASI nhưng đã có app mới, tôi muốn được dẫn tới màn đăng ký RASI, để hoàn tất điều kiện rút tiền.
3. Là người dùng dùng app cũ chưa hỗ trợ RASI, tôi muốn được dẫn ra cửa hàng ứng dụng để cập nhật, để dùng được tính năng rút tiền.
4. Là người dùng iOS, tôi muốn nhận được deeplink App Store khi cần cập nhật, để mở đúng cửa hàng của nền tảng mình.
5. Là người dùng Android, tôi muốn nhận được deeplink Google Play khi cần cập nhật, để mở đúng cửa hàng của nền tảng mình.
6. Là người dùng vừa đăng ký RASI xong, tôi muốn lần kiểm tra tiếp theo nhận đúng trạng thái `OK`, để không bị yêu cầu đăng ký lại.
7. Là người dùng, tôi muốn màn rút tiền phản hồi nhanh khi kiểm tra trạng thái, để không phải chờ lâu.
8. Là client (app), tôi muốn nhận một `state` rõ ràng kèm toàn bộ deeplink, để tự điều hướng mà không phải tự suy luận logic nghiệp vụ.
9. Là client (app), tôi muốn API trả về cấu trúc nhất quán trong cả ba trường hợp, để xử lý đồng nhất.
10. Là hệ thống `user`, tôi muốn lưu `rasiAccountNumber` và `rasiDeeplink` mỗi lần SSO Auth, để luôn có dữ liệu mới nhất phục vụ kiểm tra trạng thái.
11. Là hệ thống `withdraw`, tôi muốn đọc trạng thái RASI mới nhất từ DB qua gRPC thay vì từ JWT, để tránh dữ liệu lỗi thời do JWT sống 6 tháng.
12. Là người vận hành, tôi muốn cấu hình deeplink cửa hàng ở `common.env`, để đổi link mà không sửa code.
13. Là người dùng chưa đăng nhập, tôi muốn bị từ chối truy cập API này, để bảo đảm chỉ người dùng hợp lệ kiểm tra được trạng thái.
14. Là người dùng có tài khoản RASI nhưng `rasiDeeplink` cũng có giá trị, tôi vẫn muốn nhận `OK`, vì có số tài khoản là đủ điều kiện.

## Implementation Decisions

### Module 1 — `AccountStateResolver` (deep module, service `withdraw`)

- Hàm thuần, không I/O, không gRPC, không phụ thuộc framework HTTP.
- Interface: `Resolve(rasiAccountNumber, rasiDeeplink, appleStoreDeeplink, googlePlayStoreDeeplink) → AccountStateResult{ State, RasiDeeplink, AppleStoreDeeplink, GooglePlayStoreDeeplink }`.
- Đóng gói toàn bộ logic ba trường hợp theo bảng quy tắc trạng thái. Đây là nơi duy nhất chứa logic nghiệp vụ; các tầng khác chỉ điều phối.
- `state` là kiểu hằng chuỗi: `OK`, `NEED_REGISTER_RASI`, `NEED_UPDATE_APP`.

### Module 2 — Mở rộng gRPC user info (cross-service, submodule `external`)

- Thêm hai trường vào message `UserInfo` trong proto `user`: `rasi_account_number` và `rasi_deeplink` (đánh số tiếp theo cuối message để tương thích ngược).
- Tái sử dụng rpc method `GetUserInfo` hiện có; **không** thêm rpc method mới.
- Regenerate code gRPC bằng script biên dịch protobuf sẵn có và commit vào submodule `external`.
- Handler `getUserInfo` ở service `user` populate hai trường mới từ hồ sơ người dùng đọc từ DB.
- Client gRPC ở `withdraw` map hai trường mới vào struct user info nội bộ của `withdraw`.

### Module 3 — Lan truyền trường RASI trong SSO Auth (service `user`)

- Thêm `rasiDeeplink` chạy dọc theo đúng pattern của `rasiAccountNumber` đã có sẵn:
  - Struct response SSO từ MBBank (`UserInfo` tầng partner API): thêm `RasiDeeplink`.
  - Struct trung gian `MBUser` ở tầng service: thêm `RasiDeeplink`.
  - Model lưu trữ `UserBSON`: thêm trường `RasiDeeplink` và setter tương ứng.
  - Chuỗi map khi nhận dữ liệu từ MBBank: gán `RasiDeeplink`.
  - Nhánh cập nhật người dùng cũ: cập nhật `RasiDeeplink`.
- `rasiAccountNumber` đã tồn tại đầy đủ trong luồng này; chỉ bổ sung phần còn thiếu cho `rasiDeeplink`.

### Module 4 — HTTP endpoint (service `withdraw`)

- Route mới `GET /api/withdraw/account-state`, áp middleware `RequireLogin` sẵn có.
- Controller mỏng: lấy `userID` từ context (đã được middleware auth set), gọi client gRPC user, đọc deeplink store từ config (`common.env`), gọi `AccountStateResolver`, trả response chuẩn `Response200`.
- Response DTO riêng theo đúng convention DTO của service `withdraw`.
- Hai deeplink store được khai báo trong struct config env của `withdraw`, đọc từ `common.env`.

### Quyết định kiến trúc & làm rõ kỹ thuật

- **Không nhúng dữ liệu RASI vào JWT.** JWT do `user` phát hành sống 6 tháng; nhúng vào sẽ gây lỗi thời sau khi người dùng đăng ký RASI. Thay vào đó đọc realtime từ DB qua gRPC. `withdraw` đã có sẵn gRPC client tới `user`.
- **Logic nghiệp vụ tập trung ở backend** (trong `AccountStateResolver`), client chỉ switch theo `state`. Tránh phân tán logic ba trường hợp ra client.
- **Backend trả tất cả deeplink** ở mọi trường hợp; không cần tham số `platform`.
- **Tái sử dụng `GetUserInfo`** thay vì thêm rpc mới để giảm thay đổi proto và giữ tương thích ngược.

## Testing Decisions

- **Nguyên tắc test:** chỉ kiểm tra hành vi bên ngoài (response theo input), không kiểm tra chi tiết cài đặt nội bộ.
- **Module được test trong PRD này:** HTTP endpoint `GET /api/withdraw/account-state` (theo thống nhất với developer).
  - Kiểm tra ba trường hợp đầu ra `state`: `OK`, `NEED_REGISTER_RASI`, `NEED_UPDATE_APP`, ứng với các tổ hợp `rasiAccountNumber` / `rasiDeeplink`.
  - Kiểm tra deeplink store luôn có mặt trong response.
  - Kiểm tra yêu cầu đăng nhập: không có JWT hợp lệ → bị từ chối.
- **Prior art:** bám theo các test/handler pattern hiện có của service `withdraw` (ví dụ luồng `WithdrawGetConfig`) cho cách dựng request, set context user, và assert cấu trúc `Response200`.
- Module `AccountStateResolver` không nằm trong phạm vi viết test ở PRD này (mặc dù là hàm thuần dễ test); có thể bổ sung sau nếu cần.

## Out of Scope

- Màn đăng ký RASI trong app (do client xử lý qua `rasiDeeplink`).
- Quy trình đăng ký tài khoản RASI phía MBBank.
- Thay đổi cơ chế phát hành/verify JWT hiện có.
- Caching kết quả trạng thái ở `withdraw` (mỗi lần gọi đọc DB qua gRPC).
- Áp dụng kiểm tra trạng thái RASI ở màn hình khác ngoài màn rút tiền.
- Unit test cho `AccountStateResolver` (chỉ test HTTP endpoint trong PRD này).

## Further Notes

- `rasiAccountNumber` đã có sẵn end-to-end trong service `user` (struct partner API → `MBUser` → `UserBSON` → DB); khối lượng chính ở service `user` là bổ sung `rasiDeeplink` theo cùng pattern.
- Thay đổi proto nằm ở submodule `external` dùng chung; cần regenerate và commit vào submodule, đồng bộ cho cả `user` và `withdraw`.
- Repo working directory hiện không phải git repository (`git: no`); việc publish PRD lên issue tracker cần cấu hình tracker (chạy `/setup-matt-pocock-skills`).
