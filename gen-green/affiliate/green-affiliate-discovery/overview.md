# Green Affiliate — Trang khám phá chiến dịch affiliate

> Biến nhánh **"Green Seller (Coming soon)"** trên Green Creator thành **"Green Affiliate"** — một trang khám phá chiến dịch affiliate có giao diện y hệt trang chủ Green Creator (hero giới thiệu + danh sách chiến dịch theo partner).

**Ngày:** 27/05/2026
**Trạng thái:** Đề xuất
**Đối tượng đọc:** Business, Ops, PM, Dev
**Phạm vi:** Frontend Green Creator — nhánh thứ 2 trên thanh chuyển (top switcher) + trang đích của nhánh đó

---

## 1. Hiện tượng / Bối cảnh

Trên Green Creator hiện có **2 nhánh** ở góc trên bên phải:

- **Gen Green** — nhánh đang chạy: creator sáng tạo nội dung, nhận thưởng từ các chiến dịch nội dung của Vingroup. Dưới nhánh này có thanh tab partner: `Gen Green | VinWonders | VinFast | VEC | Vinhomes | Green SM`.
- **Green Seller (Coming soon)** — nhánh thứ 2, đang để nhãn "Coming soon", **chưa có nội dung**.

Nhánh thứ 2 này được dự định là nơi creator kiếm thu nhập từ **bán hàng affiliate** (chia sẻ link → có đơn hàng → nhận hoa hồng), bổ sung cho nguồn thu nhập từ lượt xem ở nhánh Gen Green. Nhưng hiện tại nó chỉ là một nhãn trống — creator bấm vào không thấy gì.

Trong khi đó, phía sau đã có sẵn nhiều partner (VinFast, VinWonders, Green SM...) và cơ chế chuẩn bị catalog chiến dịch affiliate (xem [Admin Setup](../admin-setup-overview.md)). Tức là **đã có hàng để bày, chỉ thiếu mặt tiền cửa hàng**.

---

## 2. Tại sao phải làm

**1. Nhánh trống làm mất cơ hội.**
Creator nhìn thấy "Green Seller (Coming soon)" mỗi ngày nhưng không vào được. Mỗi ngày trống là một ngày không có creator nào bắt đầu tạo link affiliate — trong khi mục tiêu là kích hoạt nguồn thu nhập thứ 2 cho creator.

**2. Đã có hàng nhưng không có nơi trưng bày.**
Admin đã (hoặc sắp) chuẩn bị catalog chiến dịch affiliate theo từng partner. Nếu không có trang khám phá, creator không có cách nào duyệt toàn bộ chiến dịch để chọn cái phù hợp đem đi bán.

**3. Tận dụng giao diện đã quen thuộc.**
Creator đã quen với cách trang chủ Green Creator hoạt động (hero giới thiệu + thanh tab partner + danh sách bên dưới). Clone đúng giao diện đó cho Green Affiliate giúp creator hiểu ngay, không cần học lại.

→ Đợt này team giải quyết: **đổi tên nhánh "Green Seller" → "Green Affiliate", bỏ nhãn "Coming soon", và dựng trang khám phá chiến dịch affiliate clone từ trang chủ Green Creator.**

---

## 3. Giải pháp đề xuất

### Tóm tắt giải pháp

**Clone nguyên giao diện trang chủ Green Creator cho nhánh Green Affiliate: cùng hero giới thiệu, cùng thanh tab partner, cùng cách bày danh sách bên dưới — chỉ khác phần nội dung là chiến dịch affiliate thay vì nội dung sáng tạo.**

### Cách hoạt động

1. **Đổi tên nhánh.** Nút "Green Seller (Coming soon)" trên thanh chuyển đổi thành **"Green Affiliate"**, bỏ nhãn "Coming soon". Bấm vào → mở trang Green Affiliate.

2. **Hero giới thiệu (giống trang chủ Green Creator).** Phần đầu trang là khối giới thiệu: tiêu đề "Green Affiliate", tagline, vài dòng mô tả "kiếm hoa hồng từ việc chia sẻ sản phẩm", kèm các con số tổng quan (nếu có).

3. **Thanh tab partner.** Ngay dưới hero là thanh tab partner — **giống hệt thanh tab của nhánh Gen Green**. Mỗi tab là một partner.
   - **Thứ tự tab do backend quy định** — y hệt cách Green Creator sắp tab hiện tại. Frontend không tự sắp xếp.
   - **Partner nào chưa có chiến dịch affiliate thì không hiện tab.** Ví dụ nếu VEC và Vinhomes chưa bật affiliate, thanh tab Green Affiliate chỉ hiện `VinFast | VinWonders | Green SM` (theo thứ tự backend trả về). Khi biz bật affiliate cho VEC, tab VEC tự xuất hiện — không cần chỉnh lại frontend.

4. **Danh sách chiến dịch trong mỗi tab.** Chọn một tab partner → bên dưới hiển thị danh sách chiến dịch affiliate của partner đó (dạng card: banner, tên, hoa hồng, thưởng thêm, thời gian). Bấm vào card → vào trang chi tiết chiến dịch để tham gia và tạo link (luồng đã có ở [FE Creator](../fe-display-generate-link-report-overview.md)).

### Phạm vi áp dụng

**Chỉ áp dụng cho:**
- Nhánh thứ 2 trên thanh chuyển của Green Creator (đổi tên + dựng trang).
- Hiển thị danh sách chiến dịch affiliate theo partner (đọc dữ liệu, không tạo/sửa).

