# CN-01 · Điểm cố định cho mỗi bài được duyệt

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.2 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-01.1 Mục đích

Thể lệ cho mỗi bài đạt chuẩn một số điểm cố định theo loại bài (bài post hoặc video), không phụ thuộc lượt xem. Hệ thống hiện chỉ thưởng theo lượt xem, thích, bình luận hoặc theo mốc (mỗi người một lần). Chức năng này thêm một loại nhiệm vụ mới **Cố định mỗi bài được duyệt**.

Ví dụ: mức TikTok 50, Facebook Post 25. Nhân viên đăng 4 video TikTok và 2 bài Facebook Post, BTC duyệt cả 6 bài thì có 6 khoản thưởng riêng, tổng 4 × 50 + 2 × 25 = 250 điểm. Video 10 lượt xem hay 10.000 lượt xem đều được 50 điểm.

## CN-01.2 Phạm vi

**Trong phạm vi**
- Loại nhiệm vụ Cố định mỗi bài được duyệt, mức điểm đặt theo từng nguồn.
- Vòng đời khoản thưởng theo trạng thái bài: chờ duyệt, đã duyệt, bị từ chối, duyệt lại.
- Thời hạn, số suất và ngân sách ba tầng của nhiệm vụ.
- Điều kiện kích hoạt sự kiện khi chỉ có nhiệm vụ loại này.
- Hiển thị điểm của từng bài ở màn **Danh sách bài đăng** của người tham gia.

**Ngoài phạm vi**
- Chia nhỏ khoản khi ngân sách chỉ còn một phần: thiếu chỗ thì ghi 0 điểm (CN01-BR11).
- Tính lại khoản đã ghi 0 điểm khi ngân sách tăng: hệ thống chưa có chức năng này, kể cả với thưởng theo mốc.
- Giới hạn số bài tính điểm mỗi người mỗi ngày.
- Thông báo mới cho người tham gia khi khoản được tạo: người tham gia đã nhận thông báo "bài được duyệt".
- Đối soát và chi: xem [CN-02](./prd-cn02-doi-soat-thuong-theo-bai.md).

## CN-01.3 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-02](./prd-cn02-doi-soat-thuong-theo-bai.md) | Đối soát và chi các khoản thưởng của CN-01 |
| [Nền tảng và loại bài](./ref-nen-tang-loai-bai.md) | Danh sách nguồn dùng để đặt mức điểm, cách đặt mức post và video |
| [CN-03](./prd-cn03-hien-thi-diem.md) | Đổi chữ hiển thị "đ" thành "điểm". Mọi màn hình của CN-01 hiển thị theo CN-03 |
| [CN-08](./prd-cn08-giao-dien-nguoi-tham-gia.md) | Màn người tham gia hiện điểm từng bài |

## CN-01.4 Trạng thái khoản thưởng theo trạng thái bài

Mỗi cặp (bài, nhiệm vụ) có **đúng một khoản thưởng**. Trạng thái khoản đi theo trạng thái bài:

| Sự kiện | Trạng thái khoản sau sự kiện |
|---|---|
| Người tham gia nộp bài (bài chờ duyệt) | **Chờ duyệt**. Khoản tính vào ngân sách ngay từ lúc này |
| BTC duyệt bài | **Chờ đối soát** (pending) |

Khi BTC từ chối một bài đã có khoản, và khi duyệt lại bài đó, kết quả phụ thuộc khoản đã được đối soát hay chưa:

| Tình huống | Sự kiện | Kết quả |
|---|---|---|
| **A. Khoản chưa đối soát** | A1. BTC từ chối bài | Khoản chuyển **Từ chối**. Khoản không tính vào ngân sách, bài không hiện điểm |
| | A2. BTC duyệt lại bài | Chính khoản đó chuyển về **Chờ đối soát** (pending). Không tạo khoản mới |
| **B. Khoản đã đối soát** | B1. BTC từ chối bài | Khoản giữ nguyên **Đã hoàn thành** |
| | B2. BTC duyệt lại bài | Không tạo hay sửa khoản nào |

## CN-01.5 Quy tắc nghiệp vụ

| Mã | Quy tắc |
|---|---|
| **CN01-BR01** | Điểm của khoản bằng mức điểm của **nguồn** của bài, nhập ở nhiệm vụ. Nguồn không có mức, mức bằng 0 hoặc âm thì bài không có khoản. Nếu nhiệm vụ giới hạn nguồn ở ô "Áp dụng cho các source" thì bài thuộc nguồn ngoài danh sách cũng không có khoản |
| **CN01-BR02** | Bài bị từ chối ngay từ đầu không có khoản. Bài chờ duyệt và đã duyệt có khoản theo CN-01.4 |
| **CN01-BR03** | Mỗi cặp (bài, nhiệm vụ) chỉ có một khoản. Duyệt lặp, hoặc nhiều người duyệt cùng lúc, không tạo thêm khoản |
| **CN01-BR04** | **Thời hạn nhiệm vụ** tính theo **ngày đăng bài lên nền tảng**: ngày đăng nằm trong khoảng bắt đầu – kết thúc thì bài có khoản, ngoài khoảng thì không. Bài chưa có ngày đăng (chưa lấy được thông tin từ nền tảng) tạm tính theo ngày nộp, cập nhật lại khi có ngày đăng. Khi ngày đăng thật nằm ngoài khoảng, khoản chưa đối soát chuyển Từ chối |
| **CN01-BR05** | Số suất và ngân sách là hai giới hạn khác nhau, xem bảng CN-01.6 |
| **CN01-BR06** | Ô "tối đa mỗi người" của nhiệm vụ không áp dụng cho loại này. Một người có bao nhiêu bài thì có bấy nhiêu khoản |
| **CN01-BR07** | Điểm của từng bài hiện ở màn **Danh sách bài đăng** của người tham gia: điểm chờ duyệt, điểm chờ đối soát, điểm đã nhận |

