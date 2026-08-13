# PRD — Cảnh báo lệch số liệu kỳ đối soát qua email

**Trạng thái:** Đã triển khai (branch `hotfix/issue-view-content`, 12 commit, `d0dd15e4..fb3d122d`)
**Ngày:** 2026-08-12
**Tech spec:** [2026-08-12-reconciliation-alert-tech-spec.md](2026-08-12-reconciliation-alert-tech-spec.md)
**Kế hoạch triển khai:** [superpowers/plans/2026-08-12-reconciliation-mismatch-alert-email.md](superpowers/plans/2026-08-12-reconciliation-mismatch-alert-email.md)

---

## Problem Statement

Khi admin bấm chạy một kỳ đối soát, hệ thống duyệt từng reconciliation item và chi tiền cho người dùng. Trong quá trình đó, hai loại bất thường vẫn luôn xảy ra:

- Bản ghi thưởng mốc (`event_reward`) không còn tồn tại, đã đổi trạng thái, hoặc số tiền trên đó khác số tiền đã chốt trên item.
- Tổng tiền thưởng tính lại từ dữ liệu nguồn tại thời điểm chi khác với số tiền đã chốt lúc tạo kỳ.

Hệ thống **đã** phát hiện được cả hai trường hợp này. Nhưng nó xử lý bằng cách âm thầm đánh dấu item là `rejected`, ghi một dòng `note` vào database, rồi đi tiếp. **Không ai được báo.**

Hệ quả với admin vận hành:

- Người dùng không nhận được tiền mà không ai biết, cho tới khi chính người dùng khiếu nại.
- Muốn biết kỳ vừa chạy có vấn đề gì không, admin phải tự vào màn hình chi tiết, lọc thủ công các item `rejected`, đọc từng dòng `note`. Không có tín hiệu chủ động nào.
- Không có dấu vết nào cho biết mức độ lệch là bao nhiêu — chỉ biết "item này bị loại", không biết "chốt kỳ 1.000.000, thực tế 800.000".

Ngoài ra còn một lỗ hổng chưa được che: **lượt xem được tính thưởng không hề được kiểm tra lại lúc chi.** Giá trị `TotalViewPendingRewarded` được chốt lúc tạo kỳ và ghi thẳng vào cashflow lẫn thông báo cho người dùng. Nếu dữ liệu `event_reward` biến động giữa lúc chốt kỳ và lúc chi, con số đó sai mà không có cơ chế nào phát hiện.

## Solution

Khi một kỳ đối soát chạy xong, hệ thống tự động gửi **một email tổng hợp** tới admin đã tạo ra kỳ đó, liệt kê mọi item bị loại do lệch số liệu.

Email đi qua **API AccessTrade** — cùng đường với email OTP vốn đã chạy thật trong hệ thống. Nội dung template do team AccessTrade lưu giữ; hệ thống chỉ gửi lên mã template kèm dữ liệu điền vào.

Email chứa bảng chi tiết, mỗi dòng một item bị loại, gồm: mã item, mã người dùng, loại item, loại lệch, lý do (nguyên văn dòng `note` đã ghi vào database), giá trị chốt kỳ, giá trị thực tế, và mức chênh lệch.

Đồng thời bổ sung **một guard mới**: trước khi chi tiền cho item loại content, hệ thống tính lại lượt xem được tính thưởng từ dữ liệu nguồn và so với giá trị đã chốt. Lệch dù chỉ một lượt xem cũng loại item và báo cáo — vì cả hai vế đều là số nguyên đếm được từ cùng một nguồn, nên lệch là dấu hiệu dữ liệu đã đổi giữa lúc chốt và lúc chi.

Nguyên tắc bất di bất dịch: **việc cảnh báo không bao giờ được làm hỏng, chặn, hay thay đổi luồng chi tiền.** Gọi API lỗi thì ghi log rồi thôi. Tiền đã chi xong trước khi email được nghĩ tới.

## User Stories

### Nhận cảnh báo

