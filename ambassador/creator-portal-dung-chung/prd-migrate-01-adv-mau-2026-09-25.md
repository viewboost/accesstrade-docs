# PRD: Creator Portal dùng chung — Migrate 01 ADV mẫu

Bối cảnh: giai đoạn *Phân tích & thiết kế* (4h) và *Build khung + lớp cấu hình* (98h) đã hoàn tất trong
tháng 9. Portal shell dùng chung hiện chạy được với **1 ADV mẫu nội bộ**, chưa có ADV thật nào chạy trên
đó. Đợt này là bước kiểm chứng: đưa **một ADV thật đang chạy** sang portal dùng chung để xác nhận mô hình
cấu hình đã **đủ dùng**, trước khi migrate hàng loạt.

Mọi số liệu về hiện trạng ADV trong bản này đọc từ `accesstrade-docs/ambassador/frontend-status.md`
(chụp API ngày 2026-05-21) và `accesstrade-docs/general/onboard-adv/` (playbook onboard hiện hành).

Workload: **40h** — BE 8 / FE 16 / QC 12 / PM 4. Deadline: **30/09/2026**.

---

## 1. Mục tiêu

Chứng minh rằng portal dùng chung **onboard được một ADV thật mà không cần viết thêm dòng code nào** —
toàn bộ khác biệt giữa các ADV nằm trong cấu hình.

| | Hôm nay | Sau đợt này |
|---|---|---|
| Mỗi ADV | Một folder FE riêng, build white-label riêng (14 folder trong repo) | ADV mẫu chạy trên portal dùng chung, không còn build riêng |
| Onboard ADV mới | Fork thiết kế → điền ~21 biến ENV → build → deploy một FE mới | Nhập cấu hình trên console (với ADV đã migrate) |
| Sửa một lỗi chung | Sửa rồi clone sang từng bản FE đang chạy | Sửa một chỗ, mọi ADV đã migrate nhận cùng lúc |
| Mô hình cấu hình | Chưa được kiểm chứng bằng dữ liệu thật | Có biên bản xác thực: đủ dùng, hoặc thiếu gì và thiếu bao nhiêu |

### 1.1 Vì sao phải migrate 01 ADV trước khi migrate hàng loạt

Portal dùng chung hiện chỉ chạy với ADV mẫu **nội bộ** — dữ liệu do DISO tự tạo, branding do DISO tự
chọn. ADV nội bộ không đại diện cho ADV thật ở ba điểm:

1. **Branding thật có ràng buộc thật** — logo nền trong suốt, banner 2 size (20:8 và 4:3), cover chiến
   dịch 2 bản (Tiêu chuẩn và Stretch), OG image 1200×630, font riêng của brand guide. ADV mẫu nội bộ
   không kiểm tra được các ràng buộc này.
2. **Dữ liệu thật đã tồn tại** — ADV đang chạy đã có creator, có nội dung đã duyệt, có số liệu đối soát,
   có bài CMS. Migrate phải giữ nguyên toàn bộ, không được làm gãy link cũ.
3. **Người dùng thật đang truy cập** — domain đang live, đang có traffic. Cutover phải có đường lùi.

Nếu migrate hàng loạt ngay mà mô hình cấu hình thiếu một trường nào đó, chi phí sửa nhân lên theo số ADV
đã chuyển. Migrate một ADV trước là cách rẻ nhất để phát hiện thiếu sót.

### 1.2 Thế nào là "mô hình cấu hình đủ dùng"

Mô hình được coi là đủ dùng khi đạt **cả ba** điều kiện, đo được:

| # | Điều kiện | Cách đo |
|---|---|---|
| Đ1 | Không cần sửa code để onboard ADV | Số commit vào mã nguồn portal trong quá trình migrate = **0** (không tính sửa lỗi phát sinh) |
| Đ2 | Mọi khác biệt của ADV đều có chỗ khai báo | 100% mục trong bảng §5.1 có trường cấu hình tương ứng; không mục nào phải hardcode |
| Đ3 | Người dùng không thấy khác biệt | Bộ đối chiếu parity §5.6 pass toàn bộ; không có lỗi nghiêm trọng trong 48h sau cutover |

