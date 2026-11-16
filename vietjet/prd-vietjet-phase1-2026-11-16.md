# Product Requirements Document: Chiến binh Vietjet Hybrid — Phase 1

**Date:** 2026-11-16
**Author:** Vinh Nguyễn
**Version:** 0.1
**Status:** Draft — đã có CN-01, các chức năng còn lại bổ sung sau
**Phạm vi:** App người tham gia (Ambassador Vietjet) và Admin.

---

## Document Overview

PRD cho phase 1 của chương trình **Chiến binh Vietjet Hybrid**: cán bộ nhân viên Vietjet đăng bài lên mạng xã hội, gửi link về hệ thống, BTC duyệt, người tham gia tích điểm và nhận thưởng theo tổng điểm cuối kỳ.

Tài liệu viết cho business và QC: mô tả hệ thống **làm gì**, có ví dụ, có bảng kịch bản kiểm thử. **Mỗi chức năng là một mục lớn có mã riêng** (CN-01, CN-02...), các mục con của chức năng nằm trong mục đó.

### Các chức năng của phase 1

| Mã | Chức năng | Việc trong sheet theo dõi | Trạng thái tài liệu |
|---|---|---|---|
| **CN-01** | **Điểm cố định cho mỗi bài được duyệt** | T03 | **Đã viết** |
| CN-02 | Hiển thị "điểm" thay cho "đ", ẩn màn rút tiền nếu điểm không rút được | T09, T10, T11 | Chưa viết |
| CN-03 | Kiểm tra bài (hashtag, bài trùng, bài còn công khai, quy trình duyệt) | T05–T08 | Chưa viết |
| CN-04 | Thưởng bổ sung hàng tháng cho TOP 1, 2, 3 | T12, T13 | Chưa viết |
| CN-05 | Thưởng theo mốc điểm cuối kỳ (mức 1–4, nhận cộng dồn, hết suất) | T14–T17, T21 | Chưa viết |
| CN-06 | Đối soát và chi trả cuối kỳ (kiểm thưởng cuối kỳ, danh sách trao quà, đánh dấu reset, thu hồi) | T18–T20, T22 | Chưa viết |

### Quy ước mã (để tham chiếu từ tài liệu khác)

| Loại | Dạng mã | Ví dụ |
|---|---|---|
| Chức năng | `CN-xx` | CN-01 |
| Mục con của chức năng | `CN-xx.y` | CN-01.5 là Quy tắc nghiệp vụ của CN-01 |
| Quy tắc nghiệp vụ | `CNxx-BRnn` | CN01-BR09 là quy tắc ngân sách ba tầng |
| Kịch bản kiểm thử | `CNxx-TCnn` | CN01-TC10 là kịch bản ngân sách chiến dịch |

Khi tham chiếu từ tài liệu khác, ghi mã đầy đủ (ví dụ "CN01-BR09"), không ghi số rời.

**Related Documents:**
- Thể lệ chương trình (bản gốc): https://docs.google.com/document/d/1F9rp4qd4KlchqKSQSZj4wzlScA_17utaqg996wBGnko/edit?tab=t.0
- Sheet theo dõi: thể lệ chia theo từng thông tin, việc cần làm, câu hỏi còn mở, timeline: https://claude.ai/artifact/MzAB58G2e4KSd33PjguXqW

---

## Thuật ngữ chung

