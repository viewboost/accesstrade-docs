# Thiết kế kỹ thuật — Chương trình thưởng tăng trưởng Creator

| | |
|---|---|
| **Hệ thống** | vCreator Philippines — `accesstrade-projects/vcreator-philippines/backend` (Go, MongoDB, module `viewboost`) |
| **Ngày** | 2026-07-12 |
| **Đọc trước** | [overview.md](overview.md) — bối cảnh và mục tiêu nghiệp vụ · [BaoGia.csv](BaoGia.csv) — báo giá |

## 1. Kiến trúc 4 tầng

Nguyên tắc: tách nguồn dữ liệu khỏi bộ tính thưởng, tách bộ tính thưởng khỏi sổ cái.

| Tầng | Thành phần | Trạng thái | Cụm báo giá |
|---|---|---|---|
| 4. Sổ cái | `event-rewards` → `reconciliation` → `cash-flows` → `withdraw` | Đã có đủ, dùng lại nguyên, không sửa | — |
| 3. Chương trình tăng trưởng | Program (= `event`, không gắn partner) và Rule (= `event-schema`) = Segment + Chỉ số + Điều kiện + Tiền thưởng | Xây mới: logic đọc số liệu xuyên chiến dịch | A (khung) + B–F (từng cơ chế) |
| 2. Thống kê creator | `user-stats` (trọn đời), `user-stats-monthly` (theo tháng) | Xây mới: nền móng của cả hệ thống | A |
| 1. Hoạt động (nguồn) | `contents`, `content-analytic-daily`, thu thập 2 lần/ngày | Đã có, dùng lại làm nguồn, không sửa | G (thêm kênh mới) |

Dòng dữ liệu chạy từ dưới lên: tầng 1 sinh hoạt động, tầng 2 tổng hợp thành thống kê creator, tầng 3 đọc thống kê để tính thưởng, tầng 4 ghi thưởng vào sổ cái và chi tiền.

## 2. Vì sao không tái dùng được logic thưởng hiện tại

Hệ thống đã có 3 loại thưởng (`internal/constants/event.go:4-6`), nghe qua thì trùng khớp với yêu cầu:

- `by-statistic` — tiền × (lượt xem/like/comment tăng thêm) → giống PPV
- `by-content-milestone` — đủ N nội dung được duyệt → giống thưởng N video
- `by-view-milestone` — đủ N lượt xem → giống mốc hiệu suất

**Nhưng cả ba đều gắn cứng vào chiến dịch mà nội dung thuộc về.** Chương trình tăng trưởng **không có nội dung nào thuộc về nó** — creator vẫn đăng bài vào các chiến dịch bình thường, chương trình chỉ đọc thành tích của họ.

| Loại thưởng | Cách nó đếm | Kết quả với chương trình tăng trưởng |
|---|---|---|
| `by-content-milestone` | Đếm nội dung với điều kiện `{user, event: <chiến dịch này>, status: approved}` | Chương trình không có nội dung → đếm ra **0** |
| `by-statistic` | Chạy theo `content-analytic-daily`, mỗi bản ghi mang `event` của nội dung gốc | Trả thưởng cho **chiến dịch gốc**, không phải chương trình |
| `by-view-milestone` | Đọc `user-events.statistic` (bảng creator × chiến dịch) | Chương trình không có bản ghi `user-events` → đọc ra **0** |

Cả ba đều mở đầu bằng việc lọc theo chiến dịch. Không phải chỉnh sửa — **phải viết mới**.

### Ranh giới tái dùng

| Thành phần | Tái dùng? |
|---|---|
| Cấu trúc dữ liệu (`event`, `event-schema`, `event-reward`) | Có — dùng lại khuôn, **không tạo collection mới** |
| **Logic tính thưởng** (3 hàm `CheckPassSchema*`) | **Viết mới** |
| **Điểm kích hoạt tính thưởng** | **Thêm mới** — xem mục 5 |
| Nguồn số liệu (`contents`, `content-analytic-daily`) | Có — dùng lại làm nguồn |
| **Đối soát → ví → rút tiền** | Có — **dùng lại nguyên** |