## CN-01.6 Giới hạn và ngân sách

| Giới hạn | Phạm vi tính | Khi hết |
|---|---|---|
| **Số suất** của nhiệm vụ | Tổng số khoản không bị từ chối | Bài tiếp theo **không có khoản** (CN01-BR08) |
| **Ngân sách chiến dịch** | Tổng điểm của sự kiện | Khoản vẫn được tạo nhưng ghi **0 điểm** và gắn cờ vượt ngân sách (CN01-BR09) |
| **Ngân sách creator** | Tổng điểm của một người trong sự kiện | Như trên |
| **Ngân sách nội dung** | Tổng điểm của một bài | Như trên |

| Mã | Quy tắc |
|---|---|
| **CN01-BR08** | Nhiệm vụ không để "Không giới hạn số lượng" thì tổng số khoản không vượt "Số lượng". Số suất được tính trên các khoản không ở trạng thái Từ chối |
| **CN01-BR09** | Khoản được tính vào cả ba tầng ngân sách, kể cả khi đang Chờ duyệt. Chỉ cần **một** tầng không đủ chỗ cho cả khoản thì khoản ghi 0 điểm và gắn cờ vượt ngân sách. Số điểm định thưởng vẫn được lưu để biết đã bỏ lỡ bao nhiêu |
| **CN01-BR10** | Khi tầng chiến dịch không đủ chỗ, hệ thống gửi cảnh báo vượt ngân sách cho nhóm quản lý ngân sách, như các loại thưởng khác |
| **CN01-BR11** | Khoản đã ghi 0 điểm do vượt ngân sách vẫn là 0 điểm khi BTC tăng ngân sách. Muốn trả phần điểm đó cần xử lý riêng ngoài chức năng này |
| **CN01-BR12** | **Kích hoạt sự kiện**: mỗi nguồn sự kiện nhận bài cần có ít nhất một nhiệm vụ đang bật thuộc loại **thưởng theo thông số** (lượt xem, thích, bình luận) **hoặc** loại **Cố định mỗi bài được duyệt**. Sự kiện chỉ có nhiệm vụ cố định mỗi bài vẫn kích hoạt được. Nguồn không có nhiệm vụ nào thuộc hai loại này thì không kích hoạt được và báo rõ nguồn thiếu nhiệm vụ |

## CN-01.7 Cấu hình ở Admin

**Đường dẫn:** Admin › Sự kiện › chọn sự kiện › tab **Nhiệm vụ** › Tạo.

| Ô | Nội dung | Ví dụ |
|---|---|---|
| Loại | Cố định mỗi bài được duyệt | |
| Tiêu đề | Tên nhiệm vụ | Thưởng mỗi bài |
| Thời gian | Khoảng ngày hiệu lực (CN01-BR04) | 16/11 đến 31/12 |
| Áp dụng cho các source | Các nguồn được tính | TikTok, Facebook Post, Facebook Reels |
| Thưởng mỗi bài (từng nguồn) | Mỗi nguồn đã chọn có một ô nhập riêng; để trống hoặc 0 thì nguồn đó không được thưởng | TikTok 50, Facebook Reels 50, Facebook Post 25 |
| Không giới hạn số lượng / Số lượng | Số suất (CN01-BR08) | Không giới hạn |

- Sau khi tạo, bật nhiệm vụ (đổi trạng thái sang hoạt động) thì nhiệm vụ mới có hiệu lực.
- Sửa mức điểm chỉ áp cho khoản tạo sau lúc sửa. Khoản đã tạo giữ nguyên điểm.
- Ngân sách ba tầng cấu hình ở tab **Ngân sách** của sự kiện. Để trống là không giới hạn.
- Cách đặt điểm bài post và video theo thể lệ: xem [Nền tảng và loại bài](./ref-nen-tang-loai-bai.md).

## CN-01.8 Kịch bản kiểm thử

