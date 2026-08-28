# PRD — Tách view được tính thưởng

Ngày viết: 2026-08-05 · Cập nhật: 2026-08-18 sau review lượt 2 PR #101
Nhánh: `hotfix/issue-view-content` · TECH_SPEC: `2026-08-05-tach-view-tinh-thuong-design.md`
Nhãn triage: `ready-for-agent`

> **Lịch sử hướng đi.** Bản đầu hiển thị con số "lượt xem **không** được tính thưởng" cạnh mỗi con số view. Review lượt 1 PR #101 (06/08) bác hướng đó vì con số ấy chỉ phủ một trong nhiều nguyên nhân. Tài liệu này đã viết lại theo hướng được chốt: mọi màn hiển thị phần **được** tính thưởng, phần chênh giải thích bằng tooltip.
>
> **Review lượt 2 (18/08).** Phần lõi không hồi quy: thông báo và lịch sử ví lấy đúng số được tính thưởng, bảng creator không còn phép trừ hay `Math.max`, 149 test backend. Lượt này phát sinh một vấn đề mới ở **banner ngân sách** — câu chữ đang nói sai với hành vi thật — cùng bốn mục tồn từ lượt 1. Cả hai nhóm đã được ghi vào tài liệu này.

## Problem Statement

Khi một event tiêu hết ngân sách, hệ thống vẫn ghi nhận đầy đủ lượt xem của ambassador nhưng không trả tiền cho phần vượt. Mọi con số view hiển thị ra ngoài đều gộp chung hai loại view này, trong khi con số tiền bên cạnh chỉ phản ánh phần được trả. Kết quả là view và tiền không bao giờ khớp, và không ai nhìn ra được vì sao.

Ba nơi đau nhất:

Nhân viên đối soát mở kỳ đối soát, thấy một content có 100.000 lượt xem chờ đối soát nhưng số tiền lại chỉ tương ứng 60.000 lượt. Không có cách nào biết 40.000 lượt kia đi đâu, cũng không có gì để giải trình với partner khi bị hỏi.

Quản lý xem menu thống kê admin, thấy bốn dòng lượt xem đặt song song bốn dòng tiền. Bốn dòng view đều phồng. Mọi tỉ lệ tính từ đó — tiền trên mỗi view, hiệu quả ngân sách — đều sai một cách âm thầm.

Ambassador vào trang cá nhân, thấy bảng thống kê theo nguồn báo "đã đối soát 100.000 view" nhưng số tiền nhận được không tương xứng. Họ không có thông tin nào giải thích rằng event đã hết ngân sách. Hệ thống còn gửi thông báo "Đối soát thành công N view" với N đã phồng, ghép cùng số tiền đúng.

Dữ liệu để phân biệt hai loại view **đã có sẵn** trong cơ sở dữ liệu từ lâu. Chỉ là chưa có đường đọc nào dùng tới.

## Solution

Mọi nơi hiển thị lượt xem sẽ có thêm một con số: **lượt xem được tính thưởng** — phần thực sự sinh ra tiền, khớp với số tiền đứng cạnh nó.

Con số tổng ở các cột và dòng đang có **giữ nguyên ý nghĩa**. Chỉ cột và dòng mới mang con số tách. Nhờ vậy không tài liệu nào đổi nghĩa giữa hai kỳ, và người đọc vẫn có con số tổng để đối chiếu.

Phần chênh lệch giữa hai con số **không được hiển thị thành một con số**, mà giải thích bằng tooltip. Đây là quyết định quan trọng nhất của tài liệu này và lý do nằm ở mục Implementation Decisions.

Nhân viên đối soát nhìn thấy trong bảng kỳ đối soát: cột "lượt xem được tính thưởng" khớp tuyệt đối với cột tiền theo đơn giá mỗi view. Con số này cũng có trong file Excel gửi partner.

Quản lý nhìn menu thống kê admin thấy bốn dòng "được tính thưởng" bên cạnh bốn dòng tổng. Biểu đồ xu hướng vẽ **hai đường** — tổng và được tính thưởng — nên khoảng cách giữa chúng chính là phần bị loại, mà không phải cam kết nguyên nhân.

Ambassador nhìn bảng trên trang cá nhân thấy ba cột: lượt xem, lượt xem tính thưởng đã đối soát, lượt xem tính thưởng chờ đối soát. Không con số nào được tính ở trình duyệt — tất cả lấy thẳng từ backend.