1. Là admin vận hành, tôi muốn nhận email ngay sau khi kỳ đối soát tôi tạo chạy xong và có item bị loại, để tôi biết có vấn đề mà không phải chủ động đi kiểm tra.
2. Là admin vận hành, tôi muốn email chỉ gửi tới đúng người đã tạo kỳ đó, để cảnh báo đến đúng người chịu trách nhiệm chứ không spam cả team.
3. Là admin vận hành, tôi muốn nhận **một** email tổng hợp cho cả phiên thay vì mỗi lệch một email, để hộp thư không bị ngập khi có hàng loạt item lệch.
4. Là admin vận hành, tôi muốn không nhận email nào khi kỳ chạy sạch không lệch gì, để email cảnh báo giữ được ý nghĩa báo động.
5. Là admin vận hành, tôi muốn tiêu đề email nêu rõ đây là cảnh báo đối soát, để nhận ra ngay khi liếc hộp thư.
6. Là admin vận hành, tôi muốn email cảnh báo trông khác rõ với email hệ thống thông thường, để không nhầm với thông báo thường lệ.

### Đọc hiểu nội dung cảnh báo

7. Là admin vận hành, tôi muốn thấy tên và mã kỳ đối soát trong email, để biết cảnh báo thuộc kỳ nào khi tôi quản lý nhiều kỳ cùng lúc.
8. Là admin vận hành, tôi muốn thấy khoảng thời gian của kỳ đối soát, để định vị được phạm vi dữ liệu bị ảnh hưởng.
9. Là admin vận hành, tôi muốn thấy tổng số item bị lệch ngay đầu email, để nắm ngay mức độ nghiêm trọng trước khi đọc chi tiết.
10. Là admin vận hành, tôi muốn mỗi dòng trong bảng có mã item và mã người dùng, để tra cứu ngược vào hệ thống.
11. Là admin vận hành, tôi muốn biết loại lệch của từng dòng (tiền, lượt xem, hay bản ghi thưởng), để phân loại nguyên nhân và ưu tiên xử lý.
12. Là admin vận hành, tôi muốn thấy lý do loại item đúng nguyên văn dòng ghi trong database, để nội dung email và bản ghi hệ thống không bao giờ nói khác nhau.
13. Là admin vận hành, tôi muốn thấy song song giá trị chốt kỳ và giá trị thực tế, để tự đánh giá được mức độ sai lệch.
14. Là admin vận hành, tôi muốn thấy cột chênh lệch được tính sẵn, để không phải tự trừ trong đầu.
15. Là admin vận hành, tôi muốn chênh lệch âm nghĩa là thực tế thấp hơn con số đã chốt, để đọc dấu là hiểu ngay chiều lệch.
16. Là admin vận hành, tôi muốn số liệu hiển thị theo quy ước Việt Nam (dấu chấm phân tách hàng nghìn), để đọc nhanh không nhầm hàng.
17. Là admin vận hành, tôi muốn email nói rõ các item này đã bị từ chối và không được chi trong kỳ, để không hiểu nhầm là tiền vẫn đã ra.
18. Là quản trị hệ thống, tôi muốn có sẵn một file HTML mẫu mô tả đầy đủ các biến, để bàn giao cho team AccessTrade setup template mà không phải giải thích thêm.

### Phát hiện lệch lượt xem thưởng

19. Là admin vận hành, tôi muốn hệ thống kiểm tra lại lượt xem được tính thưởng ngay trước lúc chi, để không chi tiền dựa trên con số đã lỗi thời.
20. Là admin vận hành, tôi muốn item bị loại khi lượt xem thưởng lệch, để tiền không ra khỏi hệ thống dựa trên dữ liệu sai.
21. Là admin vận hành, tôi muốn được cảnh báo cả khi lượt xem thực tế CAO hơn con số đã chốt, vì đó cũng là dấu hiệu dữ liệu bất thường chứ không phải tin tốt.
22. Là admin vận hành, tôi muốn cơ chế kiểm tra không có ngưỡng dung sai, để mọi biến động dữ liệu đều lộ ra thay vì bị che dưới ngưỡng.
23. Là admin vận hành, tôi muốn giá trị đem so được tính từ đúng nguồn dữ liệu đã dùng lúc chốt kỳ, để không có báo động giả do so hai đại lượng khác nghĩa.

