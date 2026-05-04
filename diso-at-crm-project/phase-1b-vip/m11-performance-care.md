# M11 — Bảng điều khiển Chăm sóc Hiệu suất

> **Demo:** Performance insights tích hợp trên trang chi tiết creator và Reports Dashboard

---

## Mục đích

Module M11 biến dữ liệu hiệu suất raw thành quyết định hành động cụ thể. Có dữ liệu nhưng không biết phải làm gì với nó cũng vô ích. M11 phân tích dữ liệu, phát hiện pattern, đề xuất cho người phụ trách: nên Scale, nên Optimize, hay nên Pause.

Trong vận hành CRM hằng ngày, người phụ trách dễ bỏ sót cơ hội. Một creator vừa có viral hit nhưng họ không biết → bỏ lỡ cơ hội scale. Một creator có CR đột ngột giảm nhưng họ không thấy → bỏ lỡ cơ hội intervene sớm. M11 đảm nhận vai trò "trợ lý phát hiện cơ hội và rủi ro".

---

## Người dùng chính

- **Người phụ trách Care và Senior Care:** Nhận đề xuất action cho từng creator
- **Trưởng nhóm Lead:** Xem dashboard tổng quan để cân bằng nguồn lực
- **BD:** Sử dụng signal để đề xuất campaign mới cho creator phù hợp

---

## Câu chuyện sử dụng

@thanhtam.review (creator beauty Gold tier, 84K follower) đăng video review son. M10 sync dữ liệu: 240K view, CR 5.1% sau 24 giờ.

M11 phân tích:
- View 240K so với baseline trung bình của Tâm là 80K → tăng 200%
- CR 5.1% so với benchmark ngành 3% → cao hơn rõ rệt
- Trend đang lên

M11 đánh dấu "Trending up" và đề xuất hành động "Scale với GMV Max budget 5tr". Linh nhận thông báo, bấm vào trang chi tiết creator của Tâm, thấy đề xuất nổi bật trên trang. Cô liên hệ Tâm, đồng ý scale.

Trường hợp khác: @reviewervn (creator tech, Watchlist) đã 14 ngày không đăng nội dung. M11 phát hiện inactive pattern, đánh dấu "Reactivation needed", đề xuất hành động "Senior review trước khi blacklist".

Trường hợp khác: @makeupbylinh (Diamond, top performer) có CR giảm dần ba tuần liên tiếp. M11 phát hiện trend giảm, đánh dấu "Performance declining", đề xuất "Đề xuất content angle mới".

Cuối tuần, Lead Phương vào dashboard tổng quan. Thấy số creator được đề xuất Scale là 12, Optimize là 28, Pause là 5. Cô phân bổ Senior Care cho top Scale targets.

---

## Tính năng cốt lõi

### Trang chi tiết creator — view tổng hợp
- Tất cả dữ liệu performance creator được tổng hợp vào một màn hình
- GMV trend 30 ngày, 90 ngày
- CR trend
- View và engagement
- Phân theo nền tảng

### Phát hiện anomaly
- **Drop CR:** CR giảm 30% trở lên so với baseline
- **View low:** View dưới 50% baseline
- **Content underperform:** Engagement thấp bất thường
- **Refund spike:** Tỷ lệ hoàn hàng tăng đột ngột
- **Inactive pattern:** Không đăng content trên ngưỡng thời gian
- **Trending up:** GMV/View/CR tăng mạnh — cơ hội scale

### Đề xuất hành động cụ thể
- **Scale:** Khi creator đang trending up → đề xuất GMV Max, mở campaign mới
- **Optimize:** Khi creator có một số issue nhỏ → đề xuất thay angle, voucher, sản phẩm mới
- **Reactivate:** Khi creator inactive → đề xuất chiến dịch re-engagement
- **Pause:** Khi creator có nhiều red flag → đề xuất senior review trước khi action mạnh

### So sánh cohort
- VIP cohort vs Gold vs Normal: ai có performance gap lớn nhất
- Phân tích pattern theo ngành, theo region, theo độ tuổi tài khoản
- Giúp Lead hiểu xu hướng tổng thể

### Biểu đồ trend
- GMV/CR/order theo tuần
- So sánh với baseline cá nhân
- So sánh với benchmark ngành
- Cảnh báo khi đường trend đi sai hướng

### Action history
- Lưu lại các đề xuất đã đưa ra
- Theo dõi creator có thực hiện đề xuất hay không
- Đo hiệu quả của đề xuất (creator được scale có thực sự tăng GMV?)
- Phục vụ cải thiện model đề xuất

---

## Tích hợp

- **Với M10 Performance Sync:** Sử dụng dữ liệu performance làm input
- **Với M3 Tier Engine:** Tier ảnh hưởng đến loại đề xuất (VIP được đề xuất scale ưu tiên)
- **Với M14 Notification:** Khi phát hiện anomaly quan trọng, gửi cảnh báo cho người phụ trách
- **Với M6 Task Console:** Đề xuất action xuất hiện ngay trong queue của người phụ trách

---

## Đo lường thành công

- Số đề xuất Scale dẫn đến tăng GMV thực tế, mục tiêu trên 60%
- Số đề xuất Reactivate dẫn đến creator hoạt động lại, mục tiêu trên 40%
- Tỷ lệ phát hiện anomaly trước khi vấn đề lan rộng, mục tiêu trên 80%
- Sự hài lòng người phụ trách với đề xuất (khảo sát hằng tháng)

---

## Liên quan trong demo

- **Trang chi tiết creator với suggested actions:** https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh
- Phía dưới trang chi tiết creator có section "Suggested Next Actions" hiển thị đề xuất từ M11
- Performance trend tích hợp trong cùng trang
- **Reports Dashboard:** https://vcreator.demo.accesstrade.click/mockup/dashboard — tổng quan dữ liệu hiệu suất toàn pool
