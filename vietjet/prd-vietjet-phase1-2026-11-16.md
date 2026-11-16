# Product Requirements Document: Chiến binh Vietjet Hybrid — Phase 1

**Date:** 2026-11-16
**Author:** Vinh Nguyễn
**Version:** 0.1
**Status:** Draft — mới có chức năng 1, các chức năng còn lại bổ sung sau
**Phạm vi:** App người tham gia (Ambassador Vietjet) và Admin.

---

## Document Overview

PRD cho phase 1 của chương trình **Chiến binh Vietjet Hybrid**: cán bộ nhân viên Vietjet đăng bài lên mạng xã hội, gửi link về hệ thống, BTC duyệt, người tham gia tích điểm và nhận thưởng theo tổng điểm cuối kỳ.

Tài liệu viết cho business và QC: mô tả hệ thống **làm gì**, có ví dụ, có bảng kịch bản kiểm thử ở mục 7. Mỗi chức năng một mục lớn; hiện mới có **chức năng 1**.

### Các chức năng của phase 1

| # | Chức năng | Việc trong sheet theo dõi | Trạng thái tài liệu |
|---|---|---|---|
| **1** | **Điểm cố định cho mỗi bài được duyệt** | T03, T04 | **Có trong tài liệu này** |
| 2 | Hiển thị "điểm" thay cho "đ", ẩn màn rút tiền nếu điểm không rút được | T09, T10, T11 | Chưa viết |
| 3 | Kiểm tra bài (hashtag, bài trùng, bài còn công khai, quy trình duyệt) | T05–T08 | Chưa viết |
| 4 | Thưởng bổ sung hàng tháng cho TOP 1, 2, 3 | T12, T13 | Chưa viết |
| 5 | Thưởng theo mốc điểm cuối kỳ (mức 1–4, nhận cộng dồn, hết suất) | T14–T17, T21 | Chưa viết |
| 6 | Đối soát và chi trả cuối kỳ (kiểm thưởng cuối kỳ, danh sách trao quà, đánh dấu reset, thu hồi) | T18–T20, T22 | Chưa viết |

**Related Documents:**
- Thể lệ chương trình (bản gốc): https://docs.google.com/document/d/1F9rp4qd4KlchqKSQSZj4wzlScA_17utaqg996wBGnko/edit?tab=t.0
- Sheet theo dõi: thể lệ chia theo từng thông tin, việc cần làm, câu hỏi còn mở, timeline: https://claude.ai/artifact/MzAB58G2e4KSd33PjguXqW

---

## 0. Thuật ngữ

| Thuật ngữ | Định nghĩa |
|---|---|
| **Điểm** | Đơn vị thưởng của chương trình. Trong hệ thống **1 điểm = 1 đ**; chỉ khác cách hiển thị (đổi chữ ở chức năng 2). Đến lúc đó màn hình vẫn ghi "đ" |
| **Bài** | Một bài đăng hoặc video người tham gia gửi link về hệ thống. Trong Admin gọi là nội dung |
| **Nguồn** | Nền tảng của bài: TikTok, Facebook Post, Facebook Reels, Instagram, YouTube... |
| **Duyệt** | BTC chuyển bài sang trạng thái **đã duyệt** ở Admin. Bài chưa duyệt hoặc bị từ chối không được thưởng |
| **Nhiệm vụ** | Một quy tắc thưởng của sự kiện. Trong Admin là tab **Nhiệm vụ** của sự kiện. Chức năng 1 thêm một loại nhiệm vụ mới: **Cố định mỗi bài được duyệt** |
| **Khoản thưởng** | Một dòng thưởng của một người cho một bài, trạng thái "chờ đối soát" cho tới khi đối soát xong |
| **Đối soát** | Admin › Đối soát: tạo kỳ, lấy danh sách, duyệt; duyệt xong hệ thống cộng tiền (điểm) vào số dư người tham gia |
| **Ngân sách** | Ba hạn mức của sự kiện: **chiến dịch**, **creator** (mỗi người tham gia), **nội dung** (mỗi bài). Cấu hình ở tab Ngân sách |
| **Số suất** | Giới hạn tổng số khoản mà một nhiệm vụ được trả (ô "Số lượng") |

---

## 1. Chức năng 1 — Tóm tắt

Thể lệ: mỗi bài đạt chuẩn và được BTC duyệt được **một số điểm cố định theo loại bài** (bài post hoặc video), **không phụ thuộc lượt xem**.