Không một field nào đang có bị đổi ý nghĩa trong database. Dữ liệu lịch sử vẫn đọc đúng như lúc được ghi.

## User Stories

### Nhân viên đối soát

1. Là nhân viên đối soát, tôi muốn có một cột lượt xem khớp chính xác với cột tiền theo đơn giá mỗi view, để tôi tin được con số mình đang chốt.
2. Là nhân viên đối soát, tôi muốn cột "lượt xem chờ đối soát" giữ nguyên ý nghĩa là số tổng như trước, để tôi vẫn có con số cũ để đối chiếu.
3. Là nhân viên đối soát, tôi muốn biết vì sao hai con số lệch nhau mà không phải đoán, nên cần một lời giải thích ngay tại chỗ.
4. Là nhân viên đối soát, tôi **không** muốn màn hình đưa ra một con số "không được tính thưởng", vì tôi sẽ phải bảo vệ con số đó trước partner mà không có cơ sở.
5. Là nhân viên đối soát, tôi muốn thông tin đó có trong modal chi tiết của từng content, để tra cứu nhanh khi ambassador khiếu nại.
6. Là nhân viên đối soát, tôi muốn file Excel xuất ra có cột lượt xem được tính thưởng, để gửi thẳng cho partner.
7. Là nhân viên đối soát, tôi muốn các kỳ đã chốt trước đây vẫn hiển thị đúng như lúc chốt ở những cột vốn đã có.
8. Là nhân viên đối soát, tôi không muốn thấy content mà toàn bộ lượt xem trong kỳ đều vượt ngân sách xuất hiện với số tiền 0đ, để bảng chỉ chứa dòng thực sự phải chi tiền.
9. Là nhân viên đối soát, tôi muốn số view trong thông báo gửi ambassador khớp với số tiền họ nhận, để không tạo ra khiếu nại mới từ chính thông báo của hệ thống.
10. Là nhân viên đối soát, tôi muốn số view ghi trong lịch sử dòng tiền của ambassador khớp với số tiền của giao dịch đó.

### Quản lý và partner

11. Là quản lý, tôi muốn bốn dòng lượt xem được tính thưởng đặt cạnh bốn dòng tiền, để đọc được tỉ lệ thật.
12. Là quản lý, tôi muốn bốn dòng lượt xem tổng vẫn còn đó, để so sánh hiệu suất truyền thông với hiệu quả chi tiền.
13. Là quản lý, tôi muốn biểu đồ xu hướng **giữ nguyên đường lượt xem tổng**, để một event hết ngân sách giữa chừng không bị đọc nhầm thành kênh chết.
14. Là quản lý, tôi muốn biểu đồ có thêm đường lượt xem được tính thưởng, để khoảng cách giữa hai đường cho tôi biết ngân sách đang chặn bao nhiêu.
15. Là quản lý, tôi muốn hai file Excel báo cáo event có cả cột tổng lẫn cột được tính thưởng, để gửi partner một tài liệu tự giải thích được.
16. Là quản lý, tôi muốn được báo trước rằng thứ tự cột trong file Excel đã dịch, để cảnh báo partner nào đang có macro đọc theo vị trí cột.
17. Là quản lý, tôi muốn thay đổi này không làm sai lệch phần ngân sách đã sử dụng của event.

### Ambassador