## 3. Tầng 2 — Bảng thống kê creator

### Vì sao cần tầng này

Nếu để mỗi quy tắc thưởng tự đếm trực tiếp từ bảng `contents`:

- Mỗi lần crawl (2 lần/ngày × toàn bộ creator) quét lại toàn bộ lịch sử nội dung → chậm, và chậm dần theo thời gian.
- Bảng xếp hạng tháng phải tổng hợp toàn hệ thống mỗi lần xem → không hiển thị realtime được.
- Mỗi quy tắc đếm một kiểu → số liệu không nhất quán giữa các quy tắc, và không có nguồn nào để đối chiếu khi creator khiếu nại.

**Giải pháp: một bảng thống kê tổng hợp sẵn cho mỗi creator.** Mọi quy tắc thưởng, bảng xếp hạng, và màn hình creator đều đọc từ **đúng một nguồn** → cùng một con số ở mọi nơi.

Hệ thống **đã có tiền lệ**: `user-income-month` (`user` + `month` + `year` + `totalCash`) — rollup thu nhập theo tháng. Bảng mới đi theo đúng khuôn đó, chỉ khác là thống kê **nội dung và lượt xem** thay vì tiền.

### `user-stats` — trọn đời, 1 bản ghi / creator

Phục vụ: thưởng N video đầu, mốc hiệu suất, hồ sơ creator.

| Trường | Ý nghĩa |
|---|---|
| `user` | Creator |
| `firstApprovedContentAt` | Thời điểm video **đầu tiên** được duyệt → cho cơ chế "N video đầu" |
| `approvedContentCount` | Tổng số video đã duyệt (trọn đời, xuyên chiến dịch) |
| `approvedContentBySource` | `{ tiktok: 12, youtube: 3, ... }` |
| `totalView` / `totalLike` / `totalComment` | Tổng tích luỹ |
| `totalViewBySource` | `{ tiktok: 120000, ... }` |
| `lastActivityAt` | Hoạt động gần nhất → phát hiện creator ngừng đăng bài |
| `updatedAt` / `recomputedAt` | Dấu vết cập nhật |

### `user-stats-monthly` — 1 bản ghi / creator / tháng

Phục vụ: thưởng số video/tháng, bảng xếp hạng tháng, báo cáo tăng trưởng.

| Trường | Ý nghĩa |
|---|---|
| `user`, `year`, `month` | Khoá |
| `approvedContentCount` | Số video được duyệt trong tháng |
| `view` / `like` / `comment` | Phát sinh trong tháng |
| `bySource` | Chia theo kênh |
| `rank` | Thứ hạng — ghi vào **sau khi chốt sổ**, là bản bất biến |

### Cách cập nhật — 2 cơ chế song song

**(1) Cộng dần theo sự kiện** — nội dung được duyệt → cộng số đếm; crawl về lượt xem mới → cộng phần chênh lệch; nội dung bị hủy → trừ lại. Nhanh, gần thời gian thực.

**(2) Tính lại toàn bộ hằng đêm** — quét lại từ nguồn, ghi đè.

Cơ chế (2) là bắt buộc, không phải tuỳ chọn. Cộng dần lâu ngày sẽ lệch (crawl lỗi, nội dung bị xoá, admin điều chỉnh thủ công, tiến trình dừng giữa chừng). Không có cơ chế tính lại thì số liệu trôi dần theo thời gian, và khi creator khiếu nại thì không có nguồn nào để đối chiếu.

### Số liệu admin điều chỉnh thủ công

Hệ thống **đã có sẵn** cơ chế admin cộng/trừ lượt xem thủ công: collection `content-manual-flows`, trường `Statistic.View.Manual` (tách riêng khỏi số crawl về), hàm `GetTotalView()` = `Total + Manual`, kèm audit log.

Bảng thống kê mới **phải cộng cả phần này**. Nếu chỉ lấy lượt xem từ crawl, creator được admin điều chỉnh tay sẽ không được tính vào thưởng tăng trưởng và bảng xếp hạng — trong khi thưởng chiến dịch vẫn tính. Cùng một creator sẽ có hai con số khác nhau ở hai nơi.

