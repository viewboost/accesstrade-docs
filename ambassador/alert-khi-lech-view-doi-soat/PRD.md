# PRD — Job cảnh báo bất thường dữ liệu view (vòng 2)

**Trạng thái:** Đề xuất — chưa triển khai
**Ngày:** 2026-08-13
**Phạm vi:** 7 alert thuộc "vòng 2" trong đề xuất phân loại 36 case gây lệch view
**Liên quan:** [case.md](case.md) · [2026-08-12-reconciliation-alert-prd.md](2026-08-12-reconciliation-alert-prd.md) · [2026-08-12-reconciliation-alert-tech-spec.md](2026-08-12-reconciliation-alert-tech-spec.md)

---

## Problem Statement

Cơ chế cảnh báo lệch kỳ đối soát đã triển khai (PRD 12/08) là lưới an toàn cho **khâu chi tiền**: nó so giá trị chốt lúc tạo kỳ với giá trị tính lại lúc chi, và chỉ bắt được những case làm dữ liệu biến động **trong khoảng giữa hai mốc đó**.

Vấn đề: phần lớn khiếu nại lệch view thực tế **không rơi vào khoảng đó**. Chúng là dữ liệu đã sai từ trước khi kỳ được chốt — và khi đó cả giá trị chốt lẫn giá trị tính lại đều cùng sai một cách nhất quán, không có chênh lệch nào để phát hiện.

Cụ thể, những gì đang xảy ra mà không ai được báo:

- Content **có view đầy đủ** trong dữ liệu ngày, thoả mọi điều kiện nhiệm vụ, còn budget, chưa chạm cap — nhưng **không sinh bản ghi thưởng nào**. Mắt xích giữa "đã có view" và "được tính thưởng" đứt im lặng. Đã có tiền lệ được xác định (case Nha khoa Parkway).
- Creator **đã vượt ngưỡng mốc thưởng**, đủ mọi điều kiện, đã qua chu kỳ tính — nhưng mốc không nhảy. Không có log thời điểm nhảy mốc, nên không ai tách được "chưa tới kỳ" với "bug logic".
- Vendor cào gặp sự cố diện rộng: hàng loạt content của **nhiều user, nhiều kênh** cùng đứng view trong cùng một khoảng. Chỉ phát hiện khi đủ nhiều creator khiếu nại cùng lúc.
- Hệ thống crawl đều nhưng callback **trả về rỗng**, hoặc content **chưa từng được đẩy vào hàng đợi crawl**. Nhìn từ ngoài, cả hai đều là "view đứng yên" — không phân biệt được với bài đã bão hoà tự nhiên.
- View của một ngày được ghi nhận nhiều hơn một lần, làm số nhảy vọt. Nếu kỳ đối soát chốt đúng ngày đó thì **trả thừa tiền**.
- Job tính thưởng chạy theo batch. Chưa tới kỳ thì lệch là bình thường; quá một chu kỳ mà vẫn lệch thì job đã hỏng hoặc không được trigger. Hiện không có gì phân biệt hai tình huống.

Hệ quả chung: mọi case trên đều **chỉ lộ ra khi creator khiếu nại**. Thời gian từ lúc sự cố xảy ra tới lúc Ops biết được đo bằng ngày hoặc tuần, và trong khoảng đó tiền hoặc đã chi sai, hoặc đã không chi cho người đáng được chi.

## Solution

Một **job quét định kỳ** chạy độc lập với luồng đối soát, mỗi ngày rà toàn bộ dữ liệu view và thưởng của các campaign đang hoạt động, phát hiện bảy loại bất thường, rồi gửi **một email tổng hợp** tới nhóm admin vận hành.

Bảy loại bất thường được phát hiện:

| Mã alert | Case gốc | Nội dung |
|---|---|---|
| `reward_missing` | C1 | Có view trong dữ liệu ngày nhưng không sinh bản ghi thưởng, sau khi loại trừ hết nguyên nhân setup |
| `milestone_missing` | E4 | Vượt ngưỡng mốc, đủ điều kiện, đã qua chu kỳ, nhưng không nhảy mốc |
| `vendor_outage` | A6 | Nhiều content thuộc nhiều user khác nhau, cùng nền tảng, cùng đứng view trong cùng khoảng |
| `reward_lag` | C4, E3 | Chênh lệch giữa view đã ghi nhận và view đã tính thưởng tồn tại quá một chu kỳ |
| `view_duplicated` | B2 | View một ngày nhảy vọt bất thường so với chính content đó |
| `callback_empty` | A2 | Có phản hồi crawl liên tiếp nhưng không sinh dữ liệu view |
| `crawl_not_queued` | A3 | Content hợp lệ thuộc campaign đang chạy nhưng không có dấu vết crawl nào |

Nguyên tắc thiết kế xuyên suốt, rút ra từ chính bản chất của bài toán: **cái đắt nhất ở đây không phải là phát hiện, mà là loại trừ.** Phần lớn chênh lệch giữa view và thưởng là **đúng thiết kế** — nhiệm vụ tắt rồi bật lại, hết budget, chạm cap, ngoài thời gian hiệu lực, content chưa duyệt, không thoả điều kiện hashtag hoặc kênh. Một alert không loại trừ được hết những nguyên nhân này sẽ bắn liên tục vào những trường hợp hệ thống chạy đúng, và sẽ bị Ops tắt đi trong vòng một tuần.