18. Là ambassador, tôi muốn thấy số lượt xem thực sự được tính thưởng, để hiểu vì sao tiền ít hơn kỳ vọng.
19. Là ambassador, tôi muốn biết vì sao một phần lượt xem không ra tiền, nhưng tôi cần lời giải thích trung thực chứ không phải một con số đơn lẻ đổ cho một nguyên nhân.
20. Là ambassador, tôi muốn phân biệt được phần đã đối soát và phần còn chờ đối soát, để biết còn bao nhiêu tiền đang trên đường.
21. Là ambassador, tôi muốn khối tổng ở đầu trang nói rõ dòng nào là tập con của dòng nào, để tôi không cộng nhầm rồi tưởng trang bị lỗi.
22. Là ambassador, tôi muốn banner cảnh báo ngân sách hoạt động, để biết trước khi event sắp hết tiền chứ không phải sau khi đã đăng bài.
22a. Là ambassador, tôi muốn banner nói đúng sự thật về việc lượt xem phát sinh thêm có được tính thưởng hay không, và **không** khẳng định hệ thống đã dừng nhận bài đăng khi thực tế nó vẫn nhận.
22b. Là ambassador, tôi muốn banner trấn an rõ rằng phần thưởng đã ghi nhận trước đó vẫn được chi trả, để không hiểu nhầm là mất tiền.
23. Là ambassador, tôi muốn nhãn cột nói rõ đó là lượt xem chứ không phải tiền, để không nhầm với hai dòng tiền ngay phía trên có tên giống hệt.
24. Là ambassador, tôi muốn sắp xếp bảng theo từng cột cho đúng.
25. Là ambassador, tôi muốn trải nghiệm giống nhau trên mọi ứng dụng white-label.
26. Là ambassador, tôi muốn thông báo đối soát chỉ nói một điều và nói đúng, thay vì kèm một câu giải thích mà hệ thống không đủ cơ sở để khẳng định.

### Kỹ sư

27. Là kỹ sư, tôi muốn không cột hay dòng nào đang có bị đổi ý nghĩa, để không phải rà lại toàn bộ consumer hiện tại.
28. Là kỹ sư, tôi muốn không có phép tính nào cho các con số này ở frontend, vì hai đại lượng từng bị trừ cho nhau không cùng hệ đo.
29. Là kỹ sư, tôi muốn hệ thống hoạt động bình thường ngay sau deploy mà chưa cần backfill.
30. Là kỹ sư, tôi muốn phép tính hiển thị nằm trong hàm thuần có test, để không phải suy luận lại mỗi lần đọc code.
31. Là kỹ sư, tôi muốn các nhánh aggregate được sinh bởi một builder chung, để không chép tay thêm nhánh vào một file đã có bảy mươi hai nhánh.
32. Là kỹ sư, tôi muốn hai converter dùng chung một helper, để chính sách không trôi dạt giữa chúng.
33. Là kỹ sư, tôi muốn helper đó **không** quyết định consumer nào dùng bộ số nào, vì đó chính là sai lầm đã làm biểu đồ hiển thị sai.
34. Là kỹ sư, tôi muốn logic dựng bản ghi đối soát tách khỏi truy cập cơ sở dữ liệu, để test được bất biến giữa view và tiền.
35. Là kỹ sư, tôi muốn mười khối thống kê theo nguồn gộp thành một hàm dùng chung, để không thể quên một nguồn khi thêm field mới.
36. Là kỹ sư, tôi muốn đường ghi phần thưởng hoàn toàn không bị chạm tới.

## Implementation Decisions

### Quyết định chi phối — vì sao không hiển thị con số "không được tính thưởng"

Con số `isBudgetExceeded` chỉ phủ **một** trong nhiều nguyên nhân làm lượt xem tính thưởng thấp hơn lượt xem thật. Các nguyên nhân khác tồn tại trong code và không sinh ra cờ đó: lượt xem phát sinh ngoài khoảng thời gian của schema, schema hết suất, content chưa được duyệt tại thời điểm phát sinh lượt xem.

Ngoài ra ba trần ngân sách khác nhau — theo sự kiện, theo user, theo content — gộp chung một cờ boolean. Nên nhãn "vượt ngân sách" sẽ **nói sai** với creator chạm trần cá nhân trong khi event vẫn còn tiền.

Đặt một con số vào bảng đối soát và file gửi partner với nhãn "không được tính thưởng" là ngầm khẳng định hai điều: đây là toàn bộ phần chênh, và nguyên nhân là vượt ngân sách. Cả hai đều không đúng. Tooltip nói được sự thật mà không phải cam kết con số.

### Nguyên tắc kỹ thuật

**Giữ nguyên ngữ nghĩa mọi cột và dòng đang có; chỉ cột và dòng mới mang con số tách.** Nhờ vậy file Excel gửi partner không có tình trạng cùng tên cột mà số khác nhau giữa hai kỳ, và kỳ cũ với kỳ mới không dùng chung một cột với hai nghĩa.

