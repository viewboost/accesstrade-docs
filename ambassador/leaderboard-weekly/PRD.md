# PRD — Bảng xếp hạng theo tuần

Ngày: 2026-08-06
Thiết kế chi tiết: `TECH_SPEC.md`
Trạng thái: đã triển khai, chờ bật cho campaign thật

## Problem Statement

Bảng xếp hạng xếp theo con số luỹ kế từ ngày campaign bắt đầu. Với campaign chạy vài tháng, thứ hạng đóng băng: ai vào sớm thì ở trên, ai vào muộn thì mãi ở dưới, và không hoạt động nào trong tuần này làm thay đổi được điều đó.

Creator vào sau nhìn bảng và hiểu ngay là mình không có cửa. Người đứng đầu đã tích luỹ nửa triệu lượt xem từ những tuần trước; một creator mới làm tốt trong bảy ngày cũng chỉ thêm được vài chục nghìn. Khoảng cách đó không đóng lại được bằng nỗ lực, nên họ không cố.

Creator cũ thì ngược lại — ngừng đăng bài vẫn giữ nguyên hạng. Bảng không phân biệt được người đang hoạt động với người đã bỏ cuộc, nên nó không còn phản ánh điều gì đang thực sự diễn ra trong campaign.

Về phía khách hàng, họ mất công cụ tạo nhịp. Một campaign dài không có cột mốc trung gian nào để truyền thông, không có "tuần này ai dẫn đầu" để nhắc lại mỗi thứ Hai.

## Solution

Kỳ xếp hạng trở thành một tuỳ chọn của campaign. Admin chọn trong form event: **Toàn thời gian** giữ nguyên hành vi cũ, **Theo tuần** chỉ tính phần phát sinh từ thứ Hai đến Chủ nhật của tuần hiện tại.

Mặc định là toàn thời gian. Campaign đang chạy không đổi gì khi deploy, và event cũ không có trường cấu hình cũng được hiểu là toàn thời gian.

Khi bật kỳ tuần, dưới tiêu đề bảng xuất hiện một dòng ghi rõ khung thời gian đang tính, dạng `Tuần này · 03/08 – 09/08`. Không có dòng này thì creator chỉ thấy các con số nhỏ đi mà không hiểu vì sao, và toàn bộ mục đích của tính năng biến mất.

Phạm vi cố tình hẹp: chỉ hai kỳ, không có kỳ tháng, không cho xem lại tuần đã qua, không đổi cách tính tiền thưởng.

## User Stories

### Creator

Tôi mới tham gia campaign tuần này. Tôi mở trang chủ và thấy bảng xếp hạng ghi rõ đang tính cho tuần 03/08 – 09/08, nên tôi biết mọi người đều xuất phát lại cùng lúc và công sức tuần này của tôi được tính.

Tôi đăng đều mỗi tuần. Sang thứ Hai tôi mở trang và thấy bảng đã làm mới, không phải chờ đến trưa mới thấy dữ liệu tuần mới.

Tôi nhìn cột tiền bên cạnh và không bị nhầm rằng tiền cũng reset theo tuần — tiền là tiền thật đã kiếm, luỹ kế từ đầu campaign.

### Khách hàng / brand

Tôi muốn tạo cuộc đua mới mỗi tuần cho campaign ba tháng của mình, nhưng không muốn creator cũ mất đi thành tích đã tích luỹ ở nơi khác trên trang.

Tôi cần bật được cho campaign này mà không ảnh hưởng các campaign khác đang chạy.

### Vận hành

Tôi bật hoặc tắt kỳ tuần cho từng campaign trong trang admin, không cần nhờ dev deploy.

Tôi đổi cấu hình và người xem thấy thay đổi ngay, không phải chờ hết hạn cache.

### Kỹ sư

Tôi đọc một dòng cấu hình trên event là biết bảng đang chạy kỳ nào, không phải suy ra từ query param hay trạng thái phía client.

Tôi thêm màn hình mới dùng bảng xếp hạng mà không phải rẽ nhánh theo kỳ, vì hai kỳ trả về cùng một hình dạng dữ liệu.

## Implementation Decisions

### Nguyên tắc chi phối

Không đổi ngữ nghĩa bất kỳ trường nào đang tồn tại. Thêm một trường cấu hình mới, giá trị rỗng đồng nghĩa hành vi cũ. Không cần migration, không cần cửa sổ bảo trì, và rollback chỉ là đổi lại lựa chọn trong admin.

Nhánh luỹ kế không được sửa logic. Nó đang phục vụ mọi campaign đang chạy, nên rủi ro phải bằng không. Kỳ tuần là một nhánh riêng đọc nguồn dữ liệu khác.

Hai nhánh trả cùng một hình dạng dữ liệu. Frontend dùng chung một component hiển thị, không rẽ nhánh theo kỳ. Nếu hai nhánh trả khác nhau thì mỗi partner app sẽ phải sửa hai lần và sẽ có app quên một nửa.