Vì vậy toàn bộ tri thức loại trừ được gom vào **một chỗ duy nhất**, dùng chung cho hai alert nhạy cảm nhất, và được kiểm thử kỹ hơn mọi thành phần khác.

Nguyên tắc thứ hai: **một sự cố chỉ được báo một lần.** Sự cố dữ liệu tồn tại nhiều ngày cho tới khi có người sửa. Nếu mỗi lần quét đều bắn lại, hộp thư sẽ ngập và cảnh báo mất hết ý nghĩa báo động. Hệ thống lưu dấu vân tay từng phát hiện và chỉ báo lại sau một khoảng lặng.

Nguyên tắc thứ ba, thừa hưởng từ cơ chế cảnh báo đối soát: **job cảnh báo không bao giờ được chạm vào dữ liệu nghiệp vụ.** Nó chỉ đọc và báo cáo. Không sửa trạng thái content, không sinh thưởng bù, không đánh dấu bản ghi. Con người quyết định.

## User Stories

### Phát hiện đứt mắt xích view → thưởng

1. Là admin vận hành, tôi muốn được báo khi một content có view trong dữ liệu ngày nhưng không sinh bản ghi thưởng nào, để phát hiện case Parkway trước khi creator khiếu nại.
2. Là admin vận hành, tôi muốn cảnh báo này chỉ bắn khi đã loại trừ hết nguyên nhân setup, để tôi không phải tự kiểm tra lại budget, cap và điều kiện nhiệm vụ cho từng dòng.
3. Là admin vận hành, tôi muốn cảnh báo nêu rõ content nào, thuộc nhiệm vụ nào, ngày nào, bao nhiêu view, để tra cứu ngược vào hệ thống ngay lập tức.
4. Là admin vận hành, tôi muốn biết cảnh báo này ảnh hưởng bao nhiêu creator và tổng bao nhiêu view, để ước lượng mức độ nghiêm trọng trước khi mở từng dòng.
5. Là admin vận hành, tôi muốn cảnh báo chỉ xét những ngày đã đóng hoàn toàn, để không báo động vì dữ liệu của ngày hôm nay còn đang chạy.
6. Là admin vận hành, tôi muốn cảnh báo bỏ qua content thuộc nhiệm vụ không tính theo view, để không báo về những thứ vốn dĩ không bao giờ sinh thưởng.

### Phát hiện mốc thưởng không nhảy

7. Là admin vận hành, tôi muốn được báo khi creator đã vượt ngưỡng mốc mà không có bản ghi thưởng mốc tương ứng, để bắt lỗi logic tier mà hiện không ai phát hiện được.
8. Là admin vận hành, tôi muốn ngưỡng mốc được xét theo **view được tính thưởng** chứ không phải view hiển thị thô, để không báo động giả với những creator chỉ đạt mốc trên số thô.
9. Là admin vận hành, tôi muốn cảnh báo chỉ bắn sau khi đã qua một chu kỳ tính thưởng, để phân biệt được "chưa tới kỳ" với "job hỏng".
10. Là admin vận hành, tôi muốn cảnh báo bỏ qua trường hợp đạt mốc khi campaign đã hết budget hoặc user đã chạm cap, vì đó là hành vi đúng thiết kế.
11. Là admin vận hành, tôi muốn cảnh báo bỏ qua trường hợp thời điểm đạt mốc nằm ngoài thời gian hiệu lực nhiệm vụ, vì đó cũng là đúng thiết kế.
12. Là admin vận hành, tôi muốn thấy ngưỡng mốc mà creator đã vượt và số view được tính thưởng thực tế, để tự xác nhận kết luận của hệ thống.

### Phát hiện sự cố vendor diện rộng

13. Là admin vận hành, tôi muốn được báo ngay khi nhiều content thuộc nhiều user khác nhau cùng đứng view trên cùng một nền tảng, để nhận diện sự cố vendor trước khi nó tích tụ thành hàng loạt khiếu nại.
14. Là admin vận hành, tôi muốn cảnh báo này gộp thành **một dòng cho cả cụm** thay vì một dòng cho mỗi content, để nắm được quy mô mà không bị ngập.
15. Là admin vận hành, tôi muốn cảnh báo nêu rõ nền tảng nào, bao nhiêu content, bao nhiêu user bị ảnh hưởng, để quyết định có escalate lên vendor hay không.
16. Là admin vận hành, tôi muốn cảnh báo chỉ bắn khi vượt cả ngưỡng số content lẫn ngưỡng số user, để phân biệt sự cố diện rộng với vài content lẻ đứng vì lý do riêng.
17. Là admin vận hành, tôi muốn cảnh báo này được đánh dấu mức độ cao nhất trong email, vì đây là loại sự cố duy nhất trong nhóm cần escalate ngay.

### Phát hiện job tính thưởng không chạy

