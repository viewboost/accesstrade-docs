# PRD — Tách view được tính thưởng và view vượt ngân sách

Ngày: 2026-08-05
Thiết kế chi tiết: `2026-08-05-tach-view-tinh-thuong-design.md`
Nhãn triage: `ready-for-agent`

## Problem Statement

Khi một event tiêu hết ngân sách, hệ thống vẫn ghi nhận đầy đủ lượt xem của ambassador nhưng không trả tiền cho phần vượt. Mọi con số view hiển thị ra ngoài đều gộp chung hai loại view này, trong khi con số tiền bên cạnh chỉ phản ánh phần được trả. Kết quả là view và tiền không bao giờ khớp nhau, và không ai — nhân viên đối soát, quản lý partner, hay chính ambassador — nhìn ra được vì sao.

Ba nơi đau nhất:

Nhân viên đối soát mở kỳ đối soát, thấy một content có 100.000 lượt xem chờ đối soát nhưng số tiền lại chỉ tương ứng 60.000 lượt. Không có cách nào biết 40.000 lượt kia đi đâu, cũng không có gì để giải trình với partner khi bị hỏi.

Quản lý xem menu thống kê admin, thấy bốn dòng lượt xem đặt song song bốn dòng tiền. Bốn dòng view đều phồng. Mọi tỉ lệ tính từ đó — tiền trên mỗi view, hiệu quả ngân sách — đều sai, và sai một cách âm thầm.

Ambassador vào trang cá nhân, thấy bảng thống kê theo nguồn báo "đã đối soát 100.000 view" nhưng số tiền nhận được lại không tương xứng. Họ không có thông tin nào giải thích rằng event đã hết ngân sách. Hệ thống còn gửi thông báo "Thưởng N view ngày X" với N là con số đã phồng, ghép cùng số tiền đúng.

Dữ liệu để phân biệt hai loại view **đã có sẵn** trong cơ sở dữ liệu từ lâu. Chỉ là chưa có đường đọc nào dùng tới.

## Solution

Mọi nơi hiển thị lượt xem sẽ tách rõ hai loại: **view được tính thưởng** và **view không được tính thưởng do vượt ngân sách**. Hai con số này cộng lại đúng bằng con số tổng đang hiển thị hôm nay, nên không ai mất thông tin — chỉ có thêm.

Nhân viên đối soát nhìn thấy ngay trong bảng kỳ đối soát: cột "lượt xem chờ đối soát" giờ khớp tuyệt đối với cột tiền theo đơn giá mỗi view, và một cột mới cho biết bao nhiêu view bị loại vì vượt ngân sách. Con số này cũng xuất hiện trong file Excel gửi partner.

Quản lý nhìn menu thống kê admin thấy bốn dòng lượt xem đã trừ phần vượt ngân sách, cộng thêm phần bị loại hiển thị riêng. Hai file Excel báo cáo event cũng được sửa theo. Riêng biểu đồ xu hướng giữ nguyên tổng view thật, vì ở đó view là chỉ số hiệu suất chứ không phải chứng từ thanh toán.

Ambassador nhìn bảng trên trang cá nhân thấy một cột mới "không được tính thưởng", và banner cảnh báo ngân sách — hiện đang hỏng và chưa bao giờ hiển thị — sẽ hoạt động trở lại để giải thích nguyên nhân.

Không một field nào đang có bị đổi ý nghĩa. Dữ liệu lịch sử vẫn đọc đúng như lúc được ghi. Trước khi chạy backfill, mọi màn hình hiển thị y hệt hôm nay — không có trạng thái trung gian sai.

## User Stories

### Nhân viên đối soát