**Không áp dụng cho:**
- Nhánh Gen Green (nội dung) — giữ nguyên không đổi.
- Tạo/sửa chiến dịch affiliate — đó là việc của [Admin Setup](../admin-setup-overview.md).
- Luồng tham gia chiến dịch + tạo link + báo cáo hoa hồng — đã định nghĩa ở [FE Creator](../fe-display-generate-link-report-overview.md); trang này chỉ là cửa vào (khám phá).

### Trường hợp đặc biệt

- **Chưa partner nào có chiến dịch affiliate.** Toàn bộ thanh tab rỗng → hiển thị một trạng thái trống toàn trang ("Các chiến dịch affiliate sắp ra mắt"). Theo thực tế hiện tại (đã có nhiều partner chạy), trường hợp này hiếm nhưng vẫn cần phòng hờ.
- **Một partner có tab nhưng chiến dịch vừa hết hạn hết.** Nếu mọi chiến dịch của partner đó đã hết hạn / bị tắt, partner đó không còn được tính là "có chiến dịch active" → tab ẩn theo đúng quy tắc ở mục 3.3.

---

## 4. Lợi ích kỳ vọng

### Cho creator
- ✅ Có một nơi rõ ràng để khám phá toàn bộ chiến dịch affiliate, chọn cái phù hợp đem đi bán.
- ✅ Giao diện quen thuộc (giống trang chủ Green Creator) — không phải học lại.
- ✅ Mở ra nguồn thu nhập thứ 2 (hoa hồng) bên cạnh thu nhập từ lượt xem.

### Cho hệ thống
- ✅ Tái sử dụng tối đa giao diện + component sẵn có của trang chủ Green Creator → ít code mới, ít rủi ro.
- ✅ Tab tự xuất hiện/ẩn theo dữ liệu → bật affiliate cho partner mới không cần sửa frontend.

### Cho vận hành / business
- ✅ Kích hoạt được nhánh Green Affiliate vốn đang trống — tận dụng catalog đã chuẩn bị.
- ✅ Kiểm soát được partner nào "lên kệ" Green Affiliate qua việc bật/tắt chiến dịch (không cần can thiệp frontend).

---

## 5. Chi phí và rủi ro

### Chi phí

| Hạng mục | Ước tính |
|----------|----------|
| Dev frontend (clone layout + tab + danh sách) | Thấp — clone từ trang chủ Green Creator có sẵn |
| Backend (endpoint trả tab partner + danh sách chiến dịch active) | Trung bình — có thể tái dùng API browse campaign sẵn có |

### Rủi ro & cách xử lý

| Rủi ro | Mức độ | Cách xử lý |
|--------|--------|------------|
| Creator vào tab nhưng không phân biệt được đây là affiliate hay nội dung | Thấp | Hero + tiêu đề "Green Affiliate" làm rõ ngữ cảnh; card chiến dịch hiển thị hoa hồng để phân biệt |
| Thứ tự tab Green Affiliate lệch so với Gen Green gây bối rối | Thấp | Backend dùng cùng nguồn thứ tự partner; chỉ skip partner chưa có affiliate, giữ thứ tự tương đối |
| Tab "nhảy" khi partner được bật/tắt affiliate | Thấp | Đây là hành vi đúng kỳ vọng; có thể thông báo nội bộ khi bật partner mới |
| Trang trống nếu chưa có chiến dịch nào | Thấp | Empty state toàn trang ("sắp ra mắt") |

---

## 6. Phạm vi không ảnh hưởng

Tài liệu này **không thay đổi**:
- Nhánh **Gen Green** (nội dung) — thanh tab, danh sách nội dung, luồng sáng tạo giữ nguyên.
- Luồng **liên kết tài khoản Scalef** ([Account Linking](../account-linking-overview.md)).
- Luồng **tham gia chiến dịch + tạo link + báo cáo hoa hồng** ([FE Creator](../fe-display-generate-link-report-overview.md)).
- Cơ chế **Admin Setup** chuẩn bị catalog chiến dịch.

---

## 7. Một vài câu hỏi còn để ngỏ

1. Tên hiển thị nhánh thứ 2 chốt là **"Green Affiliate"** (theo yêu cầu này) — có cần đồng bộ lại các tài liệu cũ đang dùng từ "Green Seller" không?
2. Hero Green Affiliate có hiển thị các con số tổng quan như trang chủ Green Creator (tổng chiến dịch, tổng hoa hồng đã trả...) không, hay chỉ có phần giới thiệu?
3. Trong một tab partner, danh sách chiến dịch có cần thêm tìm kiếm / sắp xếp không, hay bày phẳng giống trang chủ Green Creator là đủ cho giai đoạn đầu?

---

## 8. Tài liệu liên quan

- **PRD chi tiết:** [`prd.md`](./prd.md) — FR/NFR cho dev/PM
- **FE Creator (luồng tham gia + tạo link + báo cáo):** [`../fe-display-generate-link-report-overview.md`](../fe-display-generate-link-report-overview.md)
- **Admin Setup (chuẩn bị catalog):** [`../admin-setup-overview.md`](../admin-setup-overview.md)
- **Account Linking (liên kết Scalef):** [`../account-linking-overview.md`](../account-linking-overview.md)
- **PRD V2 affiliate (FR-T3-007 Browse chiến dịch):** [`../prd-v2-2026-05-12.md`](../prd-v2-2026-05-12.md)
- **Scalef API Reference:** [`../scalef-api.md`](../scalef-api.md)