18. Là admin vận hành, tôi muốn được báo khi view đã ghi nhận nhưng chưa quy đổi thành thưởng quá một chu kỳ, để biết job tính thưởng đã hỏng hoặc không được trigger.
19. Là admin vận hành, tôi muốn cảnh báo này phân biệt được với trường hợp chưa tới kỳ, để không bị đánh thức bởi độ trễ bình thường.
20. Là admin vận hành, tôi muốn cảnh báo gộp theo nhiệm vụ chứ không theo từng content, vì job hỏng thì ảnh hưởng cả nhiệm vụ chứ không riêng lẻ.

### Phát hiện đếm trùng view

21. Là admin vận hành, tôi muốn được báo khi view của một ngày nhảy vọt bất thường so với chính content đó, để phát hiện đếm trùng trước khi kỳ đối soát chốt vào đúng ngày đó.
22. Là admin vận hành, tôi muốn ngưỡng bất thường được tính theo mức bình thường của **chính content đó** chứ không theo một con số cố định toàn hệ thống, vì content lớn và content nhỏ có biên độ view khác nhau hoàn toàn.
23. Là admin vận hành, tôi muốn cảnh báo bỏ qua các content có lượng view quá thấp, để biến động vài chục view không bị hiểu thành nhảy vọt.
24. Là admin vận hành, tôi muốn cảnh báo nêu rõ số view của ngày nghi vấn và mức bình thường đem so, để tự đánh giá.
25. Là admin vận hành, tôi muốn cảnh báo này được nêu rõ là **rủi ro trả thừa tiền**, để ưu tiên xử lý trước khi chốt kỳ.

### Phát hiện sự cố tầng crawl

26. Là admin vận hành, tôi muốn được báo khi hệ thống có phản hồi crawl liên tiếp nhưng không sinh dữ liệu view, để phân biệt "crawl hỏng" với "bài đã bão hoà".
27. Là admin vận hành, tôi muốn được báo khi content hợp lệ thuộc campaign đang chạy mà không có dấu vết crawl nào trong nhiều ngày, để phát hiện content bị rơi khỏi hàng đợi.
28. Là admin vận hành, tôi muốn hai cảnh báo này gộp theo kênh khi nhiều content cùng một kênh cùng dính, để nhận ra ngay đây là vấn đề của kênh chứ không phải của từng bài.
29. Là admin vận hành, tôi muốn cảnh báo bỏ qua content thuộc campaign đã kết thúc, vì hệ thống dừng crawl là đúng thiết kế.
30. Là admin vận hành, tôi muốn cảnh báo bỏ qua content đã bị reject hoặc gỡ, vì hệ thống dừng crawl cũng là đúng thiết kế.

### Nhận và đọc cảnh báo

31. Là admin vận hành, tôi muốn nhận **một** email tổng hợp cho cả lần quét thay vì mỗi phát hiện một email, để hộp thư không bị ngập.
32. Là admin vận hành, tôi muốn không nhận email nào khi lần quét sạch, để email cảnh báo giữ được ý nghĩa báo động.
33. Là admin vận hành, tôi muốn email nhóm các phát hiện theo loại alert, để đọc từng nhóm một thay vì một danh sách phẳng lẫn lộn.
34. Là admin vận hành, tôi muốn mỗi nhóm hiển thị tổng số phát hiện ngay đầu nhóm, để nắm quy mô trước khi đọc chi tiết.
35. Là admin vận hành, tôi muốn thấy tổng số phát hiện của cả lần quét ở đầu email, để đánh giá mức độ nghiêm trọng ngay từ dòng đầu.
36. Là admin vận hành, tôi muốn mỗi dòng có mã định danh đủ để tra ngược vào hệ thống, để không phải đoán.
37. Là admin vận hành, tôi muốn số liệu hiển thị theo quy ước Việt Nam, để đọc nhanh không nhầm hàng.
38. Là admin vận hành, tôi muốn tiêu đề email nêu rõ đây là cảnh báo dữ liệu view, để phân biệt với cảnh báo kỳ đối soát vốn đã có.
39. Là admin vận hành, tôi muốn email nói rõ đây là **báo cáo phát hiện**, hệ thống không tự sửa gì, để không hiểu nhầm là đã được xử lý.
40. Là quản trị hệ thống, tôi muốn có sẵn file HTML mẫu mô tả đầy đủ các biến, để bàn giao cho team AccessTrade setup template mà không phải giải thích thêm.

### Không bị ngập cảnh báo

41. Là admin vận hành, tôi muốn một sự cố đã được báo không bị báo lại ở lần quét kế tiếp, để không phải đọc đi đọc lại cùng một nội dung mỗi ngày.
42. Là admin vận hành, tôi muốn sự cố kéo dài vẫn được nhắc lại sau một khoảng lặng, để vấn đề chưa xử lý không bị quên hẳn.
43. Là admin vận hành, tôi muốn số dòng chi tiết trong email có giới hạn trên, để email không phình ra hàng nghìn dòng khi có sự cố diện rộng.
44. Là admin vận hành, tôi muốn email nói rõ khi danh sách đã bị cắt bớt và còn bao nhiêu dòng nữa, để biết con số thật chứ không tưởng là đã hết.
45. Là quản trị hệ thống, tôi muốn ngưỡng của từng alert điều chỉnh được mà không phải sửa mã, để hiệu chỉnh theo dữ liệu thật sau khi chạy.
46. Là quản trị hệ thống, tôi muốn bật tắt được từng alert độc lập, để tắt riêng cái đang nhiễu mà không phải tắt cả job.