### Không phá hỏng luồng chi tiền

24. Là admin vận hành, tôi muốn việc gửi email không bao giờ làm dừng hay chậm quá trình chi tiền, để cảnh báo không trở thành rủi ro mới.
25. Là admin vận hành, tôi muốn kỳ đối soát vẫn hoàn tất bình thường ngay cả khi dịch vụ gửi mail hỏng hoặc từ chối, để sự cố hạ tầng phụ không ảnh hưởng nghiệp vụ chính.
26. Là admin vận hành, tôi muốn hành vi chi tiền của hai guard đã tồn tại giữ nguyên không đổi một ly, để tính năng cảnh báo không âm thầm thay đổi cách hệ thống trả tiền.
27. Là admin vận hành, tôi muốn hệ thống ghi log nguyên văn phản hồi khi dịch vụ mail từ chối, để biết chính xác vì sao email không đi.
28. Là admin vận hành, tôi muốn hệ thống ghi log khi không tra được địa chỉ email người tạo kỳ, để biết vì sao mình không nhận được cảnh báo.
29. Là quản trị hệ thống, tôi muốn nhiều item lệch được ghi nhận song song mà không mất bản ghi nào, vì hệ thống xử lý đối soát bằng nhiều luồng cùng lúc.
30. Là quản trị hệ thống, tôi muốn quá trình gom lệch không gây tranh chấp dữ liệu, để kết quả cảnh báo luôn nhất quán.

### Vận hành và bảo trì

31. Là quản trị hệ thống, tôi muốn tính năng không cần thêm biến môi trường mới, để triển khai không kèm bước cấu hình dễ quên.
32. Là quản trị hệ thống, tôi muốn người nhận được suy ra từ dữ liệu sẵn có trong hệ thống, để không phải bảo trì một danh sách email song song dễ lạc hậu.
33. Là quản trị hệ thống, tôi muốn tính năng dùng lại đúng kênh gửi mail đang chạy thật của hệ thống, để không phải vận hành song song hai hạ tầng gửi mail.
34. Là lập trình viên bảo trì, tôi muốn phần gom lệch tách khỏi phần gửi mail, để kiểm thử được logic mà không cần gọi ra API bên ngoài.
35. Là lập trình viên bảo trì, tôi muốn phần dựng nội dung email tách khỏi phần quyết định gửi cho ai, để sửa giao diện email không đụng tới logic nghiệp vụ.
36. Là lập trình viên bảo trì, tôi muốn mã template được khai báo tập trung một chỗ, để khi AccessTrade cấp mã thật thì chỉ phải sửa đúng một dòng.

## Implementation Decisions

### Nguồn người nhận: suy ra từ lịch sử, không từ cấu hình

Bản thiết kế đầu dùng một danh sách email cấu hình qua biến môi trường. Quyết định cuối: **gửi cho admin đã tạo ra kỳ đối soát đó**, vì đúng người chịu trách nhiệm và không phải bảo trì danh sách song song.

Khó khăn: bản ghi kỳ đối soát **không có** trường lưu người tạo. Giải pháp: truy ngược qua collection lịch sử đối soát — khi một kỳ được tạo, hệ thống đã ghi một bản ghi lịch sử loại `create` mang mã nhân viên tạo. Từ mã đó tra sang collection nhân viên để lấy email.

Lưu ý kỹ thuật: cấu trúc thông tin nhân viên được truyền quanh trong tầng service **không** chứa email; bắt buộc phải đọc bản ghi nhân viên đầy đủ từ database.

Kết quả là **không thêm biến môi trường nào**. Tính năng dùng lại nhóm biến kết nối AccessTrade vốn đã tồn tại và đang chạy thật cho email OTP.

### Ba loại lệch được ghi nhận

