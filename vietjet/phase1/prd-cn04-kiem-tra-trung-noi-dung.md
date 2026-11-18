# CN-04 · Kiểm tra trùng nội dung video

**Date:** 2026-11-16 · **Author:** Vinh Nguyễn · **Version:** 0.1 · **Status:** Draft
**Mục lục chung:** [README.md](./README.md)

## CN-04.1 Mục đích

Thể lệ không tính điểm cho nội dung trùng lặp, sao chép. Một nội dung có thể được đăng lại ở nền tảng khác hoặc ở link khác nên hệ thống cần nhận ra **cùng một video** dù khác nền tảng hoặc khác link, để chỉ một bài được tính điểm.

Hệ thống hiện chưa có cách nhận ra cùng một video được đăng lại ở nền tảng hoặc link khác.

Ví dụ: nhân viên đăng một video lên TikTok rồi đăng lại video đó lên Facebook Reels. Hai bài là một nội dung, chỉ bài đầu được tính điểm.

## CN-04.2 Phạm vi

**Trong phạm vi**
- So khớp **nội dung video** giữa các bài đã gửi.
- Gắn nhãn bài nghi trùng ở Admin, kèm bài gốc.

**Ngoài phạm vi**
- Quyết định từ chối bài trùng: thuộc người duyệt bài của BTC.
- Kiểm trùng ảnh, bài chỉ có chữ.
- Bài copy từ người khác ngoài hệ thống (không có bài gốc trong hệ thống).

## CN-04.3 Điều kiện triển khai

Chức năng cần một dịch vụ so khớp nội dung video do AT-Core cung cấp. Chưa có dịch vụ này thì chức năng chưa triển khai được.

## CN-04.4 Chức năng liên quan

| Chức năng | Quan hệ |
|---|---|
| [CN-01](./prd-cn01-diem-co-dinh-moi-bai.md) | Bài bị từ chối vì trùng thì khoản thưởng theo vòng đời của CN-01 |

## CN-04.5 Quy tắc nghiệp vụ

| Mã | Quy tắc |
|---|---|
| **CN04-BR01** | Khi người tham gia gửi bài video, hệ thống gửi nội dung video sang dịch vụ so khớp và nhận kết quả: không trùng, hoặc trùng với bài nào |
| **CN04-BR02** | Bài **gửi sau** được gắn nhãn **Nghi trùng** kèm đường dẫn tới bài gốc (bài gửi trước). Bài gốc không bị gắn nhãn |
| **CN04-BR03** | Nhãn hiện ở màn **Nội dung** của Admin và ở chi tiết bài, để người duyệt thấy khi xem xét |
| **CN04-BR04** | Hệ thống **không tự từ chối** bài nghi trùng. BTC quyết định duyệt hay từ chối |
| **CN04-BR05** | So khớp theo nội dung video, không theo link hay nền tảng: cùng video đăng ở TikTok, Facebook Reels, YouTube Shorts… đều được nhận ra |
| **CN04-BR06** | Dịch vụ so khớp lỗi hoặc quá thời gian chờ thì bài vẫn được gửi bình thường, không gắn nhãn, và hệ thống ghi lại để kiểm tra sau |

## CN-04.6 Kịch bản kiểm thử

| Mã | Kịch bản | Các bước | Kết quả mong đợi | Quy tắc |
|---|---|---|---|---|
| CN04-TC01 | Đăng lại khác nền tảng | U1 gửi video TikTok (bài A), sau đó gửi cùng video ở Facebook Reels (bài B) | Bài B có nhãn Nghi trùng, dẫn tới bài A; bài A không có nhãn | BR02, 05 |
| CN04-TC02 | Đăng lại khác link | U1 gửi hai link TikTok khác nhau cùng một video | Bài sau có nhãn Nghi trùng | BR02, 05 |
| CN04-TC03 | Hai video khác nhau | U1 gửi hai video khác nội dung | Không có nhãn | BR01 |
| CN04-TC04 | BTC quyết định | Mở bài B, từ chối | Bài B bị từ chối, khoản thưởng theo CN-01; nếu BTC duyệt thì bài vẫn được duyệt | BR04 |
| CN04-TC05 | Người xem nhãn | Mở màn Nội dung | Thấy nhãn và link bài gốc | BR03 |
| CN04-TC06 | Dịch vụ lỗi | Dịch vụ so khớp không phản hồi | Bài vẫn gửi được, không có nhãn | BR06 |
