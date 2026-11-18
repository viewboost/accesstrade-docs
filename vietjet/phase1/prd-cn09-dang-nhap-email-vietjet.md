# CN-09 · Đăng nhập bằng email Vietjet và đăng ký bằng mã nhân viên

**Date:** 2026-11-17 · **Author:** Vinh Nguyễn · **Version:** 0.6 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-09.1 Mục đích

Chương trình chỉ dành cho cán bộ nhân viên Vietjet. Hệ thống hiện cho đăng nhập bằng tài khoản mạng xã hội (TikTok, Facebook, Google) và hỏi mã nhân viên ở một bước riêng sau khi đăng nhập. Chức năng này thêm:

1. Đăng nhập bằng **email**, chỉ cho phép email thuộc **tên miền của Vietjet**.
2. Màn **đăng ký yêu cầu nhập mã nhân viên** ngay lúc đăng ký.
3. **Quên mật khẩu và đặt lại mật khẩu**, để người đã đăng ký không bị kẹt tài khoản.
4. **Đăng nhập bằng đường dẫn gửi qua email (magic link)**, cho người không muốn nhập mật khẩu.
5. Mọi email xác thực đều gồm **mã OTP kèm đường dẫn**: nhập mã hoặc bấm đường dẫn đều được (CN-09.6).

Ví dụ: nhân viên dùng email công ty Vietjet đăng ký, nhập mã nhân viên và vào được chương trình. Người dùng email Gmail cá nhân bị từ chối.

## CN-09.2 Phạm vi

**Trong phạm vi**
- Đăng nhập và đăng ký bằng email.
- Danh sách tên miền email được phép (allow list).
- Nhập mã nhân viên ở màn đăng ký.
- Quên mật khẩu, đặt lại mật khẩu (CN-09.5).
- Đăng nhập bằng magic link (CN-09.6).

**Ngoài phạm vi**
- Xác minh mã nhân viên với danh sách của HR Vietjet: mã nhân viên kiểm theo quy tắc sẵn có của hệ thống (CN09-BR05).
- Thay đổi hoặc gỡ mã nhân viên của tài khoản đã đăng ký: giữ theo hành vi sẵn có (phải nhờ bộ phận hỗ trợ).

## CN-09.3 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md) | Các màn của app sau khi đăng nhập |

## CN-09.4 Quy tắc nghiệp vụ

| Mã | Quy tắc |
|---|---|
| **CN09-BR01** | Màn đăng nhập có lựa chọn **đăng nhập bằng email** |
| **CN09-BR02** | Chỉ email có **tên miền thuộc danh sách tên miền được phép** mới đăng ký và đăng nhập được. So khớp không phân biệt hoa thường |
| **CN09-BR03** | Email ngoài danh sách bị từ chối kèm thông báo rõ: email phải là email công ty Vietjet |
| **CN09-BR04** | Danh sách tên miền được phép do Admin cấu hình; để trống thì không email nào được phép đăng ký bằng email |
| **CN09-BR05** | Màn **đăng ký** bắt buộc nhập **mã nhân viên** cùng lúc với email, ở bước đầu. Không nhập thì không gửi mã xác thực và không hoàn tất đăng ký. Mã đã gắn với tài khoản khác thì bị từ chối (một mã một tài khoản), theo quy tắc mã nhân viên sẵn có |
| **CN09-BR06** | Đăng ký gồm **hai bước**. Bước 1: email và mã nhân viên, hệ thống kiểm tên miền và mã rồi gửi **mã xác thực (OTP, hiệu lực 5 phút)** tới email; chưa đặt mật khẩu, chưa đăng nhập được. Bước 2: nhập mã xác thực, họ tên và mật khẩu; đúng mã thì mới đặt mật khẩu, ghi mã nhân viên, kích hoạt tài khoản và đăng nhập. Mật khẩu chỉ được đặt sau khi chứng minh được quyền sử dụng email, để người biết email của người khác không thể gài mật khẩu trước |
| **CN09-BR09** | Đăng ký lại bằng email đang chờ xác thực chỉ gửi mã mới, cách nhau tối thiểu 1 phút; tài khoản chờ xác thực không đăng nhập được và không giữ chỗ mã nhân viên (hai người cùng đăng ký một mã thì người xác thực sau bị từ chối) |
| **CN09-BR07** | Tài khoản đã có từ trước (mạng xã hội, hoặc mật khẩu) vẫn đăng nhập như cũ, không bị bắt đăng ký lại hay xác thực lại email. Đăng nhập bằng email và mật khẩu chỉ chặn tên miền khi chương trình đã cấu hình danh sách tên miền |
| **CN09-BR08** | Các cách đăng nhập khác (TikTok, Facebook, Google) vẫn còn nếu không có quyết định bỏ; tài khoản đăng nhập bằng cách đó vẫn phải có mã nhân viên mới tham gia được chương trình |

