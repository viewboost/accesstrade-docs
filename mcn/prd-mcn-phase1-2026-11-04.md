# Product Requirements Document: MCN trên KOC Ambassador — Phase 1

**Date:** 2026-11-04
**Author:** Vinh Nguyễn
**Version:** 1.1
**Status:** Draft — cập nhật quyết định 05–09/11/2026
**Phạm vi:** App Ambassador (`frontend/`) và Admin (`admin/`). Các app partner (parasola, vpbank, …) là bản copy riêng, **không** nằm trong phase 1.

---

## Document Overview

PRD cho phase 1 của MCN (công ty quản lý KOL/KOC) trên KOC Ambassador, theo scope chốt ở buổi họp 03/11/2026 và các quyết định bổ sung sau buổi họp.

### Nguyên tắc

1. **Đối soát và chi trả chạy như hiện nay.** Phase 1 chỉ thêm một việc vào đối soát: lúc duyệt, tách phí quản lý của thành viên có MCN. Chi trả vẫn là đợt chi ở Xử lý rút tiền, có thêm MCN là người nhận.
2. **Vai MCN đến từ bảng quan hệ, không phải loại tài khoản.** Tài khoản đăng nhập của MCN là một user bình thường. Hệ thống biết user đó là MCN vì có dòng gắn user với hồ sơ MCN. Không thêm trường `type`/`role` lên user. Tương tự, KOL/KOC thuộc MCN nào là một dòng quan hệ thành viên, không phải thuộc tính trên user.
3. **Chỉ làm phần đã chốt.** Những gì có trong tài liệu luồng (08) nhưng để sau được liệt kê ở mục 9, kèm cách phase 1 xử lý thay.

**Related Documents:**
- Bản mẫu giao diện và tài liệu nghiệp vụ (có sơ đồ): https://claude.ai/artifact/BVwnmqnqNZhjnX6pbXDikV
- Biên bản họp 03/11/2026: [meeting-261103.md](./meeting-261103.md)
- Sơ đồ tuần tự (bản đầy đủ, nhiều phần để sau): [08-Sequence.md](./08-Sequence.md)
- Tech spec: [techspec-mcn-phase1-2026-11-04.md](./techspec-mcn-phase1-2026-11-04.md)
- Plan code và tiến độ (55 đầu việc, mức sẵn sàng để code): https://claude.ai/artifact/AZHpoHEVTr3GiWy3YAWXh8

> **Khác với 08-Sequence:** 08 tạo tài khoản MCN bằng `account_type=MCN` (SD-01). Phase 1 **không** làm vậy, xem nguyên tắc 2. 08 cũng có bảng kê tháng, hóa đơn, đợt chi riêng cho MCN, xác nhận/báo sai đối soát, công bố Quy chế phiên bản mới — đều để sau (mục 9).

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **MCN** | Công ty hoặc cá nhân quản lý một nhóm KOL/KOC. Trên hệ thống là một **hồ sơ MCN** do AccessTrade tạo, loại Công ty hoặc Cá nhân |
| **Tài khoản MCN** | User đăng nhập web Ambassador, được gắn với hồ sơ MCN qua bảng quan hệ. Phase 1: mỗi MCN một tài khoản |
| **Thành viên** | KOL/KOC đã ký phụ lục và đang thuộc một MCN. Lưu ở bảng quan hệ thành viên |
| **Chờ ký** | KOL/KOC đã bấm Đồng ý lời mời nhưng chưa ký phụ lục. **Chưa phải thành viên** |
| **Link mời** | Link do MCN tạo, gắn một tỷ lệ phí 0–100%. Dùng được cho nhiều người |
| **Phí quản lý** | Phần hoa hồng của thành viên dành cho MCN = tổng hoa hồng × tỷ lệ |
| **Phụ lục** | Phụ lục chỉ định thanh toán, KOL/KOC ký trên hợp đồng điện tử, thời hạn 12 tháng |
| **Kỳ đối soát** | Kỳ ở Admin › Đối soát đang có. Trạng thái: Chờ duyệt → Đã xử lý → Đã hoàn thành, hoặc Đã từ chối |
| **Đợt chi** | Đợt ở Admin › Xử lý rút tiền đang có. Hệ thống tạo lệnh chi toàn bộ số dư cho người đủ điều kiện |
| **G** | Tổng hoa hồng của một người trong kỳ (chiến dịch, nhiệm vụ, thưởng thêm) |
| **Ngày phát sinh** | Ngày của từng khoản thưởng: thưởng view là ngày có view, thưởng mốc là ngày đạt mốc, thưởng thêm là ngày Admin tạo |

---

## 1. Executive Summary

