# PRD: Creator Portal dùng chung — Migrate 01 ADV mẫu

Bối cảnh: giai đoạn *Phân tích & thiết kế* (4h) và *Build khung + lớp cấu hình* (98h) đã hoàn tất trong
tháng 9. Portal shell dùng chung hiện chạy được với **1 ADV mẫu nội bộ**, chưa có ADV thật nào chạy trên
đó. Đợt này là bước kiểm chứng: đưa **một ADV thật đang chạy** sang portal dùng chung để xác nhận mô hình
cấu hình đã **đủ dùng**, trước khi migrate hàng loạt.

Mọi số liệu về hiện trạng ADV trong bản này đọc từ `accesstrade-docs/ambassador/frontend-status.md`
(chụp API ngày 2026-05-21) và `accesstrade-docs/general/onboard-adv/` (playbook onboard hiện hành).
Bản 1.1 bổ sung ba nguồn: `ambassador/cache-social-image-minio/baseline-truoc-deploy.md` (đo production
11/09), `ambassador/employee-code/hdsd-admin-employee-code-2026-08-15.md` (HDSD mã nhân viên) và biên bản
họp `plan/2026-08-week-24-28-meeting-note.md` + `plan/2026-09-week-21-28-meeting-note.md`.

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
| Đ1 | Không cần sửa code để onboard ADV | Số commit vào mã nguồn portal **để cấu hình ADV** = **0** (không tính sửa lỗi phát sinh). Commit để **bổ sung năng lực còn thiếu** của lớp cấu hình không tính là đạt — phải ghi vào danh sách thiếu sót và chịu ngưỡng dừng §4.6 |
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
- Xác định **cơ chế xử lý màn hình riêng theo ADV** (MG-010) — kết luận kèm estimate, **không bắt buộc
  build** trong đợt này.

### 3.2 Ngoài phạm vi

- **Migrate ADV thứ hai trở đi** — chỉ bắt đầu sau khi có biên bản xác thực.
- **Gỡ bỏ các folder FE riêng** khỏi repo — giữ nguyên để còn đường lùi.
- **Thay đổi tính năng nghiệp vụ** — đợt này là chuyển nền tảng, không thêm/bớt chức năng cho creator.
- **Đổi thiết kế** — giữ nguyên layout, cỡ chữ, cấu trúc trang như bản FE riêng.
- **Tự phục vụ hoàn toàn cho Campaign Operation** — đợt này DISO vẫn hỗ trợ thao tác; mục tiêu tự phục
  vụ 100% thuộc giai đoạn sau.
- **Xây mới cơ chế nạp màn hình riêng theo ADV** — nếu bước B2b kết luận là thiếu thì ghi nhận kèm
  estimate; việc xây thuộc đợt sau (§4.6).

---

## 4. Chọn ADV mẫu

### 4.1 Hiện trạng đội FE

Hai nguồn, bổ sung cho nhau:

**(a) Đo trên production ngày 11/09/2026** (`ambassador/cache-social-image-minio/baseline-truoc-deploy.md`,
quét `GET /partners/content-features`) — chỉ **5 partner** còn dữ liệu sống:

| Partner | Content trong BXH | Onboard | Ghi nhận |
|---|---:|---|---|
| **parasola** | 8 | ~06/2026 | Nhiều nội dung nhất; domain riêng `parasola-creator.com` (Mắt Bão); nhiều event (`week1`, `parasolasunmatch`); **partner duy nhất bật tính năng mã nhân viên** |
| **fecredit** | 2 | 08/2026 | Mới nhất; onboard bằng **fork thiết kế**, thêm 2 UI: Chiến dịch Affiliate + xác nhận/luồng nhân viên; domain theo chuẩn onboard |
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

**(c) Hai tuỳ biến per-partner phát sinh sau playbook** — không có trong bộ ~21 biến ENV, nhưng ảnh hưởng
trực tiếp đến việc chọn ADV mẫu:

