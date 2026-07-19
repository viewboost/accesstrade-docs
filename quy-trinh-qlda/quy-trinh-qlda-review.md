# QUY TRÌNH QLDA PHẦN MỀM ≤ 2 TUẦN — Bản tổng hợp để review

> Tổng hợp từ Google Sheet gồm 7 tab (A_Hướng-dẫn · 1_Template-Chung · 2_VD-ADV-Onboarding · 3_Product-Backlog · 4_Sprint-Board · 5_Sprint-Tracker · 6_Story-Point).
> **Quy ước ngày (D-Day, đếm ngược):** `D` = ngày release · `D-1` = 1 ngày trước release · dải đọc theo chiều thời gian (VD `D-7 → D-2`).
> **Trạng thái:** Chưa làm / Đang làm / Done / Blocked.

---

## A. Hướng dẫn

**File gồm:** `[1_Template-Chung]` quy trình chung ≤ 2 tuần (PRD, Tech Spec, Go/No-Go) · `[2_VD-ADV-Onboarding]` ví dụ đã điền · `[3_Product-Backlog]` kho việc ưu tiên · `[4_Sprint-Board]` Kanban · `[5_Sprint-Tracker]` velocity. Mỗi dự án mới: nhân bản các tab này. **CHỈ release khi Go/No-Go = Đạt.**

### Nhịp làm việc
*(Template tối đa 2 tuần · ví dụ ADV trong file này nén còn 1 tuần — D-4 → D: ① D-4 · ② D-3 · ③ D-2 · ④ D-1 Go/No-Go · ⑤ D release)*

| Giai đoạn | Nội dung |
|---|---|
| **Tuần 1 (D-9 → D-5)** | Khởi tạo → Chuẩn bị: thu thập input, fork design, config Dev, tech-req Dev, lập kế hoạch & rủi ro |
| **Tuần 2 (D-4 → D)** | Kiểm thử → Triển khai → Release: nghiệm thu, config Prod, Go/No-Go, release, sau release |

### Vai trò
| Vai trò | Trách nhiệm |
|---|---|
| Biz AT | Tiếp nhận input ADV, tổng hợp tech requirement (Dev & Prod) |
| Hiếu AT | Fork thiết kế từ template |
| Campaign Operation | Cấu hình ADV / Campaign / nội dung trên Dev & Prod |
| DevOps (Diso / AT) | Set ENV, deploy, release, rollback |
| QA | Nghiệm thu, quay video, smoke test sau release |
| PM | Kế hoạch, rủi ro, cổng GO/NO-GO, đóng dự án |
| Huyền Diso | Pre-release, meeting note, thông báo lịch |

### Sheet chi tiết (ở file ADV gốc)
`01 → 10`: 01_ADV-Input · 02_Design · 03_Config-Dev · 04_Tech-Req-Dev · 05_Testcases · 06_Config-Prod · 07_Tech-Req-Prod · 10_Troubleshooting

### Quy ước màu trạng thái
| Trạng thái | Màu |
|---|---|
| Chưa làm | Xám — chưa bắt đầu |
| Đang làm | Vàng — đang xử lý |
| Done | Xanh lá — hoàn thành |
| Blocked | Đỏ — bị chặn |

### ⭐ Khi nào dùng gì — 2 chế độ (đọc kỹ)
- **① Chế độ DỰ ÁN** — VD: onboarding 1 ADV mới lên landing page → Dùng **Tab 1 + Tab 2**. Checklist theo pha + Go/No-Go. Mỗi dự án nhân bản 1 bản riêng. **KHÔNG đo velocity** — mỗi ADV là 1 dự án độc lập, không so sánh điểm giữa các ADV.
- **② Chế độ DÒNG VIỆC LẶP** — phát triển sản phẩm liên tục → Dùng **Tab 3 + 4 + 5 + 6**. "Sprint" = nhịp lặp **CỐ ĐỊNH** (không phải vòng đời 1 dự án). Velocity chỉ có nghĩa khi cùng team chạy nhiều Sprint trên cùng dòng việc.