## CN-09.5 Quên mật khẩu và đặt lại mật khẩu

Người đã đăng ký bằng email nhưng quên mật khẩu tự lấy lại quyền vào, không cần nhờ bộ phận hỗ trợ.

| Mã | Quy tắc |
|---|---|
| **CN09-BR10** | Màn đăng nhập bằng email có lối **Quên mật khẩu**. Người dùng nhập email, hệ thống gửi **mã xác thực (OTP, hiệu lực 5 phút)** tới email đó |
| **CN09-BR11** | Thông báo sau khi bấm gửi luôn giống nhau dù email có tài khoản hay không, để người ngoài không dò được email nào đã đăng ký. Chỉ tài khoản đã đăng ký và đã xác thực email mới nhận được mã; email ngoài danh sách tên miền không nhận mã |
| **CN09-BR12** | Nhập đúng mã thì được **đặt mật khẩu mới**. Mật khẩu mới theo cùng quy tắc mật khẩu của lúc đăng ký. Mã chỉ dùng một lần |
| **CN09-BR13** | Giữ các giới hạn của luồng đăng ký: yêu cầu gửi lại mã cách nhau tối thiểu 1 phút; nhập sai mã quá số lần cho phép thì mã bị hủy và phải xin mã mới |
| **CN09-BR14** | Đặt lại mật khẩu xong, mọi phiên đăng nhập đang có của tài khoản đó bị **đăng xuất**; người dùng đăng nhập lại bằng mật khẩu mới |
| **CN09-BR15** | Tài khoản chưa xác thực email (đăng ký dở) không dùng quên mật khẩu để vượt bước xác thực: yêu cầu của tài khoản này được xử lý như đăng ký lại (CN09-BR09). Quên mật khẩu không đổi mã nhân viên của tài khoản |
| **CN09-BR16** | Tài khoản chỉ có đăng nhập mạng xã hội (chưa từng đặt mật khẩu) dùng quên mật khẩu để **đặt mật khẩu lần đầu**, sau khi xác thực email bằng mã |

## CN-09.6 Mã OTP kèm đường dẫn (magic link)

Mọi email xác thực của chức năng này (đăng ký, quên mật khẩu, đăng nhập bằng email không mật khẩu) đều có **hai cách xác nhận cùng lúc**: nhập **mã OTP**, hoặc bấm **đường dẫn** trong thư. Hai cách tương đương nhau; người dùng dùng cách nào tiện hơn, ví dụ mở thư trên điện thoại thì bấm đường dẫn, mở thư trên máy khác với nơi đang thao tác thì nhập mã.