| Tuỳ biến | Trạng thái | Ảnh hưởng đến migrate |
|---|---|---|
| **Mã nhân viên** (76h, release 08/2026) | Bật **riêng cho Parasola**, 12 partner còn lại tắt. Gồm 2 công tắc partner, modal **chặn cứng** khi chưa khai, chiến dịch nội bộ chặn theo nhãn nhân viên, báo cáo tách số liệu, và **backfill bắt buộc** trước khi bật | Migrate Parasola phải chuyển đúng cả 2 công tắc + trạng thái nhãn của toàn bộ user. Sai một trong hai → **mọi user Parasola gặp modal chặn cứng ở lần đăng nhập kế tiếp** |
| **Danh sách campaign affiliate theo partner** (4h, Done 17/09) | Đã thành **năng lực dùng chung**: trang riêng của ADV không còn hiển thị campaign của tất cả partner | Phần dữ liệu của *UI Chiến dịch Affiliate* (FEC) đã per-partner sẵn; phần còn lại là trình bày — cần xác nhận ở B2b |

### 4.2 Bộ tiêu chí chấm điểm

Mục tiêu của đợt này là **xác thực mô hình cấu hình**, không phải "migrate cho xong một ADV". Vì vậy tiêu
chí không chấm *ADV nào dễ nhất*, mà chấm *migrate ADV nào cho nhiều thông tin nhất với rủi ro chấp nhận
được*. Sáu tiêu chí, có trọng số, chấm thang 1–5:

| # | Tiêu chí | Trọng số | Vì sao tính | 1 điểm | 3 điểm | 5 điểm |
|---|---|---:|---|---|---|---|
| **C1** | Chạy thật với dữ liệu thật | 15% | Mô hình cấu hình chỉ bị thử thật khi có creator, nội dung, traffic thật | Không còn dữ liệu sống | Có dữ liệu, campaign vừa hết | Campaign đang chạy, có nội dung trong BXH |
| **C2** | Hồ sơ cấu hình theo playbook hiện hành | 20% | Thiếu hồ sơ thì không phân biệt được *"mô hình thiếu"* với *"hồ sơ ADV cũ thiếu"* — mất luôn giá trị kiểm chứng | Onboard trước playbook, không có hồ sơ | Có một phần hồ sơ | Onboard theo playbook, đủ file *Yêu cầu hệ thống* + bộ `02_Design` |
| **C3** | Bao phủ vùng cấu hình **chưa được kiểm chứng** | 25% | Giai đoạn Build khung chỉ làm theming, resolve domain, nội dung tĩnh, feature flag. Vùng *chưa* làm mới là nơi cần đo | Chỉ chạm branding + nội dung tĩnh | Chạm thêm một vùng tuỳ biến | Chạm đủ 8 nhóm cấu hình MG-001 **và** có module/màn hình riêng |
| **C4** | Rủi ro cutover và khả năng hoàn tác | 20% | Cutover diễn ra trên ADV thật; đường lùi phải nằm trong tay DISO/AT | Đông user + có luồng chặn cứng + DNS do bên thứ ba giữ | Một trong ba yếu tố trên | Ít user, không luồng chặn cứng, DNS trong tầm kiểm soát |
| **C5** | Tính đại diện cho 9 FE còn phải migrate | 10% | Kết luận của đợt này phải dùng lại được cho các đợt sau | Là ngoại lệ, cấu hình một mình một kiểu | Đại diện một phần | Cùng lớp với đa số FE còn lại |
| **C6** | Mức sẵn sàng của các bên | 10% | "Chốt ADV muộn" là rủi ro đã ghi ở §8 | Thiếu dữ liệu, thiếu đầu mối | Có đầu mối, hồ sơ chưa đủ | Có trong sheet Frontend Status, có đầu mối Biz/Ops/Design rõ |

**C2 là vòng loại:** dưới 3 điểm thì không xét tiếp, bất kể tổng điểm. Đây là lý do loại `hdbank`, `lusso`,
`vpbank` — cả ba onboard trước khi playbook `general/onboard-adv/` ra đời.

### 4.3 Kết quả chấm điểm

Chấm cho **5 partner còn dữ liệu sống** ở §4.1(a):

| Partner | C1 (15%) | C2 (20%) | C3 (25%) | C4 (20%) | C5 (10%) | C6 (10%) | **Tổng** | Ghi nhận |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|
| **fecredit** | 4 | 5 | 5 | 4 | 4 | 4 | **4,45** | Dẫn đầu 4/6 tiêu chí, trong đó có hai tiêu chí nặng nhất |
| **parasola** | 5 | 5 | 4 | 2 | 3 | 2 | **3,65** | Dẫn đầu C1; mất điểm ở rủi ro cutover và mức sẵn sàng |
| hdbank | 2 | 2 | 3 | 5 | 4 | 3 | **3,15** | ⛔ Trượt vòng loại C2 |
| vpbank | 3 | 2 | 4 | 2 | 3 | 3 | **2,85** | ⛔ Trượt vòng loại C2 |
| lusso | 1 | 1 | 2 | 5 | 2 | 2 | **2,25** | ⛔ Trượt vòng loại C2 |