### Vận hành và an toàn

47. Là quản trị hệ thống, tôi muốn job cảnh báo **chỉ đọc** dữ liệu nghiệp vụ, để không có đường nào nó làm hỏng dữ liệu thật.
48. Là quản trị hệ thống, tôi muốn job không bao giờ panic dù dữ liệu bất thường tới đâu, để một bản ghi hỏng không làm chết cả lần quét.
49. Là quản trị hệ thống, tôi muốn một alert lỗi không chặn các alert còn lại, để mất một phát hiện chứ không mất cả báo cáo.
50. Là quản trị hệ thống, tôi muốn job không chạy chồng lên chính nó khi lần trước chưa xong, để không nhân đôi tải lên database.
51. Là quản trị hệ thống, tôi muốn job quét theo lô có giới hạn thay vì nạp toàn bộ dữ liệu vào bộ nhớ, để không ảnh hưởng hiệu năng hệ thống.
52. Là quản trị hệ thống, tôi muốn job chạy vào khung giờ thấp điểm và sau khi các job dữ liệu khác đã xong, để đọc trên dữ liệu đã ổn định.
53. Là quản trị hệ thống, tôi muốn lỗi gửi email chỉ được ghi log chứ không làm hỏng lần quét, để hạ tầng mail hỏng không kéo theo mất khả năng phát hiện.
54. Là quản trị hệ thống, tôi muốn log ghi rõ mỗi alert phát hiện bao nhiêu và mất bao lâu, để theo dõi sức khoẻ của chính job này.
55. Là lập trình viên bảo trì, tôi muốn logic phát hiện tách hoàn toàn khỏi phần đọc database, để kiểm thử được mà không cần database thật.
56. Là lập trình viên bảo trì, tôi muốn toàn bộ điều kiện loại trừ nằm ở một chỗ duy nhất, để khi Biz đổi quy tắc thì chỉ phải sửa một nơi.
57. Là lập trình viên bảo trì, tôi muốn thêm một alert mới không phải đụng vào alert cũ, để mở rộng sang vòng 1 và vòng 3 về sau mà không sợ hồi quy.

## Implementation Decisions

### Kênh gửi: email qua API AccessTrade

Dùng lại đúng đường đã chạy cho cảnh báo kỳ đối soát — API AccessTrade với mã template và dữ liệu điền vào — thay vì Telegram (vốn cũng đã có sẵn trong các schedule job hiện tại).

Lý do chọn email dù Telegram sẵn sàng hơn: cảnh báo này là **báo cáo có cấu trúc nhiều nhóm, nhiều dòng, cần tra cứu lại**, không phải tín hiệu tức thời. Telegram hợp cho một dòng thông báo job đã chạy xong; không hợp cho bảng bảy nhóm phát hiện.

**Đánh đổi phải chấp nhận:** cần AccessTrade cấp thêm **một mã template mới**, khác mã template của cảnh báo đối soát. Cho tới khi có mã thật, job vẫn quét và vẫn ghi log đầy đủ, nhưng email bị từ chối — y hệt tình trạng đã gặp ở cảnh báo đối soát. Đây là rủi ro triển khai đã biết, xem Further Notes.

### Người nhận: nhóm admin vận hành, không phải người tạo kỳ

Khác với cảnh báo đối soát — vốn gửi cho đúng admin đã tạo ra kỳ đó, vì có người chịu trách nhiệm rõ ràng.

Job này không gắn với hành động của ai cả. Nó chạy theo lịch, quét dữ liệu toàn hệ thống. Không có "người tạo" để suy ra.

Quyết định: gửi tới **nhóm admin vận hành**, xác định qua vai trò trong hệ thống nhân sự chứ không qua một danh sách email cấu hình riêng. Lý do giống hệt lần trước: không bảo trì danh sách song song dễ lạc hậu.

### Loại trừ nhóm D: một module sâu, dùng chung

Đây là quyết định kiến trúc **quan trọng nhất** của toàn bộ PRD.

Hai alert `reward_missing` và `milestone_missing` đều phải trả lời cùng một câu hỏi trước khi kết luận có bất thường: *"content này, ngày này, có được kỳ vọng sinh thưởng hay không?"*

Câu trả lời phải loại trừ toàn bộ những nguyên nhân sau, mỗi cái đều là hành vi **đúng thiết kế**:

- Nhiệm vụ đang tắt, hoặc ngày đang xét rơi vào khoảng nhiệm vụ từng bị tắt rồi bật lại.
- Campaign hoặc nhiệm vụ đã hết budget.
- User hoặc content đã chạm trần thưởng.
- Ngày đang xét nằm ngoài thời gian hiệu lực của nhiệm vụ.
- Ngày duyệt content nằm ngoài thời gian hiệu lực.
- Content chưa được duyệt, hoặc đã bị reject/gỡ.
- Nhiệm vụ không thuộc loại tính theo view.
- Content không thoả điều kiện nhiệm vụ: hashtag, thời gian đăng, kênh liên kết.
- Campaign đã kết thúc.

