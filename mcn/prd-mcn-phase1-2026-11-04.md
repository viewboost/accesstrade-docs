# Product Requirements Document: MCN trên KOC Ambassador — Phase 1

**Date:** 2026-11-04
**Author:** Vinh Nguyễn
**Version:** 1.10 (cập nhật 2026-11-27)
**Status:** Bản mới nhất, **đồng bộ với code** đang chạy trên develop ngày 27/11/2026 (`bcab41658`). Gồm các chốt của anh Vĩnh (review PR #41, #42, group dự án 14–16/11), chị Huyền (Sheet test QC 16–17/11, file nghiệm thu 23–26/11) và anh Định (27/11). Không còn câu hỏi mở. Thay đổi so với bản trước xem mục 10
**Phạm vi nghiệp vụ:** MCN áp dụng cho **tất cả partner/ADV**. Phí quản lý áp dụng cho thu nhập từ các chiến dịch của mọi partner khi đủ điều kiện ở FR-016.

**Phạm vi giao diện phase 1:** App Ambassador (`frontend/`) và Admin (`admin/`). Các app partner (parasola, vpbank, …) là bản copy riêng, chưa bổ sung giao diện MCN trong phase 1; thu nhập từ chiến dịch của các partner này vẫn thuộc phạm vi tính phí MCN.

---

## Document Overview

PRD cho phase 1 của MCN (công ty quản lý KOL/KOC) trên KOC Ambassador, theo scope chốt ở buổi họp 03/11/2026 và các quyết định bổ sung sau buổi họp.

### Nguyên tắc

1. **Đối soát và chi trả giữ luồng hiện nay, thêm phần MCN.** Đối soát: lúc Lấy danh sách tính phí quản lý của thành viên có MCN, lúc duyệt tách phí vào số dư MCN (FR-016, FR-018). Duyệt có thêm trạng thái Duyệt lỗi và thao tác Duyệt lại (D8). Chi trả vẫn là đợt chi ở Xử lý rút tiền, có thêm MCN là người nhận; lệnh của MCN chi theo từng chiến dịch (FR-019).
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
| **Tài khoản MCN** | User đăng nhập web Ambassador, được gắn với hồ sơ MCN qua bảng quan hệ. Phase 1: mỗi MCN một tài khoản. Tài khoản chỉ để thao tác; số dư phí thuộc **hồ sơ MCN**, không thuộc user này. Phase 1 không đổi được tài khoản này sau khi kích hoạt (D27) |
| **Số dư MCN** | Số dư của hồ sơ MCN: phí quản lý từ thành viên và thu nhập nội dung của tài khoản nhà (D14). Chi về tài khoản ngân hàng đứng tên MCN (FR-019) |
| **Tài khoản nhà** | Người đứng MCN tự làm nội dung: tham gia chính MCN của mình bằng link 100% (D14). Gồm tài khoản vận hành MCN và tài khoản creator có CCCD trên hợp đồng điện tử trùng CCCD của MCN cá nhân đang hoạt động (cùng một người, khác email). Các tài khoản này chỉ được vào chính MCN đó, tỷ lệ 100% |
| **Thành viên** | KOL/KOC đã ký phụ lục và đang thuộc một MCN. Lưu ở bảng quan hệ thành viên |
| **Chờ ký** | KOL/KOC đã bấm Đồng ý lời mời nhưng chưa ký phụ lục. **Chưa phải thành viên** |
| **Link mời** | Link do MCN tạo, gắn một tỷ lệ phí 0–100%. Dùng được cho nhiều người |
| **Phí quản lý** | Phần hoa hồng của thành viên dành cho MCN = tổng hoa hồng × tỷ lệ |
| **Phụ lục** | Phụ lục chỉ định thanh toán, KOL/KOC ký trên hợp đồng điện tử, thời hạn 12 tháng |
| **Kỳ đối soát** | Kỳ ở Admin › Đối soát đang có. Trạng thái: Chờ duyệt → Đã xử lý → Đang chạy → Đã hoàn thành, hoặc Duyệt lỗi (Admin bấm Duyệt lại), hoặc Đã từ chối (D8) |
| **Đợt chi** | Đợt ở Admin › Xử lý rút tiền đang có. Hệ thống tạo lệnh chi toàn bộ số dư cho người đủ điều kiện |
| **G** | Tổng hoa hồng của một người trong kỳ: thưởng nội dung, thưởng mốc, thưởng thêm. Nhiệm vụ trả bằng điểm, không qua đối soát nên không bị tính phí |
| **Ngày phát sinh** | Ngày của từng khoản thưởng: thưởng view là ngày có view; thưởng mốc theo số bài là ngày nộp bài chạm mốc (kể cả khi bài được duyệt, đủ lượt xem và hệ thống ghi nhận mốc vào ngày sau); thưởng mốc theo lượt xem là ngày hệ thống ghi nhận mốc; thưởng thêm là ngày Admin tạo (Q11, chị Huyền chốt 26/11) |

---

## 1. Executive Summary

AccessTrade muốn cho các MCN (công ty hoặc cá nhân) đưa KOL/KOC của họ lên KOC Ambassador và nhận phí quản lý trực tiếp từ hoa hồng của thành viên, thay vì tự thu ngoài hệ thống.

```
AccessTrade tạo hồ sơ MCN, tải lên 5 hồ sơ pháp lý, kích hoạt
  → MCN đăng nhập, tạo link mời kèm tỷ lệ phí, gửi cho KOL/KOC
  → KOL/KOC mở link, đồng ý, ký phụ lục → thành viên
  → Kỳ đối soát được duyệt: KOL/KOC nhận G − phí, MCN nhận phí, vào số dư
  → AccessTrade lập đợt chi như hiện nay: KOL/KOC trừ thuế TNCN theo ngưỡng, MCN công ty không trừ thuế, MCN cá nhân trừ 10% theo ngưỡng
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
| D8 | Đối soát giữ trạng thái hiện có, thêm **Duyệt lỗi**. Duyệt xong: KOL/KOC nhận G − phí, MCN nhận phí, vào số dư. Sau khi duyệt hệ thống kiểm lại sổ; mục ghi tiền lỗi hoặc sổ không khớp thì kỳ ở **Duyệt lỗi**, gửi ngay email cảnh báo lệch. Admin bấm **Duyệt lại** để chạy nốt các mục còn chờ, không cộng hai lần; kỳ Duyệt lỗi không Hủy được. Duyệt lại xong vẫn gửi hoa hồng giới thiệu trên mọi mục của kỳ. ADV còn kỳ Đang chạy hoặc Duyệt lỗi thì chưa Lấy danh sách đợt chi (FR-019). Áp dụng cho mọi kỳ, kể cả kỳ không có MCN (anh Vĩnh chốt qua review PR #42 ngày 12/11 và group dự án 14/11; email cảnh báo và hoa hồng giới thiệu bổ sung 25/11) |
| D9 | Chi trả độc lập với đối soát, qua đợt chi ở Xử lý rút tiền. MCN được chi chung đợt. MCN công ty không khấu trừ thuế TNCN; MCN cá nhân khấu trừ 10% khi lệnh của MCN trong đợt từ 5.000.000đ (họp 10/11, FR-019) |
| D10 | Thuế TNCN không tính ở đối soát, chỉ tính lúc chi |
| D11 | KOL/KOC đang thuộc MCN khác không nhận được lời mời, phải rời MCN cũ trước |
| D12 | Không có Tạm dừng, Chấm dứt MCN |
| D13 | Hóa đơn GTGT cho phí quản lý xử lý ngoài hệ thống |
| D14 | Người đứng MCN được làm nội dung trên cùng tài khoản. Muốn tiền nội dung gộp với MCN thì tham gia chính MCN của mình bằng link 100% (tài khoản nhà): tiền vào số dư MCN, chi và tính thuế một lần cùng phí quản lý. Chưa ký phụ lục 100% thì thu nhập nội dung vẫn chi như creator bình thường (họp 10/11) |
| D15 | Báo trước khi rời: 15 ngày |
| D16 | Vai MCN và tư cách thành viên lưu bằng bảng quan hệ, không đặt loại tài khoản trên user |
| D17 | MCN có hai loại: Công ty và Cá nhân, cùng một luồng. Loại không đổi sau khi tạo |
| D18 | Ký xong phụ lục mới là thành viên. Chờ ký chưa phải thành viên: KOL/KOC được Chờ ký nhiều MCN cùng lúc, không có thao tác hủy. Ký xong một MCN thì các lời mời Chờ ký khác chuyển **Hết hiệu lực**. Mỗi KOL/KOC chỉ mở ký một phụ lục tại một thời điểm, để không ký cùng lúc hai phụ lục; muốn ký MCN khác thì ký xong, chờ hết hạn hoặc từ chối lời mời đang ký (anh Định chốt 27/11) |
| D19 | Hết 12 tháng phụ lục: quan hệ tự kết thúc, ngừng trích phí. Muốn tiếp tục thì ký lại qua link mời mới |
| D20 | Không trích phí trên khoản phát sinh trước ngày kích hoạt thành viên (chốt 11/11) hoặc từ ngày kết thúc. Xét theo ngày phát sinh của từng khoản, không theo ngày Lấy danh sách (thay đề xuất Q5) |
| D21 | Thuế TNCN của KOL/KOC: 10% trên số chi (đã trừ phí MCN) khi số chi trong đợt từ 5.000.000đ. MCN công ty không khấu trừ |
| D22 | MCN vẫn xem được chi tiết đối soát các kỳ đã hợp tác sau khi thành viên rời; không thấy thu nhập sau khi rời |
| D23 | KOL/KOC chưa eKYC hoặc chưa ký hợp đồng gốc `B2C_AMBASSADOR` thì làm ở trang Hợp đồng điện tử có sẵn, xong quay lại ký phụ lục. Phụ lục đi kèm hợp đồng gốc, chỉ ký được khi hợp đồng gốc đã ký (chị Huyền xác nhận 14/11 sau khi trao đổi với anh Vĩnh, tổng hợp luồng ký gửi group dự án) |
| D24 | Không có luồng đổi MCN. Nếu KOL/KOC rời MCN rồi tham gia MCN khác trong cùng kỳ đối soát, mỗi MCN chỉ được trích phí trên phần khoản phát sinh trong thời gian KOL/KOC là thành viên của MCN đó |
| D25 | Chỉ trích phí trên khoản thuộc chiến dịch bắt đầu từ 00:00 01/12/2026 giờ Việt Nam. Mốc là một hằng số trong code; dời mốc thì sửa code rồi deploy (chốt 12/11, FR-016) |
| D26 | MCN áp dụng cho **tất cả partner/ADV**. Khoản thưởng của thành viên từ chiến dịch của mọi partner đều được xét phí theo FR-016; không giới hạn ở partner Ambassador (Định xác nhận trong comment PR #41 ngày 13/11) |
| D27 | Phase 1 không cho đổi chủ/người vận hành MCN (tài khoản MCN); cần đổi thì để phase sau (anh Vĩnh chốt 16/11). Thông tin hồ sơ MCN (tên, mã định danh, email đăng nhập, người đại diện, địa chỉ, SĐT) sửa được khi còn **Chờ kích hoạt**; đã Hoạt động thì không sửa. Không đổi loại MCN (D17). Hồ sơ pháp lý vẫn cập nhật được (FR-003), kể cả tài khoản ngân hàng (D29, FR-004) (anh Định chốt 27/11, thay "không sửa ở bất kỳ trạng thái nào", đóng Q14) |
| D28 | File hồ sơ pháp lý: PDF, JPG hoặc PNG, tối đa **10MB** mỗi tệp. Hồ sơ định danh của MCN cá nhân là hai tệp, mặt trước và mặt sau CCCD; thiếu một mặt thì điều kiện chưa đạt (chị Huyền chốt 17/11 qua Sheet test QC, MCN-12, MCN-19; thay 20MB ở Q3) |
| D29 | Tài khoản ngân hàng của MCN: Admin chọn ngân hàng, nhập số tài khoản và tên chủ tài khoản theo giấy tờ ngân hàng. **Không** tra, không đối chiếu tên chủ tài khoản với AccessTrade (chị Huyền chốt 16–17/11 qua Sheet test QC, MCN-15, MCN-16). **Sửa được** cả trước và sau kích hoạt: mỗi lần lưu là một bản mới, bản cũ giữ trong lịch sử; lệnh chi đã tạo giữ tài khoản lúc tạo lệnh (chị Huyền chốt 26/11, thay "chỉ nhập một lần" ở MCN-17). Bỏ phụ thuộc A3. Tra thông tin ngân hàng qua AT-Core để phase sau (Q15) |
| D30 | MCN **không thấy** người đang Chờ ký phụ lục, chỉ nhận thông báo khi có người đồng ý. Ký xong thì người đó có trong mục Thành viên (chị Huyền chốt 16/11 qua Sheet test QC, MCN-42, MCN-51; thay chốt ở Q10) |
| D31 | KOL/KOC đang Chờ ký với một MCN được ký hợp đồng gốc `B2C_AMBASSADOR` và làm các bước đi kèm (thông tin thanh toán, mã số thuế, xác thực danh tính) dù chưa đủ doanh thu 50.000đ, để ký tiếp phụ lục. KOL/KOC không có lời mời giữ điều kiện cũ (anh Vĩnh, group dự án 16/11) |
| D32 | Nhân sự không có quyền xem dữ liệu nhạy cảm (`user.view_sensitive`) thấy dữ liệu MCN dạng che, ở mọi loại MCN và mọi trạng thái: SĐT giữ 3 số cuối; email (email đăng nhập, email tài khoản vận hành đang dùng và đã thu hồi) thay phần trước @ bằng đúng 3 dấu \*; địa chỉ giữ 3 ký tự đầu và 3 ký tự cuối; CCCD giữ 3 số cuối; số tài khoản giữ 4 số cuối. MST của MCN công ty giữ nguyên. Áp dụng ở Danh sách MCN, chi tiết MCN và lệnh chi MCN ở Xử lý rút tiền; file xuất chi tiền cho ngân hàng giữ đủ số. Email đã che không sao chép được. Tìm kiếm vẫn chạy trên dữ liệu gốc (chị Huyền chốt 25–26/11, file nghiệm thu #1) |
| D33 | Hồ sơ pháp lý MCN tách quyền: **Xem** tệp cần quyền xem MCN (`mcn.view`), **Tải về** cần quyền tải hồ sơ MCN (`mcn.export`), tải tệp lên cần quyền sửa MCN (`mcn.edit`). Ảnh CCCD của MCN cá nhân chỉ người có `user.view_sensitive` mới xem hoặc tải được (quyết định 12/11, FR-003) |

---

## 3. User Personas

| Persona | Ở đâu | Làm gì |
|---|---|---|
| **Admin AccessTrade** (nhân sự Admin theo quyền: `mcn.view`, `mcn.edit`, `mcn.activate`, `mcn.export`, quyền đối soát, quyền đợt chi) | Admin › Danh sách MCN, Đối soát, Xử lý rút tiền | Tạo, kích hoạt MCN; quản lý hồ sơ pháp lý; duyệt đối soát; lập đợt chi |
| **MCN (công ty hoặc cá nhân)** | Web › avatar › Quản lý MCN | Tạo/tắt link mời, theo dõi lời mời và thành viên, chấm dứt thành viên, xem phí theo kỳ |
| **KOL/KOC** | Web › link mời; avatar › MCN của tôi, Đối soát | Đồng ý lời mời, ký phụ lục, báo rời/rút lại, xem số đối soát |

---

## 4. Functional Requirements

### Nhóm A — Admin: hồ sơ MCN

#### FR-001: Danh sách MCN

Menu trái Admin có mục **Danh sách MCN** cho nhân sự có quyền xem MCN (`mcn.view`), nằm giữa menu Hồ sơ và Thông số.

- Cột: Tên MCN, Loại, Email đăng nhập (che theo D32), Thành viên (số đang hợp tác), Trạng thái, Ngày tạo.
- Lọc loại: Công ty, Cá nhân. Lọc trạng thái: Chờ kích hoạt, Hoạt động. Tìm theo tên, MST/CCCD, email.
- Nút **Tạo MCN**.

#### FR-002: Tạo hồ sơ MCN

Bước đầu chọn **Loại MCN**: Công ty hoặc Cá nhân. Không đổi được sau khi tạo.

| Trường | Công ty | Cá nhân | Kiểm tra |
|---|---|---|---|
| Tên (bắt buộc) | Tên pháp nhân | Họ và tên theo CCCD | |
| Mã định danh (bắt buộc) | Mã số thuế | Số CCCD (cũng là MST cá nhân) | Công ty 10 hoặc 13 số; cá nhân 12 số; không trùng MCN khác |
| Email đăng nhập (bắt buộc) | | | Đúng định dạng; không trùng MCN khác. Được trùng email của tài khoản creator đang có: tài khoản đó vừa quản lý MCN vừa đăng bài như creator (Q12). Không được là tài khoản đang là thành viên hoặc đang Chờ ký phụ lục với MCN khác. Quan hệ với chính MCN này chỉ được phép ở tỷ lệ 100% (đồng bộ INV-03b của tech spec; xem mục 9.1) |
| Không bắt buộc | Địa chỉ trụ sở, Người đại diện theo pháp luật, Số điện thoại | Địa chỉ liên hệ, Số điện thoại | |

- Tạo xong: trạng thái **Chờ kích hoạt**, mở trang chi tiết ở tab Điều kiện kích hoạt.
- Email đã thuộc tài khoản đang là thành viên của MCN khác: báo "Tài khoản này đang là thành viên của một MCN". Email đang Chờ ký phụ lục với MCN khác: báo "Tài khoản này đang chờ ký phụ lục với một MCN khác". Email đã dùng cho MCN khác: báo "Email đã được dùng cho MCN khác".
- Kiểm tra lại điều kiện email khi kích hoạt MCN, vì quan hệ của tài khoản có thể thay đổi sau khi tạo hồ sơ.
- Còn Chờ kích hoạt thì sửa được thông tin hồ sơ: nút **Sửa thông tin** ở tab Thông tin hồ sơ (cần quyền sửa MCN), kiểm như lúc tạo, không đổi loại MCN. Ghi nhật ký mỗi lần sửa. Đã Hoạt động thì tab chỉ để xem (D27).

#### FR-003: Hồ sơ pháp lý (5 điều kiện kích hoạt)

| Điều kiện | Cách nhập |
|---|---|
| Hồ sơ định danh | Tải lên file. Công ty: hồ sơ KYB. Cá nhân: CCCD, hai tệp mặt trước và mặt sau |
| Hợp đồng khung | Tải lên file đã ký số + ngày ký |
| Thỏa thuận xử lý dữ liệu cá nhân | Tải lên file đã ký số + ngày ký |
| Tài khoản ngân hàng | FR-004 |
| Quy chế chương trình, Quy tắc ứng xử đã ký | Tải lên file đã ký số + ngày ký |

- File: PDF, JPG hoặc PNG, tối đa 10MB mỗi tệp (D28). MCN cá nhân tải mặt trước và mặt sau CCCD ở hai ô riêng; thiếu một mặt thì điều kiện chưa đạt.
- Số CCCD, số tài khoản, SĐT, email, địa chỉ hiện dạng che theo D32. Chỉ người có quyền xem dữ liệu nhạy cảm (`user.view_sensitive`) mới xem đầy đủ. Mỗi lần xem đầy đủ ghi nhật ký: mở chi tiết MCN, mở lịch sử tài khoản ngân hàng, xem ảnh CCCD (mỗi mặt một dòng), mở lệnh chi MCN ở Xử lý rút tiền. Bấm Kích hoạt không tính là một lượt xem; Danh sách MCN không ghi.
- Ảnh CCCD của MCN cá nhân có đủ số CCCD nên cũng chỉ người có quyền này mới xem hoặc tải được. Người không có quyền thấy tên tệp và câu "Cần quyền xem CCCD để xem hoặc tải" (QC MCN-19, 17/11). Hồ sơ KYB của MCN công ty và các hồ sơ khác: Xem bằng quyền xem MCN, Tải về bằng quyền tải hồ sơ MCN (D33).
- Tải tệp hồ sơ lên cần quyền sửa MCN (D33).
- Mỗi điều kiện đã đạt có nút **Xem**: thông tin đã nhập, file (nút Xem mở tệp ngay trên Admin; nút Tải về theo D33), ngày giờ và người cập nhật, lịch sử thay đổi.
- Cập nhật lần sau tạo bản mới; bản cũ vẫn trong lịch sử, không xóa.
- Sau khi kích hoạt, tab đổi tên thành **Hồ sơ pháp lý**, vẫn cập nhật được như trên, kể cả tài khoản ngân hàng (D29).

#### FR-004: Tài khoản ngân hàng của MCN

- Admin chọn ngân hàng, nhập số tài khoản và tên chủ tài khoản theo giấy tờ ngân hàng, bấm **Lưu**. Không có bước Kiểm tra: hệ thống không tra, không đối chiếu tên chủ tài khoản với AccessTrade (D29).
- Tài khoản đứng tên chính MCN; Admin tự đối chiếu với giấy tờ trước khi lưu.
- Số tài khoản chỉ nhận chữ số, ký tự khác tự bỏ. Tên chủ tài khoản tự viết hoa, bỏ dấu, chỉ giữ chữ cái và khoảng trắng. Kiểm ở cả web và API (QC 24/11, file nghiệm thu #2).
- Sửa được cả trước và sau kích hoạt: nút **Nhập tài khoản** khi chưa có, **Sửa tài khoản** khi đã có. Form sửa để trống, không điền sẵn số đã che. Mỗi lần lưu là một bản mới, bản cũ xem được ở lịch sử. Hộp nhập ghi: "Lưu là thay tài khoản hiện hành, bản cũ vẫn xem được ở lịch sử. Lệnh chi đã tạo giữ tài khoản lúc tạo lệnh." (D29, chị Huyền chốt 26/11).
- Điều kiện kích hoạt đạt khi có đủ ngân hàng, số tài khoản và tên chủ tài khoản.
- Đây là tài khoản AccessTrade chuyển tiền cho MCN ở đợt chi (FR-019).

#### FR-005: Kích hoạt MCN

- Nút **Kích hoạt** chỉ chạy khi đủ 5 điều kiện. Bấm khi còn thiếu: hiện danh sách điều kiện còn thiếu.
- Kích hoạt xong:
  - Trạng thái **Hoạt động**, ghi người và giờ kích hoạt.
  - Hệ thống tạo **dòng tài khoản MCN** gắn email đăng nhập với hồ sơ MCN (bảng quan hệ). Email đã có tài khoản (email đã xác thực) thì gắn luôn tài khoản đó; chưa có thì dòng tài khoản MCN chờ email đó.
  - Gửi email tới email đăng nhập: MCN đã được kích hoạt, hướng dẫn đăng nhập web Ambassador bằng Google với đúng email này.
- Dòng tài khoản MCN đang chờ được gắn user ở một trong hai lúc email đã xác thực xuất hiện trên tài khoản: tạo tài khoản mới bằng Google với email đó, hoặc xác thực email đó bằng OTP. Đăng nhập thường không kiểm (13/11, giảm truy vấn ở mỗi lần đăng nhập). Gắn xong, user thấy mục **Quản lý MCN**.
- Không có thao tác Tạm dừng, Chấm dứt MCN (D12).
- Không có thao tác đổi chủ/người vận hành MCN sau khi kích hoạt (D27).

#### FR-006: Admin xem thành viên

- Trang chi tiết MCN đang hoạt động có tab **Thành viên**, chia ba nhóm: **Đang hợp tác** (gồm Đang báo rời kèm ngày rời có hiệu lực), **Chờ ký phụ lục** (kèm hạn ký), **Đã kết thúc** (KOL/KOC rời, MCN chấm dứt, hết hạn phụ lục, Đã từ chối, Quá hạn ký, Hết hiệu lực; kèm lý do). Cột: KOL/KOC, Tỷ lệ phí quản lý, Ngày tham gia (nhóm Chờ ký: Ngày đồng ý), Trạng thái, Ghi chú.
- Ô **Thành viên** ở đầu trang và nhãn tab Thành viên hiện tổng số dòng của cả ba nhóm. Cột Thành viên ở Danh sách MCN (FR-001) là số đang hợp tác.
- Chỉ xem (D6).

### Nhóm B — MCN: mời và quản lý thành viên

#### FR-007: Menu MCN trên web

- Tài khoản MCN (FR-005) thấy **Quản lý MCN** trong menu avatar. User khác không thấy.
- Trang Quản lý MCN có menu trái: **Thành viên**, **Lời mời**, **Đối soát**, và nút **Mời KOL/KOC**.
- Chưa đăng nhập mà vào thẳng `/quan-ly-mcn` hoặc `/mcn-cua-toi` thì về trang chủ (QC 24/11, file nghiệm thu #7).
- Tài khoản MCN đăng nhập xong mà đang ở trang chủ thì được chuyển vào Quản lý MCN, mỗi phiên một lần.
- Tên thương hiệu trên các màn MCN và email MCN viết **ACCESSTRADE** (QC 24/11, file nghiệm thu #4).

#### FR-008: Tạo link mời

- Bấm **Mời KOL/KOC** → nhập tỷ lệ phí (số nguyên 0–100) → **Tạo link**.
- Hiện link `…/mcn/moi/<mã>` và nút **Sao chép**. MCN tự gửi qua kênh của mình.
- Tỷ lệ không phải số nguyên hoặc ngoài 0–100: báo lỗi, không tạo. Không tự làm tròn.
- Mỗi link một mã ngẫu nhiên, không đoán được, không lộ thông tin user.

#### FR-009: Mục Lời mời

- Bảng **Link mời**: Link, Tỷ lệ, Ngày tạo, Số người đã tham gia, Trạng thái (Đang dùng/Đã tắt), Sao chép, **Tắt link**.
- Tắt link: không ai mở link đó được nữa (hiện "Link mời đã ngừng"; người vận hành MCN mở link của chính MCN mình thì thấy câu riêng, xem FR-012). Không Đồng ý, không Từ chối qua link đã tắt được. Người đã đồng ý qua đúng link đó nhưng chưa ký vẫn ký tiếp hoặc từ chối được trong hạn. Thành viên đã vào không ảnh hưởng. Không bật lại (tạo link mới).
- Bảng **Người đã đồng ý**: người đã mở lời mời nhưng không thành thành viên. Tên, Tỷ lệ, Ngày đồng ý, Trạng thái (Đã từ chối, Quá hạn ký, Hết hiệu lực — đã ký với MCN khác). Dưới tiêu đề ghi: "Người đã bấm đồng ý nhưng chưa trở thành thành viên: đã từ chối, quá hạn ký hoặc đã ký với MCN khác. Người ký xong có ở tab Thành viên." Bảng trống thì ghi "Chưa có ai từ chối hoặc quá hạn ký." (chị Huyền chốt 26/11, file nghiệm thu #8).
- Người đang Chờ ký phụ lục **không** hiện ở bảng này, kể cả khi gọi API trực tiếp (D30). MCN nhận thông báo khi có người đồng ý; ký xong thì người đó có trong mục Thành viên.

#### FR-010: Mục Thành viên (MCN)

- Hai nhóm chuyển bằng nút: **Đang hợp tác (n)** và **Đã kết thúc (n)**. Không có nhóm Chờ ký (D30).
- Đang hợp tác: Tên, Tỷ lệ, Ngày tham gia, Trạng thái, Ghi chú (ngày rời có hiệu lực; trống thì hiện "-", file nghiệm thu #12), nút **Chấm dứt**.
- MCN chỉ thấy thông tin thành viên trong thời gian hợp tác. Đã kết thúc: chỉ còn tên, ngày tham gia, ngày kết thúc, trạng thái và lý do (KOL/KOC rời, MCN chấm dứt, hết hạn phụ lục; kèm lý do người rời hoặc MCN đã nhập). Không ảnh, không thao tác. Người đã từ chối, quá hạn ký, hết hiệu lực chưa từng là thành viên nên chỉ ở bảng Người đã đồng ý (FR-009). Ngoại lệ: số liệu đối soát các kỳ đã hợp tác vẫn xem được ở mục Đối soát (D22).

#### FR-011: MCN chấm dứt thành viên

- Xác nhận bằng modal, có ô **Lý do** (không bắt buộc). Hiệu lực ngay, kể cả khi thành viên đang báo rời. Modal ghi: "Sau khi chấm dứt, bạn chỉ còn xem được số đối soát các kỳ đã hợp tác." (D22).
- Thành viên nhận thông báo. Chấm dứt có hiệu lực ngay. Khoản phát sinh từ ngày chấm dứt không bị trích phí (D20, FR-016).

### Nhóm C — KOL/KOC: tham gia và rời MCN

#### FR-012: Mở link mời

| Tình huống | Hệ thống |
|---|---|
| Chưa đăng nhập | Hiện trang lời mời rút gọn (tên MCN, tỷ lệ) và nút Đăng nhập. Giữ mã mời qua bước đăng nhập/đăng ký; xong quay lại đúng trang lời mời |
| Đã đăng nhập, không thuộc MCN nào | Hiện lời mời đầy đủ |
| Đang thuộc MCN khác (kể cả đang báo rời) | Báo "Bạn đang thuộc MCN khác. Rời MCN hiện tại trước khi nhận lời mời mới" (D11) |
| Đã là thành viên của chính MCN này | Chuyển sang MCN của tôi |
| Tài khoản đang là tài khoản MCN, link của chính MCN đó, tỷ lệ 100% | Hiện lời mời đầy đủ, được đồng ý (tài khoản nhà, D14) |
| Tài khoản đang là tài khoản MCN, link dưới 100% hoặc link của MCN khác | Báo không áp dụng |
| Link đã tắt hoặc MCN không hoạt động | "Link mời đã ngừng" |
| Người vận hành MCN mở link đã tắt của chính MCN mình (kể cả khi đã là tài khoản nhà của MCN đó) | "Link mời đã tắt. Hãy tạo link mới để mời lại." Không lộ tên MCN, tỷ lệ (file nghiệm thu #5, 25/11) |
| Đã đồng ý lời mời của MCN khác, chưa ký | Vẫn hiện lời mời đầy đủ, được đồng ý (D18) |
| Đã đồng ý chính lời mời này, chưa ký | Chuyển sang bước ký phụ lục |

#### FR-013: Đồng ý lời mời

- Lời mời ghi: tên MCN, tỷ lệ phí, thời hạn phụ lục 12 tháng, "Rời có hiệu lực từ 00:00, 15 ngày sau ngày báo", ví dụ với thu nhập 3.000.000đ (phí, phần còn lại), câu "Thuế TNCN tính khi ACCESSTRADE chi tiền, như hiện nay". Tài khoản nhà của MCN công ty thấy câu "Thu nhập chuyển về MCN. MCN công ty không bị khấu trừ thuế TNCN." (QC MCN-72, 16/11).
- Phải tick **Tôi đã hiểu** mới bấm **Đồng ý** được. Có nút **Từ chối**, kèm ô **Lý do** (không bắt buộc); MCN nhận một thông báo, bấm nhiều lần không tạo thêm. Từ chối xong ở lại trang lời mời, hiện "Bạn đã từ chối lời mời. MCN đã nhận được thông báo.", không chuyển về trang chủ.
- Ví dụ ghi rõ số KOL/KOC còn nhận, kể cả tỷ lệ 0% và 100%.
- Đồng ý: tạo dòng quan hệ trạng thái **Chờ ký phụ lục**, hạn ký 7 ngày tính tới đúng giờ đồng ý; màn ký và MCN của tôi ghi "Hạn ký đến hh:mm dd/mm" (giờ Việt Nam). Ghi tỷ lệ của link vào dòng này (tắt link sau đó không đổi tỷ lệ). Chờ ký **chưa phải thành viên** (D18).

#### FR-014: Ký phụ lục

- Chưa eKYC hoặc chưa ký hợp đồng gốc `B2C_AMBASSADOR`: chặn, dẫn sang trang **Hợp đồng điện tử** có sẵn. Làm xong quay lại ký tiếp (D23). Chưa đủ doanh thu 50.000đ vẫn ký được hợp đồng gốc khi đang Chờ ký với MCN (D31).
- Màn ký phụ lục **không có nút Từ chối** (QC 17/11). Không ký thì quá 7 ngày chuyển Quá hạn ký.
- Màn ký hiện **Thông báo xử lý dữ liệu cá nhân** (tải về được, A5). Tick riêng **Đồng ý chia sẻ dữ liệu cho MCN** (bắt buộc, lưu thời điểm).
- Ký trên hợp đồng điện tử (loại phụ lục mới, Q4). Ký xong: thành viên **Đang hợp tác**. Ngày bắt đầu tính phí = **ngày kích hoạt** (ngày hệ thống ghi nhận phụ lục đã ký), tính từ 00:00 ngày đó; ngày kết thúc phụ lục = 00:00 giờ Việt Nam của ngày kích hoạt + 12 tháng (chốt 11/11).
- Ký xong một MCN: các lời mời Chờ ký của MCN khác chuyển **Hết hiệu lực**, không ký được nữa, kể cả khi kết quả ký về muộn (D18).
- Quá 7 ngày chưa ký: **Quá hạn ký** ngay khi hết hạn (không chờ job định kỳ): không còn ở danh sách Chờ ký, không ký được, phải mở lại link để đồng ý lại.
- Hợp đồng điện tử không báo kết quả ký về hệ thống, nên hệ thống tự hỏi trạng thái định kỳ, giãn dần theo tuổi phụ lục. Màn ký có nút **Kiểm tra trạng thái ký** để người vừa ký xong cho hệ thống hỏi ngay; bấm xong khoá 10 giây (anh Vĩnh, group dự án 16/11).

#### FR-015: MCN của tôi, báo rời

- Avatar › **MCN của tôi**: hiện cho người có lời mời đang Chờ ký (một hoặc nhiều MCN) hoặc đang là thành viên. Người không có quan hệ nào không thấy mục này.
- Nội dung: tên MCN, tỷ lệ, ngày tham gia, ngày kết thúc phụ lục, trạng thái.
- **Báo rời**: ô **Lý do** (không bắt buộc). Ngày rời có hiệu lực = ngày báo + 15 ngày, 00:00. Phí vẫn trích đến ngày đó.
- **Rút lại báo rời**: được trước ngày rời có hiệu lực. Đã tới ngày đó thì báo "Đã tới ngày rời có hiệu lực, không rút lại được."
- Đến ngày rời có hiệu lực: **Đã kết thúc**, lý do "KOL/KOC rời". MCN nhận thông báo.
- Hết 12 tháng phụ lục: **Đã kết thúc**, lý do "Hết hạn phụ lục", ngừng trích phí (D19). Phụ lục hết hạn trước ngày rời có hiệu lực thì kết thúc theo hết hạn.

### Nhóm D — Đối soát và chi trả

#### FR-016: Tính phí quản lý trong kỳ đối soát

- Lúc **Lấy danh sách** (kỳ chuyển sang Đã xử lý), hệ thống tính phí cho từng khoản theo **ngày phát sinh** của khoản đó (D20): chỉ trích khi tại ngày phát sinh người đó là thành viên (Đang hợp tác hoặc Đang báo rời chưa tới ngày rời) của một MCN **Hoạt động**. Ghi lại MCN, tỷ lệ của khoản.
- Thưởng view: mỗi ngày có view là một khoản, ngày phát sinh là ngày có view (không phải ngày hệ thống ghi nhận).
- Một dòng thưởng nội dung gồm nhiều ngày: phần nào phát sinh lúc thuộc MCN nào thì MCN đó được trích (D24).
- Phí của một thành viên trong kỳ = làm tròn(tổng số tiền các khoản thuộc MCN của thành viên đó × tỷ lệ / 100) tới đồng. Làm tròn một lần trên tổng, không làm tròn từng khoản (chốt 11/11), để KOL/KOC, MCN và Kế toán tự tính tay ra đúng số.
- Chỉ trích khoản thuộc chiến dịch có ngày bắt đầu từ 00:00 ngày 01/12/2026 (giờ Việt Nam). Chiến dịch bắt đầu trước mốc này không bị trích phí, kể cả khi người đó đã là thành viên. Ngày chạy kỳ đối soát không so với mốc, nên kỳ chạy sớm hay muộn thì phí như nhau. Muốn dời mốc thì sửa code rồi deploy (chốt 12/11).
- MCN áp dụng cho **tất cả partner/ADV**: kỳ đối soát của mọi partner đều xét phí cho khoản thưởng đủ điều kiện về chiến dịch và thời gian thành viên nêu trên (D26, Q6).
- Người không thuộc MCN: không có phí, như hiện nay.

#### FR-017: Tab Người nhận

Trang chi tiết kỳ đối soát có thêm tab **Người nhận** (sau khi Lấy danh sách):

| Cột | Ghi chú |
|---|---|
| Người nhận | Tên KOL/KOC hoặc tên MCN |
| Loại | Không có MCN / Có MCN / MCN |
| MCN | Tên MCN của thành viên. Rời MCN này vào MCN khác trong cùng kỳ thì hiện đủ các MCN theo thứ tự thời gian (D24) |
| Tỷ lệ | Tỷ lệ của từng MCN ở cột MCN |
| Tổng hoa hồng | G |
| Phí quản lý | |
| Cộng vào số dư | KOL/KOC: G − phí. MCN: tổng phí của các thành viên trong kỳ |
| Trạng thái | Như trạng thái khoản hiện nay |

- Lọc theo Loại. Mỗi MCN một dòng, các dòng MCN lên đầu bảng; bấm **Xem** ở dòng MCN thấy phí của từng thành viên. Số thứ tự đánh liên tục qua các trang (QC 23/11).
- Modal Duyệt tất cả ghi thêm số MCN nhận phí trong kỳ.

#### FR-018: Cộng vào số dư khi duyệt

- Khi duyệt, với mỗi khoản có phí:
  - KOL/KOC: số dư tăng G − phí (sổ dòng tiền ghi đủ: khoản thưởng và khoản trừ phí MCN).
  - MCN: số dư MCN (hồ sơ MCN, không phải user đăng nhập) tăng phí, ghi rõ từ thành viên nào, kỳ nào, chiến dịch nào.
- Kỳ chạy lại sau lỗi không được cộng hai lần.
- KOL/KOC và MCN nhận thông báo như thông báo đối soát hiện nay. Với thành viên MCN, số tiền trong thông báo là số thật cộng vào số dư (sau phí MCN).
- Phí luôn có nơi nhận vì số dư thuộc hồ sơ MCN, không thuộc user đăng nhập.
- Hoa hồng giới thiệu tính trên G của người được giới thiệu (trước phí MCN), như trước khi có MCN.

#### FR-019: Chi trả

- Đợt chi ở Xử lý rút tiền giữ nguyên thao tác. ADV còn kỳ đối soát Đang chạy hoặc Duyệt lỗi thì chưa Lấy danh sách đợt chi, áp dụng cho mọi ADV (D8).
- MCN đủ điều kiện khi: MCN Hoạt động, có tài khoản ngân hàng (D29), số dư MCN từ mức tối thiểu của đợt. **Không** yêu cầu eKYC, hợp đồng điện tử `B2C_AMBASSADOR` hay liên kết AccessTrade.
- Mỗi MCN một lệnh chi trong đợt, chi theo từng chiến dịch: mỗi chiến dịch có số dư là một dòng trong lệnh và trong file ngân hàng (họp 10/11).
- Đợt chi có mức tối đa (Max): MCN được chọn khi số dư từ mức tối thiểu. Chi lần lượt các chiến dịch theo ngày bắt đầu tới khi đủ Max; chiến dịch làm vượt Max chỉ chi phần còn thiếu, phần còn lại chờ đợt sau. KOL/KOC giữ cách hiện nay.
- Lệnh chi của MCN: tài khoản nhận là tài khoản hiện hành ở hồ sơ pháp lý lúc tạo lệnh (FR-004), sửa tài khoản sau đó không đổi lệnh đã tạo; mã định danh (MST hoặc CCCD) lấy từ hồ sơ MCN. Trên màn Xử lý rút tiền, số tài khoản, CCCD, SĐT của MCN che theo D32.
- Thuế: MCN công ty không khấu trừ thuế TNCN. MCN cá nhân khấu trừ 10% khi tổng lệnh của MCN trong đợt từ 5.000.000đ, xét trên cả lệnh chứ không từng chiến dịch (họp 10/11). Chứng từ khấu trừ cấp ngoài hệ thống.
- Bảng chi tiết đợt chi và file xuất ngân hàng có thêm cột Loại (KOL/KOC / MCN).
- KOL/KOC: không đổi. Khấu trừ 10% khi số chi trong đợt từ 5.000.000đ (D21). Số dư KOL/KOC đã là phần sau phí MCN.

#### FR-020: MCN xem đối soát

- Quản lý MCN › **Đối soát**: các kỳ **Đã hoàn thành** có thành viên của MCN; kỳ Duyệt lỗi chưa hiện, Duyệt lại xong thì hiện (QC 23/11). Cột: Kỳ, Ngày cộng (ngày kỳ hoàn thành), Số thành viên, Tổng hoa hồng, Phí quản lý. Tổng hoa hồng ở màn này chỉ gồm các khoản bị trích phí, tức thu nhập trong thời gian hợp tác. Thu nhập ngoài thời gian đó MCN không được thấy (NFR-003).
- **Xem** một kỳ: từng thành viên với Tỷ lệ, Tổng hoa hồng, Phí quản lý. Thành viên đã rời vẫn hiện trong các kỳ đã hợp tác (D22).
- Chỉ xem, không có nút xác nhận.

#### FR-021: KOL/KOC xem đối soát

- Avatar › **Đối soát** (mọi creator): các kỳ **Đã hoàn thành** có khoản của mình. Cột: Kỳ, Ngày cộng (ngày kỳ hoàn thành), Tổng hoa hồng, Phí quản lý (— nếu không thuộc MCN), Cộng vào số dư.
- **Xem** một kỳ: Tổng hoa hồng; mỗi MCN một dòng "Phí quản lý {MCN}, {tỷ lệ}%" kèm số phí (rời MCN này vào MCN khác trong cùng kỳ thì có hai dòng, D24); Cộng vào số dư. Dưới đó là bảng **Các khoản trong kỳ**: Loại khoản (Thưởng nội dung, Thưởng mốc, Thưởng thêm), Chiến dịch, Ngày phát sinh, Số tiền, Phí quản lý.
- Trang cá nhân › **Doanh thu của bạn** (theo từng chiến dịch): người có phí MCN thấy thêm "Phí quản lý MCN đã trừ" và "Đã cộng vào số dư", kèm ghi chú các số còn lại là trước phí và link sang Đối soát (QC 23/11).
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

- Thông báo "Lời mời được đồng ý" dẫn tới trang Quản lý MCN (người Chờ ký không hiện ở mục Lời mời, D30). Thông báo "Lời mời bị từ chối" dẫn tới mục Lời mời.
- Tài khoản nhà (người vận hành tự tham gia chính MCN của mình, D14) không nhận các thông báo phía MCN do chính mình gây ra: đồng ý, từ chối, thành viên mới, báo rời, rút lại, kết thúc (QC 24/11, file nghiệm thu #13).

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
- **NFR-003 Riêng tư:** MCN không tra cứu được user. MCN chỉ thấy dữ liệu thành viên của mình trong thời gian hợp tác; số liệu đối soát các kỳ đã hợp tác vẫn xem được sau khi rời (D22). Link mời chỉ hiện tên và loại MCN (Công ty / Cá nhân, để câu thuế ở FR-013 đúng), không lộ thông tin khác. Lời mời Hết hiệu lực không cho MCN biết KOL/KOC đã vào MCN nào.
- **NFR-004 Lưu vết:** mọi thay đổi hồ sơ pháp lý, trạng thái MCN, trạng thái thành viên đều có người, giờ, lý do. Lý do Từ chối, Chấm dứt, Báo rời lưu vào lịch sử quan hệ, hiện trong thông báo gửi bên kia và ở tab Thành viên của Admin.
- **NFR-005 Ngôn ngữ:** tiếng Việt.

---

## 7. Assumptions và phụ thuộc

| # | Phụ thuộc | Bên |
|---|---|---|
| A1 | ~~Loại hợp đồng phụ lục chỉ định thanh toán trên dịch vụ econtract~~ Đã cấp mã `B2C_AMBASSADOR_ADDENDUM` (26/11). Phase 1 không truyền trường động (tên MCN, tỷ lệ, thời hạn) vào phụ lục (Q4) | AccessTrade core |
| A2 | ~~Mẫu email "MCN được kích hoạt" (template code)~~ Đã cấp (26/11) | AccessTrade |
| A3 | ~~Tra tên chủ tài khoản ngân hàng cho tài khoản của MCN~~ Không cần: phase 1 không tra tên chủ tài khoản (D29) | — |
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
| Đổi chủ/người vận hành MCN, sửa thông tin hồ sơ MCN đã Hoạt động | Không làm (D27). Hồ sơ Chờ kích hoạt sửa được (FR-002) |
| Tra tên chủ tài khoản ngân hàng MCN | Không làm. Admin nhập theo giấy tờ, sửa được khi cần (D29, Q15) |
| Giao diện MCN trên các app partner (parasola, …) | Phase 1 triển khai giao diện tại app Ambassador và Admin; phạm vi nghiệp vụ và tính phí MCN vẫn áp dụng cho tất cả partner/ADV (D26) |

---

## 9. Open Questions

| # | Câu hỏi | Đề xuất |
|---|---|---|
| Q1 | ~~Ngưỡng thuế TNCN~~ | **Đã chốt:** 5.000.000đ, tính trên số chi sau phí MCN (D21) |
| Q2 | ~~Các trường form tạo MCN~~ | **Đã chốt:** theo bảng FR-002 (bản mẫu 09/11), đã làm và QC nghiệm thu |
| Q3 | ~~Định dạng, dung lượng file hồ sơ pháp lý~~ | **Đã chốt:** PDF, JPG, PNG, tối đa 10MB mỗi tệp; CCCD MCN cá nhân hai tệp mặt trước, mặt sau (D28, chị Huyền 17/11) |
| Q4 | ~~Loại hợp đồng phụ lục trên econtract: AccessTrade core cấp mã loại và mẫu khi nào?~~ | **Đã chốt:** mã `B2C_AMBASSADOR_ADDENDUM` (chị Huyền báo 26/11), tạm dùng chung cho MCN công ty và cá nhân tới khi AT tách mẫu. Phase 1 không truyền tên MCN, tỷ lệ phí vào phụ lục; tỷ lệ lưu ở hệ thống (A1) |
| Q5 | ~~Thời điểm xét tư cách thành viên~~ | **Đã chốt:** theo ngày phát sinh từng khoản; không trích khoản trước ngày ký (D20) |
| Q6 | ~~Phạm vi MCN theo partner~~ | **Đã chốt:** MCN áp dụng cho tất cả partner/ADV; thu nhập từ chiến dịch của mọi partner được xét phí khi đủ điều kiện FR-016 (D26, Định xác nhận trong comment PR #41 ngày 13/11) |
| Q7 | ~~Hết 12 tháng phụ lục~~ | **Đã chốt:** tự kết thúc (D19) |
| Q8 | ~~Thu nhập từ nội dung của chính tài khoản MCN công ty: khi chi, cả số dư được miễn khấu trừ TNCN?~~ | **Đã chốt:** thu nhập nội dung của tài khoản nhà vào số dư MCN, chi và tính thuế theo loại MCN: công ty không khấu trừ, cá nhân 10% theo ngưỡng (D14, họp 10/11). Legal rà thêm sau, không chặn phase 1 |
| Q9 | ~~Thuế TNCN của MCN cá nhân~~ | **Đã chốt:** 10%, ngưỡng 5.000.000đ trên cả lệnh của MCN trong đợt; chứng từ ngoài hệ thống (họp 10/11, D9, FR-019) |
| Q10 | ~~MCN có thấy tên KOL/KOC đang Chờ ký không?~~ | **Chốt lại 16/11:** không. MCN chỉ nhận thông báo khi có người đồng ý; ký xong mới thấy ở mục Thành viên (D30). Chốt "có, chỉ tên" ở bản 1.1 không còn dùng |
| Q11 | ~~Thưởng mốc đạt sau ngày ký nhưng nhờ video đăng trước ngày ký; thưởng thêm tạo sau ngày ký để bù khoảng trước ngày ký: có trích phí MCN không?~~ | **Đã chốt (chị Huyền, 26/11):** theo ngày phát sinh ở mục 0. Thưởng mốc theo số bài tính theo ngày nộp bài chạm mốc: nộp trước ngày vào MCN thì không trích dù mốc ghi nhận sau; nộp khi còn là thành viên thì vẫn trích dù mốc ghi nhận sau ngày rời. Thưởng thêm tính theo ngày Admin tạo |
| Q12 | ~~MCN đã có tài khoản creator có dùng chung tài khoản đó không?~~ | **Đã chốt:** dùng chung. MCN cá nhân và creator là một tài khoản, vẫn đăng bài như creator (nguyên tắc 2, D14). Chặn tài khoản đang là thành viên hoặc đang Chờ ký với MCN khác; quan hệ với chính MCN này chỉ được phép ở tỷ lệ 100% (FR-002, xem mục 9.1) |
| Q13 | ~~Lý do Từ chối, Chấm dứt, Báo rời có hiện cho bên kia không?~~ | **Đã chốt:** có, hiện trong thông báo gửi bên kia; Admin thấy ở tab Thành viên |
| Q14 | ~~Nhập sai hồ sơ MCN thì tạo hồ sơ mới (D27), nhưng MST/CCCD và email đăng nhập không được trùng MCN khác (FR-002), kể cả hồ sơ Chờ kích hoạt tạo sai. Tạo lại với đúng MST/CCCD hoặc email sẽ bị chặn. Xử lý thế nào?~~ | **Đã chốt (anh Định, 27/11):** hồ sơ Chờ kích hoạt sửa được thông tin (D27, FR-002), không cần tạo lại |
| Q15 | ~~Lấy thông tin ngân hàng của MCN qua AT-Core (file nghiệm thu #6): AT-Core có API tra tên chủ tài khoản (`/uaa-service/api/v1.1/user/payment-info/account-name`, web Ambassador đang dùng khi thêm ngân hàng), nhưng đang gửi kèm `user_id` của người đăng nhập. Admin gọi cho MCN công ty (không có user) được không?~~ | **Đã chốt:** phase 1 Admin nhập tay theo giấy tờ (D29, đã làm). Tra qua AT-Core để phase sau |

---

### 9.1 Các điểm cần xác nhận theo review PR #41

Các điểm dưới đây được ghi riêng để phân biệt yêu cầu đã chốt và thay đổi thiết kế đang chờ xác nhận:

| Mục | Nội dung cần xác nhận |
|---|---|
| ~~D8 — Trạng thái kỳ~~ | **Đã chốt:** Duyệt lỗi, Duyệt lại, chặn Lấy danh sách đợt chi khi còn kỳ Đang chạy hoặc Duyệt lỗi (anh Vĩnh, review PR #42 ngày 12/11 và group dự án 14/11). Đã đồng bộ D8, thuật ngữ, nguyên tắc 1, FR-019 ở bản 1.10 |
| ~~D18 — Mở ký phụ lục~~ | **Đã chốt (anh Định, 27/11):** vẫn được Chờ ký nhiều MCN, chỉ mở ký một phụ lục tại một thời điểm (D18) |
| ~~FR-002 — Điều kiện email~~ | **Đã chốt:** chặn tài khoản đang là thành viên hoặc đang Chờ ký với MCN khác, kèm câu báo lỗi ở FR-002; đã làm và QC nghiệm thu |

Đường ghi tiền mới đã làm, thay đường cũ cho mọi partner, kể cả kỳ không có MCN. Không release riêng: lên cùng bản MCN, kích hoạt trích phí từ 01/12 (anh Vĩnh chốt trong group dự án ngày 14/11). Trước khi lên, kiểm hồi quy số tiền và thuế của kỳ không có MCN so với cách ghi cũ.

Điều chỉnh phí giữ đúng D7: chỉ bằng Thưởng thêm. Phase 1 không có script hay nút điều chỉnh tiền MCN (anh Vĩnh, group dự án 14/11).

## 10. Revision History

| Version | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-11-04 | Bản đầu, theo scope chốt 03/11/2026 và bản mẫu giao diện v47. Vai MCN và thành viên dùng bảng quan hệ, không dùng loại tài khoản |
| 1.1 | 2026-11-09 | Thêm D17–D24: MCN cá nhân, tỷ lệ 0–100%, Chờ ký chưa phải thành viên và được Chờ ký nhiều MCN, hết 12 tháng tự kết thúc, trích phí theo ngày phát sinh, thuế 5.000.000đ trên số sau phí, MCN xem kỳ cũ sau rời, eKYC/hợp đồng gốc ở trang có sẵn, đổi MCN trong kỳ. Đóng Q1, Q5, Q7; thêm Q9–Q13, đóng Q10, Q12, Q13. Đồng bộ với bản mẫu 09/11: file PDF/JPG/PNG, ô lý do khi Từ chối/Chấm dứt/Báo rời, Thông báo xử lý dữ liệu cá nhân ở màn ký (A5), thông báo khi KOL/KOC từ chối |
| 1.2 | 2026-11-11 | Chốt 11/11: phí tính từ ngày kích hoạt thành viên (FR-014, D20); làm tròn một lần trên tổng phí của mỗi thành viên trong kỳ thay vì từng khoản (FR-016) |
| 1.3 | 2026-11-13 | Chốt 12/11: chỉ trích phí khoản thuộc chiến dịch bắt đầu từ 00:00 01/12/2026 giờ Việt Nam (FR-016) |
| 1.4 | 2026-11-13 | Theo review của anh Vĩnh (PR #41, 12/11): sửa nguyên tắc 1; D9 và FR-019 thuế MCN cá nhân 10% trên cả lệnh, đóng Q9; D14 tài khoản nhà 100%, đóng Q8; FR-012 tài khoản MCN được nhận link 100% của chính MCN; FR-018 và thuật ngữ: số dư thuộc hồ sơ MCN; FR-019 lệnh MCN chi theo chiến dịch; thêm D25 mốc trích phí; sửa FR-011 theo D20. D7, D8, D18, Q6 chờ PO |
| 1.5 | 2026-11-13 | Xác nhận MCN áp dụng cho tất cả partner/ADV: cập nhật phạm vi nghiệp vụ, thêm D26, sửa FR-016 và đóng Q6; tách rõ phạm vi giao diện phase 1. FR-002/Q12 đồng bộ điều kiện email Chờ ký với MCN khác theo INV-03b, bổ sung câu báo lỗi và kiểm tra lại khi kích hoạt/đổi người vận hành. Mục 9.1 ghi riêng D7, D8, D18 và điều kiện email cần review; ghi kế hoạch đang làm chung branch, tách PR đường ghi tiền sau |
| 1.6 | 2026-11-15 | Theo review PR #41 ngày 14/11: viết lại D24 (không có luồng đổi MCN); ghi người và nơi xác nhận cho D23, D26, Q6. Theo chat group 14/11: đường ghi tiền lên cùng bản MCN, không release riêng; bỏ dòng D7 khỏi mục 9.1, điều chỉnh phí chỉ bằng Thưởng thêm |
| 1.7 | 2026-11-16 | Thêm D27 (anh Vĩnh chốt 16/11): phase 1 không cho đổi chủ/người vận hành MCN. FR-002: email đăng nhập chỉ sửa khi Chờ kích hoạt, bỏ kiểm tra khi đổi tài khoản vận hành; FR-005 ghi không có thao tác đổi; FR-018 và thuật ngữ bỏ câu "đổi người vận hành thì tiền vẫn ở MCN"; mục 8 thêm dòng ngoài phạm vi |
| 1.8 | 2026-11-16 | Sửa D27, FR-002, mục 8: Admin không có chức năng sửa thông tin hồ sơ MCN ở bất kỳ trạng thái nào (bản 1.7 ghi nhầm là sửa được email khi Chờ kích hoạt); nhập sai thì tạo mới. Thêm Q14: tạo lại bị chặn vì trùng MST/CCCD, email với hồ sơ tạo sai |
| 1.9 | 2026-11-17 | Theo chốt 16–17/11 qua Sheet test QC (chị Huyền) và group dự án 16/11 (anh Vĩnh): thêm D28 (file tối đa 10MB, CCCD hai tệp), D29 (tài khoản ngân hàng nhập một lần, không tra tên; bỏ A3), D30 (MCN không thấy người Chờ ký; chốt lại Q10), D31 (đang Chờ ký với MCN được ký hợp đồng gốc khi chưa đủ 50.000đ). Sửa D27, FR-001 (vị trí menu, Số thành viên), FR-002, FR-003 (che số CCCD, số TK; ảnh CCCD chỉ người có quyền xem CCCD tải được), FR-004, FR-005 (lúc gắn tài khoản MCN), FR-006 (ba nhóm, ô Thành viên là tổng), FR-009, FR-013 (màn sau khi từ chối), FR-014 (bỏ nút Từ chối ở màn ký, nút Kiểm tra trạng thái ký), FR-019, mục 8; đóng Q3 |
| 1.10 | 2026-11-26 | Theo file nghiệm thu và chốt của chị Huyền 23–26/11, đồng bộ với code: D8 Duyệt lỗi/Duyệt lại đã chốt (thuật ngữ, nguyên tắc 1, FR-019, mục 9.1); D29 tài khoản ngân hàng sửa được, giữ lịch sử, quy tắc nhập (FR-003, FR-004, D27, mục 8); thêm D32 che dữ liệu MCN, D33 tách quyền Xem/Tải hồ sơ; G không gồm nhiệm vụ; FR-007 chưa đăng nhập về trang chủ, ACCESSTRADE; FR-009 câu giải thích Người đã đồng ý, chặn từ chối qua link tắt; FR-010 nhóm Đã kết thúc, Ghi chú "-"; FR-011 câu modal; FR-012 người vận hành mở link đã tắt; FR-013 câu thuế tài khoản nhà công ty, hạn ký có giờ; FR-014 kết thúc phụ lục 00:00, quá hạn ký ngay; FR-015 rút lại sau ngày rời; FR-017 nhiều MCN, dòng MCN lên đầu; FR-018 thông báo số sau phí; FR-020, FR-021 chỉ kỳ Đã hoàn thành, chi tiết khoản, Doanh thu của bạn; FR-022 link thông báo, ngoại lệ tài khoản nhà; A2 đã cấp; thêm Q15; mục 0 ngày phát sinh của thưởng mốc theo số bài là ngày nộp bài chạm mốc, đóng Q11; FR-009 câu khi bảng Người đã đồng ý trống; Q4 mã phụ lục `B2C_AMBASSADOR_ADDENDUM`; bổ sung theo code 27/11: Tài khoản nhà gồm CCCD trùng MCN cá nhân, cột Tổng hoa hồng phía MCN, Max ở đợt chi MCN (FR-019), hoa hồng giới thiệu tính trên G (FR-018), NFR-003 cho hiện loại MCN; đóng Q2, Q4, Q15 và dòng FR-002 ở mục 9.1 (đã làm, QC nghiệm thu); A1 đã cấp mã; FR-001 và Personas ghi theo quyền thay vì vai `admin`; D27, FR-002, mục 8: hồ sơ Chờ kích hoạt sửa được thông tin, đóng Q14 (anh Định chốt 27/11); D18 chỉ mở ký một phụ lục một lúc, đóng dòng D18 ở mục 9.1 |