| Mã | Quy tắc |
|---|---|
| **CN09-BR17** | Mỗi lần gửi xác thực chỉ có **một yêu cầu xác thực**, gồm mã và đường dẫn đi cùng nhau trong một thư. Dùng mã hoặc dùng đường dẫn đều **xác nhận chính yêu cầu đó**; dùng một trong hai thì cái còn lại **mất hiệu lực** |
| **CN09-BR18** | Mã và đường dẫn cùng hiệu lực **5 phút**, chỉ dùng một lần. Hết hạn hoặc đã dùng thì báo rõ và cho xin thư mới. Xin thư mới làm thư cũ chưa dùng mất hiệu lực |
| **CN09-BR19** | Như CN09-BR11, thông báo sau khi bấm gửi luôn giống nhau dù email có tài khoản hay không |
| **CN09-BR20** | Bấm vào đường dẫn mở một trang **xác nhận** có nút bấm; chỉ bấm nút đó mới tính là xác nhận. Việc này tránh phần mềm quét thư của công ty tự mở đường dẫn và làm nó mất hiệu lực trước khi người dùng bấm |
| **CN09-BR21** | Gửi lại thư cách nhau tối thiểu 1 phút; nhập sai mã quá số lần cho phép thì yêu cầu bị hủy, kể cả đường dẫn (cùng một yêu cầu, cùng bộ đếm với CN09-BR13). Trang xác nhận của đường dẫn không cho thử lại vô hạn |
| **CN09-BR22** | Xác nhận xong, người dùng đi tiếp đúng bước kế của luồng đang làm: **đăng ký** thì sang bước 2 (họ tên, mật khẩu; mật khẩu vẫn chỉ được đặt sau khi xác nhận xong, CN09-BR06); **quên mật khẩu** thì sang màn đặt mật khẩu mới; **đăng nhập không mật khẩu** thì đăng nhập luôn |
| **CN09-BR23** | **Đăng nhập không mật khẩu**: màn đăng nhập bằng email có lựa chọn "Gửi mã đăng nhập qua email". Chỉ tài khoản đã đăng ký và đã xác thực email, thuộc tên miền được phép, mới dùng được. Không dùng để đăng ký mới, vì đăng ký bắt buộc có mã nhân viên (CN09-BR05) |
| **CN09-BR24** | Đăng nhập không mật khẩu không thay đổi mật khẩu hiện có và không bỏ yêu cầu mã nhân viên: tài khoản chưa có mã nhân viên vẫn phải nhập mã mới tham gia được (CN09-BR08) |
| **CN09-BR25** | Đường dẫn mở trên một máy khác máy đang thao tác vẫn xác nhận được yêu cầu, nhưng **phiên đăng nhập chỉ được cấp cho nơi đã xin thư** (nơi bấm nút xác nhận chỉ báo "đã xác nhận, quay lại thiết bị ban đầu"). Nếu không làm vậy, người nhận được thư chuyển tiếp sẽ vào được tài khoản trên máy của họ |

## CN-09.7 Giới hạn tần suất gửi thư và thử mã

Mục tiêu: chặn kẻ xấu dội thư vào hộp thư người khác hoặc đoán mã, mà **không** để kẻ xấu khóa được người thật ra khỏi tài khoản. Tham khảo cách làm của OWASP (Forgot Password Cheat Sheet), Auth0 (đăng nhập không mật khẩu) và luồng đăng nhập staff sẵn có của hệ thống.

