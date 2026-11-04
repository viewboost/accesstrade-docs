Speaker 1: Bên nào đi hiền ơi? 

Speaker 2:  Ừ, dạ rồi. Rồi vào đổ rồi thì em trình bày cái. 

Speaker 2:  Tổng đài của Reso ạ. 

Speaker 2:  Dạ rồi, tổng đài thì mình sẽ có một cái hạng mục cần nghiệm thu và release là cái chức năng hiển thị thông tin tiền thưởng trên trang FA riêng. 

Speaker 2:  Thì cái này là yêu cầu từng trong tháng 10 của Bank Business, là cần một các trang FA riêng của ADV, cần có một cái chỗ để mà theo dõi được số view. Cái thu nhập tiền thưởng trên trang cá nhân mà không cần phải quay về trang Bank Ambassador để mà xem. 

Speaker 2:  Thì cái tab này team cũng đã làm xong đầu test rồi, và đang chờ gửi hướng nghiệm thu. 

Speaker 2:  Dạ rồi, trong tuần này thì bên team có nhận được một yêu cầu từ phía chị Vui là cái thêm module mà MCN vào nền tảng cho xe Ambassador. Thì cái này chút anh Vĩnh sẽ resend. Thì phần này em đi nhanh qua chiếu xíu để back lại phần này cho anh Vĩnh được resend để mà chị Vui và mọi người cùng xem, và duyệt thống nhất cái scope để đưa vào plan tháng 11. 

Speaker 2:  Và cái tab thứ ba mà team sẽ dự định đưa vào plan trong tuần này đó là cái việc update phân quyền hệ thống Bank Ambassador, thì nâng cấp lại tới B1 của mình. Mình làm thêm thì hiện tại tới B1 của mình lên á, thì đang có mình đang còn thiếu cái phần mà phân quyền role admin. 

Speaker 2:  Thì nó đang gộp lại là vừa quản trị hệ thống vận hành và phụ trách ADV. Thì cái này đợt này mình sẽ nâng cấp lại cái chỗ admin một chút, làm rõ cái vai trò admin. Thì cái version này sẽ lên là mình sẽ khóa đăng nhập group luôn, không cho đăng nhập group nữa. 

Speaker 2:  Group chỉ là group hệ thống và không cho phép đăng nhập. Còn cái thứ hai là mình sẽ tách hẳn ba vai trò ra, là admin hệ thống, quản lý vận hành và quản lý ADV. Và ừm, rồi và cái thứ ba nữa là mình sẽ hạn chế cái việc nâng quyền, không cho phép là người dùng hệ thống quyền dùng chung toàn hệ thống, chỉ có tác dụng với mẫu ADV nhất định thôi. 

Speaker 2:  Dạ rồi, thì cái phần update các phân quyền Nhi sẽ làm dự kiến, team sẽ làm thêm trong phân tích và làm tiếp trong tuần này. 

Speaker 1:  Update phân quyền này em giải quyết bài toán gì của ai? 

Speaker 2:  Là hiện tại cái phần là giải quyết cái của cái phần mà chị Phượng nghiệm thu và có phản hồi á chị, tức là hiện tại. 

Speaker 1:  Cái phần của Phượng thì bọn em tiếp cận theo hướng khác đi, bọn em làm luôn cái phần quản lý permission cho chị đi, để admin hệ thống tự làm cái việc phân quyền rồi phân permission rồi add được các cái phần permission cho từng role. 

Speaker 2:  Dạ. 

Speaker 1:  Đừng làm theo cái kiểu mà ad hoc như bây giờ nữa. 

Speaker 3:  Cái này là anh đã phân tích lại cái ấy rồi, với hiện với hiện mô tả nó sai cái tab rồi. 

Speaker 3:  Tức là. 

Speaker 3:  Cái cái góc á là bên Phượng nó không hiểu được là bây giờ á là mấy cái role mà đang có trên hệ thống á, là nó đang migrate nó thành những cái vai gì. 

Speaker 3:  Đó, thứ nhất là cái đó. Thì cái đó là anh lên một cái bộ quyền. Thì cái bộ này á là anh mô tả lại kỹ, sau đó là anh đề xuất ra đúng ba cái bộ, ba cái role mình sẽ tạo bằng giao diện, chứ mình không có làm gì về code trơn á. 

Speaker 3:  Mình tạo bằng giao diện, thì xong cái giao diện đó thì mấy cái vai cũ á mình sẽ mình sẽ sửa dần qua. Đó, ông nào là admin ADV, ông nào là admin của hệ thống, ông nào là quản lý vận hành, ông nào vận hành, đó thì mình sẽ tạo crowd về permission hết, chứ không có có migrate gì ở đây trơn á. 

Speaker 3:  Rồi thì cái update thứ hai á, là để làm rõ vô cái chỗ mà cái route là gì mà cái admin là gì. Rồi cái route á thì bây giờ là cái route nó chỉ là cái phần mà hệ thống sử dụng thôi. Đó, hệ thống sử dụng, ví dụ nó chạy audit, nó viết lại audit log, nó viết là hệ thống tự duyệt hay là hệ thống tự tự gắn tag, hệ thống tự cảnh báo hủy. 

Speaker 3:  Đó là là vai trò của route, và cái route mình sẽ chặn lại, không cho đăng nhập. Còn cái cái route mới á là nó sẽ là vai admin. Thì cái chỗ vai admin nó chỉ sửa hai cái thôi. 

Speaker 3:  Thứ nhất á là là admin được gán được được được được gán vai trò vào một admin khác. Hồi xưa hôm bữa là lần trước là mình chặn là hỏi hệ thống chỉ có một admin thôi. Đó, bây giờ là cho phép luôn tạo ra có admin khác cho nó phù hợp. 

Speaker 3:  Rồi thứ hai là bổ sung thêm quyền cho admin cho nó full. Đấy, cái bộ code cũ đang thiếu một số cái bộ quyền. Thì mấy cái quyền này á lúc đầu là là chỉ có route được sử dụng, nhưng bây giờ anh đổi lại luôn là bây giờ là cái admin là nó có thao tác trên cái giao diện là admin phải làm được luôn. 

Speaker 3:  Không có cần phải chờ route nữa. Đó, cái bộ tab nó chỉ xử lý theo cái việc đó thôi. 

Speaker 3:  Được chưa? Còn cái chỗ mà Phượng nó bây giờ đã thao tác được rồi, không vấn đề gì. Đó, bây giờ lên được cái bộ role sang cái ngồi với Phượng là Phượng tạo ra các cái bộ role mới, theo permission mới, đặt sai vô, xong. 

Speaker 3:  Nha. 

Speaker 2:  Thế hiện tại mình đang ngồi thống kê lại được cái danh sách đấy với Phượng vàái danh sách user hiện tại chưa? 

Speaker 3:  Dạ đúng rồi. Thì cái đó là cái mà cần team sẽ ngồi làm đó. Thì chỉ cần làm việc với lại Phượng là là là là lên cái danh sách hiện tại này, là vai của họ là ở trong trước, trước hôm thì lên là cái gì, đây vai bây giờ nó sẽ lên là cái gì, là sai quyền qua, là xong. 

Speaker 3:  Nha. đó. 

Speaker 3:  Tab này không có cần có làm gì nhiều hết, nhưng mà nó vẫn cần một cái pull request để phân cái vụ route thôi. 

Speaker 2:  Rồi ok ạ. 

Speaker 3:  Rồi. 

Speaker 2:  Chắc mình đi luôn vào cái phần của anh Vĩnh đi, hoặc là team đầu vận hành thì đang có cái thông tin gì thìi. 

