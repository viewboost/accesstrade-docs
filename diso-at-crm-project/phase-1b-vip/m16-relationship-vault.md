# M16 — Quản lý Tài sản Quan hệ

> **Demo Offboarding Workflow:** https://vcreator.demo.accesstrade.click/mockup/ams/am-mai/offboarding

---

## Mục đích

Module M16 giải quyết một trong những bài toán doanh nghiệp lớn nhất của AccessTrade: ngăn việc nhân sự nghỉ việc kéo theo creator. Đây là module signature, đặc trưng nhất của CRM AccessTrade và là yếu tố khiến hệ thống này khác biệt với CRM thông thường.

Trong môi trường hiện tại, mỗi người phụ trách Care xây dựng quan hệ với hàng chục creator qua Zalo cá nhân. Khi họ nghỉ việc và sang đối thủ làm, họ mang theo cả mạng lưới creator. AccessTrade mất đi tài sản đã đầu tư xây dựng nhiều tháng.

M16 đảm bảo quan hệ creator là tài sản công ty, không phải tài sản cá nhân. Khi nhân sự nghỉ việc, có quy trình chuyển giao chuẩn để creator không rời theo người cũ.

Module này không chỉ là tính năng kỹ thuật, mà cần kết hợp với chính sách HR + Legal + IT để hiệu quả thực sự.

---

## Người dùng chính

- **Trưởng nhóm Lead Care:** Theo dõi Relationship Capital, kích hoạt offboarding workflow
- **HR:** Trigger workflow khi nhân sự thông báo nghỉ việc
- **Người phụ trách đang offboarding:** Tham gia ceremony bàn giao
- **Người phụ trách nhận bàn giao:** Đọc context, tiếp tục chăm sóc

---

## Câu chuyện sử dụng

Mai (người phụ trách Care, ngành mỹ phẩm) thông báo nghỉ việc, nghỉ chính thức sau 14 ngày. HR cập nhật vào hệ thống.

M16 tự động kích hoạt workflow offboarding sáu bước:

**Bước 1: Thông báo HR và lên lịch ngày cuối** — Tự động khi HR đánh dấu offboarding trong HRIS. Hoàn thành.

**Bước 2: Khóa quyền truy cập kênh cá nhân** — M16 chặn Mai dùng Zalo cá nhân liên hệ creator. Buộc tất cả tin nhắn phải qua Zalo OA chính thức. Hoàn thành.

**Bước 3: Audit conversation archive** — M16 đối chiếu mọi tin nhắn của Mai với creator, đảm bảo không có tin nhắn nào ngoài hệ thống. Tổng cộng 28 creator, 89 conversation thread, audit pass. Không phát hiện rò rỉ. Hoàn thành.

**Bước 4: Tạo handoff plan** — Hệ thống dùng AI đề xuất phân phối 28 creator của Mai cho ba người phụ trách khác dựa trên ngành chuyên môn, workload, và relationship affinity. Đang chờ Lead approve.

Lead Phương review handoff plan, thấy đề xuất hợp lý, bấm "Approve all". Hệ thống chuyển sang bước 5.

**Bước 5: Lead approval và ceremony giới thiệu** — Mỗi creator được giới thiệu với người phụ trách mới qua Zalo OA chính thức. Tin nhắn dùng template chuẩn: "Chào em [creator]. Chị [Mai] sắp chuyển việc, từ [date] em sẽ làm việc cùng [new AM] thay thế. [New AM] đã được brief đầy đủ về deal hiện tại. Em có thắc mắc gì cứ hỏi nha."

Mai cũng tham gia 1 lần cuối, gửi tin "Cảm ơn em đã đồng hành cùng chị". Tạo cảm giác chuyển giao có nghi thức.

**Bước 6: Revoke access và final exit** — Đến ngày cuối, hệ thống tự động disable CRM account của Mai, revoke API keys, gửi reminder NDA.

Sau 90 ngày, M16 vẫn theo dõi: 100% creator được giữ chân, không creator nào churn theo Mai. Risk monitoring kết luận "Low".

---

## Tính năng cốt lõi

### Cường độ quan hệ (Relationship Strength)
- Mỗi cặp (người phụ trách × creator) có điểm cường độ quan hệ 0-100
- Tính dựa trên: tần suất tương tác, response rate, content collab, GMV joint
- Hiển thị trên trang chi tiết creator và AM Detail
- Phục vụ optimize handoff (giao creator có quan hệ cao cho người mới quen với context)