AccessTrade muốn cho các MCN (công ty hoặc cá nhân) đưa KOL/KOC của họ lên KOC Ambassador và nhận phí quản lý trực tiếp từ hoa hồng của thành viên, thay vì tự thu ngoài hệ thống.

```
AccessTrade tạo hồ sơ MCN, tải lên 5 hồ sơ pháp lý, kích hoạt
  → MCN đăng nhập, tạo link mời kèm tỷ lệ phí, gửi cho KOL/KOC
  → KOL/KOC mở link, đồng ý, ký phụ lục → thành viên
  → Kỳ đối soát được duyệt: KOL/KOC nhận G − phí, MCN nhận phí, vào số dư
  → AccessTrade lập đợt chi như hiện nay: KOL/KOC trừ thuế TNCN theo ngưỡng, MCN công ty không trừ thuế
```

Ví dụ: thành viên vào qua link 15%, G = 3.000.000đ → phí 450.000đ vào số dư MCN, 2.550.000đ vào số dư KOL/KOC.

---

## 2. Bối cảnh

### 2.1 Hiện trạng

| Phần | Hiện nay |
|---|---|
| MCN | Chưa có gì: không model, không màn hình, không có chữ MCN trong code |
| Vai trò trên user | User không có trường loại/vai trò. Chỉ tài khoản nhân viên Admin (staff) có vai trò |
| Đối soát | Admin tạo kỳ, Lấy danh sách, Duyệt. Duyệt xong hệ thống cộng tiền vào số dư từng người. Chưa có tab Người nhận |
| Số dư | Tính từ sổ dòng tiền (`cash-flows`), theo từng partner |
| Chi trả | Admin tạo đợt chi ở Xử lý rút tiền. Hệ thống chọn user đã ký hợp đồng điện tử và có số dư từ mức tối thiểu, tạo lệnh chi toàn bộ số dư. User không thao tác rút |
| Thuế TNCN | Tính lúc chi, 10% trên số chi khi số chi **từ 5.000.000đ**. Giữ nguyên (D21) |
| Hợp đồng điện tử, eKYC | Qua dịch vụ econtract của AccessTrade core, một loại hợp đồng `B2C_AMBASSADOR`. Chưa có loại phụ lục |
| Đăng nhập | Google, TikTok, Facebook, mật khẩu. Không có trang đăng ký riêng: đăng nhập lần đầu rồi chấp nhận điều khoản là thành tài khoản |

### 2.2 Quyết định phase 1

| # | Quyết định |
|---|---|
| D1 | Chỉ mời bằng link. Không tra cứu, không mời theo mã/số điện thoại |
| D2 | Mỗi link một tỷ lệ là số nguyên 0–100%. Thành viên giữ tỷ lệ của link đã dùng suốt thời gian hợp tác. Không đổi tỷ lệ giữa chừng |
| D3 | Link không tự hết hạn. MCN tự tắt. Tắt link không ảnh hưởng thành viên đã vào |
| D4 | Không có Đề xuất (đổi tỷ lệ, gia hạn) |
| D5 | Không công bố Quy chế phiên bản mới. Quy chế, Quy tắc ứng xử ký ngoài hệ thống, tải lên theo từng MCN, là 1 trong 5 điều kiện kích hoạt |
| D6 | Admin chỉ xem thành viên, không thêm/mời/chấm dứt thay MCN |
| D7 | Không có KOL/KOC xác nhận hay báo sai đối soát, không dời khoản sang kỳ sau. Thấy thiếu thì liên hệ hỗ trợ, bổ sung bằng Thưởng thêm kỳ sau |
| D8 | Đối soát giữ trạng thái hiện có. Duyệt xong: KOL/KOC nhận G − phí, MCN nhận phí, vào số dư |
| D9 | Chi trả độc lập với đối soát, qua đợt chi ở Xử lý rút tiền. MCN được chi chung đợt, không khấu trừ thuế TNCN |
| D10 | Thuế TNCN không tính ở đối soát, chỉ tính lúc chi |
| D11 | KOL/KOC đang thuộc MCN khác không nhận được lời mời, phải rời MCN cũ trước |
| D12 | Không có Tạm dừng, Chấm dứt MCN |
| D13 | Hóa đơn GTGT cho phí quản lý xử lý ngoài hệ thống |
| D14 | Thu nhập từ nội dung do chính tài khoản MCN làm tính như creator bình thường |
| D15 | Báo trước khi rời: 15 ngày |
| D16 | Vai MCN và tư cách thành viên lưu bằng bảng quan hệ, không đặt loại tài khoản trên user |
| D17 | MCN có hai loại: Công ty và Cá nhân, cùng một luồng. Loại không đổi sau khi tạo |
| D18 | Ký xong phụ lục mới là thành viên. Chờ ký chưa phải thành viên: KOL/KOC được Chờ ký nhiều MCN cùng lúc, không có thao tác hủy. Ký xong một MCN thì các lời mời Chờ ký khác chuyển **Hết hiệu lực** |
| D19 | Hết 12 tháng phụ lục: quan hệ tự kết thúc, ngừng trích phí. Muốn tiếp tục thì ký lại qua link mời mới |
| D20 | Không trích phí trên khoản phát sinh trước ngày ký phụ lục hoặc từ ngày kết thúc. Xét theo ngày phát sinh của từng khoản, không theo ngày Lấy danh sách (thay đề xuất Q5) |
| D21 | Thuế TNCN của KOL/KOC: 10% trên số chi (đã trừ phí MCN) khi số chi trong đợt từ 5.000.000đ. MCN công ty không khấu trừ |
| D22 | MCN vẫn xem được chi tiết đối soát các kỳ đã hợp tác sau khi thành viên rời; không thấy thu nhập sau khi rời |
| D23 | KOL/KOC chưa eKYC hoặc chưa ký hợp đồng gốc `B2C_AMBASSADOR` thì làm ở trang Hợp đồng điện tử có sẵn, xong quay lại ký phụ lục |
| D24 | Một KOL/KOC đổi MCN trong cùng kỳ đối soát: mỗi MCN được trích phí trên phần khoản phát sinh trong thời gian KOL/KOC thuộc MCN đó |