| Thuật ngữ | Định nghĩa |
|---|---|
| **Điểm** | Đơn vị thưởng của chương trình. Trong hệ thống **1 điểm = 1 đ**; chỉ khác cách hiển thị (đổi chữ ở CN-02). Đến lúc đó màn hình vẫn ghi "đ" |
| **Bài** | Một bài đăng hoặc video người tham gia gửi link về hệ thống. Trong Admin gọi là nội dung |
| **Nguồn** | Nền tảng của bài: TikTok, Facebook Post, Facebook Reels, Instagram, YouTube... |
| **Duyệt** | BTC chuyển bài sang trạng thái **đã duyệt** ở Admin. Bài chưa duyệt hoặc bị từ chối không được thưởng |
| **Nhiệm vụ** | Một quy tắc thưởng của sự kiện. Trong Admin là tab **Nhiệm vụ** của sự kiện. CN-01 thêm một loại nhiệm vụ mới: **Cố định mỗi bài được duyệt** |
| **Khoản thưởng** | Một dòng thưởng của một người cho một bài, trạng thái "chờ đối soát" cho tới khi đối soát xong |
| **Đối soát** | Admin › Đối soát: tạo kỳ, lấy danh sách, duyệt; duyệt xong hệ thống cộng tiền (điểm) vào số dư người tham gia |
| **Ngân sách** | Ba hạn mức của sự kiện: **chiến dịch**, **creator** (mỗi người tham gia), **nội dung** (mỗi bài). Cấu hình ở tab Ngân sách |
| **Số suất** | Giới hạn tổng số khoản mà một nhiệm vụ được trả (ô "Số lượng") |

---

## CN-01 · Điểm cố định cho mỗi bài được duyệt

**Việc theo dõi:** T03.

### CN-01.1 Tóm tắt

Thể lệ: mỗi bài đạt chuẩn và được BTC duyệt được **một số điểm cố định theo loại bài** (bài post hoặc video), **không phụ thuộc lượt xem**.

```
Người tham gia đăng bài, gửi link về hệ thống
  → BTC duyệt bài
  → hệ thống tạo ngay một khoản thưởng cố định cho bài đó (chờ đối soát)
  → thẻ bài hiện số điểm nhận được
  → đến kỳ đối soát: mỗi khoản là một dòng, BTC duyệt, điểm vào số dư người tham gia
```

Ví dụ với bảng điểm TikTok 50, Facebook Reels 50, Facebook Post 25: nhân viên đăng 4 video TikTok và 2 bài Facebook Post, BTC duyệt cả 6 bài → 6 khoản thưởng riêng, tổng 4 × 50 + 2 × 25 = **250 điểm**. Video có 10 hay 10.000 lượt xem đều được đúng 50 điểm.

### CN-01.2 Bối cảnh

#### CN-01.2.1 Hiện trạng

Hệ thống chỉ có hai cách thưởng: **theo thông số** (lượt xem, thích, bình luận, tính theo từng ngày) và **theo mốc** (đủ số bài hoặc số lượt xem thì thưởng một lần cho mỗi người). Chưa có cách thưởng cố định cho từng bài.

#### CN-01.2.2 Bảng điểm chưa chốt

Thể lệ ghi hai bảng khác nhau:

| | Mục II.1 | Mục IV.5 |
|---|---|---|
| Bài post | 25 điểm | 50 điểm |
| Video TikTok / Reels | 50 điểm | 100 điểm |

Vì vậy **mức điểm không cố định trong hệ thống**: BTC nhập theo từng nguồn ở Admin, đổi được bất cứ lúc nào. Câu trả lời cho câu hỏi Q4 chỉ quyết định con số nhập vào, không làm thay đổi cách chạy. Các ví dụ trong tài liệu này dùng 25/50 chỉ để minh họa.

### CN-01.3 Nền tảng, loại bài và cách đặt điểm

Thể lệ cho điểm khác nhau giữa **bài post** và **video**. Hệ thống phân loại bài theo **nền tảng và loại bài** (gọi chung là *nguồn*) và đã có sẵn việc này, không làm thêm. Mức điểm đặt theo **nguồn**, nên "post" hay "video" do mức điểm của nguồn đó quyết định.

#### CN-01.3.1 Nền tảng và loại bài hệ thống có

| Nền tảng | Loại bài (nguồn) | Ghi chú |
|---|---|---|
| TikTok | Video | |
| YouTube | Video thường | |
| YouTube | Shorts (video ngắn) | Là nguồn riêng, đặt mức điểm riêng |
| Facebook | Video | Tự chuyển sang Reels nếu link khớp mẫu Reels (CN01-BR17) |
| Facebook | Reels | Là nguồn riêng |
| Facebook | Bài post (ảnh, chữ) | Là nguồn riêng |
| Instagram | Bài ảnh và Reels | **Gộp chung một nguồn**, chỉ đặt được một mức điểm cho cả hai |
| Threads | Bài viết | |
| Shopee | Video | |