Gom tất cả vào **một hàm thuần duy nhất**, nhận đầy đủ ngữ cảnh đã nạp sẵn và trả về hai giá trị: có kỳ vọng sinh thưởng hay không, và nếu không thì vì lý do nào.

Ba lý do cho thiết kế này:

1. **Đúng đắn.** Thiếu một điều kiện là alert ngập false positive và bị tắt. Gom một chỗ thì có một danh sách để rà, thay vì hai bản sao lệch nhau.
2. **Kiểm thử được.** Hàm thuần, không chạm database, phủ được từng nhánh loại trừ bằng test.
3. **Thay đổi được.** Quy tắc nghiệp vụ nhóm D thay đổi theo campaign và theo thoả thuận với partner. Đổi ở một nơi.

Lý do trả về **kèm lý do loại trừ** chứ không chỉ một giá trị đúng/sai: khi Ops nghi ngờ hệ thống bỏ sót, log ghi rõ "content này bị loại vì hết budget" là bằng chứng kiểm chứng được. Không có nó thì module này là hộp đen không ai tin.

**Hạn chế đã biết ngay từ thiết kế:** điều kiện "hết budget" hiện **không kiểm chứng được chính xác theo thời điểm**, vì hệ thống không có trường ghi nhận thời điểm budget cạn. Module chỉ biết trạng thái budget **tại lúc quét**, không biết nó cạn từ ngày nào. Hệ quả: một content không sinh thưởng vì hết budget từ tuần trước vẫn sẽ được loại trừ đúng, nhưng một content không sinh thưởng vì bug trong khi budget vẫn còn, rồi budget cạn sau đó, sẽ bị loại trừ **sai**. Đây là điểm mù đã ghi nhận, không giải quyết trong phạm vi này — cần bổ sung trường thời điểm hết budget trước.

### Ngưỡng: cấu hình được, không viết cứng

Bốn alert cần ngưỡng, và **không alert nào trong số đó có ngưỡng đúng suy ra được từ tài liệu.** Chúng phải hiệu chỉnh theo dữ liệu thật:

| Alert | Ngưỡng cần | Giá trị khởi đầu đề xuất |
|---|---|---|
| `vendor_outage` | Số content tối thiểu, số user tối thiểu, cửa sổ thời gian | 50 content / 10 user / 24 giờ |
| `view_duplicated` | Bội số so với mức bình thường, sàn view tối thiểu | 1.8 lần / 1.000 view |
| `reward_lag` | Số chu kỳ chờ trước khi báo | 1 chu kỳ (24 giờ) |
| `callback_empty` | Số lần callback rỗng liên tiếp | 3 lần |
| `crawl_not_queued` | Số ngày không có dấu vết crawl | 3 ngày |

Đây là **giá trị khởi đầu, không phải giá trị đúng.** Chúng được đặt theo suy luận từ tài liệu case, chưa đối chiếu với phân bố dữ liệu thật. Bắt buộc hiệu chỉnh sau lần quét đầu.

Quyết định kèm theo: mỗi alert **bật tắt được độc lập**. Khi một alert nhiễu quá trong lúc chờ hiệu chỉnh, tắt riêng nó thay vì tắt cả job — nếu không, thực tế sẽ là cả job bị tắt.

Ngưỡng của `view_duplicated` tính theo **mức bình thường của chính content đó** chứ không theo hằng số toàn hệ thống. Một content triệu view và một content nghìn view có biên độ dao động khác nhau hoàn toàn; một ngưỡng tuyệt đối sẽ vừa bỏ sót cái lớn vừa báo động giả cái nhỏ. Kèm một **sàn view tối thiểu** để loại content quá nhỏ, nơi biến động vài chục view dễ vượt mọi bội số.

### Chống bắn lặp: collection trạng thái riêng, có khoảng lặng

Sự cố dữ liệu tồn tại cho tới khi có người sửa. Không có cơ chế chống lặp thì cùng một phát hiện sẽ đi vào email mỗi ngày.

Quyết định: một **collection riêng** lưu lịch sử phát hiện. Mỗi phát hiện có một dấu vân tay suy ra từ loại alert và các mã định danh liên quan. Trước khi đưa vào email, hệ thống tra dấu vân tay đó; nếu đã báo trong khoảng lặng thì bỏ qua.

Đã cân nhắc và bỏ phương án **gắn cờ trên chính bản ghi nghiệp vụ** — dù đã có tiền lệ trong hệ thống với trạng thái kiểm định trên dữ liệu view ngày. Hai lý do: một là nó ghi vào dữ liệu nghiệp vụ, vi phạm nguyên tắc job chỉ đọc; hai là bảy loại alert trỏ tới các loại bản ghi khác nhau, không có một chỗ chung để gắn cờ.

Khoảng lặng **không phải là im lặng vĩnh viễn**. Sau khoảng lặng, sự cố chưa xử lý được nhắc lại — nếu không, một vấn đề bị bỏ quên sẽ biến mất khỏi radar hoàn toàn.

Collection này cũng cho một lợi ích phụ đáng kể: nó là **lịch sử phát hiện tra cứu được**, thứ mà cảnh báo đối soát hiện không có (dấu vết duy nhất ở đó là trạng thái item và log).

### Chia nhóm và cắt bớt trong email