```
Người tham gia đăng bài, gửi link về hệ thống
  → BTC duyệt bài
  → hệ thống tạo ngay một khoản thưởng cố định cho bài đó (chờ đối soát)
  → thẻ bài hiện số điểm nhận được
  → đến kỳ đối soát: mỗi khoản là một dòng, BTC duyệt, điểm vào số dư người tham gia
```

Ví dụ với bảng điểm TikTok 50, Facebook Reels 50, Facebook Post 25: nhân viên đăng 4 video TikTok và 2 bài Facebook Post, BTC duyệt cả 6 bài → 6 khoản thưởng riêng, tổng 4 × 50 + 2 × 25 = **250 điểm**. Video có 10 hay 10.000 lượt xem đều được đúng 50 điểm.

---

## 2. Bối cảnh

### 2.1 Hiện trạng

Hệ thống chỉ có hai cách thưởng: **theo thông số** (lượt xem, thích, bình luận, tính theo từng ngày) và **theo mốc** (đủ số bài hoặc số lượt xem thì thưởng một lần cho mỗi người). Chưa có cách thưởng cố định cho từng bài.

### 2.2 Bảng điểm chưa chốt

Thể lệ ghi hai bảng khác nhau:

| | Mục II.1 | Mục IV.5 |
|---|---|---|
| Bài post | 25 điểm | 50 điểm |
| Video TikTok / Reels | 50 điểm | 100 điểm |

Vì vậy **mức điểm không cố định trong hệ thống**: BTC nhập theo từng nguồn ở Admin, đổi được bất cứ lúc nào. Câu trả lời cho câu hỏi Q4 chỉ quyết định con số nhập vào, không làm thay đổi cách chạy. Các ví dụ trong tài liệu này dùng 25/50 chỉ để minh họa.

---

## 3. Phạm vi chức năng 1

**Nguyên tắc: chỉ thêm một loại nhiệm vụ thưởng mới và cho nó vận hành như các loại thưởng hiện có. Chức năng hệ thống cũ chưa có thì không tự thêm, làm chung ở đợt nâng cấp sau.**

### 3.1 Trong phạm vi

- Loại nhiệm vụ **Cố định mỗi bài được duyệt**, điểm nhập theo từng nguồn.
- Tạo đúng một khoản thưởng khi bài được duyệt; đóng khoản khi bài bị từ chối.
- Số suất và thời hạn của nhiệm vụ.
- Ngân sách ba tầng như các loại thưởng khác.
- Thẻ bài hiện số điểm nhận được.
- Đối soát: đi cùng luồng thưởng theo mốc (tab Milestone), mỗi bài một dòng.
- Admin: form nhập điểm theo nguồn; bảng nhiệm vụ hiện điểm theo nguồn.

### 3.2 Không bao gồm (thể lệ không yêu cầu, chưa làm)

| Nội dung | Cách xử lý hiện tại |
|---|---|
| **Chia nhỏ khoản khi ngân sách chỉ còn một phần** | Làm **theo cách của loại thưởng theo mốc**: không chia nhỏ. Thiếu chỗ ở bất kỳ tầng ngân sách nào thì khoản ghi **0 điểm** kèm cờ vượt ngân sách (xem BR-09). Chỉ thưởng theo lượt xem mới chia nhỏ được |
| **Tự tính lại khoản 0 điểm khi ngân sách được bơm thêm** | Hệ thống cũ chưa có (thưởng theo mốc cũng không). Khoản 0 điểm giữ nguyên. Làm chung ở đợt nâng cấp sau |
| **Thông báo thưởng mới cho người tham gia** | **Không thêm.** Người tham gia đã nhận thông báo "bài được duyệt" khi BTC duyệt. Khi đối soát chi xong họ nhận thông báo thưởng như các khoản theo mốc |

### 3.3 Chờ quyết định (chưa làm cho tới khi có câu trả lời)

| Nội dung | Câu hỏi |
|---|---|
| Giới hạn số bài được tính điểm mỗi người mỗi ngày (thể lệ không nêu, hệ thống cũ không có) | Q8 |
| Bảng điểm đúng là 25/50 hay 50/100 | Q4 |
| Nền tảng nào được tính (Instagram ảnh, YouTube Shorts, Threads) | Q14 |

---

## 4. Quy tắc nghiệp vụ