Speaker 2:  Ok, chắc mọi người không có thông tin gì đâu, nó sẽ xử lý hết qua tab request nên chắc anh Vĩnh đi tiếp đi anh. 

Speaker 3:  Ok. 

Speaker 3:  Huyền tắt xe em xem này. 

Speaker 3:  Ok. 

Speaker 3:  Rồi. 

Speaker 3:  Thì cái phần MCA này á thì lúc đầu anh cũng bị ngờ ngờ, nhưng mà đọc kỹ thì nó cũng cũng hiểu đượcái anh hiểu trước. 

Speaker 3:  Thì tức là MCA nó sẽ là một đối tượng mới của hệ thống này luôn. Nó tham gia ở vai trò là ở cái đầu end user, tức là ở đầu cái đầu portal của trong work creator luôn. Nhưng mà nó có cái bộ quyền riêng, nó là một cái loại riêng cho nên nó có cái nó có các cái chức năng nó nó khác biệt. 

Speaker 3:  Nha, anh hiểu sơ là như vậy. Ờm, anh đi theo các cái UK mà vui vẻ trong cái sơ đồ luồng á thì anh đã nhận là hết các cái action nó lên giao diện rồi. Anh nói anh sẽ đi từng bước một. 

Speaker 3:  Có một số chỗ anh anh chưa clear lắm thì anh sẽ đó anh sẽ hỏi. Đấy, rồi thì đầu tiên anh đi vào từng luồng luôn nè. Đầu tiên là cái luồng admin. 

Speaker 3:  Nha, thì admin thì nó đang đây là cái giao diện của bên admin, anh đang dựng lại nè. Thì bên admin này á là nó có hai chức năng chính. Thứ nhất là nó là quản lý cái phần MCN. 

Speaker 3:  Rồi anh cũng chưa biết là nay đã có đã có đổi tên cái cái đối tượng không, em vẫn giữ cái MCN trước. Rồi để tạo MCN á thì đơn giản là vô tạo có một số thông tin thôi. Đấy, một số thông tin cơ bản thôi. 

Speaker 3:  Đó, cần cái email đăng nhập đầu tiên. 

Speaker 3:  Thì một MCN mà để được kích hoạt lên á là nó phải có đầy đủ các cái thông tin như thế này. Đó, các thông tin này nó phải đủ hết. Thì bây giờ là bên admin nó phải upload đầy đủ cái đống này lên. 

Speaker 3:  Thì cái này là các cái file PDF ký thôi, toàn bộ và ký số. 

Speaker 3:  Đấy, rồi còn riêng cái tài khoản ngân hàng á thì chọn cái ngân hàng rồi sau đó nó nhập số tài khoản thôi. Có nếu như mình có API để kiểm tra á thì sẽ tích hợp API đó vào kiểm tra. Nếu như mà cái tên cái tên pháp nhân mà nó khớp á thì mình sẽ cho lưu. 

Speaker 3:  Rồi ở đây là tất cả điều kiện nó đều đạt hết nè. Mình có thể xem lại hệ khách. 

Speaker 3:  Đấy, bấm vào mình xem ngày tại đây, file nó là file gì, lịch sử như thế nào. Đã sửa cái gì. Đấy, muốn cập nhật thì cập nhật lại. 

Speaker 3:  Nha, cập nhật file mới. Nó sẽ đặt cái lịch sử.ủ hết rồi thì mới kích hoạt được. 

Speaker 3:  Đó, kích hoạt ra. Kích hoạt cái trong quá trình kích hoạt nó sẽ gửi cái email cái email kích hoạt về để mà tạo cái tài khoản cho MCN để đăng nhập được. 

Speaker 3:  Nó gửi một cái email mời ra đó. Rồi thì cái hồ sơ cũ mình sẽ xem lại ở đây. À, quản lý MCN thì nó có cái thành viên, tức là KYC, KOL. 

Speaker 3:  À, cái bản K đối soát đó, cái này xíu nữa anh anh quay lại. Rồi thì xong được cái ông admin ổng tạo được rồi á thì cái ông MCN ổng sẽ dùng hệ thống như thế nào. Thì á, ông MCN thì ổng vẫn dùng cái cái cái cái portal của mình hiện tại thôi. 

Speaker 3:  Cái ambassador.kyc.co.vn á thì trong này với ổng á là ổng sẽ có một cái trang quản lý MCN. Nếu như ổng là vai MCN quản lý. Được chưa? 

Speaker 3:  Thì trong này ổng có chức năng gì? Thứ nhất là ổng quản lý thành viên của ổng. Thành viên của ổng bằng cách là ổng mời KYC. Rồi cái chỗ mời này thì anh đang hơi anh đang hơi confuse chút, nhưng mà anh anh anh đang dựng lại cái vẫn y cái mô tả đó. 

Speaker 3:  Thì ở đây anh đang không rõ là cái mời này nó vì sao lạiYC của mình á, Vui. 

Speaker 2:  Ờ, chỗ này mình sẽ check lại nhá, sẽ không cho từ một ông MCN sẽ đi vào cái kho của nhà mình đâu. Nó chỉ có từ admin thì mới đi được vào cái kho nhà mình thôi anh ạ. 

Speaker 3:  À rồi, tức là ông tức thì bây giờ ông ông này ổng mời là ổng mời bằng cái gì? 

Speaker 2:  Ờ, ví dụ như cái phần KYC của nhà mình public ra bên ngoài nó đang có cái phần hashtag hay cái gì đấy thì mình sẽ dùng một cái key kiểu như thế để invite anh ạ. 

Speaker 3:  Là ổng dùng nhưng mà như vậy mà ổng sẽ tra cứu được gì? Nó nó sẽ tra cứu tức là cái việc mời này bây giờ là hiện tại chốt là MCN có được mời không hay là ông admin phải làm? 

Speaker 2:  Theo em thì MCN được mời. 

Speaker 3:  MCN được mời. 

Speaker 2:  Tuy nhiên thì họ ví dụ như đầu Shopee họ cũng làm như thế thôi. Họ sẽ có một cái là để cho bản thân là cái có một cái link giới thiệu để cho cái ông MCN này ông ấy hoàn toàn đưa cái link đấy cho các cái bạn KOL KYC để bạn ấy join vào. 

Speaker 2:  Hai là bạn ấy sẽ dùng một cái ID ở trên hệ thống. Ví dụ như thằng Shopee thì nó sẽ là có cái Shopee affiliate ID. Thì tương tự như của mình thì mình cũng đang có cái ID của cái user trên hệ thống ambassador này. 

Speaker 2:  Thì nó đang được thể hiện bằng cái hashtag hoặc cái gì đấy. Tuy nhiên thì cái này là mình quy định lại nhá, để cái gì đấy mà mọi người đều biết được đấy là cái định nghĩa của ở đấy đấy là định nghĩa của một bạn user ấy. 

Speaker 2:  Để người ta có thể gửi được lời mời ấy. 

Speaker 3:  Ok. Nhưng mà như vậy thì nó nó nó sẽ mang tính tra cứu được. 

Speaker 2:  Ờ, mình sẽ không cho cái hoạt động tra cứu. Tức là người ta sẽ gửi lời mời theo ấy thôi anh ạ. Theo cái hashtag hay cái gì đấy thôi. 

Speaker 3:  Ok. 

Speaker 3:  Đây thì bây giờ cái này cập nhật thì sẽ có hai cái. Đầu tiên là nhớ mở cái cái cái cái mic note ngay. Có đang mở nha. 