**Kỳ đối soát cũ suy lại từ bất biến, không đoán.** Bản ghi tạo trước khi hai field ra đời không có key nào trong hai key ấy nên cả hai decode ra `0`. Một hàm trên model xử lý việc này: khi phần được tính thưởng bằng `0`, suy lại bằng `tổng chờ đối soát − phần không được tính thưởng`. Với kỳ cũ thì cả hai đều vắng mặt nên kết quả là toàn bộ số tổng — đúng với thực tế lúc đó, khi chưa có khái niệm view vượt ngân sách và mọi view chờ đối soát đều được trả tiền. Nhánh suy lại không bao giờ chạm dữ liệu mới, vì kỳ tạo sau thay đổi này không thể có phần được tính thưởng bằng `0` — điều kiện bỏ qua content đã loại thẳng những dòng như vậy ngay lúc tạo kỳ. Đây là suy luận từ một bất biến, không phải heuristic đoán bản ghi nào là cũ.

**Cấm phép trừ ở frontend.** Backend cấp thẳng con số cần hiển thị.

**Tầng aggregate chỉ cung cấp, tầng API quyết định.** Một pipeline phục vụ năm consumer với chính sách khác nhau; trừ ở tầng pipeline sẽ áp một chính sách lên tất cả.

**Field mang con số bị loại vẫn giữ trong database**, phục vụ đối soát nội bộ. Chỉ không hiển thị.

### Thay đổi schema

Bốn field mới, không xoá hay đổi field nào đang có trên production. Tên field **không mang chữ "budget"**, vì phần không được trả tiền đến từ nhiều nguyên nhân chứ không riêng ngân sách; chữ "budget" chỉ giữ ở đường ghi và ở các điều kiện lọc, nơi nó đúng nghĩa.

```go
// Cấp nguồn, phục vụ trang cá nhân
UserContentStatistic.ViewRewarded    CommonStatisticContent // Cashback = đã đối soát, Completed = chờ đối soát

// Cấp sự kiện
UserEventStatistic.ViewRewardedTotal CommonStatisticContent // Total = Cashback + Completed

// Analytic, dùng chung cho hai collection
EventAnalyticDailyStatistic.ViewNotRewarded CommonStatisticContent // dữ liệu thô, không hiển thị

// Kỳ đối soát
ReconciliationItemContent.TotalViewPendingRewarded    int64 // khớp TotalCashPending
ReconciliationItemContent.TotalViewPendingNotRewarded int64 // giữ trong DB, không hiển thị
```

### Quy ước bucket

Tên field chỉ trạng thái trong phần thưởng **lệch một nấc** so với giá trị trạng thái thật: slot `Pending` ứng với chờ duyệt, `Completed` ứng với chờ đối soát, `Cashback` ứng với đã đối soát. Nhãn hiển thị trên giao diện thì đúng. Quy ước này được giữ nguyên.

Riêng struct thống kê theo nguồn đặt tên theo status thật, nên phép map sang slot phải **chéo**. Đây là chỗ dễ sai nhất trong toàn bộ thay đổi và không compiler nào bắt được.

### Module

**Builder nhánh aggregate.** Hàm thuần sinh nhánh tổng có điều kiện theo bộ tham số. Ba pipeline dùng chung thay vì chép tay vào một file đã có bảy mươi hai nhánh.

**Bộ tính lượt xem.** Hàm thuần thực hiện phép trừ có kẹp không âm. Là nơi duy nhất trong backend làm phép trừ này.

**Builder nhóm view.** Nhận một struct **named field** — không phải tám tham số `int64` trần, vì mọi đối số cùng kiểu thì hoán nhầm một cặp là biên dịch trót lọt — và trả về cả hai nhóm số. **Không quyết định consumer nào dùng nhóm nào.**

**Builder bản ghi đối soát.** Tách phần thuần khỏi vòng lặp có truy cập cơ sở dữ liệu, kèm hàm quyết định bỏ qua content.

**Builder thống kê theo nguồn.** Một hàm gọi trong vòng lặp thay cho mười khối chép tay dài 636 dòng.

### Quyết định theo từng màn

**Kỳ đối soát.** Cột cũ giữ số tổng, cột mới mang số được tính thưởng. Điều kiện bỏ qua content đổi từ "không có view chờ đối soát" sang "không có view chờ đối soát **được tính thưởng**". Đây là thay đổi hành vi: content 100% vượt ngân sách trước đây vào kỳ với 0đ, nay bị loại.