### ✅ Definition of Ready (DoR) — đủ điều kiện để bắt đầu / vào Sprint
Có tiêu chí chấp nhận (AC) rõ · đã estimate · rõ phụ thuộc (API/bên thứ 3/tài nguyên) · có thiết kế nếu cần · đủ nhỏ để xong trong chu kỳ.

### ✅ Definition of Done (DoD) — thế nào là "Done" (áp dụng cho mọi việc)
Code merge + review xong · test theo AC pass · hết bug blocker · đã UAT/nghiệm thu · tài liệu/ghi chú cập nhật · release được (Go/No-Go = Đạt). **Thiếu 1 mục = CHƯA Done.**

### 🚦 Pre-flight giữa kỳ (~D-4 → D-3) — trước Go/No-Go
Rà tiến độ + rủi ro sớm để còn đường cứu. Go/No-Go (D-1) chỉ là **XÁC NHẬN cuối**, không phải lần đầu phát hiện vấn đề.

---

## 1. Template chung (≤ 2 tuần)

⚠️ Ráp cho mọi task/dự án phần mềm ≤ 2 tuần. Quy mô nhỏ (vài ngày): gộp ngày, có thể bỏ UI design/UAT. **BẮT BUỘC giữ: PRD, Tech Spec, Go/No-Go.**

#### ① KHỎI TẠO — D-9
| STT | Công việc | Đầu ra (Deliverable) | Vai trò | Thời gian | Ghi chú |
|---|---|---|---|---|---|
| 1 | Tiếp nhận & làm rõ yêu cầu / bài toán | Bản ghi yêu cầu ban đầu | PM | D-9 | |
| 2 | Xác định các bên liên quan + họp kickoff | Danh sách stakeholder, biên bản kickoff | PM | D-9 | |
| 3 | Chốt mục tiêu & phạm vi sơ bộ | Scope statement | PM | D-9 | |

#### ② ĐỊNH NGHĨA & THIẾT KẾ — D-9 → D-7
| STT | Công việc | Đầu ra (Deliverable) | Vai trò | Thời gian | Ghi chú |
|---|---|---|---|---|---|
| 4 | Viết PRD (Product Requirement Document) | PRD: mục tiêu, user story, tiêu chí chấp nhận, luồng nghiệp vụ | PM | D-9 → D-8 | Nền tảng cho dev & test |
| 5 | Review & chốt PRD với các bên | PRD đã duyệt | PM | D-8 | |
| 6 | Thiết kế UI/UX (nếu có) | Wireframe / Design | Designer | D-8 | Bỏ nếu không có giao diện |
| 7 | Viết Tech Spec (Technical Specification) | Tech Spec: kiến trúc, API, data model, thư viện, giải pháp | Tech Lead | D-7 | Dựa trên PRD |
| 8 | Review Tech Spec (khả thi, rủi ro kỹ thuật) | Tech Spec đã duyệt | Tech Lead + Dev | D-7 | |

#### ③ LẬP KẾ HOẠCH — D-7
| STT | Công việc | Đầu ra (Deliverable) | Vai trò | Thời gian | Ghi chú |
|---|---|---|---|---|---|
| 9 | Chia nhỏ task từ PRD + Tech Spec | Task breakdown (WBS) | Tech Lead + PM | D-7 | |
| 10 | Ước lượng, xây lịch & phân công | Kế hoạch / lịch (Sprint plan) | PM | D-7 | |
| 11 | Nhận diện & lập kế hoạch ứng phó rủi ro | Risk log | PM | D-7 | |

#### ④ PHÁT TRIỂN — D-7 → D-2
| STT | Công việc | Đầu ra (Deliverable) | Vai trò | Thời gian | Ghi chú |
|---|---|---|---|---|---|
| 12 | Setup môi trường Dev + repo/branch | Môi trường + repo sẵn sàng | DevOps / Dev | D-7 | |
| 13 | Code theo Tech Spec | Source code | Dev | D-7 → D-2 | Cập nhật hằng ngày |
| 14 | Code review + merge | PR đã merge | Tech Lead / Dev | D-6 → D-2 | |
| 15 | Tích hợp & tự kiểm thử (dev test) | Bản build chạy được | Dev | D-5 → D-2 | |
| 16 | Checklist Release | Danh sách đầu việc chuẩn bị trước release | Cả team | D-2 | Nối Checklist Release khi go-live |