1. Là nhân viên đối soát, tôi muốn cột lượt xem chờ đối soát khớp chính xác với cột tiền theo đơn giá mỗi view, để tôi tin được con số mình đang chốt.
2. Là nhân viên đối soát, tôi muốn thấy riêng số view bị loại do vượt ngân sách trên từng dòng content, để tôi biết phần chênh lệch đi đâu.
3. Là nhân viên đối soát, tôi muốn hai con số này cộng lại bằng đúng tổng view chờ đối soát, để tôi kiểm tra chéo được mà không cần mở cơ sở dữ liệu.
4. Là nhân viên đối soát, tôi muốn thông tin đó có trong modal chi tiết của từng content, để tôi tra cứu nhanh khi ambassador khiếu nại.
5. Là nhân viên đối soát, tôi muốn file Excel xuất ra có cột view không được tính thưởng, để tôi gửi thẳng cho partner mà không phải giải thích miệng.
6. Là nhân viên đối soát, tôi muốn các kỳ đã chốt trước đây vẫn hiển thị đúng như lúc chốt, để không phải giải trình lại những kỳ đã xong.
7. Là nhân viên đối soát, tôi không muốn thấy content mà toàn bộ view trong kỳ đều vượt ngân sách xuất hiện trong danh sách với số tiền 0đ, để bảng đối soát chỉ chứa những dòng thực sự phải chi tiền.
8. Là nhân viên đối soát, tôi muốn số view trong thông báo gửi ambassador khớp với số tiền họ nhận, để không tạo ra khiếu nại mới từ chính thông báo của hệ thống.
9. Là nhân viên đối soát, tôi muốn số view ghi trong lịch sử dòng tiền của ambassador khớp với số tiền của giao dịch đó, để đối chiếu ví được.

### Quản lý và partner

10. Là quản lý, tôi muốn bốn dòng lượt xem trong menu thống kê phản ánh phần được tính thưởng, để đặt cạnh bốn dòng tiền mà không lệch.
11. Là quản lý, tôi muốn thấy riêng phần view không được tính thưởng theo từng trạng thái, để đánh giá mức độ event bị chặn bởi ngân sách.
12. Là quản lý, tôi muốn biểu đồ xu hướng lượt xem giữ nguyên tổng view thật, để đo hiệu suất truyền thông chứ không phải hiệu quả chi tiền.
13. Là quản lý, tôi muốn hai file Excel báo cáo event có cả số đã trừ lẫn số bị loại, để gửi partner một tài liệu tự giải thích được.
14. Là quản lý, tôi muốn số liệu của các ngày trong quá khứ cũng đúng sau khi chạy backfill, để so sánh theo thời gian có ý nghĩa.
15. Là quản lý, tôi muốn thay đổi này không làm sai lệch phần ngân sách đã sử dụng của event, để việc kiểm soát ngân sách không bị ảnh hưởng.

### Ambassador

16. Là ambassador, tôi muốn thấy riêng số lượt xem không được tính thưởng trên trang cá nhân, để hiểu vì sao tiền ít hơn kỳ vọng.
17. Là ambassador, tôi muốn cột "chờ đối soát" chỉ chứa những view thực sự sẽ được trả tiền, để hệ thống không hứa hẹn thứ không bao giờ đến.
18. Là ambassador, tôi muốn banner cảnh báo ngân sách hoạt động, để biết trước khi event sắp hết tiền chứ không phải sau khi đã đăng bài.
19. Là ambassador, tôi muốn thấy hạn mức ngân sách tối đa của event, để quyết định có nên đầu tư thêm nội dung hay không.
20. Là ambassador, tôi muốn nhãn cột trong bảng nói rõ đó là lượt xem chứ không phải tiền, để không nhầm với hai dòng tiền ngay phía trên có tên giống hệt.
21. Là ambassador, tôi muốn sắp xếp bảng theo từng cột cho đúng, để so sánh giữa các nguồn.
22. Là ambassador, tôi muốn trải nghiệm này giống nhau trên mọi ứng dụng white-label, để không bị lệch thông tin khi tham gia nhiều chương trình.
23. Là ambassador, tôi muốn tổng ba cột "đã đối soát", "không được tính thưởng" và "chờ đối soát" bằng đúng cột "lượt xem", để tự kiểm tra được.

### Kỹ sư