### Channel mandate — Bắt buộc kênh chính thức
- Zalo OA company channel + Email công ty là kênh duy nhất hợp lệ
- Hệ thống detect và cảnh báo nếu nhân viên dùng Zalo cá nhân
- Có thể block technical (qua chính sách MDM) trong production

### Conversation archive permanent
- Mọi tin nhắn được lưu vĩnh viễn trong CRM
- Search được, attribute đến creator, không phải đến nhân viên
- Người mới đọc được toàn bộ context khi nhận bàn giao

### Activity heatmap (AM × KOC)
- Visualize mức độ tương tác giữa từng người phụ trách và từng creator
- Phát hiện pattern bất thường: low activity in-tool nhưng creator vẫn engage = dấu hiệu "nuôi quan hệ ngoài hệ thống"

### Workflow offboarding sáu bước
- Tự động kích hoạt khi HR đánh dấu nghỉ việc
- Sáu bước với SLA cho mỗi bước
- Lead phải approve handoff plan
- Audit log đầy đủ

### Handoff plan với AI suggestion
- Đề xuất ai nhận creator nào dựa trên ngành chuyên môn, workload hiện tại, relationship affinity với new owner
- Lead có thể chỉnh sửa trước khi approve
- Cho phép re-route từng creator riêng lẻ

### Anti-poaching detection
- Sau khi nhân viên nghỉ, theo dõi creator của họ trong 90 ngày
- Cảnh báo Lead nếu creator inactive ngay sau bàn giao
- Cho phép Lead intervention nếu phát hiện creator bị poach

### Co-ownership cho VIP
- VIP creator có thể có 1 senior + 1 backup owner
- Cả hai đều có context, không phụ thuộc một người
- Giảm rủi ro mất VIP khi senior nghỉ việc

### KOC contact preference vault
- Creator được hỏi kênh nào họ muốn được liên hệ chính thức
- Lưu ở company level, không phụ thuộc cá nhân nhân viên
- Khi đổi owner, kênh giao tiếp vẫn nguyên

### Relationship Capital Report
- Báo cáo tổng giá trị quan hệ AccessTrade đang có
- Phân theo brand, ngành, tier creator
- Tài liệu cho leadership thấy tài sản vô hình của doanh nghiệp

---

## Tích hợp

- **Với M5 Owner Workload:** Lưu lịch sử ownership, sử dụng cho handoff plan
- **Với M7 Outreach:** Dữ liệu conversation là nguồn chính cho relationship strength
- **Với HR System:** Trigger offboarding workflow từ HRIS
- **Với IT System:** Khóa Zalo cá nhân, revoke access cuối quy trình
- **Với Legal:** NDA reminder, audit trail cho compliance

---

## Đo lường thành công

- Tỷ lệ giữ chân creator khi người phụ trách nghỉ việc, mục tiêu 100%
- Tỷ lệ tin nhắn qua kênh chính thức, mục tiêu trên 95%
- Số rò rỉ conversation phát hiện ngoài hệ thống, mục tiêu 0
- Thời gian hoàn thành workflow offboarding, mục tiêu dưới 14 ngày
- Sự hài lòng creator sau bàn giao (khảo sát ngắn), mục tiêu trên 4/5

---

## Cảnh báo triển khai

Module này chỉ hiệu quả khi kết hợp với chính sách rõ ràng từ HR, Legal, IT. Nếu chỉ triển khai tool mà không có chính sách buộc nhân viên dùng kênh chính thức, M16 sẽ không bảo vệ được quan hệ.

Cần tổ chức workshop training cho đội Care, giải thích M16 là công cụ bảo vệ tài sản chung, không phải công cụ giám sát cá nhân, để tránh phản ứng tiêu cực.

---

## Liên quan trong demo

- **AM Offboarding Workflow:** https://vcreator.demo.accesstrade.click/mockup/ams/am-mai/offboarding
- Trang demo hiển thị sáu bước workflow với trạng thái từng bước
- Handoff plan bảng đề xuất phân phối 28 creator
- Anti-poach guarantee card và risk monitor
- **AM Detail với Relationship Heatmap:** https://vcreator.demo.accesstrade.click/mockup/ams/am-phuong
- **Trang chi tiết creator — Relationship Capital section:** https://vcreator.demo.accesstrade.click/mockup/creators/cr-beautyquynh