Speaker 3:  Rồi rồi. Tức là. 

Speaker 2:  Thì bản chất là khi mà ông ấy đã mời thì là ông ấy đã biết cái bạn KYC đấy là ai rồi, chứ không phải là ông ấy chưa biết. Chỗ này đúng không hả? 

Speaker 2:  Khi để cho một MCN mà mời một bạn KYC trên hệ thống ambassador là ông ấy đã biết được cái bạn ambassador, cái bạn đấy ở trên ambassador là ai rồi, đúng không? 

Speaker 3:  Dạ đúng rồi anh chị. 

Speaker 3:  Là điêu ở ngoài rồi, chỉ có người ta đưa lên hệ thống nữa thôi. 

Speaker 2:  Ừ đúng rồi. 

Speaker 3:  Rồi. 

Speaker 3:  Ở đây ví dụ anh nhập cái mã này ha. Rồi anh sẽ nhập cho họ là cái tỷ lệ mà phần trăm mà anh anh suggest. Ví dụ băng mặc định nó sẽ 15%. 

Speaker 3:  Nhưng mà anh có thể sửa lại. Rồi gửi lời mời đây. Đấy. 

Speaker 3:  Thì cái ông đó ông sẽ được vào trong cái danh sách lời mời của anh để chờ. 

Speaker 3:  Đấy, chờ phản hồi. Thì bây giờ là cái vai ông KYC ông sẽ thấy gì? Ông vai KYC sẽ đăng nhập vào á là ông sẽ có cái menu là MCN của tôi nè. 

Speaker 3:  Được chưa? Khác biệt với lại cái chỗ cái chỗ quản lý MCN thì ông này ông chỉ có một cái menu tên là MCN của tôi thôi. Vào đây ông sẽ nhận được cái lời mời hoặc là cái chung nãy ông sẽ có cái mời. 

Speaker 3:  Cái thông báo sẽ có cái mời. Thì vào đây ông sẽ xem được thông tin mời. Đó là cái MCN nào mời nè. 

Speaker 3:  Đó, tỷ lệ là bao nhiêu nè. Thời gian là bao lâu nè. Đó, cái này là cái ví dụ. 

Speaker 3:  Ghi rõ luôn ví dụ theo cái phần trăm luôn. 

Speaker 3:  Đấy, rồi đồng ý. 

Speaker 3:  Đồng ý thì thì nó sẽì cần phải ký một cái phụ lục. 

Speaker 3:  Phải không? Ký một cái cái hợp đồng với phụ lục gì đó. 

Speaker 3:  Thì à khi ký hợp đồng này á thì nó sẽ đồng ý hả quay thì nó sẽ mở ra cái trang ký của Fưng anh đã không demo lại. 

Speaker 3:  Đấy. Rồi ký xong á thì nó sẽ vào cái chỗ này là có trạng thái đang hợp tác. Thì lúc hợp tác á mà cảm thấy không ổn thì có thể là báo rời. 

Speaker 3:  Được chưa? Giải pháp. 

Speaker 3:  Mình có thể báo rời. Đấy, báo rời thì đang báo báo rời xong á thì à nó sẽ kích hoạt sau bao lâu này. Đó, rồi có thể rút lại cái lời mời đó. 

Speaker 3:  Nó nó rút lại cái cái cái cái cái rời đó. 

Speaker 3:  Rồi qua bên ông kia. 

Speaker 3:  Rồi qua ông này. 

Speaker 3:  Đây, qua ông này thì có một cái ông đang báo rời. Rời đây sẽ có cái hiệu lực hoặc là ông này ông sẽ chủ động chấm dứt luôn. Được chưa? 

Speaker 3:  Chấm dứt luôn thì không không cần phải chờ nữa. 

Speaker 3:  Đó, hoặc là ông đang hoạt động cũng có thể chấm dứt được. 

Speaker 3:  Đấy, thì bên bên cái ông ACN thì quyền nó cao hơn. Ổng không có chờ, không có xin phép gì hết. Còn cái ông KYC ổng muốn rời đi để ổng xin phép. 

Speaker 3:  Rồi đó là luồng mời thành viên và nhảy vào tham gia vào MCN của KYC KOL. Thì khi mà tham gia vào rồi á là ông admin cũng sẽ thấy gì? 

Speaker 3:  Ông admin cũng sẽ thấy được là một ông như vậy ổng sẽ có những KYC KOL nào có trạng thái thế nào. Cái vụ mà đang báo rời nó cũng sẽ hiển thị đây luôn. Nhưng mà admin này không không không thao tác gì cả. 

Speaker 3:  Admin chỉ thấy thôi. 

Speaker 3:  Đấy, thì cái chỗ này anh cũng cần xác nhận lại á là cái cái những cái ông operation của nhà mình á là ổng có cần làm hộ MCN không? 

Speaker 3:  Đấy, mình mình hà xem giúp anh thử. Cái cái phần này em tưởng là admin có thể làm được luôn chứ anh. 

Speaker 2:  Thì em nghĩ là admin ổng sẽ nắm quyền cao nhất. 

Speaker 3:  Rồi tức là admin được thao tác giúp luôn đúng không? 

Speaker 2:  Dạ đúng rồi. 

Speaker 3:  Rồi thì bây giờ là nếu như admin thao tác nó bị một cái là ví dụ như những cái vụ mà chấm dứt hay là hay là rời khỏi nó đó là nó rất là nghiêm trọng á nha. Mình phải xác định đúng là cho phép thì thì thì thì thì sẽ sẽ làm. 

Speaker 2:  Chúng mình vẫn là đầu kiểm soát là em thấy ok. 

Speaker 3:  Rồi ok. 

Speaker 3:  Thế thì cái phần lời mời lúc nãy á là admin nó có nó có nó có thêm luôn thẳng không hay nó nó không cần phải nó không cần phải mời nha. Tức là lúc nãy là là thằng MCN thì nó phải mời. Thằng KYC nó phải chấp nhận nó mới vào. 

Speaker 3:  Còn admin bây giờ có có cần cái luồng là admin mình thêm thêm thành viên vào luôn không? 

Speaker 3:  Tức là thêm là xong luôn á. Không có hỏi luôn á. 

Speaker 2:  Ừ. 

Speaker 3:  Đấy, thì cái cái cái admin thì nó nếu như vai trò đúng á thì nó sẽ có cái luồng đó nữa. Nhưng mà anh không biết là cái đó có approve được không. Và cái cái luồng mà vui vẻ trên cái sơ đồ thì không có cái đó. 

Speaker 3:  Những cái luồng mà mà admin thì không có nha. 

Speaker 3:  Trên cái sơ đồ đây có file PDF á. 

Speaker 2:  Ủa cái luồng hiện tại chỉ vui vẻ là đang admin đang ở cái chế độ là view thôi hả chị? 

Speaker 1:  Đúng rồi. Có phải cái việc gì thì admin nó cũng sẽ được làm đâu. 

Speaker 2:  Ừ, ok ok. Vậy thì nếu vậy cũng được. Tại em cũng sợ. 

Speaker 1:  Và mình cái này thì bọn em cứ check lại theo cái việc mà hoạt động thực tế. Còn khi mà em đã giao quyền cho ông MCN rồi thì tốt nhất để cho ông ấy tự quản lý được cái việc mà KYC của ông ấy. Còn bọn em thì mang tính chất hỗ trợ thôi. 

Speaker 1:  Ví dụ như cái công cụ đấy nó sẽ có thể có nhưng mà nó chỉ là mang đem theo hoạt động hỗ trợ của em thôi. Vì sau này nó sẽ liên quan đến tiền rất là nhạy cảm. 