Server chốt biên tuần và trả xuống, frontend chỉ hiển thị lại. Máy người dùng có thể ở múi giờ khác; nếu để client tự tính thì cùng một bảng sẽ hiện hai khung ngày khác nhau trên hai máy.

Kỳ là thuộc tính của campaign, không phải tham số truy vấn. Một nguồn sự thật duy nhất là cấu hình admin. Nếu nhận từ client thì frontend phải chờ dữ liệu event về mới gọi được bảng, và sẽ có lúc gọi sai vì thứ tự tải.

### Nguồn dữ liệu

Ba collection có thể dùng, chỉ một cái đủ.

Collection thống kê luỹ kế theo user-event không có chiều thời gian — nó chỉ giữ con số hiện tại, không biết con số đó hình thành ngày nào. Không cắt theo tuần được.

Collection thống kê theo ngày của từng content có chiều thời gian và tách được view theo nền tảng, nhưng **không có tiền thưởng**. Parasola hiển thị hai cột, view và tiền, nên thiếu một nửa.

Collection thống kê theo ngày của user-event có cả hai. Mỗi bản ghi là số phát sinh của một creator trong đúng một ngày, dựng từ bản ghi phần thưởng lọc theo đúng ngày đó. Cộng theo khoảng ngày ra đúng nghĩa "phát sinh trong tuần". Đây là lựa chọn.

Cái giá phải trả: collection này không tách view theo nền tảng. Các partner app hiển thị icon TikTok/Facebook/Threads kèm số view riêng từng nền tảng sẽ **không dựng lại được giao diện đó** ở kỳ tuần. Parasola không vướng vì bảng của nó là hai cột view và tiền.

### Định nghĩa tuần

Thứ Hai 00:00:00 đến Chủ nhật 23:59:59, theo giờ Việt Nam.