`hdbank` và `lusso` được C4 = 5 vì hiện không có traffic — nhưng đúng vì thế cũng gần như không kiểm chứng
được gì (C1 = 2 và 1).

**Độ nhạy của kết luận.** Chênh lệch FEC − Parasola = **+0,80**. Parasola chỉ hơn ở C1 (+1); FEC hơn ở C3
(+1), C4 (+2), C5 (+1), C6 (+2). Thử đổi trọng số để xem kết luận có mong manh không:

| Giả định | FEC | Parasola | Kết luận |
|---|:-:|:-:|---|
| Bỏ hẳn C4 (không tính rủi ro cutover), dồn 20% sang C1 | 4,45 | 4,25 | Vẫn chọn FEC |
| Bỏ hẳn C3 (không tính bao phủ), dồn 25% sang C1 | 4,20 | 3,90 | Vẫn chọn FEC |
| Bỏ **cả** C3 và C4, dồn 45% sang C1 | 4,20 | 4,50 | Đổi sang Parasola |

⇒ Kết luận chỉ đảo khi **bỏ đồng thời** tiêu chí bao phủ và tiêu chí rủi ro cutover — tức khi mục tiêu đợt
này đổi từ *"xác thực mô hình cấu hình"* sang *"migrate ADV nhiều dữ liệu nhất cho xong"*.

### 4.4 Đối chiếu chi tiết FE Credit ↔ Parasola

| | **FE Credit** | **Parasola** |
|---|---|---|
| Thời điểm onboard | 08–09/2026, mới nhất, theo playbook | ~06/2026, theo playbook |
| Nội dung trong BXH (đo 11/09) | 2 | 8 — nhiều nhất |
| Kiểu thiết kế FE | Fork template chung **+ 2 UI mới**: Chiến dịch Affiliate, xác nhận/luồng nhân viên | Fork template chung, **không có màn hình riêng trong FE** |
| Tuỳ biến nền tảng đang bật | Không ghi nhận | **Mã nhân viên** — partner duy nhất bật: 2 công tắc partner, modal **chặn cứng**, backfill bắt buộc, báo cáo tách số liệu |
| Domain | Theo chuẩn onboard — cần xác nhận domain thật ở B2 | **Domain riêng** `parasola-creator.com` (Mắt Bão) — DNS ngoài tầm kiểm soát trực tiếp của DISO/AT |
| Số event / slug | Ít | Nhiều (`week1`, `parasolasunmatch`) |
| Quan hệ đối tác | Vừa go-live 09/2026, đối tác còn đang làm quen | Đã chạy ~3 tháng, đã qua giai đoạn ổn định |
| Có trong sheet Frontend Status | Có (`fec`, onboard 08/2026) | **Chưa có** — §4.1 đã ghi là điểm cần Biz bổ sung |
| Kiểm chứng được điều gì | Mô hình cấu hình **ở mức khó nhất**: feature flag per-ADV có gánh nổi module/màn hình riêng không | Resolve **domain riêng** + nhiều event + tuỳ biến mã nhân viên |
| Kịch bản hỏng nặng nhất khi cutover | Lớp cấu hình không gánh được 2 UI riêng → parity không đạt, phải lùi | Sai cấu hình mã nhân viên → **toàn bộ user Parasola bị modal chặn cứng ở lần đăng nhập kế tiếp**; rollback còn phải chờ DNS bên thứ ba |

**Ba dữ kiện làm đổi kết luận so với bản 25/09:**

1. **Parasola không phải "ADV thuần template".** HDSD mã nhân viên (`ambassador/employee-code/`, 15/08) ghi
   rõ tính năng chỉ bật cho Parasola. Kèm theo là **modal chặn cứng** — không nút đóng, không ESC, không
   click ra ngoài — và yêu cầu **backfill trước khi bật công tắc**; bật sai thì mọi user cũ, kể cả creator
   ngoài chưa từng nghe tới mã nhân viên, bị chặn ở lần đăng nhập kế tiếp. Đây là loại lỗi tệ nhất có thể
   xảy ra trong một đợt cutover. Bản 25/09 xếp Parasola là "không có màn hình riêng" — đúng với phần FE,
   nhưng bỏ sót phần nền tảng.
