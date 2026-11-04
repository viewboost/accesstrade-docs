<!-- Chuyển đổi từ 08-Sequence.pdf. Sơ đồ được dựng lại bằng Mermaid từ hình trong PDF; số bước khớp bản gốc. -->

# 08 · Sequence

| Mã | Phiên bản | Ngày | Người soạn | Căn cứ |
| --- | --- | --- | --- | --- |
| MCN-SEQ | 3.0 (final) | 22/10/2026 | PO (Trần Tiến Đạt) | Tài liệu 01 (BR), tài liệu 02 (luồng đối soát), phản hồi Legal 21/10/2026, quyết định PO 21/10/2026, sổ mã `_bao-tri/So-ma-tai-lieu.md` |

Tài liệu liên quan: 05 (use case), 06 (đặc tả chức năng), 07 (state machine), 09 (API), 10 (database).

Tài liệu gồm sơ đồ thành phần (Hình 0) và 8 sơ đồ tuần tự (SD-01…SD-08) cho các điểm tích hợp: hợp đồng điện tử, luồng đối soát, đợt chi trả KOL/KOC, bảng kê và hóa đơn MCN, thông báo, job. Tên API khớp tài liệu 09; trạng thái khớp tài liệu 07.

Quy ước chung cho mọi sơ đồ:

- Mọi lệnh gọi sang hệ thống khác có thể thất bại giữa chừng (hợp đồng điện tử, thông báo, kết quả đợt chi) được ghi vào outbox cùng giao dịch nghiệp vụ rồi gửi đi.
- API nội bộ idempotent theo mã nghiệp vụ: `user_id + period_key + version` cho `settlements:build`, `event_id` cho `payment-status` và webhook hợp đồng.
- Mốc thời gian nghiệp vụ lấy từ dữ liệu đã lưu (`leave_effective_at`, `planned_end_at`, `confirm_deadline`), không lấy giờ job chạy.

| Sơ đồ | Nội dung | Use case |
| --- | --- | --- |
| Hình 0 | Thành phần và ranh giới tích hợp | — |
| SD-01 | Tạo và kích hoạt MCN, xác nhận Quy chế | UC-01, UC-23 |
| SD-02 | Mời và phản hồi lời mời | UC-03, UC-05, UC-07 |
| SD-03 | Ký Phụ lục chỉ định thanh toán | UC-06, UC-08 |
| SD-04 | Đối soát, tách theo ngày phát sinh, lập bản đối soát | UC-13 |
| SD-05 | KOL/KOC xác nhận số và AT chi trả | UC-14, UC-21 |
| SD-06 | Chốt bảng kê, hóa đơn và thanh toán MCN | UC-15, UC-16, UC-17, UC-22 |
| SD-07 | Báo rời có báo trước, kết thúc quan hệ, đổi trạng thái MCN | UC-02, UC-09, UC-10, UC-20 |
| SD-08 | Job hết hạn, nhắc và tự chốt | UC-09, UC-14, UC-18 |

## 1. Thành phần (Hình 0)

```mermaid
flowchart LR
    WebUser["Web người dùng<br/>ambassador.koc.com.vn"]
    WebAdmin["Web admin<br/>admin-ambassador.diso.vn"]
    Api["KOC Ambassador API<br/>(hiện có)"]
    Settle["Đối soát theo cấu hình<br/>(hiện có · SỬA)"]
    Batch["Đợt chi trả KOL/KOC<br/>(menu Xử lý rút tiền hiện có · SỬA)"]
    Users["Người dùng (hiện có)"]
    Job["Job scheduler<br/>khóa phân tán"]
    Mcn["Module MCN · MỚI"]
    Contract["Hợp đồng điện tử<br/>eKYC FPT (hiện có)"]
    Notify["Thông báo (hiện có)"]
    Bank["Xác minh tài khoản ngân hàng<br/>(hiện có)"]

    WebUser --> Api
    WebAdmin --> Api
    Api --> Mcn
    Settle -- "settlements:build sau khi duyệt kỳ" --> Mcn
    Batch -- "payment-status IN_BATCH, ON_HOLD_INELIGIBLE, PAID, PAYMENT_CANCELLED (outbox)" --> Mcn
    Users -- "khóa tài khoản (outbox)" --> Mcn
    Job --> Mcn
    Mcn -- "tạo / hủy / tra cứu hợp đồng (outbox)" --> Contract
    Contract -- "webhook ký (HMAC)" --> Mcn
    Mcn --> Notify
    Mcn --> Bank
```