---

## 3. User Personas

| Persona | Ở đâu | Làm gì |
|---|---|---|
| **Admin AccessTrade** (vai `admin`) | Admin › Danh sách MCN, Đối soát, Xử lý rút tiền | Tạo, kích hoạt MCN; quản lý hồ sơ pháp lý; duyệt đối soát; lập đợt chi |
| **MCN (công ty hoặc cá nhân)** | Web › avatar › Quản lý MCN | Tạo/tắt link mời, theo dõi lời mời và thành viên, chấm dứt thành viên, xem phí theo kỳ |
| **KOL/KOC** | Web › link mời; avatar › MCN của tôi, Đối soát | Đồng ý lời mời, ký phụ lục, báo rời/rút lại, xem số đối soát |

---

## 4. Functional Requirements

### Nhóm A — Admin: hồ sơ MCN

#### FR-001: Danh sách MCN

Menu trái Admin có mục **Danh sách MCN** (vai `admin`).

- Cột: Tên MCN, Loại, Email đăng nhập, Số thành viên, Trạng thái, Ngày tạo.
- Lọc loại: Công ty, Cá nhân. Lọc trạng thái: Chờ kích hoạt, Hoạt động. Tìm theo tên, MST/CCCD, email.
- Nút **Tạo MCN**.

#### FR-002: Tạo hồ sơ MCN

Bước đầu chọn **Loại MCN**: Công ty hoặc Cá nhân. Không đổi được sau khi tạo.

| Trường | Công ty | Cá nhân | Kiểm tra |
|---|---|---|---|
| Tên (bắt buộc) | Tên pháp nhân | Họ và tên theo CCCD | Dùng để đối chiếu tên chủ tài khoản ngân hàng |
| Mã định danh (bắt buộc) | Mã số thuế | Số CCCD (cũng là MST cá nhân) | Công ty 10 hoặc 13 số; cá nhân 12 số; không trùng MCN khác |
| Email đăng nhập (bắt buộc) | | | Đúng định dạng; không trùng email của user đã có (đang xem lại, Q12); không trùng MCN khác |
| Không bắt buộc | Địa chỉ trụ sở, Người đại diện theo pháp luật, Số điện thoại | Địa chỉ liên hệ, Số điện thoại | |

- Tạo xong: trạng thái **Chờ kích hoạt**, mở trang chi tiết ở tab Điều kiện kích hoạt.
- Email trùng: báo "Email đã được dùng cho một tài khoản khác".
- Danh sách trường đang chờ chốt (Q2).

#### FR-003: Hồ sơ pháp lý (5 điều kiện kích hoạt)

| Điều kiện | Cách nhập |
|---|---|
| Hồ sơ định danh | Tải lên file. Công ty: hồ sơ KYB. Cá nhân: CCCD hai mặt |
| Hợp đồng khung | Tải lên file đã ký số + ngày ký |
| Thỏa thuận xử lý dữ liệu cá nhân | Tải lên file đã ký số + ngày ký |
| Tài khoản ngân hàng | FR-004 |
| Quy chế chương trình, Quy tắc ứng xử đã ký | Tải lên file đã ký số + ngày ký |