Email nhóm theo loại alert, mỗi nhóm có tiêu đề và tổng số. Phát hiện thuộc `vendor_outage` đã được gộp thành **một dòng cho cả cụm** ngay từ tầng phát hiện, không phải một dòng cho mỗi content — nếu không, một sự cố vendor sẽ tự nó chiếm hết cả email.

Số dòng chi tiết **có giới hạn trên**. Khi vượt, email hiển thị phần đầu và nói rõ còn bao nhiêu dòng nữa. Lý do: sự cố diện rộng sinh ra hàng nghìn phát hiện, và một email hàng nghìn dòng vừa bị nhà cung cấp mail cắt vừa không ai đọc. Con số quan trọng hơn danh sách.

### Kiến trúc: bảy module tách bạch

Tách theo trách nhiệm, để phần logic phát hiện kiểm thử được không cần database:

1. **Module kiểu dữ liệu phát hiện** — mô tả một phát hiện: loại alert, mức độ, các mã định danh, số liệu kèm theo, dấu vân tay. Thuần dữ liệu.
2. **Module loại trừ nghiệp vụ** — hàm thuần trả lời "có kỳ vọng sinh thưởng không, nếu không thì vì sao". Dùng chung cho `reward_missing` và `milestone_missing`.
3. **Module phát hiện** — bảy hàm thuần, mỗi hàm nhận lát dữ liệu đã nạp và trả danh sách phát hiện. Không chạm I/O.
4. **Module quét** — nạp dữ liệu theo lô có giới hạn, gọi module phát hiện. Chạm database, không chứa logic nghiệp vụ.
5. **Module gom kết quả** — gom, khử trùng, gộp cụm, sắp xếp theo mức độ, áp giới hạn số dòng. Thuần logic.
6. **Module trạng thái cảnh báo** — đọc ghi lịch sử phát hiện, quyết định phát hiện nào bị chặn bởi khoảng lặng. Chạm database, nhưng phần quyết định chặn tách riêng thành hàm thuần.
7. **Module gửi** — dựng dữ liệu email và gọi API AccessTrade. Nơi duy nhất gọi ra ngoài hệ thống.

Ranh giới quan trọng nhất là giữa module 3 và module 4: **mọi tri thức nghiệp vụ nằm ở module 3, mọi truy cập dữ liệu nằm ở module 4.** Đây là điều kiện để test được logic phát hiện mà không cần database.

Module 3 được thiết kế để **thêm alert mới không đụng alert cũ**: mỗi hàm phát hiện độc lập, đăng ký vào một danh sách. Vòng 1 và vòng 3 về sau chỉ là thêm phần tử vào danh sách đó.

### Điểm chạy: cron riêng, hằng ngày, sau các job dữ liệu

Đăng ký thành một mục cron mới, chạy hằng ngày theo giờ Việt Nam, **sau** các job đã có: kiểm định dữ liệu view ngày, tự động reject content, gắn thẻ cảnh báo. Lý do: đọc trên dữ liệu đã ổn định, không đọc giữa lúc job khác đang ghi.

Job chỉ xét những **ngày đã đóng hoàn toàn**, không xét ngày hiện tại. Dữ liệu của ngày đang chạy chưa đầy đủ theo định nghĩa, và mọi alert dựa trên nó đều là báo động giả.

Có **khoá chống chạy chồng**, theo đúng cách các job nặng hiện có đang làm: lần quét trước chưa xong thì lần sau bỏ qua.

### Hợp đồng chống hỏng

Job này không nằm trong đường tiền, nên rủi ro thấp hơn cảnh báo đối soát. Nhưng vẫn giữ nguyên tắc tương đương:

- Job **chỉ đọc** dữ liệu nghiệp vụ. Chỉ ghi vào collection trạng thái cảnh báo của chính nó.
- Một alert lỗi **không chặn** các alert còn lại. Mỗi hàm phát hiện chạy trong phạm vi cô lập, lỗi được ghi log và đi tiếp.
- Một bản ghi dữ liệu hỏng **không làm chết lần quét**.
- Lỗi gửi email chỉ ghi log. Lần quét vẫn được coi là hoàn tất, trạng thái vẫn được lưu.
- Không có đường nào panic.

Một quyết định tinh tế: khi gửi email thất bại, **trạng thái cảnh báo vẫn được lưu** — nghĩa là phát hiện đó sẽ không bắn lại ở lần quét kế tiếp dù admin chưa hề nhận được email. Đây là đánh đổi có chủ ý: phương án ngược lại (chỉ lưu khi gửi thành công) sẽ khiến một sự cố mail kéo dài tích tụ thành một email khổng lồ khi mail hồi phục. Bù lại, log ghi rõ lần quét nào gửi thất bại.

## Testing Decisions

### Thế nào là một test tốt ở đây

Giữ nguyên tiêu chuẩn đã áp dụng ở cảnh báo đối soát: chỉ kiểm tra **hành vi quan sát được từ bên ngoài**, không kiểm tra chi tiết cài đặt. Kiểm tra "cho đầu vào này thì trả ra kết quả kia", không kiểm tra "hàm này có gọi hàm kia không".