**Chú thích.** Module MCN có thể là service riêng hoặc module trong backend hiện có; tài liệu chỉ ràng buộc ranh giới API. Hai luồng hiện có phải sửa: luồng đối soát theo cấu hình gửi dòng thu nhập kèm ngày phát sinh sang module (SD-04); luồng đợt chi (menu "Xử lý rút tiền", giữ tên theo OQ-T1) lập đợt từ bản đối soát đã chốt và báo kết quả về module (SD-05).

## 2. SD-01 · Tạo và kích hoạt MCN

Admin tạo hồ sơ, hoàn tất KYB, hợp đồng khung ①, Thỏa thuận xử lý DLCN, tài khoản ngân hàng và ghi nhận bản xác nhận Quy chế, Quy tắc ứng xử mà MCN đã ký ngoài hệ thống; sau đó kích hoạt, hệ thống tạo tài khoản MCN dùng được ngay.

```mermaid
%%{init: {"sequence": {"wrap": true}}}%%
sequenceDiagram
    autonumber
    actor Admin
    participant WA as Web admin
    participant M as Module MCN
    participant U as User service (hiện có)
    participant B as Xác minh ngân hàng
    participant N as Thông báo
    actor MCN

    Admin->>WA: Nhập hồ sơ MCN
    WA->>M: POST /admin/mcns
    M->>U: Kiểm tra email đăng nhập
    U-->>M: chưa tồn tại
    M-->>WA: 201 mcn PENDING_ACTIVATION
    Admin->>WA: Tải hồ sơ KYB, hợp đồng ① ký bằng chữ ký số, Thỏa thuận xử lý DLCN, xác nhận từng mục
    WA->>M: PUT framework-contract (dpa_signed_at, dpa_file), POST documents, PATCH documents/{code}
    Admin->>WA: Nhập tài khoản ngân hàng
    WA->>M: PUT /admin/mcns/{id}/bank-account
    M->>B: verify-account-name(bank, số TK)
    B-->>M: tên chủ tài khoản
    M->>M: So khớp đã chuẩn hóa
    alt Khớp
        M-->>WA: VERIFIED
    else Không khớp
        M-->>WA: MISMATCH_PENDING
        Admin->>WA: Xác nhận khớp có lý do
        WA->>M: POST /admin/mcns/{id}/bank-account/confirm-mismatch
    end
    Note over Admin,MCN: MCN đã xác nhận Quy chế, Quy tắc ứng xử ngoài hệ thống trước khi cấp tài khoản
    Admin->>WA: Ghi nhận bản xác nhận Quy chế, Quy tắc ứng xử (phiên bản, ngày, file)
    WA->>M: PATCH /admin/mcns/{id}/documents {policy_acceptances}
    M->>M: Lưu mcn_policy_acceptances source OFFLINE (evidence_file, recorded_by), audit
    Admin->>WA: Kích hoạt
    WA->>M: POST /admin/mcns/{id}/activate
    M->>M: canActivate(): KYB, hợp đồng ① + DLCN, bank_payable, đã ghi nhận xác nhận Quy chế bản hiện hành
    M->>U: Kiểm tra lại email đăng nhập
    alt Thiếu điều kiện
        M-->>WA: 422 MCN_ACTIVATION_INCOMPLETE {missing}
    else Email đã thuộc người dùng khác
        M-->>WA: 409 MCN_EMAIL_IN_USE
    else Đủ
        M->>U: create_or_get(external_ref=mcn:id, account_type=MCN, referral_enabled=false)
        U-->>M: user_id (dùng được ngay)
        M->>M: Giao dịch: ACTIVE, user_id, status_history, audit, outbox N-01
        M-->>WA: 200 ACTIVE
        M->>N: N-01 email MCN
        N-->>MCN: Email, đăng nhập OTP, dùng ngay mục Quản lý MCN
    end
    opt AT công bố phiên bản Quy chế mới sau khi MCN đã hoạt động (BR-50)
        Admin->>WA: Công bố phiên bản mới
        WA->>M: PUT /admin/mcn-policies
        M->>N: N-29 tới MCN
        MCN->>M: GET /mcn/policies/current
        M-->>MCN: Quy chế chương trình, Quy tắc ứng xử bản mới (M-00)
        MCN->>M: POST /mcn/policies/accept
        M->>M: Lưu mcn_policy_acceptances source ONLINE (phiên bản, accepted_at, ip), audit
    end
```

**Chú thích.**

- Quy chế và Quy tắc ứng xử được MCN xác nhận ngoài hệ thống trước khi cấp tài khoản; Admin ghi nhận ở A-03 (BR-03 điều kiện 4) **[Đã chốt]** (PO 21/10).
- Tài khoản MCN được tạo lúc kích hoạt và dùng được ngay; thao tác lại sau lỗi dùng lại user đã tạo theo `external_ref`.
- Khi AT công bố bản Quy chế mới sau khi MCN đã hoạt động (`PUT /admin/mcn-policies`), N-29 gửi MCN; chưa xác nhận lại trên M-00 thì mời, đề xuất trả `POLICY_NOT_ACCEPTED` **[Giả định]** (OQ-L5). M-00 không dùng lúc PENDING_ACTIVATION.