- File: PDF, JPG hoặc PNG, tối đa 20MB (Q3). Ảnh dùng cho CCCD hai mặt của MCN cá nhân.
- Mỗi điều kiện đã đạt có nút **Xem**: thông tin đã nhập, file, ngày giờ và người cập nhật, lịch sử thay đổi.
- Cập nhật lần sau tạo bản mới; bản cũ vẫn trong lịch sử, không xóa.
- Sau khi kích hoạt, tab đổi tên thành **Hồ sơ pháp lý**, vẫn cập nhật được như trên.

#### FR-004: Tài khoản ngân hàng của MCN

- Admin chọn ngân hàng, nhập số tài khoản, bấm **Kiểm tra**. Hệ thống tra tên chủ tài khoản.
- Tài khoản đứng tên chính MCN. Tên khớp tên trên hồ sơ (tên pháp nhân hoặc họ tên theo CCCD; so không dấu, không phân biệt hoa thường, bỏ khoảng trắng thừa): lưu được ngay.
- Không khớp hoặc không tra được: hiện tên tra được (nếu có), Admin **phải nhập lý do** mới lưu được. Lý do lưu trong lịch sử.
- Đây là tài khoản AccessTrade chuyển tiền cho MCN ở đợt chi (FR-019).

#### FR-005: Kích hoạt MCN

- Nút **Kích hoạt** chỉ chạy khi đủ 5 điều kiện. Bấm khi còn thiếu: hiện danh sách điều kiện còn thiếu.
- Kích hoạt xong:
  - Trạng thái **Hoạt động**, ghi người và giờ kích hoạt.
  - Hệ thống tạo **dòng tài khoản MCN** gắn email đăng nhập với hồ sơ MCN (bảng quan hệ), chưa gắn user.
  - Gửi email tới email đăng nhập: MCN đã được kích hoạt, hướng dẫn đăng nhập web Ambassador bằng Google với đúng email này.
- Lần đầu user đăng nhập bằng email đó (email đã xác thực), hệ thống gắn user vào dòng tài khoản MCN. Từ đó user thấy mục **Quản lý MCN**.
- Không có thao tác Tạm dừng, Chấm dứt MCN (D12).

#### FR-006: Admin xem thành viên

- Trang chi tiết MCN đang hoạt động có tab **Thành viên**: Tên, Tỷ lệ, Ngày tham gia, Trạng thái (Đang hợp tác, Đang báo rời kèm ngày rời có hiệu lực, Đã kết thúc kèm lý do).
- Chỉ xem (D6).

### Nhóm B — MCN: mời và quản lý thành viên

#### FR-007: Menu MCN trên web

- Tài khoản MCN (FR-005) thấy **Quản lý MCN** trong menu avatar. User khác không thấy.
- Trang Quản lý MCN có menu trái: **Thành viên**, **Lời mời**, **Đối soát**, và nút **Mời KOL/KOC**.

#### FR-008: Tạo link mời

- Bấm **Mời KOL/KOC** → nhập tỷ lệ phí (số nguyên 0–100) → **Tạo link**.
- Hiện link `…/mcn/moi/<mã>` và nút **Sao chép**. MCN tự gửi qua kênh của mình.
- Tỷ lệ không phải số nguyên hoặc ngoài 0–100: báo lỗi, không tạo. Không tự làm tròn.
- Mỗi link một mã ngẫu nhiên, không đoán được, không lộ thông tin user.

#### FR-009: Mục Lời mời

- Bảng **Link mời**: Link, Tỷ lệ, Ngày tạo, Số người đã tham gia, Trạng thái (Đang dùng/Đã tắt), Sao chép, **Tắt link**.
- Tắt link: không ai mở link đó được nữa (hiện "Link mời đã ngừng"). Người đã đồng ý nhưng chưa ký vẫn ký tiếp được trong hạn. Thành viên đã vào không ảnh hưởng. Không bật lại (tạo link mới).
- Bảng **Người đã đồng ý**: người đã đồng ý nhưng chưa thành viên. Tên, Tỷ lệ, Ngày đồng ý, Trạng thái (Chờ ký phụ lục kèm hạn ký, Đã từ chối, Quá hạn ký, Hết hiệu lực — đã ký với MCN khác). MCN thấy tên người Chờ ký (MCN gửi link cho người mình đã biết); thông tin khác chỉ hiện sau khi ký phụ lục và đồng ý chia sẻ dữ liệu.

#### FR-010: Mục Thành viên (MCN)

- Bảng: Tên, Tỷ lệ, Ngày tham gia, Trạng thái, Ghi chú (ngày rời có hiệu lực / lý do kết thúc), nút **Chấm dứt**.
- MCN chỉ thấy thông tin thành viên trong thời gian hợp tác. Đã kết thúc: chỉ còn tên, ngày, trạng thái và lý do (KOL/KOC rời, MCN chấm dứt, hết hạn phụ lục). Ngoại lệ: số liệu đối soát các kỳ đã hợp tác vẫn xem được ở mục Đối soát (D22).