### Ràng buộc và chỉ mục

- **Khoá duy nhất**: `user` (bảng trọn đời), `user + year + month` (bảng tháng). Không có ràng buộc này thì hai tiến trình chạy song song sẽ tạo hai bản ghi và số liệu bị nhân đôi.
- **Chỉ mục cho bảng xếp hạng**: `{ year, month, view: -1 }`. Thiếu thì mỗi lần xem xếp hạng sẽ quét toàn bộ collection.

## 4. Tầng 3 — Quy tắc thưởng

Mỗi quy tắc = **Đối tượng + Chỉ số + Điều kiện + Tiền thưởng + Chu kỳ**.

| Thành phần | Nội dung |
|---|---|
| **Đối tượng (segment)** | Creator có `user.createdAt` trong khoảng `[X, Y]` |
| **Chỉ số** | Số video duyệt / lượt xem / tương tác — đọc từ tầng 2 |
| **Điều kiện** | Đạt ngưỡng N, hoặc lọt vào top hạng |
| **Tiền thưởng** | Cố định, hoặc theo hạng |
| **Chu kỳ** | Trọn đời hoặc theo tháng |
| **Chống trả trùng** | Khoá theo `creator + quy tắc + chu kỳ` |

### Segment — hệ thống đã có một nửa

`segments` + `user-segments` **đã tồn tại** (`internal/model/mg/user_segment.go`), nhưng là segment **tĩnh**: admin gán tay từng creator (`createdBy`), và hiện chỉ dùng để gửi thông báo.

Chương trình tăng trưởng cần segment **động**: "creator đăng ký trong khoảng [X, Y]" — hệ thống tự xác định, creator không cần đăng ký tham gia.

**Quyết định:** giữ nguyên segment tĩnh (không phá thứ đang chạy), bổ sung định nghĩa segment động cho quy tắc thưởng. Về sau hai loại có thể hội tụ.

### Ánh xạ các cơ chế thưởng

| Cụm | Cơ chế | Segment | Chỉ số | Điều kiện | Chu kỳ |
|---|---|---|---|---|---|
| **B** | N video đầu | Creator mới | `approvedContentCount` (trọn đời) | Đạt video thứ 1, 2, … N | Trọn đời |
| **C** | Video duyệt/tháng | Creator mới | `approvedContentCount` (tháng) | Đạt các mốc | Tháng |
| **D** | Lượt xem (PPV) | Creator mới | Lượt xem tăng thêm | Theo đơn giá | Liên tục |
| **E** | Mốc hiệu suất | Creator mới | `totalView` (trọn đời) | Đạt các mốc | Trọn đời |
| **F** | Bảng xếp hạng | Creator mới *(hoặc toàn bộ)* | `view` (tháng) | Lọt top N | Tháng |

**"N video đầu" — N phải cấu hình được.** Yêu cầu ban đầu là 3. Không gắn cứng số 3 vào code.

**Nhiều mốc = cộng dồn.** Ba mốc (5/10/20 video) là ba khoản độc lập; creator đạt 20 video nhận cả ba. Đây là ý đồ, không phải lỗi. Đặt mức tiền phải tính theo tổng cộng dồn.

## 5. Hai điểm cần xử lý

### 5.1 — Điểm kích hoạt chương trình

Hiện thưởng chỉ được tính khi nội dung **đổi trạng thái**, hoặc khi **crawl xong nội dung của chính chiến dịch đó**. Chương trình tăng trưởng không có nội dung nào thuộc về nó, nên không có gì kích hoạt nó chạy.

**Xử lý:** thêm nhánh — mỗi khi số liệu của bất kỳ nội dung nào được cập nhật (crawl hoặc duyệt), hệ thống cập nhật bảng thống kê creator, rồi quét các chương trình tăng trưởng đang chạy.

**Kiểm thử:** creator đăng bài cho chiến dịch A → thưởng tăng trưởng vẫn được tính.

