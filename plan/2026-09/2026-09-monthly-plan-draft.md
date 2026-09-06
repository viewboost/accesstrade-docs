---
title: "[DISO] Kế hoạch triển khai Tháng 9/2026 (Nháp)"
date: 2026-09-04
status: draft
---

> ⚠️ **BẢN NHÁP NỘI BỘ** — dùng để đưa vào phiên lập kế hoạch tháng 9. Workload là ước lượng
> sơ bộ của PM dựa trên LOC/effort ghi trong tài liệu gap, **chưa qua dev estimate**. Deadline
> là mốc đề xuất, chưa chốt với ADV.
>
> 🔴 **Bản này đã gộp 2 nguồn:** (a) hạng mục port từ gap analysis, (b) 5 dòng đã có sẵn trên
> tab `Plan tháng 9` của sheet kế hoạch. Tổng nhu cầu **435h** so với chuẩn hợp đồng tháng 9
> chỉ còn **149h** — xem mục *Ràng buộc tháng 9* bên dưới, **chưa chốt phương án cắt scope**.

---

# KẾ HOẠCH THÁNG 9/2026 — AMBASSADOR (NHÁP)

## Bối cảnh

Ambassador là sản phẩm được đầu tư trong giai đoạn tới. Hướng đi: **kéo những chức năng đã
production-tested từ T-Fluencers và vCreator về Ambassador**, thay vì build lại từ đầu.

Nguồn: [gap-analysis-priority.md](https://github.com/viewboost/accesstrade-docs/blob/main/general/gap-analysis-priority.md)
— 42 gap giữa 3 sản phẩm, trong đó 20 gap có hướng port **vào** Ambassador.

**Đã hoàn thành trước tháng 9:**

| # | Chức năng | Nguồn | Trạng thái |
|---|-----------|-------|------------|
| 2 | InfluencerProfile — collection riêng, enrich qua at-core, brand portal browse/filter theo tier, auto-approve config | T-Fluencers | ✅ Done (Ambassador) |
| 32 | EmployeeRegistry — mã nhân viên 18 field, match engine 10 action, import Excel từ HR | vCreator | ✅ Done (Ambassador) |

> Gap #2 xong đã **mở khoá** cho gap #16 (Profile Review + Rating) và #24 (Campaign matching
> engine) — hai hạng mục này trước đây bị chặn vì cần `profile_id` để reference.

---

## ⛔ Ràng buộc tháng 9 — đọc trước khi chốt scope

**Chuẩn hợp đồng tháng 9 giảm còn khoảng một nửa so với tháng 7–8:**

| | BE | FE | QC | PM | Total |
|---|---:|---:|---:|---:|------:|
| Tháng 7 & tháng 8 | 81 | 77 | 77 | 60 | **295h** |
| **Tháng 9** | 53 | 38 | 38 | 20 | **149h** |

**Nhu cầu hiện tại so với trần — vỡ ở mọi vai, không riêng tổng:**

| | BE | FE | QC | PM | Total | % chuẩn |
|---|---:|---:|---:|---:|------:|--------:|
| Mục 1 — Ổn định hiển thị ảnh & nội dung | 40 | 32 | 20 | 6 | 98 | |
| Mục 2 — Creator Portal dùng chung | 80 | 112 | 48 | 32 | 272 | |
| Mục 3 — Hạng mục đã có trên sheet | 25 | 20 | 18 | 2 | 65 | |
| **TỔNG NHU CẦU** | **145** | **164** | **86** | **40** | **435** | **292%** |
| Chuẩn hợp đồng T9 | 53 | 38 | 38 | 20 | 149 | 100% |
| **Vượt trần** | **+92** | **+126** | **+48** | **+20** | **+286** | |
| *tỷ lệ theo vai* | 274% | **432%** | 226% | 200% | 292% | |

> **FE là vai vỡ nặng nhất — 164h trên trần 38h (432%).** Creator Portal một mình đã ngốn
> 112h FE. Nếu giữ Creator Portal trong tháng 9 thì gần như không còn chỗ cho bất cứ hạng mục
> FE nào khác.

**Bù trừ giờ luỹ kế:** tháng 8 kết thúc ở **+138h** vượt chuẩn (BE +250 / FE −9.5 / QC −8 /
PM −95). Con số này chưa nghiệm thu xong nên còn có thể điều chỉnh — tháng 7 sau nghiệm thu đã
bị chỉnh từ +161.5h xuống +132h. Ô `Bù trừ giờ tháng 8` trên sheet hiện **đang để trống**.