2. **Một trong hai UI riêng của FEC đã có đường về bản mẫu.** Biên bản họp 24–28/08: *UI Xác nhận nhân viên*
   đã được Design đưa về bản **T-Fluencers** đang chạy (đã sửa xong); *UI Chiến dịch Affiliate* được đề
   nghị đưa về bản **Ambassador KOC** — khi đó còn chờ Design phản hồi, **cần chốt lại trước B1**.
3. **Dữ liệu campaign affiliate đã per-partner.** Hạng mục *Show danh sách campaign affiliate cho từng
   partner* (4h) Done 17/09 — phần dữ liệu của UI Chiến dịch Affiliate đã dùng chung, phần còn lại là
   trình bày.

⇒ Lập luận ở bản 25/09 — *"FEC có màn hình riêng nên sẽ biến đợt kiểm chứng thành đợt xây thêm năng lực"* —
vẫn là rủi ro thật, nhưng **nhỏ hơn** so với lúc viết, và **không còn là lợi thế một chiều của Parasola**:
Parasola cũng có tuỳ biến riêng, chỉ nằm ở nền tảng thay vì ở FE, và hậu quả khi sai thì nặng hơn.

### 4.5 Đề xuất

**Chọn FE Credit (FEC) làm ADV mẫu.** Ba lý do, theo đúng thứ tự trọng số:

1. **Bao phủ (C3 — 25%).** FEC là ADV duy nhất trong nhóm đủ hồ sơ mà chạm được vùng lớp cấu hình **chưa
   từng được kiểm chứng**: module/màn hình riêng theo ADV. Nếu vùng này thiếu thì sớm muộn cũng phải phát
   hiện — phát hiện ở ADV đầu tiên rẻ hơn phát hiện ở ADV thứ năm, đúng lập luận §1.1.
2. **Rủi ro cutover (C4 — 20%).** FEC mới go-live, 2 nội dung trong BXH, không có luồng chặn cứng, domain
   theo chuẩn onboard. Hỏng thì ít người thấy và lùi được nhanh. Parasola kém hơn ở cả ba điểm.
3. **Tính đại diện (C5).** Trong 5 partner còn sống, **4 có tuỳ biến riêng**: Parasola (mã nhân viên), FEC
   (2 UI), hdbank (ẩn Top Creator theo Chủ đề), vpbank (luồng ký hợp đồng + TOS riêng). "ADV thuần
   template" là **ngoại lệ**, không phải phần đông — nên một ADV mẫu có tuỳ biến riêng đại diện đúng hơn
   cho 9 FE còn lại.

**Parasola là ứng viên dự phòng, và là ADV của đợt 2.** Hai việc của Parasola cần chuẩn bị riêng, không nên
gộp vào đợt kiểm chứng đầu tiên: (a) chuyển trạng thái mã nhân viên — 2 công tắc + nhãn của toàn bộ user —
sang portal dùng chung, có backfill; (b) đổi DNS một domain do đối tác/Mắt Bão quản, cần lịch phối hợp với
đối tác. Bù lại, migrate Parasola ở đợt 2 vẫn giữ được giá trị kiểm chứng **domain riêng** (MG-002 ở dạng
khó) mà một ADV dùng domain chuẩn không kiểm chứng được.

**Lưu ý cần AT xác nhận:** kế hoạch tháng 9 (mục 6) mô tả đợt này là *"Chọn ADV có branding đơn giản
nhất"*. Đề xuất này **lệch khỏi mô tả đó một cách có chủ ý**: branding của FEC không phức tạp hơn Parasola,
nhưng FEC có màn hình riêng nên không phải "đơn giản nhất" theo nghĩa rộng. Cần AT xác nhận đổi cách chọn
từ *dễ nhất* sang *giá trị kiểm chứng cao nhất với rủi ro cutover thấp hơn*.

### 4.6 Điều kiện kèm theo và ngưỡng dừng