24. Là kỹ sư, tôi muốn không field nào đang có bị đổi ý nghĩa, để không phải rà lại toàn bộ consumer hiện tại.
25. Là kỹ sư, tôi muốn hệ thống hoạt động bình thường trong khoảng thời gian giữa lúc deploy và lúc backfill xong, để triển khai không cần cửa sổ bảo trì.
26. Là kỹ sư, tôi muốn phép tính hiển thị nằm trong một hàm thuần có test, để không phải suy luận lại mỗi lần đọc code.
27. Là kỹ sư, tôi muốn các nhánh aggregate được sinh bởi một builder chung, để không chép tay thêm mười lăm nhánh vào một file đã có bảy mươi hai nhánh.
28. Là kỹ sư, tôi muốn logic dựng bản ghi đối soát tách khỏi truy cập cơ sở dữ liệu, để test được bất biến giữa view và tiền.
29. Là kỹ sư, tôi muốn mười khối thống kê theo nguồn gộp thành một hàm dùng chung, để không thể quên một nguồn khi thêm field mới.
30. Là kỹ sư, tôi muốn có test hồi quy cho việc gộp đó, để chứng minh mười nguồn vẫn cho kết quả như trước.
31. Là kỹ sư, tôi muốn đường ghi phần thưởng hoàn toàn không bị chạm tới, để không có rủi ro sai tiền.
32. Là kỹ sư, tôi muốn backfill tái sử dụng các job đã có, để không phải viết và vận hành script một lần rồi bỏ.

## Implementation Decisions

### Nguyên tắc chi phối

Không đổi ngữ nghĩa bất kỳ field nào đang tồn tại. Thêm field mới song song. Điều này bảo toàn dữ liệu lịch sử, loại bỏ nhu cầu backfill để số cũ đúng, và cho phép triển khai không cần cửa sổ bảo trì.

Field mới mang kiểu có sẵn breakdown theo trạng thái, không phải một số vô hướng. Một con số đơn lẻ không mô tả nổi hai chiều trạng thái × vượt-ngân-sách, và mọi phương án dùng số vô hướng đều dẫn tới phép trừ cho ra kết quả âm hoặc vô nghĩa ở một nhánh nào đó.

Tầng aggregate chỉ cung cấp hai bộ số song song, không tự trừ. Tầng API quyết định trừ hay không. Quy tắc phân loại: lượt xem đứng cạnh số tiền thì trừ, lượt xem đứng một mình như chỉ số hiệu suất thì giữ nguyên tổng.

Bất biến xuyên suốt, đúng cho từng bucket trạng thái:

```
View.<bucket>  ==  (phần được tính thưởng)  +  ViewExceedBudget.<bucket>
```

### Thay đổi schema

Ba field mới, không xoá hay đổi field nào.

Struct thống kê chung của analytic nhận thêm một nhánh cùng kiểu với nhánh view hiện có. Nhờ hai collection analytic dùng chung struct này, một thay đổi phủ cả hai.

```go
ViewExceedBudget CommonStatisticContent
```

Struct thống kê theo nguồn của user-event nhận thêm nhánh tương tự, kiểu giá trị thường cho đồng bộ với các nhánh còn lại. Hệ quả: field xuất hiện dưới dạng toàn số 0 ở hai response content dùng chung struct — vô hại; và không cần xử lý con trỏ rỗng ở bất kỳ đâu vì document cũ unmarshal ra struct zero.

Bản ghi content trong kỳ đối soát nhận thêm hai số nguyên, vì ở đó chỉ một bucket cần tách:

```go
TotalViewPendingRewarded int64
TotalViewPendingExceeded int64
// bất biến: Rewarded + Exceeded == TotalViewPending
```

### Quy ước bucket của field mới

`ViewExceedBudget` dùng đúng quy ước bucket của nhánh view bên cạnh nó trong cùng struct. Lưu ý quy ước này lệch một nấc so với tên trạng thái thật, và đó là quy ước có sẵn của codebase chứ không phải do PRD này tạo ra: slot `Pending` ứng với trạng thái chờ duyệt, slot `Completed` ứng với trạng thái chờ đối soát, slot `Cashback` ứng với trạng thái đã đối soát.

### Module

**M1 — Builder nhánh aggregate.** Hàm thuần sinh nhánh tổng có điều kiện theo bộ tham số (trường cần cộng, trạng thái, có vượt ngân sách hay không). Ba pipeline cần sửa sẽ dùng chung builder này thay vì chép tay. Interface nhỏ, giấu toàn bộ chi tiết lặp lại của cú pháp aggregate.

**M2 — Bộ tính view settlement.** Hàm thuần nhận nhánh view và nhánh view vượt ngân sách, trả ra bộ số dùng để hiển thị. Đây là nơi tập trung mọi phép trừ dễ sai. Dùng ở converter của menu thống kê admin, và ở tầng response của trang cá nhân nếu chọn trừ ở backend.