#### FR-011: MCN chấm dứt thành viên

- Xác nhận bằng modal, có ô **Lý do** (không bắt buộc). Hiệu lực ngay, kể cả khi thành viên đang báo rời.
- Thành viên nhận thông báo. Phí quản lý không trích từ kỳ đối soát lấy danh sách sau thời điểm đó (FR-016).

### Nhóm C — KOL/KOC: tham gia và rời MCN

#### FR-012: Mở link mời

| Tình huống | Hệ thống |
|---|---|
| Chưa đăng nhập | Hiện trang lời mời rút gọn (tên MCN, tỷ lệ) và nút Đăng nhập. Giữ mã mời qua bước đăng nhập/đăng ký; xong quay lại đúng trang lời mời |
| Đã đăng nhập, không thuộc MCN nào | Hiện lời mời đầy đủ |
| Đang thuộc MCN khác (kể cả đang báo rời) | Báo "Bạn đang thuộc MCN khác. Rời MCN hiện tại trước khi nhận lời mời mới" (D11) |
| Đã là thành viên của chính MCN này | Chuyển sang MCN của tôi |
| Tài khoản đang là tài khoản MCN | Báo không áp dụng |
| Link đã tắt hoặc MCN không hoạt động | "Link mời đã ngừng" |
| Đã đồng ý lời mời của MCN khác, chưa ký | Vẫn hiện lời mời đầy đủ, được đồng ý (D18) |
| Đã đồng ý chính lời mời này, chưa ký | Chuyển sang bước ký phụ lục |

#### FR-013: Đồng ý lời mời

- Lời mời ghi: tên MCN, tỷ lệ phí, thời hạn phụ lục 12 tháng, báo trước khi rời 15 ngày, ví dụ với thu nhập 3.000.000đ (phí, phần còn lại), câu "Thuế TNCN tính khi AccessTrade chi tiền, như hiện nay".
- Phải tick **Tôi đã hiểu** mới bấm **Đồng ý** được. Có nút **Từ chối**, kèm ô **Lý do** (không bắt buộc); MCN nhận thông báo.
- Ví dụ ghi rõ số KOL/KOC còn nhận, kể cả tỷ lệ 0% và 100%.
- Đồng ý: tạo dòng quan hệ trạng thái **Chờ ký phụ lục**, hạn ký 7 ngày; ghi tỷ lệ của link vào dòng này (tắt link sau đó không đổi tỷ lệ). Chờ ký **chưa phải thành viên** (D18).

#### FR-014: Ký phụ lục

- Chưa eKYC hoặc chưa ký hợp đồng gốc `B2C_AMBASSADOR`: chặn, dẫn sang trang **Hợp đồng điện tử** có sẵn. Làm xong quay lại ký tiếp (D23).
- Màn ký hiện **Thông báo xử lý dữ liệu cá nhân** (tải về được, A5). Tick riêng **Đồng ý chia sẻ dữ liệu cho MCN** (bắt buộc, lưu thời điểm).
- Ký trên hợp đồng điện tử (loại phụ lục mới, Q4). Ký xong: thành viên **Đang hợp tác**, ngày bắt đầu = ngày ký, ngày kết thúc phụ lục = +12 tháng.
- Ký xong một MCN: các lời mời Chờ ký của MCN khác chuyển **Hết hiệu lực**, không ký được nữa, kể cả khi kết quả ký về muộn (D18).
- Quá 7 ngày chưa ký: **Quá hạn ký**, phải mở lại link để đồng ý lại.

#### FR-015: MCN của tôi, báo rời

- Avatar › **MCN của tôi**: hiện cho người có lời mời đang Chờ ký (một hoặc nhiều MCN) hoặc đang là thành viên. Người không có quan hệ nào không thấy mục này.
- Nội dung: tên MCN, tỷ lệ, ngày tham gia, ngày kết thúc phụ lục, trạng thái.
- **Báo rời**: ô **Lý do** (không bắt buộc). Ngày rời có hiệu lực = ngày báo + 15 ngày, 00:00. Phí vẫn trích đến ngày đó.
- **Rút lại báo rời**: được trước ngày rời có hiệu lực.
- Đến ngày rời có hiệu lực: **Đã kết thúc**, lý do "KOL/KOC rời". MCN nhận thông báo.
- Hết 12 tháng phụ lục: **Đã kết thúc**, lý do "Hết hạn phụ lục", ngừng trích phí (D19). Phụ lục hết hạn trước ngày rời có hiệu lực thì kết thúc theo hết hạn.