| Loại | Ý nghĩa | Nguồn |
|---|---|---|
| `reward` | Bản ghi thưởng mốc không tồn tại, sai trạng thái, hoặc số tiền khác giá trị chốt | Guard đã có sẵn |
| `cash` | Tổng tiền tính lại khác số tiền chốt trên item | Guard đã có sẵn |
| `view` | Lượt xem được tính thưởng tính lại khác giá trị chốt | **Guard mới** |

Hai guard đầu vốn đã tồn tại và đang âm thầm loại item. Thay đổi ở đây là **ghi nhận** chúng, không đổi điều kiện, không đổi thứ tự, không đổi chuỗi lý do ghi vào database.

### Guard lệch lượt xem: không có ngưỡng dung sai

So sánh là bằng-hay-khác tuyệt đối. Lý do: cả hai vế đều là số nguyên đếm được từ **cùng một pipeline tổng hợp, cùng một trường, cùng một phép ép kiểu**. Chúng đồng nghĩa và đồng đơn vị hoàn toàn, nên chênh lệch dù bằng 1 cũng là bằng chứng dữ liệu đã đổi giữa lúc chốt kỳ và lúc chi — không phải nhiễu.

Guard đặt **sau** guard kiểm tra tiền và **trước** mọi thao tác chuẩn bị dữ liệu chi tiền, để item bị loại trước khi bất kỳ giá trị nào chạm vào dòng tiền hoặc thông báo người dùng.

**Đây là thay đổi hành vi chi tiền thật.** Item bị loại là item không được trả tiền. Một số item trước đây được chi nay sẽ bị từ chối nếu dữ liệu thực sự có biến động. Đó là chủ ý — không nên chi tiền theo con số đã lỗi thời — nhưng là rủi ro vận hành lớn nhất của thay đổi này.

### Kiến trúc: bốn module tách bạch

Tách theo trách nhiệm, để phần logic thuần kiểm thử được mà không cần database hay máy chủ mail:

1. **Module gom lệch** — kiểu dữ liệu mô tả một lần lệch, và bộ gom an toàn đa luồng. Thuần logic, không chạm I/O.
2. **Module tra người nhận** — suy ra email admin tạo kỳ. Chạm database, nhưng phần chuẩn hoá danh sách email tách riêng thành hàm thuần.
3. **Module dựng dữ liệu email** — kiểu dữ liệu mô tả nội dung email và hàm chuyển sang định dạng API AccessTrade yêu cầu. Chỉ dựng dữ liệu, không tính toán: mọi số liệu đều đã là chuỗi định dạng sẵn.
4. **Module điều phối gửi** — nối ba module trên với API AccessTrade. Nơi **duy nhất** gọi ra ngoài hệ thống.

Việc tách module 1 khỏi module 4 là có chủ đích: module 1 kiểm thử được không cần mock, module 4 chứa toàn bộ tác dụng phụ.

### An toàn đa luồng

Quá trình chi tiền chạy qua một worker pool **50 luồng song song**, nên bộ gom lệch bắt buộc phải có khoá. Mọi thao tác đọc và ghi đều qua khoá; hàm trả về danh sách trả một **bản sao**, để bên gọi đọc thoải mái trong khi các luồng khác vẫn đang ghi.

Bộ gom còn được làm **chịu được con trỏ rỗng**: cả ba thao tác thêm/đọc/đếm đều trả về êm khi bộ gom chưa được khởi tạo. Lý do: các thao tác này nằm trong đường chi tiền, một điểm khởi tạo mới trong tương lai quên gán sẽ làm sập giữa lúc trả tiền người dùng. Rẻ để loại bỏ vĩnh viễn.

### Điểm gọi: sau khi tiền đã chi xong

Lời gọi gửi mail đặt trong khối chạy nền **đã tồn tại** ở cuối quy trình, tức là sau khi mọi luồng công nhân đã ghi xong bộ gom và trạng thái kỳ đã chuyển hoàn tất. Không tạo luồng nền mới. Hệ quả: tiền đã chi xong hoàn toàn trước khi email được nghĩ tới; kể cả khi gửi mail treo trên timeout, nó chỉ giữ một luồng nền chứ không chặn gì.