Không đạt một trong ba → mô hình **chưa đủ dùng**, và đợt này vẫn thành công: đầu ra là **danh sách
thiếu sót kèm estimate bổ sung**, làm đầu vào cho kế hoạch tháng 10.

---

## 2. Người dùng

| Vai trò | Quan tâm điều gì |
|---|---|
| **Creator của ADV được migrate** | Trang vẫn vào được bằng link cũ, vẫn đúng nhận diện thương hiệu, bài đã nộp và số liệu không đổi |
| **Campaign Operation (AT)** | Tự cấu hình được ADV trên console: branding, slug, allow domains, toggle, bài CMS — không phải nhờ dev |
| **DISO (dev/QA)** | Có bằng chứng mô hình cấu hình đủ dùng trước khi cam kết migrate hàng loạt |
| **ADV được chọn** | Không gián đoạn chiến dịch đang chạy |

---

## 3. Phạm vi

### 3.1 Trong phạm vi

- Chọn và chốt **01 ADV** theo tiêu chí §4.
- Ánh xạ toàn bộ cấu hình build-time của ADV đó sang cấu hình runtime của portal dùng chung.
- Dựng ADV trên portal ở môi trường nghiệm thu, đối chiếu parity với bản FE riêng đang chạy.
- Cutover domain thật sang portal dùng chung, kèm phương án rollback.
- Theo dõi 48h sau cutover và lập **biên bản xác thực mô hình cấu hình**.

### 3.2 Ngoài phạm vi

- **Migrate ADV thứ hai trở đi** — chỉ bắt đầu sau khi có biên bản xác thực.
- **Gỡ bỏ các folder FE riêng** khỏi repo — giữ nguyên để còn đường lùi.
- **Thay đổi tính năng nghiệp vụ** — đợt này là chuyển nền tảng, không thêm/bớt chức năng cho creator.
- **Đổi thiết kế** — giữ nguyên layout, cỡ chữ, cấu trúc trang như bản FE riêng.
- **Tự phục vụ hoàn toàn cho Campaign Operation** — đợt này DISO vẫn hỗ trợ thao tác; mục tiêu tự phục
  vụ 100% thuộc giai đoạn sau.

---

## 4. Chọn ADV mẫu

### 4.1 Hiện trạng đội FE

Hai nguồn, bổ sung cho nhau:

**(a) Đo trên production ngày 11/09/2026** (`ambassador/cache-social-image-minio/baseline-truoc-deploy.md`,
quét `GET /partners/content-features`) — chỉ **5 partner** còn dữ liệu sống:

| Partner | Content trong BXH | Onboard | Ghi nhận |
|---|---:|---|---|
| **parasola** | 8 | ~06/2026 | Nhiều nội dung nhất; domain riêng `parasola-creator.com`; nhiều event (`week1`, `parasolasunmatch`) |
| **fecredit** | 2 | 08/2026 | Mới nhất; có 2 UI riêng: Chiến dịch Affiliate + luồng nhân viên |
| hdbank | 3 | 2025 | Có tuỳ biến ẩn Top Creator theo Chủ đề |
| lusso | 4 | 2025 | Cấu hình cũ, không theo playbook hiện hành |
| vpbank | 1 | 2025 | Luồng ký hợp đồng riêng, TOS riêng |