Speaker 2:  Ừ. Dạ ok ok ok. Em hiểu rồi. 

Speaker 3:  Rồi xong full cái luồng mà quản lý thành viên nha. 

Speaker 3:  Đó, ba vai. 

Speaker 3:  Nó sẽ như vậy. Rồi cái bây giờ cái chính là cái cái quy chế này. 

Speaker 3:  Cái quy chế này thì nó hơi rối. Nó là anh đọc anh cũng chưa hiểu. Và cái cái tài liệu phân tích của mọi người cũng cũng đang ghi là đang chờ thống nhất gì đó. 

Speaker 3:  Thì anh hiểu á là bây giờ mình sẽ có một cái phiên bản. Những phiên bản quy chế và phiên bản quy chế này nó sẽ nó sẽ áp dụng với tất cả các MCN luôn. Thì mỗi quy chế nó sẽ có hai cái tài liệu. 

Speaker 3:  Thứ nhất là tài liệu là quy chế chương trình. Thứ hai là quy tắc ứng xử. Đó, nó sẽ áp dụng với tất cả các ông MCN trên hệ thống luôn. 

Speaker 3:  Và mỗi lần mình phát hành phiên bản á mình công bố phiên bản mới á là mình sẽ upload hai cái hai cái thông tin này. là mình sẽ chờ mấy ông này ổng ký. 

Speaker 3:  Đó, chờ mấy ông này ổng ký. Thì mỗi ông mỗi ông mình phải gửi qua cho mỗi ông để mấy ông ổng ký. Ký á thì sẽ upload lên. 

Speaker 3:  Ký thì vẫn vẫn phải lên upload chứ ký hiện tại là không có cái ký trực tiếp trên hệ thống mà ký là phải đi upload. Upload thì nó sẽ upload lên đây nè. Anh thấy không? 

Speaker 3:  Chờ MCN xác nhận 2.0 thấy không? Đó, khi các bạn 2.0 ra là ông này bên đây em ký. Ký thì upload cập nhật vào. 

Speaker 3:  Đó, phiên bản 2.0 cập nhật phiên bản 2.0 vào. 

Speaker 3:  Đây, đó thì nó ra cái file hiện thành. Nó sẽ ra cái file của 2.0 này. 

Speaker 3:  Được chưa? Thì anh anh hiểu cái như vậy có đúng không? 

Speaker 3:  Cái cái cái luồng cái luồng mà mà quy tắc ứng xử này nè. 

Speaker 3:  Rồi xong khi sau khi quy tắc ứng xử này nó nó nó đồng ý xong á là ở trong cái tài liệu có một cái phần nói là nó sẽ chặn mời. Nó chặn lại là không phép khôngổng mời. Nếu như ổng chưa ký. 

Speaker 3:  Đó, tức là nếu như ổng chưa cập nhật là ổng chưa đồng ý với quy tắc ứng xử mới á là ổng sẽ không được mời luôn. 

Speaker 3:  Trong cáiệu của vui đời đang đề xuất như vậy. Đề xuất thôi chứ cũng chưa có chốt nữa. 

Speaker 1:  Chỗ này thì các cái hạng mục liên quan đến legal thì Hà final note đi. Một là liên quan đến cái việc mà bọn em ký với cả MCN thì bọn em đăng ký trên hệ thống hay là bọn em sẽ để ký ở bên ngoài trước để chạy trước. 

Speaker 1:  Hoặc là mình có thể chia scope ra anh Vĩnh ạ. 

Speaker 3:  Ờ. 

Speaker 1:  Mình hoàn toàn có thể chia scope ra để chạy á. 

Speaker 3:  Rồi nhưng mà nó có chặn cái cái hoạt động mời KYC không? 

Speaker 1:  Với các bạn mà đang chưa ký hợp đồng thì tốt nhất là mình đang chưa có làm gì liên quan đến cho mời KYC cả. Bắt buộc là phải sau khi mà admin họ phải được duyệt họ duyệt trên hệ thống thì mới bắt đầu cho vào. 

Speaker 1:  Và có các hồ sơ pháp lý thì mới cho vào để chạy được anh ạ. 

Speaker 3:  Ok. Rồi thì cái version 1 nó sẽ hơi mình sẽ chặn kỹ một chút. Sau này đấy. 

Speaker 3:  Là mỗi lần mà cập nhật cái phiên bản này nè, cái phiên bản này nó sẽ nó sẽ ảnh ảnh hưởng tới rất là nhiều MCN luôn. Ví dụ như bây giờ mình có 20 MCN đúng không? Mà nó nó nó phải chờ 20 ông này phải ký hết nè. 

Speaker 3:  Thì thì thì 20 ông này là lần lượt là ngâm một nó đi mời được. Đó một cái một cái phiên bản này nó áp dụng với tất cả MCN chứ không phải là là từng từng MCN đúng không? Đó là cái đó là cái chính á. 

Speaker 3:  Rồi công bố phiên bản 3. 

Speaker 3:  Bố phiên bản 3 thì nó lên version 3 đây. Đó anh này anh chưa xác nhận. 

Speaker 3:  Thì bây giờ anh phải vào trong cái danh sách MCN này coi cái chỗ này. 

Speaker 3:  Đó ổng thấy nó chưa xác nhận ổng phải vô xác nhận coi không là có cái này ổng không được mời để qua cái cái có lại được cái gì đó không ta. 

Speaker 3:  Đây đó đây đã công bố quy chế mới nè. Đó bạn phải xác nhận trước khi mời chứ không là bây giờ là không cho mời nữa nha. Chặn luôn. 

Speaker 3:  Xem và xác nhận. 

Speaker 3:  À có cái này có cái online này. 

Speaker 3:  Đấy rồi anh anh dẫn luôn cái online lên lên rồi đó. 

Speaker 3:  Nhưng mà cái luồng đó thì thì chưa biết nó nó mở ký như thế nào. 

Speaker 3:  Rồi qua lạiái quy chế rồi tới cái phần mà tiền. 

Speaker 3:  Đó bây giờ tới tiền này. 

Speaker 3:  Tiền á là mỗi lần mà đối soát á. 

Speaker 3:  Bây giờ mỗi lần mà đối soát á đây thì trong cái đối soát này á là sẽ có cái phần à mỗi người nhận á có cái phần danh sách người nhận. Đó mình duyệt đối soát rồi là mỗi người sẽ nhận được bao nhiêu tiền đó. Thì nếu như ông đó mà có MCN á là ổng phải có cái phí quản lý. 

Speaker 3:  Đó ổng có cái phí quản lý rồi ổng sẽ tự phí quản lý ra làm cái giấy thực nhận và ổng giảm xuống. 

Speaker 3:  Đấy là gửi tạo ra một kỳ đối soát á là nó sẽ có những dòng như thế thì mình sẽ có rất là nhiều trạng thái đối soát đúng không? Đây ví dụ trạng thái đang chờ chờ cái ông KYC xác nhận nè. Ông này ổng chưa xác nhận nè. 

Speaker 3:  Đó ông này ổng báo sai nè. Ông này xác nhận rồi nè. Đó thì nó có một cái là. 

Speaker 1:  MS. 

Speaker 3:  Sau một khoảng thời gian ví dụ mình để cái đó 5 ngày mình sẽ cho 5 ngày. 5 ngày á mà ông ông không xác nhận nó sẽ tự xác nhận luôn. Đó nó vô đây nè. 

Speaker 3:  Nó tự chạy. 

Speaker 3:  Đó. 