#### CN-01.3.2 Cách đặt điểm bài post và video theo thể lệ

Thể lệ có hai mức: **bài post** và **video TikTok/Reels**. Hệ thống không có ô "post" hay "video", chỉ có ô theo nguồn, nên nhập mức của loại nào vào đúng nguồn thuộc loại đó. Chỉ cần **một** nhiệm vụ Cố định mỗi bài được duyệt cho cả hai loại. Không tạo hai nhiệm vụ riêng cho post và video, vì hai nhiệm vụ cùng áp một nguồn sẽ cộng điểm hai lần cho một bài.

| Loại theo thể lệ | Nguồn trong hệ thống | Nhập mức | Ví dụ (bảng 25/50) |
|---|---|---|---|
| Bài post | Facebook Post | Mức post | 25 |
| Video TikTok / Reels | TikTok, Facebook Reels | Mức video | 50 |
| Video Facebook thường | Facebook | Mức video (link khớp Reels sẽ tự tính theo Reels) | 50 |
| Bài ảnh và Reels Instagram | Instagram | Chỉ một mức, chọn mức post hoặc video, chờ chốt (Q14) | Chờ chốt |
| Nền tảng khác (YouTube, YouTube Shorts, Threads, Shopee) | Từng nguồn | Chỉ nhập khi BTC chấp thuận nền tảng đó; để trống thì không được thưởng | |

Các bước: Admin › Sự kiện › tab Nhiệm vụ › Tạo nhiệm vụ Cố định mỗi bài được duyệt › chọn các nguồn ở ô "Áp dụng cho các source" › nhập mức cho từng nguồn như bảng trên. Sự kiện cần nhận **cả Facebook và Facebook Reels** (CN01-BR18).

#### CN-01.3.3 Cách hệ thống nhận biết loại bài (hành vi có sẵn)

| # | Quy tắc |
|---|---|
| **CN01-BR15** | Người tham gia chọn **nguồn** của bài khi gửi (trong danh sách nguồn mà sự kiện nhận), rồi dán link. Hệ thống không đoán loại bài từ nội dung bài |
| **CN01-BR16** | Hệ thống kiểm **link khớp với nguồn đã chọn**. Mỗi nguồn có mẫu link riêng; link không khớp thì bị từ chối |
| **CN01-BR17** | **Facebook, tự chuyển sang Reels:** người tham gia chọn nguồn Facebook (video) mà link cũng khớp mẫu Reels thì bài được lưu là **Facebook Reels** và tính điểm theo nguồn Reels. Đây là chỗ **duy nhất** hệ thống tự đổi nguồn |
| **CN01-BR18** | Hệ quả của CN01-BR17: sự kiện nhận Facebook mà **không nhận Facebook Reels** thì link rơi vào trường hợp Reels bị từ chối với thông báo "Chương trình chỉ chấp nhận bài đăng ...". Sự kiện Vietjet cần nhận **cả Facebook và Facebook Reels** |
| **CN01-BR19** | YouTube: chọn nguồn YouTube mà link là Shorts thì bị từ chối, phải gửi bằng nguồn YouTube Shorts (không tự chuyển). Hệ thống phải hỏi YouTube để biết link có phải Shorts; nếu hỏi không được thì báo thử lại, không coi là video thường |
| **CN01-BR20** | Facebook post: không tự chuyển, chỉ kiểm link có đúng mẫu bài post (bài đăng, ảnh, permalink, chia sẻ) |
| **CN01-BR21** | Instagram: một nguồn nhận cả link bài ảnh lẫn link Reels, nên không phân biệt được hai loại và cùng một mức điểm |
| **CN01-BR22** | Nguồn mà sự kiện **không nhận** thì người tham gia không chọn được. Nguồn nhận nhưng nhiệm vụ chưa nhập mức điểm thì bài vẫn gửi được nhưng **không được thưởng** (CN01-BR02) |