| # | Quy tắc |
|---|---|
| **BR-01** | Loại nhiệm vụ **Cố định mỗi bài được duyệt** trả một số điểm cố định cho mỗi bài được duyệt, không phụ thuộc lượt xem, thích, bình luận |
| **BR-02** | Điểm theo **nguồn** của bài. Nguồn không có mức, mức bằng 0 hoặc mức âm thì bài đó **không được thưởng**. Nếu nhiệm vụ giới hạn nguồn ở ô "Áp dụng cho các source" thì bài thuộc nguồn ngoài danh sách cũng không được thưởng |
| **BR-03** | Chỉ bài ở trạng thái **đã duyệt** mới có khoản thưởng. Bài chờ duyệt hoặc bị từ chối thì không |
| **BR-04** | Mỗi bài chỉ có **đúng một khoản** cho mỗi nhiệm vụ. Duyệt lại, đổi trạng thái lặp lại, hoặc nhiều người duyệt cùng lúc đều không tạo thêm khoản |
| **BR-05** | Bài bị từ chối thì khoản **chưa đối soát** của bài đó chuyển sang từ chối, thẻ bài không còn hiện điểm. Khoản đã đối soát xong thì giữ nguyên. Bài được duyệt lại sau đó thì sinh **khoản mới** |
| **BR-06** | Thời hạn nhiệm vụ tính theo **ngày gửi link** của bài (ngày người tham gia nộp bài vào hệ thống): nằm trong khoảng bắt đầu – kết thúc thì được thưởng, ngoài khoảng thì không |
| **BR-07** | **Số suất**: nếu nhiệm vụ không để "Không giới hạn số lượng" thì tổng số khoản được trả không vượt số lượng. Hết suất thì bài duyệt sau không được thưởng |
| **BR-08** | Mọi bài của cùng một người đều được thưởng. Ô "tối đa mỗi người" của nhiệm vụ **không áp dụng** cho loại này |
| **BR-09** | **Ngân sách ba tầng**: khoản được tính vào ngân sách **chiến dịch**, **creator** và **nội dung** (mỗi bài). Nếu **bất kỳ tầng nào** không đủ chỗ cho cả khoản thì khoản được ghi **0 điểm** và gắn cờ vượt ngân sách (không trả thiếu một phần). Số điểm định thưởng vẫn được lưu để biết đã bỏ lỡ bao nhiêu. Khi thiếu ở tầng chiến dịch, hệ thống còn gửi cảnh báo vượt ngân sách như các loại thưởng khác. Làm theo cách của loại thưởng theo mốc |
| **BR-10** | Khoản 0 điểm không tự được tính lại khi ngân sách tăng (xem 3.2 Không bao gồm) |
| **BR-11** | Thẻ bài hiện số điểm **chờ đối soát** (và số đã nhận sau đối soát) của bài đó |
| **BR-12** | **Đối soát, lấy danh sách**: khoản có điểm và bài còn được duyệt thì thành một dòng ở tab **Milestone**, mỗi bài một dòng (một người có hai bài thì có hai dòng), cột ghi chú có link bài. Khoản 0 điểm và khoản của bài không còn được duyệt thì **không** vào danh sách |
| **BR-13** | **Đối soát, chạy chi**: kiểm lại bài vẫn được duyệt. Bài bị từ chối sau lúc lập bản thì dòng đó bị từ chối ("Thông tin nội dung không chính xác") và không chi. Khoản được chi thì chuyển sang đã hoàn thành |
| **BR-14** | Điểm hiển thị bằng chữ "đ" cho tới khi làm chức năng 2 |

---

## 5. Cấu hình ở Admin (để QC dựng dữ liệu thử)

**Đường dẫn:** Admin › Sự kiện › chọn sự kiện › tab **Nhiệm vụ** › Tạo.

| Ô | Điền gì | Ví dụ |
|---|---|---|
| Loại | **Cố định mỗi bài được duyệt** | |
| Tiêu đề | Tên nhiệm vụ | Thưởng mỗi bài |
| Thời gian | Khoảng ngày hiệu lực (xem BR-06) | 16/11 đến 31/12 |
| Áp dụng cho các source | Các nguồn được tính | TikTok, Facebook Post, Facebook Reels |
| **Thưởng mỗi bài (từng nguồn)** | Mỗi nguồn đã chọn có một ô riêng; để trống hoặc 0 thì nguồn đó không được thưởng | TikTok 50, Facebook Reels 50, Facebook Post 25 |
| Không giới hạn số lượng / Số lượng | Số suất (BR-07) | Không giới hạn |