Speaker 1:  Còn không thì. 

Speaker 3:  Thì ở đây á là cái này nó xác nhận thì nó sẽ cái chỗ người nhận này sẽ thêm một cái dòng là ông ông MCN này ổng sẽ được nhận cái phần của ổng nữa. Đó trong cái phần mà biên bản này sẽ luôn có thêm nó luôn. 

Speaker 3:  Thì anh em có thể filter filter. 

Speaker 1:  Filter xác nhận kia là khi nào nó lên cái chờ xác nhận là khi cái bạn KYC đấy chưa join vào MCN hay như thế nào? 

Speaker 3:  Ờ trong cái luồng vẽ ra là yêu cầu là ông KYC ổng phải xác nhận là trong cái kỳ đối soát này ổ thì nó mới tính là đối soát xong. Rồi để em qua cái màn hình KYC này. 

Speaker 3:  Màn hình KYCN của tao này sẽ có cái phần cái này. 

Speaker 3:  Để họ thông xong thì họ mới config thì phần đối soát này. 

Speaker 3:  Mọi mỗi ông KYC này á ổng sẽ vô trong cái chỗ đối soát này ổng coi đây ổng vô ổng coi đúng không? 

Speaker 3:  Vô đây ổng vô kỳ đối soát và ổng xem ổng xem rồi ổng thấy là ổng có thể bấm cái nút báo sai. 

Speaker 3:  Rồi cái giao diện nó mất cái nút báo sai nè. 

Speaker 3:  Rồi ở trong nói chung là ổng có một cái một cái một cái bảng kia nói chung nó giống như giống như là cái biên bản đối soát á giống như là cái cái sau kia á. Đó cái sau kia là cái bay slip á gửi qua cho ổng. 

Speaker 3:  Ổng ở đây là sẽ có cái trạng thái là ổng có một cái nút báo sai được nè. Một cái nút báo sai đi đâu trời. 

Speaker 1:  Ví dụ ở cái cái màn mà đối soát bình thường mà các cái bạn KYC bạn ấy đang thấy bình thường ấy thì nó sẽ đang như thế nào anh? Đây đúng không? Nó sẽ là màn này đây đúng không? 

Speaker 3:  Hiện tại là nó hiện tại là cái hệ thống mình đang rất là tệ chỗ này nè. Nó nó đang không có cái thông tin đối soát cho KYC coi. 

Speaker 1:  À hiện tại là không có luôn ạ. 

Speaker 3:  Đúng rồi. Đấy thì bây giờ muốn làm cái đó là phải đưa cái này về. 

Speaker 1:  Rồi xong này vào rồi bây giờ mới thấy được thấy xong á thì chỗ này là có kiện cáo gì đó. Nói chung là kiện đại khái là chỗ này có một cái nút kiện hay xử lý gì đó thì bên ông admin á là ổng sẽ vào ở trong đối soát ổng sẽ thấy ổng thấy rõ là là là có một cái một cái luồng m này đó một cái ông KYC báo sai ông này ổng báo là thiếu hoa hồng của tôi nè ông này thì bảo là thế này ông này bảo thế này được chưa thì nó sẽ có cái nút xử lý rồi cái xử lý thì mới mới mới mới mới mệt nè tức là báo sai này xử lý thế nào thì rất là khó. 

Speaker 1:  Cái đối soát của mình thì anh ta không có nắm được nhiệm vụ rõ lắm. Đó nhưng mà nó báo sai xong nó lẽ nó phải có một cái dòng là cộng trừ hoa hồng gì đó hay chỉnh sửa hoa hồng gì đó thì mới đóng được. 

Speaker 1:  Tức là cái tính năng bonus của mình hiện tại á là nó sẽ phải được bổ sung vào để mà nó xử lý cái đối soát này. Đó nhưng mà hiện tại mình không có. Thì hiện tại anh chỉ có đơn giản là nó có một cái nút là nó sẽ dời qua kỳ sau. 

Speaker 1:  Đó tức là cái ông này ổng sẽ không được đối soát được này. Ổng ổng có kiện cáo mà ổng sẽ dời qua đợt sau để ổng ổng xử. Nhưng mà đợt sau sẽ xử lý thế nào thì chưa chưa có action. 

Speaker 1:  Đấy ví dụ như là qua lại bên này. 

Speaker 2:  Mày feedback nghe nha. 

Speaker 3:  Đây đây ví dụ như chỗ này nè. Xử lý báo sai hoặc là dời qua cái dời qua kỳ sau. 

Speaker 3:  Đó nhưng mà xử lý báo sai này đang xử lý thế nào chưa có. 

Speaker 3:  Đó cái này là hoàn toàn thiếu nè. 

Speaker 1:  Nó hơi phức tạp nhỉ mà cũng không giống với cả cái cách mà mọi người đang vận hành hiện tại nhỉ. Cơ bản là bây giờ đã đang vận hành hết ở bên ngoài rồi xong rồi thực hiện add bonus các kiểu chứ trong cái trường hợp mà còn đợi để xác nhận như thế này thì chắc cũng không biết là bao giờ ông MCN được nhận cái thư cái tiền đấy. 

Speaker 3:  Ừ ở đây có vị canh này anh hỏi vị canh thử là lỡ mà trong lúc đối soát á mà có creator nó kiện á thì tụi anh đang làm ra cái vị canh nó bảo thiếu thiếu thiếu hoa hồng thiếu view của nó thì em đang làm ra. 

Speaker 2:  Cái sắp xếp đó áp thưởng thêm sắp xếp đó kiểm tra xem nếu mà đúng thật chứ còn nếu mà sai thì đương nhiên là mình không áp rồi. 

Speaker 3:  Còn còn dư là để im đó hả? 

Speaker 3:  Dư dư thì chắc đi im quá vậy. Còn thiếu là mới thêm vào quá vậy. 

Speaker 2:  Dư có nghĩa là mình phải có dư cho creator á. 

Speaker 3:  Ừ. 

Speaker 2:  Hay là sao? 

Speaker 3:  Mình mình đối soát cái tổng tiền dữ. 

Speaker 2:  Ừ. 

Speaker 2:  Nhưng mà cái, cái màn này rời lại, lạ quá nhỉ. 

Speaker 2:  Thường thì với cả creator, khi mà các bạn ấy chỉ comp lên ấy, trong trường hợp là thiếu thôi. Còn các bạn ấy chưa bao giờ comp lên, trường hợp mà thường. 

Speaker 1:  Ờ, thiếu thì mình xử bằng cách là mình thêm tiền cho họ đó. Đúng rồi. 

Speaker 2:  Vâng. Nhưng mà thiếu mà rồi xong chỉ sau thì nhìn nó sợ, nó phức tạp ấy. 

Speaker 2:  Tại vì nếu mà mình bảo mình rời xong kỳ sau bằng mồm xong mình áp thêm thưởng dễ hơn xong rồi. 

Speaker 2:  Có nhiều cái phức tạp quá. 

Speaker 1:  Mình, mình chưa bao giờ, mình, mình, mình giờ qua kỳ sau à? 

Speaker 2:  Có. 

Speaker 2:  Nhưng mà với những cái, cái, cái trường hợp rời xong kỳ sau thì áp thưởng tay hệ thống, hoặc là như những conưa thì dùng tay file ngoài 100% cũng không cần dùng hệ thống. 

Speaker 1:  Ờ, điều đó thì cái phần thưởng thêm đó, có nghĩa là bây giờ mình không chốt được mà mình, mình, mình bảo là mình chờ diễn lâu quá đúng không? Bây giờ mình bấm, mình bấm nhanh, ông đó là qua kỳ sau sẽ lấy. Còn cái kỳ đấu sót này tôi, tôi loại ông ra, tôi chốt cho xong đã. 