#### CN-01.3.4 Hashtag chương trình (hành vi có sẵn)

Thể lệ bắt buộc bài có #Vietjet và #ChienBinhVietjetHybrid. Hệ thống đã có sẵn việc kiểm này, không làm thêm.

| # | Quy tắc |
|---|---|
| **CN01-BR23** | Hashtag của chương trình do BTC **điền ở cấu hình sự kiện** (ô Hashtag). Khi người tham gia gửi bài, hệ thống kiểm bài có đủ các hashtag đó; thiếu thì từ chối và nêu hashtag còn thiếu ("Nội dung không có chứa đầy đủ hashtag của chương trình: …") |
| **CN01-BR24** | Kiểm **không phân biệt chữ hoa, chữ thường** |

### CN-01.4 Phạm vi

**Nguyên tắc: chỉ thêm một loại nhiệm vụ thưởng mới và cho nó vận hành như các loại thưởng hiện có. Chức năng hệ thống cũ chưa có thì không tự thêm, làm chung ở đợt nâng cấp sau.**

#### CN-01.4.1 Trong phạm vi

- Loại nhiệm vụ **Cố định mỗi bài được duyệt**, điểm nhập theo từng nguồn.
- Tạo đúng một khoản thưởng khi bài được duyệt; đóng khoản khi bài bị từ chối.
- Số suất và thời hạn của nhiệm vụ.
- Ngân sách ba tầng như các loại thưởng khác.
- Thẻ bài hiện số điểm nhận được.
- Đối soát: đi cùng luồng thưởng theo mốc (tab Milestone), mỗi bài một dòng.
- Admin: form nhập điểm theo nguồn; bảng nhiệm vụ hiện điểm theo nguồn.

#### CN-01.4.2 Không bao gồm (thể lệ không yêu cầu, chưa làm)

| Nội dung | Cách xử lý hiện tại |
|---|---|
| **Chia nhỏ khoản khi ngân sách chỉ còn một phần** | Làm **theo cách của loại thưởng theo mốc**: không chia nhỏ. Thiếu chỗ ở bất kỳ tầng ngân sách nào thì khoản ghi **0 điểm** kèm cờ vượt ngân sách (xem CN01-BR09). Chỉ thưởng theo lượt xem mới chia nhỏ được |
| **Giới hạn số bài được tính điểm mỗi người mỗi ngày** | Không làm. Quyết định: không giới hạn. Thể lệ không nêu và hệ thống cũ cũng không có |
| **Tự tính lại khoản 0 điểm khi ngân sách được bơm thêm** | Hệ thống cũ chưa có (thưởng theo mốc cũng không). Khoản 0 điểm giữ nguyên. Làm chung ở đợt nâng cấp sau |
| **Thông báo thưởng mới cho người tham gia** | **Không thêm.** Người tham gia đã nhận thông báo "bài được duyệt" khi BTC duyệt. Khi đối soát chi xong họ nhận thông báo thưởng như các khoản theo mốc |

#### CN-01.4.3 Chờ quyết định (chưa làm cho tới khi có câu trả lời)

| Nội dung | Câu hỏi |
|---|---|
| Bảng điểm đúng là 25/50 hay 50/100 | Q4 |
| Nền tảng nào được tính (Instagram ảnh, YouTube Shorts, Threads) | Q14 |

### CN-01.5 Quy tắc nghiệp vụ

