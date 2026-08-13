# Danh mục các case gây lệch view — mục Nội dung ↔ File đối soát ↔ mục Thông số

**Ngày:** 2026-08-13
**Nguồn:** Playbook xử lý sự cố cho Ops — AT × DISO v2.1 (31/07/2026), mục PB-1, PB-3, PB-4, PB-9, PB-11; tổng hợp từ Meeting Weekly Tech × Biz (2/6, 9/6, 16/6, 30/6, 14/7, 21/7) và danh sách issue tháng 7.
**Liên quan:** [PRD.md](PRD.md) · [TECH_SPEC.md](TECH_SPEC.md)

---

## Mục đích tài liệu

Liệt kê **đầy đủ các nguyên nhân** làm số view ở **mục Nội dung** khác số view ở **file đối soát** hoặc **mục Thông số**. Tài liệu này chỉ mô tả **case và cơ chế gây lệch** — không bao gồm các bước kiểm tra (đã có trong PB-1 của playbook Ops).

Dùng để: (1) khoanh vùng nhanh khi có khiếu nại lệch view; (2) xác định phạm vi mà cơ chế cảnh báo lệch số liệu kỳ đối soát bắt được và **không** bắt được (xem mục 9).

## 1. Quy ước đọc

Ba nguồn số liệu và bản chất của từng nguồn:

| Nguồn | Bản chất số liệu | Bảng dữ liệu gốc |
| --- | --- | --- |
| **Mục Nội dung** (admin) | View thô đã crawl về của từng content, theo ngày | `content-analytic-daily` |
| **Mục Thông số** (admin) | Số tổng hợp theo sự kiện/campaign trên khoảng ngày được lọc | tổng hợp từ `content-analytic-daily` |
| **File đối soát** | Số **được tính thưởng** đã chốt để thanh toán | `event-rewards` + snapshot chốt kỳ |

Hệ quả quan trọng: **ba nguồn không cùng một loại chỉ số.** Nội dung/Thông số là *view thu thập được*; đối soát là *view đủ điều kiện tính thưởng*. Chênh lệch giữa chúng chỉ là bug khi cùng loại chỉ số mà vẫn khác nhau.

Ký hiệu hướng lệch dùng trong tài liệu:

- **N > Đ** — Nội dung có view, đối soát thiếu hoặc thấp hơn.
- **N < Đ** — Đối soát cao hơn Nội dung.
- **N ≠ T** — Nội dung khác Thông số.
- **Đ ≠ Đ'** — cùng file đối soát nhưng export ở hai thời điểm khác nhau ra hai số khác nhau.

Cột **Bản chất** trong tài liệu nhận một trong ba giá trị: **Bug** (lỗi hệ thống), **Đúng thiết kế** (hệ thống chạy đúng cấu hình, không escalate), **Đọc sai** (không có lệch thật, do cách đọc/lọc số).

---

## 2. Bảng tổng hợp nhanh — 36 case