### Hợp đồng chống hỏng luồng chính

Hàm gửi cảnh báo **không trả về lỗi** — chữ ký không có giá trị trả về, nên lỗi không thể rò ra ngoài về luồng đối soát. Bốn nhánh thoát, tất cả đều ghi log rồi kết thúc êm:

- Không có lệch nào → về ngay.
- Không tra được email người nhận → ghi log kèm số item lệch, về.
- Gọi API thất bại → ghi log kèm nội dung lỗi, về.
- API trả về trạng thái khác thành công → ghi log kèm nguyên văn phản hồi, về.

Không có đường nào panic.

Nhánh thứ tư đáng lưu ý: API trả mã HTTP 200 kèm trạng thái nằm trong thân phản hồi, nên bắt buộc phải đọc trạng thái mới biết email có thực sự được tiếp nhận hay không. Bỏ qua bước này sẽ dẫn tới việc ghi log "đã gửi thành công" trong khi email chưa hề đi.

### Mã template khai báo tập trung

Mã template và đường dẫn API đặt trong một file hằng riêng, thay vì rải rác trong mã nghiệp vụ. File đó cũng gom luôn mã template OTP vốn đang được viết thẳng trong mã.

Mã template cảnh báo **chưa được AccessTrade cấp**. Giá trị hiện tại đặt theo đúng quy ước đặt tên của mã OTP đã có. Sau khi bàn giao file HTML mẫu và nhận mã thật, chỉ cần sửa đúng một dòng.

### Định dạng số theo quy ước Việt Nam

Phân tách hàng nghìn bằng dấu chấm, cắt bỏ phần thập phân. Cả tiền lẫn lượt xem đều làm tròn về số nguyên: email chỉ để admin nhận biết có lệch, không phải chứng từ kế toán.

## Testing Decisions

### Thế nào là một test tốt ở đây

Chỉ kiểm tra **hành vi quan sát được từ bên ngoài**, không kiểm tra chi tiết cài đặt. Cụ thể: kiểm tra "cho đầu vào này thì trả ra kết quả kia", không kiểm tra "hàm này có gọi hàm kia không". Một test chỉ có giá trị nếu nó **fail được** khi hành vi sai — test luôn xanh bất kể code thế nào là test vô dụng.

Trong quá trình triển khai, hai test được kiểm chứng bằng cách **cố ý phá code rồi xác nhận test đỏ**, sau đó khôi phục:

- Test an toàn con trỏ rỗng: gỡ bỏ kiểm tra rỗng → test panic thật.
- Test bất biến "không lệch thì không chạm database/mail": đảo thứ tự kiểm tra → test panic thật.

Đây là tiêu chuẩn nên áp dụng cho các test tương lai trong vùng này.

### Module nào được kiểm thử

| Module | Kiểm thử | Lý do |
|---|---|---|
| Gom lệch | **Có** — gồm test 200 luồng ghi song song, chạy với công cụ phát hiện tranh chấp dữ liệu | Thuần logic, và an toàn đa luồng là lý do tồn tại của module |
| Điều kiện lệch lượt xem | **Có** — phủ bốn biên: bằng nhau, thấp hơn, cao hơn, cùng bằng 0 | Hàm thuần, quyết định trực tiếp việc tiền có ra hay không |
| Chuẩn hoá danh sách email | **Có** — cắt khoảng trắng, bỏ rỗng, hạ chữ thường, khử trùng giữ thứ tự | Hàm thuần tách được khỏi phần chạm database |
| Định dạng số | **Có** — phủ số 0, số âm, dưới nghìn, đúng nghìn, hàng triệu | Hàm thuần, sai là sai toàn bộ nội dung email |
| Dựng dữ liệu email | **Có** — đếm số dòng, ánh xạ đủ trường, xử lý điều kiện kỳ rỗng | Hàm thuần |
| Dựng dữ liệu gửi API | **Có** — đủ khoá cấp trên và cấp dòng, danh sách rỗng phải là mảng rỗng chứ không phải null | Hàm thuần; sai cấu trúc là API từ chối |
| Hàm điều phối gửi | **Một phần** — chỉ khoá bất biến "không lệch thì không chạm database/API" | Phần còn lại phụ thuộc database và API AccessTrade thật |
| Nội dung hiển thị email | **Không** | Template nằm ở hệ thống AccessTrade, ngoài tầm kiểm soát của repo |
| Tra email người nhận | **Không** | Thuần I/O, cần database thật hoặc tầng mock chưa tồn tại trong dự án |
| Guard trong luồng chi tiền | **Không** | Phụ thuộc các đối tượng truy cập database toàn cục, không kiểm thử đơn vị được nếu không tái cấu trúc — ngoài phạm vi |