**Dữ liệu chung:** sự kiện đang chạy nhận TikTok, Facebook Post, Facebook Reels, Instagram. Một nhiệm vụ Cố định mỗi bài được duyệt hiệu lực hôm nay, không giới hạn số lượng, mức TikTok 50, Facebook Reels 50, Facebook Post 25, Instagram để trống. Hai người tham gia U1, U2. Không đặt ngân sách trừ khi kịch bản nói khác.

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN01-TC01 | Bài chờ duyệt có khoản | U1 gửi 1 video TikTok, chưa duyệt | 1 khoản 50 điểm **Chờ duyệt**; Danh sách bài đăng hiện 50 điểm chờ duyệt | BR01, 02 |
| CN01-TC02 | Duyệt bài | Duyệt bài ở TC01 | Cùng khoản chuyển **Chờ đối soát**, vẫn 1 khoản | BR03 |
| CN01-TC03 | Mức theo nguồn | Duyệt một bài Facebook Post | Khoản 25 điểm | BR01 |
| CN01-TC04 | Nguồn không có mức | U1 gửi 1 bài Instagram, duyệt | Không có khoản | BR01 |
| CN01-TC05 | Duyệt lặp | Bấm duyệt thêm lần nữa trên bài đã duyệt; hai BTC duyệt cùng lúc | Vẫn 1 khoản | BR03 |
| CN01-TC06 | Từ chối khi chưa đối soát | Từ chối bài đã duyệt (khoản Chờ đối soát) | Khoản **Từ chối**; bài không hiện điểm; không tính vào ngân sách | CN-01.4 |
| CN01-TC07 | Duyệt lại sau từ chối chưa đối soát | Duyệt lại bài ở TC06 | Khoản cũ về **Chờ đối soát**, không có khoản mới | CN-01.4 |
| CN01-TC08 | Từ chối khi đã đối soát | Bài có khoản Đã hoàn thành, từ chối bài | Khoản giữ nguyên Đã hoàn thành | CN-01.4 |
| CN01-TC09 | Duyệt lại sau từ chối đã đối soát | Duyệt lại bài ở TC08 | Không tạo hay sửa khoản nào | CN-01.4 |
| CN01-TC10 | Nhiều bài một người | U1 có 4 video TikTok và 2 bài Facebook Post, duyệt hết | 6 khoản, tổng 250 điểm | BR06 |
| CN01-TC11 | Thời hạn theo ngày đăng | Nhiệm vụ hiệu lực 01/12–31/12; bài nộp 16/11 nhưng đăng lên nền tảng ngày 05/12 | Bài có khoản | BR04 |
| CN01-TC12 | Ngày đăng ngoài thời hạn | Như TC11 nhưng bài đăng ngày 20/11 | Không có khoản | BR04 |
| CN01-TC13 | Ngày đăng thật ngoài thời hạn | Bài chưa có ngày đăng (tạm tính ngày nộp, trong thời hạn) có khoản Chờ duyệt; sau đó lấy được ngày đăng ngoài thời hạn | Khoản chuyển **Từ chối** | BR04 |
| CN01-TC14 | Hết suất | Nhiệm vụ Số lượng = 3, duyệt 4 bài | Bài thứ 4 không có khoản | BR08 |
| CN01-TC15 | Ngân sách chiến dịch | Ngân sách chiến dịch 120; duyệt 3 video TikTok | Bài 1, 2: 50 điểm; bài 3: 0 điểm có cờ vượt ngân sách; có cảnh báo | BR09, 10 |
| CN01-TC16 | Bài chờ duyệt giữ chỗ ngân sách | Ngân sách chiến dịch 60; bài A chờ duyệt (50), bài B duyệt sau | Bài B: 0 điểm có cờ (chỗ đã bị bài A giữ) | BR09 |
| CN01-TC17 | Ngân sách creator | Ngân sách creator 70; U1 2 video, U2 1 video | U1: 50 rồi 0 điểm; U2: 50 điểm | BR09 |
| CN01-TC18 | Ngân sách nội dung | Ngân sách nội dung 60; hai nhiệm vụ cố định cùng áp một bài | Một khoản 50, một khoản 0 điểm có cờ | BR09 |
| CN01-TC19 | Tăng ngân sách | Sau TC15 tăng ngân sách chiến dịch lên 200 | Khoản 0 điểm của bài 3 vẫn 0 điểm | BR11 |
| CN01-TC20 | Sửa mức điểm | Sửa mức TikTok từ 50 lên 60, gửi video mới | Khoản cũ 50, khoản mới 60 | CN-01.7 |
| CN01-TC21 | Thông báo | Duyệt một bài | Người tham gia nhận thông báo bài được duyệt; không có thông báo thưởng mới lúc tạo khoản | CN-01.2 |
| CN01-TC22 | Hồi quy thưởng cũ | Sự kiện còn nhiệm vụ theo thông số và theo mốc | Hai loại cũ tính như trước | |
| CN01-TC23 | Kích hoạt chỉ có nhiệm vụ cố định | Sự kiện nhận TikTok, chỉ có nhiệm vụ Cố định mỗi bài được duyệt đang bật, bấm kích hoạt | Kích hoạt được | BR12 |
| CN01-TC24 | Nguồn thiếu nhiệm vụ | Sự kiện nhận TikTok và Facebook Post; chỉ có nhiệm vụ cố định cho TikTok, bấm kích hoạt | Không kích hoạt được, báo thiếu nhiệm vụ cho Facebook Post | BR12 |