## 3. SD-02 · Mời và phản hồi lời mời

MCN tìm KOL/KOC, gửi lời mời; KOL/KOC xem nội dung theo BR-11 rồi đồng ý hoặc từ chối.

```mermaid
%%{init: {"sequence": {"wrap": true}}}%%
sequenceDiagram
    autonumber
    actor MCN
    participant WU as Web người dùng
    participant M as Module MCN
    participant N as Thông báo
    actor K as KOL/KOC

    MCN->>WU: Nhập mã/email/SĐT
    WU->>M: GET /mcn/creators/lookup?q=
    M-->>WU: found + invitable + thẻ (chỉ khi mời được)
    MCN->>WU: Tỷ lệ 15, lời nhắn, Gửi
    WU->>M: POST /mcn/invitations {creator_user_id, rate, message}
    M->>M: Giao dịch: ghi MCN (ACTIVE, version, đã xác nhận Quy chế BR-50), khóa creator, kiểm tra BR-08 đến BR-15
    M-->>WU: 201 invitation PENDING, expires_at
    M->>N: N-02 tới KOL/KOC
    N-->>K: Chuông + email
    K->>WU: Mở lời mời
    WU->>M: GET /me/mcn/invitations/{id}
    M-->>WU: MCN, tỷ lệ, ví dụ (thuế trên toàn bộ hoa hồng), thời hạn phụ lục, số ngày báo trước, link Quy chế
    alt Đồng ý
        K->>WU: Tick đã hiểu, Đồng ý
        WU->>M: POST /me/mcn/invitations/{id}/accept {acknowledged_rate: 15}
        M->>M: Giao dịch: ghi MCN, khóa creator, ACCEPTED, hủy lời mời khác, tạo membership (active_slot) và phụ lục JOIN chờ ký
        M-->>WU: 200 {agreement_id, sign_deadline}
        M->>N: N-03 tới MCN
    else Từ chối
        K->>WU: Từ chối (lý do)
        WU->>M: POST /me/mcn/invitations/{id}/decline
        M-->>WU: 200 DECLINED
        M->>N: N-03 tới MCN
    end
    Note over M: Gửi đề xuất đổi tỷ lệ/gia hạn (UC-07) theo cùng mẫu: POST /mcn/members/{id}/proposals, đặt pending_change_slot, thành viên LEAVING thì trả MEMBER_LEAVING
```

**Chú thích.**

- MCN chưa xác nhận phiên bản Quy chế mới công bố sau kích hoạt (M-00): `POLICY_NOT_ACCEPTED`.
- Người không mời được (thuộc MCN khác, kể cả đang chờ ký hoặc đang báo rời, BR-09) chỉ nhận câu chung, không lộ lý do (BR-10).
- Ví dụ trong lời mời dùng số chuẩn: thu nhập 3.000.000đ, tỷ lệ 15%: phí quản lý 450.000đ, thuế TNCN 300.000đ, nhận về 2.250.000đ.

## 4. SD-03 · Ký Phụ lục chỉ định thanh toán (vào mới, đổi tỷ lệ, gia hạn)

KOL/KOC xem Thông báo xử lý DLCN, đồng ý riêng chia sẻ dữ liệu cho MCN, ký phụ lục qua FPT eContract; module nhận kết quả qua webhook.