### Nhóm D — Đối soát và chi trả

#### FR-016: Tính phí quản lý trong kỳ đối soát

- Lúc **Lấy danh sách** (kỳ chuyển sang Đã xử lý), hệ thống tính phí cho từng khoản theo **ngày phát sinh** của khoản đó (D20): chỉ trích khi tại ngày phát sinh người đó là thành viên (Đang hợp tác hoặc Đang báo rời chưa tới ngày rời) của một MCN **Hoạt động**. Ghi lại MCN, tỷ lệ, phí của khoản.
- Thưởng view: mỗi ngày có view là một khoản, ngày phát sinh là ngày có view (không phải ngày hệ thống ghi nhận).
- Một dòng thưởng nội dung gồm nhiều ngày: phần nào phát sinh lúc thuộc MCN nào thì MCN đó được trích (D24).
- Phí một khoản = làm tròn(số tiền khoản × tỷ lệ / 100) tới đồng.
- Chỉ áp dụng cho partner bật MCN; phase 1 bật cho partner Ambassador (Q6).
- Người không thuộc MCN: không có phí, như hiện nay.

#### FR-017: Tab Người nhận

Trang chi tiết kỳ đối soát có thêm tab **Người nhận** (sau khi Lấy danh sách):

| Cột | Ghi chú |
|---|---|
| Người nhận | Tên KOL/KOC hoặc tên MCN |
| Loại | Không có MCN / Có MCN / MCN |
| MCN | Tên MCN của thành viên |
| Tỷ lệ | |
| Tổng hoa hồng | G |
| Phí quản lý | |
| Cộng vào số dư | KOL/KOC: G − phí. MCN: tổng phí của các thành viên trong kỳ |
| Trạng thái | Như trạng thái khoản hiện nay |

- Lọc theo Loại. Mỗi MCN một dòng; bấm **Xem** ở dòng MCN thấy phí của từng thành viên.
- Modal Duyệt tất cả ghi thêm số MCN nhận phí trong kỳ.

#### FR-018: Cộng vào số dư khi duyệt

- Khi duyệt, với mỗi khoản có phí:
  - KOL/KOC: số dư tăng G − phí (sổ dòng tiền ghi đủ: khoản thưởng và khoản trừ phí MCN).
  - Tài khoản MCN: số dư tăng phí, ghi rõ từ thành viên nào, kỳ nào.
- Kỳ chạy lại sau lỗi không được cộng hai lần.
- KOL/KOC và MCN nhận thông báo như thông báo đối soát hiện nay.
- Phí luôn có user nhận: MCN phải đăng nhập (đã gắn user) mới tạo được link, nên MCN có thành viên thì chắc chắn đã có user.

#### FR-019: Chi trả

- Đợt chi ở Xử lý rút tiền giữ nguyên thao tác.
- Tài khoản MCN đủ điều kiện khi: MCN Hoạt động, có tài khoản ngân hàng hiện hành, số dư từ mức tối thiểu của đợt. **Không** yêu cầu eKYC, hợp đồng điện tử `B2C_AMBASSADOR` hay liên kết AccessTrade.
- Lệnh chi của MCN: tài khoản nhận lấy từ hồ sơ pháp lý (FR-004), mã định danh (MST hoặc CCCD) lấy từ hồ sơ MCN. MCN công ty không khấu trừ thuế TNCN; MCN cá nhân khấu trừ như KOL/KOC (tạm, Q9).
- Bảng chi tiết đợt chi và file xuất ngân hàng có thêm cột Loại (KOL/KOC / MCN).
- KOL/KOC: không đổi. Khấu trừ 10% khi số chi trong đợt từ 5.000.000đ (D21). Số dư KOL/KOC đã là phần sau phí MCN.

#### FR-020: MCN xem đối soát

- Quản lý MCN › **Đối soát**: các kỳ đã duyệt có thành viên của MCN. Cột: Kỳ, Ngày cộng, Số thành viên, Tổng hoa hồng, Phí quản lý.
- **Xem** một kỳ: từng thành viên với Tỷ lệ, Tổng hoa hồng, Phí quản lý. Thành viên đã rời vẫn hiện trong các kỳ đã hợp tác (D22).
- Chỉ xem, không có nút xác nhận.

#### FR-021: KOL/KOC xem đối soát

- Avatar › **Đối soát** (mọi creator): các kỳ đã duyệt có khoản của mình. Cột: Kỳ, Ngày cộng, Tổng hoa hồng, Phí quản lý (— nếu không thuộc MCN), Cộng vào số dư.
- **Xem** một kỳ: chi tiết khoản, tỷ lệ, MCN.
- Có dòng hướng dẫn: thấy chưa đúng thì liên hệ ở Hỗ trợ nhà sáng tạo (D7).