#### ⑤ KIỂM THỬ (QA) — D-7 → D-2
| STT | Công việc | Đầu ra (Deliverable) | Vai trò | Thời gian | Ghi chú |
|---|---|---|---|---|---|
| 17 | Viết test case theo PRD / tiêu chí chấp nhận | Test case | QA | D-7 | *(shift-left: viết sớm ngay khi có PRD)* |
| 18 | Thực hiện test + log bug | Test report, bug list | QA | D-4 → D-2 | |
| 19 | Fix bug + retest | Bản đã fix | Dev + QA | D-3 → D-2 | |
| 20 | UAT / nghiệm thu với stakeholder | Bản dev final | QA + Stakeholder | D-2 | |

#### ⑥ TRIỂN KHAI — D-1 → D
| STT | Công việc | Đầu ra (Deliverable) | Vai trò | Thời gian | Ghi chú |
|---|---|---|---|---|---|
| 21 | Chuẩn bị môi trường Prod + backup/snapshot | Môi trường Prod, bản backup | DevOps | D-1 | |
| 22 | 🚦 Cổng Go / No-Go | Quyết định release | PM | D-1 | Chỉ release khi tất cả đạt · Gate cuối = xác nhận (đã có pre-flight giữa kỳ ~D-4 → D-3) |
| 23 | Deploy lên Production | Bản release | DevOps | D | |
| 24 | Smoke test sau deploy | Kết quả smoke test | QA | D | |

#### ⑦ ĐÓNG & SAU RELEASE — D trở đi
| STT | Công việc | Đầu ra (Deliverable) | Vai trò | Thời gian | Ghi chú |
|---|---|---|---|---|---|
| 25 | Nghiệm thu & bàn giao | Biên bản nghiệm thu | PM / PO | D | |
| 26 | Retrospective / post-mortem | Ghi chú cải tiến | Cả team | Sau D | |
| 27 | Hỗ trợ vận hành / xử lý sự cố | Log hỗ trợ | Support / DevOps | Sau D | |

#### ⑧ GIÁM SÁT (song song cả chu kỳ)
| STT | Công việc | Đầu ra (Deliverable) | Vai trò | Thời gian | Ghi chú |
|---|---|---|---|---|---|
| 28 | Daily standup, theo dõi tiến độ/rủi ro, quản lý thay đổi | Báo cáo tiến độ | PM | Hằng ngày | |

---

## 2. Ví dụ — Dự án ADV Onboarding (1 tuần)

⚠️ Chu kỳ 1 tuần (D-4 → D, release = D). Chỉ release khi **CỔNG GO/NO-GO (D-1) = Đạt**. Sheet chi tiết nằm ở file ADV gốc.

#### ① KHỎI TẠO — D-4
| STT | Công việc | Đầu mối | Thời gian | Ghi chú |
|---|---|---|---|---|
| 1 | Tiếp nhận & thu thập đầu vào ADV (gửi mẫu, nhận bản điền đủ) | Biz AT | D-4 | Nhu cầu ADV mới từ đối tác |
| 2 | Nhận diện các bên liên quan + họp kickoff | PM | D-4 | |
| 3 | Xây dựng kế hoạch dự án (chốt scope, mốc thời gian) | PM | D-4 | |

#### ② CHUẨN BỊ (Design + Config Dev) — D-3
| STT | Công việc | Đầu mối | Thời gian | Ghi chú |
|---|---|---|---|---|
| 4 | Fork thiết kế từ template (Logo/Favicon/Banner/Cover/Màu/Font) | Hiếu AT | D-3 | Giữ layout/cấu trúc |
| 5 | Cấu hình ADV trên Develop (nhận diện, slug, allow domains, toggle) | Campaign Operation | D-3 | |
| 6 | Setup Campaign + ngân sách; tạo bài CMS → sinh các ID | Campaign Operation | D-3 | EVENT_ID, *_ARTICLE_ID |
| 7 | Tổng hợp tech requirement Dev (ENV + ID) → bàn giao DevOps | Biz AT | D-3 | |
| 8 | Định nghĩa & sắp xếp công việc, ước lượng, xây lịch trình | PM / Dev lead | D-3 | |
| 9 | Nhận diện & lập kế hoạch ứng phó rủi ro | PM | D-3 | |