**M3 — Builder bản ghi content trong kỳ đối soát.** Tách phần thuần tuý khỏi vòng lặp có truy cập cơ sở dữ liệu: ánh xạ từ kết quả aggregate cộng thông tin content sang bản ghi đối soát, kèm hàm quyết định có bỏ qua content hay không.

**M4 — Mapper thống kê analytic.** Tách phần ánh xạ từ báo cáo aggregate sang struct thống kê analytic. Hiện hai hàm cập nhật analytic đang ánh xạ tay cùng một thứ; gộp lại thì chúng không thể lệch nhau.

**M5 — Builder thống kê theo nguồn.** Gộp mười khối gần giống hệt nhau trong hàm cập nhật thống kê user-event thành một hàm dùng chung gọi trong vòng lặp. Hàm đó hiện dài 636 dòng.

### Quyết định theo từng màn

**Kỳ đối soát.** Pipeline thêm hai nhánh cho bucket chờ đối soát, giữ nguyên nhánh tổng. Bản ghi lưu cả hai số nên tầng hiển thị không phải trừ. Điều kiện bỏ qua content đổi từ "không có view chờ đối soát" sang "không có view chờ đối soát **được tính thưởng**".

Đây là thay đổi hành vi: content mà toàn bộ view đều vượt ngân sách hiện đang vào kỳ với số tiền 0đ, sau thay đổi sẽ bị loại khỏi kỳ. Đánh đổi đã chấp nhận: các bản ghi phần thưởng vượt ngân sách của những content này không được chuyển trạng thái, nên ở lại trạng thái chờ vô thời hạn. Chúng không sinh dòng trùng ở kỳ sau, nhưng sẽ cộng dồn vào số view bị loại của kỳ nào đó về sau nếu content ấy phát sinh thêm view được trả tiền. Nói cách khác, số view bị loại là con số **lũy kế**, không phải chỉ phát sinh trong kỳ.

Hai chỗ tự đúng theo mà không tốn công thêm: số view ghi trong dòng tiền và số view trong thông báo đẩy, vì cả hai lấy thẳng từ bản ghi đối soát.

**Menu thống kê admin.** Pipeline nguồn thêm bộ nhánh vượt ngân sách song song. Hai hàm cập nhật analytic ghi thêm nhánh mới. Pipeline đọc thêm bốn nhánh tổng, không trừ ở tầng này.

Pipeline đọc được năm consumer dùng chung. Quyết định từng chỗ: menu thống kê trừ và bổ sung nhóm mới trong response; hai file Excel báo cáo event trừ và thêm cột; hai biểu đồ xu hướng giữ nguyên tổng.

**Trang cá nhân.** Pipeline theo nguồn thêm bộ nhánh vượt ngân sách. Hàm cập nhật thống kê user-event ghi nhánh mới cho đủ mười nguồn. Response không cần sửa vì nó trả thẳng model, field mới tự chảy ra. Backend không trừ; nơi đặt phép trừ do người triển khai quyết định lúc code.

Cạm bẫy phải ghi nhớ khi viết phép trừ ở màn này: nhánh view của user-event trộn hai nguồn dữ liệu, còn nhánh vượt ngân sách thuần từ bản ghi phần thưởng. Slot `completed` của nhánh view nghĩa là view của content đã duyệt, còn slot `completed` của nhánh vượt ngân sách nghĩa là view của phần thưởng đang chờ đối soát. Hai thứ không cùng hệ đo, trừ thẳng cho ra số vô nghĩa. Chỉ hai slot `cashback` và `transfer` so sánh trực tiếp được.

### Hợp đồng ghi dữ liệu

Câu lệnh cập nhật thống kê user-event ghi đè nguyên khối object thống kê chứ không cập nhật từng field. Hai hệ quả: field mới tự xuất hiện ngay lần hàm chạy đầu tiên nên **không cần migration**; nhưng nếu quên gán ở bất kỳ nguồn nào trong mười nguồn thì giá trị của nguồn đó bị **xoá** chứ không giữ nguyên. Đây là lý do chính khiến M5 được chọn làm cùng đợt.