Chọn FEC chỉ hợp lý khi kèm ngưỡng dừng. Không có ngưỡng thì rủi ro *"đợt kiểm chứng biến thành đợt xây
thêm năng lực"* ở §8 thành hiện thực và vỡ mốc 30/09 — đúng cảnh báo của bản 25/09.

| | Nội dung |
|---|---|
| **Cửa quyết định** | Hết bước **B2b** — spike 4h, lấy trong 40h hiện có (BE 2 / FE 1 / PM 1), không xin thêm giờ |
| **Việc của B2b** | Chốt 2 UI riêng của FEC hiện là (a) module có bản mẫu sẵn — T-Fluencers cho xác nhận nhân viên, Ambassador KOC cho Chiến dịch Affiliate — hay (b) thiết kế mới hoàn toàn; và xác định lớp cấu hình cần gì để nạp được chúng theo ADV |
| **Nếu (a)** | Coi là **bật/tắt module có sẵn theo ADV** → thuộc feature flag per-ADV, giữ nguyên phạm vi và 40h |
| **Nếu (b)** | Kích hoạt **carve-out**: migrate phần chuẩn, đưa 2 UI vào danh sách thiếu sót kèm estimate, **không build trong đợt này**, ghi rõ hạn chế vào biên bản MG-009 |
| **Ngưỡng giờ** | Việc phát sinh ngoài phạm vi cấu hình vượt **8h** (20% của 40h) → dừng build, ghi nhận |
| **Đường lùi chọn ADV** | Nếu carve-out làm parity (MG-006) không thể đạt → **đổi ADV mẫu sang Parasola** trong 1 ngày làm việc, kèm điều kiện đã có phương án mã nhân viên và lịch DNS với đối tác |
| **Người quyết** | PM DISO + đầu mối AT, quyết trong ngày, ghi vào biên bản |

---

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
| Module riêng | UI Chiến dịch Affiliate · UI/luồng xác nhận nhân viên (FEC) | Fork thiết kế + code trong FE riêng |
| Mã nhân viên | 2 công tắc partner (bật tính năng · bắt buộc kiểm tra mã tồn tại) + danh sách mã đã import + nhãn nhân viên của user | Admin — hiện chỉ Parasola bật |

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

Ba toggle của playbook onboard (BXH, hiển thị số tiền trong BXH, cho phép gửi lại nội dung) áp dụng độc
lập cho từng ADV. Kiểm kê toggle phải tính thêm các công tắc per-partner phát sinh **sau** playbook: **2
công tắc mã nhân viên** (hiện chỉ Parasola bật) và **phạm vi danh sách campaign affiliate theo partner**
(dùng chung từ 17/09).

**Tiêu chí chấp nhận:** bật/tắt toggle của ADV mẫu không ảnh hưởng ADV mẫu nội bộ đang chạy song song;
toggle nào chưa có chỗ khai báo per-ADV → vào danh sách thiếu sót.

### MG-010 — Màn hình riêng theo ADV: xác định cơ chế *(bổ sung 28/09)*

FEC có 2 UI không nằm trong template chung: *Chiến dịch Affiliate* và *xác nhận/luồng nhân viên*. Giai đoạn
Build khung chỉ làm theming, resolve domain, nội dung tĩnh và feature flag — **không** làm cơ chế nạp màn
hình riêng theo ADV. Đợt này phải trả lời được: lớp cấu hình hiện tại nạp được 2 UI đó ở dạng bật/tắt module
có sẵn, hay thiếu hẳn một cơ chế.

**Tiêu chí chấp nhận:** có kết luận bằng văn bản ở bước B2b, kèm một trong hai đầu ra — (a) cách khai báo
2 UI bằng cấu hình, đã thử trên môi trường nghiệm thu; hoặc (b) mô tả năng lực còn thiếu kèm estimate, đưa
vào danh sách thiếu sót của MG-009. **Không bắt buộc build** trong đợt này (§4.6).

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
| B1 | Chốt ADV mẫu (§4.5) — **điều kiện tiên quyết, chưa chốt thì chưa khởi động** | AT + PM |
| B2 | Lập bảng đối chiếu cấu hình (MG-001) | PM + BE |
| B2b | **Spike 4h** — chốt cơ chế cho 2 UI riêng của FEC (MG-010) → tiếp tục hay kích hoạt ngưỡng dừng §4.6 | PM + FE + BE |
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
- ☑ Có kết luận về **cơ chế màn hình riêng theo ADV** (MG-010): đủ dùng, hoặc thiếu gì kèm estimate.
- ☑ Có **biên bản xác thực mô hình cấu hình** với kết luận rõ ràng.
- ☑ Bản FE riêng vẫn còn nguyên, vẫn trỏ lại được.