| Mã | Quy tắc |
|---|---|
| **CN09-BR26** | Gửi thư xác thực tính **theo email và theo từng luồng** (đăng ký, quên mật khẩu, đăng nhập không mật khẩu): mỗi luồng cách nhau tối thiểu **1 phút** và tối đa **5 yêu cầu trong 30 phút**; ngoài ra tổng ba luồng của một email tối đa **12 yêu cầu trong 30 phút**. Hết cửa sổ thì xin lại được. **Không có trần theo ngày**. Tách theo luồng để kẻ xấu dội thư vào một luồng của email người khác không chặn được các luồng còn lại. Rủi ro còn lại được chấp nhận: kẻ xấu làm một luồng của một email không xin được thư trong tối đa 30 phút; người dùng vẫn đăng nhập được bằng mật khẩu hoặc mạng xã hội. Giải pháp triệt để (CAPTCHA) để giai đoạn sau |
| **CN09-BR27** | Mỗi địa chỉ IP gửi tối đa **500 yêu cầu trong 1 giờ**. Mức này rất rộng vì nhân viên Vietjet dùng chung IP văn phòng và ngày mở chương trình có thể có hàng trăm người cùng lúc; chỉ để chặn quét hàng loạt, lớp chính là giới hạn theo email (BR26, BR32). Địa chỉ IP phải lấy đúng từ proxy, việc cấu hình thuộc bên triển khai (ghi ở tài liệu triển khai) |
| **CN09-BR28** | Mọi yêu cầu được đếm, **kể cả email không có tài khoản hoặc ngoài danh sách tên miền**, để giới hạn không trở thành cách dò email nào có tài khoản (CN09-BR11). Vượt giới hạn thì báo "thử lại sau" giống nhau cho mọi email |
| **CN09-BR29** | Nhập sai mã quá **5 lần** thì yêu cầu bị hủy kể cả đường dẫn (CN09-BR13, BR21); phải xin thư mới. **Không khóa tài khoản**: tài khoản vẫn đăng nhập được bằng mật khẩu và cách khác trong lúc bị tấn công |
| **CN09-BR30** | Bước 1 của đăng ký trả **cùng một phản hồi** dù email đã có tài khoản hay chưa; email đã có tài khoản không nhận thư và không tạo gì. Thông báo ghi: "Nếu email này chưa đăng ký, chúng tôi đã gửi mã xác thực. Nếu bạn đã có tài khoản, hãy dùng Đăng nhập hoặc Quên mật khẩu." Để không ai dò được email nào đã đăng ký (CN09-BR11) |
| **CN09-BR31** | Đường dẫn trong thư đặt thông tin xác thực trong **phần sau dấu #** của địa chỉ, để không vào nhật ký truy cập của máy chủ và proxy; trang xác nhận đọc xong thì xóa khỏi thanh địa chỉ. Bấm đường dẫn sai không làm hỏng mã và đường dẫn đúng của người khác: chỉ yêu cầu đúng chủ mới bị tính lần sai |
| **CN09-BR32** | Mỗi email tối đa **30 lượt nhập sai mã trong 24 giờ**, cộng dồn qua mọi yêu cầu và mọi luồng (đăng ký, quên mật khẩu, đăng nhập không mật khẩu). Hết lượt thì **đường nhập mã** của email đó đóng đến hết cửa sổ; đường **đường dẫn**, đăng nhập bằng mật khẩu và mạng xã hội vẫn dùng được, nên không khóa tài khoản (BR29). Lý do: bỏ trần gửi theo ngày (BR26) không được làm kẻ xấu có thêm lượt đoán mã trên email của người khác |

## CN-09.8 Kịch bản kiểm thử