Speaker 2:  Ừ. 

Speaker 1:  Còn nếu, còn cái nào mà ổng, ổng, ổng lâu á là mình sẽ để kỳ sau, kỳ sau mình sẽ tặng cái đấu sót mới để chỉ có một hai ông bị xử lý sai thôi. 

Speaker 1:  Thì cái cách làm của anh ở bên mấy cái hệ thống đấu sót kia nó như vậy. 

Speaker 2:  Ừ. 

Speaker 1:  Ngày xưa mà anh làm soly hay là anh làm gì bên kia hay là. 

Speaker 1:  Rồi cái này thì anh sẽ, anh sẽ, anh sẽ nghiênơ đồ vui vẻ thì không có. 

Speaker 1:  Chỉ có cái phần xem thôi. 

Speaker 2:  Ừ. 

Speaker 1:  Và có cái báo động. 

Speaker 1:  Rồi, thì báo sai xong á mà xử lý hết rồi á thì mới, mới được approve cái đấu sót. Chốt kỳ, chốt kỳ á thì đi tiền thôi. 

Speaker 1:  Đấy. 

Speaker 1:  Rồi chuyển qua thanh toán. 

Speaker 1:  Đấy. 

Speaker 1:  Rồi chuyển qua thanh toán thì xuất Excel rồi gọi. Tối nay gọi qua cái chi hội cho quen. 

Speaker 1:  Rồi xong. 

Speaker 1:  Tắt, tắt cái mic đi Việt Anh ơi. 

Speaker 1:  Rồi. 

Speaker 1:  Đấy, thì cái đấu sót nó sẽ như vậy. Đó, đấu sót mà liên quan tới thằng KOC với thằng, thằng, thằng, thằng FCN thì nó như vậy. Thì nó có thêm cái phần là cái người nhận nó sẽ là có cái ông MCN. 

Speaker 1:  Rồi rồi, chỗ này có ông đây xem ta. 

Speaker 1:  Đây, có thêm ông ACN vào trong cái đợt nó luôn. 

Speaker 1:  Đó là sẽ chuyển tiền thì chuyển luôn cho ông ACN nữa chứ không phải chuyển mình KOC KOL không. 

Speaker 1:  Cái chỗ này là mình thanh toán cho M một đợt hay là mình, mình, mình muốn tách rời nè. 

Speaker 1:  À, cái phần này em đang muốn là đi chung một đợt với creator luôn. 

Speaker 1:  Tại vì theo cái, cái, cái phần lầu hồi nãy với lại show thì em thấy là khi mà báo đối soát qua chốt tổng xong rồi MCN nó xác nhận thì bắt đầu là bên mình sẽ bắt đầu đi thanh toán dựa theo cái phần đó. Thì ờ, sẽ thanh toán và đầu MCN lẫn búp luôn. 

Speaker 1:  Thì em thấy là ok. 

Speaker 2:  Rồi thế thì ok rồi đó. 

Speaker 1:  Đó, cái thanh toán nó sẽ đi chung. Rồi thì cái chỗ này á thì mình sẽ cập nhật cái gì? Thứ nhất á, luồng đấu sót là mình thêm cái cái trạng thái của creator vào. 

Speaker 1:  Thứ hai á là ông creator ổng có thêm cái cái giao diện xác nhận. Rồi đây. Chỗ này em thấy bị thiếu mất cái nút đó rồi. 

Speaker 1:  Nó nãy có cái nút nó mới đúng. 

Speaker 1:  Đấy, nó có nút để báo này nè. 

Speaker 1:  Nha. 

Speaker 1:  Rồi để em qua coi cái giao diện của MCN nè. MCN cũng có cái đợt đó luôn. 

Speaker 1:  Dạ, thì ổng coi thử á là ổng, ổng sẽ ông này á là hoa hồng chừng này, phí quản lý chừng này. Ông này hoa hồng chừng này, phí quản lý chừng này. Để em thêm 1% vào cho nó chuẩn. 

Speaker 1:  Ông đó chừng này, phí quản lý chừng này. Rồi xong cái xác nhận. 

Speaker 1:  Đấy. 

Speaker 1:  Rồi ừm, rồi tới cái đề xuất nè. Cái đề xuất này mới rắc rối nè. Tức là bây giờ ông này ổng đang là 15% đúng không? 

Speaker 1:  Bây giờ ổng là 3, ổng, ổng đề xuất đang 30%. Đó, để gửi qua cho ông, ông KOC. Ông qua ông KOC này á là ổng thấy cái đề xuất rồi. 

Speaker 1:  Rồi rồi, xem của tao rồi rồi. 

Speaker 1:  Rồi ổng thấy đề xuất rồi, ổng đồng ý đi. 

Speaker 1:  Ổng ví dụ ổng thấy đề xuất xong ổng đồng ý đi. Thì bây giờ á là, là cái tình huống này á là cái hoa hồng nó tính như thế nào. Bây giờ sẽ có câu hỏi là khi người ta đề xuất thay đổi cái phần trăm như vậy thì hoa hồng nó tính như thế nào. 

Speaker 1:  Nó tính theo thời điểm chấp nhận cái đề xuất hay là, hay sao? Hay là nó tính cho cả đợt đối sót rồi á. 

Speaker 1:  À, nút. 

Speaker 1:  Đề xuất này nè. Đó, đề xuất này mới, mới phức tạp nè. Đó, bây giờ tôi muốn, tôi không để 10% nữa. 

Speaker 1:  Đó, mà tôi lấy 20. 

Speaker 1:  Đấy, thì sao? Có đi gia hạn đấy nữa xíu nói sau nha. Gia hạn đấy là cái hợp đồng thôi. 

Speaker 1:  Không liên quan. Rồi cái đề xuất này bây giờ tôi sửa lên 20%. 

Speaker 1:  Thì cái 20% nó thường nó áp dụng thế nào? 

Speaker 2:  Thường có cái hệ thống khác ấy nó sẽ không cho chạy lại back test đâu anh. Nó sẽ cho áp dụng từ thời điểm đấy trở đi thôi ấy. Kể cả thằng Shopee MCN hay gì đấy mình đang chạy thì nó cũng tương tự thế thôi. 

Speaker 1:  Ừ. 

Speaker 2:  Cho nên tốt nhất là mình làm một cái gu trong sáng nhất mình cho họ chạy lại hay làm gì cả. 

Speaker 1:  Ừ, nếu như mà tính từ đó trở đi thì cái lúc vào cái đấu sót mình sẽ xử lý sao ta? 

Speaker 1:  Bây giờ là cái chỗ này là cái phần trăm nó sẽ, nó có hai dòng luôn rồi. 

Speaker 1:  Một cái dòng lúc 15%, một cái dòng lúc 20%. 

Speaker 1:  Tại vì nó đổi lễ dở trong tháng ấy. 

Speaker 2:  À, xong cái trường hợp của anh đưa ra là nó sẽ thay đổi ở trong tháng là một tháng nó có thể thay đổi hai lần đúng không? 

Speaker 1:  Ừ. 

Speaker 2:  Ờ, sẽ có hai cái tỉ lệ khác nhau đúng không? 

Speaker 1:  Đúng. 

Speaker 1:  Đổi hai lần thì nó là ba tỉ lệ mà đổi một lần nó là hai tỉ lệ. 