```mermaid
%%{init: {"sequence": {"wrap": true}}}%%
sequenceDiagram
    autonumber
    actor K as KOL/KOC
    participant WU as Web người dùng
    participant M as Module MCN
    participant E as Hợp đồng điện tử
    participant N as Thông báo

    K->>WU: Mở màn ký phụ lục
    WU->>M: GET /me/mcn/annex-preview/{agreement_id}
    M-->>WU: Nội dung phụ lục, Thông báo xử lý DLCN bản hiện hành (privacy_notice_version)
    K->>WU: Tick đồng ý riêng chia sẻ dữ liệu cho MCN, bấm Ký phụ lục
    WU->>M: POST /me/mcn/agreements/{id}/sign {data_share_consent: true, privacy_notice_version}
    alt Thiếu đồng ý riêng
        M-->>WU: 422 DATA_SHARE_CONSENT_REQUIRED
    else Có đồng ý riêng
        M->>E: check-conditions-ekyc(user)
        alt Chưa eKYC
            E-->>M: chưa đạt
            M-->>WU: 412 EKYC_REQUIRED
            WU-->>K: Dẫn sang /thong-tin-dinh-danh
        else Đã eKYC
            E-->>M: đạt
            M->>M: Cập nhật có điều kiện sign_state CREATING (chặn bấm đôi), lưu đồng ý riêng và phiên bản Thông báo DLCN
            M->>E: Tạo phụ lục từ mẫu Phụ lục chỉ định thanh toán (MCN, tỷ lệ, hiệu lực, thời hạn, số ngày báo trước), hạn ký = sign_deadline
            E-->>M: provider_contract_id, sign_url
            M-->>WU: 200 {sign_url}
            WU-->>K: Mở trang ký
            K->>E: Ký (OTP / chữ ký số)
            E->>M: POST /webhooks/econtract {event_id, contract_id, SIGNED, signed_at, file_url}
            M->>M: Xác thực HMAC(ts.body), chống trùng event_id, received_at = now
            alt Phụ lục còn chờ ký, ký trong hạn, MCN ACTIVE
                M->>M: effective_from = max(signed_at, received_at), data_share_consent_at
                alt JOIN
                    M->>M: agreement ACTIVE, membership ACTIVE, mcn_ever_member = true
                    M->>N: N-04 MCN, KOL/KOC, Admin
                else RATE_CHANGE / RENEWAL
                    M->>M: agreement cũ SUPERSEDED, agreement mới ACTIVE với thời hạn mới
                    M->>N: N-06 MCN, KOL/KOC
                end
            else Đã hủy ở AT, ký sau hạn, hoặc MCN không ACTIVE
                M->>M: provider_status = SIGNED_AFTER_CANCEL, đưa vào A-10
                M->>E: Thu hồi/thanh lý (outbox)
                M->>N: N-17 KOL/KOC, Admin
            end
            M-->>E: 200
        end
    end
    Note over M,E: Không có webhook sau 15 phút: job tra trạng thái theo provider_contract_id, xử lý như webhook
```

**Chú thích.**

- Phụ lục thuộc hợp đồng AT – KOL/KOC ②; Publisher cũ không ký lại hợp đồng gốc (BR-17).
- `privacy_notice_version` khác bản hiện hành: 409 `CONFLICT`, KOL/KOC xem lại Thông báo DLCN bản mới. Quá hạn ký 7 ngày: `AGREEMENT_SIGN_EXPIRED`.
- Webhook không tìm thấy phụ lục: lưu orphan, trả 200, cảnh báo.
- Hiệu lực phụ lục và chuyển trạng thái theo ST-04, ST-05 (tài liệu 07).

## 5. SD-04 · Đối soát, tách theo ngày phát sinh, lập bản đối soát

Luồng đối soát hiện có duyệt kỳ rồi gửi các dòng thu nhập kèm ngày phát sinh sang module; module tính phí quản lý theo ngày phát sinh, thuế, số nhận về và lập bản đối soát chờ KOL/KOC xác nhận.

```mermaid
%%{init: {"sequence": {"wrap": true}}}%%
sequenceDiagram
    autonumber
    participant D as Đối soát (hiện có)
    participant M as Module MCN
    participant Q as Hàng đợi thử lại
    participant N as Thông báo
    actor K as KOL/KOC

    D->>D: Duyệt kỳ đối soát theo cấu hình chiến dịch
    D->>D: Gom dòng thu nhập từng người nhận, mỗi dòng có loại, số tiền g, occurred_at (ngày phát sinh)
    D->>M: POST /internal/settlements:build {user_id, period_key, version, các dòng}
    alt Phản hồi trong thời gian chờ
        M->>M: Kiểm tra trùng user_id + period_key + version, đã có thì trả bản đã lưu
        alt Người nhận là tài khoản MCN
            M->>M: Ghi thu nhập tự chạy, không trích, không TNCN, không qua bước xác nhận, chờ vào bảng kê tháng
        else KOL/KOC
            M->>M: Từng dòng: phụ lục hiệu lực tại occurred_at (gồm thời gian báo rời) và MCN ACTIVE tại occurred_at?
            M->>M: Có thì fee_d = floor(g × rate / 100), không thì fee_d = 0 kèm lý do, lưu koc_settlement_lines CALCULATED
            M->>M: G = tổng g (không gồm quà hiện vật, voucher), D = tổng fee_d, PIT = 10% × G nếu G ≥ mcn.pit_threshold, Net = G − D − PIT
            M->>M: Kiểm Net + PIT + D = G, lệch thì đưa vào hàng lỗi A-10 và dừng
            M->>M: Tạo koc_settlements PENDING_CONFIRM, confirm_deadline = now + 5 ngày, outbox N-22
            M->>N: N-22 tới KOL/KOC
            N-->>K: Chuông + email: G, phí quản lý, thuế, nhận về, hạn xác nhận
        end
        M-->>D: 200 kết quả (settlement_id, G, D, pit, net hoặc tự chạy)
    else Lỗi / quá thời gian
        D->>Q: Giữ kỳ ở trạng thái chờ, chưa hiển thị số cho KOL/KOC
        Q->>M: Gọi lại cùng user_id, period_key, version (10 lần, lũy tiến)
        Q->>Q: Quá số lần → hàng lỗi A-10
    end
    Note over D,M: Ví dụ G 3.000.000, tỷ lệ 15%: phí quản lý 450.000, thuế 300.000, nhận về 2.250.000
```