Sau khi tạo, **bật** nhiệm vụ (đổi trạng thái sang hoạt động), thì mới có hiệu lực.

**Điều kiện kích hoạt sự kiện (đã có sẵn, không đổi):** hệ thống chỉ cho kích hoạt sự kiện khi **mỗi nguồn nhận bài** có ít nhất một nhiệm vụ **theo thông số** đang bật. Vì vậy sự kiện Vietjet cần thêm một nhiệm vụ theo thông số cho các nguồn đó (có thể để mức thưởng 0). Nếu thiếu, hệ thống báo "Chưa cấu hình nhiệm vụ thưởng theo thông số cho nguồn …".

**Ngân sách:** tab Ngân sách của sự kiện có ba ô Ngân sách/Chiến dịch, Ngân sách/Creator, Ngân sách/Nội dung. Để trống nghĩa là không giới hạn.

**Sửa mức điểm:** chỉ áp cho bài được duyệt **sau lúc sửa**. Khoản đã tạo giữ nguyên số điểm.

---

## 6. Luồng

### 6.1 Người tham gia

1. Đăng bài lên mạng xã hội, gửi link vào hệ thống. Bài ở trạng thái chờ duyệt, chưa có điểm.
2. BTC duyệt → người tham gia nhận thông báo "bài được duyệt", thẻ bài hiện điểm chờ đối soát.
3. Đối soát chi xong → nhận thông báo thưởng, điểm vào số dư.

### 6.2 BTC

1. Duyệt bài ở Admin. Hệ thống tự tạo khoản, BTC không phải nhập gì.
2. Đến kỳ: Admin › Đối soát › tạo kỳ cho sự kiện › **Lấy danh sách** › xem tab **Milestone** (mỗi bài một dòng) › **Duyệt**.
3. Bài bị từ chối ở bất kỳ lúc nào trước khi chi thì khoản của bài không được chi (BR-05, BR-13).

---

## 7. Kịch bản kiểm thử (QC)

**Dữ liệu chung:** một sự kiện đang chạy, nguồn nhận bài TikTok, Facebook Post, Facebook Reels, Instagram; một nhiệm vụ **theo thông số** (để kích hoạt được sự kiện, mức 0); một nhiệm vụ **Cố định mỗi bài được duyệt** hiệu lực hôm nay, không giới hạn số lượng, mức TikTok 50, Facebook Reels 50, Facebook Post 25, **Instagram để trống**; hai người tham gia U1, U2; không đặt ngân sách trừ khi kịch bản nói khác.