**Dữ liệu chung:** danh sách tên miền được phép có tên miền Vietjet; mã nhân viên NV001 chưa ai dùng.

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN09-TC01 | Đăng ký đúng | Đăng ký bằng email Vietjet, nhập NV001, xác thực email | Tạo tài khoản, vào được chương trình | BR01, 05, 06 |
| CN09-TC02 | Email ngoài danh sách | Đăng ký bằng email Gmail | Bị từ chối, thông báo phải dùng email Vietjet | BR02, 03 |
| CN09-TC03 | Hoa thường | Đăng ký bằng email có chữ hoa trong tên miền | Vẫn được chấp nhận | BR02 |
| CN09-TC04 | Thiếu mã nhân viên | Đăng ký bằng email Vietjet, để trống mã | Không hoàn tất, báo thiếu mã nhân viên | BR05 |
| CN09-TC05 | Mã đã dùng | Người thứ hai đăng ký với NV001 | Bị từ chối, báo mã đã được dùng | BR05 |
| CN09-TC06 | Chưa xác thực email | Làm bước 1, chưa nhập mã | Chưa có mật khẩu, không đăng nhập được, không vào được chương trình | BR06 |
| CN09-TC10 | Gài mật khẩu | Người khác đăng ký bằng email của nạn nhân khi nạn nhân chưa xác thực | Không có mật khẩu nào được đặt; nạn nhân đặt mật khẩu của mình ở bước 2 | BR06 |
| CN09-TC11 | Gửi lại mã | Đăng ký lại cùng email trong 1 phút | Bị từ chối; sau 1 phút gửi mã mới | BR09 |
| CN09-TC07 | Danh sách trống | Xóa hết tên miền trong cấu hình | Mọi email bị từ chối | BR04 |
| CN09-TC08 | Tài khoản cũ | Người đã có tài khoản mạng xã hội và mã nhân viên đăng nhập | Vào như trước | BR07 |
| CN09-TC09 | Đăng nhập mạng xã hội chưa có mã | Đăng nhập TikTok, chưa có mã nhân viên | Phải nhập mã nhân viên mới tham gia được | BR08 |
| CN09-TC12 | Quên mật khẩu đúng | Tài khoản đã đăng ký bấm Quên mật khẩu, nhập mã, đặt mật khẩu mới | Đăng nhập được bằng mật khẩu mới; mật khẩu cũ không còn dùng được | BR10, 12 |
| CN09-TC13 | Không lộ email | Quên mật khẩu với email chưa đăng ký, rồi với email đã đăng ký | Hai trường hợp hiện cùng một thông báo; email chưa đăng ký không nhận mã | BR11 |
| CN09-TC14 | Email ngoài danh sách | Quên mật khẩu với email Gmail | Không gửi mã, thông báo như BR11 | BR11 |
| CN09-TC15 | Mã hết hạn hoặc dùng lại | Nhập mã sau 5 phút; nhập lại mã đã dùng | Bị từ chối, phải xin mã mới | BR12, 13 |
| CN09-TC16 | Nhập sai mã nhiều lần | Nhập sai mã quá số lần cho phép | Mã bị hủy, phải xin mã mới | BR13 |
| CN09-TC17 | Đăng xuất phiên cũ | Tài khoản đang đăng nhập trên máy A; đặt lại mật khẩu trên máy B | Máy A bị đăng xuất | BR14 |
| CN09-TC18 | Tài khoản đăng ký dở | Quên mật khẩu với email chưa xác thực lần đăng ký | Xử lý như đăng ký lại, không đặt được mật khẩu bằng đường này | BR15 |
| CN09-TC19 | Tài khoản mạng xã hội | Tài khoản TikTok chưa có mật khẩu dùng Quên mật khẩu | Đặt được mật khẩu lần đầu sau khi xác thực email | BR16 |
| CN09-TC20 | Đăng nhập bằng đường dẫn | Tài khoản đã đăng ký chọn gửi mã đăng nhập, mở thư trên cùng máy, bấm đường dẫn rồi bấm nút xác nhận | Đăng nhập được, vào đúng chương trình | BR20, 22, 23 |
| CN09-TC25 | Đăng nhập bằng mã | Như TC20 nhưng nhập mã OTP trong thư thay vì bấm đường dẫn | Đăng nhập được; đường dẫn của thư đó không còn dùng được | BR17, 23 |
| CN09-TC21 | Không đăng ký mới bằng đăng nhập không mật khẩu | Email Vietjet chưa có tài khoản chọn gửi mã đăng nhập | Không tạo tài khoản, không gửi thư; thông báo như BR19 | BR19, 23 |
| CN09-TC22 | Đường dẫn hết hạn / dùng lại | Mở đường dẫn sau 5 phút; mở lại đường dẫn đã dùng; xin thư mới rồi mở đường dẫn của thư cũ | Cả ba bị từ chối, báo rõ | BR18 |
| CN09-TC23 | Phần mềm quét thư | Đường dẫn bị mở tự động nhưng chưa bấm nút xác nhận | Đường dẫn vẫn còn hiệu lực, chưa đăng nhập | BR20 |
| CN09-TC24 | Đăng nhập không mật khẩu chưa có mã nhân viên | Tài khoản mạng xã hội chưa có mã nhân viên vào bằng đường dẫn | Đăng nhập được nhưng phải nhập mã mới tham gia được | BR24 |
| CN09-TC26 | Đăng ký bằng đường dẫn | Làm bước 1 đăng ký, bấm đường dẫn trong thư, bấm xác nhận | Sang bước 2 để nhập họ tên và mật khẩu; chưa có mật khẩu trước bước này | BR06, 22 |
| CN09-TC27 | Quên mật khẩu bằng đường dẫn | Bấm Quên mật khẩu, bấm đường dẫn trong thư, bấm xác nhận | Sang màn đặt mật khẩu mới | BR22 |
| CN09-TC28 | Mã và đường dẫn dùng chung bộ đếm | Nhập sai mã gần đủ số lần cho phép, rồi thử đường dẫn | Vẫn tính chung một yêu cầu; vượt giới hạn thì cả mã và đường dẫn bị hủy | BR21 |
| CN09-TC29 | Mở đường dẫn trên máy khác | Xin thư trên máy A, bấm đường dẫn rồi xác nhận trên máy B | Máy B báo đã xác nhận; chỉ máy A được cấp phiên đăng nhập | BR25 |
| CN09-TC30 | Gửi dồn theo email | Xin thư quên mật khẩu 6 lần cho cùng một email trong 30 phút (mỗi lần cách hơn 1 phút) | Lần thứ 6 bị từ chối "thử lại sau"; luồng đăng nhập và đăng ký của email đó vẫn xin được; hết 30 phút xin lại được. Trộn ba luồng, tổng 12 yêu cầu thì yêu cầu thứ 13 bị từ chối | BR26 |
| CN09-TC31 | Không đốt hạn mức cả ngày | Đủ 5 yêu cầu của một email, chờ hết 30 phút | Chủ email xin được thư mới, không bị chặn đến hôm sau | BR26 |
| CN09-TC32 | Giới hạn theo IP | Một IP xin thư cho 501 email khác nhau trong 1 giờ | Yêu cầu thứ 501 bị từ chối; IP khác vẫn xin được | BR27 |
| CN09-TC33 | Không lộ email qua giới hạn | Gửi dồn cho email có và không có tài khoản | Hai trường hợp bị từ chối cùng lúc, cùng thông báo | BR28 |
| CN09-TC34 | Không khóa tài khoản | Kẻ xấu xin thư dồn và nhập sai mã cho email của nạn nhân | Nạn nhân vẫn đăng nhập được bằng mật khẩu | BR29 |
| CN09-TC38 | Trần đoán mã theo ngày | Xin thư đăng nhập và quên mật khẩu nhiều lần cho một email, nhập sai mã tổng cộng quá 30 lần trong 24 giờ | Từ lượt thứ 31, nhập mã bị từ chối dù yêu cầu còn mới; đường dẫn vẫn dùng được; chủ email vẫn đăng nhập được bằng mật khẩu | BR32 |
| CN09-TC39 | Văn phòng dùng chung IP | 400 nhân viên sau một IP mỗi người đăng ký một lần trong 1 giờ | Cả 400 yêu cầu qua; chỉ bị chặn khi IP vượt 500 | BR27 |
| CN09-TC35 | Dò email đã đăng ký | Đăng ký bước 1 với email đã có tài khoản và với email chưa có | Hai trường hợp cùng thông báo, cùng thời gian; email đã có tài khoản không nhận thư | BR30 |
| CN09-TC36 | Phá yêu cầu người khác | Gọi xác nhận đường dẫn với mã đúng của nạn nhân nhưng token sai nhiều lần | Mã và đường dẫn đúng của nạn nhân vẫn dùng được | BR31 |
| CN09-TC37 | Dội một luồng | Dội 5 yêu cầu quên mật khẩu vào một email | Quên mật khẩu của email đó bị chặn tạm; đăng nhập và đăng ký của email đó không bị ảnh hưởng | BR26 |