**Chú thích.**

- Xét theo **ngày phát sinh** của từng khoản, không theo ngày đối soát (BR-26). Thời gian báo rời vẫn là đang hợp tác nên vẫn trích.
- Thuế TNCN = 10% × G (toàn bộ hoa hồng) khi G ≥ `mcn.pit_threshold` **[Đã chốt]** (Legal 21/10); ngưỡng chờ OQ-T9. Quà hiện vật, voucher không tính vào G **[Đã chốt]** (PO 21/10); quà, voucher, hoa hồng affiliate không trích phí quản lý (BR-25).
- Gọi lại cùng `user_id + period_key + version` trả bản đã lưu, không tính lại. Version mới khi bản chưa chốt thì tính lại, dòng cũ VOIDED (ST-06).
- Dữ liệu ngày phát sinh từng loại khoản chờ Tech lead xác nhận **[Giả định]** (OQ-T6).
- Ví dụ số: 2.250.000 + 300.000 + 450.000 = 3.000.000.

## 6. SD-05 · KOL/KOC xác nhận số và AT chi trả

KOL/KOC xác nhận hoặc báo sai số đối soát trong 5 ngày; Admin vận hành xử lý báo sai; Kế toán lập đợt chi từ số đã chốt và luồng đợt chi báo trạng thái về module.

```mermaid
%%{init: {"sequence": {"wrap": true}}}%%
sequenceDiagram
    autonumber
    actor K as KOL/KOC
    participant WU as Web người dùng
    participant M as Module MCN
    actor AV as Admin vận hành
    actor KT as Kế toán
    participant DC as Đợt chi (hiện có)
    participant N as Thông báo

    K->>WU: Mở màn xác nhận số đối soát
    WU->>M: GET /me/settlements/{id}
    M-->>WU: G, phí quản lý (MCN, tỷ lệ, theo ngày phát sinh), thuế 10% × G, Net, confirm_deadline
    alt Xác nhận
        K->>WU: Xác nhận
        WU->>M: POST /me/settlements/{id}/confirm
        M->>M: CONFIRMED, confirm_source = USER, dòng LOCKED, payment_status UNPAID
        M-->>WU: 200 CONFIRMED
    else Báo sai
        K->>WU: Báo sai, nhập lý do
        WU->>M: POST /me/settlements/{id}/dispute {reason}
        M->>M: DISPUTED, dừng đếm hạn, ghi disputes
        M->>N: N-26 tới Admin vận hành
        AV->>M: GET /admin/settlement-disputes
        AV->>M: POST /admin/settlements/{id}/resolve (ADJUSTED kèm dòng sửa hoặc KEPT kèm lý do)
        M->>M: ADJUSTED: dòng cũ VOIDED, dòng mới CALCULATED, tính lại G, D, PIT, Net, version + 1
        M->>M: PENDING_CONFIRM, confirm_deadline = now + 5 ngày
        M->>N: N-25 tới KOL/KOC, KOL/KOC xác nhận lại từ đầu
    else Không phản hồi
        Note over M: Job nhắc trước 24 giờ (N-23), quá hạn thì AUTO_CONFIRMED (N-24), xem SD-08
    end
    KT->>DC: Lập đợt chi trả KOL/KOC (P-01) từ bản đối soát đã chốt (UNPAID, PAYMENT_CANCELLED, ON_HOLD_INELIGIBLE)
    DC->>M: Đọc bản đã chốt (G, D, pit, net)
    DC->>DC: Kiểm điều kiện nhận tiền
    alt Đủ điều kiện (≥ 50.000đ tính trên G chưa trả, eKYC, ngân hàng, MST, hợp đồng)
        DC->>M: POST /internal/settlements/{id}/payment-status IN_BATCH (outbox)
        M->>M: payment_status IN_BATCH, payout_batch_ref
        KT->>DC: Chuyển Net cho KOL/KOC, khấu trừ và nộp TNCN, cấp chứng từ ghi thu nhập chịu thuế G
        alt Chuyển thành công
            DC->>M: POST /internal/settlements/{id}/payment-status PAID (outbox)
            M->>M: payment_status PAID, paid_at
            DC->>N: Thông báo KOL/KOC đã thanh toán (hiện có)
        else Đợt chi bị hủy
            DC->>M: POST /internal/settlements/{id}/payment-status PAYMENT_CANCELLED (outbox)
            M->>M: PAYMENT_CANCELLED, chờ đợt chi sau (IN_BATCH)
        end
    else Chưa đủ điều kiện
        DC->>M: POST /internal/settlements/{id}/payment-status ON_HOLD_INELIGIBLE (outbox)
        M->>M: ON_HOLD_INELIGIBLE, giữ số đã chốt đến khi đủ
    end
    Note over M: Phí quản lý của bản đã chốt vào bảng kê tháng chốt (BR-33), không chờ KOL/KOC nhận tiền
```