> ⚠️ Tồn tại một nghịch lý cần đưa ra bàn: định hướng là **đầu tư cho Ambassador**, nhưng khối
> lượng hợp đồng lại **giảm một nửa**. Hai việc này không đi cùng nhau được — cần AT làm rõ.

---

## 1. Ổn định hiển thị ảnh & nội dung

Ba hạng mục nhỏ, không phụ thuộc nhau, có pattern sẵn ở dự án nguồn nên rủi ro thấp.

| STT | Hạng mục | Mô tả | Tài liệu | Deadline | BE | FE | QC | PM | Total (h) | Trạng thái |
|-----|----------|-------|----------|----------|---:|---:|---:|---:|----------:|------------|
| 1 | Cache ảnh cover content về MinIO | Ảnh cover của content đang trỏ thẳng vào CDN của social, signature hết hạn thì ảnh vỡ.<br>**Tác động: bảng xếp hạng (BXH) sẽ không còn bị mất ảnh.**<br>Port pattern `cover_host.go` từ T-Fluencers (159 LOC, commits `dcd358bd` + `7197a1bd`) — hạ tầng MinIO của Ambassador đã có sẵn, chỉ thiếu service layer. | [Gap #42](https://github.com/viewboost/accesstrade-docs/blob/main/general/gaps/p1/42-cache-content-cover-to-minio.md) | 12/09 | 16 | 4 | 6 | 2 | 28 | ⚪ Not Started |
| 2 | Cache avatar về MinIO + resize 3 size | Avatar creator đang dùng URL social trực tiếp (TikTok/Google/Facebook) → hết hạn thì vỡ ảnh, đồng thời **lộ đường dẫn gốc sang bên thứ ba**.<br>**Tác động: xử lý vấn đề bảo mật mà phía Gen-Green đã nêu.**<br>Port từ T-Fluencers: cache permanent về MinIO + resize 3 kích thước. Dùng chung module `resizeimage` đã có. | [Gap #17](https://github.com/viewboost/accesstrade-docs/blob/main/general/gaps/p2/17-upload-avatar-cache.md) | 19/09 | 16 | 8 | 6 | 2 | 32 | ⚪ Not Started |
| 3 | Editor article/news: HTML → Markdown | Thay `braft-editor` (xuất HTML) bằng `@uiw/react-md-editor`. Bổ sung upload ảnh trong editor.<br>Lý do: HTML dán qua lại giữa các bài mất format, khó soạn bằng AI, preview kém. Package đã được cài sẵn ở vCreator, chỉ chưa wire.<br>Cần kèm **script migrate nội dung HTML cũ sang Markdown**. | [Gap #41](https://github.com/viewboost/accesstrade-docs/blob/main/general/gaps/p1/41-content-editor-html-to-markdown.md) | 19/09 | 8 | 20 | 8 | 2 | 38 | ⚪ Not Started |
| | **Tổng mục 1** | | | | **40** | **32** | **20** | **6** | **98** | |

**Ghi chú kỹ thuật:** hạng mục 1 và 2 dùng **cùng một pattern** (tải ảnh về MinIO, đổi URL trả
về, cron dọn ảnh mồ côi). Đề xuất **gộp thành 1 PR** — làm tách ra sẽ tốn thêm khoảng 8h do
phải review và test hai lần cùng một luồng.

---

## 2. Creator Portal dùng chung cho các ADV

Hạng mục lớn nhất của tháng. Hiện mỗi ADV mới lại dựng một trang creator riêng → chi phí
onboard tăng tuyến tính theo số ADV, và mỗi lần sửa lỗi phải sửa ở nhiều nơi.

Mục tiêu: **một codebase portal duy nhất**, phân biệt ADV bằng cấu hình (branding, domain,
nội dung, chức năng bật/tắt) thay vì bằng bản clone.

| STT | Hạng mục | Mô tả | Tài liệu | Deadline | BE | FE | QC | PM | Total (h) | Trạng thái |
|-----|----------|-------|----------|----------|---:|---:|---:|---:|----------:|------------|
| 4 | Creator Portal dùng chung — Phân tích & thiết kế | Khảo sát các trang creator đang chạy, tách phần **chung** khỏi phần **riêng theo ADV**. Chốt mô hình cấu hình: branding (logo/màu/font), domain & routing, nội dung tĩnh (thể lệ, hướng dẫn), feature flag theo ADV, cấu trúc phân quyền.<br>Output: PRD + sơ đồ kiến trúc + danh sách ADV sẽ migrate. | *chờ tạo PRD* | 12/09 | 8 | 8 | 0 | 16 | 32 | ⚪ Not Started |
| 5 | Creator Portal dùng chung — Build khung + lớp cấu hình | Dựng portal shell dùng chung: theming theo cấu hình, resolve ADV theo domain/subdomain, quản lý nội dung tĩnh per-ADV trong admin, feature flag per-ADV.<br>Chưa migrate ADV nào — chỉ chạy được với 1 ADV mẫu nội bộ. | *chờ tạo PRD* | 30/09 | 40 | 64 | 24 | 8 | 136 | ⚪ Not Started |
| 6 | Creator Portal dùng chung — Migrate 01 ADV mẫu | Chuyển một ADV đang chạy sang portal dùng chung để xác thực mô hình cấu hình đủ dùng. Chọn ADV có branding đơn giản nhất.<br>⚠️ **Phụ thuộc hạng mục 5** — nếu 5 trượt thì đẩy sang T10. | *chờ tạo PRD* | 30/09 | 8 | 16 | 12 | 4 | 40 | ⚪ Not Started |
| 7 | Vòng đời mật khẩu tài khoản staff | Đi kèm hạng mục Creator Portal để tối ưu chung phần tài khoản.<br>Hiện admin tạo mật khẩu thủ công rồi gửi qua chat — **là vấn đề bảo mật thật**. Port từ T-Fluencers: `InviteStaff`, `ResendInvite`, `BulkInvite`, `VerifyInviteToken`, `AcceptInvite`, `ForgotPassword`, `ResetPassword`, `UpdateMyPassword` + field `InviteToken`/`ResetToken` + mẫu email.<br>T-Fluencers có 980 LOC / 18 method, Ambassador mới 453 LOC / 8 method (~46%).<br>**Đề xuất ghép luôn gap #12** (rate limit đăng nhập admin + audit log mọi lần thử) — cùng vùng code, thêm khoảng 8h. | [Gap #40](https://github.com/viewboost/accesstrade-docs/blob/main/general/gaps/p1/40-staff-account-password-and-invite-flow.md) · [Gap #12](https://github.com/viewboost/accesstrade-docs/blob/main/general/gaps/p3/12-admin-login-security.md) | 26/09 | 24 | 24 | 12 | 4 | 64 | ⚪ Not Started |
| | **Tổng mục 2** | | | | **80** | **112** | **48** | **32** | **272** | |

---

## 3. Hạng mục đã có trên sheet `Plan tháng 9`

Các dòng đã được nhập sẵn trên tab kế hoạch, **không nằm trong gap analysis**. Ba dòng chưa có
estimate — cần dev ước lượng trước khi chốt tổng.

| STT | Hạng mục | Mô tả | Dự án | Tài liệu | Deadline | BE | FE | QC | PM | Total (h) | Trạng thái |
|-----|----------|-------|-------|----------|----------|---:|---:|---:|---:|----------:|------------|
| S1 | Clone Xử lý lệch view từ Ambassador qua T-Fluencers | 1. Xây dựng cơ chế tính toán sao cho tường minh view content, view tính thưởng, tiền thưởng tương ứng.<br>2. Thêm Email Alert. | **T-Fluencers** | PRD lệch view · PRD alert | *chưa có* | 24 | 16 | 16 | 2 | 58 | ⚪ Not Started |
| S2 | Xây dựng FE landing page template | 1. Tạo 1–2 theme cho LDP.<br>2. Customize theo branding. | Ambassador | — | *chưa có* | — | — | — | — | **chưa est** | ⚪ Not Started |
| S3 | Clone fix vấn đề bảo mật API từ Gen-Green sang Ambassador và T-Fluencers | Xử lý các vấn đề bảo mật API. | Ambassador | — | *chưa có* | — | — | — | — | **chưa est** | ⚪ Not Started |
| S4 | Xử lý lỗi liên kết TikTok khi hết hạn | Khi TikTok hết hạn, không thực hiện liên kết lại được.<br>*Impact: ảnh hưởng đến trải nghiệm người dùng.* | Ambassador | Request | 03/09 | 1 | 4 | 2 | 0 | 7 | ✅ Done |
| S5 | Cải tiến luồng phân nhóm nhân viên trên Ambassador | Đợt rồi hệ thống chỉ làm riêng cho các FE. | Ambassador | — | *chưa có* | — | — | — | — | **chưa est** | ⚪ Not Started |
| | **Tổng mục 3** *(chỉ tính 2 dòng đã có estimate)* | | | | | **25** | **20** | **18** | **2** | **65** | |

**Ba điểm cần đối chiếu với mục 1 và 2:**

1. **S3 có thể trùng hạng mục 2.** Hạng mục 2 (cache avatar) ghi tác động là *"xử lý vấn đề bảo
   mật mà phía Gen-Green đã nêu"*, còn S3 là *"clone fix vấn đề bảo mật API từ Gen-Green"*. Cần
   xác định đây là **một** vấn đề hay **hai** vấn đề khác nhau (lộ URL ảnh gốc vs lỗ hổng API) —
   nếu là một thì gộp, tránh est hai lần.
2. **S5 nối tiếp gap #32** (EmployeeRegistry) đã Done. Đây là phần mở rộng từ "chỉ riêng FE"
   sang phân nhóm tổng quát — nên gắn nhãn là *continue* của #32 chứ không phải hạng mục mới.
3. **S1 làm vỡ giả định "tháng 9 thuần Ambassador"** của bản nháp này. S1 là việc của
   **T-Fluencers** và chiếm 58h — tức **39% toàn bộ ngân sách 149h** của tháng. Đây là chiều
   ngược lại: Ambassador là bên **cho**, T-Fluencers là bên nhận.

---

## 🔢 Tổng hợp workload Tháng 9/2026 (nháp)

| Nhóm chức năng | BE | FE | QC | PM | Total (h) |
|----------------|---:|---:|---:|---:|----------:|
| 1. Ổn định hiển thị ảnh & nội dung | 40 | 32 | 20 | 6 | 98 |
| 2. Creator Portal dùng chung | 80 | 112 | 48 | 32 | 272 |
| 3. Hạng mục đã có trên sheet | 25 | 20 | 18 | 2 | 65 |
| **TỔNG NHU CẦU** | **145** | **164** | **86** | **40** | **435** |
| Chuẩn hợp đồng tháng 9 | 53 | 38 | 38 | 20 | **149** |
| **Vượt trần** | +92 | +126 | +48 | +20 | **+286** |

> 🔢 **Tổng nhu cầu ~435 giờ trên trần 149 giờ — gấp 2.9 lần.** Creator Portal một mình đã là
> **272h (63%)**, gấp gần **2 lần** toàn bộ ngân sách tháng.

**Ngân sách còn lại nếu giữ nguyên các dòng đã có trên sheet (mục 3):**

| | BE | FE | QC | PM | Total |
|---|---:|---:|---:|---:|------:|
| Chuẩn hợp đồng | 53 | 38 | 38 | 20 | 149 |
| Trừ mục 3 (đã có trên sheet) | −25 | −20 | −18 | −2 | −65 |
| **Còn lại cho mục 1 + 2** | **28** | **18** | **20** | **18** | **84** |

Với 84h còn lại: **Mục 1 (98h) đã không vừa**, chưa nói tới Creator Portal. Trần FE chỉ còn
**18h** trong khi riêng hạng mục 3 (editor Markdown) cần 20h FE.

---

## ❗ Cần chốt trước khi lên kế hoạch chính thức

**Nhóm A — quyết định scope (đang chặn việc lên plan chính thức):**

1. **🔴 Hướng xử lý khoảng vênh 435h / 149h.** Ba phương án:
   - (a) cắt scope xuống vừa 149h, phần còn lại thành lộ trình T10–T11;
   - (b) cam kết 149h + liệt kê phần dư thành backlog "sẵn sàng nếu AT mở thêm giờ";
   - (c) giữ nguyên scope và đề nghị AT nâng lại khối lượng hợp đồng.
2. **🔴 Creator Portal có khởi động trong tháng 9 không.** Nếu có thì ở mức nào — chỉ hạng mục 4
   (PRD, 32h), hay cả hạng mục 5 (build khung, 136h)? Đây là hạng mục quyết định tháng có về
   đích hay không.
3. **S1 (Clone lệch view sang T-Fluencers, 58h) có giữ trong tháng 9 không** — chiếm 39% ngân
   sách và không thuộc hướng đầu tư Ambassador.
4. **Xác nhận chuẩn hợp đồng 149h và bù trừ +138h từ tháng 8** — ô `Bù trừ giờ tháng 8` trên
   sheet đang trống; tháng 8 chưa nghiệm thu xong nên con số còn có thể đổi.

**Nhóm B — cần trước khi estimate:**

5. **Estimate hạng mục 4–6 với dev.** Ba con số này là ước lượng của PM, chưa có PRD nên sai số
   lớn nhất trong cả bảng.
6. **Estimate S2, S3, S5** — ba dòng trên sheet chưa có giờ.
7. **S3 có trùng hạng mục 2 không** (xem mục 3, điểm 1).
8. **Chọn ADV nào để migrate mẫu** (hạng mục 6) — cần biết trước khi bắt đầu hạng mục 4.
9. **Có ghép gap #12 vào hạng mục 7 không** (+8h, được thêm rate limit + audit đăng nhập admin).

---

## 📋 Backlog kế tiếp — chưa đưa vào tháng 9

Các chức năng đã chọn để kéo về Ambassador nhưng chưa xếp lịch. Xếp theo thứ tự đề xuất.

### Nhóm nhỏ, gom 1 sprint là xong

| # | Chức năng | Nguồn | Effort | Ghi chú |
|---|-----------|-------|--------|---------|
| 37 | Chuẩn hoá tag lý do từ chối content (14 tag i18n vi/en + thống kê per-tag) | T-Fluencers | 2–3 ngày | Ambassador hiện chỉ có `RejectedBy`/`RejectedAt`, không thống kê được |
| 36 | Cho phép resubmit link đã bị reject ở campaign khác (flag per-partner) | vCreator | 1–2 ngày | 47 LOC + 1 field `PartnerOpts` |
| 39 | Tag phân loại campaign (`EventTags`) | T-Fluencers | ~1 ngày | Model `TagRaw` đã có sẵn, chỉ thiếu wire vào `EventRaw` |
| 38 | Mã nội bộ cho campaign (`Event.Code`, hiển thị `[code] name`) | T-Fluencers | ~1 ngày | BTC chạy nhiều campaign song song hay nhầm |
| 5 | Field `ActorType` trong audit log | vCreator | 1–2 ngày | Phân biệt automation vs thao tác tay khi tra log |
| 4 | `pfloat.RoundToOneDecimal` | vCreator | <1 ngày | Chặn bug làm tròn tiền |
| 25 | Helper `GetRoot()` cho staff root account | vCreator | <1 ngày | Bỏ raw bson query inline trong `opshub_webhook.go` |

### Nhóm lớn, cần xếp riêng theo tháng

| # | Chức năng | Nguồn | Effort | Ghi chú |
|---|-----------|-------|--------|---------|
| 15 | Hệ thống đối chiếu (reconciliation) + snapshot mỗi lần crawl | T-Fluencers | 5–7 tuần | 🔝 Top P1. Chống fraud boost view + audit trail trả lời "vì sao trả creator X số Y ngày Z" |
| 16 | Profile Review 5 tiêu chí + RatingCache | T-Fluencers | 2 tuần | **Đã hết bị chặn** sau khi gap #2 xong |
| 31 | Admin đại diện creator (tạo account + link social + bulk import content) | T-Fluencers | 2–3 tuần | Cần cho onboard partner mới và backfill content lịch sử |
| 24 | Campaign matching engine (AI scoring + AT-Core) | T-Fluencers | 3–4 tuần | Chờ T-Fluencers hoàn thiện (~786 LOC đang dở). **Đã hết bị chặn** sau gap #2 |

### Cần quyết định trước khi xếp lịch

| # | Chức năng | Câu hỏi cần trả lời |
|---|-----------|---------------------|
| 7 | Analytics Dashboard Next.js executive (~10 section) | Stakeholder Ambassador có thật sự cần executive view không, hay đang dùng BI khác? Effort 4–6 tuần |
| 19 | Extended Period mode (content đăng sau ngày kết thúc vẫn map về kỳ kế toán cũ) | Ambassador có nghiệp vụ kỳ kế toán linh hoạt không? |

### Không đụng — Ambassador là bên cho, không phải bên nhận

Gap **#8** (budget control), **#9** (recheck recovery), **#18** (BudgetInfo), **#20** (affiliate
suite), **#21** (mission/gamification), **#33** (referral seed user), **#34** (Threads binding),
**#35** (crawl Facebook Post) — Ambassador đã có, các dự án khác đi lấy về.