#### ③ KIỂM THỬ (Deploy Dev & Nghiệm thu) — D-2
| STT | Công việc | Đầu mối | Thời gian | Ghi chú |
|---|---|---|---|---|
| 10 | DevOps set ENV theo tech-req + deploy Dev | DevOps Diso | D-2 | |
| 11 | Nghiệm thu theo mẫu test case | QA / DevOps Diso | D-2 | |
| 12 | Quay video nghiệm thu + ghi mục không test được | QA | D-2 | Lưu link video |
| 13 | Xác nhận tính năng đặc biệt (banner/webview/redirect) | Dev + QA | D-2 | |

#### ④ TRIỂN KHAI (Config Prod + Pre-release) — D-1
| STT | Công việc | Đầu mối | Thời gian | Ghi chú |
|---|---|---|---|---|
| 14 | Cấu hình ADV trên Production (giống Dev; trỏ IP thật, dọn domain test) | Campaign Operation | D-1 | |
| 15 | Tổng hợp tech requirement Prod (ID Prod KHÁC Dev) → bàn giao DevOps | Biz AT | D-1 | Lưu ý ID Prod ≠ ID Dev |
| 16 | Chốt danh sách trực release + kế hoạch rollback | PM / DevOps | D-1 | |
| 17 | Pre-release: soạn meeting note, thông báo lịch release | Huyền Diso | D-1 | |
| 18 | 🚦 CỔNG XÁC NHẬN GO / NO-GO | PM | D-1 | Chỉ release khi tất cả = Đạt |

#### ⑤ RELEASE & SAU RELEASE — D
| STT | Công việc | Đầu mối | Thời gian | Ghi chú |
|---|---|---|---|---|
| 19 | Backup / snapshot trước release | DevOps | D | Bắt buộc để rollback |
| 20 | Merge PR, deploy, setup ENV Production | DevOps AT | D | |
| 21 | Post-release smoke test (theo mẫu test case) | QA | D | |
| 22 | Xử lý sự cố (tra triệu chứng → task) / rollback nếu lỗi | Campaign Op / DevOps | D | |

#### ⑥ ĐÓNG & GIÁM SÁT — song song / sau D
| STT | Công việc | Đầu mối | Thời gian | Ghi chú |
|---|---|---|---|---|
| 23 | Giám sát tiến độ/rủi ro, Daily standup, quản lý thay đổi | PM | Hằng ngày | |
| 24 | Đóng dự án/giai đoạn + post-mortem; duy trì hỗ trợ vận hành | PM / Support | Sau D | |

---

## 3. Product Backlog

| ID | User Story / Task | Loại | Ưu tiên | Story Point | Sprint | Trạng thái | Đầu mối | Ghi chú |
|---|---|---|---|---|---|---|---|---|
| PB-01 | Là người dùng, tôi muốn đăng nhập bằng email/mật khẩu | Feature | P1 | 5 | Sprint 1 | Done | Dev | Mẫu — thay bằng story thật |
| PB-02 | Là người dùng, tôi muốn xem dashboard tổng quan | Feature | P1 | 8 | Sprint 1 | In Progress | Dev | |
| PB-03 | Là người dùng, tôi muốn nhận thông báo khi có cập nhật | Feature | P2 | 3 | Sprint 1 | Review / Test | Dev | |
| PB-04 | Tích hợp API bên thứ 3 (đối tác/dịch vụ) | Tech | P2 | 5 | Sprint 1 | To Do | Dev | |
| PB-05 | Sửa lỗi hiển thị trên mobile | Bug | P1 | 2 | Sprint 1 | Blocked | Dev | |
| PB-06 | Viết & chạy test cho luồng chính | Tech | P2 | 3 | Sprint 1 | To Do | QA | |
| PB-07 | Là admin, tôi muốn quản lý người dùng | Feature | P3 | 8 | Sprint 2 | To Do | Dev | |
| PB-08 | Tối ưu hiệu năng trang chính | Tech | P3 | 5 | Backlog | To Do | Dev | |

**Sprint 1 = 5+8+3+5+2+3 = 26 điểm.**

