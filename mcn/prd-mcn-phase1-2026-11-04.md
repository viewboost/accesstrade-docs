# Product Requirements Document: MCN trên KOC Ambassador — Phase 1

**Date:** 2026-11-04
**Author:** Vinh Nguyễn
**Version:** 1.0
**Status:** Draft — chờ review
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

> **Khác với 08-Sequence:** 08 tạo tài khoản MCN bằng `account_type=MCN` (SD-01). Phase 1 **không** làm vậy, xem nguyên tắc 2. 08 cũng có bảng kê tháng, hóa đơn, đợt chi riêng cho MCN, xác nhận/báo sai đối soát, công bố Quy chế phiên bản mới — đều để sau (mục 9).

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **MCN** | Công ty quản lý một nhóm KOL/KOC. Trên hệ thống là một **hồ sơ MCN** do AccessTrade tạo |
| **Tài khoản MCN** | User đăng nhập web Ambassador, được gắn với hồ sơ MCN qua bảng quan hệ. Phase 1: mỗi MCN một tài khoản |
| **Thành viên** | KOL/KOC đã ký phụ lục và đang thuộc một MCN. Lưu ở bảng quan hệ thành viên |
| **Link mời** | Link do MCN tạo, gắn một tỷ lệ phí 1–99%. Dùng được cho nhiều người |
| **Phí quản lý** | Phần hoa hồng của thành viên dành cho MCN = tổng hoa hồng × tỷ lệ |
| **Phụ lục** | Phụ lục chỉ định thanh toán, KOL/KOC ký trên hợp đồng điện tử, thời hạn 12 tháng |
| **Kỳ đối soát** | Kỳ ở Admin › Đối soát đang có. Trạng thái: Chờ duyệt → Đã xử lý → Đã hoàn thành, hoặc Đã từ chối |
| **Đợt chi** | Đợt ở Admin › Xử lý rút tiền đang có. Hệ thống tạo lệnh chi toàn bộ số dư cho người đủ điều kiện |
| **G** | Tổng hoa hồng của một người trong kỳ (chiến dịch, nhiệm vụ, thưởng thêm) |

---

## 1. Executive Summary

AccessTrade muốn cho các công ty MCN đưa KOL/KOC của họ lên KOC Ambassador và nhận phí quản lý trực tiếp từ hoa hồng của thành viên, thay vì tự thu ngoài hệ thống.