**Chú thích.**

- KOL/KOC không bấm rút; AT chủ động chi trả theo đợt (BR-47), menu admin hiện có "Xử lý rút tiền" giữ tên (OQ-T1).
- Mã lỗi: xác nhận khi đã quá hạn `SETTLEMENT_CONFIRM_EXPIRED`; bản đang báo sai `SETTLEMENT_NOT_PENDING`; thao tác trên bản đã chốt `SETTLEMENT_ALREADY_FINAL`; báo sai không có lý do `DISPUTE_REASON_REQUIRED`.
- Dừng đếm khi báo sai (OQ-T7), giữ số khi chưa đủ điều kiện (OQ-T8), trả MCN không chờ KOL/KOC nhận tiền (OQ-T3) là **[Giả định]**.
- Chuyển trạng thái `status` và `payment_status` theo ST-07 (tài liệu 07).

## 7. SD-06 · Chốt bảng kê, hóa đơn và thanh toán MCN

Job chốt bảng kê tháng; MCN xác nhận bảng kê, xuất hóa đơn trước và khai báo từng dòng; Kế toán kiểm tra từng dòng rồi mới trả; Admin vận hành tạm dừng dòng có tranh chấp.

```mermaid
%%{init: {"sequence": {"wrap": true}}}%%
sequenceDiagram
    autonumber
    participant J as Job
    participant M as Module MCN
    participant N as Thông báo
    actor MCN
    actor AV as Admin vận hành
    actor KT as Kế toán
    participant WA as Web admin

    J->>M: Chốt tháng P lúc 00:00 ngày 1 giờ VN (khóa close:P)
    M->>M: Mỗi MCN: gom bản đối soát CONFIRMED, AUTO_CONFIRMED trong P có D > 0 theo từng KOL/KOC, cộng thu nhập tự chạy
    M->>M: Tạo mcn_statements CLOSED, mcn_statement_lines AWAITING_INVOICE (một dòng mỗi KOL/KOC, một dòng tự chạy), không có dòng thì NO_PAYMENT
    M->>N: N-14 tới MCN
    MCN->>M: GET /mcn/statements/{P}
    MCN->>M: POST /mcn/statements/{P}/confirm
    M->>M: Bảng kê MCN_CONFIRMED
    MCN->>M: GET /mcn/statements/{P}/invoice-list
    M-->>MCN: Dòng phí quản lý, họ tên và MST chỉ với KOL/KOC đã đồng ý riêng
    Note over MCN: Xuất HĐ phí quản lý cho từng KOL/KOC, HĐ GTGT tự chạy cho AT (ngoài hệ thống)
    loop Mỗi dòng
        MCN->>M: POST /mcn/statements/{P}/lines/{line_id}/invoice {số, ngày, file}
        M->>M: Dòng INVOICE_SUBMITTED
    end
    KT->>WA: Kiểm tra hóa đơn từng dòng, khớp bảng kê
    WA->>M: POST /admin/mcn-statement-lines/{id}/invoice-review
    alt APPROVE
        M->>M: Dòng READY
    else REJECT kèm lý do
        M->>M: Dòng về AWAITING_INVOICE
        M->>N: N-27 tới MCN
    end
    opt Khiếu nại bằng văn bản MCN – KOL/KOC (UC-22)
        AV->>M: POST /admin/mcn-disputes {mcn_id, user_id, document_file, scope_line_ids}
        M->>M: Dòng trong phạm vi chưa PAID → ON_HOLD (DISPUTE)
        M->>N: N-28 tới MCN, KOL/KOC (tạm dừng)
        Note over M: Tranh chấp còn mở khi chốt bảng kê tháng sau thì dòng mới cùng cặp MCN – KOL/KOC tự ON_HOLD, gắn cùng tranh chấp
        AV->>M: POST /admin/mcn-disputes/{id}/resolve
        M->>M: Dòng về trạng thái trước khi giữ
        M->>N: N-28 tới MCN, KOL/KOC (giải tỏa)
    end
    KT->>WA: Xuất file, chuyển khoản vào TK đứng tên MCN, không khấu trừ thuế
    WA->>M: POST /admin/mcn-payouts/mark-paid {line_ids, paid_at, bank_ref}
    M->>M: Kiểm từng dòng READY, không ON_HOLD, tạo mcn_payouts, dòng PAID, bảng kê PARTIALLY_PAID hoặc PAID
    M-->>WA: 200, hoặc 409 INVOICE_REQUIRED, LINE_ON_HOLD
    M->>N: N-15 tới MCN
```