Speaker 2:  Ok, đơn giản với cái phây đầu tiên mà anh chưa làm được thì anh cho xét theo tháng thôi thế là xong. 

Speaker 1:  Ừ, thì đó cũng được. 

Speaker 2:  Đó là thu gọn các cái scope để cho nó nhỏ nhất có thể thôi ạ. 

Speaker 1:  Cái cái kỳ đấu sót này của mình nó cũng chẳng phải theo tháng đâu nha. Kỳ đấu sót của mình nó cũng, nó cũng, nó cũng bưa lắm. Nó cũng, nó cũng vô chừng á. 

Speaker 1:  Đấy, sau cái đó thì để, để anh coi thử có một cái cách gì nó nhanh nhất không. 

Speaker 1:  Nhưng mà anh muốn hỏi chỗ hạ là bây giờ cái này là ngoài thực tế mình hay làm thế nào ấy. 

Speaker 1:  Cái đề xuất nó sẽ. 

Speaker 3:  Ờ, cái này á, tại vì thường thì cái cam ambassador nó đang chạy theo từng tháng, từng tháng nó sẽ chốt đối soát. Thì như vậy thì em thấy là theo chị Vui nói là hợp lý anh. Là mình cứ chốt theo tháng đi. 

Speaker 3:  Kiểu như là cái hoa hồng đó vẫn sẽ giữ cho tới đầu tháng sau mới được thay đổi. Thì nó sẽ ok hơn. Cho dới được thay đổi. 

Speaker 3:  Để mà cuối tháng này là chốt hết tất cả cam trước. 

Speaker 1:  Cho nó dễ hơn chứ không nó bị cái đầu đối soát. 

Speaker 2:  Rồi, 

Speaker 3:  Mình làm như cái sản phẩm iFlex hoa hồng của TikTok Shop á, có thay đổi hoa hồng của sản phẩm thì nó vẫn thay đổi theo tháng, tính từ thời điểm mà thay đổi thì qua tháng sau nó mới thay đổi mà update cái hoa hồng mới. Thì cái phần này mình cứ làm theo, theo vậy cũng được anh. 

Speaker 3:  Ok không? 

Speaker 1:  Ok rồi. Để anh nghiên cứu lại cái chỗ đó. 

Speaker 2:  Nó cũng cho dù vào đầu tháng nó cũng nhiều cái biến số đó, chứ nó không, cũng không phải là cứ đầu tháng là anh giải quyết được đâu. Nhất là cái hệ thống của mình là nó, nó đi theo ngày. 

Speaker 2:  Nó đi theo ngày. Cái này nó phải lưu. 

Speaker 1:  Mà để em coi coi. 

Speaker 2:  Rồi thì những cái mà nãy giờ mọi người chốt á là nó sẽ thay đổi ít nhiều so với cái sơ đồ luồng, mấy cái luồng mà Vui gửi qua email nha. Thì cái này anh sẽ viết lại, viết lại gửi mọi người xác nhận nha. 

Speaker 1:  Ừ, cái này thì em nghĩ là mình cũng phải chốt lại được một cái scope MVP anh Vĩnh để mình chốt được một cái scope nhỏ nhất để, để nó chạy được ấy. 

Speaker 2:  Ờ. 

Speaker 1:  Tránh là mình làm cái scope hiện tại anh, anh trình bày nó đủ nhưng mà nó rất là to. Cái mà em gửi thì nó cũng là đang một cái đầy đủ nhưng mà nó cũng là sẽ là một cái to và mình sẽ cần phải update nhiều qua các tháng ấy. 

Speaker 2:  Ừ. 

Speaker 1:  Chứ nó không, cũng, cũng không phải là tháng này mình lên là mình chạy được luôn hết theo cả cái nguyên cái luồng đấy. 

Speaker 2:  Ok. 

Speaker 1:  Thì mình sẽ phải chốt lại xem là cái gì sẽ phải làm trước ấy. 

Speaker 2:  Rồi, thế thì bên anh giờ anh sẽ chọn thế này nè. Thứ nhất á là có danh sách MCN. Thứ hai á là có cái phần thành viên. 

Speaker 2:  Thì cái phần thành viên này á là bây giờ là anh cần cái câu á là Hà đang, đang, đang, đang xử lý á. mình đưa lên. 

Speaker 2:  Hay là cái ông. 

Speaker 2:  Hai, hay là cái ông MCN ông sẽ đưa lên. 

Speaker 2:  Đấy, tức là cái danh sách thành viên đó mình sẽ làm giúp họ hay là sao đó. 

Speaker 2:  Thì cái version 1 là Hà muốn thế nào? 

Speaker 3:  Ờ, thành viên ở đây là KC đúng không anh? 

Speaker 2:  Ờ, KC đó. 

Speaker 3:  KC này thì ờ, cái thành viên này ủa em tưởng là khi mà MCN nó mời theo cái luồng hồi nãy mình có nói á là MCN, MCN nó mời thì nó sẽ hiển thị lên đây luôn chứ. 

Speaker 2:  Rồi đó thì mời đúng không? Ấy là, ấy là anh đang hỏi là bây giờ mình có muốn là ột nó, nó, nó, nó nhập hết ở giai đoạn một không ạ? 

Speaker 2:  Hay là, hay là MCN vào nó phải onbox từ đầu chứ nó phải mời lại từng thành viên đó từ đầu. 

Speaker 3:  Ok, nếu mà thao tác như vậy thì em nghĩ là để cho MCN nó tự thao tác luôn cho nó dễ. 

Speaker 2:  Rồi ok, thế chốt như thế. Rồi cái MCN tự thao tác này nó sẽ sinh ra hai vấn đề nè Vui nè. Thứ nhất á là cái ông KOC nếu ổng, ổng khả năng cao là ổng sẽ chưa tồn tại trên hệ thống mình. 

Speaker 2:  Anh nghĩ vậy. 

Speaker 1:  Tức là cái khả năng mà lúc mà cái ông MCN này ổng mời á là ông KOC này ổng chưa tồn tại đâu. 

Speaker 2:  Ừ. 

Speaker 1:  Sao lại chưa tồn tại nhỉ? Trong cái trường hợp mời lại còn chưa tồn tại luôn ấy ạ. 

Speaker 2:  Thế thì có cách nào để khi nó đăng ký với link mời của thằng MCN thì nó cũng đăng checking được không? em có chạy một cái luồng ở trên hệ thống của IT. 

Speaker 1:  Ừ. 

Speaker 2:  Thì em có build một cái luồng đấy rồi. Thì bản thân trong cái phần link invite của em ấy là khi mà bạn ấy vào bằng cái link invite đấy mà bạn ấy đăng ký thì là bạn ấy đã được tính cho bạn MCN khi mà chia sẻ link rồi. 

Speaker 1:  Rồi ok. Thế thì em sẽ chọn giải pháp chia sẻ link cho anh chạy anh chưa chọn giải pháp mời. 

Speaker 1:  Nó chia sẻ link nó sẽ ok hơn. 

Speaker 1:  Đấy, chia sẻ link thì bây giờ á là ông này ông chưa có tài khoản á là ông phải đăng ký tài khoản trước. Ông đăng ký tài khoản xong ông mới vào cái luồng chấp nhận lời mời. Còn không á là bây giờ là ổng nhận được cái link xong á là bây giờ là ổng chỉ phải bấm chấp nhận lời mời luôn. 

Speaker 2:  Đó. Còn cái nút mời này á, là anh sẽ chưa cho search, chưa cho gõ gì hết. 

Speaker 1:  Dạ. 