| # | Quy tắc |
|---|---|
| **CN01-BR01** | Loại nhiệm vụ **Cố định mỗi bài được duyệt** trả một số điểm cố định cho mỗi bài được duyệt, không phụ thuộc lượt xem, thích, bình luận |
| **CN01-BR02** | Điểm theo **nguồn** của bài. Nguồn không có mức, mức bằng 0 hoặc mức âm thì bài đó **không được thưởng**. Nếu nhiệm vụ giới hạn nguồn ở ô "Áp dụng cho các source" thì bài thuộc nguồn ngoài danh sách cũng không được thưởng |
| **CN01-BR03** | Chỉ bài ở trạng thái **đã duyệt** mới có khoản thưởng. Bài chờ duyệt hoặc bị từ chối thì không |
| **CN01-BR04** | Mỗi bài chỉ có **đúng một khoản** cho mỗi nhiệm vụ. Duyệt lại, đổi trạng thái lặp lại, hoặc nhiều người duyệt cùng lúc đều không tạo thêm khoản |
| **CN01-BR05** | Bài bị từ chối thì khoản **chưa đối soát** của bài đó chuyển sang từ chối, thẻ bài không còn hiện điểm. Khoản đã đối soát xong thì giữ nguyên. Bài được duyệt lại sau đó thì sinh **khoản mới** |
| **CN01-BR06** | Thời hạn nhiệm vụ tính theo **ngày gửi link** của bài (ngày người tham gia nộp bài vào hệ thống): nằm trong khoảng bắt đầu – kết thúc thì được thưởng, ngoài khoảng thì không |
| **CN01-BR07** | **Số suất**: nếu nhiệm vụ không để "Không giới hạn số lượng" thì tổng số khoản được trả không vượt số lượng. Hết suất thì bài duyệt sau không được thưởng |
| **CN01-BR08** | Mọi bài của cùng một người đều được thưởng. Ô "tối đa mỗi người" của nhiệm vụ **không áp dụng** cho loại này |
| **CN01-BR09** | **Ngân sách ba tầng**: khoản được tính vào ngân sách **chiến dịch**, **creator** và **nội dung** (mỗi bài). Nếu **bất kỳ tầng nào** không đủ chỗ cho cả khoản thì khoản được ghi **0 điểm** và gắn cờ vượt ngân sách (không trả thiếu một phần). Số điểm định thưởng vẫn được lưu để biết đã bỏ lỡ bao nhiêu. Khi thiếu ở tầng chiến dịch, hệ thống còn gửi cảnh báo vượt ngân sách như các loại thưởng khác. Làm theo cách của loại thưởng theo mốc |
| **CN01-BR10** | Khoản 0 điểm không tự được tính lại khi ngân sách tăng (xem CN-01.4.2) |
| **CN01-BR11** | Thẻ bài hiện số điểm **chờ đối soát** (và số đã nhận sau đối soát) của bài đó |
| **CN01-BR12** | **Đối soát, lấy danh sách**: khoản có điểm và bài còn được duyệt thì thành một dòng ở tab **Milestone**, mỗi bài một dòng (một người có hai bài thì có hai dòng), cột ghi chú có link bài. Khoản 0 điểm và khoản của bài không còn được duyệt thì **không** vào danh sách |
| **CN01-BR13** | **Đối soát, chạy chi**: kiểm lại bài vẫn được duyệt. Bài bị từ chối sau lúc lập bản thì dòng đó bị từ chối ("Thông tin nội dung không chính xác") và không chi. Khoản được chi thì chuyển sang đã hoàn thành |
| **CN01-BR14** | Điểm hiển thị bằng chữ "đ" cho tới khi làm CN-02 |

### CN-01.6 Cấu hình ở Admin (để QC dựng dữ liệu thử)

**Đường dẫn:** Admin › Sự kiện › chọn sự kiện › tab **Nhiệm vụ** › Tạo.

| Ô | Điền gì | Ví dụ |
|---|---|---|
| Loại | **Cố định mỗi bài được duyệt** | |
| Tiêu đề | Tên nhiệm vụ | Thưởng mỗi bài |
| Thời gian | Khoảng ngày hiệu lực (xem CN01-BR06) | 16/11 đến 31/12 |
| Áp dụng cho các source | Các nguồn được tính | TikTok, Facebook Post, Facebook Reels |
| **Thưởng mỗi bài (từng nguồn)** | Mỗi nguồn đã chọn có một ô riêng; để trống hoặc 0 thì nguồn đó không được thưởng | TikTok 50, Facebook Reels 50, Facebook Post 25 |
| Không giới hạn số lượng / Số lượng | Số suất (CN01-BR07) | Không giới hạn |