| Mã | Case | Nhóm | Hướng lệch | Bản chất |
| --- | --- | --- | --- | --- |
| A1 | `totalNotFound` ≥ 3 → hệ thống ngừng crawl vĩnh viễn | Thu thập | N > Đ, cả 3 nguồn cùng thiếu | Bug hoặc lỗi nội dung |
| A2 | Crawl thành công nhưng không có `content-callbacks` trả về | Thu thập | Cả 3 nguồn cùng thiếu | Bug |
| A3 | Content không được đưa vào hàng đợi crawl | Thu thập | Cả 3 nguồn cùng thiếu | Bug |
| A4 | Token kênh (TikTok) hết hạn | Thu thập | Toàn bộ content của kênh đứng view | Lỗi nội dung |
| A5 | Bài bị xoá / chuyển riêng tư / đổi link / tài khoản bị khoá sau khi nộp | Thu thập | Đứng view từ thời điểm thay đổi | Đúng thiết kế |
| A6 | Vendor cào lỗi diện rộng | Thu thập | Nhiều user, nhiều kênh cùng đứng | Bug (bên thứ 3) |
| A7 | Content không nộp được vào hệ thống ngay từ đầu | Thu thập | Content không tồn tại ở cả 3 nguồn | Hỗn hợp |
| B1 | **Dữ liệu view về trễ rồi ghi đè số cũ** (trễ tới 30 ngày) | Ghi số ngày | Đ ≠ Đ', N ≠ Đ | Bug |
| B2 | Đếm trùng — view nhảy gấp đôi trong một ngày | Ghi số ngày | N < Đ hoặc N > thực tế | Bug |
| B3 | Chuỗi ngày đứt gãy — view đầu ngày N+1 < view cuối ngày N | Ghi số ngày | N ≠ Đ | Bug |
| B4 | Ngày bị miss hoàn toàn — không có bản ghi cho ngày đó | Ghi số ngày | N > Đ | Bug |
| C1 | Có view trong `content-analytic-daily` nhưng **không sinh** `event-rewards` | Sinh thưởng | N > Đ | Bug (case Parkway) |
| C2 | Bản ghi `event_reward` mất / đổi trạng thái / đổi số tiền sau khi chốt kỳ | Sinh thưởng | N > Đ | Bug |
| C3 | `TotalViewPendingRewarded` chốt lúc tạo kỳ ≠ view tính lại lúc chi | Sinh thưởng | Đ ≠ Đ' | Bug |
| C4 | Job tính thưởng chạy theo batch, chưa tới kỳ | Sinh thưởng | N > Đ (tạm thời) | Đúng thiết kế |
| D1 | Nhiệm vụ **tắt rồi bật lại** — khoảng giữa có view, không thưởng | Setup | N > Đ | Đúng thiết kế |
| D2 | Hết budget nhiệm vụ / campaign | Setup | N > Đ từ thời điểm hết budget | Đúng thiết kế |
| D3 | Chạm trần thưởng (cap) theo user / content | Setup | N > Đ, phần vượt cap bị cắt | Đúng thiết kế |
| D4 | Ngày duyệt content nằm ngoài thời gian hiệu lực nhiệm vụ | Setup | N > Đ, content không lên đối soát | Đúng thiết kế |
| D5 | Nhiệm vụ không tính theo view | Setup | N > Đ, content không lên đối soát | Đúng thiết kế |
| D6 | Campaign đã kết thúc → dừng crawl | Setup | Đứng view từ ngày kết thúc | Đúng thiết kế |
| D7 | Content bị reject / gỡ **sau khi** đã duyệt và đã có view | Setup | N > Đ, mất dòng ở đối soát | Đúng thiết kế |
| D8 | Content chưa duyệt / đang chờ duyệt | Setup | N > Đ | Đúng thiết kế |
| D9 | Content không thoả điều kiện nhiệm vụ (hashtag, thời gian đăng, kênh liên kết) | Setup | N > Đ | Đúng thiết kế |
| E1 | **View hiển thị ≠ view được tính thưởng** khi xét mốc (case Phở Cung Đình) | Mốc thưởng | N > Đ ở cột mốc | Đúng thiết kế |
| E2 | Cấu hình mốc thưởng sai / thiếu trong admin | Mốc thưởng | Đ sai so với thể lệ | Bug cấu hình |
| E3 | Job nhảy mốc chưa chạy / chạy trễ | Mốc thưởng | N > Đ (tạm thời) | Đúng thiết kế |
| E4 | Lỗi logic tính tier — đủ điều kiện mà không nhảy mốc | Mốc thưởng | N > Đ | Bug |
| E5 | Đạt mốc ngoài thời gian hiệu lực nhiệm vụ | Mốc thưởng | N > Đ | Đúng thiết kế |
| E6 | Hết budget / chạm cap đúng tại thời điểm đạt mốc | Mốc thưởng | N > Đ, mốc không được cộng đủ | Đúng thiết kế |
| F1 | So nhầm **view lũy kế** với **view phát sinh trong ngày** | Đọc số | N ≠ Đ ≠ T tuỳ ý | Đọc sai |
| F2 | Lệch múi giờ / mốc cắt ngày | Đọc số | Lệch ngày N ≈ phần đầu ngày N+1 | Đọc sai |
| F3 | Bộ lọc mặc định mục Thông số là 7 ngày gần nhất | Đọc số | N ≠ T | Đọc sai |
| F4 | Lọc sai `event_id` / sai khoảng ngày trong file đối soát | Đọc số | N ≠ Đ | Đọc sai |
| F5 | Cache / FE hiển thị lệch — backend đã đúng | Hiển thị | Trang cá nhân ≠ đối soát | Bug hiển thị |
| F6 | Bài đã bão hoà tự nhiên, bị báo nhầm là đứng view | Đọc số | Không lệch thật | Đọc sai |

---

## 3. Nhóm A — Tầng thu thập dữ liệu (crawl)

Đặc điểm chung của cả nhóm: view **không bao giờ vào được hệ thống**. Vì vậy cả ba nguồn (Nội dung, Thông số, đối soát) đều cùng thiếu như nhau — lệch xuất hiện khi so với **số view thực tế trên nền tảng gốc** (TikTok/Facebook), chứ không phải lệch giữa ba màn hình với nhau. Đây là điểm hay bị nhầm nhất khi phân loại.

### A1 · `totalNotFound` ≥ 3 → hệ thống ngừng crawl

**Cơ chế:** mỗi lần crawl thất bại, hệ thống tăng cờ `totalNotFound` trên bảng `content`. Khi cờ chạm **3**, content bị đánh dấu crawl failed và **hệ thống không crawl content đó nữa** — vĩnh viễn, không tự phục hồi kể cả khi bài đã trở lại bình thường.

**Biểu hiện:** view của content đứng yên hoàn toàn kể từ một ngày cụ thể, trong khi số view thực tế trên nền tảng gốc vẫn tăng. Đối soát chốt theo số đã đứng → thiếu tiền cho creator.

**Bản chất:** hai khả năng, phải tách bạch —
- Bài đã bị xoá / chuyển riêng tư / link sai / tài khoản đổi tên hoặc bị khoá → crawl fail là **đúng**, lỗi nằm phía nội dung (xem A5).
- Bài vẫn công khai bình thường → **crawl fail sai**, là bug của hệ thống hoặc vendor.