### Nhóm E — Thông báo

#### FR-022: Email và thông báo

| Sự kiện | Gửi tới | Kênh |
|---|---|---|
| MCN được kích hoạt | Email đăng nhập MCN | Email |
| KOL/KOC đồng ý lời mời | MCN | Thông báo web |
| KOL/KOC từ chối lời mời | MCN | Thông báo web |
| KOL/KOC ký xong, thành viên mới | MCN | Thông báo web |
| Còn 2 ngày tới hạn ký | KOL/KOC | Thông báo web |
| KOL/KOC báo rời / rút lại | MCN | Thông báo web |
| MCN chấm dứt | KOL/KOC | Thông báo web |
| Rời có hiệu lực, hết hạn phụ lục | KOL/KOC, MCN | Thông báo web |
| Phí quản lý cộng vào số dư | MCN | Thông báo web |

---

## 5. Ai thấy gì, làm được gì

| Việc | Admin | Công ty MCN | KOL/KOC |
|---|---|---|---|
| Tạo, kích hoạt MCN | Làm | — | — |
| Hồ sơ pháp lý | Tải lên, cập nhật | — | — |
| Tạo, tắt link mời | — | Làm | — |
| Đồng ý lời mời, ký phụ lục | — | — | Làm |
| Danh sách thành viên | Xem | Xem | Xem MCN của mình |
| Chấm dứt thành viên | — | Làm | — |
| Báo rời, rút lại | — | — | Làm |
| Duyệt đối soát | Làm | — | — |
| Số đối soát | Xem tất cả | Phí của thành viên | Số của mình |
| Lập đợt chi | Làm | Nhận về tài khoản đứng tên MCN | Nhận như hiện nay |

---

## 6. Non-Functional Requirements

- **NFR-001 Không đổi hành vi cũ:** người không thuộc MCN, kỳ đối soát không có thành viên MCN, đợt chi không có MCN — kết quả giống hệt hiện nay.
- **NFR-002 Đúng tiền:** với mỗi khoản, (phần KOL/KOC) + (phí MCN) = số tiền khoản, không lệch đồng nào. Không cộng hai lần khi chạy lại.
- **NFR-003 Riêng tư:** MCN không tra cứu được user. MCN chỉ thấy dữ liệu thành viên của mình trong thời gian hợp tác; số liệu đối soát các kỳ đã hợp tác vẫn xem được sau khi rời (D22). Link mời không lộ thông tin MCN ngoài tên. Lời mời Hết hiệu lực không cho MCN biết KOL/KOC đã vào MCN nào.
- **NFR-004 Lưu vết:** mọi thay đổi hồ sơ pháp lý, trạng thái MCN, trạng thái thành viên đều có người, giờ, lý do. Lý do Từ chối, Chấm dứt, Báo rời lưu vào lịch sử quan hệ, hiện trong thông báo gửi bên kia và ở tab Thành viên của Admin.
- **NFR-005 Ngôn ngữ:** tiếng Việt.

---

## 7. Assumptions và phụ thuộc

| # | Phụ thuộc | Bên |
|---|---|---|
| A1 | Loại hợp đồng phụ lục chỉ định thanh toán trên dịch vụ econtract (mẫu, trường động: MCN, tỷ lệ, thời hạn) | AccessTrade core |
| A2 | Mẫu email "MCN được kích hoạt" (template code) | AccessTrade |
| A3 | Tra tên chủ tài khoản ngân hàng cho tài khoản của MCN (không có SSO user) | AccessTrade core |
| A4 | Email đăng nhập MCN là tài khoản Google (Google Workspace hoặc Google account tạo bằng email đó) | MCN |
| A5 | Văn bản Thông báo xử lý dữ liệu cá nhân cho KOL/KOC khi ký phụ lục (bản hiện hành) | AccessTrade, Legal |

---

## 8. Out of Scope (phase 1)

| Phần | Phase 1 làm thế nào |
|---|---|
| Công bố Quy chế phiên bản mới, chặn mời khi MCN chưa xác nhận | Quy chế ký ngoài hệ thống, tải lên theo từng MCN |
| Đề xuất đổi tỷ lệ phí, gia hạn phụ lục | Tỷ lệ theo link, giữ suốt thời gian hợp tác |
| Tra cứu, mời theo mã | Chỉ mời bằng link |
| KOL/KOC xác nhận/báo sai đối soát, tự xác nhận sau 5 ngày | Chỉ xem; thiếu thì Thưởng thêm kỳ sau |
| Dời khoản sang kỳ sau | Không có |
| Bảng kê tháng, MCN xác nhận, khai hóa đơn | MCN xem phí theo kỳ; hóa đơn ngoài hệ thống |
| Đợt chi riêng cho MCN | Chi chung đợt với KOL/KOC |
| Tạm dừng, Chấm dứt MCN | Không làm |
| Hàng lỗi | Không có |
| Admin thêm thành viên thay MCN | Admin chỉ xem |
| Nhiều tài khoản đăng nhập cho một MCN | Mỗi MCN một tài khoản (bảng quan hệ đã cho phép mở rộng) |
| MCN trên các app partner (parasola, …) | Chỉ app Ambassador |