Sau khi tạo, **bật** nhiệm vụ (đổi trạng thái sang hoạt động), thì mới có hiệu lực.

**Điều kiện kích hoạt sự kiện (đã có sẵn, không đổi):** hệ thống chỉ cho kích hoạt sự kiện khi **mỗi nguồn nhận bài** có ít nhất một nhiệm vụ **theo thông số** đang bật. Vì vậy sự kiện Vietjet cần thêm một nhiệm vụ theo thông số cho các nguồn đó (có thể để mức thưởng 0). Nếu thiếu, hệ thống báo "Chưa cấu hình nhiệm vụ thưởng theo thông số cho nguồn …".

**Ngân sách:** tab Ngân sách của sự kiện có ba ô Ngân sách/Chiến dịch, Ngân sách/Creator, Ngân sách/Nội dung. Để trống nghĩa là không giới hạn.

**Sửa mức điểm:** chỉ áp cho bài được duyệt **sau lúc sửa**. Khoản đã tạo giữ nguyên số điểm.

### CN-01.7 Luồng

#### CN-01.7.1 Người tham gia

1. Đăng bài lên mạng xã hội, gửi link vào hệ thống. Bài ở trạng thái chờ duyệt, chưa có điểm.
2. BTC duyệt → người tham gia nhận thông báo "bài được duyệt", thẻ bài hiện điểm chờ đối soát.
3. Đối soát chi xong → nhận thông báo thưởng, điểm vào số dư.

#### CN-01.7.2 BTC

1. Duyệt bài ở Admin. Hệ thống tự tạo khoản, BTC không phải nhập gì.
2. Đến kỳ: Admin › Đối soát › tạo kỳ cho sự kiện › **Lấy danh sách** › xem tab **Milestone** (mỗi bài một dòng) › **Duyệt**.
3. Bài bị từ chối ở bất kỳ lúc nào trước khi chi thì khoản của bài không được chi (CN01-BR05, CN01-BR13).

### CN-01.8 Kịch bản kiểm thử (QC)

**Dữ liệu chung:** một sự kiện đang chạy, nguồn nhận bài TikTok, Facebook Post, Facebook Reels, Instagram; một nhiệm vụ **theo thông số** (để kích hoạt được sự kiện, mức 0); một nhiệm vụ **Cố định mỗi bài được duyệt** hiệu lực hôm nay, không giới hạn số lượng, mức TikTok 50, Facebook Reels 50, Facebook Post 25, **Instagram để trống**; hai người tham gia U1, U2; không đặt ngân sách trừ khi kịch bản nói khác.

| # | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN01-TC01 | Video TikTok được duyệt | U1 gửi 1 video TikTok, BTC duyệt | 1 khoản **50 điểm**, chờ đối soát; thẻ bài hiện 50 | 01, 02, 11 |
| CN01-TC02 | Bài Facebook Post được duyệt | U1 gửi 1 bài Facebook Post, BTC duyệt | 1 khoản **25 điểm** | 02 |
| CN01-TC03 | Nguồn không có mức | U1 gửi 1 bài Instagram, BTC duyệt | **Không** có khoản | 02 |
| CN01-TC04 | Bài chưa duyệt | U1 gửi 1 video TikTok, chưa duyệt | Không có khoản. Duyệt xong thì mới có 1 khoản 50 | 03 |
| CN01-TC05 | Duyệt lặp | Bài đã duyệt (có 1 khoản), BTC bấm duyệt thêm lần nữa; hoặc hai BTC bấm duyệt cùng lúc (không qua bước từ chối) | Vẫn **đúng 1 khoản** cho bài | 04 |
| CN01-TC06 | Bài bị từ chối rồi duyệt lại | Duyệt bài (có khoản 50), từ chối bài, rồi duyệt lại | Sau từ chối: khoản bị từ chối, thẻ bài không còn điểm. Sau duyệt lại: 1 khoản **mới** 50 còn hiệu lực, khoản cũ vẫn ở trạng thái từ chối | 05 |
| CN01-TC07 | Nhiều bài một người | U1 có 4 video TikTok và 2 bài Facebook Post, duyệt hết | 6 khoản, tổng **250 điểm**; không bị chặn ở bài thứ hai | 08 |
| CN01-TC08 | Ngoài thời hạn | Nhiệm vụ hiệu lực 01/12–31/12, gửi link ngày 16/11, duyệt | Không có khoản | 06 |
| CN01-TC09 | Hết suất | Nhiệm vụ Số lượng = 3. Duyệt 4 bài | Chỉ 3 bài đầu có khoản, bài thứ 4 **không** | 07 |
| CN01-TC10 | Ngân sách chiến dịch | Ngân sách/Chiến dịch = 120. Duyệt 3 video TikTok | Bài 1, 2: 50 điểm. Bài 3: **0 điểm** có cờ vượt ngân sách (chỉ còn 20); có cảnh báo vượt ngân sách | 09 |
| CN01-TC11 | Ngân sách creator | Ngân sách/Creator = 70. U1 duyệt 2 video, U2 duyệt 1 video | U1 bài 1: 50; U1 bài 2: **0** (còn 20); U2 bài 1: **50** (hạn mức của U2 độc lập) | 09 |
| CN01-TC12 | Ngân sách nội dung | Ngân sách/Nội dung = 60. Hai nhiệm vụ cố định cùng áp cho một bài TikTok 50 điểm. Duyệt bài | Một khoản 50 và một khoản **0** có cờ | 09 |
| CN01-TC13 | Không tự tính lại | Sau CN01-TC10, vào tab Ngân sách tăng Ngân sách/Chiến dịch lên 200, rồi duyệt thêm một bài khác | Khoản 0 điểm của bài 3 **vẫn 0**. Bài mới (còn chỗ) được 50 | 10 |
| CN01-TC14 | Đối soát, lấy danh sách | Có khoản 50, 25, một khoản 0 điểm, một khoản của bài đã bị từ chối. Tạo kỳ đối soát, Lấy danh sách | Tab Milestone chỉ có 2 dòng (50 và 25), mỗi dòng ghi chú có link bài. Hai bài cùng người vẫn là hai dòng riêng | 12 |
| CN01-TC15 | Đối soát, chạy chi | Duyệt kỳ ở CN01-TC14 | Hai khoản **đã hoàn thành**; số dư người tham gia tăng đúng 75; người nhận thông báo thưởng | 13 |
| CN01-TC16 | Bài bị huỷ sau lúc lập bản | Lấy danh sách có 1 dòng của bài X. Trước khi duyệt kỳ, từ chối bài X. Duyệt kỳ | Dòng của bài X bị từ chối ("Thông tin nội dung không chính xác"), **không chi**; dòng khác vẫn chi | 13 |
| CN01-TC17 | Thông báo | Duyệt một bài | Người tham gia nhận thông báo "bài được duyệt"; **không** có thông báo thưởng thêm lúc tạo khoản | CN-01.4.2 |
| CN01-TC18 | Cấu hình form | Tạo nhiệm vụ, chọn 3 nguồn | Có 3 ô "Thưởng mỗi bài" tương ứng; bảng nhiệm vụ hiện số nguồn, rê chuột ra danh sách điểm từng nguồn | CN-01.6 |
| CN01-TC19 | Sửa mức điểm | Khoản đã có 50. Sửa mức TikTok lên 60, duyệt một video mới | Khoản cũ vẫn 50; video mới 60 | CN-01.6 |
| CN01-TC20 | Hồi quy loại thưởng cũ | Sự kiện có thêm nhiệm vụ theo thông số và theo mốc đang chạy | Hai loại cũ tính như trước, không bị ảnh hưởng | 01 |
| CN01-TC21 | Mỗi nguồn một mức | Nhiệm vụ cố định: TikTok 50, Facebook Reels 50, Facebook Post 25. Duyệt một bài mỗi nguồn | TikTok 50, Facebook Reels 50, Facebook Post 25 | CN01-BR15, 16 |
| CN01-TC22 | Facebook tự chuyển Reels | Sự kiện nhận Facebook và Facebook Reels. Chọn nguồn Facebook, dán link dạng `facebook.com/watch/?v=…` | Bài được lưu ở nguồn **Facebook Reels**, thưởng theo mức Reels | CN01-BR17 |
| CN01-TC23 | Sự kiện không nhận Reels | Sự kiện nhận Facebook nhưng không nhận Facebook Reels. Làm như CN01-TC22 | Bị từ chối "Chương trình chỉ chấp nhận bài đăng …" | CN01-BR18 |
| CN01-TC24 | YouTube Shorts | Chọn nguồn YouTube, dán link Shorts | Bị từ chối, yêu cầu gửi bằng nguồn YouTube Shorts | CN01-BR19 |
| CN01-TC25 | Instagram gộp | Gửi một bài ảnh và một Reels Instagram, duyệt cả hai | Cả hai cùng một mức điểm của nguồn Instagram | CN01-BR21 |
| CN01-TC26 | Link không khớp nguồn | Chọn nguồn TikTok, dán link YouTube | Bị từ chối, không tạo bài | CN01-BR16 |
| CN01-TC27 | Nguồn sự kiện không nhận | Sự kiện chỉ nhận TikTok và Facebook Post | Người tham gia không chọn được nguồn khác | CN01-BR22 |
| CN01-TC28 | Nguồn chưa có mức | Nhận Instagram nhưng nhiệm vụ không nhập mức Instagram. Duyệt một bài Instagram | Bài được duyệt, **không** có khoản thưởng | CN01-BR22 |
| CN01-TC29 | Thiếu hashtag chương trình | Sự kiện điền hashtag #Vietjet và #ChienBinhVietjetHybrid. Gửi bài chỉ có #Vietjet | Bị từ chối, thông báo nêu thiếu #ChienBinhVietjetHybrid | CN01-BR23 |
| CN01-TC30 | Hashtag khác hoa thường | Gửi bài có #CHIENBINHVIETJETHYBRID và #vietjet | Được chấp nhận | CN01-BR24 |