*Chú thích — Ưu tiên: P1 = cao nhất · P2 = trung bình · P3 = thấp nhất | Story Point: thang Fibonacci (xem mục 6) | Trạng thái đồng bộ với Sprint-Board.*

---

## 4. Sprint Board — Kanban

🎯 Sprint Goal: `[điền mục tiêu Sprint]` | **Điểm cam kết: 26**

| To Do | In Progress | Review / Test | Done | Blocked |
|---|---|---|---|---|
| PB-04 · Tích hợp API | PB-02 · Dashboard tổng quan | PB-03 · Thông báo cập nhật | PB-01 · Đăng nhập | PB-05 · Fix lỗi mobile |
| PB-06 · Test tự động | | | | |

---

## 5. Sprint Tracker — cam kết & velocity

⚠️ **Chỉ dùng cho CHẾ ĐỘ DÒNG VIỆC LẶP** (nhiều Sprint, cùng team). KHÔNG đo velocity cho onboarding từng ADV — mỗi ADV là 1 dự án riêng, dùng checklist Tab 1/2.

| Sprint | Ngày bắt đầu | Ngày kết thúc | Sprint Goal | Point cam kết | Point hoàn thành | Ghi chú (velocity / carry-over) |
|---|---|---|---|---|---|---|
| Sprint 1 | | | [mục tiêu Sprint 1] | 26 | | |
| Sprint 2 | | | [mục tiêu Sprint 2] | | | |
| Sprint 3 | | | | | | |

---

## 6. Cách chấm Story Point

Story Point = ước lượng **TƯƠNG ĐỐI** độ to/khó của việc (KHÔNG phải giờ). Dùng để tính velocity & dự báo Sprint.

### ① Thang điểm Fibonacci (1 · 2 · 3 · 5 · 8 · 13)
| Điểm | Ý nghĩa | Ví dụ điển hình | Lưu ý |
|---|---|---|---|
| 1 | Rất nhỏ, rõ ràng, làm chốc lát | Đổi text, sửa màu, config nhỏ | |
| 2 | Nhỏ, quen thuộc, ít rủi ro | 1 API cơ bản, form đơn giản | |
| 3 | Nhỏ–vừa, ít rủi ro | CRUD 1 entity, validate form | |
| 5 | Vừa, 1 tính năng hoàn chỉnh | Luồng đăng nhập, thông báo | ⭐ Hay dùng làm story mốc |
| 8 | To, nhiều phần / nhiều case | Dashboard, tích hợp bên ngoài | |
| 13 | Rất to / còn mơ hồ | Nhiều luồng phức tạp | ✂️ NÊN chẻ nhỏ trước khi làm |

### ② 3 tiêu chí đánh giá (chạm càng nhiều → điểm càng cao)
| Tiêu chí | Hỏi gì | Điểm cao khi… |
|---|---|---|
| Độ phức tạp | Logic rắc rối? Nhiều case/nhánh? | Thuật toán khó, nhiều nhánh xử lý |
| Khối lượng | Nhiều màn hình/API/việc lặp? | Làm nhiều, dù mỗi phần đơn giản |
| Bất định & rủi ro | Có phần chưa rõ / phụ thuộc? | Công nghệ mới, chờ API bên thứ 3 |

### ③ Cách chấm — Planning Poker
1. Chọn 1 story mốc quen thuộc, gán = 2 hoặc 3 điểm làm chuẩn.
2. So tương đối: việc mới "gấp đôi mốc" → điểm gấp đôi.
3. Cả team ra điểm cùng lúc; ai cao/thấp bất thường giải thích → chốt (đây là lúc lộ ra hiểu sai scope).

### ④ Nguyên tắc ghi nhớ
- 🚫 KHÔNG quy đổi cứng "1 point = X giờ" — point là tương đối, gắn với team.
- ✂️ Story > 8 điểm → chẻ nhỏ (khó ước lượng, khó xong trong 1 Sprint).
- 👥 Point là của TEAM, không dùng để đánh giá năng suất cá nhân.
- 📈 Sau 2–3 Sprint, lấy velocity trung bình để biết mỗi Sprint nhận bao nhiêu điểm là vừa.