Hàm này tính lại từ đầu mỗi lần chạy, aggregate lại toàn bộ từ ba collection nguồn, nên tự chữa lành. Backfill chỉ là chạy lại.

### Vùng cấm

Đường tính toán phần thưởng tuyệt đối không bị chạm. Cụ thể, aggregate phục vụ phép trừ chống trả thưởng trùng phải giữ nguyên: lọc thêm điều kiện vượt ngân sách ở đó sẽ khiến hệ thống tưởng view chưa được xử lý và tính thưởng lại, ghi đè lên bản ghi đã hoàn tất.

### Sửa kèm

Ba lỗi có sẵn ở trang cá nhân được sửa trong cùng đợt vì đằng nào cũng phải chạm vào những file đó: nhãn cột lượt xem trùng nhãn dòng tiền; hàm sắp xếp của ba cột đều so sánh nhầm cùng một giá trị; và trường ngân sách của event không được expose ra API nên banner cảnh báo cùng nhãn hạn mức chưa bao giờ hiển thị.

Việc expose trường ngân sách liên quan trực tiếp tới chủ đề: khi ambassador nhìn thấy cột "không được tính thưởng", banner ngân sách chính là thứ giải thích nguyên nhân.

Ngoài ra M5 sẽ sửa luôn lỗi chép nhầm ở hai nguồn youtube, nơi slot lượt xem chờ duyệt đang lấy giá trị của số bình luận.

### Phạm vi frontend

Bảng thống kê theo nguồn không có package dùng chung, mỗi ứng dụng một bản — tổng cộng mười bốn file, bốn biến thể khác nhau ở nhãn cột và bản đồ nguồn. Hàm dựng dữ liệu giống hệt nhau ở cả mười bốn bản nên bản vá áp gần như y nguyên. Interface của response cũng nhân bản theo ứng dụng.

## Testing Decisions

### Thế nào là test tốt ở đây

Chỉ test hành vi quan sát được từ bên ngoài module: đầu vào là dữ liệu, đầu ra là dữ liệu. Không test cách module lưu trạng thái nội bộ, không mock cơ sở dữ liệu, không khẳng định về thứ tự gọi hàm. Nếu một test phải biết module cài đặt thế nào mới viết được thì ranh giới module đang sai, không phải test sai.

Cụ thể với thay đổi này: test khẳng định các **bất biến số học** thay vì khẳng định từng con số cứng ở mọi nơi. Bất biến sống sót qua refactor, con số cứng thì không.

### Prior art

Bộ test hiện có cho phần tách ngân sách trong `internal/service` là khuôn mẫu trực tiếp: hàm thuần, không cần cơ sở dữ liệu, hai mươi mốt trường hợp phủ từ ca thường tới ca biên như hết sạch ngân sách, đơn giá bằng không, chia không hết. Có sẵn hai hàm trợ giúp so sánh số nguyên và số thực. Bộ test cho các module dưới đây bám đúng khuôn đó.

Ngoài ra trong `pkg/admin/model/request` và `pkg/public/service` đã có tiền lệ test cho backfill và cho logic nghiệp vụ thuần.

### Module được test

**M1 — Builder nhánh aggregate.** So khớp cấu trúc sinh ra với cấu trúc kỳ vọng, cho từng tổ hợp trạng thái và cờ vượt ngân sách. Bao gồm trường hợp bản ghi cũ không có cờ vượt ngân sách — điều kiện phải coi là được tính thưởng chứ không phải bị loại.

**M2 — Bộ tính view settlement.** Giá trị cao nhất, vì đây là nơi mọi phép trừ dễ sai tụ lại. Các ca cần phủ: event còn đủ ngân sách nên phần bị loại bằng không; event vượt một phần; event hết sạch ngân sách; dữ liệu cũ chưa backfill nên nhánh vượt ngân sách toàn số 0; và ca hai nguồn dữ liệu lệch nhau khiến kết quả bị chặn về không.

**M3 — Builder bản ghi content trong kỳ đối soát.** Khẳng định bất biến giữa hai số mới và số tổng, khẳng định tích của số view được tính thưởng với đơn giá bằng đúng số tiền chờ đối soát, và phủ logic bỏ qua content mà toàn bộ view đều vượt ngân sách.