```
AccessTrade tạo hồ sơ MCN, tải lên 5 hồ sơ pháp lý, kích hoạt
  → MCN đăng nhập, tạo link mời kèm tỷ lệ phí, gửi cho KOL/KOC
  → KOL/KOC mở link, đồng ý, ký phụ lục → thành viên
  → Kỳ đối soát được duyệt: KOL/KOC nhận G − phí, MCN nhận phí, vào số dư
  → AccessTrade lập đợt chi như hiện nay: KOL/KOC trừ thuế TNCN theo ngưỡng, MCN không trừ thuế
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
| Thuế TNCN | Tính lúc chi, 10% trên số chi khi số chi **từ 5.000.000đ** (theo code). Xem câu hỏi Q1 |
| Hợp đồng điện tử, eKYC | Qua dịch vụ econtract của AccessTrade core, một loại hợp đồng `B2C_AMBASSADOR`. Chưa có loại phụ lục |
| Đăng nhập | Google, TikTok, Facebook, mật khẩu. Không có trang đăng ký riêng: đăng nhập lần đầu rồi chấp nhận điều khoản là thành tài khoản |

### 2.2 Quyết định phase 1

| # | Quyết định |
|---|---|
| D1 | Chỉ mời bằng link. Không tra cứu, không mời theo mã/số điện thoại |
| D2 | Mỗi link một tỷ lệ 1–99%. Thành viên giữ tỷ lệ của link đã dùng suốt thời gian hợp tác. Không đổi tỷ lệ giữa chừng |
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

---

## 3. User Personas

| Persona | Ở đâu | Làm gì |
|---|---|---|
| **Admin AccessTrade** (vai `admin`) | Admin › Danh sách MCN, Đối soát, Xử lý rút tiền | Tạo, kích hoạt MCN; quản lý hồ sơ pháp lý; duyệt đối soát; lập đợt chi |
| **Công ty MCN** | Web › avatar › Quản lý MCN | Tạo/tắt link mời, theo dõi lời mời và thành viên, chấm dứt thành viên, xem phí theo kỳ |
| **KOL/KOC** | Web › link mời; avatar › MCN của tôi, Đối soát | Đồng ý lời mời, ký phụ lục, báo rời/rút lại, xem số đối soát |

---

## 4. Functional Requirements

### Nhóm A — Admin: hồ sơ MCN

#### FR-001: Danh sách MCN

Menu trái Admin có mục **Danh sách MCN** (vai `admin`).

- Cột: Tên pháp nhân, Email đăng nhập, Số thành viên, Trạng thái, Ngày tạo.
- Lọc trạng thái: Chờ kích hoạt, Hoạt động. Tìm theo tên, MST, email.
- Nút **Tạo MCN**.

#### FR-002: Tạo hồ sơ MCN

| Trường | Bắt buộc | Kiểm tra |
|---|---|---|
| Tên pháp nhân | Có | Dùng để đối chiếu tên chủ tài khoản ngân hàng |
| Mã số thuế | Có | 10 hoặc 13 số; không trùng MCN khác |
| Email đăng nhập | Có | Đúng định dạng; không trùng email của user đã có; không trùng MCN khác |
| Địa chỉ trụ sở, Người đại diện theo pháp luật, Số điện thoại | Không | |

- Tạo xong: trạng thái **Chờ kích hoạt**, mở trang chi tiết ở tab Điều kiện kích hoạt.
- Email trùng: báo "Email đã được dùng cho một tài khoản khác".
- Danh sách trường đang chờ chốt (Q2).

#### FR-003: Hồ sơ pháp lý (5 điều kiện kích hoạt)

| Điều kiện | Cách nhập |
|---|---|
| Hồ sơ KYB | Tải lên file |
| Hợp đồng khung | Tải lên file đã ký số + ngày ký |
| Thỏa thuận xử lý dữ liệu cá nhân | Tải lên file đã ký số + ngày ký |
| Tài khoản ngân hàng | FR-004 |
| Quy chế chương trình, Quy tắc ứng xử đã ký | Tải lên file đã ký số + ngày ký |

- File: PDF, tối đa 20MB (Q3).
- Mỗi điều kiện đã đạt có nút **Xem**: thông tin đã nhập, file, ngày giờ và người cập nhật, lịch sử thay đổi.
- Cập nhật lần sau tạo bản mới; bản cũ vẫn trong lịch sử, không xóa.
- Sau khi kích hoạt, tab đổi tên thành **Hồ sơ pháp lý**, vẫn cập nhật được như trên.

#### FR-004: Tài khoản ngân hàng của MCN

- Admin chọn ngân hàng, nhập số tài khoản, bấm **Kiểm tra**. Hệ thống tra tên chủ tài khoản.
- Tên khớp tên pháp nhân (so không dấu, không phân biệt hoa thường, bỏ khoảng trắng thừa): lưu được ngay.
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

- Bấm **Mời KOL/KOC** → nhập tỷ lệ phí (số nguyên 1–99) → **Tạo link**.
- Hiện link `…/mcn/moi/<mã>` và nút **Sao chép**. MCN tự gửi qua kênh của mình.
- Tỷ lệ ngoài 1–99: báo lỗi, không tạo.
- Mỗi link một mã ngẫu nhiên, không đoán được, không lộ thông tin user.

#### FR-009: Mục Lời mời

- Bảng **Link mời**: Link, Tỷ lệ, Ngày tạo, Số người đã tham gia, Trạng thái (Đang dùng/Đã tắt), Sao chép, **Tắt link**.
- Tắt link: không ai mở link đó được nữa (hiện "Link mời đã ngừng"). Người đã đồng ý nhưng chưa ký vẫn ký tiếp được trong hạn. Thành viên đã vào không ảnh hưởng. Không bật lại (tạo link mới).
- Bảng **Người đã đồng ý**: người đã đồng ý nhưng chưa thành viên. Tên, Tỷ lệ, Ngày đồng ý, Trạng thái (Chờ ký phụ lục kèm hạn ký, Đã từ chối, Quá hạn ký).

#### FR-010: Mục Thành viên (MCN)

- Bảng: Tên, Tỷ lệ, Ngày tham gia, Trạng thái, Ghi chú (ngày rời có hiệu lực / lý do kết thúc), nút **Chấm dứt**.
- MCN chỉ thấy thông tin thành viên trong thời gian hợp tác. Đã kết thúc: chỉ còn tên, ngày và trạng thái.

#### FR-011: MCN chấm dứt thành viên

- Xác nhận bằng modal. Hiệu lực ngay, kể cả khi thành viên đang báo rời.
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
| Đã đồng ý một lời mời khác, chưa ký | Phải từ chối lời mời kia trước |

#### FR-013: Đồng ý lời mời

- Lời mời ghi: tên MCN, tỷ lệ phí, thời hạn phụ lục 12 tháng, báo trước khi rời 15 ngày, ví dụ với thu nhập 3.000.000đ (phí, phần còn lại), câu "Thuế TNCN tính khi AccessTrade chi tiền, như hiện nay".
- Phải tick **Tôi đã hiểu** mới bấm **Đồng ý** được. Có nút **Từ chối**.
- Đồng ý: tạo dòng thành viên trạng thái **Chờ ký phụ lục**, hạn ký 7 ngày; ghi tỷ lệ của link vào dòng này (tắt link sau đó không đổi tỷ lệ).

#### FR-014: Ký phụ lục

- Chưa eKYC: chặn, dẫn sang **Thông tin định danh**. Làm xong quay lại ký tiếp.
- Tick riêng **Đồng ý chia sẻ dữ liệu cho MCN** (bắt buộc, lưu thời điểm).
- Ký trên hợp đồng điện tử (loại phụ lục mới, Q4). Ký xong: thành viên **Đang hợp tác**, ngày bắt đầu = ngày ký, ngày kết thúc phụ lục = +12 tháng.
- Quá 7 ngày chưa ký: **Quá hạn ký**, phải mở lại link để đồng ý lại.

#### FR-015: MCN của tôi, báo rời

- Avatar › **MCN của tôi**: hiện cho người có lời mời đang chờ hoặc đang là thành viên. Người không thuộc MCN không thấy mục này.
- Nội dung: tên MCN, tỷ lệ, ngày tham gia, ngày kết thúc phụ lục, trạng thái.
- **Báo rời**: ngày rời có hiệu lực = ngày báo + 15 ngày, 00:00. Phí vẫn trích đến ngày đó.
- **Rút lại báo rời**: được trước ngày rời có hiệu lực.
- Đến ngày rời có hiệu lực: **Đã kết thúc**, lý do "KOL/KOC rời". MCN nhận thông báo.

### Nhóm D — Đối soát và chi trả

#### FR-016: Tính phí quản lý trong kỳ đối soát

- Lúc **Lấy danh sách** (kỳ chuyển sang Đã xử lý), với mỗi khoản của mỗi người, hệ thống xét người đó có đang là thành viên (Đang hợp tác hoặc Đang báo rời chưa tới ngày rời) của một MCN **Hoạt động** không. Có: ghi lại MCN, tỷ lệ, phí của khoản đó. Thời điểm xét: xem Q5.
- Phí một khoản = làm tròn(số tiền khoản × tỷ lệ / 100) tới đồng.
- Chỉ áp dụng cho kỳ đối soát của partner Ambassador (Q6).
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
- Lệnh chi của MCN: không khấu trừ thuế TNCN, tài khoản nhận lấy từ hồ sơ pháp lý (FR-004), MST lấy từ hồ sơ MCN.
- Bảng chi tiết đợt chi và file xuất ngân hàng có thêm cột Loại (KOL/KOC / MCN).
- KOL/KOC: không đổi. Khấu trừ 10% khi số chi trong đợt từ ngưỡng (Q1).

#### FR-020: MCN xem đối soát

- Quản lý MCN › **Đối soát**: các kỳ đã duyệt có thành viên của MCN. Cột: Kỳ, Ngày cộng, Số thành viên, Tổng hoa hồng, Phí quản lý.
- **Xem** một kỳ: từng thành viên với Tỷ lệ, Tổng hoa hồng, Phí quản lý.
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
| KOL/KOC ký xong, thành viên mới | MCN | Thông báo web |
| Còn 2 ngày tới hạn ký | KOL/KOC | Thông báo web |
| KOL/KOC báo rời / rút lại | MCN | Thông báo web |
| MCN chấm dứt | KOL/KOC | Thông báo web |
| Rời có hiệu lực | KOL/KOC, MCN | Thông báo web |
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
| Lập đợt chi | Làm | Nhận về tài khoản công ty | Nhận như hiện nay |

---

## 6. Non-Functional Requirements

- **NFR-001 Không đổi hành vi cũ:** người không thuộc MCN, kỳ đối soát không có thành viên MCN, đợt chi không có MCN — kết quả giống hệt hiện nay.
- **NFR-002 Đúng tiền:** với mỗi khoản, (phần KOL/KOC) + (phí MCN) = số tiền khoản, không lệch đồng nào. Không cộng hai lần khi chạy lại.
- **NFR-003 Riêng tư:** MCN không tra cứu được user. MCN chỉ thấy dữ liệu thành viên của mình trong thời gian hợp tác. Link mời không lộ thông tin MCN ngoài tên.
- **NFR-004 Lưu vết:** mọi thay đổi hồ sơ pháp lý, trạng thái MCN, trạng thái thành viên đều có người, giờ, lý do.
- **NFR-005 Ngôn ngữ:** tiếng Việt.

---

## 7. Assumptions và phụ thuộc

| # | Phụ thuộc | Bên |
|---|---|---|
| A1 | Loại hợp đồng phụ lục chỉ định thanh toán trên dịch vụ econtract (mẫu, trường động: MCN, tỷ lệ, thời hạn) | AccessTrade core |
| A2 | Mẫu email "MCN được kích hoạt" (template code) | AccessTrade |
| A3 | Tra tên chủ tài khoản ngân hàng cho tài khoản công ty | AccessTrade core |
| A4 | Email đăng nhập MCN là tài khoản Google (Google Workspace hoặc Google account tạo bằng email đó) | MCN |

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
| Q1 | Ngưỡng thuế TNCN: nghiệp vụ nói 2.000.000đ, code đang 5.000.000đ (`MinTaxableRevenue`). Ngưỡng nào đúng? Đổi có ảnh hưởng mọi creator, không riêng MCN | Chốt với kế toán trước khi code; nếu đổi thì làm thành việc riêng |
| Q2 | Các trường form tạo MCN (tài liệu 01/09) | Đang dùng bảng FR-002 |
| Q3 | Định dạng, dung lượng file hồ sơ pháp lý | PDF, ≤ 20MB |
| Q4 | Loại hợp đồng phụ lục trên econtract: AccessTrade core cấp mã loại và mẫu khi nào? | Phụ thuộc A1, cần trước khi làm FR-014 |
| Q5 | Thời điểm xét tư cách thành viên để tính phí: lúc Lấy danh sách (đề xuất), hay theo ngày phát sinh từng khoản? Thu nhập phát sinh trước ngày ký phụ lục có bị trích không? | Lúc Lấy danh sách — đơn giản, Admin thấy trước khi duyệt |
| Q6 | MCN chỉ áp dụng cho kỳ đối soát của partner Ambassador, hay mọi partner mà thành viên tham gia? | Chỉ Ambassador |
| Q7 | Hết 12 tháng phụ lục mà phase 1 không có gia hạn: thành viên tự kết thúc, hay giữ nguyên? | Cần chốt |
| Q8 | Thu nhập từ nội dung của chính tài khoản MCN: khi chi, cả số dư được miễn khấu trừ TNCN (vì người nhận là công ty)? | Có — tài khoản MCN chi không khấu trừ |

---

## 10. Revision History

| Version | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-11-04 | Bản đầu, theo scope chốt 03/11/2026 và bản mẫu giao diện v47. Vai MCN và thành viên dùng bảng quan hệ, không dùng loại tài khoản |