**Menu thống kê admin.** Bốn dòng tổng giữ nguyên, thêm bốn dòng được tính thưởng.

**Biểu đồ.** Giữ đường tổng, thêm đường thứ hai. Lý do cụ thể: một event 30 ngày cạn ngân sách ngày 20 mà truyền thông vẫn chạy, nếu đường lượt xem là số đã trừ thì nó sụt gần về 0 từ ngày 21. Người xem kết luận "kênh chết" và cắt kênh, trong khi việc cần làm là nạp thêm tiền. Đường thứ hai cộng đúng ba bucket mà đường tổng đang cộng, nếu khác bộ thì hai đường không so sánh được.

**Excel báo cáo event.** Bốn cột tổng giữ nguyên, thêm bốn cột được tính thưởng.

**Trang cá nhân.** Bảng theo nguồn còn ba cột, mọi con số đọc thẳng. Khối tổng thêm một dòng có tiền tố `(trong đó)` để người đọc biết nó là tập con chứ không phải một phần của phép cộng.

**Thông báo đẩy.** Giữ một câu, số view là số được tính thưởng. Câu thứ hai nêu con số bị loại đã bị bỏ, vì push notification không gắn tooltip được nên không thể nói nguyên nhân trung thực.

### Hợp đồng ghi dữ liệu

Câu lệnh cập nhật thống kê user-event ghi đè **nguyên khối** object thống kê. Hai hệ quả: field mới tự xuất hiện ngay lần hàm chạy đầu tiên nên không cần migration; nhưng nếu quên gán ở bất kỳ nguồn nào trong mười nguồn thì giá trị của nguồn đó bị **xoá**.

Hàm này tính lại từ đầu mỗi lần chạy nên tự chữa lành — backfill chỉ là chạy lại.

### Vùng cấm

Đường tính toán phần thưởng tuyệt đối không bị chạm. Aggregate phục vụ phép trừ chống trả thưởng trùng phải giữ nguyên: lọc thêm điều kiện vượt ngân sách ở đó sẽ khiến hệ thống tưởng view chưa được xử lý và tính thưởng lại, ghi đè lên bản ghi đã hoàn tất.

### Banner cảnh báo ngân sách — nội dung phải nói đúng hành vi thật

Banner được sửa để hiển thị được (xem mục Sửa kèm), nhưng câu chữ ba mức ngưỡng ở bản đầu **nói sai**. Hai chuỗi ở mức 95% và 100% được sao chép nguyên văn từ ứng dụng Techcombank, nơi tính năng chặn nộp bài là thật. Ở Ambassador, cờ chặn chỉ được **ghi** xuống cơ sở dữ liệu bằng string key, không có field trên model, không nơi nào đọc, không có toggle, và **không có chốt chặn nào trong luồng nộp nội dung**. Ba đường kiểm chứng độc lập trong review đều cho cùng kết quả: ngân sách chỉ ảnh hưởng tới việc tính thưởng và việc hiển thị, không ảnh hưởng tới quyền nộp bài.

Ngoài ra bộ ngưỡng 75/95/100 trong backend chỉ dùng để chống gửi trùng cảnh báo Telegram, không dùng để chặn gì. Hàm xử lý chỉ chạy khi ngân sách còn lại không đủ trả một phần thưởng cụ thể — tức gần 100%, không phải 95%.

Vì vậy ở mức 95–99% hệ thống **vẫn nhận bài đăng bình thường**, và lượt xem phát sinh thêm **hoàn toàn có thể không được tính thưởng**. Cả hai vế của câu ban đầu đều sai.

Quyết định: giữ nguyên khung render, chỉ đổi ba hằng câu chữ và hậu tố tiêu đề.

- **75% ≤ x < 95%** — nói rõ lượt xem lúc này vẫn được tính thưởng, và khi chạm 100% thì lượt xem mới không còn sinh thưởng. Tạo động lực bằng sự thật, không bằng hối thúc.
- **95% ≤ x < 100%** — ngân sách sắp cạn, lượt xem phát sinh thêm **có thể** không được tính thưởng; phần thưởng đã ghi nhận vẫn được chi trả ở kỳ đối soát gần nhất.
- **x ≥ 100%** — đã dùng hết ngân sách thưởng, lượt xem phát sinh từ giờ sẽ không được tính thưởng; phần thưởng đã ghi nhận vẫn được chi trả. Bỏ câu "chương trình đã khép lại" vì hết ngân sách không phải hết chiến dịch.