Tổng cộng **28 test mới** do tính năng này thêm, nằm trong `pkg/admin/service`; chạy cùng các test có sẵn của package là 37 test, đều xanh.

### Prior art trong dự án

Phong cách test bám theo các test sẵn có trong cùng khu vực: dùng thư viện chuẩn, không framework ngoài; tên hàm test và thông điệp lỗi viết **không dấu**; mỗi test một tình huống rõ ràng. Tham chiếu gần nhất là bộ test dựng dữ liệu item đối soát và bộ test tính lượt xem thưởng đã có từ trước.

## Out of Scope

- **Cấu hình danh sách người nhận.** Đã cân nhắc và bỏ. Người nhận suy ra từ dữ liệu, không cấu hình.
- **Ngưỡng dung sai cho lệch.** Mọi chênh lệch khác 0 đều cảnh báo. Không có tham số điều chỉnh.
- **Cảnh báo định kỳ hoặc theo lịch.** Chỉ kích hoạt tại luồng đối soát khi kỳ chạy.
- **Cảnh báo qua kênh khác** (Slack, webhook, thông báo trong ứng dụng). Chỉ email.
- **Giao diện quản trị** để xem lại lịch sử cảnh báo. Email là kênh duy nhất; dấu vết còn lại nằm ở trạng thái item và log.
- **Tự động sửa lệch hoặc chạy lại item bị loại.** Hệ thống chỉ báo cáo, con người quyết định.
- **Sửa lỗi `panic` trong mẫu email xác thực sẵn có.** Đó là mã chết (xem Further Notes), đã thống nhất không đụng trong phạm vi này.
- **Dọn dẹp hạ tầng SMTP không dùng.** Sau thay đổi này, `intenralsmtp` quay lại trạng thái không có nơi nào gọi tới. Việc xoá hẳn nằm ngoài phạm vi.
- **Thiết kế giao diện email.** Repo chỉ cung cấp file HTML mẫu; nội dung hiển thị cuối cùng do team AccessTrade dựng và lưu giữ.
- **Kiểm soát thời điểm template được setup bên AccessTrade.** Cho tới khi nhận được mã template thật, tính năng sẽ gọi API với mã tạm và bị từ chối — xem Further Notes.
- **Gộp hai truy vấn tổng hợp làm một.** Guard mới chạy lại đúng pipeline mà bước kiểm tra tiền vừa chạy. Đúng chủ ý (bảo đảm hai con số đến từ cùng một lát cắt dữ liệu), có thể tối ưu sau mà không đổi ngữ nghĩa.

## Further Notes

### Rủi ro vận hành 1 — Guard lượt xem thay đổi hành vi trả tiền

Đây là **rủi ro lớn nhất** của toàn bộ thay đổi, lớn hơn nhiều so với chuyện email. Guard không có dung sai, nên nếu lượt xem có biến động lành tính giữa lúc chốt kỳ và lúc chi, kỳ chạy đầu sau khi triển khai có thể loại nhiều item hơn dự kiến. **Item bị loại là item không được trả tiền.**

Bắt buộc theo dõi sát tỉ lệ item bị từ chối ở kỳ đối soát đầu tiên sau khi triển khai, và đối chiếu với các kỳ trước.

### Rủi ro vận hành 2 — Mã template chưa được AccessTrade cấp