Một test chỉ có giá trị nếu nó **fail được** khi hành vi sai. Với job cảnh báo, tiêu chuẩn này đặc biệt quan trọng vì cái sai nguy hiểm nhất không phải là "không phát hiện được" mà là "phát hiện nhầm". Vì vậy mỗi hàm phát hiện phải có **cả test khẳng định lẫn test phủ định**: test rằng nó bắn đúng khi có bất thường, và test rằng nó **im lặng** khi dữ liệu bình thường hoặc khi rơi vào một nhánh loại trừ.

Áp dụng lại kỹ thuật đã dùng lần trước: với các bất biến quan trọng, **cố ý phá code rồi xác nhận test đỏ**, sau đó khôi phục. Cụ thể cho vòng này:

- Gỡ một nhánh loại trừ nhóm D → test tương ứng phải đỏ.
- Bỏ kiểm tra khoảng lặng → test chống lặp phải đỏ.
- Bỏ điều kiện "chỉ xét ngày đã đóng" → test phải đỏ.

### Module nào được kiểm thử

Đã thống nhất kiểm thử **toàn bộ bảy module**.

| Module | Trọng tâm kiểm thử |
|---|---|
| Kiểu dữ liệu phát hiện | Dấu vân tay ổn định giữa các lần chạy; phát hiện khác nhau cho vân tay khác nhau |
| **Loại trừ nghiệp vụ** | **Phủ từng nhánh loại trừ một cách độc lập**, cộng với nhánh "không có lý do loại trừ nào" — đây là bộ test dày nhất của cả tính năng |
| Bảy hàm phát hiện | Mỗi hàm: bắn đúng khi bất thường, im lặng khi bình thường, im lặng khi rơi vào loại trừ, phủ các biên ngưỡng (dưới, đúng bằng, trên), xử lý dữ liệu rỗng |
| Module quét | Phân trang đúng, không bỏ sót lô cuối, dừng đúng khi hết dữ liệu, chỉ lấy ngày đã đóng |
| Gom kết quả | Khử trùng, gộp cụm đúng, sắp xếp theo mức độ, cắt đúng giới hạn và báo đúng số dòng còn lại |
| Trạng thái cảnh báo | Chặn đúng trong khoảng lặng, cho qua sau khoảng lặng, phát hiện mới không bị chặn nhầm |
| Module gửi | Dựng đúng cấu trúc dữ liệu gửi API; danh sách rỗng phải là mảng rỗng chứ không phải null; bất biến "không phát hiện thì không chạm API" |

Ba module chạm I/O (quét, trạng thái, gửi) cần **một tầng trừu tượng để kiểm thử** — dự án hiện chưa có tầng mock cho truy cập database, và các job hiện tại gọi thẳng đối tượng truy cập toàn cục.

**Đây là chi phí phát sinh cần nói rõ:** để kiểm thử ba module này, phải đưa vào một ranh giới cho phép thay thế phần truy cập dữ liệu và phần gọi API trong test. Việc này không có tiền lệ trong khu vực mã hiện tại — cảnh báo đối soát đã **không** test ba phần tương ứng chính vì lý do đó. Đổi lại, ranh giới này là thứ khiến các alert của vòng 1 và vòng 3 về sau kiểm thử được ngay từ đầu.

### Prior art trong dự án

Bám theo phong cách test đã có trong cùng khu vực: thư viện chuẩn, không framework ngoài; tên hàm test và thông điệp lỗi viết **không dấu**; mỗi test một tình huống rõ ràng. Tham chiếu gần nhất là bộ test của cảnh báo lệch kỳ đối soát, bộ test dựng dữ liệu item đối soát, và bộ test tính lượt xem thưởng.

## Out of Scope

- **Toàn bộ alert vòng 1** — đứt chuỗi view lũy kế, ngừng crawl khi cờ không tìm thấy chạm ngưỡng, token kênh hết hạn, miss ngày dữ liệu. Đã cân nhắc và Ops quyết định để sau, dù chúng rẻ hơn.
- **Toàn bộ alert vòng 3** — phát hiện ghi đè dữ liệu ngày cũ, cảnh báo hết budget, đối chiếu cấu hình mốc thưởng. Cả ba đều phụ thuộc thay đổi lược đồ dữ liệu chưa có.
- **Lưu lịch sử thay đổi số liệu view.** Không có nó thì không phát hiện được ghi đè dữ liệu trễ — case phổ biến nhất trong toàn bộ tài liệu. Nằm ngoài phạm vi vì là thay đổi lược đồ và ghi dữ liệu, không phải job đọc.
- **Trường ghi nhận thời điểm hết budget.** Thiếu nó là nguyên nhân của điểm mù đã nêu trong module loại trừ.
- **Tự động sửa lỗi.** Không sinh thưởng bù, không chạy lại tính thưởng, không đổi trạng thái content. Hệ thống chỉ báo cáo.
- **Giao diện quản trị xem lịch sử cảnh báo.** Collection trạng thái có dữ liệu, nhưng không dựng màn hình đọc trong phạm vi này.
- **Cảnh báo qua Telegram hoặc webhook.** Đã cân nhắc Telegram và bỏ; chỉ email.
- **Cảnh báo tức thời.** Job chạy theo lịch hằng ngày, không phát hiện realtime.
- **Thiết kế giao diện email.** Repo cung cấp file HTML mẫu; nội dung hiển thị cuối do team AccessTrade dựng và lưu giữ.
- **Kiểm soát thời điểm template được setup bên AccessTrade.**
- **Alert cho toàn bộ nhóm D, nhóm F và các case E1/E2/E5/E6.** Đây là hành vi đúng thiết kế hoặc lỗi đọc số; alert cho chúng chỉ tạo nhiễu. Giải pháp đúng là audit log thay đổi setup và bổ sung cột "view được tính thưởng" vào file export — cả hai nằm ngoài phạm vi.