Bỏ cả hai emoji. Riêng emoji ăn mừng ở mức 100% là ăn mừng đúng lúc ambassador hết cửa nhận thưởng; badge phần trăm và màu đỏ đã đủ truyền mức độ.

Tooltip trợ giúp bổ sung phạm vi: banner chỉ phản ánh ngân sách **sự kiện**, trong khi ambassador còn có thể chạm hạn mức riêng của mình hoặc hạn mức của từng nội dung.

Ba hằng câu chữ này có **14 bản sao giống nhau từng byte**, phải áp đồng loạt rồi verify bằng checksum. Test chỉ khẳng định theo mức ngưỡng, **không** khẳng định nội dung chuỗi — nên đổi text không làm test đỏ; cần kiểm mắt hoặc bổ sung khẳng định chuỗi để khoá lại.

### Sửa kèm

Ba lỗi có sẵn ở trang cá nhân được sửa trong cùng đợt: nhãn cột lượt xem trùng nhãn dòng tiền; hàm sắp xếp của ba cột đều so sánh cùng một giá trị; và trường ngân sách của event không được expose ra API nên banner cảnh báo cùng nhãn hạn mức chưa bao giờ hiển thị.

Việc expose ngân sách chỉ trả **phần trăm đã dùng**, không trả số tiền tuyệt đối — đây là quyết định của người sở hữu sản phẩm, vì API public trước đó chưa từng lộ con số ngân sách bằng VNĐ.

Ngoài ra sửa lỗi chép nhầm ở hai nguồn youtube, nơi slot lượt xem chờ duyệt đang lấy giá trị của số bình luận.

### Phạm vi frontend

Bảng thống kê theo nguồn không có package dùng chung, mỗi ứng dụng một bản — **14 file**. Khối tổng có ở **12 app**; hai app còn lại hiển thị khối tiền thay vì khối view. Mọi app dùng nhãn tiếng Việt.

## Testing Decisions

### Thế nào là test tốt ở đây

Chỉ test hành vi quan sát được từ bên ngoài module: đầu vào là dữ liệu, đầu ra là dữ liệu. Không test cách module lưu trạng thái nội bộ, không mock cơ sở dữ liệu.

Test khẳng định các **bất biến số học** thay vì con số cứng ở mọi nơi. Bất biến sống sót qua refactor.

Với mọi test kiểm một phép ánh xạ, giá trị mẫu của các nhánh phải **phân biệt nhau**, để hoán nhầm một cặp làm test đỏ với con số sai nhìn thấy được — chứ không chỉ đỏ.

Một test tính lại chính biểu thức của implementation thì không chứng minh gì. Phải ghim giá trị literal.

### Prior art

`internal/service/budget_split_test.go` là khuôn mẫu trực tiếp: hàm thuần, không cần cơ sở dữ liệu, hai mươi mốt trường hợp phủ từ ca thường tới ca biên. Có sẵn hai hàm trợ giúp so sánh số nguyên và số thực.

Toàn bộ 87 test hiện có đều đặt tên **tiếng Anh**, không ngoại lệ. Comment thì tiếng Việt — 68 file `.go` đã như vậy từ trước.

### Module được test

**Builder nhánh aggregate** — so khớp cấu trúc sinh ra cho từng tổ hợp trạng thái và cờ ngân sách, gồm cả trường hợp bản ghi cũ không có cờ, khi đó phải được tính là có thưởng.

**Bộ tính lượt xem** — mọi phép trừ dễ sai tụ ở đây. Phủ ca đủ ngân sách, vượt một phần, hết sạch, dữ liệu chưa backfill, và ca hai nguồn lệch nhau khiến kết quả bị kẹp.

**Builder nhóm view** — ghim rằng nhóm tổng và nhóm được tính thưởng thực sự khác nhau khi có phần bị loại, để một thay đổi gộp chúng lại thành một chính sách sẽ đỏ.

**Builder bản ghi đối soát** — bất biến giữa hai số mới và số tổng, và logic bỏ qua content.

**Builder thống kê theo nguồn** — chặn hồi quy cho việc gộp 636 dòng, và ghim hai bất biến money-path:

```
viewRewarded.cashback  × CashPerView == cash.completed
viewRewarded.completed × CashPerView == cash.pending
```

**Tổng cấp sự kiện** — mỗi nguồn một giá trị phân biệt, để sót hoặc cộng hai lần một nguồn đều làm test đỏ.

**Chuỗi thông báo** — phải render qua template đã nạp thật, không dựng struct bằng tay. Một key properties nạp hỏng cho ra chuỗi rỗng, `fmt.Sprintf` không báo lỗi, và ambassador nhận thông báo trống.

### Không test

Mapper ánh xạ trường sang trường không có nhánh rẽ. Không viết test tích hợp chạm cơ sở dữ liệu cho pipeline; đúng đắn của chúng xác minh bằng đối chiếu thủ công trên dữ liệu thật.

### Hồi quy bắt buộc

Chạy lại toàn bộ luồng tính thưởng trên dữ liệu có sẵn và xác nhận collection phần thưởng không thay đổi. Không thay đổi nào được phép chạm vào đường ghi.

## Ghi nhận từ review lượt 2

Hai mục dưới đây **chưa xử lý**, ghi lại để có dấu vết.

**Guard lượt xem mới đang chặn chi tiền.** Quy trình chạy kỳ đối soát thêm điều kiện loại bỏ content khi số lượt xem được tính thưởng ghi trong bản ghi lệch so với số tính lại, **không có dung sai**. Guard này chạy **sau khi kiểm tiền đã đạt** — tức tiền đã đúng, content vẫn bị loại chỉ vì con số báo cáo lệch một đơn vị. Tiền có thể khớp mà view lệch khi phần thưởng gồm cả lượt thích và bình luận bù trừ nhau, khi đơn giá mỗi view của schema bị sửa, hoặc do chỉ đọc bản ghi đầu tiên với content có nhiều schema. Điểm giảm nhẹ: bản ghi phần thưởng không đổi trạng thái nên kỳ sau tính lại và tự lành — ambassador chậm một kỳ chứ không mất tiền. Đây là **thay đổi hành vi trên đường tiền** và không nằm trong tài liệu này; ghi lại để có dấu vết.

**Gọi aggregate hai lần cho cùng một truy vấn.** Hai hàm lấy tiền và lấy lượt xem được tính thưởng theo content chạy cùng một truy vấn với điều kiện y hệt, chỉ đọc field khác nhau từ kết quả. Trong vòng chạy đối soát chúng được gọi liên tiếp cho từng content qua nhóm năm mươi worker, làm gấp đôi tải lên cơ sở dữ liệu đúng lúc chạy đối soát. Gộp thành một lần gọi trả cả hai giá trị là đủ.

**Bốn mục tồn từ review lượt 1 — trạng thái tính đến 27/08.**

1. **Đã xong.** Đổi tên field `exceedBudget` thành `notRewarded`. Tên còn sót duy nhất nằm trong một test đóng vai chốt chặn, khẳng định payload không còn key `viewExceedBudget`.
2. **Chưa xong.** Trang thống kê phụ vẫn còn ở hai ứng dụng, số vẫn mâu thuẫn với trang cá nhân. Trang này không có menu, link hay nút nào trỏ tới, chỉ vào được bằng cách gõ thẳng địa chỉ. Đề nghị xoá; giữ lại nghĩa là phải bảo trì song song thêm một nguồn số nữa. **Đây là mục tồn duy nhất còn lại từ lượt 1.**
3. **Đã xong.** Kỳ đối soát cũ không còn hiển thị `0` — hàm suy lại trên model xử lý, xem mục Nguyên tắc kỹ thuật. Áp cho cả bảng admin lẫn file Excel.
4. **Đã xong.** Cập nhật tài liệu — mục này chính là việc đó.

**Banner ngân sách (phát hiện chính của lượt 2) — đã xong.** Ba hằng câu chữ đã đổi theo hướng chốt ở trên, áp đủ 14 bản và verify bằng checksum: cả 14 file cho ra cùng một giá trị.

## Out of Scope

Các nơi khác cũng đang phồng số view nhưng không sửa lần này: file Excel danh sách ambassador theo partner, thẻ tổng lượt xem trên dashboard admin, và hai tab thống kê của ambassador ngoài trang cá nhân.