**Chú thích.**

- Khai hóa đơn trước khi xác nhận bảng kê: `STATEMENT_NOT_CONFIRMED`. Thiếu hóa đơn dòng nào chỉ giữ dòng đó; dòng khác vẫn trả (BR-35).
- Tranh chấp còn mở thì dòng phí quản lý mới của cùng cặp MCN – KOL/KOC cũng tự ON_HOLD **[Đã chốt]** (PO 21/10). Tranh chấp không ảnh hưởng số nhận về của KOL/KOC (BR-48).
- Phí quản lý là khoản AT thanh toán theo chỉ định của KOL/KOC (BR-30). Không có bảng kê âm, không chuyển kỳ (BR-34). VAT dòng tự chạy chờ OQ-T4.
- Ví dụ bảng kê tháng 10/2026: Linh Trần 450.000 + Quang Vũ 250.000 + Hà My 420.000 + tự chạy 1.200.000 = 2.320.000 (chi tiết ở tài liệu 02).

## 8. SD-07 · Báo rời có báo trước, kết thúc quan hệ và đổi trạng thái MCN

KOL/KOC báo rời (hiệu lực sau N ngày, rút lại được), MCN chấm dứt thành viên ngay, Admin tạm dừng, mở lại, chấm dứt MCN.

```mermaid
%%{init: {"sequence": {"wrap": true}}}%%
sequenceDiagram
    autonumber
    actor K as KOL/KOC
    actor MCN
    actor A as Admin
    participant M as Module MCN
    participant E as Hợp đồng điện tử
    participant N as Thông báo

    K->>M: POST /me/mcn/leave {reason?}
    alt Đã LEAVING
        M-->>K: 409 LEAVE_ALREADY_REQUESTED
    else ACTIVE hoặc PAUSED
        M->>M: Giao dịch: khóa creator, membership LEAVING, leave_requested_at, leave_effective_at = 00:00 giờ VN của ngày (ngày báo + leave_notice_days), hủy đề xuất và phụ lục thay đổi chờ ký
        M->>E: Hủy phụ lục chờ ký (outbox)
        M-->>K: 200 {leave_effective_at}
        M->>N: N-07 MCN, KOL/KOC, Admin (ghi rõ ngày hiệu lực)
    end
    Note over M: Thời gian báo trước vẫn là đang hợp tác, phí quản lý vẫn trích. Đến leave_effective_at job chuyển ENDED (SD-08)
    opt Rút lại trước ngày hiệu lực
        K->>M: POST /me/mcn/leave/cancel
        alt Còn LEAVING, chưa đến leave_effective_at
            M->>M: membership LEAVING → ACTIVE (PAUSED nếu MCN đang tạm dừng), leave_cancelled_at, phụ lục giữ nguyên
            M->>N: N-21 MCN, Admin
        else Không còn LEAVING hoặc đã quá hạn
            M-->>K: 409 LEAVE_NOT_PENDING
        end
    end
    MCN->>M: POST /mcn/members/{id}/terminate {reason}
    M->>M: Giao dịch: membership ENDED (MCN_REMOVED) ngay, kể cả khi đang LEAVING, phụ lục ENDED effective_to = now, hủy đề xuất và phụ lục chờ ký
    M->>E: Hủy phụ lục chờ ký (outbox)
    M->>M: Đối soát lần cuối, thu hồi quyền xem dữ liệu của MCN với thành viên này
    M->>N: N-08
    A->>M: POST /admin/mcns/{id}/suspend {reason}
    M->>M: MCN SUSPENDED, hủy lời mời, đề xuất, phụ lục chờ ký, membership ACTIVE → PAUSED, LEAVING giữ nguyên ngày hiệu lực, mở khoảng SUSPENDED (không trích phí quản lý)
    M->>E: Hủy phụ lục chờ ký (outbox)
    M->>N: N-11 MCN và thành viên
    A->>M: POST /admin/mcns/{id}/resume
    M->>M: MCN ACTIVE, membership PAUSED → ACTIVE, LEAVING giữ nguyên, mở khoảng ACTIVE
    M->>N: N-12
    A->>M: POST /admin/mcns/{id}/terminate {reason}
    M->>M: MCN TERMINATED, mọi membership ENDED (MCN_TERMINATED) kể cả LEAVING, đối soát lần cuối, thu hồi quyền xem dữ liệu
    M->>N: N-13
```