## Further Notes

### Rủi ro 1 — Ngưỡng khởi đầu chưa được kiểm chứng bằng dữ liệu thật

**Đây là rủi ro lớn nhất của toàn bộ tính năng.** Năm ngưỡng trong bảng trên được suy ra từ tài liệu case, **chưa đối chiếu với phân bố dữ liệu thật một lần nào**.

Nguy cơ cụ thể: `view_duplicated` với bội số 1.8 có thể bắn vào mọi content vừa lên xu hướng — tăng gấp đôi view trong một ngày là chuyện bình thường với content đang viral, không phải đếm trùng. Tương tự, `vendor_outage` với ngưỡng 50 content / 10 user có thể bắn vào những khoảng thấp điểm bình thường của nền tảng.

Bắt buộc: lần quét đầu tiên chạy ở **chế độ chỉ ghi log**, không gửi email. Đối chiếu số lượng phát hiện của từng alert với thực tế, hiệu chỉnh ngưỡng, rồi mới bật gửi. Bỏ qua bước này gần như chắc chắn dẫn tới việc Ops tắt cả job trong tuần đầu.

### Rủi ro 2 — Điểm mù về thời điểm hết budget

Module loại trừ chỉ biết trạng thái budget **tại lúc quét**, không biết nó cạn từ ngày nào. Hệ quả đã phân tích ở trên: một bug thật xảy ra khi budget còn, rồi budget cạn sau đó, sẽ bị loại trừ sai và **không bao giờ được báo**.

Đây là bỏ sót, không phải báo động giả — nghĩa là nó im lặng, khó phát hiện hơn nhiều. Không có cách khắc phục trong phạm vi này; chỉ giải quyết được bằng cách bổ sung trường thời điểm hết budget.

### Rủi ro 3 — Mã template chưa được AccessTrade cấp

Giống hệt tình huống đã gặp ở cảnh báo đối soát, và **tình huống đó tới nay vẫn chưa được giải quyết** — mã template của cảnh báo đối soát cũng chưa có.

Nghĩa là: nếu triển khai job này trước khi việc bàn giao template hoàn tất, sẽ có **hai** tính năng cảnh báo cùng nằm chờ cùng một thứ. Nên gộp việc bàn giao: gửi cả hai file HTML mẫu trong một lần, nhận cả hai mã template.

Cho tới lúc đó, cảnh báo chỉ tồn tại dưới dạng log — chấp nhận được cho giai đoạn hiệu chỉnh ngưỡng, vì giai đoạn đó vốn dĩ chỉ cần log.

### Rủi ro 4 — Tải lên database

Bảy alert quét toàn bộ dữ liệu view và thưởng của các campaign đang hoạt động. Đây là khối lượng đọc lớn hơn hẳn mọi job hiện có.

Giảm thiểu: quét theo lô có giới hạn, chạy vào khung giờ thấp điểm, có khoá chống chạy chồng. Nhưng **chưa ước lượng được chi phí thật** cho tới khi chạy trên dữ liệu production. Cần theo dõi thời gian chạy và tải database ở lần quét đầu; nếu quá nặng thì phương án đầu tiên là giảm phạm vi ngày quét, không phải giảm số alert.

### Ghi chú — quan hệ với cảnh báo kỳ đối soát

Hai cơ chế **bổ sung cho nhau, không thay thế nhau**:

- Cảnh báo kỳ đối soát là lưới an toàn cho **khâu chi tiền**, chạy tại thời điểm chi, bắt biến động giữa lúc chốt và lúc chi.
- Job này là giám sát **chất lượng dữ liệu đầu vào**, chạy theo lịch, bắt sai lệch trước khi nó đi vào kỳ đối soát.

Một sự cố nghiêm trọng có thể kích hoạt cả hai, và đó là hành vi mong muốn — hai góc nhìn khác nhau về cùng một vấn đề. Không gộp chung email vì hai loại có người đọc khác nhau và mức khẩn khác nhau.

### Ghi chú — đường mở rộng sang vòng 1 và vòng 3

Kiến trúc được thiết kế để thêm alert là thêm một phần tử vào danh sách hàm phát hiện. Cụ thể:

- **Vòng 1** (đứt chuỗi lũy kế, cờ không tìm thấy chạm ngưỡng, token hết hạn, miss ngày) đều là hàm thuần trên dữ liệu đã có, cắm thẳng vào được, không cần thay đổi gì khác.
- **Vòng 3** cần thay đổi lược đồ trước, nhưng phần phát hiện vẫn cắm vào cùng chỗ.

Nếu sau này quyết định làm vòng 1, chi phí gần như chỉ còn là viết hàm phát hiện và test — toàn bộ hạ tầng quét, gom, chống lặp, gửi đã có.