Speaker 2:  Thì vì cái này anh đang nghĩ là nó rất là rủi ro về, về, về bảo mật này. 

Speaker 1:  Nó không có, nó vi phạm nhiều lắm. 

Speaker 2:  Bây giờ cái này chỉ việc mời thôi. 

Speaker 1:  Đấy, rồi sẽ lấy link, link là gửi đi. Cầm cái link gửi đi là nó giải quyết được hai tình huống luôn. Ông chưa có tài khoản cũng được, ổng có tài khoản cũng được. 

Speaker 2:  Rồi cái phần trăm thì bây giờ xác định là sẽ có một thôi. Bây giờ bỏ cái nút đề xuất đi. Đấy, tạm thời là dừng cái nút này. 

Speaker 2:  Da. 

Speaker 1:  Thì ông, ông đề xuất đổi phần trăm gì đó thì anh sẽ tính lại sau. 

Speaker 2:  Cái này version 1 mình chưa cần làm. 

Speaker 1:  Rồi tiếp tục là xử lý cái đối soát. Đó thì cái bây giờ cái đối soát thì bây giờ là chưa cần chờ xác nhận và chưa cần chờ báo lỗi. Mấy cái luồng đó bây giờ mình sẽ để cho nó chạy ở ngoài. 

Speaker 1:  Được chưa? Thì nhận tiền xong rồi chuyển cáo gì đó là giống y cái bây giờ cái mình đang chạy á. Tại vì vốn, vốn dĩ mấy, mấy cái đang chạy hiện tại là cũng KOC nó cũng đâu biết gì đâu. 

Speaker 1:  Nó cứ tới giờ nó nhận tiền thôi. Nó, nó nhận được thông báo là bạn đã được đối soát thôi. 

Speaker 2:  Da. 

Speaker 1:  Tại vì nếu như mà hệ thống mình tính đúng á, thì ông MCN sẽ nhận đúng tiền. Nhưng mà hệ thống mình đã tính sai rồi là kiểu gì nó cũng, nó cũng, nó cũng thiếu cách giải quyết. 

Speaker 2:  Đấy, nhưng ông, cái ông KOC của mình hiện tại mà ổng, ổng được thiếu view các kiểu á, thì ổng cũng kiện cáo, kiện cáo xong rồi nó tới, nó vào cái luồng mà, mà tặng bonus. Vào luồng tặng bonus thì nó lại đối soát ở kỳ tiếp theo. 

Speaker 2:  Thì cái riêng cái bonus nó sẽ kỳ tiếp theo. Còn cái mà, cái mà bị thiếu á, nó vẫn đối soát ở kỳ này. Thì số nó vẫn sẽ đúng. 

Speaker 2:  Thì cái luồng đối soát bây giờ sẽ tự động. 

Speaker 1:  Được chưa? Và nó chỉ thấy cái bảng kia thôi. Đó, bảng sau kia thôi chứ không thấy cái, nó không có cái action chờ nữa. 

Speaker 1:  Da, sẽ có như vậy. 

Speaker 2:  Rồi ông này nè, ổng vô là không có cái, cái, cái, cái trang này thấy cũng được. Cái trang này thì ok. Đấy, nhưng mà không có cái nút, đấy, không có cái nút, không có cái nút báo sai nữa thì nó đã, rồi ông, ông Bạch Mi ổng bấm là ông này cũng thấy bảng kia thôi. 

Speaker 2:  Đó, mỗi ông như thế này. Đó, là bao nhiêu, bao nhiêu, bao nhiêu. Nè, tổng bao nhiêu tiền. 

Speaker 2:  Xong. 

Speaker 2:  Ông Bạch Mi thì cũng vậy, ổng chi tiền chi một lúc luôn. Với MCN luôn. 

Speaker 1:  Rồiái quy chế này thì. 

Speaker 2:  Cái quy chế này sao? Mọi người có nghĩ đây là v1 không? Anh thì nghĩ là không. 

Speaker 2:  Tại vì mấy cái này mình sẽ admin sẽ upload trước ấy. Là bây giờ mình khoan làm cái vụ ban bố quy chế mới vậy. 

Speaker 1:  Ok. 

Speaker 2:  Thì bây giờ mình chỉ vào là, ờ, mỗi ông MCN đó thì ổng lại có cái, có cái này. Đó, upload lên. 

Speaker 1:  Da. 

Speaker 2:  Nó lại upload lên. 

Speaker 1:  Ông mà đã upload, ổng có mấy cái nút này trạng thái là đã hết á, thì ổng sẽ được nhận thanh toán. Còn ông mà có cái gì đó mà cái trạng thái ổng bị thiếu á là ổng không nhận được thanh toán. Vậy thôi. 

Speaker 2:  Đó, sẽ có v1 nó sẽ vậy nha. 

Speaker 1:  Ok anh. 

Speaker 2:  Rồi. 

Speaker 1:  Thì cũng, cũng, cũng. 

Speaker 2:  MCN. 

Speaker 1:  Anh nhớ hồi xưa làm cái này bên tech, bên TV luôn xài Techcom nó cũng, nó cũng đòi nè. Techcom nó phức tạp hơn nhiều. Techcom là một cái ông như thế này á, là ổng một cái ông KOC nó còn thuộc nhiều ông MCN cơ. 

Speaker 2:  Chứ nó không có quan hệ một một đâu. 

Speaker 1:  Mình làm theo mô hình đơn giản thôi anh. Bản chất là các cái hệ thống khác trên thế giới nó cũng thế thôi. Thằng Shopee, thằng TikTok nó cũng thế thôi. 

Speaker 1:  Cùng một thời điểm thì chỉ cùng, chỉ được thuộc một ông MCN thôi. Có thể out nhưng mà sau thời điểm đấy thì sẽ phải join ông MCN khác. 

Speaker 2:  Rồi. 

Speaker 1:  Cái gì nữa quên rồi. 

Speaker 2:  Ừm, luồng rời đi. 

Speaker 1:  Được chưa? 

Speaker 2:  Thì anh hiểu mà cái này là cái ông MCN ổng sẽ đưa KOC vào để làm video nói chuyện theo view hả? Chứ cái này không phải là luồng, luồng, luồng booking tính tiền hả? 

Speaker 1:  Đúng rồi, đúng rồi đấy anh. Là người ta đang mình để grow cái, cái KOC ở trong cái này đấy anh ạ. 

Speaker 2:  Ok. Nó đang tính view. 

Speaker 2:  Rồi. 

Speaker 1:  Đấy, là cái top sẽ có vậy. Anh sẽ ngày mai, ngày mai anh sẽ soạn lại cái, cái scope anh sẽ chốt lại cái design, anh sẽ sửa lại những cái tính năng gì mà sẽ là v1 để mới có trên design thôi. 

Speaker 2:  Rồi gửi vào một luồng cho mọi người cùng coi. 

Speaker 1:  Ha, xác nhận là cái mình chạy thôi. 

Speaker 2:  Vâng, anh cứ gửi vào cái luồng plan tháng 11 ấy, xong rồi em sẽ gửi thêm anh email của bạn Dũng với cả bạn Hà group thêm hai bạn đấy vào thôi. 

Speaker 1:  Ok, được. 

Speaker 2:  Rồi xong. 

Speaker 1:  Rồi xong. 

Speaker 2:  Ok. 

Speaker 1:  Chắc mình kết thúc buổi họp thôi ạ. 

Speaker 2:  Cảm ơn cả nhà. 

Speaker 1:  Rồi. 

Speaker 2:  Bye bye cả nhà nhé. 

Speaker 1:  Bye bye cả nhà. 