### 5.2 — Danh sách loại thưởng trong quy trình đối soát

Quy trình đối soát hiện lọc theo *loại thưởng* bằng danh sách cố định. Loại thưởng mới phải được thêm vào danh sách này, nếu không thì khoản thưởng sẽ dừng ở trạng thái chờ và không vào ví creator. Đây là lỗi không có thông báo, chỉ phát hiện qua khiếu nại.

**Kiểm thử toàn trình bắt buộc:** tạo thưởng → đối soát → vào ví → rút được tiền thật.

## 6. Hiện trạng vCreator-PH

### Đã có

| Thành phần | Chi tiết |
|---|---|
| Sổ cái đầy đủ | `event-rewards` → `reconciliation` (+items, +histories) → `cash-flows` → `transfers` → `withdraw` |
| 3 loại thưởng | Dùng lại được **khuôn**, không dùng lại được **logic** |
| Số liệu theo ngày | `content-analytic-daily` có sẵn `user`, `date`, `month`, `year` → nguồn cho tầng 2, **không cần chuyển đổi dữ liệu** |
| Mốc thời gian creator | `user.createdAt` (`internal/model/mg/user.go:42`) → làm segment được ngay |
| Mốc thời gian nội dung | `content.date` (ngày đăng), `content.completedAt` (ngày duyệt) |
| Khuôn rollup theo tháng | `user-income-month` — tiền lệ cho `user-stats-monthly` |
| Điều chỉnh số liệu thủ công | `content-manual-flows` + `Statistic.View.Manual` + audit log |
| Segment (một nửa) | `segments` + `user-segments` — tĩnh, gán tay, dùng cho thông báo |
| Thu thập số liệu | Cron **2 lần/ngày**: TikTok, YouTube, Facebook |

### Chưa có

| Thành phần | Ghi chú |
|---|---|
| **Bảng thống kê creator** | `users.statistic` chỉ có **tiền** — không có số video, không có lượt xem. Hạng mục lớn nhất. |
| **Logic thưởng xuyên chiến dịch** | Toàn bộ logic hiện tại gắn cứng vào chiến dịch |
| **Segment động** | Segment hiện tại là gán tay |
| **Bảng xếp hạng** | Không có cơ chế nào |
| **Kênh Threads** | Chỉ hỗ trợ 7 nguồn: youtube, youtube_shorts, tiktok, facebook, facebook_reels, instagram, instagram_reels (`internal/constants/content.go:4-30`) |
| **Kênh X (Twitter)** | Chưa có |
| **Lượt xem tối thiểu cho mốc video** | `EventSchemaMilestone` chỉ có `numberOfContent` / `numberOfView` — không có `minimumOfView`. Mốc video hiện đếm cả video 0 lượt xem. |
| **Giao diện tiến độ creator** | Chưa có |
| **Giới hạn ngân sách** | Không có trần chi ở bất kỳ cấp nào. Ngoài phạm vi dự án — xem [overview.md](overview.md) mục 7. |

## 7. Lưu ý vận hành

**Số liệu cập nhật 2 lần/ngày, không tức thời.** Phải nói rõ trên app.

**Đếm theo ngày đăng, không phải ngày duyệt.** Hệ thống dùng `content.date` (thời điểm creator đăng bài). Creator đăng 30/7, admin duyệt 2/8 → tính vào tháng 7. Đây là hành vi mong muốn, đã xác nhận.

**Bảng xếp hạng lưu bản bất biến.** Chốt sổ xong thì đóng băng thứ hạng vào `user-stats-monthly.rank` — creator khiếu nại thì có bằng chứng đối chiếu, và chạy lại quy trình không làm đổi kết quả.

**Kênh mới cần xác minh nguồn dữ liệu.** Trước khi bật thưởng theo lượt xem cho một kênh, cần xác nhận nguồn thu thập có trả về lượt xem hay chỉ like/bình luận. Hệ thống nhận biết mỗi kênh cung cấp chỉ số nào và cảnh báo khi gói thưởng không phù hợp với kênh được chọn.