**Chú thích.**

- Báo rời ghi nhận tại thời điểm máy chủ nhận yêu cầu; rời có hiệu lực lúc 00:00 giờ VN của ngày (ngày báo + `leave_notice_days`), mặc định 15 ngày (Legal cho phép 15–30, OQ-L2). Ví dụ Quang Vũ báo rời 05/10/2026, rời có hiệu lực 00:00 20/10/2026.
- Được báo rời cả khi thành viên PAUSED (MCN đang tạm dừng) **[Đã chốt]** (PO 21/10). MCN tạm dừng khi thành viên đang báo rời: giữ LEAVING, ngày hiệu lực không đổi, không trích phí quản lý ngày dừng (ST-05, tài liệu 07).
- MCN chấm dứt thành viên và Admin chấm dứt MCN có hiệu lực ngay tại thời điểm máy chủ nhận yêu cầu, kể cả khi thành viên đang báo rời (BR-22).
- Phí quản lý phát sinh trước khi kết thúc vẫn vào bảng kê và trả cho MCN (BR-06, BR-23).

## 9. SD-08 · Job hết hạn, nhắc và tự chốt

Các job định kỳ xử lý hết hạn lời mời, đề xuất, hạn ký, rời có hiệu lực, phụ lục hết hạn, nhắc và tự chốt bản đối soát.

```mermaid
%%{init: {"sequence": {"wrap": true}}}%%
sequenceDiagram
    autonumber
    participant J as Job 15 phút
    participant M as Module MCN
    participant E as Hợp đồng điện tử
    participant N as Thông báo

    J->>M: expire_invitations(), expire_proposals()
    M->>N: N-05 tới MCN
    J->>M: expire_signatures()
    M->>E: Hủy phụ lục quá hạn ký (outbox)
    M->>N: N-05 tới MCN, KOL/KOC
    J->>M: Kết thúc thành viên LEAVING đã đến leave_effective_at
    M->>M: membership ENDED (CREATOR_LEFT), phụ lục ENDED effective_to = leave_effective_at, hủy thay đổi chờ
    M->>M: Đối soát lần cuối, thu hồi quyền xem dữ liệu của MCN
    M->>N: N-20 tới MCN, KOL/KOC
    J->>M: end_expired_agreements() gồm thành viên Tạm dừng và Đang báo rời
    M->>M: phụ lục ENDED effective_to = planned_end_at, membership ENDED (CONTRACT_EXPIRED), hủy thay đổi chờ
    M->>N: N-09
    J->>M: Nhắc hạn xác nhận: bản đối soát PENDING_CONFIRM còn mcn.settlement_reminder_before_hours (24 giờ)
    M->>N: N-23 tới KOL/KOC (một lần mỗi hạn)
    J->>M: Tự chốt bản đối soát PENDING_CONFIRM quá confirm_deadline (mcn.settlement_confirm_days = 5)
    M->>M: AUTO_CONFIRMED, confirm_source = AUTO, dòng LOCKED, payment_status UNPAID
    M->>N: N-24 tới KOL/KOC
    J->>M: poll_pending_contracts()
    M->>E: GET trạng thái phụ lục
    E-->>M: SIGNED / chưa
    Note over J,M: Job 08:00 giờ VN: nhắc phụ lục hết hạn ở mốc 30, 15, 7, 1 ngày (mcn.expiry_reminder_days, bỏ qua MCN Tạm dừng) → N-10
```

**Chú thích.**

- Mỗi job chạy theo lô, idempotent, có khóa phân tán; mốc thời gian lấy từ dữ liệu đã lưu (`leave_effective_at`, `planned_end_at`, `confirm_deadline`), không lấy giờ chạy job.
- Bản đối soát `DISPUTED` không tự chốt **[Giả định]** (OQ-T7). Tự chốt theo khoản 2 Điều 393 BLDS và hợp đồng ②; căn cứ cho KOL/KOC không thuộc MCN chờ OQ-L3.
- Phụ lục hết hạn trước ngày rời có hiệu lực thì kết thúc theo `CONTRACT_EXPIRED` (ST-04, ST-05).