**M5 — Builder thống kê theo nguồn.** Vai trò chính là chặn hồi quy cho việc gộp 636 dòng: với cùng đầu vào, mười nguồn phải cho ra kết quả như trước khi gộp. Kèm một test khẳng định nhánh vượt ngân sách được gán cho **đủ** mười nguồn — đây chính là loại lỗi mà hợp đồng ghi đè nguyên khối biến thành mất dữ liệu.

### Không test

M4 không có test riêng, vì nó là ánh xạ trường sang trường không có nhánh rẽ; giá trị của nó nằm ở chỗ khử trùng lặp chứ không ở logic.

Không viết test tích hợp chạm cơ sở dữ liệu cho các pipeline aggregate. Đúng đắn của chúng được xác minh bằng đối chiếu thủ công trên dữ liệu thật trước khi backfill.

### Hồi quy bắt buộc

Chạy lại toàn bộ luồng tính thưởng trên dữ liệu có sẵn và xác nhận collection phần thưởng không thay đổi. Không thay đổi nào trong PRD này được phép chạm vào đường ghi.

## Out of Scope

Các nơi khác cũng đang phồng số view nhưng không sửa lần này: file Excel danh sách ambassador theo partner, thẻ tổng lượt xem trên dashboard admin, và hai tab thống kê của ambassador ngoài trang cá nhân.

Số lượt thích và số bình luận cũng phồng theo đúng cơ chế, ảnh hưởng tới các nhánh tương ứng trong analytic. Không xử lý lần này.

Phép đếm số bản ghi phần thưởng trong một aggregate đang phồng gấp đôi với content bị tách. Hiện chưa consumer nào đọc nên chưa gây hại.

Chỉ số tương tác trong kỳ đối soát sai theo hai cách độc lập nhau: tử số lấy từ collection content nên không bị chặn theo mốc thời gian của kỳ, trong khi mẫu số lấy từ bản ghi phần thưởng thì bị chặn và còn phồng. Sửa nó là đổi ngữ nghĩa field đang có, trái nguyên tắc của đợt này.

View vượt ngân sách bị khoá vĩnh viễn: sau khi kỳ đối soát chạy, mọi bản ghi phần thưởng chờ xử lý đều chuyển sang trạng thái hoàn tất, kể cả bản ghi vượt ngân sách. Từ đó phép trừ chống trả thưởng trùng coi như chúng đã được xử lý. Nếu event được nạp thêm ngân sách sau đó, số view kia không có đường nào để được trả thưởng. Chưa rõ đây là chính sách cố ý hay lỗi tiềm ẩn; cần một phiên thiết kế riêng.

## Further Notes

Thứ tự triển khai đề xuất: hạ tầng dùng chung trước (M1, M2 kèm test), rồi kỳ đối soát (M3) vì đây là yêu cầu gốc và không cần backfill, rồi menu thống kê admin (M4), cuối cùng là trang cá nhân kèm refactor lớn (M5) vì nó chạm nhiều file nhất và có mười bốn bản white-label.

Triển khai an toàn theo từng bước: deploy backend trước, khi đó field mới toàn số 0 và mọi màn hình hiển thị y hệt hôm nay. Chạy backfill sau, số bắt đầu đúng dần. Deploy frontend cuối cùng để hiển thị cột mới. Không bước nào cần cửa sổ bảo trì.

Với event đang chạy thì gần như không cần backfill thủ công cho thống kê user-event: hàm cập nhật được gọi realtime sau mỗi lần tính thưởng, cộng năm điểm chạy định kỳ. Chỉ những cặp ambassador-event đã ngừng phát sinh phần thưởng mới cần chạy tay.

Hai collection analytic thì bắt buộc phải backfill theo khoảng ngày, dùng lại các job lặp theo ngày đã có sẵn.

Một điểm về ngôn ngữ trong codebase mà người triển khai nên biết trước: tên biến chỉ trạng thái trong phần thưởng lệch một nấc so với giá trị trạng thái thật. Nhãn hiển thị trên giao diện thì đúng. Đây là nguồn hiểu nhầm lớn nhất khi đọc phần code này, và PRD này giữ nguyên quy ước đó thay vì sửa, để không mở rộng phạm vi.