### CN-01.9 Câu hỏi còn mở

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| Q4 | Bảng điểm 25/50 hay 50/100? | Con số BTC nhập ở CN-01.6. Không ảnh hưởng cách hệ thống chạy |
| Q14 | Nền tảng nào được tính (Instagram ảnh, YouTube Shorts, Threads)? | Nguồn nào được nhập mức ở CN-01.6 |
| Q17 | Ngày bắt đầu và kết thúc chương trình | Khoảng thời gian hiệu lực của nhiệm vụ (CN01-BR06) |
| (cần kiểm) | Một số dạng link khớp mẫu của nhiều nguồn Facebook cùng lúc (ví dụ link `watch/?v=` khớp cả Facebook và Reels; link `/ten/videos/…` hoặc `/ten/reels/…` khớp cả Facebook Post), nên người tham gia có thể chọn nguồn có điểm cao hơn cho cùng một link | Cần kiểm bằng link thật để biết dạng nào lọt, rồi quyết định có siết mẫu link không |

Danh sách đầy đủ các câu hỏi nằm trong sheet theo dõi (phần Related Documents).

---

## Tham chiếu triển khai

- Issue: diso-pmax/ambassador-vietjet#145. Mã nguồn: PR #146 (đã merge). Cách cấu hình chi tiết cho người vận hành: `docs/THUONG-THEO-BAI.md` trong repo ambassador-vietjet.
- Kiểm thử tự động của chức năng này nằm trong repo; bảng kịch bản kiểm thử ở CN-01.8 là kịch bản kiểm tay cho QC.