**Ghi chú:** hiện **không có cảnh báo nào** khi `totalNotFound` chạm 3 — không ai biết content đã dừng crawl cho tới khi creator khiếu nại. Đã nằm trong backlog cải tiến (mục 6 của playbook, đề xuất #8).

### A2 · Crawl thành công nhưng không có `content-callbacks` trả về

**Cơ chế:** hệ thống có gọi crawl, có bản ghi callback trong bảng `content-callbacks`, nhưng callback **không mang theo dữ liệu content** — không có số view để ghi vào `content-analytic-daily`.

**Biểu hiện:** view đứng yên nhưng khác A1 ở chỗ hệ thống *vẫn đang crawl đều đặn* — có lịch sử callback mới, chỉ là rỗng dữ liệu.

**Bản chất:** Bug. Không tự phục hồi.

### A3 · Content không được đưa vào hàng đợi crawl

**Cơ chế:** content tồn tại trong hệ thống, ở trạng thái hợp lệ, thuộc campaign còn hiệu lực có nhiệm vụ tính view — nhưng **không có bản ghi callback nào trong nhiều ngày**, tức là chưa từng được đẩy vào hàng đợi crawl.

**Biểu hiện:** view = 0 hoặc đứng ở số của lần cập nhật cuối, không có dấu vết hoạt động crawl nào.

**Bản chất:** Bug ở khâu đưa content vào hàng đợi.

### A4 · Token kênh hết hạn

**Cơ chế:** token của kênh mạng xã hội (điển hình là TikTok) lưu ở bảng `user-social` hết hạn. Không có token hợp lệ thì không lấy được dữ liệu view của toàn bộ content thuộc kênh đó.

**Biểu hiện:** **tất cả** content của cùng một kênh cùng đứng view từ cùng một thời điểm — đây là dấu hiệu phân biệt với A1/A2 (vốn chỉ ảnh hưởng từng content lẻ).

**Bản chất:** không phải bug hệ thống. Khắc phục bằng cách user liên kết lại kênh để refresh token; sau đó view cập nhật lại ở chu kỳ crawl tiếp theo (thường trong 24 giờ).

**Ghi chú:** hệ thống **không cảnh báo trước** khi token sắp hết hạn — nằm trong backlog đề xuất #8.

### A5 · Bài bị xoá / chuyển riêng tư / đổi link / tài khoản bị khoá sau khi nộp

**Cơ chế:** creator thay đổi trạng thái bài viết sau khi đã nộp link — xoá bài, chuyển từ Công khai sang Bạn bè/Chỉ mình tôi, giới hạn quyền xem, sửa link, hoặc đổi tên/khoá tài khoản đăng. Crawler không còn đọc được bài → crawl fail → dần dần dẫn tới A1.

**Biểu hiện:** view đứng yên kể từ đúng thời điểm creator thay đổi bài.

**Bản chất:** Đúng thiết kế. Lỗi nằm phía nội dung, không phải hệ thống.

### A6 · Vendor cào lỗi diện rộng

**Cơ chế:** đơn vị thứ ba cung cấp dịch vụ crawl gặp sự cố — bị nền tảng chặn, đổi định dạng dữ liệu trả về, hoặc dừng dịch vụ. Đã ghi nhận: `facebook_id` lúc trả về dạng **number**, lúc dạng **hashstring**; link dạng `/share/...` và `/photo/?fbid=...` lúc crawl được lúc không.

**Biểu hiện:** nhiều content, của **nhiều user và nhiều kênh khác nhau**, cùng một nền tảng, cùng đứng view trong cùng một khoảng thời gian.

**Bản chất:** Bug phía bên thứ ba. Đây là case duy nhất trong nhóm A cần nâng mức P1 ngay khi xác nhận.

### A7 · Content không nộp được vào hệ thống ngay từ đầu

**Cơ chế:** creator không submit được link Facebook/Threads (hệ thống báo bị chặn), nên content **chưa từng tồn tại** trong hệ thống. Toàn bộ view của bài đó không bao giờ được ghi nhận ở bất kỳ nguồn nào.

Các nguyên nhân con:
- Bài không ở chế độ **Công khai** (để Bạn bè / Chỉ mình tôi / đăng trong nhóm kín) → crawler không đọc được. Rất phổ biến, **không phải bug**.
- Sai định dạng link: link `/photo/?fbid=...` (hệ thống không lấy được link cuối dạng `share/p/{id}`), link `/share/...`, link từ app mobile có kèm tham số theo dõi.
- Bài đăng từ **tài khoản chưa liên kết** với hệ thống hoặc khác với user đang nộp → đúng thiết kế.
- Vendor cào lỗi tạm thời tại đúng thời điểm submit.

**Biểu hiện:** creator khẳng định "tôi có đăng bài và bài có view" nhưng không tìm thấy content ở cả mục Nội dung lẫn đối soát.

**Ghi chú vận hành quan trọng:** cơ chế **"vendor cào failed thì cho pass"** (áp dụng giống Instagram) hiện **chỉ mới release cho T-Fluencer**. **VCreator và Ambassador chưa được áp dụng** — nên cùng một tình huống, creator Ambassador sẽ mất view còn creator T-Fluencer thì không. Đây là nguồn lệch mang tính hệ thống giữa các partner.

---

## 4. Nhóm B — Tầng ghi số liệu view theo ngày

Đặc điểm chung: view **đã** vào hệ thống nhưng bị ghi sai, ghi thiếu, hoặc ghi đè ở bảng `content-analytic-daily`. Đây là nhóm gây lệch **thật sự giữa ba màn hình** và là nhóm cần escalate Dev DISO nhiều nhất.

### B1 · Dữ liệu view về trễ rồi ghi đè số cũ ⚠️ NGUYÊN NHÂN PHỔ BIẾN NHẤT

**Cơ chế:** dữ liệu view của một ngày trong quá khứ có thể được trả về **trễ** rồi **ghi đè** lên số đã ghi trước đó. Độ trễ đã ghi nhận thực tế: **tới 30 ngày**.

Hệ quả dây chuyền:
- File đối soát export lúc 10h và export lại lúc 10h hôm sau cho **hai con số khác nhau trên cùng một khoảng ngày** — dù không ai thao tác gì.
- Nếu kỳ đối soát đã chốt số trước khi dữ liệu trễ về, số chốt là số cũ → sai so với số hiện tại của mục Nội dung.
- Nếu kỳ đã thanh toán, khoản chênh không được truy thu/bù tự động.

**Biểu hiện:** **Đ ≠ Đ'** — dấu hiệu nhận diện đặc trưng nhất của case này. Số của ngày cũ thay đổi sau 24 giờ mà không có thao tác nào.

**Bản chất:** Bug. Hệ thống hiện **không ghi nhận lịch sử thay đổi số liệu** và **không cảnh báo khi dữ liệu ngày cũ bị ghi đè** — backlog cải tiến đề xuất #2.

**Lưu ý vận hành:** nếu sự kiện đang gần kỳ đối soát/thanh toán mà phát hiện case này, phải cân nhắc **hoãn chốt số** cho tới khi dữ liệu ổn định.

### B2 · Đếm trùng

**Cơ chế:** view của cùng một ngày được ghi nhận nhiều hơn một lần, làm số view trong ngày đó **tăng vọt bất thường**, đặc biệt là **gấp khoảng 2 lần** so với mức bình thường của content.

**Biểu hiện:** một ngày duy nhất trong chuỗi có số nhảy gấp đôi, các ngày kề bên bình thường. Nếu đối soát chốt vào đúng ngày đó → **trả thừa tiền**.

**Bản chất:** Bug.

### B3 · Chuỗi ngày đứt gãy — dữ liệu bị ghi đè hoặc mất

**Cơ chế:** quy tắc bất biến của dữ liệu view lũy kế là **view cuối ngày N phải bằng view đầu ngày N+1**. Khi *số đầu ngày N+1 nhỏ hơn số cuối ngày N*, tức là đã có dữ liệu bị ghi đè hoặc mất.

**Biểu hiện:** chuỗi số view theo ngày bị "tụt", không đơn điệu tăng.

**Bản chất:** Bug. Khác B1 ở chỗ B1 làm số **thay đổi theo thời gian export**, còn B3 làm chuỗi **tự mâu thuẫn ngay tại một thời điểm export**.

### B4 · Ngày bị miss hoàn toàn

**Cơ chế:** không có bản ghi `content-analytic-daily` nào cho một hoặc nhiều ngày — không phải ghi sai số mà là **không có dòng dữ liệu**.

**Biểu hiện:** mục Nội dung nhảy cóc qua ngày, đối soát thiếu hẳn phần view của những ngày đó.

**Bản chất:** Bug. Cần dev backfill. Danh sách ngày bị miss là dữ liệu bắt buộc khi escalate.

---

## 5. Nhóm C — Tầng sinh thưởng và chốt kỳ

Đặc điểm chung: view đã ghi nhận **đúng** ở `content-analytic-daily`, nhưng không chuyển hoá thành bản ghi thưởng ở `event-rewards`, hoặc bản ghi thưởng biến động sau khi kỳ đối soát đã chốt.

### C1 · Có view nhưng không sinh bản ghi thưởng (case Nha khoa Parkway)

**Cơ chế:** `content-analytic-daily` **có** ghi nhận view cho content trong ngày, nhưng `event-rewards` **không sinh bản ghi** tương ứng. Mắt xích giữa "đã có view" và "được tính thưởng" bị đứt.

**Biểu hiện:** mục Nội dung hiển thị view đầy đủ và đúng, file đối soát **không có dòng nào** cho content/ngày đó. **N > Đ** rõ ràng, và loại trừ được hết các nguyên nhân setup ở nhóm D.

**Bản chất:** Bug. Đây là case đã có tiền lệ được xác định (Nha khoa Parkway, Meeting 14/7) — khi khớp đúng dấu hiệu này thì chuyển thẳng Dev DISO.

### C2 · Bản ghi `event_reward` biến động sau khi chốt kỳ

**Cơ chế:** kỳ đối soát chốt số dựa trên bản ghi `event_reward` tại thời điểm tạo kỳ. Giữa lúc chốt và lúc chi tiền, bản ghi đó có thể: **không còn tồn tại**, **đã đổi trạng thái**, hoặc **số tiền trên đó khác** số đã chốt trên item.

**Biểu hiện:** item bị đánh dấu `rejected` trong kỳ đối soát, người dùng không nhận được tiền dù đối soát ban đầu có ghi nhận.

**Bản chất:** Bug ở tầng dữ liệu nguồn. **Đã có guard bắt được** (loại lệch `reward`) — xem mục 9.

### C3 · `TotalViewPendingRewarded` chốt lúc tạo kỳ ≠ view tính lại lúc chi

**Cơ chế:** số lượt xem được tính thưởng được chốt lúc tạo kỳ và ghi thẳng vào cashflow lẫn thông báo cho người dùng. Nếu dữ liệu `event_reward` biến động giữa lúc chốt kỳ và lúc chi, con số này **sai** — và trước đây không có cơ chế nào phát hiện.

**Biểu hiện:** người dùng nhận được thông báo ghi số view khác với số thực tế đủ điều kiện tại thời điểm chi.

**Bản chất:** Bug. **Guard `view` mới được bổ sung chính là để bắt case này** — ngưỡng lệch bằng 0, lệch dù chỉ một lượt xem cũng loại item và báo cáo, vì cả hai vế đều là số nguyên đếm từ cùng một nguồn.

### C4 · Job tính thưởng chạy theo batch, chưa tới kỳ

**Cơ chế:** cơ chế cộng thưởng không chạy tức thời mà theo batch / chu kỳ crawl. View mới ghi nhận trong vài giờ gần đây chưa được quy đổi thành bản ghi thưởng.

**Biểu hiện:** **N > Đ** nhưng **mang tính tạm thời** — hết một chu kỳ (thường trong 24 giờ) thì tự khớp lại.

**Bản chất:** Đúng thiết kế nếu chưa quá một chu kỳ. Quá chu kỳ mà vẫn lệch → nghi job lỗi hoặc không được trigger, chuyển thành bug.

---

## 6. Nhóm D — Setup và điều kiện nghiệp vụ

Đặc điểm chung: **phần lớn là hệ thống chạy đúng theo cách admin đã setup.** Đây là nhóm **hay bị báo nhầm thành bug nhất**. View vẫn được ghi nhận đầy đủ ở mục Nội dung, nhưng **không được tính thưởng** nên không lên đối soát — chênh lệch là có thật nhưng **đúng thiết kế**.

Điểm chung của cả nhóm: mỗi khoảng lệch phải trùng khớp được với một khoảng thay đổi setup cụ thể trong audit log. Không trùng khớp được ⇒ mới là bất thường thật.

### D1 · Nhiệm vụ tắt rồi bật lại

**Cơ chế:** nhiệm vụ kết thúc hoặc bị tắt, sau đó được bật lại. Trong khoảng ở giữa, hệ thống **vẫn ghi nhận view bình thường** nhưng **không tính thưởng**.

**Ví dụ thực tế đã gặp:** nhiệm vụ kết thúc **15/5**, được bật lại **29/5** → toàn bộ view phát sinh trong khoảng **16/5 → 28/5** có ở mục Nội dung nhưng không có ở đối soát.

**Bản chất:** Đúng thiết kế. Nếu Biz muốn tính thưởng cho khoảng đó thì phải điều chỉnh setup, và **bắt buộc có xác nhận PM/Biz vì liên quan trực tiếp đến tiền**.

**Ghi chú:** phần lớn khiếu nại nhóm này bắt nguồn từ một thay đổi setup mà **không ai ghi nhận lại lý do**.

### D2 · Hết budget nhiệm vụ / campaign

**Cơ chế:** khi budget của nhiệm vụ đã tiêu hết, hệ thống **ngừng cộng thưởng** nhưng **vẫn tiếp tục ghi nhận view**.

**Biểu hiện:** đối soát dừng tăng ở một mốc, mục Nội dung tiếp tục tăng.

**Bản chất:** Đúng thiết kế.

**Hạn chế đã biết:** hệ thống **không có thông số ghi nhận thời điểm hết budget** — nên rất khó chứng minh chính xác khoảng lệch trùng với thời điểm nào. Đã nằm trong backlog cải tiến (đề xuất #3).

### D3 · Chạm trần thưởng (cap) theo user / content

**Cơ chế:** nhiệm vụ có trần thưởng theo từng content hoặc từng user. Khi đã chạm trần, phần view vượt quá không còn được quy đổi thành thưởng.

**Biểu hiện:** view ở mục Nội dung tiếp tục tăng, số tiền/số view tính thưởng ở đối soát đứng yên ở đúng mức trần.

**Bản chất:** Đúng thiết kế.

### D4 · Ngày duyệt content nằm ngoài thời gian hiệu lực nhiệm vụ

**Cơ chế:** content được duyệt ở một thời điểm nằm ngoài khoảng hiệu lực của nhiệm vụ → không được gộp vào đối soát.

**Biểu hiện:** content xuất hiện đầy đủ ở mục Nội dung với trạng thái **Đã duyệt** và có view, nhưng **không có dòng nào** ở file đối soát.

**Bản chất:** Đúng thiết kế.

### D5 · Nhiệm vụ không tính theo view

**Cơ chế:** campaign/nhiệm vụ mà content thuộc về **không có loại nhiệm vụ tính theo view**. Hệ thống không crawl và không đưa content lên đối soát.

**Biểu hiện:** content đã duyệt nhưng không có ở đối soát; view ở mục Nội dung cũng không tăng.

**Bản chất:** Đúng thiết kế. Đây là case cần loại trừ **đầu tiên** khi có báo "content đã duyệt mà không thấy trong đối soát".

### D6 · Campaign đã kết thúc

**Cơ chế:** campaign hết thời gian hiệu lực → hệ thống dừng crawl toàn bộ content thuộc campaign đó.

**Biểu hiện:** view đứng yên đúng từ ngày campaign kết thúc, đồng loạt trên mọi content của campaign.

**Bản chất:** Đúng thiết kế.

### D7 · Content bị reject / gỡ sau khi đã duyệt và đã có view

**Cơ chế:** content đã được duyệt, đã tích luỹ view, sau đó bị reject hoặc gỡ. Hệ thống ngừng crawl và loại content khỏi đối soát.

**Biểu hiện:** **N > Đ** — mục Nội dung vẫn giữ số view đã tích luỹ, đối soát mất hẳn dòng của content. Đây là case dễ gây tranh cãi nhất với creator vì họ đã thấy số view trên hệ thống trước đó.

**Bản chất:** Đúng thiết kế.

### D8 · Content chưa duyệt / đang chờ duyệt

**Cơ chế:** view của content chưa được duyệt không được gộp vào đối soát và không được dùng để xét mốc thưởng.

**Bản chất:** Đúng thiết kế. Sau khi content được duyệt, cần kiểm tra lại việc gộp view.

### D9 · Content không thoả điều kiện nhiệm vụ

**Cơ chế:** content không đáp ứng một trong các điều kiện của nhiệm vụ: sai/thiếu **hashtag**, **thời gian đăng bài** nằm ngoài khoảng quy định, hoặc đăng từ **kênh không nằm trong danh sách kênh đã liên kết**.

**Biểu hiện:** content có view ở mục Nội dung nhưng không sinh thưởng.

**Bản chất:** Đúng thiết kế.

**Dấu hiệu phân biệt với bug:** nếu creator khác **trong cùng nhiệm vụ, cùng khoảng ngày** vẫn được thưởng bình thường ⇒ vấn đề mang tính cá biệt của content/user (nhóm D), không phải lỗi cấu hình chung.

---

## 7. Nhóm E — Mốc thưởng theo tier

Áp dụng cho campaign có **cơ chế thưởng theo mốc view (tier)**. Đặc điểm chung: số view hiển thị thì đúng, nhưng **mốc thưởng đứng yên** ở mốc thấp hơn hoặc mức thưởng của mốc không được cộng — làm file đối soát lệch so với kỳ vọng.

### E1 · View hiển thị ≠ view được tính thưởng khi xét mốc ⚠️

**Cơ chế:** việc xét mốc dựa trên **view được tính thưởng** (đã lọc theo điều kiện nhiệm vụ, thời gian hiệu lực, cap...), **không phải view hiển thị thô**. View đã lọc luôn ≤ view thô, nên creator có thể thấy mình "đã đạt mốc" trong khi hệ thống xác định là **chưa đạt**.

**Ví dụ thực tế (case Phở Cung Đình):** file đối soát ghi thưởng thông số **N views** trong khi mốc tính thưởng lại áp cho **M views** — hai con số khác nhau trên cùng một file, do đến từ hai loại chỉ số khác nhau.

**Biểu hiện:** view hiển thị ≥ ngưỡng mốc, nhưng view-được-tính-thưởng < ngưỡng mốc.

**Bản chất:** Đúng thiết kế.

**Hạn chế đã biết:** file export **chưa có cột "view được tính thưởng"** riêng, nên Ops không tự đối chiếu được — đã đề xuất bổ sung (backlog PB-11: thêm cột "view được tính thưởng" và "mốc đã đạt").

### E2 · Cấu hình mốc thưởng sai hoặc thiếu

**Cơ chế:** setup tier trong admin không khớp với thể lệ campaign đã duyệt — chưa set mốc, sai ngưỡng view, hoặc sai số tiền của mốc.

**Biểu hiện:** đối soát chi đúng theo setup nhưng sai so với thể lệ mà Biz đã cam kết với partner.

**Bản chất:** Bug cấu hình (do con người). **Không được tự sửa số tiền** — phải có PM/Biz xác nhận, và sau khi sửa còn phải xác định có cần chạy lại tính thưởng cho khoảng đã qua hay không.

### E3 · Job nhảy mốc chưa chạy / chạy trễ

**Cơ chế:** cơ chế cộng thưởng theo mốc chạy theo batch/chu kỳ crawl. Creator mới đạt mốc trong vài giờ gần đây thì hệ thống chưa kịp nhảy mốc.

**Biểu hiện:** **tạm thời** — hết một chu kỳ (thường trong 24 giờ) là khớp lại.

**Bản chất:** Đúng thiết kế nếu chưa quá chu kỳ; quá chu kỳ mà chưa nhảy → nghi job lỗi hoặc không được trigger.

**Hạn chế đã biết:** hệ thống **không log thời điểm nhảy mốc**, nên không tách bạch được "chưa tới kỳ" với "bug logic" — đã đề xuất bổ sung.

### E4 · Lỗi logic tính tier

**Cơ chế:** view-được-tính-thưởng đã vượt ngưỡng mốc, content đủ điều kiện, còn budget và chưa chạm cap, đã qua chu kỳ tính — **nhưng vẫn không nhảy mốc**. Thường là lỗi trigger reward theo mốc.

**Biểu hiện:** loại trừ được toàn bộ E1, E2, E3, E5, E6 mà vẫn thiếu thưởng mốc. Creator khác cùng campaign đã nhảy mốc bình thường.

**Bản chất:** Bug. Cần dev kiểm tra logic tier và có thể phải chạy lại tính thưởng.

### E5 · Đạt mốc ngoài thời gian hiệu lực nhiệm vụ

**Cơ chế:** thời điểm view chạm ngưỡng mốc nằm **sau khi** campaign/nhiệm vụ đã kết thúc, hoặc rơi vào khoảng nhiệm vụ đang tắt (tham chiếu chéo D1).

**Bản chất:** Đúng thiết kế. Nếu Biz muốn ghi nhận thì phải có xác nhận PM/Biz rồi điều chỉnh setup.

### E6 · Hết budget / chạm cap đúng tại thời điểm đạt mốc

**Cơ chế:** creator đạt mốc nhưng budget campaign đã cạn hoặc trần thưởng theo user/content đã chạm — không còn đủ để chi mức thưởng của mốc đó.

**Biểu hiện:** mốc được ghi nhận là đạt nhưng số tiền tương ứng không xuất hiện hoặc chỉ xuất hiện một phần ở đối soát.

**Bản chất:** Đúng thiết kế.

---

## 8. Nhóm F — Cách đọc số và tầng hiển thị

Đặc điểm chung: **phần lớn không có lệch thật.** Số liệu hệ thống đúng, chênh lệch đến từ việc so sánh nhầm loại chỉ số, nhầm khoảng thời gian, hoặc từ cache phía hiển thị. Phải loại trừ hết nhóm này trước khi kết luận là bug.

### F1 · So nhầm view lũy kế với view phát sinh trong ngày ⚠️ BẪY PHỔ BIẾN #1

**Cơ chế:** file đối soát có cả cột **view lũy kế** và **view phát sinh trong ngày**. Lấy nhầm cột này so với cột kia ở nguồn khác cho ra chênh lệch lớn và hoàn toàn giả.

**Bản chất:** Đọc sai. Trước khi kết luận lệch, phải xác nhận cả ba nguồn đang cùng một loại chỉ số.

### F2 · Lệch múi giờ / mốc cắt ngày ⚠️ BẪY PHỔ BIẾN #2

**Cơ chế:** hai nguồn dùng mốc cắt ngày khác nhau (hoặc khác múi giờ), nên một phần view bị xếp sang ngày kế tiếp ở nguồn này mà không ở nguồn kia.

**Dấu hiệu nhận diện:** chênh lệch của ngày N **gần đúng bằng** phần đầu ngày N+1. Khi khớp dấu hiệu này thì gần như chắc chắn là mốc cắt ngày chứ không phải mất dữ liệu.

**Bản chất:** Đọc sai — thường không phải bug.

### F3 · Bộ lọc mặc định mục Thông số là 7 ngày gần nhất

**Cơ chế:** mục Thông số mặc định lọc **7 ngày gần nhất**. Nếu không chỉnh lại khoảng ngày cho khớp với khoảng đang đối chiếu, số tổng hợp sẽ luôn khác file đối soát.

**Bản chất:** Đọc sai.

### F4 · Lọc sai `event_id` hoặc sai khoảng ngày trong file đối soát

**Cơ chế:** file đối soát chứa dữ liệu của nhiều sự kiện. Lọc thiếu `event_id` hoặc lệch khoảng ngày cho ra tập dòng khác với tập đang xem ở mục Nội dung.

**Bản chất:** Đọc sai.

### F5 · Cache / FE hiển thị lệch

**Cơ chế:** backend đã tính và cộng thưởng đúng, nhưng trang cá nhân creator hoặc màn hình hiển thị chưa cập nhật cache → hiển thị số view / mốc thưởng / số tiền tạm tính **thấp hơn** thực tế.

**Biểu hiện:** file đối soát và dữ liệu backend **có** thưởng đúng, chỉ có màn hình hiển thị lệch. Đây là điều **phải làm rõ đầu tiên** khi creator báo thiếu thưởng: thiếu tiền thật hay chỉ hiển thị sai.

**Bản chất:** Bug hiển thị — mức ưu tiên thấp hơn thiếu tiền thật.

### F6 · Bài đã bão hoà tự nhiên, bị báo nhầm là đứng view

**Cơ chế:** bài viết hết vòng đời phân phối, view tăng rất chậm hoặc không tăng nữa một cách tự nhiên.

**Dấu hiệu phân biệt:** "đứng view" thật là số **không đổi hoàn toàn** qua nhiều ngày. Nếu vẫn nhích vài view/ngày, và số view trên nền tảng gốc **bằng** số trên hệ thống ⇒ hệ thống đang đúng.

**Bản chất:** Đọc sai — không phải lỗi hệ thống.

---

## 9. Đối chiếu với cơ chế cảnh báo lệch kỳ đối soát

Cơ chế cảnh báo mô tả ở [PRD.md](PRD.md) so sánh **giá trị đã chốt lúc tạo kỳ** với **giá trị tính lại tại thời điểm chi tiền**, qua ba loại lệch: `reward`, `cash`, `view`.

Điều này quyết định phạm vi phát hiện: **cảnh báo chỉ bắt được các case làm dữ liệu thay đổi *trong khoảng giữa lúc chốt kỳ và lúc chi tiền*.** Mọi case làm dữ liệu sai **trước khi** kỳ được chốt đều nằm ngoài tầm — vì khi đó cả giá trị chốt lẫn giá trị tính lại đều cùng sai một cách nhất quán, không có chênh lệch nào để phát hiện.

### 9.1 Case cảnh báo bắt được

| Mã | Case | Loại lệch |
| --- | --- | --- |
| C2 | Bản ghi `event_reward` mất / đổi trạng thái / đổi số tiền sau khi chốt kỳ | `reward` |
| C3 | `TotalViewPendingRewarded` chốt kỳ ≠ view tính lại lúc chi | `view` |
| B1 | Dữ liệu về trễ ghi đè — **chỉ khi** việc ghi đè rơi đúng vào khoảng giữa chốt kỳ và chi tiền | `view` / `cash` |
| B2, B3, B4 | Đếm trùng / đứt chuỗi / miss ngày — **chỉ khi** xảy ra sau khi kỳ đã chốt | `view` / `cash` |
| E4 | Lỗi logic tier — nếu làm bản ghi `event_reward` biến động sau khi chốt | `reward` |

### 9.2 Vùng mù — case cảnh báo KHÔNG bắt được

| Nhóm | Vì sao không bắt được |
| --- | --- |
| **A1–A7** (toàn bộ tầng crawl) | View chưa từng vào hệ thống. Giá trị chốt và giá trị tính lại đều thiếu như nhau → không có chênh lệch. |
| **B1–B4** khi sai **trước** lúc chốt kỳ | Kỳ đã chốt trên số sai; tính lại vẫn ra đúng số sai đó. |
| **C1** (không sinh `event-rewards`) | Không có bản ghi thưởng nào để đưa vào kỳ → item không tồn tại trong kỳ đối soát để mà so sánh. |
| **C4, E3** (job batch chưa chạy) | Chưa tới kỳ tính, hai vế vẫn nhất quán. |
| **D1–D9** (toàn bộ nhóm setup) | Hệ thống chạy đúng cấu hình; hai vế luôn khớp nhau. |
| **E1, E2, E5, E6** | Sai từ cấu hình hoặc từ định nghĩa chỉ số, không phải biến động dữ liệu. |
| **F1–F6** | Không có lệch thật ở tầng dữ liệu. |

**Hệ quả cần lưu ý:** phần lớn khiếu nại lệch view thực tế rơi vào nhóm A và D — tức là **nằm ngoài** phạm vi cảnh báo hiện tại. Cảnh báo này là lưới an toàn cho khâu **chi tiền**, không phải cơ chế giám sát chất lượng dữ liệu view đầu vào.

**Rủi ro triển khai liên quan tới nhóm B:** guard `view` dùng **ngưỡng lệch bằng 0**. Trong môi trường mà B1 (dữ liệu về trễ tới 30 ngày) là chuyện thường xuyên, mọi biến động view giữa lúc chốt kỳ và lúc chi đều sẽ làm item bị `rejected` — kể cả những item trước đây vẫn được chi bình thường. Cần theo dõi sát tỉ lệ reject ở kỳ đối soát production đầu tiên sau khi triển khai.

---

## 10. Các khoảng trống hệ thống làm lệch view khó phát hiện

Không phải nguyên nhân gây lệch, nhưng là lý do khiến các case trên tồn tại lâu mà không ai biết:

| # | Khoảng trống | Case liên quan | Trạng thái |
| --- | --- | --- | --- |
| 1 | Không cảnh báo khi dữ liệu ngày cũ bị ghi đè; không lưu lịch sử thay đổi số liệu | B1 | Đề xuất mới |
| 2 | Không có trường ghi nhận **thời điểm** hết budget | D2, E6 | Đã nêu trong meeting |
| 3 | Không cảnh báo khi `totalNotFound` chạm 3; không báo token kênh sắp hết hạn | A1, A4 | Đề xuất mới |
| 4 | File export chưa có cột "view được tính thưởng" và "mốc đã đạt" | E1 | Đề xuất mới |
| 5 | Không log thời điểm nhảy mốc → không tách được "chưa tới kỳ" với "bug logic" | E3, E4 | Đề xuất mới |
| 6 | Chưa có job audit cảnh báo khi creator vượt ngưỡng mốc mà chưa sinh reward tương ứng | E4 | Đề xuất mới |
| 7 | Cơ chế "vendor cào failed thì cho pass" mới chỉ áp dụng cho T-Fluencer | A7 | Đang chờ |

---

## 11. Nguồn tham chiếu

| Nguồn | Nội dung lấy về |
| --- | --- |
| Playbook Ops v2.1 — **PB-1** | Lệch view đối soát / view nội dung / thông số; hai bẫy đọc số; bảng phân biệt nguyên nhân |
| Playbook Ops v2.1 — **PB-3** | View có tính nhưng không cộng thưởng: bật/tắt nhiệm vụ, hết budget, cap, điều kiện content |
| Playbook Ops v2.1 — **PB-4** | Không submit được link Facebook/Threads; cơ chế cho pass khi vendor cào failed |
| Playbook Ops v2.1 — **PB-9** | Content không được crawl tiếp (đứng view): 6 nguyên nhân đã biết |
| Playbook Ops v2.1 — **PB-11** | Đạt mốc view nhưng không được cộng thưởng theo mốc: 8 nguyên nhân |
| Playbook Ops v2.1 — **mục 6** | Backlog cải tiến đã đề xuất |
| Meeting 9/6 | Lệch view Lusso |
| Meeting 14/7 | Case Nha khoa Parkway (C1); thanh toán trùng kỳ |
| Meeting 16/6 | Kiểm tra hiển thị số tiền tạm tính |
| Meeting 21/7 | Lệch view đối soát |
| Case Phở Cung Đình | Thưởng thông số N views vs mốc tính thưởng M views (E1) |
| [PRD.md](PRD.md), [TECH_SPEC.md](TECH_SPEC.md) | Ba loại lệch `reward` / `cash` / `view` và phạm vi phát hiện |

### Bảng thuật ngữ dữ liệu

| Bảng | Vai trò trong luồng view |
| --- | --- |
| `content` | Lưu trạng thái content và cờ `totalNotFound` (≥ 3 thì ngừng crawl) |
| `content-callbacks` | Lịch sử phản hồi crawl cho từng content |
| `content-analytic-daily` | View theo ngày của content — nguồn của mục Nội dung và Thông số |
| `event-rewards` | Thưởng phát sinh từ sự kiện — nguồn của file đối soát |
| `user-social` | Kênh mạng xã hội đã liên kết, bao gồm token |