**Tính năng chưa gửi được email cho tới khi có mã template thật.** Mã hiện tại đặt theo quy ước, chưa tồn tại bên hệ thống AccessTrade, nên mọi lời gọi sẽ bị từ chối.

Việc bị chặn tốt: hệ thống ghi log nguyên văn phản hồi từ API và đi tiếp, không ảnh hưởng chi tiền. Nhưng nghĩa là **cho tới khi hoàn tất bàn giao, cảnh báo chỉ tồn tại dưới dạng dòng log.**

Các bước cần làm theo thứ tự:

1. Gửi file HTML mẫu (kèm bảng mô tả biến ở đầu file) cho team AccessTrade.
2. Nhận lại mã template.
3. Cập nhật hằng mã template — đúng một dòng.
4. Chạy thử ở môi trường dev, kiểm tra log tìm tiền tố `[notifyMismatches]` để biết nhánh nào đã được đi vào.

Cần thống nhất thêm với team AccessTrade: template bên đó có hỗ trợ **vòng lặp trên mảng** hay không. Dữ liệu gửi lên đưa danh sách dòng lệch dưới dạng mảng đối tượng vì số dòng không cố định. Nếu hệ thống bên đó chỉ nhận biến phẳng, phải đổi sang đẩy một chuỗi HTML đã dựng sẵn — thay đổi này gói gọn trong một hàm.

### Ghi chú — hạ tầng SMTP nay là mã chết

Phát hiện trong quá trình triển khai: **toàn bộ hạ tầng SMTP trong dự án chưa từng có nơi nào gọi tới.** Bản triển khai đầu tiên của tính năng này dùng SMTP, sau đó chuyển sang API AccessTrade cho nhất quán với email OTP.

Sau khi chuyển, SMTP quay lại trạng thái mã chết như trước. Việc xoá hẳn nằm ngoài phạm vi, nhưng nên cân nhắc dọn dẹp ở một thay đổi riêng để tránh người sau nhầm tưởng đó là kênh gửi mail đang hoạt động.

### Hạn chế đã biết

- **Độ phân giải chẩn đoán của lệch loại `reward`.** Guard này gộp ba nguyên nhân (bản ghi không tồn tại / sai trạng thái / sai số tiền) nhưng luôn báo cáo trường "thực tế" bằng số tiền trên bản ghi thưởng. Khi nguyên nhân thật là bản ghi biến mất, email sẽ hiện thực tế bằng 0 — kỹ thuật thì đúng, nhưng admin có thể hiểu nhầm thành "lệch tiền" thay vì "bản ghi biến mất". Dòng lý do nguyên văn có cứu vãn phần nào.
- **Cắt cụt phần thập phân.** Lệch tiền nhỏ hơn 1 đồng sẽ hiển thị chênh lệch bằng 0, khiến email trông như báo động giả. Xác suất thấp vì tiền thường là số nguyên.
- **Năm ở chân email dùng giờ máy chủ** (thường là UTC) thay vì giờ Việt Nam. Chỉ ảnh hưởng dòng bản quyền, sai lệch tối đa vài giờ mỗi năm một lần.
- **Không có sắp xếp khi tra bản ghi lịch sử tạo kỳ.** Đã kiểm chứng: quy trình tạo kỳ chỉ ghi lịch sử loại `create` đúng một lần, nên trùng lặp chỉ xảy ra nếu dữ liệu đã hỏng — và khi đó hai bản ghi vẫn cùng một người tạo.

### Chưa kiểm chứng được nếu thiếu môi trường thật

- Truy vấn tra email người nhận đầu-cuối (cần database có dữ liệu lịch sử và nhân viên thật). Đã kiểm chứng **tĩnh** rằng tên trường, hằng số, và đường đi từ mã nhân viên sang email đều khớp mô hình dữ liệu thật.
- Hình thức email hiển thị trên client thật (Gmail, Outlook). Mẫu dùng bố cục bảng theo đúng quy ước email, nhưng chưa kiểm tra bằng mắt.
