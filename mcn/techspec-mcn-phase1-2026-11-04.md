# Technical Specification: MCN trên KOC Ambassador — Phase 1

| Mục | Giá trị |
|---|---|
| Project | KOC Ambassador — module MCN (Multi-Channel Network) |
| Date | 2026-11-11 |
| Author | Nguyễn Đăng Định |
| Reviewer | Thành Trung, Vinh Nguyễn |
| Version | 2.1 |
| Status | Draft — chờ review kiến trúc. v2.1 cập nhật theo họp 10/11 (§16) |
| PRD | [prd-mcn-phase1-2026-11-04.md](./prd-mcn-phase1-2026-11-04.md) (v1.1 ở PR #41, nhánh [`docs/mcn-phase1-prd-decisions-261109`](https://github.com/viewboost/accesstrade-docs/blob/docs/mcn-phase1-prd-decisions-261109/mcn/prd-mcn-phase1-2026-11-04.md)). Bản trên `main` là v1.0, chưa có D17–D24, Q8–Q13; cần merge PR #41 trước hoặc cùng PR này |
| Repo | `ambassador/`: `backend/` (Go, module `viewboost`, MongoDB replica set), `frontend/` (Umi 3 + dva), `admin/` (Umi + antd) |
| Nhánh code | `feat/mcn-phase1` (head `82edb83c7`) |

Đường dẫn code tính từ gốc repo `ambassador/`, số dòng đọc ngày 2026-11-10 trên `feat/mcn-phase1`. Các mã viết tắt (D, Q, FR, SD, BA, OQ, ADR, G, NG, INV, R, E1–E4, phase) giải thích ở §0.1.

## Tóm tắt cho người review

### Vấn đề

Hiện tại một user vừa là người đăng nhập, vừa có số dư, vừa nhận tiền, vừa chịu thuế. Bản v1.0 cộng phí MCN vào số dư của tài khoản vận hành MCN, nên tiền của MCN nằm trong số dư của một cá nhân. Hậu quả: đổi người vận hành thì tiền vẫn nằm ở người cũ. Tài khoản đó bị khóa thì MCN không được chi. Thu nhập creator của người đó được miễn thuế theo MCN (§2.7).

### Cách làm

1. MCN là một bản ghi riêng (`mcns`), không phải user. User chỉ được gắn quyền vận hành MCN, qua bảng `mcn-accounts`.
2. Tiền của MCN ghi ở bảng riêng `mcn-cash-flows`, chi bằng lệnh riêng `mcn-payouts`. Tiền creator vẫn ở `cash-flows` như cũ.
3. Người đứng MCN muốn làm creator thì tham gia chính MCN của mình với tỷ lệ 100%. Từ ngày ký phụ lục, thu nhập nội dung ở chiến dịch bắt đầu từ mốc áp dụng chuyển vào số dư MCN.
4. Phí chỉ tính cho chiến dịch bắt đầu từ 01/12/2026, theo ngày phát sinh của từng reward, trong thời gian KOL/KOC là thành viên.
5. Duyệt đối soát ghi tiền trong transaction. Chạy lại không cộng trùng. Lỗi giữa chừng thì báo để Duyệt lại.
6. MCN được chi theo từng chiến dịch: mỗi chiến dịch một lệnh. Với MCN cá nhân, ngưỡng 5.000.000 và thuế 10% xét trên tổng các lệnh của MCN đó trong cùng đợt chi (`groupBase`), không xét từng lệnh (chờ OQ-01). MCN công ty không bị khấu trừ.

Ví dụ: K thuộc MCN A, tỷ lệ 15%, có thưởng 3.000.000. K nhận 2.550.000, A nhận 450.000.

### So với các bản trước

So với v1.0 (04/11):
- Phí không cộng vào số dư của tài khoản vận hành. MCN có bảng tiền và lệnh chi riêng.
- Số dư KOL/KOC ghi hai dòng (thưởng, trừ phí) thay vì một dòng đã trừ.
- Duyệt và Chuyển tiền của creator chạy trong transaction, bật theo cờ partner `LedgerV2`. Creator không thuộc MCN có số tiền và thuế như hiện nay (§11.1, G-6).

So với v2.0 (10/11), theo họp 10/11:
- Người đứng MCN làm creator: tham gia chính MCN với tỷ lệ 100% thay vì hai lệnh chi riêng (ADR-12).
- Thêm mốc chiến dịch (ADR-13) và lệnh chi MCN theo chiến dịch (ADR-14).
- Phase 1 không chặn và không có màn hình riêng cho việc rời hoặc đổi MCN giữa chiến dịch. Nếu xảy ra, phí chia theo số ngày là thành viên (`FeeWindow`, §7.1). Đây là đề xuất, chờ PO chốt ở OQ-14. Luồng riêng để phase 2 (NG-9).

### Còn chờ chốt

- OQ-01 (Kế toán): thuế MCN cá nhân có khấu trừ 10% như KOL/KOC không.
- OQ-13 (PO, Kế toán): chi theo chiến dịch chỉ cho MCN hay cả creator; Kế toán có chấp nhận nhiều lệnh nhỏ, mỗi lệnh một phí chuyển khoản không.
- OQ-14 (PO): KOL/KOC rời MCN giữa chiến dịch thì tính phí thế nào.
- OQ-15 (PO, Legal): người đứng MCN có bắt buộc ký tỷ lệ 100% không.
- OQ-04 (AT): AT chi theo file xuất hay theo econtract.
- OQ-16 (AT, team My): phụ lục KOL/KOC–AT có tách mẫu theo MCN cá nhân và MCN công ty không.

## Trả lời các câu hỏi của tech lead

1. Tài khoản MCN khác tài khoản creator thế nào?
   MCN là bản ghi `mcns`. Tài khoản đăng nhập chỉ có quyền vận hành MCN, qua bảng `mcn-accounts`. Đổi người vận hành thì tiền của MCN không đổi chủ. Chi tiết: ADR-01, ADR-03.

2. Số dư MCN và số dư creator tách thế nào?
   Hai bảng riêng: creator ở `cash-flows`, MCN ở `mcn-cash-flows`. Ví dụ K có thưởng 3.000.000, MCN 15%: bảng của K ghi `+3.000.000` và `−450.000`; bảng của MCN ghi `+450.000`. Chi tiết: ADR-02, ADR-05.

3. Thuế của MCN khi người đứng MCN cũng làm creator?
   Tài khoản creator của họ tham gia chính MCN với tỷ lệ 100%. Thu nhập nội dung từ ngày ký phụ lục, ở chiến dịch bắt đầu từ mốc áp dụng, chuyển vào số dư MCN. Thuế xét một lần trên tổng các lệnh của MCN trong đợt.
   - MCN cá nhân P: phí 3.000.000 + nội dung 2.500.000 = 5.500.000, khấu trừ 10% là 550.000 (chờ Kế toán chốt ở OQ-01).
   - MCN công ty C: phí 8.000.000 + nội dung 6.000.000 = 14.000.000, không khấu trừ.

   Chi tiết: ADR-12, ADR-09, §7.3.

4. Database thay đổi gì?
   Thêm 2 bảng: `mcn-cash-flows` (dòng tiền MCN) và `mcn-payouts` (lệnh chi MCN). Thêm một số trường vào bảng có sẵn. Không thêm loại tài khoản vào `users`. Chi tiết: §6.

5. MCN là đối tượng gì?
   Công ty hoặc cá nhân ký hợp đồng với AccessTrade, định danh bằng MST hoặc CCCD. MCN sở hữu số dư, nhận tiền và chịu thuế. Công ty: không khấu trừ. Cá nhân: khấu trừ 10% (chờ Kế toán chốt ở OQ-01). Chi tiết: §0, ADR-02.

6. Chi theo chiến dịch thế nào?
   Mỗi dòng tiền của MCN ghi kèm chiến dịch, mỗi chiến dịch một lệnh chi. Ví dụ MCN cá nhân P có 3.000.000 từ chiến dịch C1 và 2.500.000 từ chiến dịch C2: hai lệnh chi. Thuế 10% tính trên tổng 5.500.000 là 550.000, chia về hai lệnh 300.000 và 250.000. Chi tiết: ADR-14, ADR-09.

7. Chỗ nào dễ nhầm creator với MCN?
   Mỗi màn hình chỉ đọc một bảng: trang Số dư của creator đọc `cash-flows`, trang Quản lý MCN đọc `mcn-cash-flows`. Chi tiết: §8.3.

Ba trường hợp thường gặp:

```mermaid
flowchart LR
  subgraph CA1["Ca 1. MCN công ty C, nhân viên E vận hành"]
    UE["user của E"] -- "vận hành" --> MC1["MCN C"] --> L1["Bảng tiền MCN C"] --> P1["Chi vào TK công ty"]
  end
  subgraph CA2["Ca 2. MCN cá nhân P, P cũng làm creator"]
    UP["user của P"] -- "vận hành" --> M2["MCN P"] --> L2["Bảng tiền MCN P"] --> P2O["Chi theo chiến dịch, thuế tính trên tổng đợt"]
    UP -- "làm nội dung, tỷ lệ 100%" --> L2
  end
  subgraph CA3["Ca 3. Người vận hành C tự làm nội dung"]
    UC["user của người vận hành"] -- "vận hành" --> MC3["MCN C"] --> L3["Bảng tiền MCN C"] --> P3O["Chi vào TK công ty, không khấu trừ"]
    UC -- "làm nội dung, tỷ lệ 100%" --> L3
  end
```

Ca 2 và ca 3: thu nhập nội dung phát sinh từ ngày ký phụ lục 100%, ở chiến dịch bắt đầu từ 01/12/2026, chuyển hết sang MCN. Thu nhập trước đó vẫn nằm ở số dư creator và chi bằng lệnh creator như hiện nay (ADR-12).

Trình bày 17 phút:

1. Bài toán và bảng §2.7 (2 phút).
2. MCN tách khỏi user, hai bảng tiền, sơ đồ trên (5 phút).
3. Một kỳ đối soát và một đợt chi với ví dụ 3.000.000đ, §7.1–7.2 (4 phút).
4. Thuế và tài khoản nhà 100%, §7.3, ADR-12 (2 phút).
5. Chiến dịch: mốc áp dụng và lệnh chi theo chiến dịch, ADR-13, ADR-14 (2 phút).
6. Câu hỏi cần chốt, §15.2 (2 phút).

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa | Ví dụ / không nhầm với |
|---|---|---|
| MCN | Công ty hoặc cá nhân ký Hợp đồng khung ① với AccessTrade. Bản ghi `mcns`, định danh bằng MST hoặc CCCD | Không phải user. Đổi người đăng nhập không đổi MCN |
| Tài khoản vận hành MCN | User có dòng `mcn-accounts` hiện hành (`isCurrent`). Chỉ mang quyền thao tác | Không sở hữu số dư MCN. "Tài khoản MCN" trong PRD và bản mẫu BA là khái niệm này |
| Người đứng MCN | Chủ MCN cá nhân, hoặc người được MCN công ty giao tài khoản vận hành | Dùng khi nói về con người. Khi nói về user đăng nhập thì dùng "tài khoản vận hành" |
| Creator, KOL/KOC | User tạo nội dung, có thu nhập ghi vào `cash-flows` | Tài khoản vận hành cũng có thể là creator (ADR-03) |
| Tài khoản nhà MCN (house account) | Dòng `mcn-members` có `rate = 100`, `house = true`: user làm nội dung cho chính MCN và tham gia MCN đó với tỷ lệ 100%. Hệ thống đặt `house = true` lúc Agree nếu user là tài khoản vận hành của chính MCN đó, hoặc có CCCD trùng CCCD của MCN cá nhân (hai lúc khác ở §6.2). User vẫn phải tự nhận link 100% và ký phụ lục. Có bắt buộc hay không thì chờ OQ-15 | Không phải loại tài khoản mới; vẫn là `users` + `mcn-members` (ADR-12) |
| Chiến dịch (campaign) | Bản ghi `events`. "Campaign" trong biên bản họp 10/11 là chiến dịch, không phải ADV (chốt 11/11) | Khác partner (ADV) |
| Mốc áp dụng | `MCN_FEE_EVENT_START_FROM`: chỉ chiến dịch có `events.startAt` từ mốc này mới bị trích phí MCN (ADR-13) | Không phải ngày ký phụ lục |
| Vai hiển thị | Mỗi màn hình hoặc API chỉ thuộc một vai: creator hoặc MCN. Một user có thể vừa là creator vừa là tài khoản vận hành | Không màn hình nào cộng số của hai vai (§8.3) |
| Dòng quan hệ | Một bản ghi `mcn-members`, mọi trạng thái (`agreed`, `active`, `leaving`, `ended`, `declined`, `sign_expired`, `superseded`) | Không đồng nghĩa với thành viên |
| Thành viên | Dòng quan hệ có `isMember = true` (`active`, `leaving`) | `agreed` (Chờ ký) chưa là thành viên (D18) |
| Reward | Một khoản thưởng gốc: `event-rewards` (thưởng view, thưởng mốc) hoặc `event-bonus` (Thưởng thêm) | Phí tính theo từng reward rồi mới cộng lên item |
| Item đối soát | Một bản ghi `reconciliation-items`. Item content gộp các reward theo (user, content, schema); item Thưởng thêm ứng với một `event-bonus` | Một item gồm nhiều reward, có thể trải nhiều ngày |
| Phần phí (`mcnSplits`) | Phần phí của một dòng quan hệ trên một item đối soát, lưu trong mảng `mcnSplits` của `reconciliation-items` | Một item có thể có hai phần phí nếu KOL/KOC đổi MCN trong khoảng ngày của item |
| Cửa sổ phí (fee window) | Khoảng ngày `[feeFrom, effTo)` giờ Asia/Ho_Chi_Minh của một dòng quan hệ, tính bằng `FeeWindow(m)` (§7.1) | Ranh giới ngày, không phải thời điểm `startAt/endAt` |
| Ngày phát sinh (incurred date) | Thưởng view: ngày có view (`event-rewards.date`); thưởng mốc: ngày đạt mốc (`date`); Thưởng thêm: ngày Admin tạo (`event-bonus.createdAt`) | Không dùng `event-rewards.createdAt` (crawler ghi trễ) hay thời điểm Lấy danh sách |
| G (gross) | Tổng thưởng của một item đối soát (`reconciliation-items.totalCash`) | Trước khi trừ phí quản lý |
| Người nhận tiền (payee) | Bên được chuyển tiền trên lệnh chi: user (creator) hoặc MCN (`mcns`) | Không suy ra từ người đăng nhập |
| Người chịu thuế (taxpayer) | Bên được ghi nhận khoản khấu trừ thuế, khóa `taxpayerKey` = `cccd:<số>`, `mst:<số>` hoặc `user:<id>` | Một taxpayer có thể có hai payee. Người đứng MCN cá nhân P có lệnh MCN P, và có thể có thêm lệnh creator cho thu nhập trước ngày ký phụ lục 100% hoặc ở chiến dịch trước mốc áp dụng. Phase 1 không gộp ngưỡng thuế giữa hai loại lệnh này (NG-6) |
| Bảng dòng tiền (sổ), bút toán, số dư | `cash-flows` là bảng dòng tiền của creator, `mcn-cash-flows` của MCN. "Sổ creator", "sổ MCN" trong tài liệu là hai bảng này. Bút toán là một dòng trong bảng: một khoản cộng (+) hoặc trừ (−) tiền. Số dư = tổng `value` theo user (creator) hoặc theo MCN | `statistic.cashRemaining` chỉ là cache hiển thị |
| Đợt chi (payout batch), lệnh chi; Min, Max | `transfers`; lệnh creator `withdraws`, lệnh MCN `mcn-payouts`. Min = `minValueCashRemaining` (số dư tối thiểu để có lệnh), Max = `maxCashWithdraw` (trần số chi) | `backend/internal/model/mg/transfer.go:44-45`. Khi đặt Max, code hiện tại chỉ lấy user có `cashRemaining ≥ max(Min, Max)` (`backend/pkg/admin/service/transfer_processing.go:96-104`), nên user có số dư dưới Max bị loại khỏi đợt; user còn lại bị cắt số chi về Max (:136-138) |
| Thuế khấu trừ tại nguồn (withholding) | TNCN AccessTrade khấu trừ lúc chi (D10) | Không tính ở đối soát |
| Snapshot | Giá trị chép tại một thời điểm, không cập nhật về sau | `rate` lúc đồng ý; `mcnSplits` lúc Lấy danh sách; `bank`, `payee`, `tax` lúc tạo lệnh |
| Idempotency key (`idemKey`) | Khóa duy nhất của một bút toán. Ghi lại cùng khóa không tạo bản ghi thứ hai | `rc:<itemId>:fee:<relId>` |
| Hợp đồng ①, ②, phụ lục | ① khung AT–MCN; ② `B2C_AMBASSADOR` AT–KOL/KOC; phụ lục chỉ định thanh toán gắn với ② | Căn cứ chi cho MCN là ①, không phải ② |

Thao tác trên UI và bước chuyển trạng thái, theo thiết kế v2.1 (code hiện tại chưa ghi `run_failed`, §2.3):

| Màn hình | Thao tác: bước chuyển |
|---|---|
| Admin › Đối soát | Lấy danh sách: `pending → processing → processed`. Duyệt tất cả: `processed → running`. Duyệt lại: `run_failed → running`. Kết thúc Duyệt: `running → completed` nếu đạt E1–E4 (§7.1), ngược lại `running → run_failed`. Hủy: `pending`, `processing`, `processed → rejected`; `run_failed` không Hủy được (INV-16) |
| Admin › Xử lý rút tiền, đợt chi | Lấy danh sách: `new → processing → processed`. Chuyển tiền: `processed → transferring → transferred`. Hoàn tất: `transferred → finished` |
| Admin › Xử lý rút tiền, lệnh MCN (`mcn-payouts`, mới) | Lấy danh sách tạo lệnh ở `draft`. Chuyển tiền: `draft → transferring`. Hoàn tất: `transferring → completed`, hoặc `→ rejected` với lệnh bị loại hay lỗi (§6.7) |

### 0.1 Tài liệu và mã tham chiếu

| Mã | Nguồn |
|---|---|
| D1–D24, Q1–Q13, FR-001–FR-022, A1–A5, NFR-001, NFR-002 | PRD v1.1 (PR #41) |
| G-x, NG-x | Mục tiêu, phi mục tiêu của tài liệu này (§1.2, §1.3) |
| INV-xx | Bất biến (§3) |
| ADR-xx | Quyết định kiến trúc (§5) |
| E1–E4 | Bốn phép kiểm cuối kỳ Duyệt của `verifyRunTotals` (§7.1). Không phải tên chiến dịch; chiến dịch trong ví dụ đặt tên C1, C2 |
| OQ-xx | Câu hỏi còn mở (§15.2) |
| R-xx | Rủi ro (§15.3) |
| Phase 1–8 | Phase của plan triển khai code (bảng ở §11.4). Khác "Phase 1" trong tên tài liệu, là phạm vi sản phẩm. "P2" là phase 2 của sản phẩm |
| SD-01–SD-08 | [08-Sequence.md](./08-Sequence.md) v3.0, 22/10/2026. Mô hình cũ: MCN là `account_type`, có bảng kê, xác nhận đối soát |
| BA-01…BA-05 | Bản mẫu BA (artifact `BVwnmqnqNZhjnX6pbXDikV`): 01 Tạo và kích hoạt, 02 Mời và thành viên, 03 Phí quản lý, 04 Đối soát và chi trả, 05 Ai thấy gì |
| BA Cần chốt, BA Đã chốt | Mục cuối bản mẫu BA |
| v1.0 | Tech spec này, bản 04/11 của Vinh Nguyễn, commit [`00aa629`](https://github.com/viewboost/accesstrade-docs/blob/00aa629bef56ed3d89c29b51615641fd3a31200c/mcn/techspec-mcn-phase1-2026-11-04.md). Mục v1.0 §n trong tài liệu này trỏ tới bản đó |
| Họp 03/11 | [meeting-261103.md](./meeting-261103.md) |
| Họp 10/11 | Biên bản họp sáng 10/11/2026 (chưa đưa lên repo): phạm vi phase 1, mốc áp dụng, cấu trúc hợp đồng trên FPT e-contract, MCN kiêm creator, tài khoản nhà 100%, chi theo chiến dịch. Mã `[seg-…]` trỏ tới đoạn trong biên bản |

## 1. Bối cảnh và phạm vi

### 1.1 Bài toán kiến trúc

PRD và bản mẫu BA mô tả hành vi (mời, ký, trích phí, chi). Hai tài liệu không nói tiền thuộc về ai và ai chịu thuế. Thiết kế dữ liệu phải trả lời bốn câu hỏi trước khi code phần sổ tiền và chi trả (phase 5–6 của plan triển khai, §11.4):

1. Số dư phí quản lý thuộc MCN hay thuộc user đăng nhập?
2. Người vừa vận hành MCN vừa là creator thì số dư, lệnh chi, thuế tách thế nào?
3. Đổi người vận hành, khóa user, chạy lại kỳ đối soát có làm mất hoặc cộng trùng tiền không?
4. Thành viên đổi MCN giữa kỳ, hoặc có khoản phát sinh trước ngày ký, thì phí tính trên phần nào?

### 1.2 Mục tiêu

- G-1. Tách bốn vai: user đăng nhập, MCN (`mcns`), người nhận tiền (payee), người chịu thuế (taxpayer). MCN có số dư, lệnh chi và chính sách thuế riêng, độc lập với tài khoản vận hành.
- G-2. Bảo toàn tiền theo từng khoản: phần KOL/KOC bị trừ đúng bằng phần MCN được cộng, kiểm được bằng truy vấn (NFR-002).
- G-3. Idempotent: chạy lại Duyệt, Lấy danh sách đợt chi, job đồng bộ không cộng trùng và không mất bút toán.
- G-4. Phí của một kỳ chỉ phụ thuộc dữ liệu phụ lục và dữ liệu thưởng tại lúc Lấy danh sách; không phụ thuộc thời điểm job chạy.
- G-5. Thuế xác định bởi loại payee và loại thu nhập; thông số thuế là cấu hình, snapshot lên lệnh chi.
- G-6. Partner không có MCN và creator không thuộc MCN có kết quả tiền và thuế như trước (NFR-001).
- G-7. MCN chỉ đọc được dữ liệu của mình (chống IDOR); giữ Q10, Q13.
- G-8. Truy vết được mọi đồng phí từ reward tới dòng file ngân hàng.

### 1.3 Phi mục tiêu (phase 1)

- NG-1. Tạm dừng, Chấm dứt MCN; đổi tỷ lệ giữa chừng; gia hạn phụ lục (D4, D12).
- NG-2. KOL/KOC xác nhận hoặc báo sai đối soát; Admin thao tác thay MCN (D6, D7).
- NG-3. MCN tự rút tiền; bảng kê, hóa đơn GTGT, chứng từ khấu trừ trong hệ thống (D13).
- NG-4. UI điều chỉnh bút toán; clawback tự động.
- NG-5. Maker-checker khi đổi tài khoản ngân hàng MCN.
- NG-6. Gộp ngưỡng thuế theo CCCD giữa lệnh MCN và lệnh creator; lũy kế ngưỡng theo tháng hoặc năm. Phase 1 chỉ gộp các lệnh của cùng một MCN trong đợt (ADR-09).
- NG-7. Viết lại đường tiền creator ngoài các điểm liệt kê ở §11.1. Các điểm đó bật theo cờ partner.
- NG-8. MCN cho partner khác Ambassador (Q6).
- NG-9. Luồng riêng cho KOL/KOC rời, vào lại hoặc đổi MCN khi chiến dịch đang chạy; đổi MCN theo yêu cầu từng tháng (họp 10/11 [seg-007, seg-039-047], để P2). Phase 1 không chặn và không có UX riêng; nếu xảy ra, `FeeWindow` chia phí theo ngày (§7.1). Cách tính này là đề xuất, chờ PO chốt ở OQ-14.
- NG-10. Chi theo chiến dịch cho lệnh creator. Đề xuất phase 1 chỉ tách lệnh MCN, chờ OQ-13.
- NG-11. Rà soát pháp lý, thuế cho MCN kiêm creator ngoài quy tắc 100% (họp 10/11 [seg-081-089], để P2).

### 1.4 Ràng buộc

- MongoDB replica set, driver `go.mongodb.org/mongo-driver v1.11.3` (`backend/go.mod:39`). Wrapper `TransactionDatabase().WithTransaction` (`backend/internal/module/database/mongodb/transaction.go:28-72`) gọi `StartTransaction`/`CommitTransaction` thủ công, không retry theo label `TransientTransactionError` hay `UnknownTransactionCommitResult`; khi commit lỗi, `AbortTransaction` trả `ErrAbortAfterCommit` và che lỗi gốc. Code MCN và code ghi sổ tiền phải dùng hàm mới `RunInTransaction` bọc `session.WithTransaction` của driver (§14.1 #1). Callback của hàm này có thể chạy lại, nên chỉ được chứa thao tác DB.
- Phiên bản server prod chưa xác nhận, nên partial index chỉ dùng điều kiện bằng, `$exists:true` và `$and` mức trên cùng.
- Tiền trong code cũ là `float64` (`backend/internal/model/mg/event_reward.go:22`, `backend/internal/model/mg/reconciliation_item.go:20`, `backend/internal/model/mg/withdraw.go:26-30`). Phần mới dùng `int64` VND.
- Econtract không có webhook; trạng thái phụ lục lấy bằng polling. Repo đã có khuôn webhook AT core ký HMAC-SHA256 (`backend/pkg/public/router/routeauth/auth.go:95-130`, dùng ở `backend/pkg/public/router/creator_profile.go:20`), có thể dùng nếu AT core gửi sự kiện SIGNED (OQ-05).
- Repo không có hạ tầng metrics. Cảnh báo qua Telegram (`backend/internal/config/env.go:44-50`).

## 2. Hiện trạng hệ thống (đã kiểm chứng)

### 2.1 Danh tính

| Thành phần | Vị trí | Hành vi |
|---|---|---|
| `users` | `backend/internal/model/mg/user.go:19-58` | Không có trường cho biết user là cá nhân hay tổ chức. `contract` (:44) giữ MST, CCCD tự khai; `accesstrade` (:51) là SSO id; `is_ekyc` (:54). Không có index nào, email không unique ở DB |
| Gắn tài khoản MCN | `backend/internal/service/mcn.go:152-204` | Theo `google.email` hoặc `info.email` đã xác thực. `VerifiedUserByEmail` (:96-109) chọn user cũ nhất khi trùng email. Không transaction |
| Q12 trong code | `backend/pkg/admin/service/mcn_validate.go:71-81`; `backend/pkg/admin/service/mcn_activate.go:59-69` | Cho dùng chung email creator; chỉ chặn user đang `isMember`; kích hoạt gắn luôn user có sẵn |
| `EnsureUserPartner` | `backend/internal/service/mcn.go:116-124`, gọi ở `backend/pkg/admin/service/mcn_activate.go:90` | Upsert `user-partners{isJoined:true}` cho user vận hành, nên user đó được đếm là creator (`backend/pkg/admin/service/partner.go:60`, `backend/pkg/admin/service/staff_statistic.go:84, 105`) |
| Middleware, lịch sử đăng nhập | `backend/pkg/public/router/routeauth/mcn.go:15-29`; `backend/pkg/public/service/user.go:1827` | `mcnID` lấy từ tài khoản, không nhận từ client; không kiểm `banned`; cache 5 phút (`backend/internal/service/mcn.go:58-73`). Lịch sử đăng nhập ghi cứng role `creator` |

### 2.2 Sổ dòng tiền và số dư

| Thành phần | Vị trí | Hành vi |
|---|---|---|
| `CashFlowRaw` | `backend/internal/model/mg/cash_flow.go:14-29` | Trường chính không có `omitempty`; `user` kiểu giá trị; `value float64`; không có idempotency key |
| `AddCashFlow` | `backend/internal/service/cashflow.go:58-84` | `oldBalance` đọc không khóa (:60-61); bỏ qua lỗi `InsertOne` (:79); gọi `UpdateStatistic` sau mỗi dòng (:81); luôn trả `nil` (:83) |
| Index `cash-flows` | `backend/internal/module/database/mongodb/index.go:222-229` | Không có unique index |
| Cache `statistic` | `backend/internal/service/user.go:141-280` | `UpdateStatistic` chạy 6 goroutine dùng chung `ctx`; `cashRemaining` = Σ sổ (:160); `CashTotal = Pending + Rejected + Completed` (:270, :482); `$set` đè cả object (:271-279) |
| `ActionMustTaxReward` | `backend/internal/constants/cash_flow.go:16-20` | Chỉ dùng cho thống kê và job thuế tháng đã tắt (`backend/pkg/public/router/schedule.go:28` bị comment). Không tham gia khấu trừ |
| UI số dư, lịch sử | `frontend/src/pages/bank/components/cashflow-section.tsx:34`; `frontend/src/pages/bank/components/withdraw-history/index.tsx:11, 28-31` | Số dư đọc `user.statistic.cashRemaining`. Tiêu đề lịch sử theo action (`backend/pkg/public/service/user.go:1070`, `backend/internal/locale/cash_flow.go:46-61`); cột `newBalance` đang bị comment |

### 2.3 Đối soát

| Thành phần | Vị trí | Hành vi |
|---|---|---|
| Gom thưởng | `backend/pkg/admin/service/reconciliation.go:421-437` | Điều kiện chỉ có `date < toAt` và `events`, không có `fromAt` |
| Item content | `backend/internal/module/database/mongodb/aggregate_pipeline/event_reward.go:34-62`; `backend/pkg/admin/service/reconciliation_processing.go:218` | Gộp theo (user, content, schema), không lọc `status`; `TotalCash` lấy `totalCashPending`. Nhóm có thể chứa reward đã completed ở kỳ trước |
| Lấy danh sách | `backend/pkg/admin/service/reconciliation_processing.go:21-66` | Ba goroutine không trả lỗi; `wg.Wait()` (:49); CAS `processing → processed` (:54-60) |
| Chuyển trạng thái | `backend/pkg/admin/service/reconciliation.go:365-373, 387, 475-493` | Đếm kỳ `running` trên mọi partner rồi mới CAS, không atomic. `run_failed` là nguồn hợp lệ của `running` và của `rejected`; không code nào ghi ra `run_failed`; admin không có nhãn cho trạng thái này |
| Duyệt | `backend/pkg/admin/service/reconciliation_running.go:83-115` | Pool 50 worker theo user; `wg.Wait()` (:103); `Sleep 15s` (:105); đặt `completed` vô điều kiện (:108-115) |
| Ghi tiền | `backend/pkg/admin/service/reconciliation_running.go:514-542, 582-638` | Thưởng thêm được CAS `approved → completed` trước khi cộng tiền vào `cash-flows` (:514-542). Cash-flow (:582-591) và reward (:593-601) ghi trong goroutine; content-analytic ghi đồng bộ và `return` sớm khi lỗi (:603-609), trước BulkWrite item (:611-620) |
| Hoa hồng người giới thiệu | `backend/pkg/admin/service/reconciliation_running.go:120, 144-239` | Gửi một lần sau khi đặt `completed`, tính trên mọi item pending lúc bắt đầu, kể cả item sau đó bị rejected; id = `user_referrer_type_firstItem_lastItem` |

Ba trạng thái ghi dở (partial write) của đường ghi tiền hiện tại, đều không có cảnh báo:

| # | Lỗi ở bước | Trạng thái để lại | Lần Duyệt sau |
|---|---|---|---|
| a | Insert cash-flow (bị bỏ qua) | Item và reward completed, thiếu dòng cộng tiền | Không xét lại; KOL/KOC mất tiền |
| b | Content-analytic, `return` sớm | Đã cộng tiền, reward completed, item pending | Reward không còn pending nên mismatch, item rejected dù tiền đã cộng |
| c | BulkWrite reward | Đã cộng tiền, item completed, reward pending | Kỳ sau gom lại reward (không có `fromAt`), cộng trùng (double credit) |

### 2.4 Đợt chi và thuế

| Thành phần | Vị trí | Hành vi |
|---|---|---|
| Trạng thái đợt | `backend/pkg/admin/service/transfer.go:376-389` | `new → processing → processed → transferring → transferred → finished`; `rejected` từ new, processed |
| Một đợt mở mỗi partner | `backend/pkg/admin/service/transfer.go:406-417` | `CountByCondition` rồi mới insert. Collection `transfers` không có index nào |
| Lấy danh sách | `backend/pkg/admin/service/transfer_processing.go:19-116` | User `banned:false` (:22-26); `return` sớm khi không có user (:41-44); cần SSO, `B2C_AMBASSADOR` SIGNED. Khi đặt Max, chỉ lấy user có `cashRemaining ≥ max(Min, Max)` (:96-104), nên user có số dư từ Min tới dưới Max bị loại |
| Tạo lệnh, khấu trừ | `backend/pkg/admin/service/transfer_processing.go:118-153`; `backend/internal/service/withdraw.go:136-139` | Số dư đọc từ sổ (:131), cắt theo Max (:136-138). `Cash ≥ 5.000.000` thì `CashTax = round(10% × Cash)`, theo từng lệnh |
| Chuyển tiền | `backend/pkg/admin/service/transfer_transferring.go:46-105` | Ghi `withdraw`, `tax`, `withdraw_fee` âm bằng `AddCashFlow`; nhánh lỗi (:83-96) không bao giờ chạy vì hàm luôn trả `nil`. Insert lỗi thì lệnh vẫn được chi mà sổ không bị trừ |
| Loại lệnh | `backend/pkg/admin/service/transfer.go:541-576` | Nhận lệnh ở `transferring` (:569); không kiểm lệnh thuộc đúng đợt |
| Hoàn tất | `backend/pkg/admin/service/transfer_finish.go:35-122` | Lệnh bị loại sau Chuyển tiền: đảo bút toán, giữ action, giá trị dương (:64-107). Gắn `transferId` lên các bút toán cộng tiền theo thứ tự cũ trước (FIFO), theo (user, partner) (:154-167) |
| File ngân hàng | `backend/pkg/admin/service/export_transfer.go:68-82, 93-120, 181-187` | 13 cột; không lọc trạng thái, chỉ loại lệnh trong `Declined`; MST, CCCD lấy từ `users.contract` |

### 2.5 Hợp đồng điện tử và phần MCN đã code

| Thành phần | Vị trí | Hành vi |
|---|---|---|
| eKYC, hợp đồng ② | `backend/pkg/public/handler/user.go:869-943`; service `backend/pkg/public/service/user.go:2554-2582`; route `backend/pkg/public/router/user.go:62-64` | Lưu eKYC (:869-887) đặt `is_ekyc` cho user tìm theo SSO id lấy từ body; Ký ② (:889-907) nhận `user_id` SSO từ body (`backend/internal/module/core/model.go:11-15`); Tra ② (:909-943) nhận `sso_ids` từ query. Là IDOR nếu econtract không ràng buộc token với SSO id (AT core xác nhận) |
| Kích hoạt thành viên | `backend/pkg/public/service/mcn_annex.go:234-264` | `signedAt` là giờ đồng bộ; filter `signDeadline > signedAt` (:242); chuyển mọi dòng `agreed` khác sang `superseded` (:256-257) |
| Kết thúc quan hệ | `backend/pkg/public/service/mcn_leave.go:114-148`; `backend/pkg/public/schedule/schedule.go:61`; `backend/pkg/public/service/mcn_member.go:159-175` | KOL/KOC rời và hết 12 tháng chỉ chuyển `ended` qua job 15 phút; MCN chấm dứt quan hệ thì ghi `ended` ngay. Job tắt được bằng `MCN_JOB_ENABLED` (`backend/pkg/public/service/mcn_job.go:27-29`); khóa `SETNX` + `DEL` không kiểm token (:31-37) |

Các chênh lệch khác của code MCN trên nhánh (StartSign, Agree, hết hạn ký, sửa hồ sơ) liệt kê ở §14.1 kèm file:dòng.

### 2.6 Giả định ngầm của hệ thống hiện tại

(1) Một user là một payee: danh tính chi trả đi qua SSO và hợp đồng ② của một cá nhân. (2) Người làm ra tiền là người nhận tiền: `runCashBack` cộng toàn bộ `TotalCash` cho `item.User`. (3) Một (user, partner) là một quỹ: số dư cộng mọi action, lệnh chi rút toàn bộ. (4) Người nộp thuế là cá nhân cư trú, 10% trên số chi từng lệnh; không có loại người nộp thuế, loại thu nhập, MST tổ chức. (5) Điều kiện chi (`banned`, SSO, ②, Min) áp ở mức user; MST, CCCD trên file chi lấy từ `users.contract`. (6) Ghi sổ không cần idempotency vì mỗi kỳ chỉ chạy một lần.

### 2.7 Vì sao không thể cộng phí MCN vào số dư user

v1.0 cộng `mcn_fee` vào `cash-flows` của user vận hành (v1.0 §8.2) và chi bằng `IsPayableMcnUser` + `TaxExempt=true` (v1.0 §9). Kết hợp với PRD Q12 (dùng chung tài khoản creator):

| # | Tình huống | Theo v1.0 | Theo v2.1 | Sai lệch của v1.0 |
|---|---|---|---|---|
| 1 | MCN cá nhân P dùng chung tài khoản creator. Trong đợt: thu nhập creator 2.500.000, phí 3.000.000 | Một lệnh 5.500.000, `TaxExempt` nên thuế 0 | Tài khoản creator của P (uP) là tài khoản nhà 100%: cả 5.500.000 vào số dư MCN P, chi theo chiến dịch. Thuế 550.000 tính trên tổng các lệnh của P trong đợt (`groupBase`, ADR-09, ADR-12) | Miễn khấu trừ cả phí MCN cá nhân lẫn thu nhập creator, trong khi BA-04 và FR-019 ghi MCN cá nhân khấu trừ như KOL/KOC (Kế toán xác nhận ở OQ-01). Chứng từ không tách được loại thu nhập |
| 2 | MCN công ty C, tài khoản vận hành uC có thu nhập nội dung 6.000.000, phí 8.000.000 | Một lệnh 14.000.000, thuế 0, chi vào TK công ty | uC là tài khoản nhà 100% của C: lệnh MCN theo chiến dịch, tổng 14.000.000, thuế 0, chi vào TK công ty. Căn cứ là phụ lục 100%, không phải cờ trên tài khoản (ADR-12) | Thuế của thu nhập nội dung là hệ quả của cờ trên tài khoản, không phải quyết định nghiệp vụ. PRD Q8 đề xuất miễn; nếu Legal chốt khác, v1.0 không biểu diễn được |
| 3 | Đổi người vận hành U1 → U2 sau kỳ K, rồi chạy lại K | 3.000.000 nằm ở U1. v1.0 chống cộng trùng bằng cách so tổng `mcn_fee` đã ghi theo (user, kỳ) với số phải ghi. Tổng đã ghi của U2 là 0, nên chạy lại K cộng thêm 3.000.000 cho U2 trong khi U1 vẫn giữ 3.000.000 | Số dư gắn với `mcns`; `idemKey` theo (item, dòng quan hệ) | Cộng trùng (double credit) 3.000.000 |
| 4 | uC bị `banned` vì vi phạm với tư cách creator | Đợt chi lọc `banned:false` (`backend/pkg/admin/service/transfer_processing.go:22-26`): phí của C không được chi | Điều kiện chi MCN dựa trên ① và TK ngân hàng | Giữ tiền của pháp nhân vì lỗi của cá nhân |
| 5 | Thống kê creator của uC | `cashRemaining` tăng 3.000.000, `CashTotal` không đổi (`backend/internal/service/user.go:160, 270`) | Thống kê creator không chứa phí | Màn số dư creator lệch; lịch sử lẫn phí MCN |

Kết luận: số dư phí quản lý phải gắn với bản ghi MCN (`mcns`), không gắn với user. Sửa một hàm không đủ, vì số dư, lệnh chi và thuế hiện đều tính theo `user`.

## 3. Bất biến (invariant)

| ID | Bất biến | Cơ chế bảo đảm | Kiểm chứng |
|---|---|---|---|
| INV-01 | Một KOL/KOC có tối đa một dòng quan hệ `isMember` | Partial unique `user` `{isMember:true}` (`backend/internal/module/database/mongodb/index.go:469`) | Test đồng thời (đã có) |
| INV-02 | Mỗi (user, MCN) tối đa một dòng `agreed` | Partial unique `(user, mcn)` `{isPending:true}` | Test Agree đồng thời |
| INV-03a | Tài khoản vận hành của MCN X chỉ được có dòng `mcn-members` (`agreed`, `active` hoặc `leaving`) với chính X. Dòng đó phải có `rate = 100` và `house = true` | `RunInTransaction` + `$inc users.mcnGuardVer` ở mọi bước chuyển vai (ADR-04) | Test tài khoản vận hành nhận link 15% của chính MCN; test gắn user đang có dòng dưới 100% với chính MCN |
| INV-03b | User đang có dòng `agreed`, `active` hoặc `leaving` với MCN khác thì không gắn được làm tài khoản vận hành của X | Như INV-03a | Test bind giữa lúc Chờ ký MCN khác rồi ký |
| INV-04 | Mỗi MCN tối đa một tài khoản hiện hành; mỗi user vận hành tối đa một MCN | Partial unique `mcn` và `user` `{isCurrent:true}` | Test index |
| INV-05 | Mỗi user tối đa một phụ lục đang mở ký | Partial unique `user` `{annexInFlight:true}` trên `mcn-members` | Test StartSign hai MCN đồng thời |
| INV-06 | `rate ∈ [0,100]`, không đổi; `feeFrom` ghi một lần; cận trên cửa sổ là hàm `FeeWindow(m)` của các mốc đã lưu, không đọc trạng thái do job ghi | Không có API sửa; filter `{feeFrom:{$exists:false}}` | Test Lấy danh sách khi job chưa chạy |
| INV-07 | Cửa sổ phí của một user không chồng nhau | Suy ra từ INV-01 và §7.1 | Unit test |
| INV-08 | Mỗi reward: `0 ≤ fee_r ≤ floor(cash_r)`. Mỗi item: `Σ base_j ≤ totalCash`, `totalCash = netCash + mcnFee` | Công thức §7.1; kiểm trong `applyMcnFees` | Unit test |
| INV-09 | Kỳ chỉ sang `processed` khi `mcnSnapshot.status = done`; `mcnSplits` không đổi sau `processed` | CAS điều kiện; chỉ `applyMcnFees` ghi | Test lỗi snapshot |
| INV-10 | Item `completed` khi và chỉ khi có đủ bút toán `rc:<itemId>:*`. Item không ở trạng thái `completed` không có bút toán nào mang khóa đó | `postItem` trong transaction, CAS item đầu tiên; E1–E4 | `verifyRunTotals`, job đối chiếu |
| INV-11 | Bảo toàn theo item: `−Σ cash-flows(mcn_fee) = Σ mcn-cash-flows(mcn_fee) = mcnFee` | Cùng transaction | E2 |
| INV-12 | Mỗi `idemKey` một bút toán trên mỗi sổ; `idemKey` không bao giờ là chuỗi rỗng; mỗi (transfer, mcn, event) một lệnh | `uniq(idemKey)`; `omitempty`; `uniq(transfer, mcn, event)` | Test chạy lại; test mức nguồn |
| INV-13 | `mcn-cash-flows` chỉ ghi thêm (append-only), chỉ qua `McnLedger().Post` | Repository riêng không trả `IDatabase` | Rà mức nguồn trong CI |
| INV-14 | Lệnh MCN chỉ trừ tiền MCN khi `Balance(mcn, event) ≥ cash`, đọc trong cùng transaction có `$inc mcns.ledgerVer` | ADR-08, ADR-14 | Test hai đợt đồng thời |
| INV-15 | Đợt chi của partner bật `LedgerV2` không sang `processing` khi partner có kỳ `running` hoặc `run_failed` | Kiểm ở bước Lấy danh sách đợt chi | Test |
| INV-16 | Kỳ `run_failed` chỉ chuyển sang `running`, không sang `rejected` | `isValidStatus` | Test |
| INV-17 | Snapshot `bank`, `payee` của lệnh MCN ghi lúc tạo lệnh. `tax` ghi ở bước thuế nhóm, chỉ được tính lại khi lệnh khác cùng nhóm bị loại lúc còn `draft`. Từ khi lệnh rời `draft`, cả ba không đổi. Cờ `taxGroupBroken` là trường riêng, nằm ngoài `tax`. `identityNumber`, `type` của MCN không đổi sau `active` | Không có đường cập nhật | Rà route |
| INV-18 | MCN chỉ đọc dữ liệu của chính mình | `mcnID` từ context; lọc `mcnSplits.mcn`, `mcn` | Test IDOR |
| INV-19 | Dòng quan hệ `house = true` có `rate = 100` | Kiểm trong transaction ở mọi bước đặt `house` (Agree, StartSign, Bind, Admin Activate); không có API sửa `rate` | Test Agree link dưới 100% khi là tài khoản nhà |
| INV-20 | Phí chỉ trích trên khoản của chiến dịch có `events.startAt ≥ MCN_FEE_EVENT_START_FROM` | Lọc trong `applyMcnFees`; mốc snapshot lên `reconciliations.mcnSnapshot.eventStartFrom` | Test chiến dịch bắt đầu 30/11 và 01/12 |

## 4. Kiến trúc tổng thể

Hệ thống chia ba lớp. Lớp đăng nhập (`users`, `mcn-accounts`) chỉ quyết định ai được thao tác. Lớp MCN và thành viên (`mcns`, `mcn-documents`, `mcn-invite-links`, `mcn-members`) quyết định MCN nào thu phí của KOL/KOC nào, tỷ lệ bao nhiêu, trong khoảng ngày nào. Lớp tiền (đối soát, hai bảng dòng tiền, hai loại lệnh chi, chính sách thuế, file ngân hàng) không đọc `mcn-members` lúc ghi sổ. Đối soát chép phần phí vào `mcnSplits` lúc Lấy danh sách. Lệnh chi chép `bank`, `payee`, `tax` lúc tạo lệnh.

```mermaid
flowchart TB
  subgraph S1["Đăng nhập"]
    U["users (người đăng nhập)"] -- "vận hành" --> ACC["mcn-accounts (isCurrent)"]
  end
  subgraph S2["MCN và thành viên"]
    MCN["mcns (chủ số dư, payee, taxpayer)"] --> DOC["mcn-documents (bank, hợp đồng ①)"]
    MCN --> LINK["mcn-invite-links (rate)"] --> MBR["mcn-members (rate, feeFrom, endAt)"]
  end
  subgraph S3["Tiền"]
    ER["event-rewards, event-bonus"] -- "Lấy danh sách, applyMcnFees" --> RI["reconciliation-items + mcnSplits"]
    RI -- "postItem: +G, -fee" --> CF["cash-flows (creator)"] --> WD["withdraws"]
    RI -- "postItem: +fee" --> MCF["mcn-cash-flows (MCN)"] --> PO["mcn-payouts"]
    WD --> TAX["TaxPolicyFor, file ngân hàng"]
    PO --> TAX
  end
  ACC --> MCN
  U -- "KOL/KOC" --> MBR
  MBR -. "FeeWindow" .-> RI
```

```mermaid
erDiagram
  partners ||--o{ mcns : "mcnEnabled"
  mcns ||--o{ mcn_accounts : "tối đa 1 isCurrent"
  users ||--o{ mcn_accounts : "tối đa 1 isCurrent"
  mcns ||--o{ mcn_documents : "phiên bản"
  mcns ||--o{ mcn_invite_links : "tạo"
  mcn_invite_links ||--o{ mcn_members : "tham gia qua"
  users ||--o{ mcn_members : "KOL/KOC"
  reconciliations ||--o{ reconciliation_items : "gồm"
  reconciliation_items ||--o{ mcn_splits : "nhúng"
  mcn_members ||--o{ mcn_splits : "mỗi phần phí thuộc một dòng quan hệ"
  users ||--o{ cash_flows : "sổ creator"
  mcns ||--o{ mcn_cash_flows : "sổ MCN"
  events ||--o{ mcn_cash_flows : "event bắt buộc"
  transfers ||--o{ withdraws : "lệnh creator"
  transfers ||--o{ mcn_payouts : "lệnh MCN"
  mcns ||--o{ mcn_payouts : "payee"
  events ||--o{ mcn_payouts : "một lệnh mỗi chiến dịch"
  mcn_payouts ||--o{ mcn_cash_flows : "bút toán chi"
```

Tên trong ER dùng gạch dưới; collection thật dùng gạch nối. `mcn_splits` là mảng nhúng trong `reconciliation-items`. `mcn-accounts` giữ cả dòng `revoked`, nên quan hệ là 1-n với tối đa một dòng hiện hành.

## 5. Quyết định kiến trúc (ADR)

### ADR-01. Liên kết danh tính

Bối cảnh
- v1.0 Nguyên tắc 1 đã đúng: không thêm `type`/`role` lên `users`; vai MCN đến từ `mcn-accounts`. Code đã làm theo (`backend/pkg/public/router/routeauth/mcn.go:15-29`).
- Thiếu: không có trạng thái thu hồi; `uniq(user)` không phân biệt dòng hiện hành (`backend/internal/module/database/mongodb/index.go:452-456`); không có `uniq(mcn)`.

| Tiêu chí | A. Bảng quan hệ `mcn-accounts` (v1.0) | B. User riêng cho MCN, `account_type` (SD-01) | C. Role, claim trên `users` |
|---|---|---|---|
| Đổi người vận hành | Thu hồi dòng, mời email mới | Đổi email đăng nhập trên user MCN; lịch sử đăng nhập lẫn hai người | Sửa trường trên user |
| Ảnh hưởng code cũ | Thấp | User MCN xuất hiện trong các vòng quét mọi user (`backend/pkg/admin/service/admin_notification.go:525-535`, `backend/pkg/admin/service/partner.go:60`, `backend/pkg/admin/service/staff_statistic.go:84, 105`) | Mọi chỗ đọc `users` |
| Khớp PRD | Có (D16, Nguyên tắc 2 của PRD) | Không | Không |

Quyết định: A, giữ như v1.0. Bổ sung `isCurrent`, trạng thái `revoked`, `history[]`, `uniq(mcn)` và `uniq(user)` theo `isCurrent`. Phase 1 mỗi MCN một tài khoản hiện hành.

Hệ quả
- (+) Chiếm tài khoản (ATO) người vận hành không đổi được nơi nhận tiền, vì tài khoản ngân hàng do Admin khai.
- (−) Đổi người vận hành cần script có ticket (`cmd/mcn-rebind`), phase 1 chưa có UI.

### ADR-02. Ai sở hữu phí quản lý; sổ `mcn-cash-flows`

Bối cảnh
- Khác biệt thật giữa v1.0 và v2.0 nằm ở quyết định này. v1.0 đã có `mcns`, `mcn-accounts`, `WithdrawRaw.RecipientType/Mcn`, lấy MST từ `mcns` (v1.0 §2, §9). Nhưng số dư phí và lệnh chi treo trên `users._id` của người vận hành: `creditMcnFees` ghi `cash-flows` của `acc.User` (v1.0 §8.2), đợt chi tìm MCN qua `IsPayableMcnUser(user)` (v1.0 §9). Hệ quả ở §2.7.

| Tiêu chí | A. `cash-flows` của user vận hành (v1.0) | B. Tạo một user giả cho mỗi MCN để đứng tên số dư | C. Sổ riêng `mcn-cash-flows` theo `mcns` | D. `cash-flows` thêm owner `mcn`, `user` rỗng |
|---|---|---|---|---|
| Chủ sở hữu đúng pháp lý | Không | Gián tiếp qua user giả | Có | Có |
| Đổi người vận hành | Số dư nằm ở user cũ; cộng trùng khi chạy lại | Không ảnh hưởng | Không ảnh hưởng | Không ảnh hưởng |
| Điều kiện chi, thuế | Lẫn với điều kiện cá nhân (`banned`, SSO, ②) | Phải bỏ qua kiểm SSO, ② cho user giả | Riêng | Phải rẽ nhánh ở mọi chỗ đọc `withdraws` |
| Ảnh hưởng code cũ | `UpdateStatistic`, lịch sử public | User giả xuất hiện trong các vòng quét mọi user | Không | Dòng `user` rỗng rơi vào mọi `$group` theo user |
| Khối lượng | Thấp | Trung bình | Trung bình | Trung bình |

Quyết định: C.
- MCN (`mcns`) sở hữu số dư MCN, nhận tiền và chịu thuế cho hai khoản: phí quản lý và thu nhập nội dung của tài khoản nhà.
- Thu nhập nội dung cộng vào `cash-flows` của user làm nội dung. Với tài khoản nhà, toàn bộ số đó bị trừ lại và cộng sang `mcn-cash-flows` qua phần phí 100% (ADR-12).
- `mcn-cash-flows` chỉ ghi thêm; `value int64` có dấu; `idemKey` unique; số dư `Balance(mcn) = Σ value`, không lưu `oldBalance/newBalance`, không có cache dùng để quyết định chi.
- Mọi đọc ghi `mcn-cash-flows` đi qua repository `McnLedger()`, gồm `Post(sc, entries...)` (trả lỗi thật), `Balance(sc, mcn)` và `EventBalance(sc, mcn, event)`. Ký hiệu `Balance(mcn, event)` trong tài liệu là hàm `EventBalance` (ADR-14). Khác các DAO hiện có, repository này không lộ `IDatabase`, `UpdateOne`, `DeleteOne`, `Collection()`, để không đường nào sửa hay xóa được bút toán.
- Mọi thao tác làm giảm số dư MCN (chi, điều chỉnh âm) chạy trong transaction có `$inc mcns.ledgerVer`, để các thao tác trên cùng một MCN chạy lần lượt. Cộng phí lúc Duyệt thì không cần, vì không làm giảm số dư.

Hệ quả
- (+) Không kế thừa lỗi bỏ qua insert và race `oldBalance` của `AddCashFlow`.
- (+) Điều chỉnh chỉ phía MCN (MCN nhận thiếu) không chạm sổ creator. Hoàn phí trích thừa thì ghi cả hai sổ trong một transaction (§7.5).
- (−) Báo cáo tổng hợp phải union hai sổ. Màn Xử lý rút tiền cần khối MCN.

### ADR-03. Tài khoản vận hành có được là creator không

Bối cảnh
- Sau khi được gắn vào MCN, tài khoản vận hành vẫn đăng bài như creator. Vì vậy hệ thống phải cho một user vừa vận hành MCN vừa làm creator, bất kể quy tắc email lúc tạo.
- Thu nhập nội dung của user đó tính theo ADR-12 (tài khoản nhà 100%). D14 và mục Đã chốt của bản mẫu BA ghi "tính như creator bình thường"; họp 10/11 đã thay quy tắc này (§14.3 #8).
- PRD Q12 cho dùng chung email creator. v2.1 chỉ chặn khi user đang Chờ ký hoặc là thành viên của MCN khác (INV-03b). Code hiện chặn email của mọi thành viên ở tạo và kích hoạt MCN (`backend/pkg/admin/service/mcn_validate.go:71-81`).
- BA-01 ghi "Không trùng với tài khoản đã có". Mục Cần chốt #3 của bản mẫu BA hỏi "MCN cá nhân thường đã có tài khoản creator. Có cho dùng email của tài khoản đó làm email đăng nhập MCN?" và đang để câu trả lời "Không, dùng email chưa có tài khoản như MCN công ty". Cả hai ngược với PRD Q12.
- Họp 10/11 chốt: người đứng MCN được đồng thời là creator trên cùng portal [seg-056-060]. Lệch trên giải quyết theo PRD Q12.
- Sau ADR-02 và ADR-12, lựa chọn này không ảnh hưởng tiền và thuế. Đây là quyết định trải nghiệm và vận hành, không phải điều kiện để tiền đúng. Phương án "chặn email của user đã có dữ liệu creator" bị loại: chỉ kiểm tại lúc gắn nên không giữ được ranh giới, mà vẫn chặn MCN cá nhân đã là creator.

| Tiêu chí | A. Dùng chung (PRD Q12, code hiện tại) | B. Email chưa thuộc user nào lúc tạo và kích hoạt (BA-01) |
|---|---|---|
| Sau khi gắn, user vừa vận hành MCN vừa làm creator | Có | Có (D14) |
| MCN cá nhân đã là creator | Dùng tài khoản đang có | Phải tạo Google khác; P có hai user cùng CCCD |
| Bất biến kiểm được | INV-03a, INV-03b | INV-03a, INV-03b và email trống tại lúc tạo, sửa, kích hoạt, gắn |
| Chi phí kỹ thuật | Đã có | Thêm kiểm ở 4 điểm; xử lý user tạo sau kích hoạt, trước khi gắn |
| Ảnh hưởng tiền, thuế | Không | Không |

Quyết định: A, theo PRD Q12 và họp 10/11. Câu hỏi cũ OQ-02 (email MCN có được trùng tài khoản creator không) đóng tại đây. Bất biến về vai: INV-03a, INV-03b, INV-19. Thu nhập nội dung của tài khoản vận hành đi theo ADR-12 (tài khoản nhà 100%). Mỗi màn hình, thông báo, thống kê chỉ hiện số của một vai, creator hoặc MCN (bảng §8.3). Bỏ `EnsureUserPartner` cho user vận hành, để user đó chỉ được đếm là creator khi tự onboarding.

Hệ quả
- (+) Không chặn MCN cá nhân đã là creator, ca phổ biến mà BA nêu ở Cần chốt #3. Một người một user nên `taxpayerKey` nhất quán.
- (−) UI phải tách rõ hai vai. Bản mẫu BA-01 phải bỏ câu "Không trùng với tài khoản đã có".

### ADR-04. Bất biến vai và xử lý đồng thời

Bối cảnh
- "Tài khoản MCN không là thành viên" chỉ chặn ở Agree (`backend/pkg/public/service/mcn_invite.go:142-145, 172-174`). `StartSign`, `SyncSign`, `ActivateMember`, job `McnSyncAnnex` không kiểm lại. Bind chỉ xét dòng `isMember`, chưa xét dòng `agreed`.
- Kịch bản vi phạm: U đồng ý lời mời của MCN A. Admin kích hoạt MCN B bằng email của U; U đăng nhập và được gắn vào B. Sau đó U ký phụ lục của A, vừa thu phí vừa chịu phí.
- Agree là check-then-insert.

| Tiêu chí | A. Check-then-act (hiện tại) | B. Collection guard `mcn-user-roles` | C. Transaction + `$inc users.mcnGuardVer` + partial unique `isPending` |
|---|---|---|---|
| Chặn write skew giữa hai collection | Không | Có | Có (write conflict trên cùng document `users`) |
| Rủi ro lệch dữ liệu | – | Cao: mọi đường kết thúc phải xóa dòng guard | Không sao chép trạng thái |
| Phủ trạng thái `agreed` | Không | Không | Có |

Quyết định: C.
- Mọi bước chuyển vai chạy trong `RunInTransaction`: `$inc users.mcnGuardVer` trên user liên quan; đọc lại điều kiện trong transaction; ghi.
- Hai bước chuyển vai chạy đồng thời trên cùng user đều ghi một document `users`, nên một bên nhận `WriteConflict`. Driver chạy lại callback của bên đó và đọc trạng thái mới. Điều kiện không còn đúng thì trả `409 MCN_MEMBER_STATE_CHANGED`; còn đúng thì ghi bình thường. Hết số lần retry cũng trả 409.
- `mcn-members.isPending` (true khi và chỉ khi `status=agreed`), partial unique `(user, mcn)` `{isPending:true}`.

| Phía | Bước | Điều kiện kiểm trong transaction |
|---|---|---|
| Thành viên | Agree, StartSign, SyncSign, ActivateMember, `McnSyncAnnex` | User không có `mcn-accounts` hiện hành. Nếu có, `mcn-accounts.mcn` phải bằng `link.mcn` và `link.rate = 100`; dòng được ghi `house = true` |
| Người vận hành | Admin Activate (khi gắn ngay), `BindAccountOnLogin` | User không có dòng `agreed`, `active` hoặc `leaving` với MCN khác (INV-03b). Nếu có dòng với chính MCN này: `rate = 100` thì gắn và đặt `house = true` cho dòng đó; dưới 100% thì không gắn (INV-03a) |

- Bind tìm thấy hơn một user có cùng email đã xác thực thì không gắn, gửi Telegram (`users` không có unique index theo email).
- Agree đặt `house = true` khi (1) user là tài khoản vận hành của chính MCN, hoặc (2) MCN là cá nhân và `users.contract.identificationNumber` của user (đã chuẩn hóa, chỉ giữ chữ số) bằng `mcns.identityNumber`.
- Dòng `house` mà link dưới 100% thì Agree trả `MCN_HOUSE_RATE_REQUIRED` (INV-19).
- User chưa khai CCCD thì vẫn cho đồng ý, ghi `selfCheck = unresolved`. StartSign so lại. Khớp CCCD của MCN cá nhân mà link dưới 100% thì từ chối ký, trả `MCN_HOUSE_RATE_REQUIRED`. Khớp và link 100% thì đặt `house = true`. Từ StartSign trở đi, CCCD không làm đổi `house` nữa; chỉ bước gắn tài khoản vận hành (bảng trên) còn đặt được `house = true`.
- v2.0 dùng mã `MCN_SELF_MEMBERSHIP` để chặn hẳn việc tự tham gia MCN của mình. v2.1 bỏ mã này, vì họp 10/11 yêu cầu ngược lại (ADR-12).
- Agree yêu cầu KOL/KOC đã tham gia partner của MCN (`user-partners{isJoined:true}`).
- Lời gọi econtract (`CreateAnnex`) nằm ngoài transaction (§6.8).

Hệ quả
- (+) Bất biến bảo đảm ở mức DB, không cần collection phụ.
- (−) Ghi ngoài transaction lên cùng document `users` (ví dụ `UpdateStatistic`) chờ transaction kết thúc. Bước chuyển vai hiếm, độ tranh chấp thấp.

### ADR-05. Ghi sổ phía KOL/KOC: gross và dòng trừ phí

Bối cảnh
- v1.0 §8.2 ghi một dòng net với lý do giữ cơ sở thuế qua `ActionMustTaxReward`. Lý do không đúng: khấu trừ chỉ diễn ra ở `backend/internal/service/withdraw.go:136-139` trên số chi; `ActionMustTaxReward` chỉ nuôi thống kê và job thuế tháng đã tắt.
- FR-018 yêu cầu sổ ghi đủ khoản thưởng và khoản trừ phí.

| Tiêu chí | A. Một dòng net | B. `+G` và một dòng `−fee_j` cho mỗi phần phí |
|---|---|---|
| Khớp FR-018 | Không | Có |
| Truy vết G và phí trên sổ | Mất phần phí | Đủ |
| Bảo toàn tiền kiểm được trên sổ | Không | Có, theo cặp `idemKey` |

Quyết định: B.
- Action mới `mcn_fee`, giá trị âm, `options.{mcn, mcnMember, rate, reconciliationItem, event}`. Category giữ `event` để bộ lọc lịch sử (`backend/internal/util/mgquery/common.go:361-365`) hiện khoản trừ cạnh khoản thưởng. Khai `TitleCashFlowVn/En` cho `mcn_fee`, `mcn_fee_adjustment` (`backend/internal/locale/cash_flow.go`), tiêu đề kèm tên MCN và tỷ lệ.
- Mỗi phần phí một dòng, cùng `idemKey` với dòng `+fee_j` bên `mcn-cash-flows`. Mỗi item đối soát mới cộng tiền bằng khóa `rc:<itemId>:credit`, kể cả item không có MCN.
- `cash-flows.idemKey` khai `string` với tag `bson:"idemKey,omitempty"`, partial unique `{idemKey:{$exists:true}}`. Thiếu `omitempty` thì mọi bút toán chưa đặt khóa (withdraw, tax, hoàn thuế…) mang `idemKey:""`, từ dòng thứ hai trùng khóa và bị `AddCashFlow` bỏ qua lỗi. Chuỗi rỗng là lỗi lập trình; writer mới từ chối.
- `mcn_fee` không thuộc `ActionMustTaxReward`.

Hệ quả
- (+) Idempotent ở cấu trúc dữ liệu.
- (−) Nếu Legal đổi cơ sở thuế sang G (R-01) thì không thể chỉ đổi cấu hình. Phải thiết kế thêm cách phân bổ G về từng lệnh chi (§7.3).

### ADR-06. Snapshot phí: thời điểm xét, cửa sổ ngày, làm tròn

Bối cảnh
- Đã chốt: không trích phí khoản phát sinh trước ngày ký hoặc từ ngày kết thúc, xét theo ngày phát sinh (D20, D24); Thưởng thêm phát sinh ngày Admin tạo (PRD §0, Q11). Item content gộp nhiều ngày, không lọc trạng thái (§2.3).
- Rời MCN và hết 12 tháng chỉ thành `ended` khi job chạy (§2.5). Nếu cận trên cửa sổ phí lấy từ trạng thái do job ghi, thì Lấy danh sách chạy trước job vẫn trích phí cả những ngày sau khi rời hoặc sau 12 tháng.
- Phụ lục cũng có thể được kích hoạt sau khi kỳ đã Lấy danh sách. Nếu `feeFrom` theo giờ ký thật thì cửa sổ phí lùi về trước và chạm vào kỳ đã chốt.
- Ba nguồn làm tròn khác nhau: FR-016 từng khoản; SD-04 `floor` từng dòng; BA-03 trên tổng kỳ.

| Trục | Phương án loại | Phương án chọn |
|---|---|---|
| Thời điểm xét | Trạng thái lúc Lấy danh sách (v1.0), trái D20 | Ngày phát sinh của từng reward |
| Cận dưới | `startOfDayHCM(annex.signedAt)`: hồi tố khi kích hoạt sau snapshot | `feeFrom = startOfDayHCM(activatedAt)`, ghi một lần khi `agreed → active` |
| Cận trên | `feeTo` do job ghi khi `→ ended` | `FeeWindow(m)` tính từ `endAt`, `leaveEffectiveAt`, `endedAt` |
| Ngày phát sinh Thưởng thêm | Trường `incurredAt` Admin lùi được: trái PRD §0, cho phép dời phí giữa KOL/KOC và MCN | `event-bonus.createdAt` |
| Làm tròn | Trên tổng kỳ (BA-03) hoặc trên phần phí | Từng reward, half-up, chặn bởi `floor(cash_r)` (FR-016) |
| Lỗi khi snapshot | Item thiếu phần phí coi như không có MCN (fail-open) | Kỳ giữ `processing`, không sang `processed` (fail-closed) |

Quyết định
- Công thức và cửa sổ: §7.1.
- `applyMcnFees(ctx, rc)` chạy sau `wg.Wait()` (`backend/pkg/admin/service/reconciliation_processing.go:49`), trước CAS `processing → processed` (:54-60). Xét mọi dòng quan hệ đã có `feeFrom` của MCN có `mcns.partner = rc.partner`, gồm cả `ended`. Mỗi phần phí gắn với một dòng quan hệ, không gắn với MCN, vì KOL/KOC có thể rời rồi ký lại cùng MCN trong khoảng ngày của một item.
- Mỗi item đã xét ghi `mcnEvaluatedAt`, kể cả khi không có phần phí. Xong toàn kỳ thì ghi `reconciliations.mcnSnapshot{status: done, items, splits, totalFee}`. CAS sang `processed` có điều kiện `mcnSnapshot.status = done`. Lỗi sau 3 lần thử: `mcnSnapshot.status = failed`, kỳ giữ `processing`, Telegram; Admin Hủy kỳ rồi lập lại.
- Tỷ lệ 0% vẫn lưu phần phí (MCN cần thấy) nhưng không sinh bút toán.

Hệ quả
- (+) Kết quả không phụ thuộc thời điểm chạy job; không có hồi tố qua snapshot đã chốt. MCN chỉ trích phần thuộc thời gian của mình (D24), xem được kỳ cũ sau khi thành viên rời (D22).
- (−) `feeFrom` lấy theo ngày hệ thống phát hiện phụ lục SIGNED, không theo ngày ký. Hai ngày thường trùng nhau. Đồng bộ qua nửa đêm thì MCN mất một ngày phí; job chậm, tắt hoặc econtract lỗi thì mất số ngày tương ứng (lệch FR-014, §14.3).
- (−) Tổng phí MCN trong kỳ có thể lệch `ΣG × tỷ lệ` (cách BA-03 hiển thị) vài đồng.
- (−) Thưởng thêm Admin tạo để bù cho một khoản cũ sẽ bị trích phí theo dòng quan hệ có hiệu lực vào ngày tạo Thưởng thêm, không theo ngày của khoản gốc (PRD Q11).

### ADR-07. Ghi sổ lúc Duyệt cho mọi khoản

Bối cảnh
- Đường cũ ghi cash-flow, reward, item bằng các lệnh độc lập, để lại ba trạng thái ghi dở ở §2.3. v1.0 §8.2 đề xuất `creditMcnFees` kiểu delta (đọc tổng đã ghi rồi ghi phần chênh): read-then-write, hai runner đồng thời cộng trùng.
- Phương án B (giữ đường ghi cũ cho khoản không có MCN, chỉ thêm `verifyRunTotals`) không đủ. Lỗi (a) ở §2.3 làm mất dòng cộng tiền, nên phép kiểm E3 ở §7.1 (mỗi item completed có đúng một dòng `rc:<itemId>:credit`) luôn sai. Duyệt lại chỉ xử lý item `pending`, nên kỳ kẹt ở `run_failed`. Với lỗi (b) và (c), E3 không phát hiện được.

| Tiêu chí | A. Giữ đường cũ | B. Đường cũ + `idemKey` + `verifyRunTotals` | C. `postItem` trong transaction cho mọi khoản | D. Delta `creditMcnFees` (v1.0) |
|---|---|---|---|---|
| Mất tiền không cảnh báo | Có | E3 phát hiện (a) nhưng không tự sửa | Không | Có (a) |
| Cộng trùng khi chạy lại | Có (c) | Có (c) | Không | Có khi chạy đồng thời |
| Duyệt lại đưa được kỳ từ `run_failed` về `completed` | – | Không | Có | – |
| Đổi hành vi partner không có MCN | Không | Có | Có | Không |

Quyết định: C, bật theo cờ `PartnerOpts.LedgerV2`.
- Mọi khoản đi qua `postItem` (§7.1). Partner tắt cờ chạy đúng code cũ.
- Partner có MCN phải bật `LedgerV2` trước kỳ đối soát đầu tiên có phí. `Mcn().EnabledFor` chỉ kiểm `McnEnabled`. `applyMcnFees` không làm gì khi `MCN_FEE_EVENT_START_FROM` trống. Mốc đã đặt mà partner chưa bật `LedgerV2` thì `applyMcnFees` báo lỗi, kỳ giữ `processing` (fail-closed như ADR-06).
- Bỏ `Sleep 15s` (`backend/pkg/admin/service/reconciliation_running.go:105`) và bước đặt `completed` vô điều kiện (:108-115), thay bằng `verifyRunTotals`.
- Trong transaction chỉ dùng writer chặt `CashFlow().AppendStrict(sc, entries)`: chỉ insert, trả lỗi thật, từ chối `idemKey` rỗng, không gọi `UpdateStatistic`, không gọi `GetRemaining` ngoài session. `AddCashFlow` không được nhận `SessionContext`: hàm này bỏ qua lỗi insert, và `UpdateStatistic` chạy 6 goroutine dùng chung một `ctx`, trong khi session của driver không an toàn khi dùng đồng thời.
- `AppendStrict` điền `oldBalance/newBalance` bằng Σ đọc trong session. Hai trường chỉ để hiển thị, như hiện nay; UI đang ẩn (`frontend/src/pages/bank/components/withdraw-history/index.tsx:28-31`).
- Hoa hồng người giới thiệu theo mẫu outbox (§7.1 bước 6).

Hệ quả
- (+) Bảo toàn tiền theo từng khoản cho mọi partner bật cờ. Duyệt lại đưa được kỳ từ `run_failed` về `completed`.
- (−) Đổi hành vi đường creator, đảo Nguyên tắc 2 của v1.0 (§11.1, §14.2). Cần chạy hồi quy trên partner không có MCN trước khi bật cờ.
- (−) Thêm một trạng thái kỳ (`run_failed`) ở admin, lệch D8 và BA-04 (§14.3).

### ADR-08. Chi trả cho MCN

Bối cảnh: hiện trạng đợt chi ở §2.4. Mọi bước khóa theo `withdraw.User`; điều kiện chi là điều kiện cá nhân. Ràng buộc một đợt mở mỗi partner chỉ là check-then-insert, không có ở DB. `mcn-cash-flows` chỉ ghi thêm, nên hai transaction chèn hai dòng khác nhau không gây write conflict (write skew).

| Tiêu chí | A. Qua user vận hành + `TaxExempt` (v1.0) | B. `withdraws.payeeType=mcn` | C. `mcn-payouts`, giữ tiền ở Lấy danh sách | D. `mcn-payouts`, trừ sổ MCN ở Chuyển tiền, kiểm số dư trong transaction |
|---|---|---|---|---|
| Đúng payee | Sai khi dùng chung tài khoản | Đúng | Đúng | Đúng |
| Failure mode khi thiếu một nhánh | – | Fail-open: `AddCashFlow(user rỗng)`, sổ MCN không bị trừ, đợt sau chi trùng | Fail-closed | Fail-closed nhờ INV-14 |
| Chi vượt số dư khi có hai đợt mở hoặc điều chỉnh âm xen giữa | Có | Có | Có | Không |
| Hủy đợt từ processed | Đúng | Đúng | Phải nhả bút toán giữ | Đúng: chưa có bút toán |
| Ảnh hưởng đường creator | Sửa lõi | Rẽ nhánh ở mọi file đọc `withdraws` | Chỉ thêm lời gọi | Chỉ thêm lời gọi |

Quyết định: D. Luồng ở §7.2. Khuyến nghị thêm partial unique `transfers(partner)` `{isOpen:true}` (trường mới, `false` khi `finished` hoặc `rejected`) để khóa "một đợt mở" ở DB.

Phương án dự phòng nếu team ưu tiên tái sử dụng `withdraws` là B, kèm bốn điều kiện:

- `WithdrawRaw.User` thành con trỏ hoặc có `omitempty`; `withdraws.mcn` có `omitempty`.
- Constructor kiểm `payeeType=mcn ⇒ user=nil ∧ mcn≠nil`.
- `AddCashFlow` trả lỗi khi user rỗng.
- Test rà mọi file đọc `withdraws`.

Hệ quả
- (+) Code chi creator không đọc thấy lệnh MCN. Đổi tài khoản ngân hàng sau khi tạo lệnh không ảnh hưởng lệnh đó.
- (−) Màn Xử lý rút tiền cần khối MCN (danh sách, loại lệnh, thống kê).

### ADR-09. Thuế TNCN khi chi

Bối cảnh
- Khấu trừ chỉ ở `backend/internal/service/withdraw.go:136-139`, theo từng lệnh, không có loại người nộp thuế hay loại thu nhập.
- Đã chốt (D21, 05/11): 10% trên số chi sau phí, ngưỡng 5.000.000đ mỗi đợt; MCN công ty không khấu trừ. MCN cá nhân tạm khấu trừ như KOL/KOC (Q9, chờ Kế toán).
- Ở v2.0, tách sổ làm thuế khác so với khi MCN cá nhân chỉ dùng một tài khoản (PRD Q12). Ví dụ P có phí 3.000.000 và thu nhập creator 2.500.000. Gộp một lệnh 5.500.000, áp `pit_10` thì khấu trừ 550.000. Tách hai lệnh theo payee thì cả hai dưới ngưỡng, khấu trừ 0. (v1.0 ở §2.7 cũng một lệnh nhưng `TaxExempt`, nên thuế 0.)
- Họp 10/11 gọi đúng rủi ro này là chia nhỏ dưới 5.000.000đ để lách TNCN [seg-065-073, seg-079-089] và chốt gộp một lần qua tài khoản nhà 100% (ADR-12).
- Lệnh MCN tách theo chiến dịch (ADR-14) lại sinh nhiều lệnh nhỏ cho cùng một payee trong một đợt.

| Tiêu chí | A. Theo user + `TaxExempt` (v1.0) | B. Theo payee, ngưỡng từng lệnh | C. Theo người nộp thuế, gộp ngưỡng trong đợt | D. Lũy kế theo tháng |
|---|---|---|---|---|
| Khớp D21, BA-04 | Không | Có | Có | Không |
| Thuế bằng khi gộp một lệnh (ví dụ P ở trên) | – | Không | Có | – |
| Ảnh hưởng creator không thuộc MCN | Không | Không | Có thể (creator trùng CCCD với MCN cá nhân) | Cao |
| Phụ thuộc chất lượng CCCD | Không | Không | Có (`users.contract` tự khai; eKYC của AT chưa có API) | Có |
| Khối lượng | Thấp | Thấp | Trung bình: gom nhóm, tính lại khi loại lệnh, phân bổ làm tròn | Cao |

Quyết định: lệnh creator xét ngưỡng từng lệnh như hiện nay (B). Lệnh MCN cộng `cash` mọi lệnh của cùng MCN trong đợt rồi mới so ngưỡng, không gộp với lệnh creator cùng CCCD.
- `TaxPolicyFor(payee)` thay đoạn inline; kết quả với creator giống hệt code cũ (test hồi quy).
- Mỗi lệnh snapshot `taxpayerKey`, `incomeType`, `policy`, `base`, `rate`, `threshold`, `amount`, `ruleVersion`. File ngân hàng có cột `taxpayerKey` để Kế toán tự tổng hợp.
- Thu nhập nội dung của tài khoản nhà: payee là MCN, ghi vào sổ MCN như phí, khấu trừ theo loại MCN (ADR-12). Bỏ phương án payee là user của v2.0.
- Lệnh MCN cá nhân: ngưỡng và thuế tính trên `groupBase` (§7.2 bước 6), rồi chia về từng lệnh theo tỷ lệ `cash` (largest remainder). Gom nhóm chỉ trong một `mcns`, không theo CCCD, nên không chạm creator.
- Phase 1 không gộp ngưỡng thuế theo CCCD giữa lệnh MCN và lệnh creator (C đầy đủ, NG-6). Sau khi tài khoản nhà ký phụ lục 100%, thu nhập nội dung vào sổ MCN, nên phần lớn ca P không còn. Lệnh creator còn lại (thu nhập trước khi kích hoạt phụ lục, chiến dịch trước mốc, người chưa ký 100%) xét ngưỡng riêng; Kế toán tổng hợp theo `taxpayerKey`.

Hệ quả
- (+) Creator không thuộc MCN không đổi kết quả thuế (G-6). Không phụ thuộc CCCD tự khai.
- (+) Một MCN một lần quyết định thuế trong đợt, dù tách lệnh theo chiến dịch.
- (−) Loại một lệnh MCN thì nhóm đổi. Trước Chuyển tiền: tính lại thuế cả nhóm. Sau Chuyển tiền (ngân hàng trả về): đảo lệnh bị loại cùng phần thuế đã phân bổ cho nó. Thuế các lệnh còn lại giữ nguyên. Mọi lệnh cùng nhóm được đặt cờ `taxGroupBroken = true` (trường riêng của `mcn-payouts`, nằm ngoài `tax`) để Kế toán xử lý tay (§7.2 bước 7).
- (−) Thu nhập của tài khoản nhà phát sinh trước ngày ký phụ lục 100% vẫn đi lệnh creator, thuế riêng.

### ADR-10. Phạm vi cờ `PartnerOpts.McnEnabled`

| Tiêu chí | A. Chỉ lúc tạo hồ sơ (hiện tại) | B. Mọi điểm, kể cả trích phí và chi | C. Chỉ các bước onboarding |
|---|---|---|---|
| Chặn MCN mới khi tắt | Không đủ | Có | Có |
| Giữ tiền đang nợ MCN | Không | Có | Không |
| Thay đổi điều khoản phụ lục đã ký | Không | Có (thôi trích phí) | Không |

Quyết định: C. `Mcn().EnabledFor(partner)` kiểm ở tạo, sửa hồ sơ, kích hoạt, tạo link, xem lời mời, Agree, StartSign, Bind. Không kiểm ở `applyMcnFees` (phụ lục đã ký đang có hiệu lực), `generateMcnPayouts` và các màn xem. Lệch câu "chỉ áp dụng cho partner bật MCN" của FR-016 (§14.3).

Hệ quả: tắt cờ chỉ dừng onboarding; muốn dừng thu phí phải chấm dứt phụ lục. Bật cờ trên prod trước khi phase 5 và 6 lên là an toàn khi `MCN_FEE_EVENT_START_FROM` còn trống, vì `applyMcnFees` không tạo phần phí nào (ADR-13, §11.4).

### ADR-11. Điều chỉnh, bù thiếu, số dư âm

Bối cảnh: phase 1 không có báo sai đối soát; thiếu thì bù bằng Thưởng thêm kỳ sau (D7); Admin không thao tác thay MCN (D6).

| Tiêu chí | A. Thưởng thêm kèm `mcnFeeMode: exempt` | B. Thưởng thêm cho thu nhập gốc; script cho phí trích sai | C. UI điều chỉnh |
|---|---|---|---|
| Bảo toàn tiền | Không: hoàn phí cho KOL/KOC mà MCN vẫn giữ phí | Có, hai vế cùng transaction | Có |
| Khối lượng phase 1 | Thấp | Thấp | Cao |

Quyết định: B.
- Thưởng thêm chỉ dùng để bù thu nhập gốc; bị trích phí theo dòng quan hệ tại ngày tạo. Dùng Thưởng thêm để hoàn phí trích thừa sẽ bị trích phí lần nữa (hoàn 450.000 với tỷ lệ 15% thì KOL/KOC chỉ nhận 382.500).
- Phí trích sai xử lý bằng script `cmd/mcn-adjust` (runbook, không có UI): bắt buộc `ticket`, `reason`, `createdBy`, người duyệt, chế độ dry-run. Đây là năng lực ngoài D7, cần PO đồng ý (§14.3).
- Số dư MCN âm sau điều chỉnh không tự bù. MCN có bất kỳ chiến dịch nào `Balance(mcn, event) < 0` thì đợt chi không tạo lệnh nào cho MCN đó và gửi Telegram. Vận hành xử lý bằng `cmd/mcn-adjust` (ADR-14, §7.2 bước 3).

### ADR-12. Tài khoản nhà MCN và thu nhập nội dung của người đứng MCN

Bối cảnh
- Họp 10/11: người đứng MCN được làm creator trên cùng portal; "gộp thanh toán và tính thuế một lần, không tách riêng hai vai trò"; account nhà MCN đặt share 100% cho MCN để dồn chi về một mối, tránh hai lần chuyển dưới 5.000.000đ lách TNCN [seg-056-060, seg-065-073, seg-079-089].
- v2.0 làm ngược lại: thu nhập nội dung luôn thuộc user làm nội dung và đi lệnh creator. Tài khoản vận hành không được là thành viên MCN nào (mã `MCN_SELF_MEMBERSHIP`, nay đã bỏ). Vì vậy người đứng MCN có hai lệnh và hai lần xét ngưỡng, đúng tình huống họp 10/11 muốn bỏ.
- Trước commit `82edb83c7`, code nhánh chặn ở ba chỗ: trang mời trả `is_mcn_account` (`backend/pkg/public/service/mcn_invite.go:144, 174, 281`); tạo và kích hoạt MCN từ chối email của thành viên (`backend/pkg/admin/service/mcn_validate.go:71-81`); gắn tài khoản bỏ qua user đang là thành viên (`backend/internal/service/mcn.go:172-176`). Commit đó đã nới trang mời, Agree và Bind; việc còn lại ở §14.1 #22.

| Tiêu chí | A. Hai payee (v2.0) | B. Tài khoản nhà 100% qua link và phụ lục | C. Cộng thẳng vào sổ MCN theo vai đăng nhập (`mcn_self_content`, PRD Q8) |
|---|---|---|---|
| Khớp họp 10/11 | Không: hai lệnh, hai lần xét ngưỡng | Có | Có |
| Căn cứ chi thu nhập nội dung cho MCN | – | Phụ lục chỉ định thanh toán 100% gắn với ②, cùng mẫu với KOL/KOC | Không có văn bản riêng, dựa vào vai đăng nhập |
| Thay đổi sổ, đối soát | Không | Không: `applyMcnFees` tạo phần phí tỷ lệ 100% như mọi phần phí | `postItem` rẽ nhánh cộng tiền theo vai của `item.User` tại ngày phát sinh |
| Đổi người vận hành giữa kỳ | Không ảnh hưởng | Không ảnh hưởng: quan hệ gắn với user làm nội dung, không với vai vận hành | Phải chia khoản theo ngày đổi vai |
| Kênh khác do MCN sở hữu | Không xử lý | Cùng cơ chế (link 100%) | Không xử lý |
| Thay đổi code | – | Nới ba điểm chặn, thêm `house`, INV-19 | Rẽ nhánh ở lõi ghi sổ |

Quyết định: B.
- Tài khoản nhà là dòng `mcn-members` bình thường, `rate = 100`, `house = true`. Đi đúng luồng Agree → ký phụ lục → `active`. `applyMcnFees` tạo phần phí 100%: sổ creator `+G`, `−G`; sổ MCN `+G`. Không thêm action ghi sổ.
- Điều kiện để là tài khoản nhà: user là tài khoản vận hành của chính MCN, hoặc trùng CCCD với MCN cá nhân. `house` được đặt ở Agree; ở StartSign khi CCCD lúc Agree chưa xác định; hoặc lúc user được gắn làm tài khoản vận hành mà đã có dòng 100% với chính MCN đó (ADR-04, §6.2).
- Kênh khác do MCN sở hữu vào qua link 100% như KOL/KOC, `house = false`, kết quả tiền như nhau.
- Tài khoản vận hành chỉ được là thành viên của chính MCN mình (INV-03a). Đề xuất: phụ lục 100% vẫn yêu cầu eKYC và ② của người đứng sau tài khoản, chờ Legal ở OQ-08.
- Thu nhập phát sinh trước ngày ký phụ lục 100%, hoặc thuộc chiến dịch trước mốc áp dụng (ADR-13), đi lệnh creator như hiện nay.
- Có bắt buộc tài khoản vận hành ký phụ lục 100% trước chiến dịch đầu tiên không: OQ-15. Đề xuất: hệ thống không chặn; báo cáo vận hành liệt kê MCN có tài khoản vận hành phát sinh thu nhập creator mà chưa là tài khoản nhà.

Hệ quả
- (+) Một payee, một số dư, một lần quyết định thuế cho MCN kiêm creator; hết ca tách hai lệnh dưới ngưỡng giữa hai vai.
- (+) Không thêm nhánh ghi sổ; đúng cho cả MCN công ty và cá nhân.
- (−) Với MCN công ty, thu nhập nội dung của người vận hành thành doanh thu của pháp nhân, không khấu trừ TNCN. Cần Legal xác nhận phụ lục 100% đủ căn cứ (OQ-08, chưa chốt, hạn 17/11). Rà soát sâu để P2 theo họp 10/11 (NG-11).
- (−) Tài khoản nhà hiện trong danh sách thành viên của MCN; UI gắn nhãn "Tài khoản nhà".

### ADR-13. Mốc áp dụng theo chiến dịch

Bối cảnh
- Họp 10/11 [seg-024-031]: MCN chỉ áp cho chiến dịch mới, từ tháng sau go-live; go-live cuối tháng 11 thì từ tháng 12. "Campaign" là chiến dịch (`events`), chốt 11/11.
- Mọi khoản đối soát xác định được chiến dịch: `event-rewards.event` (`backend/internal/model/mg/event_reward.go:23`), `event-bonus.event` (`backend/internal/model/mg/event_bonus.go:14`). Ngày bắt đầu chiến dịch là `events.startAt` (`backend/internal/model/mg/event.go:33`).

| Tiêu chí | A. `events.startAt ≥ mốc`, mốc là cấu hình | B. Cờ `events.mcnApplicable`, Admin bật từng chiến dịch | C. Ngày phát sinh ≥ mốc |
|---|---|---|---|
| Khớp "chỉ chiến dịch mới" | Có | Có | Không: chiến dịch đang chạy qua mốc vẫn bị trích |
| Vận hành | Không thao tác | Bật từng chiến dịch; quên bật là mất phí | Không thao tác |
| Đổi điều kiện chiến dịch đang chạy | Không thể | Bật, tắt giữa chừng được | – |
| Code | Lọc một chỗ | Thêm trường, UI admin | Lọc một chỗ |

Quyết định: A.
- ENV `MCN_FEE_EVENT_START_FROM` (ngày, giờ Asia/Ho_Chi_Minh). Trống nghĩa là chưa áp dụng: `applyMcnFees` không tạo phần phí nào. Mốc đã đặt mà partner chưa bật `LedgerV2` thì `applyMcnFees` báo lỗi, kỳ giữ `processing` (ADR-07).
- `applyMcnFees` bỏ qua item thuộc chiến dịch có `startAt` trước mốc; mốc snapshot lên `mcnSnapshot.eventStartFrom` (INV-20). Đổi ENV sau đó không đổi kỳ đã `processed`.
- Mốc áp dụng chung cho cả tài khoản nhà (ADR-12).

Hệ quả
- (+) Chiến dịch đang chạy lúc go-live giữ nguyên điều khoản với KOL/KOC.
- (−) KOL/KOC đã ký nhưng chỉ có thu nhập từ chiến dịch cũ thì MCN chưa có phí. Màn mời và màn MCN ghi rõ "Phí áp dụng cho chiến dịch bắt đầu từ 01/12/2026".

### ADR-14. Lệnh chi MCN theo chiến dịch

Bối cảnh
- Họp 10/11 [seg-091-101]: Kế toán chi theo từng chiến dịch, không gộp nhiều chiến dịch vào một lần chi.
- Hiện trạng: đợt chi `transfers` lọc theo partner và khoảng ngày (`backend/internal/model/mg/transfer.go:41-46`), rút cả số dư. Số dư creator cộng dồn mọi chiến dịch. Bút toán cộng tiền mang `options.event` (`backend/internal/model/mg/cash_flow.go:33`); bút toán chi `withdraw` không mang.

| Tiêu chí | A. Chỉ lệnh MCN theo chiến dịch | B. Mọi lệnh, creator và MCN, theo chiến dịch | C. Một lệnh mỗi MCN mỗi đợt (v2.0) |
|---|---|---|---|
| Khớp họp 10/11 | Cho MCN | Đủ | Không |
| Ảnh hưởng creator không thuộc MCN | Không (G-6) | Có: `withdraws`, FIFO theo chiến dịch, file ngân hàng, thuế | Không |
| Sổ | `mcn-cash-flows.event` bắt buộc; `Balance(mcn, event)` | Thêm `event` cho bút toán chi creator; số dư theo (user, chiến dịch) | Như v2.0 |
| Ngưỡng thuế | Tổng lệnh của MCN trong đợt (ADR-09) | Gộp theo payee trong đợt cho mọi creator | Một lệnh |
| Khối lượng | Thấp, sổ MCN là sổ mới | Cao, ngoài phase 1 | Không |

Quyết định: A. Đây là đề xuất của team, chờ PO và Kế toán chốt ở OQ-13.
- Mọi bút toán `mcn-cash-flows` có `event`: phí lấy chiến dịch của item; chi lấy chiến dịch của lệnh; điều chỉnh bắt buộc chỉ định. `Balance(mcn, event) = Σ value` theo (MCN, chiến dịch), đọc bằng `McnLedger().EventBalance`. `Balance(mcn)` là tổng mọi chiến dịch.
- `generateMcnPayouts` tạo một lệnh draft cho mỗi (transfer, mcn, event) có `Balance(mcn, event) > 0`. Unique `(transfer, mcn, event)` thay cho `(transfer, mcn)` (INV-12).
- Min so với tổng `Balance(mcn)`. Nếu tổng số chi vượt Max thì xếp chiến dịch theo `events.startAt` tăng dần và cấp đủ từng chiến dịch tới khi chạm Max. Chiến dịch chạm Max chỉ nhận phần còn lại. Các chiến dịch sau chờ đợt sau.
- INV-14 kiểm `Balance(mcn, event) ≥ cash` trong transaction, vẫn khóa bằng `$inc mcns.ledgerVer`.
- MCN có bất kỳ chiến dịch nào `Balance(mcn, event) < 0` thì đợt chi không tạo lệnh nào cho MCN đó và gửi Telegram. Vận hành xử lý bằng `cmd/mcn-adjust` (ADR-11). Lý do: chiến dịch âm không được bù bằng chiến dịch khác, và nếu vẫn chi các chiến dịch dương thì tổng chi lớn hơn `Balance(mcn)`.

Hệ quả
- (+) Kế toán đối chiếu từng chiến dịch với ADV; creator không đổi.
- (−) Nhiều lệnh nhỏ cho cùng một TK MCN: phí chuyển khoản tính theo lệnh, file ngân hàng thêm cột chiến dịch. Cần Kế toán chấp nhận (OQ-13, chưa chốt).
- (−) Ngưỡng thuế phải xét theo nhóm lệnh (ADR-09), thêm bước tính thuế nhóm trước Chuyển tiền.

## 6. Mô hình dữ liệu

### 6.1 Collection MCN hiện có

| Collection | Model | Trường chính, ràng buộc | Thay đổi trong bản này |
|---|---|---|---|
| `mcns` | `backend/internal/model/mg/mcn.go:23-43` | `partner`; `type` company \| individual; `name` (so tên chủ TK); `identityNumber` unique (MST 10/13 số, CCCD 12 số); `loginEmail` unique; `status` pending \| active; `phone` | Thêm `ledgerVer int64` (chỉ `$inc`). Khóa `type`, `identityNumber` sau `active`, chỉ đổi qua script có ticket. Đổi `name` sau `active` thì đặt `bank.match = unverified` của TK hiện hành; lệnh chi yêu cầu `mismatchReason` |
| `mcn-accounts` | `backend/internal/model/mg/mcn.go:53-64` | `mcn`, `email` (lowercase), `user` (có khi đã gắn), `status` invited \| active | Thêm `isCurrent` (⇔ `status ∈ {invited, active}`, cập nhật trong cùng lệnh với `status`), status `revoked`, `revokedAt/By`, `history[]` |
| `mcn-documents` | `backend/internal/model/mg/mcn.go:68-95` | `kind` identity \| contract \| dpa \| bank \| policy; `isCurrent` đổi trong transaction (`backend/pkg/admin/service/mcn_document.go:63-66`); `bank.match` ok \| mismatch \| unverified, khác `ok` bắt buộc lý do | Không. Lệnh chi chép bản `bank` hiện hành |
| `mcn-invite-links` | `backend/internal/model/mg/mcn_member.go:19-30` | `code` unique; `rate` 0..100 (`backend/internal/constants/mcn.go:67-68`); `status` active \| off, một chiều | Không |

### 6.2 `mcn-members` (`backend/internal/model/mg/mcn_member.go:43-80`)

| Trường | Kiểu | Ràng buộc | Ghi chú |
|---|---|---|---|
| `mcn`, `user`, `link` | ObjectID | Bắt buộc | |
| `rate` | int | 0..100, snapshot từ link lúc đồng ý | Không đổi |
| `status` | string | §6.7 | |
| `isMember`, `isPending` | bool | `isMember` ⇔ `status ∈ {active, leaving}`; `isPending` ⇔ `status = agreed` | `isPending` mới |
| `annexInFlight` | bool | true từ CAS `annex.state: none → creating` tới khi dòng rời `agreed` | Mới, INV-05 |
| `annex.state`, `annex.signedAt`, `annex.signedAtSource` | string, Date, string | `state`: none \| creating \| created; `signedAtSource`: econtract \| sync \| sync_capped | Mới. `signedAt` lấy giờ ký từ econtract nếu có (OQ-05) |
| `startAt`, `endAt` | Date | `startAt = annex.signedAt`; `endAt = startAt + 12 tháng` | Có, sửa nguồn |
| `activatedAt`, `feeFrom` | Date | Ghi một lần khi `agreed → active`; `feeFrom = startOfDayHCM(activatedAt)` | Mới |
| `leaveEffectiveAt`, `endedAt`, `endReason` | Date, Date, string | Có sẵn (`backend/pkg/public/service/mcn_leave.go:68, 121-140`; `backend/pkg/public/service/mcn_member.go:165-166`) | Nguồn của `FeeWindow` |
| `signedAfterClose`, `selfCheck` | bool, string | `signedAfterClose`: phụ lục SIGNED khi dòng đã `declined`, `sign_expired`, `superseded`. `selfCheck`: ok \| unresolved | Mới. `selfCheck` là kết quả so CCCD của user với `mcns.identityNumber` (MCN cá nhân) lúc Agree. `unresolved` nghĩa là user chưa có CCCD; StartSign so lại (ADR-04) |
| `house` | bool | `house ⇒ rate = 100` (INV-19). Chỉ đổi từ false sang true | Mới, ADR-12. Đặt ở một trong ba lúc: Agree; StartSign khi `selfCheck = unresolved` và lần so lại khớp CCCD (link dưới 100% thì từ chối `MCN_HOUSE_RATE_REQUIRED`); Bind hoặc Admin Activate khi user được gắn làm tài khoản vận hành mà đã có dòng 100% với chính MCN này. Từ StartSign trở đi, chỉ bước gắn tài khoản vận hành còn đặt được `house` |
| `declinedByCode` | bool | true cho dòng tạo khi KOL/KOC bấm Từ chối ngay trên trang mời mà chưa từng Đồng ý | Mới. Dùng cho partial unique `uniq(user, link)` (§6.6) |

### 6.3 `mcn-cash-flows` (mới, append-only)

| Trường | Kiểu | Ràng buộc | Ghi chú |
|---|---|---|---|
| `mcn` | ObjectID | Bắt buộc | MCN sở hữu dòng tiền |
| `partner` | ObjectID | Chép từ `mcns.partner` | Chỉ để lọc |
| `event` | ObjectID | Bắt buộc với mọi action | Chiến dịch; số dư tính theo (mcn, event) (ADR-14) |
| `action` | string | `mcn_fee` \| `withdraw` \| `tax` \| `withdraw_fee` \| `withdraw_reversal` \| `adjustment` | |
| `reversalOf` | string | Chỉ với `withdraw_reversal`: `withdraw` \| `tax` \| `withdraw_fee` | Thuế khấu trừ ròng = Σ`tax` + Σ`withdraw_reversal{reversalOf: tax}` |
| `value` | int64 | Khác 0; dấu khớp action | Dương là cộng vào số dư MCN (`mcn_fee`, `withdraw_reversal`), âm là trừ (`withdraw`, `tax`, `withdraw_fee`). `adjustment` mang dấu theo chiều điều chỉnh |
| `idemKey` | string | Bắt buộc, không rỗng, unique | §7.1, §7.2, §7.5 |
| `source` | object | Chỉ với `mcn_fee` | `{reconciliation, reconciliationItem, member, koc, rate, baseCash, windowFrom, windowTo}` |
| `payout`, `transfer`; `adjustment` | ObjectID; object | Chỉ với action chi; chỉ với `adjustment` | `adjustment`: `{ticket, seq, reason, approvedBy}` |
| `createdBy`, `createdAt` | object, Date | `createdBy` bắt buộc: `{type: system \| staff \| script, id}` | Ngày cộng hiển thị lấy `reconciliations.completedAt`, không lấy `createdAt` |

### 6.4 `mcn-payouts` (mới)

| Trường | Kiểu | Ràng buộc | Ghi chú |
|---|---|---|---|
| `transfer`, `partner`, `mcn`, `event` | ObjectID | `uniq(transfer, mcn, event)` | Một lệnh mỗi chiến dịch (ADR-14) |
| `cash`, `cashTax`, `bankFee`, `actualCash` | int64 | `cash > 0`; `actualCash = cash − cashTax − bankFee ≥ 0` | |
| `status` | string | draft \| transferring \| completed \| rejected (§6.7) | |
| `declined`, `declinedReason`, `rejectReason` | bool, string, string | `rejectReason`: `transfer_rejected` \| `insufficient_balance` \| `transfer_failed` \| `declined` \| `declined_after_transfer` | `transfer_rejected`: Hủy đợt. `insufficient_balance`: thiếu số dư lúc Chuyển tiền. `transfer_failed`: Chuyển tiền lỗi, lệnh còn `draft` tới Hoàn tất. `declined`: lệnh bị loại khi còn `draft`, tới Hoàn tất. `declined_after_transfer`: lệnh bị loại sau Chuyển tiền (ngân hàng trả về) |
| `bank` | object | Snapshot lúc tạo lệnh | `{document, bankId, bankName, accountNumber, holderName, match, mismatchReason}` |
| `payee` | object | Snapshot lúc tạo lệnh | `{type: company \| individual, name, identityNumber, phone, contractSignedAt}` |
| `tax` | object | Snapshot ở bước thuế nhóm (INV-17) | `{policy, incomeType, taxpayerType, taxpayerKey, base, groupBase, rate, threshold, amount, ruleVersion, computedAt}`. `groupBase`: tổng `cash` các lệnh `draft` chưa bị loại của MCN đó trong đợt (§7.2 bước 6) |
| `taxGroupBroken` | bool | Nằm ngoài `tax`, để không trái INV-17 | Đặt lên mọi lệnh cùng nhóm khi một lệnh trong nhóm bị loại sau Chuyển tiền, hoặc bị `rejected` (`insufficient_balance`, `transfer_failed`) sau khi thuế nhóm đã chốt. Kế toán xử lý tay (§7.2 bước 7, 8, 10) |
| `history[]`, `createdAt`, `updatedAt` | array, Date | | `history`: `{status, at, byType, by, note}` |

### 6.5 Collection hiện có được sửa

| Collection | Thêm hoặc đổi | Ràng buộc |
|---|---|---|
| `users` | `mcnGuardVer int64`, chỉ `$inc` | – |
| `reconciliations` | `completedAt`; `mcnSnapshot{status: pending \| done \| failed, items, splits, totalFee, eventStartFrom, at}` | `completedAt` ghi cùng CAS `running → completed` |
| `reconciliation-items` | `mcnSplits[]{member, mcn, rate int32, baseCash int64, fee int64, windowFrom, windowTo, rewardCount}`; `mcnFee int64`; `netCash float64`; `mcnEvaluatedAt`; `postedAt`; `referral{state: pending \| sent, base, sentAt}` | `mcnSplits` không đổi sau `processed`; `totalCash = netCash + mcnFee` |
| `cash-flows` | `idemKey string` với `bson:"idemKey,omitempty"`; action `mcn_fee`, `mcn_fee_adjustment`; `options.{mcn, mcnMember, rate}` | Mỗi khóa ghi một lần; không có chuỗi rỗng |
| `withdraws` | `tax` (snapshot), `incomeType` (mặc định `creator_reward`); giữ `cashTax` | Snapshot không đổi sau draft |
| `users.statistic`, `user-partners.statistic` | `totalCashMcnFee = −Σ value(mcn_fee) − Σ value(mcn_fee_adjustment)` | Tính trong `UpdateStatistic` và `UpdateUserPartnerStatistic`, nếu không sẽ bị `$set` đè. Chỉ để hiển thị |
| `transfers` | `isOpen bool` (khuyến nghị, ADR-08) | |

Số dư creator luôn là `cashRemaining = Σ value(cash-flows)` theo user. Test đối chiếu dùng đẳng thức theo action: `cashRemaining = Σ event_* + Σ mcn_fee + Σ mcn_fee_adjustment + Σ withdraw + Σ tax + Σ withdraw_fee + Σ tax_refund`. Mỗi tổng có dấu và đã gồm bút toán đảo, vì bút toán đảo giữ action (`backend/pkg/admin/service/transfer_finish.go:64-107`). `CashTotal` không tham gia vì gồm cả thưởng pending và rejected (`backend/internal/service/user.go:270`).

### 6.6 Index

| Collection | Index | Mục đích |
|---|---|---|
| `mcn-cash-flows` | `uniq(idemKey)`; `(mcn, event, createdAt)`; `(source.reconciliation, mcn)`; `(payout)` | INV-12; số dư theo chiến dịch, lịch sử; đối chiếu kỳ; đối chiếu lệnh |
| `mcn-payouts` | `uniq(transfer, mcn, event)`; `(mcn, -createdAt)`; `(transfer, status)` | Một lệnh mỗi (MCN, chiến dịch) mỗi đợt |
| `cash-flows` | `uniq(idemKey)` partial `{idemKey:{$exists:true}}` | Không vướng dữ liệu cũ |
| `reconciliation-items` | `(mcnSplits.mcn, reconciliation)` multikey | Màn đối soát MCN |
| `mcn-members` | Mới: `uniq(user, mcn)` partial `{isPending:true}`; `uniq(user)` partial `{annexInFlight:true}`; `uniq(user, link)` partial `{declinedByCode:true}`: chỉ áp cho dòng tạo khi KOL/KOC bấm Từ chối ngay trên trang mời mà chưa từng Đồng ý. Dòng đi `agreed → declined` không đặt cờ này, nên không vi phạm unique. Giữ: `uniq(user)` partial `{isMember:true}` và 5 index thường (2 tra cứu, 3 theo hạn) ở `backend/internal/module/database/mongodb/index.go:469-474` | INV-01, INV-02, INV-05; Từ chối trên trang mời là upsert theo (user, link) |
| `mcn-accounts` | `uniq(mcn)` partial `{isCurrent:true}`; `uniq(user)` partial `{isCurrent:true, user:{$exists:true}}` thay index ở `backend/internal/module/database/mongodb/index.go:453`; giữ `uniq(email)` partial `{status:"invited"}` | INV-04 |
| `transfers` | `uniq(partner)` partial `{isOpen:true}` (khuyến nghị) | Một đợt mở mỗi partner |

### 6.7 Máy trạng thái

MCN, tài khoản vận hành (`isCurrent` đúng ở `invited`, `active`) và link mời. Phase 1 chưa có thao tác Tạm dừng hay Chấm dứt cả MCN. Việc MCN chấm dứt quan hệ với một KOL/KOC nằm ở sơ đồ dòng quan hệ bên dưới.

```mermaid
stateDiagram-v2
  state "mcns" as M {
    [*] --> pending : Admin tạo hồ sơ
    pending --> active : Kích hoạt khi đủ 5 hồ sơ
  }
  state "mcn-accounts" as A {
    [*] --> invited : Kích hoạt, chưa có user hợp lệ
    [*] --> bound : Kích hoạt, gắn ngay user qua guard
    invited --> bound : Đăng nhập, email khớp, qua guard
    invited --> revoked : Script đổi email
    bound --> revoked : Script đổi người vận hành
  }
  state "mcn-invite-links" as L {
    [*] --> on : MCN tạo link, rate 0..100
    on --> off : MCN tắt link, một chiều
  }
```

Trong sơ đồ, `bound` là `status = active` của `mcn-accounts`, `on` là `status = active` của link (đổi tên để không trùng trạng thái của `mcns`).

Dòng quan hệ (`mcn-members`). Mọi bước chuyển là CAS theo trạng thái nguồn; bước ra khỏi `agreed` đặt `isPending=false`, `annexInFlight=false` trong cùng lệnh.

```mermaid
stateDiagram-v2
  [*] --> agreed : Đồng ý lời mời
  [*] --> declined : Từ chối trên trang mời (upsert)
  agreed --> declined : KOL/KOC từ chối
  agreed --> sign_expired : Quá hạn, econtract chưa SIGNED
  agreed --> superseded : Đã ký với MCN khác
  agreed --> active : Phụ lục SIGNED, ghi activatedAt, feeFrom
  active --> leaving : Báo rời
  leaving --> active : Rút lại trước ngày hiệu lực
  leaving --> ended : Tới ngày rời, MCN chấm dứt quan hệ hoặc hết 12 tháng
  active --> ended : MCN chấm dứt quan hệ hoặc hết 12 tháng
  ended --> [*]
```

Kỳ đối soát (`reconciliations`). `run_failed` là trạng thái mới về mặt ghi; Hủy từ `run_failed` bị chặn (INV-16).

```mermaid
stateDiagram-v2
  [*] --> pending : Admin tạo kỳ
  pending --> processing : Lấy danh sách
  processing --> processed : Gom xong, mcnSnapshot done
  pending --> rejected : Hủy
  processing --> rejected : Hủy
  processed --> rejected : Hủy
  processed --> running : Duyệt tất cả
  running --> completed : verifyRunTotals đạt
  running --> run_failed : Lệch, lỗi hoặc panic
  run_failed --> running : Duyệt lại
  completed --> [*]
  rejected --> [*]
```

Lệnh chi MCN (`mcn-payouts`).

```mermaid
stateDiagram-v2
  [*] --> draft : Lấy danh sách đợt chi
  draft --> rejected : Hủy đợt, thiếu số dư, Chuyển tiền lỗi, bị loại
  draft --> transferring : Chuyển tiền, trừ sổ MCN
  transferring --> completed : Hoàn tất
  transferring --> rejected : Hoàn tất với lệnh bị loại, ghi đảo
  completed --> [*]
  rejected --> [*]
```

### 6.8 Luồng onboarding và điểm guard

```mermaid
sequenceDiagram
  autonumber
  actor K as KOL/KOC
  participant S as Public service
  participant DB as MongoDB
  participant E as Econtract (AT core)
  K->>S: Agree(code)
  S->>DB: Tx: $inc users.mcnGuardVer, tài khoản vận hành chỉ nhận link 100% của chính MCN mình (đặt house = true), insert agreed (uniq isPending)
  K->>S: StartSign
  S->>DB: Tx: $inc mcnGuardVer, kiểm guard, CAS annex none→creating, annexInFlight=true (uniq user)
  S->>E: CreateAnnex (ngoài transaction)
  E-->>S: contractId, link
  S->>DB: CAS annex creating→created
  K->>E: Ký phụ lục
  S->>E: AnnexStatus (SyncSign, job McnSyncAnnex, hoặc McnExpireSign trước khi hết hạn)
  alt SIGNED
    S->>DB: Tx: $inc mcnGuardVer, kiểm guard, CAS agreed→active, ghi activatedAt, feeFrom, agreed khác→superseded
  else Quá hạn và chưa ký
    S->>DB: CAS agreed→sign_expired, annexInFlight=false
  end
```

SIGNED phát hiện sau hạn ký: kích hoạt với `signedAt = min(giờ đồng bộ, signDeadline)`, `signedAtSource = sync_capped`.

Phía người vận hành, Admin Activate (khi gắn ngay) và `BindAccountOnLogin` chạy trong transaction có `$inc users.mcnGuardVer`. Không gắn khi user có dòng `agreed`, `active` hoặc `leaving` với MCN khác (INV-03b). User có dòng với chính MCN này: `rate = 100` thì gắn và đặt `house = true` cho dòng đó; dưới 100% thì không gắn (INV-03a).

## 7. Luồng tiền

### 7.1 Đối soát

`applyMcnFees` chạy ở bước Lấy danh sách, ghi `mcnSplits`, `mcnFee`, `netCash`, `mcnEvaluatedAt` lên item `pending`, rồi `mcnSnapshot.status = done`. Sau `processed` không ghi lại. Item thuộc chiến dịch có `events.startAt` trước `MCN_FEE_EVENT_START_FROM` (hoặc mốc trống) chỉ ghi `mcnEvaluatedAt`, không có phần phí (ADR-13, INV-20).

Cửa sổ phí của dòng quan hệ m, giờ Asia/Ho_Chi_Minh, nửa mở `[feeFrom, effTo)`:

```
feeFrom(m) = startOfDayHCM(m.activatedAt)                     // ghi một lần
effTo(m)   = startOfDayHCM(m.endedAt)                         nếu status = ended
           = min(startOfDayHCM(m.endAt), m.leaveEffectiveAt)  nếu status = leaving
           = startOfDayHCM(m.endAt)                           nếu status = active
// endedAt: KOL/KOC rời = leaveEffectiveAt (00:00, ngày báo + 15);
//          MCN chấm dứt quan hệ = thời điểm chấm dứt; hết 12 tháng = endAt.
//          Ngày kết thúc không tính phí (D19, D20).
```

`endAt`, `leaveEffectiveAt` và thời điểm MCN chấm dứt quan hệ đều được ghi ngay khi sự việc xảy ra, không chờ job `McnEndMembers`. Vì vậy phí của kỳ không phụ thuộc lúc job chạy (G-4). Các mốc này luôn rơi vào ngày ghi hoặc sau đó, nên không đổi phí của kỳ đã Lấy danh sách. Trường hợp duy nhất bị ảnh hưởng: MCN chấm dứt quan hệ trong ngày D, kỳ có `toAt` bằng ngày D bị Hủy rồi Lấy danh sách lại sau lúc chấm dứt. Lần lấy lại không còn phí của ngày D.

Công thức cho item i và phần phí j (phần phí của một dòng quan hệ trên item, lưu ở `mcnSplits`):

```
R_i      = { r ∈ event-rewards : điều kiện của item i ∧ r.status = pending }   // reconciliation_running.go:411-415
           (item Thưởng thêm: chính khoản event-bonus của item)
D(r)     = startOfDayHCM(r.date)          // thưởng view, thưởng mốc
         = startOfDayHCM(bonus.createdAt) // Thưởng thêm
R_ij     = { r ∈ R_i : feeFrom_j ≤ D(r) < effTo_j }
fee_r    = min( roundHalfUp(cash_r × rate_j / 100), floor(cash_r) )  // từng khoản, FR-016; netCash ≥ 0 cả khi 100%
base_j   = Σ cash_r,  r ∈ R_ij
fee_j    = Σ fee_r,   r ∈ R_ij
mcnFee_i = Σ_j fee_j
netCash_i = totalCash_i − mcnFee_i
Kiểm: Σ_{r ∈ R_i} cash_r = totalCash_i ;  Σ_j base_j ≤ totalCash_i
```

Ghi sổ lúc Duyệt, `postItem(item)` trong `RunInTransaction`:

1. CAS `reconciliation-items{_id, status: pending} → completed`, đặt `postedAt`. Không khớp thì abort, trả `ErrAlreadyPosted`.
2. `validateItem` dùng chung cho mọi loại item: content còn `approved`; lượt xem được thưởng khớp (`backend/pkg/admin/service/reconciliation_running.go:339, 382`); Thưởng thêm còn `approved`, đúng số tiền, `bonusMatchesItem` (:500-512); Σ`cash_r` bằng `totalCash`; tính lại `base_j` của từng phần phí từ reward hiện tại và so với `mcnSplits[].baseCash` đã lưu. Lệch thì abort; ngoài transaction CAS item `pending → rejected` kèm ghi chú như nhánh mismatch hiện có.
3. CAS reward `{_id ∈ R_i, status: pending} → completed`, yêu cầu số dòng đổi bằng `|R_i|`; Thưởng thêm CAS `approved → completed`.
4. `cash-flows`: `+totalCash`, action như hiện nay, khóa `rc:<itemId>:credit`.
5. Mỗi phần phí có `fee_j > 0`: `cash-flows{mcn_fee, −fee_j}` và `mcn-cash-flows{mcn_fee, +fee_j}`, cùng khóa `rc:<itemId>:fee:<relId>`.
6. User có người giới thiệu hợp lệ (tạo dưới 6 tháng, có `referrerInfo.referrer`): ghi `referral{state: pending, base: totalCash}` lên item.
7. Commit. Sau commit, ngoài transaction và idempotent: content-analytic, `UpdateStatistic`, thông báo (số cộng vào số dư là `netCash`).

`RunInTransaction` tự chạy lại khi `WriteConflict` (ví dụ crawler ghi cùng reward). Hết số lần thử thì item giữ `pending`, phép kiểm E1 (không còn item `pending`) không đạt.

Kết kỳ, `verifyRunTotals(rc)` chạy bốn phép kiểm E1–E4:

| Kiểm | Điều kiện |
|---|---|
| E1 | Không còn item `pending` |
| E2 | Mỗi item completed có phần phí: `−Σ cash-flows(mcn_fee) = Σ mcn-cash-flows(mcn_fee) = item.mcnFee` |
| E3 | Mỗi item completed có đúng một dòng `rc:<itemId>:credit`, giá trị bằng `totalCash` |
| E4 | Item không ở trạng thái `completed` (`pending`, `rejected`) không có bút toán `rc:<itemId>:*` nào trên `cash-flows` và `mcn-cash-flows` |

Đạt thì CAS `running → completed`, ghi `completedAt`. Không đạt, lỗi hoặc panic thì CAS `running → run_failed` và gửi Telegram. Duyệt lại từ `run_failed` chỉ xử lý item còn `pending`. E2–E4 không đạt nghĩa là dữ liệu bất thường; xử lý bằng script sửa có dry-run và ticket (ghi bù hoặc đảo theo `idemKey`).

Hiệu lực của bút toán: mỗi item được cộng vào số dư ngay khi transaction của item đó commit, không chờ cả kỳ `completed`. Vì vậy kỳ dừng giữa chừng vẫn có item đã vào số dư. Ngày cộng hiển thị cho KOL/KOC và MCN vẫn là `reconciliations.completedAt`. Để không chi tiền của kỳ chưa xong, đợt chi không sang `processing` khi partner còn kỳ `running` hoặc `run_failed` (INV-15).

Hoa hồng người giới thiệu chỉ gửi sau khi kỳ `completed`: mỗi user một postback trên các item completed có `referral.state = pending`, id giữ định dạng hiện có (`user_referrer_type_firstItem_lastItem`, item sắp theo `_id`), gửi xong CAS `pending → sent`. Lỗi postback thì giữ `pending`, job hằng ngày gửi lại. Cách này cũng bỏ lỗi hiện tại tính hoa hồng trên item bị rejected.

Ví dụ:
- K ký với MCN A (15%) lúc 14:00 ngày 05/12/2026, kích hoạt cùng ngày. Item content thuộc chiến dịch bắt đầu 01/12/2026, thưởng view 300.000/ngày từ 01/12 đến 10/12, `G = 3.000.000`. Cửa sổ `[05/12/2026, 05/12/2027)`. Có 6 reward trong cửa sổ (05/12 đến 10/12), mỗi reward `fee_r = 45.000`, nên `fee = 270.000`, `net = 2.730.000`. Sổ K: `+3.000.000`, `−270.000`. Sổ A: `+270.000`.
- Ví dụ BA: `G = 3.000.000`, cả kỳ trong cửa sổ, 15%: `fee = 450.000`, KOL/KOC nhận 2.550.000 vào số dư.
- Tài khoản nhà uP của MCN cá nhân P (100%), item G = 2.500.000 cả kỳ trong cửa sổ: `fee = 2.500.000`, `net = 0`. Sổ uP: `+2.500.000`, `−2.500.000`. Sổ P: `+2.500.000` (ADR-12).
- Phase 1 không có luồng riêng cho đổi MCN giữa chiến dịch (NG-9); nếu xảy ra, công thức vẫn chia theo ngày. Cùng item ở ví dụ đầu: A chấm dứt quan hệ với K lúc 10:00 ngày 07/12; K ký B (10%) lúc 09:00 ngày 08/12. Phần phí của A: `[05/12, 07/12)` 2 ngày, 600.000 × 15% = 90.000. Phần phí của B: `[08/12, …)` 3 ngày, 900.000 × 10% = 90.000. Ngày 07/12 không thuộc cửa sổ nào. `net = 2.820.000`.

### 7.2 Đợt chi

| Bước | Creator | MCN |
|---|---|---|
| Lấy danh sách | Vòng hiện có; thuế qua `TaxPolicyFor` | `generateMcnPayouts`: một lệnh draft mỗi (MCN, chiến dịch) có số dư dương; thuế tính theo nhóm lệnh của MCN |
| Loại, bỏ loại | `ChangeDeclined` hiện có | CAS trên chính lệnh MCN |
| Hủy đợt | `draft → rejected` | `draft → rejected`, chưa có bút toán |
| Chuyển tiền | Mỗi lệnh một transaction: CAS `draft → transferring` và bút toán `wd:<withdrawId>:<action>` qua `AppendStrict` (cờ `LedgerV2`; tắt cờ như hiện nay) | Mỗi lệnh một transaction: kiểm số dư, trừ sổ MCN |
| Hoàn tất | Đảo bút toán theo khóa `wd:<withdrawId>:reversal:<action>` (cờ `LedgerV2`) | Mỗi lệnh một transaction: hoàn tất hoặc đảo |

Chi tiết phía MCN:

1. Chặn chung: partner bật `LedgerV2` có kỳ `running` hoặc `run_failed` thì đợt không sang `processing` (INV-15).
2. Vị trí gọi: `generateMcnPayouts` chạy trước vòng user, không phụ thuộc `return` sớm ở `backend/pkg/admin/service/transfer_processing.go:41-44`.
3. Điều kiện chọn MCN: `mcns.partner = transfer.partner`, `status = active`; có Hợp đồng ① hiện hành; TK ngân hàng hiện hành `match = ok` hoặc có `mismatchReason`; `Balance(mcn) > 0` và `Balance(mcn) ≥ Min`. Không xét SSO, eKYC, ②, `banned` của user vận hành (FR-019). MCN có bất kỳ chiến dịch nào `Balance(mcn, event) < 0` thì không tạo lệnh nào cho MCN đó và gửi Telegram; vận hành xử lý bằng `cmd/mcn-adjust` (ADR-11). MCN đạt điều kiện: mỗi chiến dịch có `Balance(mcn, event) > 0` thành một lệnh (ADR-14).
4. Số chi: mỗi lệnh `cash = Balance(mcn, event)`. Có Max thì tổng số chi của MCN không vượt Max. Xếp chiến dịch theo `events.startAt` tăng dần, chi đủ từng chiến dịch tới khi chạm Max. Chiến dịch chạm Max nhận phần còn lại. Các chiến dịch sau không có lệnh trong đợt này. MCN có số dư dưới Max vẫn được chi. Khác với creator: code hiện tại loại creator có số dư dưới Max khỏi đợt (§2.4, OQ-10).
5. Insert draft kèm snapshot `bank`, `payee`. Trùng `(transfer, mcn, event)` thì bỏ qua (chạy lại an toàn).
6. Thuế nhóm: sau khi tạo xong lệnh của một MCN, tính `groupBase` = tổng `cash` các lệnh `draft` chưa bị loại của MCN đó trong đợt. `TaxPolicyFor(mcn)` tính thuế một lần trên `groupBase`, rồi chia về từng lệnh theo tỷ lệ `cash`: mỗi lệnh lấy phần nguyên, số đồng còn dư cộng lần lượt cho lệnh có phần lẻ lớn nhất (largest remainder). Ghi snapshot `tax` (ADR-09). MCN công ty: `amount = 0`.
7. Loại lệnh có hai trường hợp. Cả hai CAS đều lọc theo `status`, nên không chạy chồng với bước Chuyển tiền trên cùng lệnh.
   - Đợt ở `processed`, lệnh còn `draft`: CAS `{_id, transfer, status: draft}` đặt `declined = true`, rồi tính lại thuế cả nhóm như bước 6. Tới Hoàn tất, lệnh này thành `rejected` với `rejectReason = declined`.
   - Đợt ở `transferred` (ngân hàng trả về, TK sai): CAS `{_id, transfer, status: transferring}` đặt `declined = true`. Thuế các lệnh còn lại giữ nguyên. Các lệnh cùng nhóm được đặt `taxGroupBroken = true` (trường riêng, nằm ngoài `tax`) để Kế toán xử lý tay.
8. Chuyển tiền, mỗi lệnh `draft` không bị loại, một `RunInTransaction`: `$inc mcns.ledgerVer`; đọc `Balance(mcn, event)` trong session.
   - `Balance(mcn, event) < cash`: abort. Ngoài transaction, CAS `draft → rejected` với `insufficient_balance`, đặt `taxGroupBroken = true` lên các lệnh cùng nhóm, gửi Telegram.
   - Đủ số dư: CAS `draft → transferring` và ghi `withdraw −actualCash` (`po:<id>:withdraw`), `tax −cashTax` (`po:<id>:tax`, khi > 0), `withdraw_fee −bankFee` (`po:<id>:withdraw_fee`, khi > 0).
   - Lỗi khác: lệnh giữ `draft`, Telegram.
9. Thống kê đợt (`GetStatistic`, `backend/pkg/admin/service/transfer.go:678-704`) cộng thêm aggregate `mcn-payouts`.
10. Hoàn tất, mỗi lệnh một `RunInTransaction`:
    - Lệnh `transferring` không bị loại → `completed`.
    - Lệnh `transferring` bị loại → `rejected` (`declined_after_transfer`). Ghi `withdraw_reversal` dương cho mỗi bút toán đã trừ (`reversalOf` theo action, khóa `po:<id>:reversal:<action>`).
    - Lệnh còn `draft` bị loại → `rejected` (`declined`).
    - Lệnh còn `draft` không bị loại (Chuyển tiền lỗi) → `rejected` (`transfer_failed`), đặt `taxGroupBroken = true` lên các lệnh cùng nhóm.

    Bấm Hoàn tất lại chỉ xử lý lệnh còn `transferring`. Sổ MCN không cần bước gắn `transferId` lên các bút toán cộng tiền theo thứ tự FIFO như sổ creator (`backend/pkg/admin/service/transfer_finish.go:154-167`), vì mỗi bút toán chi đã mang `payout` và `event`.

### 7.3 Thuế

`TaxPolicyFor(payee)` (file mới `backend/internal/service/tax.go`) thay đoạn inline `backend/internal/service/withdraw.go:136-139`.

| Payee | `incomeType` | `policy` | Cơ sở | Ngưỡng |
|---|---|---|---|---|
| KOL/KOC. Tài khoản nhà cũng đi lệnh creator cho thu nhập phát sinh trước ngày ký phụ lục 100%, hoặc thu nhập của chiến dịch bắt đầu trước `MCN_FEE_EVENT_START_FROM` | `creator_reward` | `pit_10` | Số chi của lệnh (sổ đã trừ phí, D21) | `TAX_PIT_THRESHOLD` = 5.000.000đ |
| MCN công ty | `mcn_income` (phí quản lý và thu nhập nội dung của tài khoản nhà) | `none` | – | – |
| MCN cá nhân | `mcn_income` | `MCN_INDIVIDUAL_TAX_POLICY`, mặc định `pit_10` (Q9, OQ-01) | `groupBase` (§7.2 bước 6) | Như trên, xét trên `groupBase` |

`taxpayerKey`: MCN công ty `mst:<identityNumber>`; MCN cá nhân `cccd:<identityNumber>`; creator `cccd:<users.contract.identificationNumber>` chuẩn hóa chỉ giữ chữ số, không có thì `user:<id>` kèm `taxIdUnresolved`.

Bảng tình huống (ngưỡng 5.000.000, suất 10%, phí ngân hàng 0):

| # | Tình huống | Lệnh trong đợt | Thuế | Thực nhận |
|---|---|---|---|---|
| 1 | KOL/KOC không MCN, số dư 6.000.000 | Creator 6.000.000 | 600.000 | 5.400.000 (như hiện nay) |
| 2 | KOL/KOC có MCN 15%, G = 6.000.000 | Creator 5.100.000; MCN A nhận 900.000 vào sổ | 510.000 | 4.590.000 |
| 3 | KOL/KOC có MCN 15%, G = 3.000.000 (ví dụ BA) | Creator 2.550.000 | 0 | 2.550.000 |
| 4 | MCN công ty C, số dư 8.000.000 | MCN 8.000.000, `mst:C` | 0 | 8.000.000 (HĐ GTGT ngoài hệ thống, OQ-06) |
| 5 | MCN cá nhân P (CCCD X), số dư 6.000.000 | MCN 6.000.000, `cccd:X` | 600.000 | 5.400.000 |
| 6 | MCN cá nhân P (CCCD X): phí 3.000.000 từ chiến dịch C1; tài khoản nhà uP (100%) có nội dung 2.500.000 ở chiến dịch C2 | Hai lệnh MCN P: C1 3.000.000, C2 2.500.000; `groupBase` 5.500.000, `cccd:X` | 550.000, phân bổ 300.000 + 250.000 | 2.700.000 và 2.250.000 |
| 7 | MCN công ty C: phí 8.000.000; tài khoản nhà uC (100%) có nội dung 6.000.000 | Lệnh MCN C theo chiến dịch, tổng 14.000.000, `mst:C` | 0 | 14.000.000 (HĐ GTGT ngoài hệ thống, OQ-06) |

Nếu xét ngưỡng từng lệnh thì cả hai lệnh của ca 6 đều dưới 5.000.000 nên không bị khấu trừ. Đó là chia nhỏ khoản chi để né thuế, điều họp 10/11 muốn chặn. Vì vậy lệnh MCN xét ngưỡng trên `groupBase` (ADR-09).

### 7.4 File ngân hàng

`backend/pkg/admin/service/export_transfer.go` thêm dòng MCN và sáu cột cuối: Chiến dịch, Loại người nhận, Loại đối tượng, Loại thu nhập, `taxpayerKey`, `groupBase`. Dòng creator để trống Chiến dịch và `groupBase`. Vị trí 13 cột cũ không đổi (:68-82).

| Cột | Dòng creator | Dòng MCN |
|---|---|---|
| STT | `withdraw.User.Hex()` như hiện nay | `po:<payoutId>`, mã lệnh `mcn-payouts`. Mỗi lệnh một dòng; dùng `mcn:<mcnId>` sẽ trùng khi MCN có nhiều chiến dịch, và không truy vết được lệnh (§12) |
| Số tiền trước thuế, thuế, số chuyển | `cash`, `cashTax`, `actualWithdrawCash` | `cash`, `cashTax`, `actualCash` |
| TK hưởng, tên người hưởng, ngân hàng | Như hiện nay (đang rỗng, OQ-04) | Từ snapshot `bank` |
| MST, CCCD | `users.contract.taxNumber`, `identificationNumber` | MST: `identityNumber` (cá nhân: CCCD là MST cá nhân). CCCD: cá nhân `identityNumber`, công ty rỗng |
| Nội dung, Số điện thoại, Ngày ký TOS | Như hiện nay | Chi MCN kèm mã đợt và tên chiến dịch; `mcns.phone`; ngày ký Hợp đồng ① |
| Chiến dịch (mới, ADR-14) | Rỗng | `events.name` của lệnh |
| Loại người nhận (mới, FR-019) | KOL/KOC | MCN |
| Loại đối tượng, Loại thu nhập, `taxpayerKey` (mới) | Cá nhân; `creator_reward`; snapshot | Công ty hoặc Cá nhân; `mcn_income`; snapshot |
| `groupBase` (mới, ADR-09) | Rỗng | Snapshot, để Kế toán thấy cơ sở thuế của nhóm |

File bỏ các lệnh đã bị loại (`declined`) và các lệnh `rejected`, áp dụng như nhau cho dòng creator và dòng MCN. File thêm dòng tổng. Khuyến nghị Kế toán xuất file sau Chuyển tiền; xuất ở `processed` thì file gồm cả lệnh có thể bị `insufficient_balance`. Job đối chiếu kiểm Σ cột "Số tiền chuyển" của lệnh `transferring`, `completed` bằng Σ bút toán `withdraw` của đợt trên hai sổ.

### 7.5 Điều chỉnh và bù

| Tình huống | Cách xử lý |
|---|---|
| KOL/KOC thiếu thu nhập gốc | Thưởng thêm (D7). Phí trích theo dòng quan hệ tại ngày tạo Thưởng thêm |
| Phí bị trích thừa | `cmd/mcn-adjust`, một `RunInTransaction` có `$inc mcns.ledgerVer`: `cash-flows{mcn_fee_adjustment, +x}` khóa `adj:<ticket>:<seq>:koc` và `mcn-cash-flows{adjustment, −x, event}` khóa `adj:<ticket>:<seq>:mcn`. `x > 0`; `event` là chiến dịch của khoản gốc |
| MCN nhận thiếu phí, KOL/KOC không bị trích thừa (AT bù) | Script ghi `mcn-cash-flows{adjustment, +x, event}`, khóa `adj:<ticket>:<seq>:mcn` |
| Số dư MCN âm sau điều chỉnh | Số dư của chiến dịch đó giữ âm, không lấy chiến dịch khác bù. MCN có bất kỳ chiến dịch nào âm thì đợt chi không tạo lệnh nào cho MCN đó, gửi Telegram; vận hành xử lý bằng `cmd/mcn-adjust` (ADR-11, §7.2 bước 3) |

`seq` là số thứ tự dòng trong ticket, nên một ticket có nhiều KOL/KOC hoặc nhiều kỳ không trùng khóa.

### 7.6 Sơ đồ Duyệt kỳ

```mermaid
sequenceDiagram
  autonumber
  actor A as Admin
  participant RS as Reconciliation service
  participant DB as MongoDB
  participant TG as Telegram
  A->>RS: Duyệt tất cả hoặc Duyệt lại
  RS->>DB: CAS kỳ processed hoặc run_failed sang running
  loop Mỗi item còn pending
    RS->>DB: Tx: CAS item sang completed, validateItem, CAS reward hoặc bonus
    RS->>DB: Tx: cash-flows +totalCash và -fee, mcn-cash-flows +fee, referral pending, commit
    RS->>DB: Sau commit: analytic, thống kê, thông báo
  end
  RS->>DB: verifyRunTotals E1 đến E4
  alt Đạt
    RS->>DB: CAS running sang completed, ghi completedAt
    RS->>DB: Gửi hoa hồng người giới thiệu, đánh dấu sent
  else Lệch, lỗi hoặc panic
    RS->>DB: CAS running sang run_failed
    RS->>TG: Cảnh báo kèm mã kỳ
  end
```

### 7.7 Sơ đồ Đợt chi

```mermaid
sequenceDiagram
  autonumber
  actor A as Admin
  participant TS as Transfer service
  participant DB as MongoDB
  participant K as Kế toán và ngân hàng
  A->>TS: Lấy danh sách
  TS->>DB: Kiểm không có kỳ running hoặc run_failed
  TS->>DB: mcn-payouts draft kèm snapshot, rồi vòng creator, đợt sang processed
  A->>TS: Chuyển tiền
  loop Mỗi mcn-payout draft không bị loại
    TS->>DB: Tx: inc ledgerVer, đọc Balance, CAS draft sang transferring, trừ sổ MCN
  end
  A->>TS: Xuất file ngân hàng
  TS-->>K: Dòng creator và dòng MCN, dòng tổng
  A->>TS: Hoàn tất
  loop Mỗi mcn-payout transferring
    TS->>DB: Tx: completed, hoặc rejected kèm withdraw_reversal
  end
```

## 8. API (phần MCN)

### 8.1 Admin

Router `backend/pkg/admin/router/mcn.go:11-28`, quyền ở `backend/pkg/admin/router/routeauth/registry_routes.go:173-177`. Phạm vi ADV qua `IsAllowPartner`; ngoài phạm vi trả như không tồn tại.

| Method | Path | Quyền | Mô tả | Trạng thái |
|---|---|---|---|---|
| GET | `/mcns`, `/mcns/:id`, `/mcns/:id/documents/:kind`, `.../:docId/download` | `mcn.view` | Danh sách, chi tiết kèm 5 điều kiện; lịch sử hồ sơ; presigned URL 10 phút | Có |
| POST, PUT | `/mcns`, `/mcns/:id`, `/mcns/:id/documents`, `/mcns/:id/bank/lookup`; GET `/mcns/banks` | `mcn.edit` | Tạo, sửa (khóa `type`, `identityNumber` sau `active`); hồ sơ mới; tra tên chủ TK (stub `unverified`, `backend/pkg/admin/service/mcn_bank.go:57-59`) | Có, sửa |
| POST | `/mcns/:id/activate` | `mcn.activate` | Kích hoạt; xung đột trả 409 | Có, sửa guard |
| GET | `/mcns/:id/members`, `/mcns/:id/ledger` | `mcn.view` | Thành viên (chỉ đọc); số dư và bút toán `mcn-cash-flows` | Mới |
| GET | `/reconciliations/:id/recipients`, `.../recipients/mcn/:mcnId` | Quyền đối soát hiện có | Tab Người nhận (FR-017). Trước Duyệt đọc `mcnSplits`; sau Duyệt chỉ tính item completed, item bị loại hiện "Đã loại" với phí 0 | Mới |
| GET, POST | `/transfers/:id/mcn-payouts`, `/transfers/:id/mcn-payouts/declined` | Quyền đợt chi hiện có | Lệnh MCN của đợt; loại, bỏ loại | Mới |

### 8.2 Public

Tài khoản vận hành (`backend/pkg/public/router/mcn.go:13-27`, `RequiredLogin` + `RequiredMcnAccount`; `mcnID` lấy từ context):

| Method | Path | Mô tả | Trạng thái |
|---|---|---|---|
| GET, POST | `/mcn/me`; `/mcn/links`, `/mcn/links/:id/off`; `/mcn/members?group=…`, `/mcn/members/:id/terminate` | Hồ sơ; link mời 0..100; thành viên và người đã đồng ý (Q10); chấm dứt kèm lý do (Q13) | Có |
| GET | `/mcn/balance` | `McnLedger().Balance(mcnID)`, đọc trực tiếp sổ | Mới, phase 7 |
| GET | `/mcn/ledger` | Bút toán `mcn-cash-flows` của MCN: phí theo thành viên và kỳ, chi, đảo (FR-018) | Mới, phase 7 |
| GET | `/mcn/reconciliations`, `/mcn/reconciliations/:id` | Kỳ completed có bút toán phí của MCN; từng thành viên: tỷ lệ, G trong cửa sổ, phí. Số lấy từ Σ `mcn-cash-flows` theo `source.reconciliation` | Stub, phase 7 |
| GET | `/mcn/payouts` | Lịch sử lệnh chi MCN | Mới, phase 7 |

KOL/KOC (`backend/pkg/public/router/mcn_invite.go:12-29`):

| Method | Path | Mô tả | Trạng thái |
|---|---|---|---|
| GET | `/mcn-invites/:code`, `/mcn-memberships/me` | Lời mời (không bắt đăng nhập); dòng quan hệ của mình | Có |
| POST | `/mcn-invites/:code/agree\|decline`, `/mcn-memberships/:id/decline\|sign\|sync-sign`, `/mcn-memberships/me/leave\|cancel-leave` | Đồng ý; từ chối trên trang mời (upsert theo (user, link)); ký phụ lục; báo rời, rút lại | Có, sửa guard |
| GET | `/users/reconciliations`, `/users/reconciliations/:id` | Mọi creator: G, phí, số cộng vào số dư theo kỳ completed (FR-021) | Mới, phase 7 |

Route web đã có: `frontend/config/routes.ts:119-150`; admin `admin/config/routes.ts:205-217`.

Mã lỗi: frontend phân biệt lỗi theo mã trong body (mã 2400–2599, `backend/internal/locale/mcn.go:9`), không theo HTTP status (`backend/pkg/public/handler/mcn_invite.go:30-31`). Mã mới: `MCN_MEMBER_STATE_CHANGED`, `MCN_ANNEX_IN_FLIGHT`, `MCN_HOUSE_RATE_REQUIRED` (tài khoản nhà nhận link dưới 100%). Đã bỏ `MCN_EMAIL_IN_USE` (v1.0, bỏ từ v2.0 theo PRD Q12) và `MCN_SELF_MEMBERSHIP` (v2.0, bỏ ở v2.1 theo họp 10/11). HTTP 409 cho xung đột trạng thái cần thêm `Response409` vào `backend/internal/echo/echo.go` (hiện chỉ có 200, 400, 401, 403, 404 ở :262-345).

### 8.3 Ánh xạ màn hình với vai và nguồn số

| Điểm | Vai | Nguồn, quy tắc |
|---|---|---|
| Số dư, Lịch sử dòng tiền (`frontend/src/pages/bank`) | Creator | `cash-flows` của user; `statistic.cashRemaining` |
| Avatar › Đối soát; Avatar › MCN của tôi | Creator | `reconciliation-items` completed của user; `mcn-members` của user |
| Quản lý MCN › Số dư (mới) | MCN | `/mcn/balance`, `/mcn/ledger` |
| Quản lý MCN › Đối soát | MCN | `mcn-cash-flows` theo `source.reconciliation` |
| Quản lý MCN › Thành viên, Lời mời | MCN | `mcn-members`, `mcn-invite-links` |
| Thông báo | Theo loại | `mcn_*` gửi user vận hành hiện hành tại lúc gửi (không theo user lúc ghi sổ); đối soát creator gửi `item.User` |
| `GET /users/me` | Cả hai | Trả `mcn` (id, tên, vai) độc lập với các trường creator; quyền thật kiểm ở middleware |
| Lịch sử đăng nhập | Cả hai | Giữ role `creator`; thêm trường `mcn` khi user có tài khoản hiện hành (thay việc ghi cứng ở `backend/pkg/public/service/user.go:1827`) |
| Admin › danh sách creator, thống kê partner | Creator | `user-partners.isJoined` |
| Đợt chi creator | Creator | User vận hành được xét như mọi creator (SSO, eKYC, ②, `banned`) |

User vừa vận hành MCN vừa làm creator thấy hai khu tách biệt, nhãn "Số dư của bạn" (creator) và "Số dư MCN <tên MCN>". Hai số không cộng gộp ở bất kỳ màn hình nào.

## 9. Phân quyền, bảo mật, quyền riêng tư

| Chủ đề | Thiết kế |
|---|---|
| AuthZ MCN | `RequiredMcnAccount` đặt `mcnID` từ `mcn-accounts` hiện hành; handler không nhận mcn id từ client. Thêm kiểm `banned`; route tiền và PII đọc trực tiếp, không qua cache 5 phút |
| AuthZ admin | RBAC `mcn.view`, `mcn.edit`, `mcn.activate`; dành sẵn `mcn.adjust` cho phase có UI. Lệnh MCN dùng quyền đợt chi hiện có |
| IDOR | Mọi truy vấn phía MCN lọc theo `mcnID` từ context. API đối soát chỉ trả phần phí và bút toán của MCN đó, không trả thu nhập của KOL/KOC ngoài cửa sổ phí. Dòng quan hệ phía KOL/KOC lọc theo `user` của phiên |
| IDOR eKYC, hợp đồng ② | Ba route ở §2.5 dùng SSO của phiên, bỏ `user_id`, `sso_ids` từ client. Vá trước go-live vì `is_ekyc` là điều kiện ký phụ lục |
| Q10, Q13 | Người Chờ ký: chỉ tên và thông tin lời mời; ảnh chỉ trả khi đã là thành viên (`backend/pkg/public/service/mcn_member.go:126-151`); không trả email, SĐT. Lý do Từ chối, Chấm dứt, Báo rời hiện cho bên kia và Admin |
| PII | Hồ sơ pháp lý ở bucket riêng tư, tải qua presigned URL ngắn hạn. Số TK, CCCD, MST chỉ trả cho admin có quyền; log che số TK và CCCD (giữ 4 số cuối) |
| Nơi nhận tiền, người vận hành | Chỉ admin sửa TK ngân hàng MCN; đổi TK tạo phiên bản mới, audit, Telegram; lệnh chi dùng snapshot. Đổi người vận hành bằng `cmd/mcn-rebind`: `mcn-accounts` cũ sang `revoked`, mời email mới; tiền không di chuyển |
| Audit | Bút toán MCN ghi `createdBy`; mọi bước chuyển `mcn-members`, `mcn-accounts`, `mcn-payouts` ghi `history`; thao tác admin ghi audit hiện có (`recordDocAudit`) |

## 10. Đồng thời, idempotency, xử lý lỗi

| Tình huống | Hành vi |
|---|---|
| Hai Agree đồng thời cùng (user, MCN) | Partial unique `isPending` chặn dòng thứ hai; request thua trả dòng đang Chờ ký |
| Bind và StartSign của cùng user chạy đồng thời | Cùng `$inc users.mcnGuardVer`; bên thua `WriteConflict`, driver chạy lại, đọc thấy trạng thái mới, trả 409 |
| Hai StartSign cùng một dòng | CAS `annex.state none → creating`; bên thua trả link khi `created`, 409 khi `creating` |
| StartSign ở MCN thứ hai khi đang mở ký MCN thứ nhất | Partial unique `annexInFlight` chặn; 409 `MCN_ANNEX_IN_FLIGHT` kèm tên MCN đang ký; KOL/KOC ký xong hoặc Từ chối lời mời kia trước |
| Econtract lỗi hoặc timeout khi tạo phụ lục | Dòng giữ `annex.state = creating`. Job `McnAnnexCleanup` xét các dòng `creating` quá 10 phút và tra econtract theo SSO. Econtract đã có phụ lục thì đặt `created`. Chưa có thì đặt `none` và `annexInFlight = false`, để KOL/KOC mở ký lại |
| Ký trước hạn, đồng bộ sau hạn | Trước khi chuyển dòng sang `sign_expired`, job `McnExpireSign` hỏi trạng thái phụ lục trên econtract. Đã SIGNED thì kích hoạt với `signedAt = min(giờ đồng bộ, signDeadline)`, `annex.signedAtSource = sync_capped`. Econtract lỗi thì giữ `agreed`; lần chạy job kế tiếp hỏi lại |
| Phụ lục SIGNED khi dòng đã `declined`, `sign_expired`, `superseded` | `signedAfterClose=true`, không kích hoạt, không trích phí, Telegram (OQ-07) |
| Lấy danh sách khi job `McnEndMembers` chưa chạy hoặc bị tắt | `FeeWindow` dùng mốc đã lưu; kết quả như khi job đã chạy |
| `applyMcnFees` lỗi | Thử 3 lần; vẫn lỗi thì `mcnSnapshot.status = failed`, kỳ giữ `processing`, Telegram; Admin Hủy kỳ rồi lập lại |
| Hai runner Duyệt cùng item | CAS item trong transaction; runner sau nhận `ErrAlreadyPosted` |
| `WriteConflict` trong `postItem` | Driver chạy lại. Hết số lần thử thì item giữ `pending`, phép kiểm E1 của `verifyRunTotals` (không còn item `pending`) không đạt, kỳ sang `run_failed`, Admin Duyệt lại |
| Duplicate key ở bước ghi sổ | Transaction abort, item giữ `pending`, Telegram; kỳ sang `run_failed`; điều tra trước khi Duyệt lại |
| Tiến trình dừng giữa Running | Kỳ ở `running`. Job `ReconRunningWatch` cảnh báo khi `updatedAt` quá 2 giờ; script chuyển `run_failed` sau khi xác nhận không còn runner; Duyệt lại an toàn |
| Hai đợt chi mở cùng partner (race ở Create), hoặc điều chỉnh âm giữa Lấy danh sách và Chuyển tiền | INV-14: lệnh thiếu số dư sang `rejected` (`insufficient_balance`) |
| Chuyển tiền lỗi với một lệnh MCN | Transaction abort, lệnh giữ `draft`, Telegram; Hoàn tất chuyển `rejected` (`transfer_failed`); số dư còn nguyên |
| Loại lệnh chạy đồng thời với Chuyển tiền; dừng giữa Hoàn tất; `generateMcnPayouts` chạy lại | Lần lượt ở §7.2 bước 7, bước 10, bước 5 |
| MCN có chiến dịch số dư âm lúc Lấy danh sách đợt chi | Không tạo lệnh nào cho MCN đó, Telegram; vận hành dùng `cmd/mcn-adjust` (§7.2 bước 3) |
| Bind gặp hai user cùng email đã xác thực | Không gắn, Telegram |

## 11. Tương thích ngược, migration, feature flag, rollout

### 11.1 Thay đổi trên đường tiền creator

v1.0 Nguyên tắc 2: "không đổi trạng thái kỳ đối soát…; người không liên quan MCN cho kết quả y như cũ". Bản này giữ kết quả tiền và thuế, nhưng đổi cách ghi sổ:

| Thay đổi | Phạm vi | Cờ | Lý do |
|---|---|---|---|
| `postItem` transaction, `verifyRunTotals`, `run_failed`, `idemKey` cho bút toán đối soát, writer `AppendStrict`, referral outbox | Partner bật cờ | `PartnerOpts.LedgerV2` | Ba trạng thái ghi dở ở §2.3; không có cách bảo toàn tiền cho khoản có MCN mà giữ đường cũ cho khoản không có MCN (ADR-07) |
| Chặn Lấy danh sách đợt chi khi có kỳ `running`, `run_failed` | Partner bật cờ | Như trên | Không chi khoản của kỳ đang điều tra |
| Chuyển tiền, Hoàn tất creator trong transaction với khóa `wd:<withdrawId>:*` | Partner bật cờ | Như trên | Nhánh lỗi ở `backend/pkg/admin/service/transfer_transferring.go:83-96` không chạy: insert lỗi thì lệnh vẫn được chi mà sổ không bị trừ, đợt sau chi trùng (double payout) |
| Chặn Hủy kỳ `run_failed` | Mọi partner | Không | Kỳ đã ghi sổ một phần không được hiện là "Đã từ chối" |
| `TaxPolicyFor` thay đoạn inline | Mọi partner | Không | Kết quả giống hệt (test hồi quy) |
| `cash-flows.idemKey` (omitempty) | Mọi partner | Không | Trường bổ sung, dòng cũ không có |

Dòng `mcn_fee` trên `cash-flows` mang giá trị âm. Code cũ tính số dư bằng Σ`value`, nên nếu rollback code thì số dư creator vẫn đúng. Bước Hoàn tất vẫn gán `transferId` cho bút toán theo thứ tự cũ trước (FIFO) như hiện nay.

### 11.2 Migration

Onboarding lên prod từ cuối tháng 11 (§11.4 bước 2). Vì vậy §14.1 #5 phải xong trước go-live, để mọi dòng kích hoạt trên prod có `activatedAt`, `feeFrom`. M1–M3 chạy trên dev, QA và prod trong bản go-live. M1: tạo index mới (§6.6); môi trường nào đã có `uniq(user)` cũ của `mcn-accounts` (dev, QA) thì xóa trước khi tạo bản partial theo `isCurrent`. M2: `mcn-members` đặt `isPending=true` cho dòng `agreed`; `activatedAt`, `feeFrom` lấy từ `startAt` cho dòng `active`, `leaving`, `ended`; `annex.signedAtSource=sync`. M3: `mcn-accounts.isCurrent=true` cho dòng `invited`, `active`. M4 (nếu làm khuyến nghị ADR-08): `transfers.isOpen` cho đợt chưa `finished`, `rejected`.

### 11.3 Feature flag và cấu hình

| Cờ, ENV | Mặc định | Phạm vi |
|---|---|---|
| `PartnerOpts.McnEnabled` | false | Onboarding (ADR-10) |
| `PartnerOpts.LedgerV2` | false; bật cho Ambassador trước khi đặt `MCN_FEE_EVENT_START_FROM` | §11.1 |
| `TAX_PIT_RATE`, `TAX_PIT_THRESHOLD` | 10, 5.000.000 | `TaxPolicyFor`; `MinTaxableRevenue` chỉ còn là giá trị mặc định |
| `MCN_INDIVIDUAL_TAX_POLICY` | `pit_10` | Thuế của MCN cá nhân (phí quản lý và thu nhập tài khoản nhà), tính trên `groupBase` (ADR-09, OQ-01) |
| `MCN_JOB_ENABLED` | bật | Job MCN (`backend/internal/config/env.go:27-29`). Tắt job không làm sai phí (G-4) |
| `MCN_FEE_EVENT_START_FROM` | trống: chưa trích phí; prod đặt `2026-12-01` khi phase 5–6 đã lên và Ambassador đã bật `LedgerV2` | ADR-13. Mốc đã đặt mà partner chưa bật `LedgerV2` thì `applyMcnFees` báo lỗi (ADR-07) |
| `MCN_ANNEX_CONTRACT_TYPE` | trống: StartSign báo chưa cấu hình | Mã mẫu phụ lục trên FPT e-contract. Nếu AT tách mẫu phụ lục theo loại MCN (OQ-16), thay bằng `MCN_ANNEX_CONTRACT_TYPE_COMPANY` và `MCN_ANNEX_CONTRACT_TYPE_INDIVIDUAL` |

### 11.4 Rollout và rollback

Phase trong tài liệu này là phase của plan triển khai code, khác "Phase 1" của sản phẩm:

| Phase | Nội dung | Lên prod |
|---|---|---|
| 1–4 | Hồ sơ và kích hoạt MCN, gắn tài khoản, link mời, lời mời, ký phụ lục, thành viên và rời MCN | Go-live cuối tháng 11 |
| 5 | Đối soát: trích phí, ghi sổ lúc Duyệt, `cmd/mcn-adjust` | Cùng bản với phase 6, trước kỳ đối soát đầu tiên có chiến dịch tháng 12 |
| 6 | Chi trả MCN, thuế, file ngân hàng | Cùng bản với phase 5 |
| 7 | Màn xem đối soát cho MCN và KOL/KOC | Sau phase 5–6 |
| 8 | Thông báo, kiểm thử, bàn giao | Cuối |

Mốc theo họp 10/11: mẫu hợp đồng chốt trong tuần; biên bản ghi "ký 17/11" với team My (nhóm phụ trách mẫu hợp đồng phía AT); demo tuần 16–20/11; go-live cuối tháng 11; phí áp dụng cho chiến dịch bắt đầu từ 01/12/2026; nghiệm thu theo tuần với Hà Lê; màn mới làm mockup cho duyệt trước khi code.

Go-live cuối tháng 11 chỉ cần phần onboarding. Phí và chi trả phải lên trước kỳ đối soát đầu tiên có chiến dịch bắt đầu từ 01/12, không cần cùng ngày go-live.

1. Trước demo 16–20/11: sửa nhóm "Sửa ngay" ở §14.1, gồm nới chặn tài khoản nhà (#22) và mốc kích hoạt `activatedAt`, `feeFrom` (#5). Demo luồng hồ sơ, mời, ký, thành viên; chưa có phần tiền.
2. Cuối tháng 11: deploy prod phase 1–4 kèm migration M1–M3 (§11.2). Trước đó phải xong #19 (IDOR eKYC, hợp đồng ②) và `cmd/mcn-rebind` (#21). Đặt `McnEnabled=true` cho Ambassador. `MCN_FEE_EVENT_START_FROM` để trống. `LedgerV2` vẫn false. MCN được tạo, mời, ký phụ lục; chưa có khoản phí nào.
3. Phase 5 (ADR-05, 06, 07, 13) và phase 6 (ADR-08, 09, 14) lên cùng một bản phát hành, để phí không vào sổ khi chưa có đường chi.
4. Chạy hồi quy trên bản sao dữ liệu: một kỳ đối soát và một đợt chi của một partner không có MCN (FEC, HDBank hoặc VPBank), bật `LedgerV2=true`. So `cash-flows` của kỳ (trừ `idemKey`) và `cashTax` từng lệnh với bản trước tính năng.
5. Bật `LedgerV2` cho Ambassador. Theo dõi một kỳ và một đợt chi: `verifyRunTotals` đạt cả bốn phép kiểm E1–E4 (§7.1), thuế không đổi.
6. Sau bước 5, đặt `MCN_FEE_EVENT_START_FROM=2026-12-01` trước kỳ đối soát đầu tiên chứa chiến dịch tháng 12. Theo dõi kỳ đầu có phí bằng job đối chiếu.
7. Phase 7 (màn xem), phase 8 (thông báo).

Rollback
- Code: an toàn vì trường và collection mới là bổ sung. Phí đã vào `mcn-cash-flows` giữ nguyên, chưa chi cho tới khi deploy lại.
- Không rollback giữa Chuyển tiền và Hoàn tất của một đợt có lệnh MCN.
- Tắt `LedgerV2` khi partner còn kỳ `run_failed` thì Duyệt lại chạy code cũ; phải xử lý hết kỳ `run_failed` trước khi tắt.

## 12. Observability

| Loại | Nội dung |
|---|---|
| Log có cấu trúc | Mỗi bút toán và bước chuyển: `idemKey`, `reconciliation`, `item`, `member`, `mcn`, `payout`, `transfer`, `value`. Mức `error` cho abort transaction và duplicate key |
| Cảnh báo Telegram | Kỳ `run_failed`; `mcnSnapshot.status = failed`; duplicate key trong `postItem`; Chuyển tiền MCN lỗi hoặc `insufficient_balance`; MCN có chiến dịch số dư âm lúc Lấy danh sách đợt chi; job đối chiếu lệch; `signedAfterClose`; đổi TK ngân hàng MCN; kỳ `running` quá 2 giờ; bind gặp email trùng |
| Job `LedgerReconcile` (hằng ngày) | E2–E4 cho mọi kỳ có bút toán `rc:*` trong N ngày, mọi trạng thái kỳ; mỗi `mcn-payouts` `transferring`, `completed` có bút toán `withdraw`; mỗi lệnh `rejected` có bút toán `withdraw` thì có đủ `withdraw_reversal`; Σ cột file ngân hàng bằng Σ bút toán `withdraw` của đợt; số MCN hiển thị bằng Σ sổ; gửi lại referral `pending` của kỳ completed |
| Số liệu vận hành | Repo chưa có metrics backend; số liệu lấy bằng truy vấn: tổng phí theo kỳ, số MCN, số lệnh MCN theo trạng thái, số `run_failed` |
| Truy vết tiền | Dòng file ngân hàng (cột STT mang mã lệnh, §7.4) → `mcn-payouts` → bút toán chi `mcn-cash-flows{payout}`. Phí cấu thành lệnh là các bút toán `mcn_fee` cùng (`mcn`, `event`) → `source.reconciliationItem` → `reconciliation-items.mcnSplits` → `event-rewards` hoặc `event-bonus`. Chiều creator: `cash-flows{idemKey, options.reconciliationItem}` |

## 13. Chiến lược test

| Lớp | Phạm vi | Ca bắt buộc |
|---|---|---|
| Unit | `FeeWindow`, công thức phí, `TaxPolicyFor`, chuẩn hóa CCCD | `fee_r` với `cash_r` lẻ; tỷ lệ 0 và 100; kích hoạt 23:59 và 00:00 giờ VN; `feeFrom = effTo`; hai phần phí cùng item; `leaving` có `endAt` trước `leaveEffectiveAt`; ngưỡng đúng 5.000.000 và 4.999.999; creator cho kết quả như code cũ |
| Integration Mongo thật (`-tags integration`, port 27099) | Transaction, partial unique, CAS | Agree đồng thời (INV-02); bind giữa lúc Chờ ký MCN khác rồi ký (INV-03b); bind user đã có dòng 100% với chính MCN, kiểm `house = true` (INV-03a); StartSign khi `selfCheck = unresolved` và CCCD khớp MCN cá nhân với link dưới 100%; StartSign hai MCN đồng thời (INV-05); ký trước hạn, đồng bộ sau hạn không có `signed_at`; kích hoạt sau `processed` với ngày ký ≤ `toAt`; Lấy danh sách khi job end-members chưa chạy; `applyMcnFees` lỗi giữa chừng; `postItem` chạy hai lần và hai runner đồng thời; `WriteConflict` do ghi reward đồng thời; Duyệt dừng giữa chừng rồi Duyệt lại từ `run_failed`; Hủy kỳ `run_failed` bị chặn; referral sau Duyệt lại; hai đợt chi đồng thời cùng MCN; điều chỉnh âm giữa Lấy danh sách và Chuyển tiền; loại lệnh MCN sau Chuyển tiền rồi Hoàn tất; hai bút toán đường cũ liên tiếp không có `idemKey` đều được ghi; lỗi insert ở Chuyển tiền creator giữ lệnh ở `draft` |
| Ca biên tiền và thuế | §7.1, §7.3 | Mọi dòng bảng §7.3; KOL/KOC đổi MCN giữa item; Thưởng thêm tạo sau khi rời MCN; MCN có một chiến dịch số dư âm: không có lệnh nào cho MCN đó; Max cắt số chi MCN; `Balance = 0` không tạo lệnh; chiến dịch bắt đầu 30/11 và 01/12 với mốc 01/12; mốc trống; mốc đã đặt mà partner chưa bật `LedgerV2`: kỳ giữ `processing`; tài khoản nhà 100% (`net = 0`, không có lệnh creator cho thu nhập từ ngày ký); tài khoản vận hành đồng ý link 15% của chính MCN mình: Agree trả `MCN_HOUSE_RATE_REQUIRED`; MCN cá nhân có hai lệnh theo chiến dịch, mỗi lệnh dưới 5.000.000 nhưng tổng từ 5.000.000 trở lên: khấu trừ 10% trên tổng; MCN công ty trong cùng ca: không khấu trừ; loại một lệnh trong nhóm trước và sau Chuyển tiền |
| Hồi quy creator | Đường cũ và cờ `LedgerV2` | Kỳ không có MCN: `cash-flows` của kỳ giống bản trước tính năng (trừ `idemKey`); `cashTax` từng lệnh giống code cũ; partner tắt cờ chạy đúng code cũ |
| Đối chiếu số | Sau mỗi test tích hợp tiền | E1–E4; INV-11 theo item; `Balance(mcn) = Σ mcn_fee + Σ adjustment + Σ withdraw + Σ tax + Σ withdraw_fee + Σ withdraw_reversal` (mỗi tổng có dấu), kiểm cả theo từng (mcn, event); đẳng thức theo action của sổ creator ở §6.5 |
| Rà mức nguồn (CI) | grep, test AST | Chỉ file của `McnLedger` tham chiếu `CollectionMcnCashFlow`; `CashFlowRaw.IdemKey` có `omitempty`; không gọi `AddCashFlow` với `SessionContext`; không route `/mcn/*` đọc `CollectionCashFlow`; `mcn_fee` không thuộc `ActionMustTaxReward`; không có `TaxExempt` |
| IDOR, quyền | Router e2e | MCN A đọc kỳ, thành viên, sổ, lệnh của MCN B; user bị `banned` gọi `/mcn/*`; người Chờ ký không lộ email, SĐT, ảnh; route eKYC với SSO của người khác |

## 14. Hiện trạng triển khai và chênh lệch phải sửa

### 14.1 So với code trên nhánh

| # | Hạng mục | Trạng thái trên nhánh | Việc còn lại | Khi |
|---|---|---|---|---|
| 1 | Transaction có retry | Wrapper không retry, che lỗi gốc khi commit lỗi (`backend/internal/module/database/mongodb/transaction.go:28-72`) | `RunInTransaction` bọc `session.WithTransaction`; map `WriteConflict` sau retry sang 409. Mục 3, 4, 6, 12, 15 phụ thuộc mục này | Sửa ngay |
| 2 | `EnsureUserPartner` | `isJoined:true` cho user vận hành (`backend/internal/service/mcn.go:116-124`), gọi ở kích hoạt và trong `BindAccountOnLogin` | Bỏ hai lời gọi này. Trước khi bỏ, kiểm các luồng chọn partner theo header Origin (đăng nhập, `/events`), để user vận hành chưa tự onboarding vẫn vào được Quản lý MCN | Sửa ngay |
| 3 | Bind, guard vai ở bước ký | Bind chỉ xét dòng `isMember` (`backend/internal/service/mcn.go:172-176`), chưa xét dòng `agreed`; không transaction. StartSign, SyncSign, ActivateMember, `McnSyncAnnex` không kiểm | Transaction + guard (INV-03a, INV-03b); chặn khi có dòng `agreed` với MCN khác; không gắn khi trùng email | Sửa ngay |
| 4 | Agree đồng thời, từ chối trên trang mời | Check-then-insert (`backend/pkg/public/service/mcn_invite.go:172-189`); từ chối insert mỗi lần (:274-279) | `isPending` + partial unique; upsert theo (user, link) + partial unique `declinedByCode` | Sửa ngay |
| 5 | Mốc ký, cửa sổ | `startAt = time.Now()`; filter hạn bằng giờ đồng bộ (`backend/pkg/public/service/mcn_annex.go:242`) | `activatedAt`, `feeFrom`, `annex.signedAt`, `sync_capped`. Phải xong trước go-live, vì onboarding lên prod cuối tháng 11 và mọi dòng kích hoạt trên prod phải có `feeFrom` (§11.2) | Sửa ngay |
| 6 | Phụ lục | Hết hạn ký không hỏi econtract (`backend/pkg/public/service/mcn_job.go:67-79`); tạo phụ lục không chống gọi đồng thời, không giới hạn số phụ lục mở (`backend/pkg/public/service/mcn_annex.go:154-203`) | Hỏi econtract trước khi hết hạn; CAS `annex.state`; `annexInFlight`; job `McnAnnexCleanup` | Sửa ngay |
| 7 | `McnEnabled` | Chỉ kiểm lúc tạo hồ sơ (`backend/pkg/admin/service/mcn.go:94`) | Kiểm ở bước onboarding | Sửa ngay |
| 8 | Index `mcn-accounts`, middleware | Không có `uniq(mcn)`; `uniq(user)` không lọc `isCurrent`; middleware không kiểm `banned`, cache mọi route | `isCurrent` + hai partial unique; kiểm `banned`; bỏ cache ở route tiền, PII | Sửa ngay |
| 9 | Lịch sử đăng nhập, mã lỗi | Role `creator` cứng (`backend/pkg/public/service/user.go:1827`); không có `Response409` | Thêm trường `mcn`; thêm `Response409`, map mã locale | Sửa ngay |
| 10 | Khóa job | `SETNX` + `DEL` không kiểm token (`backend/pkg/public/service/mcn_job.go:31-37`) | Token ngẫu nhiên, compare-and-delete | Sửa ngay |
| 11 | Sửa hồ sơ MCN | Ghi đè `name`, `identityNumber` sau `active` (`backend/pkg/admin/service/mcn.go:168-179`) | Khóa `type`, `identityNumber`; đổi `name` thì đặt lại `bank.match` | Sửa ngay |
| 12 | Snapshot phí, ghi sổ Duyệt, sổ MCN | Chưa có; Duyệt chạy đường cũ | `applyMcnFees`, `mcnSnapshot`; `postItem`, `AppendStrict`, `verifyRunTotals`, `LedgerV2`, referral outbox, `completedAt`; `mcn-cash-flows`, `McnLedger`, `ledgerVer` | Phase 5 |
| 13 | Hiển thị phía creator | Chưa khai tiêu đề `mcn_fee`, `mcn_fee_adjustment`; `UpdateStatistic` `$set` cả object | `TitleCashFlowVn/En`; `totalCashMcnFee` trong hai hàm thống kê | Phase 5 |
| 14 | `run_failed` ở admin | Không có nhãn (`admin/src` không có chuỗi `run_failed`); cho Hủy từ `run_failed` (`backend/pkg/admin/service/reconciliation.go:484-489`) | Nhãn "Duyệt lỗi", nút "Duyệt lại"; chặn Hủy; báo BA trạng thái mới | Phase 5 |
| 15 | Chi trả | Chưa có phần MCN; Chuyển tiền creator bỏ qua lỗi ghi sổ | `mcn-payouts`, `TaxPolicyFor`, chặn Lấy danh sách đợt chi khi partner có kỳ `running` hoặc `run_failed` (INV-15), export, khối MCN ở admin; Chuyển tiền và Hoàn tất creator trong transaction (`LedgerV2`) | Phase 6 |
| 16 | Job | 4 job MCN | `McnAnnexCleanup` (10 phút), `ReconRunningWatch` (quá 2 giờ), `LedgerReconcile` (hằng ngày) | Phase 5–6 |
| 17 | Màn MCN | `/mcn/reconciliations` là stub (`backend/pkg/public/handler/mcn.go:119-124`) | Đối soát, số dư, sổ, lệnh chi MCN; tab Người nhận | Phase 7 |
| 18 | Plan | phase-05: `creditMcnFees` delta, ghi net; phase-06: `PayableMcnOf` + `TaxExempt` | Viết lại theo ADR-05 đến 09 | Trước code phase 5 |
| 19 | IDOR eKYC, hợp đồng ② | SSO từ client (§2.5) | Dùng SSO của phiên | Trước go-live |
| 20 | `CreateAnnex` | Chỉ gửi email, SĐT (`backend/pkg/public/service/mcn_annex.go:58-78`); một mã loại phụ lục | Tên MCN, MST, tỷ lệ, ngày; chọn mã mẫu theo loại MCN nếu AT tách mẫu phụ lục (OQ-16, §11.3). Biên bản họp 10/11 ghi "ký 17/11" (team My) | Chờ AT |
| 21 | `cmd/mcn-rebind`, `cmd/mcn-adjust` | Chưa có | Runbook không có UI, dry-run, ticket; `mcn-adjust` cần PO đồng ý (ngoài D7) | `mcn-rebind`: trước go-live. `mcn-adjust`: phase 5, vì chỉ cần khi đã có phí |
| 22 | Tài khoản nhà | Đã code trên `feat/mcn-phase1` (commit `82edb83c7`): trang mời, Agree, Bind, nhãn ở màn MCN. Tài khoản vận hành nhận được link 100% của chính MCN mình, dòng có `house = true`; link dưới 100% trả `MCN_HOUSE_RATE_REQUIRED`; link của MCN khác vẫn chặn. Bind bỏ qua khi user là thành viên MCN khác, hoặc là thành viên chính MCN đó với tỷ lệ dưới 100% | Guard trong transaction, gồm chặn dòng `agreed` với MCN khác ở tạo, kích hoạt MCN và Bind (#3, INV-03b). StartSign so lại CCCD khi `selfCheck = unresolved` (ADR-04) | Sửa ngay |
| 23 | Nhãn tài khoản nhà | Nhãn ở bảng thành viên màn Quản lý MCN đã có (commit `82edb83c7`). Tab Thành viên ở admin đang làm | Nhãn "Tài khoản nhà" theo `house` ở tab Thành viên admin | Phase 4 |
| 24 | Mốc chiến dịch, lệnh theo chiến dịch | Chưa có | `MCN_FEE_EVENT_START_FROM` trong `applyMcnFees`; `event` trên `mcn-cash-flows`, `mcn-payouts`; thuế nhóm; cột chiến dịch ở file ngân hàng và màn đối soát MCN | Phase 5–6 |

Giữ nguyên vì đã đúng: các collection `mcns`, `mcn-documents`, `mcn-invite-links`, `mcn-members`; index `isMember`; CAS theo trạng thái nguồn; Q10, Q13; tỷ lệ 0..100; hai loại MCN; route web và admin; test e2e hiện có (`backend/pkg/admin/service/mcn_e2e_test.go`, `backend/pkg/public/service/mcn_invite_e2e_test.go`, `backend/pkg/public/service/mcn_bind_e2e_test.go`, `backend/pkg/public/router/mcn_*_e2e_test.go`).

### 14.2 So với tech spec v1.0

| Mục v1.0 | v1.0 | Bản này (v2.1) |
|---|---|---|
| §1 Nguyên tắc 1 | Vai MCN qua bảng quan hệ, không `type/role` trên `users` | Giữ (ADR-01) |
| §1 Nguyên tắc 2 | Không đổi trạng thái kỳ, người không liên quan MCN y như cũ | Giữ kết quả tiền và thuế; đổi cách ghi sổ và thêm `run_failed` theo cờ partner (§11.1) |
| §1 Nguyên tắc 4; §3.3, §8.2, §9 | Mọi dòng tiền MCN qua `AddCashFlow`, khóa theo kỳ; phí vào `cash-flows` của `acc.User`; `IsPayableMcnUser` + `TaxExempt` | `McnLedger().Post`, `AppendStrict`, khóa theo (item, dòng quan hệ); sổ `mcn-cash-flows`, lệnh `mcn-payouts`, `TaxPolicyFor` theo payee |
| §2.4, §2.5 | Tỷ lệ 1..99; cờ `open` unique theo user | 0..100; `isMember` theo user + `isPending` theo (user, MCN) + `annexInFlight` theo user |
| §2.6, §8.1, §8.2 | Một `ReconciliationItemMcn` mỗi item, xét thành viên lúc Lấy danh sách; ghi net vì `ActionMustTaxReward` | `mcnSplits[]` theo dòng quan hệ và ngày phát sinh; `+G` và `−fee` |
| §4, §12 | `MCN_EMAIL_IN_USE` khi email đã có user; 5 job | Dùng chung theo PRD Q12 và họp 10/11; thêm 3 job (§14.1 #16) |

### 14.3 Chỗ lệch PRD và bản mẫu BA

| # | Nội dung | PRD, BA | Bản này (v2.1) | Lý do | Người duyệt |
|---|---|---|---|---|---|
| 1 | Ngày bắt đầu tính phí | FR-014: ngày bắt đầu = ngày ký | `feeFrom` = ngày hệ thống kích hoạt; khác ngày ký khi đồng bộ qua nửa đêm, job chậm hoặc econtract lỗi | Không hồi tố qua snapshot đã chốt | PO |
| 2 | Làm tròn | FR-016 từng khoản; BA-03 trên tổng kỳ; SD-04 `floor` | Từng khoản half-up, chặn bởi `floor(cash_r)` | Khớp FR-016; BA-03 sửa cách hiển thị | PO, BA |
| 3 | Phạm vi cờ MCN | FR-016: chỉ partner bật MCN | Tắt cờ không dừng trích phí phụ lục đã ký | Phụ lục là hợp đồng đang có hiệu lực | PO |
| 4 | Trạng thái kỳ | D8, BA-04: giữ trạng thái hiện có | Thêm "Duyệt lỗi" (`run_failed`), chỉ Duyệt lại | Bảo toàn tiền | PO, BA |
| 5 | Đợt chi khi partner có kỳ `running` hoặc `run_failed` | Không quy định | Chặn Lấy danh sách đợt chi (INV-15) | Không chi khoản đang điều tra | PO, Kế toán |
| 6 | Mở ký phụ lục | D18: Chờ ký nhiều MCN | Vẫn Chờ ký nhiều MCN; chỉ mở ký một phụ lục tại một thời điểm | Tránh hai phụ lục SIGNED | PO, BA |
| 7 | Điều chỉnh phí | D7: chỉ bù bằng Thưởng thêm | Thêm runbook `mcn-adjust` cho phí trích sai | Thưởng thêm bị trích phí lần nữa | PO |
| 8 | Thu nhập nội dung của tài khoản vận hành MCN | D14: tính như creator bình thường; Q8: đề xuất miễn khấu trừ | Tài khoản nhà vào MCN 100%, thu nhập vào sổ MCN, thuế theo loại MCN | Họp 10/11, ADR-12. PRD sửa D14, FR-002, FR-012 | PO |
| 9 | Email MCN trùng tài khoản creator | PRD Q12: dùng chung; BA-01: không | Theo PRD Q12 và họp 10/11 | ADR-03. BA sửa BA-01 | BA |
| 10 | Đổi MCN giữa kỳ | D24: chia theo thời gian | Đề xuất giữ công thức chia theo ngày, không có luồng riêng ở phase 1. Chờ PO chốt ở OQ-14 | Họp 10/11 để luồng riêng sang P2 (NG-9) | PO |
| 11 | Chi trả MCN | FR-019: đợt chi chung, chi toàn bộ số dư | Lệnh MCN theo chiến dịch, ngưỡng thuế theo nhóm | Họp 10/11, ADR-14, ADR-09 | PO, Kế toán |
| 12 | Phạm vi trích phí | FR-016 không giới hạn chiến dịch | Chỉ chiến dịch bắt đầu từ mốc áp dụng | Họp 10/11, ADR-13 | PO |

## 15. Câu hỏi và rủi ro

### 15.1 Đã chốt

| Nội dung | Nguồn | Ảnh hưởng thiết kế |
|---|---|---|
| Thuế KOL/KOC 10% trên số chi sau phí, ngưỡng 5.000.000đ mỗi đợt; MCN công ty không khấu trừ | D21 (05/11), D9 | `TaxPolicyFor`; lệch SD-04 ghi ở R-01 |
| Ngày ký có tính phí; từ ngày kết thúc không trích | D20, BA-03 | `FeeWindow` |
| Ngày phát sinh: view là ngày có view, mốc là ngày đạt mốc, Thưởng thêm là ngày Admin tạo | PRD §0 | `D(r)` |
| MCN kiêm creator trên cùng portal, dùng chung tài khoản; gộp chi và thuế một lần: tài khoản nhà MCN đặt 100% cho MCN | Họp 10/11 [seg-056-073, seg-079-089]; thay D14 | ADR-03, ADR-12, INV-03a, INV-03b, INV-19. Đóng OQ-02 cũ (email MCN trùng tài khoản creator) và OQ-03 cũ (thu nhập nội dung của tài khoản vận hành MCN công ty là của cá nhân hay của pháp nhân) |
| MCN chỉ áp cho chiến dịch mới, từ tháng sau go-live | Họp 10/11 [seg-024-031] | ADR-13, INV-20 |
| "Campaign" là chiến dịch (`events`), không phải ADV | Chốt 11/11 | ADR-13, ADR-14 |
| Kế toán chi theo từng chiến dịch, không gộp | Họp 10/11 [seg-091-101] | ADR-14. Áp cho lệnh MCN hay cả lệnh creator: đề xuất chỉ MCN, chờ OQ-13 |
| Không làm luồng riêng cho rời, vào lại, đổi MCN giữa chiến dịch ở phase 1 | Họp 10/11 [seg-007, seg-032, seg-052] | NG-9. Cách tính phí khi việc này xảy ra (chia theo ngày) là đề xuất, chờ OQ-14 |
| Hợp đồng MCN–AT (①) riêng; hợp đồng KOL/KOC–AT (②) riêng, phụ lục ghi tỷ lệ; ký trên FPT e-contract. Biên bản ghi "chuẩn bị version cho cả đối tác là cá nhân và công ty", không nói của hợp đồng nào; phụ lục có tách mẫu hay không ở OQ-16. Biên bản ghi "ký 17/11" (team My) | Họp 10/11 [seg-012-018, seg-239-249] | §11.3, §14.1 #20, OQ-16 |
| Đổi TK ngân hàng MCN không cần maker-checker ở phase 1; dùng audit và Telegram (câu hỏi cũ OQ-12) | NG-5 | §9, R-07 |
| Chờ ký nhiều MCN; ký một MCN thì lời mời khác Hết hiệu lực | D18 | `superseded` |
| Hết 12 tháng tự kết thúc; báo rời trước 15 ngày; MCN chấm dứt có hiệu lực ngay | D19, D15, FR-011 | `FeeWindow` |
| MCN xem kỳ đã hợp tác sau khi thành viên rời | D22 | Xét cả dòng `ended` |
| MCN thấy tên người Chờ ký; lý do hiện cho bên kia | Q10, Q13 | §9 |

### 15.2 Còn mở

| ID | Câu hỏi | Đề xuất mặc định | Tác động nếu khác | Người chốt | Hạn |
|---|---|---|---|---|---|
| OQ-01 | Thu nhập của MCN cá nhân (phí và nội dung tài khoản nhà) khấu trừ 10% như KOL/KOC hay là thu nhập kinh doanh? Biên bản họp 10/11 chưa ghi | `pit_10` trên `groupBase` | Policy khác: thêm policy, cấu trúc giữ nguyên | Kế toán | Trước phase 6 |
| OQ-04 | AT chi theo file xuất (cột TK đang rỗng) hay theo hồ sơ econtract theo SSO? | AT chi theo file xuất; dòng MCN lấy TK từ snapshot `bank` | Chi theo econtract: MCN không nhận tiền qua đợt chi, cần kênh chi riêng | AT, vận hành | Trước phase 6 |
| OQ-05 | Ba câu hỏi cho AT core. (a) Econtract có trả `signed_at` của phụ lục không? (b) Có API tra CCCD eKYC theo SSO không? (c) AT core có gửi sự kiện SIGNED qua webhook HMAC (khuôn `backend/pkg/public/router/routeauth/auth.go:95-130`) không? | (a) Chưa có thì dùng giờ đồng bộ. (b) Chưa có thì lấy CCCD từ `users.contract`. (c) Chưa có thì polling | Thay nguồn, cấu trúc giữ nguyên; webhook giảm R-06 | AT core | Trước phase 5 |
| OQ-06 | Phí quản lý trong phụ lục đã gồm VAT chưa? Kế toán có yêu cầu nhận hóa đơn của MCN công ty trước khi chi? | Đã gồm VAT; không chặn chi theo hóa đơn | Chưa gồm VAT: số trên file khác số trên sổ; chặn theo hóa đơn: thêm `invoiceReceived` lên lệnh | Kế toán | Trước phase 6 |
| OQ-07 | Phụ lục SIGNED sau khi dòng đã Từ chối, Quá hạn, Hết hiệu lực: ai thanh lý trên econtract? | `signedAfterClose`, không trích phí, báo vận hành | – | Legal, AT | Trước go-live |
| OQ-08 | Phụ lục 100% có đủ căn cứ chi thu nhập nội dung của tài khoản nhà cho MCN không (với MCN công ty, khoản này thành doanh thu pháp nhân)? Tài khoản nhà (số dư creator về 0đ vì 100% chuyển sang MCN) có vẫn phải eKYC và ký ② không? | Đủ, vẫn bắt buộc | Không đủ: cần mẫu phụ lục riêng cho tài khoản nhà | Legal, team My | Trước 17/11 |
| OQ-09 | Thời hạn lưu dữ liệu đối soát MCN xem sau khi thành viên rời; DPA có bao phủ (NĐ 13/2023)? | Theo thời hạn chứng từ kế toán | Thêm bộ lọc thời hạn | Legal | Trước phase 7 |
| OQ-10 | Đợt chi hiện bỏ qua creator có số dư dưới Max (lọc `cashRemaining ≥ max(Min, Max)`, `backend/pkg/admin/service/transfer_processing.go:96-104`). Hành vi này có cố ý không? | Giữ cho creator. MCN chỉ xét Min; số dư trên Max thì cắt còn Max (§7.2 bước 4) | – | PO | Trước phase 6 |
| OQ-11 | Hoa hồng người giới thiệu tính trên G hay sau phí? | G, như hiện nay | Đổi `base` của outbox | PO | Trước phase 5 |
| OQ-13 | Chi theo chiến dịch chỉ áp cho lệnh MCN hay cả lệnh creator? Kế toán có chấp nhận nhiều lệnh nhỏ cho cùng một TK MCN, mỗi lệnh một phí chuyển khoản không? | Chỉ lệnh MCN (ADR-14) | Mọi lệnh: đổi đường chi creator, ngoài phase 1 | PO, Kế toán | Trước phase 6 |
| OQ-14 | KOL/KOC rời hoặc đổi MCN khi chiến dịch đang chạy: phí của chiến dịch tính thế nào ở phase 1? | Không chặn; phí chia theo số ngày là thành viên (`FeeWindow`) | Chặn rời tới hết chiến dịch: sửa báo rời, chấm dứt, job hết 12 tháng | PO | Trước phase 5 |
| OQ-15 | Tài khoản vận hành bắt buộc ký phụ lục 100% với MCN của mình trước chiến dịch đầu tiên? | Không chặn bằng hệ thống; báo cáo vận hành | Bắt buộc: chặn đăng ký chiến dịch của tài khoản vận hành chưa là tài khoản nhà (`house = true`) | PO, Legal | Trước go-live |
| OQ-16 | Phụ lục KOL/KOC–AT có tách mẫu theo MCN cá nhân và MCN công ty không? Biên bản họp 10/11 chỉ ghi "chuẩn bị version cho cả đối tác là cá nhân và công ty", không nói của hợp đồng nào | Một mẫu phụ lục, dùng `MCN_ANNEX_CONTRACT_TYPE` | Hai mẫu: thay bằng `MCN_ANNEX_CONTRACT_TYPE_COMPANY` và `MCN_ANNEX_CONTRACT_TYPE_INDIVIDUAL`; `CreateAnnex` chọn mã theo `mcns.type` (§14.1 #20) | AT, team My (nhóm phụ trách mẫu hợp đồng phía AT) | 17/11 |

### 15.3 Rủi ro

| ID | Mô tả | Khả năng | Tác động | Giảm thiểu |
|---|---|---|---|---|
| R-01 | Legal giữ SD-04 (21/10): thuế 10% trên G thay vì số sau phí (D21) | Thấp | Thuế tính lúc chi trên số dư gộp nhiều kỳ; không có ánh xạ lệnh chi về G. Phải phân bổ G vào lệnh ở Lấy danh sách đợt chi (FIFO các bút toán cộng tiền, lưu `taxBaseGross`). Phải quy định ai chịu thuế trên phần phí và giới hạn tỷ lệ: tỷ lệ 95% với G 6.000.000 cho net 300.000, thấp hơn thuế 600.000 | Legal xác nhận lại D21 trước phase 6; sổ giữ `+G` nên dữ liệu đủ để phân bổ |
| R-02 | Ngưỡng 5.000.000đ và suất 10% (D21) là cấu hình dùng chung cho lệnh creator (xét từng lệnh) và lệnh MCN cá nhân (xét trên `groupBase`). Quy tắc này đang chạy cho mọi creator (`backend/internal/constants/cash_flow.go:12`) | Thấp | Quy định đổi thì cả hai loại lệnh cùng lệch | Ngưỡng và suất là cấu hình, snapshot kèm `ruleVersion` lên từng lệnh; Kế toán giữ căn cứ pháp lý |
| R-03 | Dữ liệu ghi dở từ đường cũ (trạng thái b ở §2.3: reward completed, item pending, đã có dòng cộng tiền không mang `idemKey`) | Thấp | Duyệt lại đánh item `rejected` dù tiền đã ghi, như hành vi cũ; E4 không thấy vì dòng cũ không có khóa `rc:` | Trước khi bật cờ, script dry-run liệt kê item pending có reward completed và có `cash-flows.options.reconciliationItem`; xử lý tay theo ticket |
| R-04 | Mẫu phụ lục trên FPT e-contract không kịp mốc 17/11 (giả định A1 của PRD) | Cao | Go-live không có thành viên | Lên phần hồ sơ, mời trước; mở bước ký khi có mẫu (FR-014 bật sau) |
| R-06 | Không có webhook, đồng bộ phụ lục trễ | Trung bình | Thành viên kích hoạt muộn, MCN mất phí của các ngày trước kích hoạt | `SyncSign` khi KOL/KOC quay về; job 15 phút; webhook (OQ-05) |
| R-07 | Đổi TK ngân hàng MCN do tài khoản admin bị chiếm | Thấp | Chi sai người | Audit + Telegram; maker-checker phase sau (NG-5) |
| R-08a | Đặt mốc áp dụng khi phase 6 chưa lên | Trung bình | Phí vào sổ MCN mà chưa có đường chi | Phase 5 và 6 lên cùng bản (§11.4 bước 3). `applyMcnFees` báo lỗi khi mốc đã đặt mà partner chưa bật `LedgerV2`; mốc trống thì không làm gì |
| R-08b | Đặt mốc sau khi đã chạy kỳ đối soát có chiến dịch tháng 12 | Trung bình | Kỳ đó không có phí, MCN mất phí của kỳ đó | Rollout §11.4 bước 6; checklist trước mỗi kỳ tháng 12 |
| R-09 | Màn hình hiển thị phí khác `ΣG × tỷ lệ` (cách tính BA-03) | Cao | Vài đồng chênh, khiếu nại | Màn hình đọc sổ; BA sửa công thức hiển thị (§14.3 #2) |
| R-10 | Tài khoản vận hành không ký phụ lục 100%, vẫn nhận thu nhập nội dung qua lệnh creator riêng | Trung bình | Lại có hai lệnh, hai lần xét ngưỡng cho cùng người (điều họp 10/11 muốn tránh) | OQ-15; báo cáo vận hành; `taxpayerKey` trên file để Kế toán tổng hợp |
| R-11 | Kênh khác do MCN sở hữu (không phải tài khoản vận hành, không trùng CCCD với MCN cá nhân) tham gia bằng link dưới 100% | Trung bình | Thu nhập chia hai lệnh dưới ngưỡng | Hệ thống không nhận diện được; quy định trong Hợp đồng ①, Kế toán rà theo `taxpayerKey` |
| R-12 | Phase 5–6 (sổ, chi, `LedgerV2`) chưa xong trước kỳ đối soát đầu của chiến dịch tháng 12 | Trung bình | Lùi mốc áp dụng, MCN mất phí tháng đầu | Tách go-live onboarding khỏi phase 5–6 (§11.4); demo theo tuần với Hà Lê để chốt sớm |

## 16. Lịch sử thay đổi

| Version | Ngày | Người viết | Thay đổi |
|---|---|---|---|
| 1.0 | 2026-11-04 | Vinh Nguyễn | Bản đầu. Vai MCN qua `mcn-accounts`, thành viên qua `mcn-members`; không thêm loại tài khoản trên `users` |
| 2.0 | 2026-11-10 | Nguyễn Đăng Định | Viết lại kiến trúc tài khoản, sổ cái, chi trả, thuế: MCN là chủ sở hữu phí; sổ `mcn-cash-flows`; lệnh `mcn-payouts`; thuế theo payee; kiêm vai theo PRD Q12; phí theo ngày phát sinh với cửa sổ không phụ thuộc job; `postItem` trong transaction cho mọi khoản theo cờ partner; bất biến vai mức DB; đối chiếu với code nhánh `feat/mcn-phase1` |
| 2.1 | 2026-11-11 | Nguyễn Đăng Định | Cập nhật theo họp 10/11: tài khoản nhà MCN 100%, một lần chi và một lần thuế cho MCN kiêm creator (ADR-12, thay ADR-03 phần thu nhập, INV-03, INV-19); mốc áp dụng theo chiến dịch (ADR-13); lệnh chi MCN theo chiến dịch và ngưỡng thuế theo nhóm (ADR-14, ADR-09); NG-9 đến NG-11; rollout theo mốc thời gian; đóng OQ-02, OQ-03; thêm OQ-13 đến OQ-15, R-10 đến R-12. Rà soát câu chữ cho dễ đọc; sửa mâu thuẫn ví dụ, mốc, cờ `LedgerV2`; số dư âm theo chiến dịch chặn cả MCN khỏi đợt chi; `taxGroupBroken` tách khỏi `tax`; thêm `rejectReason = declined`, `declinedByCode`; tách INV-03 thành INV-03a, INV-03b và R-08 thành R-08a, R-08b; bỏ R-05 (trùng OQ-04); chuyển OQ-12 sang §15.1; thêm OQ-16; §14.1 #5 chuyển sang Sửa ngay, migration M1–M3 chạy cả prod |