**(b) Xác nhận của Biz** trên [Frontend Status](https://docs.google.com/spreadsheets/d/1V2Eb1FaNrxdjhf-LjbacmOaya0Wp8ZqfsgMQz53BBow/edit?gid=0#gid=0)
— 13 folder FE, chia làm ba nhóm:

| Nhóm | FE | Xác nhận của Biz | Ý nghĩa với migrate |
|---|---|---|---|
| **Off hẳn** | `wildrift`, `mbbank`, `flamingo`, `yody` | "Off hẳn" | **Không cần migrate** — loại khỏi phạm vi, cân nhắc gỡ FE khỏi repo |
| **Có lộ trình chạy lại** | `hdbank` (T6/2026), `lusso` (Q2/2026), `vng` (Q2/2026), `vnpay` (Q2/2026), `tpbank` (T8/2026), `anker` (camp mới T9/2026) | "Có lộ trình triển khai lại" | Phải migrate, nhưng **hiện không có traffic** → cutover rủi ro thấp |
| **Đang / chuẩn bị chạy** | `vpbank` ("đã mở camp, chuẩn bị chạy lại"), `turborg` (vừa hết T7), `fec` (onboard 08/2026) | | Cutover phải cẩn trọng |

⇒ Phạm vi migrate thực tế là **9 FE**, không phải 13. Bốn FE "off hẳn" nên được chốt loại bỏ ngay để khỏi
tính vào ước lượng các đợt sau.

**Hai điểm cần Biz bổ sung:** (1) `parasola` **chưa có trong sheet Frontend Status** dù đang là partner
nhiều nội dung nhất trên production; (2) các mốc "triển khai lại" ghi Q2/2026, T6/2026, T8/2026 đều đã
qua — cần cập nhật lại mốc thật.

### 4.2 Tiêu chí chọn

Mục tiêu của đợt này là **xác thực mô hình cấu hình**, nên ADV mẫu phải vừa *chạy thật*, vừa *đại diện*
cho các ADV sẽ migrate sau. Bốn tiêu chí:

1. **Đang chạy thật** — có creator, có nội dung, có traffic.
2. **Cấu hình lập theo playbook hiện hành** — có đủ hồ sơ ~21 biến ENV để ánh xạ 1–1 sang cấu hình
   runtime. ADV onboard từ 2025 không có bộ hồ sơ này.
3. **Đại diện cho phần đông ADV tương lai** — dùng template chung, không phải ngoại lệ.
4. **Rủi ro cutover chấp nhận được** — có đường lùi, không ảnh hưởng quan hệ đối tác đang nhạy cảm.

Tiêu chí 2 là lý do loại hdbank, lusso, vpbank: cả ba onboard trước khi playbook `general/onboard-adv/`
ra đời, hồ sơ cấu hình không đầy đủ, nên nếu migrate gặp trục trặc sẽ khó phân biệt *"mô hình cấu hình
thiếu"* với *"hồ sơ ADV cũ thiếu"* — đúng thứ làm hỏng giá trị kiểm chứng của đợt này.

### 4.3 Đánh giá Parasola và FE Credit

Cả hai đều mới onboard, đều có bộ hồ sơ cấu hình đầy đủ theo playbook. Khác nhau ở chỗ chúng kiểm chứng
**hai thứ khác nhau**.

| | **Parasola** | **FE Credit** |
|---|---|---|
| Thời điểm onboard | ~06/2026 | 08–09/2026 (mới nhất) |
| Nội dung trong BXH | 8 (nhiều nhất) | 2 |
| Kiểu thiết kế | Fork template chung, **không có màn hình riêng** | Fork template chung **+ 2 UI hoàn toàn mới**: Chiến dịch Affiliate, luồng nhân viên |
| Domain | **Domain riêng** `parasola-creator.com` (Mắt Bão, không phải `*.accesstrade.click`) | Theo chuẩn onboard |
| Số event / slug | Nhiều (`week1`, `parasolasunmatch`) | Ít hơn |
| Quan hệ đối tác | Đã chạy ~3 tháng, đã qua giai đoạn ổn định | Vừa go-live, đối tác còn đang làm quen |
| Kiểm chứng được điều gì | Mô hình cấu hình cho **ADV tiêu chuẩn** + resolve **domain riêng** + nhiều event | Mô hình cấu hình ở **mức khó nhất**: feature flag per-ADV có gánh nổi màn hình riêng không |

**Điểm mấu chốt về FE Credit:** hai UI riêng của FEC chính là loại khác biệt mà lớp cấu hình hiện tại
**nhiều khả năng chưa bao phủ** — vì giai đoạn Build khung chỉ làm theming, resolve domain, nội dung tĩnh
và feature flag, không làm cơ chế nạp màn hình riêng theo ADV. Nếu chọn FEC cho lần migrate đầu, khả năng
cao đợt này biến từ *"kiểm chứng mô hình"* thành *"xây thêm năng lực còn thiếu"* — vượt 40h và vượt mốc
30/09.

**Điểm mấu chốt về Parasola:** đây là hình mẫu của phần đông ADV sẽ migrate — fork template, khác nhau ở
branding và nội dung. Thêm vào đó Parasola dùng **domain riêng**, nên migrate nó kiểm chứng luôn yêu cầu
MG-002 ở dạng khó (domain riêng, không phải subdomain có sẵn) — thứ mà một ADV dùng `*.accesstrade.click`
không kiểm chứng được.

### 4.4 Đề xuất

**Chọn Parasola.** Đại diện cho phần đông ADV sẽ migrate, nhiều nội dung nhất trong 5 partner đang sống
trên production, và kiểm chứng được cả resolve domain riêng lẫn nhiều event. Nếu mô hình cấu hình đủ dùng
với Parasola thì đủ dùng cho đa số ADV còn lại.

## 5. Yêu cầu chức năng

### MG-001 — Ánh xạ toàn bộ cấu hình build-time sang cấu hình runtime

Hôm nay mỗi ADV được phân biệt bằng **~21 biến ENV lúc build** cộng với cấu hình phía admin. Portal dùng
chung phải có chỗ khai báo cho **từng mục** dưới đây, không mục nào được hardcode.

| Nhóm | Mục cấu hình hiện tại | Nguồn hôm nay |
|---|---|---|
| Định danh | `APP_NAME`, `PARTNER_ID` (slug), `AMBASSADOR_PARTNER_ID` (ObjectId) | ENV lúc build |
| Domain | `DOMAIN`, Allow domains, Website (CTA "Về đối tác") | ENV + admin |
| Branding | `LOGO_FILE`, `FAVICON_FILE`, `BANNER` (2 size), `OG_IMAGE`, `PRIMARY_COLOR`, `SECONDARY_COLOR`, `FONT` | ENV + file build |
| SEO / social | `OG_TITLE`, `OG_DESCRIPTION`, `SEO_KEYWORDS` | ENV |
| Đo lường | `GTM_ID` | ENV |
| Nội dung tĩnh | `SUPPORT_ARTICLE_ID`, `QA_ARTICLE_ID`, `TERM_ID`, `CONDITION_ID` | Admin (CMS) |
| Chiến dịch | `EVENT_ID`, tên chiến dịch, thời gian, ngân sách, hashtag, tiêu đề BXH | Admin |
| Toggle | Bật/tắt BXH · hiển thị số tiền trong BXH · cho phép gửi lại nội dung | Admin |

**Tiêu chí chấp nhận:** lập bảng đối chiếu 1–1 giữa cột "Mục cấu hình hiện tại" và trường tương ứng trên
portal. Mục nào chưa có trường → ghi vào **danh sách thiếu sót** kèm estimate, không được hardcode để
"cho xong".

### MG-002 — Resolve ADV theo domain

Portal phải nhận ra ADV nào từ domain người dùng truy cập, và **fail-closed**: domain không khớp ADV nào
→ từ chối, không rơi về ADV mặc định.

- Allow domains giữ nguyên quy tắc hiện hành: chỉ tên miền, **không** `https://`, **không** dấu `/` cuối,
  **không** `@`-prefix.
- Slug **không đổi** sau migrate — slug nằm trong URL, đổi là hỏng toàn bộ link cũ (404).

**Tiêu chí chấp nhận:** truy cập bằng domain của ADV mẫu → ra đúng portal của ADV đó; truy cập bằng domain
lạ → bị chặn; link cũ của creator vẫn vào đúng trang.

### MG-003 — Branding theo cấu hình, không build lại

Logo, favicon, banner (2 size), cover chiến dịch (2 bản), OG image, màu chính/phụ, font — tất cả nạp theo
cấu hình của ADV tại runtime.

**Tiêu chí chấp nhận:** đổi logo hoặc màu chính trên console → trang đổi theo mà **không cần build lại và
không cần deploy**.

### MG-004 — Nội dung tĩnh per-ADV

Bốn bài CMS (hỗ trợ, Q&A, điều khoản, điều kiện) và phần mô tả chương trình phải lấy theo ADV đang truy
cập.

**Tiêu chí chấp nhận:** nội dung 4 bài trên portal trùng khớp nội dung đang hiển thị ở bản FE riêng.

### MG-005 — Toggle tính năng per-ADV

Ba toggle hiện có (BXH, hiển thị số tiền trong BXH, cho phép gửi lại nội dung) áp dụng độc lập cho từng
ADV.

**Tiêu chí chấp nhận:** bật/tắt toggle của ADV mẫu không ảnh hưởng ADV mẫu nội bộ đang chạy song song.

### MG-006 — Đối chiếu tương đương (parity) với bản FE riêng

Trước cutover, QA đối chiếu **song song** portal dùng chung và bản FE riêng đang chạy, trên cùng tài khoản
và cùng dữ liệu:

| Nhóm | Điểm đối chiếu |
|---|---|
| Hiển thị | Trang chủ, banner, logo, favicon, màu, font, OG preview khi chia sẻ link |
| Chiến dịch | Danh sách chiến dịch, chi tiết chiến dịch, thể lệ, hashtag, thời gian, ngân sách |
| Creator | Đăng ký/đăng nhập, liên kết mạng xã hội, nộp bài, xem bài đã nộp |
| BXH | Thứ hạng, số liệu, ảnh cover và avatar hiển thị đúng |
| Số liệu | Lượt xem, tiền thưởng tạm tính, lịch sử đối soát — khớp số với bản cũ |
| Nội dung tĩnh | 4 bài CMS + mô tả chương trình |

**Tiêu chí chấp nhận:** không có sai khác về **số liệu**; sai khác về hiển thị (nếu có) phải được ghi nhận
và chấp thuận trước khi cutover.

### MG-007 — Kiểm tra cô lập dữ liệu giữa các ADV

Theo DoD của playbook onboard hiện hành, mọi lần onboard đều phải *verify tenant isolation*.

**Tiêu chí chấp nhận:** tài khoản quản trị phạm vi ADV mẫu không đọc/ghi được dữ liệu của ADV khác trên
portal; nội dung, creator, số liệu của hai ADV không lẫn sang nhau.

### MG-008 — Cutover và rollback

- Cutover thực hiện **ngoài giờ cao điểm**, không vào thứ Sáu.
- Bản FE riêng của ADV mẫu **giữ nguyên, không xoá**, sẵn sàng trỏ domain trở lại.
- Có mốc quyết định rollback rõ ràng và người được quyền quyết định.

**Tiêu chí chấp nhận:** diễn tập rollback thành công trên môi trường nghiệm thu trước khi cutover thật;
thời gian rollback mục tiêu **≤ 30 phút**.

### MG-009 — Biên bản xác thực mô hình cấu hình

Đầu ra bắt buộc của đợt này, kể cả khi kết luận là "chưa đủ dùng":

1. Bảng đối chiếu cấu hình (MG-001) — mục nào đã có trường, mục nào thiếu.
2. Kết quả ba điều kiện Đ1/Đ2/Đ3 tại §1.2.
3. Danh sách thiếu sót kèm estimate bổ sung.
4. Kết luận: **đủ dùng để migrate hàng loạt** / **cần bổ sung trước khi migrate tiếp**.

---

## 6. Yêu cầu phi chức năng

| | Yêu cầu |
|---|---|
| Hiệu năng | Thời gian tải trang của portal không chậm hơn bản FE riêng quá 20% |
| Sẵn sàng | Gián đoạn khi cutover ≤ 15 phút |
| Rollback | ≤ 30 phút kể từ lúc quyết định |
| Theo dõi | Giám sát liên tục 48h sau cutover; có kênh nhận báo lỗi từ Ops |
| Môi trường | Nghiệm thu trên **server UAT** tách biệt môi trường dev (đề xuất đã trao đổi tại họp 22/09). Chưa có UAT → nghiệm thu trên môi trường dev và **ghi rõ hạn chế này vào biên bản** |

---

## 7. Kế hoạch triển khai

| Bước | Nội dung | Vai trò |
|---|---|---|
| B1 | Chốt ADV mẫu (§4.3) — **điều kiện tiên quyết, chưa chốt thì chưa khởi động** | AT + PM |
| B2 | Lập bảng đối chiếu cấu hình (MG-001) | PM + BE |
| B3 | Dựng ADV mẫu trên portal ở môi trường nghiệm thu | BE + FE |
| B4 | Đối chiếu parity (MG-006) + kiểm tra cô lập dữ liệu (MG-007) | QC |
| B5 | Diễn tập rollback | BE |
| B6 | Cutover domain thật | BE + DevOps |
| B7 | Theo dõi 48h + lập biên bản xác thực (MG-009) | QC + PM |

### Định nghĩa Hoàn thành

- ☑ ADV mẫu chạy trên portal dùng chung bằng **domain thật**.
- ☑ Bộ đối chiếu parity pass; không sai khác về số liệu.
- ☑ Kiểm tra cô lập dữ liệu pass.
- ☑ Diễn tập rollback thành công.
- ☑ Theo dõi 48h không có lỗi nghiêm trọng.
- ☑ Có **biên bản xác thực mô hình cấu hình** với kết luận rõ ràng.
- ☑ Bản FE riêng vẫn còn nguyên, vẫn trỏ lại được.

---

## 8. Rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Mô hình cấu hình thiếu trường, phát hiện giữa chừng | Trễ mốc 30/09 | Làm MG-001 **trước** khi code; thiếu thì ghi nhận, không hardcode |
| Lớp cấu hình chưa gánh được màn hình riêng theo ADV | Đợt kiểm chứng biến thành đợt xây thêm năng lực, vỡ mốc 30/09 | Chọn ADV không có màn hình riêng cho lần 1 (§4.4); FEC để lần 2 |
| Chưa có server UAT | Nghiệm thu trên môi trường dev, kết quả kém tin cậy | Ghi rõ hạn chế vào biên bản; đẩy nhanh đề xuất UAT |
| Sai khác số liệu sau cutover | Ảnh hưởng đối soát, mất niềm tin của ADV | Đối chiếu số liệu trước cutover; theo dõi 48h; rollback ≤ 30 phút |
| Chốt ADV muộn | 40h dồn vào ít ngày còn lại | Đưa việc chốt ADV thành mục cần quyết trong buổi họp gần nhất |

---

## 9. Phụ thuộc và giả định

**Phụ thuộc**

- **AT chốt ADV mẫu** — điều kiện tiên quyết của toàn bộ đợt.
- **Campaign Operation** cung cấp bộ tài sản branding của ADV theo chuẩn `02_Design` (logo nền trong
  suốt, banner 2 size, cover 2 bản, OG image 1200×630).
- **DevOps** hỗ trợ trỏ domain lúc cutover và lúc rollback.
- **Server UAT** — nếu AT bố trí kịp, nghiệm thu chạy trên UAT thay vì dev.

**Giả định**

- Giai đoạn *Build khung + lớp cấu hình* (98h, Done 24/09) đã bao gồm theming theo cấu hình, resolve ADV
  theo domain/subdomain, quản lý nội dung tĩnh per-ADV và feature flag per-ADV.
- Dữ liệu ADV (creator, nội dung, số liệu) **không cần di chuyển** — portal dùng chung đọc cùng backend,
  đợt này chỉ đổi lớp trình bày. *Giả định này phải được xác nhận ở bước B2; nếu sai, phạm vi và estimate
  đổi đáng kể.*
- Số liệu 5 partner tại §4.1 đo trên production ngày 2026-09-11; cần xác nhận lại trạng thái campaign
  của ADV được chọn ngay trước khi cutover.