---

## 9. Open Questions

| # | Câu hỏi | Đề xuất |
|---|---|---|
| Q1 | ~~Ngưỡng thuế TNCN~~ | **Đã chốt:** 5.000.000đ, tính trên số chi sau phí MCN (D21) |
| Q2 | Các trường form tạo MCN | Theo bảng FR-002 (bản mẫu 09/11), chờ AccessTrade xác nhận lần cuối |
| Q3 | Định dạng, dung lượng file hồ sơ pháp lý | PDF, JPG, PNG, ≤ 20MB (theo bản mẫu 09/11) |
| Q4 | Loại hợp đồng phụ lục trên econtract: AccessTrade core cấp mã loại và mẫu khi nào? | Phụ thuộc A1, cần trước khi làm FR-014 |
| Q5 | ~~Thời điểm xét tư cách thành viên~~ | **Đã chốt:** theo ngày phát sinh từng khoản; không trích khoản trước ngày ký (D20) |
| Q6 | MCN chỉ áp dụng cho kỳ đối soát của partner Ambassador, hay mọi partner mà thành viên tham gia? | Chỉ Ambassador |
| Q7 | ~~Hết 12 tháng phụ lục~~ | **Đã chốt:** tự kết thúc (D19) |
| Q8 | Thu nhập từ nội dung của chính tài khoản MCN công ty: khi chi, cả số dư được miễn khấu trừ TNCN? | Có — tài khoản MCN công ty chi không khấu trừ |
| Q9 | Thuế TNCN của MCN cá nhân: chung ngưỡng và mức 10% như KOL/KOC? Chứng từ khấu trừ cấp thế nào? | Tạm làm như KOL/KOC, chứng từ ngoài hệ thống; họp 10/11/2026 chốt |
| Q10 | ~~MCN có thấy tên KOL/KOC đang Chờ ký không?~~ | **Đã chốt:** có, chỉ tên. MCN gửi link cho người mình đã biết. Thông tin khác chỉ hiện sau khi ký và đồng ý chia sẻ dữ liệu |
| Q11 | Thưởng mốc đạt sau ngày ký nhưng nhờ video đăng trước ngày ký; thưởng thêm tạo sau ngày ký để bù khoảng trước ngày ký: có trích phí MCN không? | Đề xuất: có, tính theo ngày khoản được ghi nhận |
| Q12 | MCN (nhất là MCN cá nhân) đã có tài khoản creator: dùng chung tài khoản đó (cùng nick Google) để quản lý MCN được không? FR-002 đang chặn email trùng, mâu thuẫn với nguyên tắc 2 và D14 | Đề xuất: cho dùng chung. Kích hoạt thì gắn luôn tài khoản có sẵn; chỉ chặn khi tài khoản đó đang là thành viên của một MCN |
| Q13 | ~~Lý do Từ chối, Chấm dứt, Báo rời có hiện cho bên kia không?~~ | **Đã chốt:** có, hiện trong thông báo gửi bên kia; Admin thấy ở tab Thành viên |

---

## 10. Revision History

| Version | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-11-04 | Bản đầu, theo scope chốt 03/11/2026 và bản mẫu giao diện v47. Vai MCN và thành viên dùng bảng quan hệ, không dùng loại tài khoản |
| 1.1 | 2026-11-09 | Thêm D17–D24: MCN cá nhân, tỷ lệ 0–100%, Chờ ký chưa phải thành viên và được Chờ ký nhiều MCN, hết 12 tháng tự kết thúc, trích phí theo ngày phát sinh, thuế 5.000.000đ trên số sau phí, MCN xem kỳ cũ sau rời, eKYC/hợp đồng gốc ở trang có sẵn, đổi MCN trong kỳ. Đóng Q1, Q5, Q7; thêm Q9–Q13, đóng Q10, Q13. Đồng bộ với bản mẫu 09/11: file PDF/JPG/PNG, ô lý do khi Từ chối/Chấm dứt/Báo rời, Thông báo xử lý dữ liệu cá nhân ở màn ký (A5), thông báo khi KOL/KOC từ chối |