---

## 8. Rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Mô hình cấu hình thiếu trường, phát hiện giữa chừng | Trễ mốc 30/09 | Làm MG-001 **trước** khi code; thiếu thì ghi nhận, không hardcode |
| Lớp cấu hình chưa gánh được 2 UI riêng của FEC | Đợt kiểm chứng biến thành đợt xây thêm năng lực, vỡ mốc 30/09 | Spike B2b **trước** khi code; carve-out + ngưỡng 8h; đường lùi đổi ADV mẫu sang Parasola (§4.6) |
| Chưa rõ *UI Chiến dịch Affiliate* của FEC đã về bản mẫu Ambassador KOC hay giữ thiết kế mới | Sai giả định đầu vào của B2b, ước lượng lệch | Xác nhận với Design (anh Hiếu) **trước B1** — treo từ họp 24–28/08, xem §9 |
| Đối tác FEC vừa go-live, chưa qua giai đoạn ổn định | Sự cố cutover ảnh hưởng quan hệ với đối tác mới | Cutover ngoài giờ cao điểm, thông báo trước cho Biz/đối tác, giữ nguyên FE riêng để lùi trong ≤ 30 phút |
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
- **Design (anh Hiếu)** xác nhận kết luận cuối về *UI Chiến dịch Affiliate* của FEC: đã đưa về bản mẫu
  Ambassador KOC hay giữ thiết kế mới (treo từ họp 24–28/08).
- **Bản thiết kế FEC thực tế đã implement** trong đợt onboard 08–09/2026, kèm danh sách thay đổi so với
  template (task T2.3 của playbook onboard) — đầu vào bắt buộc của B2b.

**Giả định**

- Giai đoạn *Build khung + lớp cấu hình* (98h, Done 24/09) đã bao gồm theming theo cấu hình, resolve ADV
  theo domain/subdomain, quản lý nội dung tĩnh per-ADV và feature flag per-ADV.
- Dữ liệu ADV (creator, nội dung, số liệu) **không cần di chuyển** — portal dùng chung đọc cùng backend,
  đợt này chỉ đổi lớp trình bày. *Giả định này phải được xác nhận ở bước B2; nếu sai, phạm vi và estimate
  đổi đáng kể.*
- Số liệu 5 partner tại §4.1 đo trên production ngày 2026-09-11; cần xác nhận lại trạng thái campaign
  của ADV được chọn ngay trước khi cutover.
- Giả định 2 UI riêng của FEC **dùng được bản mẫu sẵn có** — T-Fluencers cho xác nhận nhân viên, Ambassador
  KOC cho Chiến dịch Affiliate. *Phải xác nhận ở B2b; nếu sai, kích hoạt ngưỡng dừng §4.6.*
- Giả định điểm C1/C4 của FEC (2 nội dung trong BXH, traffic thấp) vẫn đúng ngay trước cutover — FEC đang
  trong giai đoạn tăng trưởng, cần đo lại. Nếu FEC đã đông hơn đáng kể thì C4 tụt và phải chấm lại §4.3.
- Giả định domain thật của FEC nằm trong chuẩn onboard (DNS do AT/DISO điều phối được). Nếu FEC cũng dùng
  domain do đối tác quản thì C4 tụt 1 điểm — chênh lệch với Parasola còn +0,60, kết luận không đổi.

---

## 10. Lịch sử thay đổi

| Bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 25/09/2026 | Bản đầu. Đề xuất ADV mẫu: **Parasola** |
| 1.1 | 28/09/2026 | Đổi đề xuất sang **FE Credit**. Thay §4.2–4.4 bằng bộ **6 tiêu chí có trọng số** + bảng chấm điểm 5 partner + phân tích độ nhạy. Thêm §4.6 *Điều kiện kèm theo và ngưỡng dừng*, MG-010, bước B2b, 3 rủi ro mới. Ghi nhận 2 tuỳ biến per-partner phát sinh sau playbook: mã nhân viên (chỉ Parasola bật) và danh sách campaign affiliate theo partner (dùng chung từ 17/09) |