| # | Kịch bản | Các bước | Kết quả mong đợi | BR |
|---|---|---|---|---|
| TC-01 | Video TikTok được duyệt | U1 gửi 1 video TikTok, BTC duyệt | 1 khoản **50 điểm**, chờ đối soát; thẻ bài hiện 50 | 01, 02, 11 |
| TC-02 | Bài Facebook Post được duyệt | U1 gửi 1 bài Facebook Post, BTC duyệt | 1 khoản **25 điểm** | 02 |
| TC-03 | Nguồn không có mức | U1 gửi 1 bài Instagram, BTC duyệt | **Không** có khoản | 02 |
| TC-04 | Bài chưa duyệt | U1 gửi 1 video TikTok, chưa duyệt | Không có khoản. Duyệt xong thì mới có 1 khoản 50 | 03 |
| TC-05 | Duyệt lặp | Bài đã duyệt (có 1 khoản), BTC bấm duyệt thêm lần nữa; hoặc hai BTC bấm duyệt cùng lúc (không qua bước từ chối) | Vẫn **đúng 1 khoản** cho bài | 04 |
| TC-06 | Bài bị từ chối rồi duyệt lại | Duyệt bài (có khoản 50), từ chối bài, rồi duyệt lại | Sau từ chối: khoản bị từ chối, thẻ bài không còn điểm. Sau duyệt lại: 1 khoản **mới** 50 còn hiệu lực, khoản cũ vẫn ở trạng thái từ chối | 05 |
| TC-07 | Nhiều bài một người | U1 có 4 video TikTok và 2 bài Facebook Post, duyệt hết | 6 khoản, tổng **250 điểm**; không bị chặn ở bài thứ hai | 08 |
| TC-08 | Ngoài thời hạn | Nhiệm vụ hiệu lực 01/12–31/12, gửi link ngày 16/11, duyệt | Không có khoản | 06 |
| TC-09 | Hết suất | Nhiệm vụ Số lượng = 3. Duyệt 4 bài | Chỉ 3 bài đầu có khoản, bài thứ 4 **không** | 07 |
| TC-10 | Ngân sách chiến dịch | Ngân sách/Chiến dịch = 120. Duyệt 3 video TikTok | Bài 1, 2: 50 điểm. Bài 3: **0 điểm** có cờ vượt ngân sách (chỉ còn 20); có cảnh báo vượt ngân sách | 09 |
| TC-11 | Ngân sách creator | Ngân sách/Creator = 70. U1 duyệt 2 video, U2 duyệt 1 video | U1 bài 1: 50; U1 bài 2: **0** (còn 20); U2 bài 1: **50** (hạn mức của U2 độc lập) | 09 |
| TC-12 | Ngân sách nội dung | Ngân sách/Nội dung = 60. Hai nhiệm vụ cố định cùng áp cho một bài TikTok 50 điểm. Duyệt bài | Một khoản 50 và một khoản **0** có cờ | 09 |
| TC-13 | Không tự tính lại | Sau TC-10, vào tab Ngân sách tăng Ngân sách/Chiến dịch lên 200, rồi duyệt thêm một bài khác | Khoản 0 điểm của bài 3 **vẫn 0**. Bài mới (còn chỗ) được 50 | 10 |
| TC-14 | Đối soát, lấy danh sách | Có khoản 50, 25, một khoản 0 điểm, một khoản của bài đã bị từ chối. Tạo kỳ đối soát, Lấy danh sách | Tab Milestone chỉ có 2 dòng (50 và 25), mỗi dòng ghi chú có link bài. Hai bài cùng người vẫn là hai dòng riêng | 12 |
| TC-15 | Đối soát, chạy chi | Duyệt kỳ ở TC-14 | Hai khoản **đã hoàn thành**; số dư người tham gia tăng đúng 75; người nhận thông báo thưởng | 13 |
| TC-16 | Bài bị huỷ sau lúc lập bản | Lấy danh sách có 1 dòng của bài X. Trước khi duyệt kỳ, từ chối bài X. Duyệt kỳ | Dòng của bài X bị từ chối ("Thông tin nội dung không chính xác"), **không chi**; dòng khác vẫn chi | 13 |
| TC-17 | Thông báo | Duyệt một bài | Người tham gia nhận thông báo "bài được duyệt"; **không** có thông báo thưởng thêm lúc tạo khoản | 3.2 |
| TC-18 | Cấu hình form | Tạo nhiệm vụ, chọn 3 nguồn | Có 3 ô "Thưởng mỗi bài" tương ứng; bảng nhiệm vụ hiện số nguồn, rê chuột ra danh sách điểm từng nguồn | 5 |
| TC-19 | Sửa mức điểm | Khoản đã có 50. Sửa mức TikTok lên 60, duyệt một video mới | Khoản cũ vẫn 50; video mới 60 | 5 |
| TC-20 | Hồi quy loại thưởng cũ | Sự kiện có thêm nhiệm vụ theo thông số và theo mốc đang chạy | Hai loại cũ tính như trước, không bị ảnh hưởng | 01 |

---

## 8. Câu hỏi còn mở ảnh hưởng chức năng 1

| # | Câu hỏi | Ảnh hưởng |
|---|---|---|
| Q4 | Bảng điểm 25/50 hay 50/100? | Con số BTC nhập ở mục 5. Không ảnh hưởng cách hệ thống chạy |
| Q8 | Có giới hạn số bài tính điểm mỗi người mỗi ngày không? | Nếu có, cần thêm quy tắc mới (chưa làm) |
| Q14 | Nền tảng nào được tính (Instagram ảnh, YouTube Shorts, Threads)? | Nguồn nào được nhập mức ở mục 5 |
| Q17 | Ngày bắt đầu và kết thúc chương trình | Khoảng thời gian hiệu lực của nhiệm vụ (BR-06) |

Danh sách đầy đủ các câu hỏi nằm trong sheet theo dõi (phần Related Documents).

---

## 9. Tham chiếu triển khai

- Issue: diso-pmax/ambassador-vietjet#145. Mã nguồn: PR #146 (đã merge). Cách cấu hình chi tiết cho người vận hành: `docs/THUONG-THEO-BAI.md` trong repo ambassador-vietjet.
- Kiểm thử tự động của chức năng này nằm trong repo; bảng ở mục 7 là kịch bản kiểm tay cho QC.