Chọn tuần lịch thay vì bảy ngày tính từ ngày mở campaign vì creator hiểu ngay không cần giải thích. Đánh đổi đã chấp nhận: campaign khởi động giữa tuần sẽ có tuần đầu ngắn hơn bảy ngày. Nếu khách có trao thưởng theo tuần thì tuần đầu không công bằng — xem [Open Questions](#open-questions).

### Thứ hạng tính trên số nào

Tổng view của trạng thái chờ duyệt cộng trạng thái chờ đối soát, đúng công thức mà frontend đang hiển thị ở cột Views.

Nếu xếp hạng chỉ theo một trong hai thì thứ hạng sẽ mâu thuẫn với con số nằm ngay bên cạnh nó trên cùng một dòng, và người dùng sẽ tin con số chứ không tin thứ hạng.

Creator không phát sinh view nào trong tuần bị loại khỏi bảng thay vì hiện với số 0. Bản ghi ngày vẫn tồn tại nếu họ có hoạt động khác, nên không lọc thì bảng đầy dòng rỗng.

### Vùng cấm

Không sửa logic nhánh luỹ kế.

Không đổi cách tính tiền thưởng. Tiền là tiền thật đã kiếm, không reset theo tuần dù bảng có reset.

Không thêm tham số kỳ vào API cho client truyền lên.

Không đụng `TableLeaderBoardView` trong parasola — component đó không file nào import, sửa vào là sửa mù.

### Sửa kèm

Hai thứ sửa nhân tiện vì cùng vùng code, đều có lợi cho nhánh luỹ kế đang chạy:

Tra thông tin creator gom thành một truy vấn cho cả trang thay vì mỗi dòng một truy vấn. Trước đó hai mươi dòng là hai mươi truy vấn, trên một endpoint công khai không cache.

Bổ sung cache cho bảng xếp hạng event. Bảng xếp hạng nhiệm vụ đã cache mười phút từ lâu, bảng event thì chưa, dù query kỳ tuần nặng hơn.

### Phạm vi frontend

Chỉ parasola. Backend dùng chung nên các partner app còn lại chỉ cần thêm phần hiển thị nhãn khi có nhu cầu — với lưu ý về giới hạn nền tảng đã nêu ở mục nguồn dữ liệu.

## Testing Decisions

### Thế nào là test tốt ở đây

Tính năng này gần như không có logic nghiệp vụ phức tạp; rủi ro nằm ở ba chỗ tính toán thuần mà sai thì im lặng: biên tuần, cấu trúc pipeline, và khoá cache.

Test tốt ở đây là test chạy không cần cơ sở dữ liệu, khẳng định một bất biến cụ thể, và sẽ đỏ nếu ai đó sửa nhầm. Test dựng cả Mongo lên để đếm số dòng trả về không nói được gì mà lại chậm.

### Prior art

creator-os tách `mergePinnedRanked` thành hàm thuần export riêng để test không cần cơ sở dữ liệu. Áp dụng đúng cách đó: hàm dựng pipeline và hàm phân giải kỳ đều là hàm thuần, nhận tham số trả giá trị, test gọi thẳng.

### Module được test

**Biên tuần.** Chủ nhật là ca dễ sai nhất vì Go đánh số Chủ nhật bằng 0; không quy về thứ Hai bằng 0 thì Chủ nhật bị đẩy sang tuần sau. Ngoài ra: hai tuần liền kề phải khít, không hở giây nào và không chồng lấn; tuần vắt qua ranh giới tháng phải đúng.

**Cấu trúc pipeline.** Guard chặn giá trị phân trang không hợp lệ, vì Mongo ném lỗi khi giới hạn bằng hoặc nhỏ hơn 0 và lỗi đó bị tầng service nuốt, kết quả là bảng rỗng không rõ nguyên nhân. Thứ tự các bước cũng được khẳng định: đảo bước sắp xếp xuống sau bước bỏ qua là ra sai trang. Công thức xếp hạng và tiêu chí phân định khi bằng điểm cũng nằm trong test này.

**Khoá cache.** Mọi thời điểm trong cùng một tuần phải cho ra cùng một khoá, nếu không cache vỡ vụn. Sang tuần phải đổi khoá, đó là thứ cho phép bảng làm mới ngay lúc 00:00 thứ Hai. Khoá của kỳ luỹ kế không được trôi theo thời gian.

### Không test

Không test tầng truy cập cơ sở dữ liệu. Không test component frontend — thay đổi chỉ là một dòng nhãn có điều kiện.

### Hồi quy bắt buộc

Event không cấu hình kỳ phải trả kết quả y hệt trước khi có tính năng. Đây là hồi quy quan trọng nhất vì nó bảo vệ mọi campaign đang chạy.

## Out of Scope

Kỳ theo tháng. creator-os có sẵn ba kỳ trong model nhưng khách chỉ yêu cầu tuần.

Xem lại tuần đã qua. Cần thêm API liệt kê các tuần trong khoảng thời gian campaign.

Hạng của chính mình khi creator nằm ngoài top hiển thị. Xem [Open Questions](#open-questions).

Ghim creator lên đầu bảng. creator-os có, ambassador chưa cần.

Trao thưởng tự động theo tuần.

Nhãn kỳ cho các partner app ngoài parasola.

## Open Questions

**Bảng biến mất sáng thứ Hai.** Điều kiện hiển thị hiện tại là danh sách không rỗng. Đầu tuần mới chưa có bản ghi ngày nào nên bảng rỗng và cả khối bị ẩn, cho tới lượt chạy đầu tiên của job thống kê. Đề xuất giữ khối và hiện trạng thái rỗng dạng "Tuần này chưa có ai ghi điểm" — mất hẳn một mục quen thuộc gây hoang mang hơn một dòng chữ. Cần PO chốt.

**Tuần lịch hay bảy ngày từ ngày mở campaign.** Chỉ cần đổi nếu khách xác nhận có trao thưởng theo tuần. Cần khách xác nhận.

**Creator không thấy hạng của chính mình.** Ngoài top hiển thị là không biết mình đứng đâu, mà với một cuộc thi đua theo tuần thì đây chính là thứ tạo động lực. Hạ tầng đã có sẵn: API nhận định danh người xem nhưng chưa dùng tới. Lưu ý bắt buộc khi làm: phải đưa định danh người xem vào khoá cache, không thì người này đọc phải dữ liệu của người kia.

**Số liệu cá nhân vẫn luỹ kế.** Bảng xếp hạng theo tuần đứng cạnh khối tiền luỹ kế mà không có gì phân biệt. Tiền nên giữ luỹ kế, nhưng nên gắn nhãn cho khối đó. Cần PO chốt.

## Further Notes

Tính năng này mượn mô hình và cách gọi tên của creator-os — `LeaderboardDefinition.period` với nhãn *Toàn thời gian / Theo tuần* — nhưng phần truy vấn phải tự làm, vì bên đó `queryRanked` bỏ qua trường kỳ và tài liệu ghi rõ kỳ tuần là hạng mục hoãn lại do *"cần daily rollup đầy đủ"*. Ambassador có sẵn bảng thống kê theo ngày chính là daily rollup đó.

Điểm khác biệt có chủ đích so với creator-os: bên đó không hiển thị kỳ ở trang công khai. Bê nguyên thì creator thấy bảng đổi số mà không biết vì sao.

Kỷ luật đánh index cũng học từ creator-os, mục *Index rank* trong tài liệu data model của họ.

Liên quan: `../prd-partner-leaderboard-config-2026-04-02.md` — cấu hình bật/tắt bảng xếp hạng và ẩn/hiện số tiền theo partner. Hai cấu hình độc lập nhau: partner quyết định có hiện bảng không, event quyết định bảng tính theo kỳ nào.