Số lượt thích và số bình luận cũng phồng theo đúng cơ chế. Phép đếm số bản ghi phần thưởng phồng gấp đôi nhưng chưa consumer nào đọc.

Chỉ số tương tác trong kỳ đối soát sai theo hai cách độc lập: tử số lấy từ collection content nên không bị chặn theo mốc thời gian của kỳ, mẫu số lấy từ phần thưởng thì bị chặn và còn phồng.

**Backfill.** Kỳ đối soát cũ **không cần** backfill — hàm suy lại trên model đã xử lý. Với thống kê theo nguồn và analytic theo ngày thì có hai job migration để chạy lại khi cần số quá khứ đúng; hệ thống hoạt động bình thường ngay sau deploy mà chưa cần chạy chúng, vì hàm thống kê tính lại từ đầu mỗi lần chạy nên tự chữa lành.

**Tính năng chặn nộp bài khi hết ngân sách.** Nếu sản phẩm thật sự muốn "dừng nhận bài đăng mới" thì đó là quyết định tính năng, không phải sửa câu chữ. Cần đủ bốn phần: field trên model event, hàm đọc, expose ra admin kèm công tắc, **và một chốt chặn thật trong luồng nộp nội dung**. Ambassador hiện không có phần nào trong bốn phần đó. Tách issue riêng, không gộp vào đợt này.

**View vượt ngân sách bị khoá vĩnh viễn.** Sau khi kỳ đối soát chạy, mọi bản ghi phần thưởng chờ xử lý đều chuyển sang hoàn tất, kể cả bản ghi vượt ngân sách, nên phép trừ chống trả thưởng trùng coi như chúng đã xong. Nếu event được nạp thêm ngân sách sau đó thì số view kia không có đường nào để được trả. Cần một phiên thiết kế riêng.

## Further Notes

**Thứ tự triển khai.** Hạ tầng dùng chung trước, rồi kỳ đối soát vì đây là yêu cầu gốc và không cần backfill, rồi menu thống kê admin, cuối cùng là trang cá nhân vì nó chạm nhiều file nhất.

**Deploy theo bước.** Backend trước — khi đó field mới toàn số 0 và mọi màn hiển thị y hệt hôm nay. Chạy backfill nếu và khi cần. Deploy frontend cuối cùng. Không bước nào cần cửa sổ bảo trì.

**Bản ghi cũ.** Kỳ đối soát tạo trước thay đổi này **không** hiện 0 ở cột "được tính thưởng". Hai field mới vắng mặt trong document cũ nên decode ra 0, nhưng một hàm trên model suy lại từ bất biến `được tính thưởng + không được tính thưởng = tổng chờ đối soát`: với kỳ cũ cả hai đều vắng mặt nên kết quả là toàn bộ số tổng — đúng với thực tế lúc đó, khi mọi view chờ đối soát đều được trả tiền. Áp cho cả bảng admin lẫn file Excel gửi partner. Nhánh suy lại không chạm dữ liệu mới, vì kỳ tạo sau thay đổi này không thể có phần được tính thưởng bằng 0.

**Số pha trộn ở màn thống kê.** Chọn khoảng ngày trải qua thời điểm deploy sẽ ra số pha trộn — ngày mới đã trừ, ngày cũ chưa. Chạy lại hai job analytic theo ngày khi cần số quá khứ đúng.

**Cần báo ops trước khi deploy.** Thứ tự cột trong file Excel báo cáo event đã dịch — bốn cột tiền chuyển từ vị trí 9–12 sang 13–16. Ai đang có file mẫu hoặc macro đọc theo vị trí cột sẽ vỡ.

**Điểm hiển thị sẽ đổi.** Sửa lỗi chép nhầm ở nhánh youtube kéo theo điểm chờ của hai nguồn youtube thay đổi, vì hàm tính điểm sao chép thẳng bốn slot của nhánh view. Cân nhắc thông báo trước cho ambassador có content youtube.

**Một điểm về ngôn ngữ trong codebase.** Tên biến chỉ trạng thái trong phần thưởng lệch một nấc so với giá trị trạng thái thật; nhãn hiển thị thì đúng. Đây là nguồn hiểu nhầm lớn nhất khi đọc phần code này, và tài liệu này giữ nguyên quy ước đó thay vì sửa.
