# KẾ HOẠCH & TIMELINE — MSHT × TPBANK: CHI HỘ TỰ ĐỘNG THEO LÔ QUA AT CORE (PHASE 2)

## 1. Bối cảnh tóm tắt

- **Sự cố:** TPBank tắt self key của MSHT khi AT chuyển sang ký HSM nhưng không báo trước. Từ đó user không rút được tiền (hơn 20 complain).
- **Phase 1 (đã xong, đang chạy):** chi thủ công.
  - MSHT validate yêu cầu rút rồi lưu **Pending**.
  - Thứ 2 và thứ 4, MSHT xuất file (mỗi user 1 request).
  - Kế toán AT chuyển khoản tay, sau đó MSHT import kết quả.
- **Phase 2 (dự án này):** chi tự động qua AT Core. Kỳ vọng ban đầu là xong trước 17/09, **hiện đã trễ gần 1 tháng**.
  - 12/10: TPBank đã mở dịch vụ, AT Core chi thử thành công (90.000đ, đã hoàn trả).
  - **Gap phát hiện khi rà soát:** MSHT đang chi **ngay từng lệnh**, trong khi AT yêu cầu **gom lô theo khung giờ**. Lý do là mỗi lần gọi AT Core, kể cả truy vấn trạng thái, tốn khoảng **5.000đ phí ký HSM**.
- **Áp lực:** Biz và AT muốn xong trong tuần này hoặc đầu tuần sau, vì chi thủ công tốn workload của cả Biz lẫn Product, và user nhận tiền chậm.

## 2. Phạm vi

**Trong phạm vi**
1. **Scheduler chi theo lô** chạy vào **0h00 · 8h00 · 12h00 · 16h00 · 20h00**. Mỗi khung gọi AT Core **1 lần cho cả lô**, không gọi từng lệnh.
2. **Kiểm soát ngưỡng chi hộ** (AT cập nhật 10/09):

   | Ngưỡng | Giá trị | Xử lý trong hệ thống |
   |---|---|---|
   | Số GD / tài khoản tổng / giờ | 30 | Mỗi lô tối đa 30 lệnh, phần dư dời sang khung kế tiếp (theo thứ tự thời gian tạo) |
   | Số GD / tài khoản tổng / ngày | 100 | Tổng các lô trong ngày ≤ 100, phần dư dời sang ngày sau |
   | Số tiền GD tối đa / tài khoản tổng / giờ | 10.000.000đ | Tổng tiền mỗi lô ≤ 10.000.000đ; lô dừng ở lệnh đầu tiên làm vượt ngưỡng, phần dư dời sang khung kế tiếp (FIFO) |
   | Số tiền tối thiểu / GD | 10.000đ | Chặn từ lúc user tạo yêu cầu |
   | Hạn mức / ngày / user | 1.900.000đ | Chặn từ lúc user tạo yêu cầu |
   | Hạn mức / tháng / user | 1.900.000đ | Chặn từ lúc user tạo yêu cầu |

3. **Trạng thái giao dịch:** Chờ lô → Đã gửi lô → Thành công / Thất bại. Cập nhật lịch sử giao dịch cho user.
4. **Truy vấn trạng thái theo lô**, hạn chế số lần gọi để tiết kiệm phí HSM.
5. **Chuyển đổi (cutover)** từ chi thủ công sang chi tự động, **không chi trùng**.
6. Log/báo cáo theo từng lô để đối soát với AT.

**Ngoài phạm vi:** API kiểm tra tên chủ tài khoản. TPBank không cung cấp API này, nên giữ logic cũ: user tự nhập số TK và tên TK. Thay đổi hạn mức hay UI rút tiền cũng không làm trong đợt này.

---

## 3. Timeline tổng

| Giai đoạn | T6 16/10 | T2 19/10 | T3 20/10 | T4 21/10 | T5 22/10 |
|---|---|---|---|---|---|
| 1. Code (2 ngày) | ■ | ■◆ | | | |
| 2. QC | ■ viết TC | | ■◆ | | |
| 3. Nghiệm thu E2E | | | | ■◆ | |
| 4. Deploy & cutover | | ■ chuẩn bị | | ■ kỳ thủ công cuối | ■◆ |

■ = đang thực hiện · ◆ = mốc

| # | Mốc | Thời điểm | Điều kiện đạt |
|---|---|---|---|
| M1 | Code xong, bàn giao QC | **19/10 18:00** | Deploy lên DEV, dev đã tự test xong |
| M2 | QC pass trên DEV | **20/10 18:00** | 100% testcase P1 pass, 0 bug Critical/Major |
| M3 | Nghiệm thu E2E chi tiền thành công | **21/10 17:00** | AT xác nhận tiền về TK test, biên bản nghiệm thu |
| M4 | Go/No-Go + cutover | **22/10** | Checklist mục 7 đủ |
| M5 | Release Production | **22/10** | Smoke test pass |
| M6 | Lô production đầu tiên thành công | **22/10** | Có lệnh về tài khoản user, khớp số liệu với AT → AT dừng chi thủ công |

---

## 4. Kế hoạch chi tiết

### Giai đoạn 1 — Code (16/10 → 19/10, 2 ngày)

| # | Công việc | PIC | Thời gian | Đầu ra |
|---|---|---|---|---|
| 1.1 | Trạng thái mới "Chờ lô": yêu cầu rút sau khi validate thì vào hàng đợi, không gọi AT Core ngay | Dev BE | 16/10 | Migration + logic |
| 1.2 | Validate ngưỡng: min 10.000đ, 1.900.000đ/ngày/user, 1.900.000đ/tháng/user (tận dụng logic Phase 1) | Dev BE | 16/10 | Unit test |
| 1.3 | Scheduler 0h/8h/12h/16h/20h: chọn tối đa 30 lệnh và ≤ 10.000.000đ/lô, ≤ 100 lệnh/ngày, FIFO, khoá chống chạy song song (lock) | Dev BE | 19/10 sáng | Job batch |
| 1.4 | Gọi AT Core 1 lần/lô theo spec chi theo lô đã thống nhất với AT; lưu batch_id; idempotency theo mã lệnh | Dev BE | 19/10 sáng | Client AT Core batch |
| 1.5 | Nhận/truy vấn kết quả lô, cập nhật trạng thái từng lệnh, hoàn số dư khi thất bại (theo quy tắc đã thống nhất với AT) | Dev BE | 19/10 chiều | Cập nhật lịch sử GD |
| 1.6 | Log + báo cáo theo lô (batch_id, số lệnh, tổng tiền, kết quả); alert khi lô lỗi hoặc dư lệnh dồn quá 1 ngày | Dev BE | 19/10 chiều | Báo cáo đối soát |
| 1.7 | Feature flag: bật/tắt chi tự động (tắt = quay về luồng Pending thủ công Phase 1) | Dev BE | 19/10 chiều | Flag cấu hình |
| 1.8 | Cho phép chạy lô thủ công trên DEV (trigger tay) để QC không phải chờ khung giờ | Dev BE | 19/10 | Endpoint/command nội bộ |
| 1.9 | Code review, deploy DEV, self-test | Dev Lead | 19/10 cuối ngày | **Build DEV (M1)** |

### Giai đoạn 2 — QC (16/10 viết TC, 20/10 test)

| # | Công việc | PIC | Thời gian | Đầu ra |
|---|---|---|---|---|
| 2.0 | Cập nhật testcase: thêm case chi theo lô / ngưỡng / cutover vào file nghiệm thu DEV | QC | 16/10 | Testcase v2 |
| 2.1 | Regression luồng rút tiền theo file smoke test TPBank | QC | 20/10 sáng | Kết quả smoke |
| 2.2 | Test batch: lệnh vào đúng lô, không gọi ngoài khung giờ, 1 lần gọi AT/lô | QC | 20/10 sáng | Kết quả |
| 2.3 | Test ngưỡng: lô > 30 lệnh, lô > 10.000.000đ, ngày > 100 lệnh, < 10.000đ, vượt 1,9tr ngày/tháng | QC | 20/10 | Kết quả |
| 2.4 | Test lỗi: AT Core timeout / trả lỗi / một phần lô thất bại; chạy lại lô không gây chi trùng | QC | 20/10 chiều | Kết quả |
| 2.5 | Test cutover: lệnh đã chi thủ công (đã import) không bị đưa vào lô | QC | 20/10 chiều | Kết quả |
| 2.6 | Fix bug + retest | Dev | 20/10 | **Test report (M2)** |

### Giai đoạn 3 — Nghiệm thu E2E (21/10)

| # | Công việc | PIC | Phối hợp | Thời gian | Đầu ra |
|---|---|---|---|---|---|
| 3.1 | Hẹn AT Core trực cùng | PM | Ngọc Thảo, AT | chốt từ 19/10 | Lịch nghiệm thu |
| 3.2 | Tạo yêu cầu rút trên DEV bằng TK test AT cấp (email 10/09), chạy lô, **xác nhận tiền về tài khoản nhận** | QC | AT Core | 21/10 sáng | Bằng chứng: ảnh / sao kê |
| 3.3 | Chạy case thất bại (sai TK) trên DEV, xác nhận hoàn số dư và trạng thái | QC | AT Core | 21/10 sáng | Bằng chứng |
| 3.4 | Đối chiếu log lô MSHT với log AT Core (số lệnh, số tiền, trạng thái) | Dev Lead | AT Core | 21/10 chiều | Bảng đối chiếu |
| 3.5 | Ký nghiệm thu, PM + AT xác nhận qua email | PM | Ngọc Thảo, AT | 21/10 17:00 | **Biên bản nghiệm thu (M3)** |

#### Tiêu chí nghiệm thu

| Mã | Nhóm | Tiêu chí | Đạt khi |
|---|---|---|---|
| AC-01 | **E2E (bắt buộc AT)** | Chi tiền thành công end-to-end MSHT → AT Core → TPBank → TK nhận | Tiền về đúng số, đúng TK; trạng thái MSHT = Thành công |
| AC-02 | Batch | Lệnh chỉ được gửi tại 0h00 / 8h00 / 12h00 / 16h00 / 20h00 | Không có lần gọi AT Core nào ngoài khung (kiểm tra log) |
| AC-03 | Batch | Mỗi khung gọi AT Core **1 lần cho cả lô**; truy vấn trạng thái theo lô | Số lần gọi = số lô (+ số lần truy vấn đã chốt) |
| AC-04 | Ngưỡng | Lô tối đa 30 lệnh và ≤ 10.000.000đ; tổng/ngày ≤ 100; phần dư dời khung sau theo FIFO | Test 35 lệnh → lô 1: 30, lô 2: 5. Test 6 lệnh × 1.900.000đ → lô 1: 5 lệnh (9.500.000đ), lô 2: 1 |
| AC-05 | Ngưỡng | Chặn < 10.000đ, vượt 1.900.000đ/ngày/user, vượt 1.900.000đ/tháng/user | Báo lỗi rõ cho user, không tạo lệnh |
| AC-06 | An toàn tiền | Không chi trùng khi chạy lại lô, AT timeout, hay scheduler chạy 2 lần | Mỗi mã lệnh chỉ được chi 1 lần |
| AC-07 | An toàn tiền | Lệnh thất bại được xử lý đúng quy tắc chốt (hoàn số dư / chờ xử lý) | Số dư user đúng sau thất bại |
| AC-08 | Cutover | Lệnh đã chi thủ công không bị đưa vào lô tự động | 0 lệnh trùng giữa file thủ công và lô |
| AC-09 | Hiển thị | Lịch sử giao dịch user hiển thị đúng trạng thái: Chờ lô / Đang xử lý / Thành công / Thất bại | Khớp DB |
| AC-10 | Đối soát | Báo cáo theo lô khớp log AT Core (số lệnh, tổng tiền, trạng thái) | Khớp 100% |
| AC-11 | Vận hành | Feature flag tắt được chi tự động, quay về luồng thủ công | Test bật/tắt pass |
| AC-12 | Smoke | 100% testcase trong file smoke test luồng rút tiền TPBank pass | Pass |

**Điều kiện ký:** AC-01, AC-02, AC-03, AC-06, AC-08 đạt 100%. Không còn bug Critical/Major.

### Giai đoạn 4 — Deploy & cutover (19/10 → 22/10)

**Chuẩn bị (19–21/10)**

| # | Công việc | PIC | Phối hợp | Thời gian |
|---|---|---|---|---|
| 4.1 | Kiểm tra cấu hình Production: partner code `TPBANK_MSHT`, key, endpoint AT Core prod, cron 5 khung giờ, flag mặc định TẮT | DevOps | Dev Lead | 20/10 |
| 4.2 | AT xác nhận phía AT Core/TPBank Production sẵn sàng nhận lô từ MSHT (cert HSM còn hạn, dịch vụ TP đã mở) | Ngọc Thảo | AT Core | 20/10 |
| 4.3 | **Kỳ chi thủ công cuối T4 21/10:** MSHT xuất file như thường lệ → Kế toán AT chi → gửi kết quả | PM | Kế toán AT | 21/10 |
| 4.4 | MSHT import kết quả kỳ 21/10 **trước Go/No-Go ngày 22/10** | PM | Dev | 22/10 sáng |

**Ngày release 22/10**

| # | Bước | Người làm | Xác nhận |
|---|---|---|---|
| 1 | **Go/No-Go**: checklist mục 7, đã import xong kết quả kỳ thủ công cuối | PM | Dev Lead, QC, Ngọc Thảo |
| 2 | Thông báo bắt đầu release trên group nội bộ + Slack với AT | PM | — |
| 3 | Backup DB, deploy Production, chạy migration | DevOps | Dev Lead |
| 4 | Smoke test production theo file smoke test (flag vẫn TẮT) | QC | PM |
| 5 | Rà danh sách lệnh "Chờ lô": chỉ còn lệnh chưa chi thủ công | Dev Lead | PM |
| 6 | **Bật flag chi tự động** | DevOps | PM |
| 7 | **Lô production đầu tiên:** theo dõi realtime, đối chiếu với AT Core | Dev Lead | AT Core |
| 8 | AT/Biz xác nhận tiền về TK user của lô đầu tiên | Ngọc Thảo | AT |
| 9 | Lô thứ 2: theo dõi và đối chiếu | Dev Lead | AT Core |
| 10 | **Ngọc Thảo xác nhận với AT: dừng chi thủ công** (M6). Thông báo hoàn tất | Ngọc Thảo | PM |
| 11 | Các lô tối và đêm: alert tự động, Dev trực on-call | Dev trực | — |

**Rollback** (khi lô lỗi, chi trùng, sai tiền, hoặc AT báo bất thường):
1. Tắt flag chi tự động. Yêu cầu mới quay về Pending như Phase 1.
2. Đối chiếu với AT từng lệnh đã gửi trong lô lỗi.
3. AT tiếp tục chi thủ công theo kỳ T2/T4 cho tới khi fix xong.
4. Rollback code chỉ khi lỗi ảnh hưởng luồng rút tiền chung.

**Sau release (23/10 → 30/10):** Dev Lead đối soát log lô với AT mỗi sáng trong 1 tuần, kể cả các lô cuối tuần. PM gửi báo cáo ngắn cho Biz/AT.

---

## 5. Phân vai & trách nhiệm các bên

### 5.1 Các bên tham gia

| Bên | Vai trò | Người | Trách nhiệm chính |
|---|---|---|---|
| Diso / MSHT | PM / Product | **Huyền** | Lập & theo dõi kế hoạch, chủ trì Go/No-Go, ký nghiệm thu, đầu mối nội bộ với Ngọc Thảo/AT |
| Diso / MSHT | Người bàn giao | Huyền | Bàn giao hiện trạng, hỗ trợ PM trong tuần đầu khi cần tra lại lịch sử trao đổi với AT |
| Diso / MSHT | Dev Lead / Dev BE | Trung | Code batch, deploy, đối chiếu log, trực sau release |
| Diso / MSHT | QC | Huyền | Testcase, test DEV, nghiệm thu E2E, smoke test production |
| Diso / MSHT | DevOps | Trung | Cấu hình prod, cron, flag, backup/rollback |
| Biz | Account / đầu mối AT | Ngọc Thảo | Gửi kế hoạch cho AT, chốt thời điểm dừng chi thủ công, kênh escalate với AT |
| AT-Core | AT Core / HSM | Dev AT-Core | API batch, ký HSM, môi trường DEV/Prod, xác nhận giao dịch, trực ngày release |
| AT-MSHT | Nghiệp vụ | Quỳnh | Xác nhận nghiệp vụ, ngưỡng chi hộ, nghiệm thu phía AT |
| AT-MSHT | Kế toán | Hằng | Chi thủ công kỳ cuối 21/10, gửi kết quả, đối soát sau release |
| TPBank | Ngân hàng | Làm việc **qua AT** | Mở dịch vụ chi hộ cho MSHT (đã mở 12/10), thực hiện chuyển tiền |

### 5.2 Cam kết của từng bên

**Diso / MSHT**
- Chỉ gọi AT Core theo lô ở 5 khung giờ. Không gọi lẻ, không truy vấn trạng thái ngoài số lần đã chốt (để không phát sinh phí HSM).
- Tuân thủ ngưỡng 30 GD/giờ, 10.000.000đ/giờ, 100 GD/ngày, 10.000đ tối thiểu, 1.900.000đ/ngày và /tháng mỗi user.
- Bảo đảm không chi trùng giữa luồng thủ công và luồng tự động.
- Bảo mật key `TPBANK_MSHT`; trực theo dõi các lô trong 1 tuần sau release.
- Báo AT ngay khi phát hiện lô lỗi; có flag để quay về chi thủ công.

**AT (AccessTrade)**
- Đảm bảo cert HSM còn hạn và AT Core sẵn sàng trên DEV (ngày 21/10) và Production (ngày 22/10).
- Cử người trực nghiệm thu ngày **21/10** và theo dõi các lô đầu tiên ngày **22/10**.
- Kế toán AT chi kỳ thủ công cuối ngày 21/10 và gửi kết quả trước Go/No-Go ngày 22/10. **Dừng chi thủ công sau khi Ngọc Thảo xác nhận.**
- Làm đầu mối với TPBank cho mọi vấn đề phía ngân hàng.

**TPBank (qua AT)**
- Duy trì dịch vụ chi hộ đã mở cho tài khoản MSHT.
- Báo trước cho AT khi thay đổi key, cert hay hạn mức. Sự cố tắt self key trước đây chính là do thiếu bước báo này.

**Biz (Ngọc Thảo)**
- Gửi kế hoạch cho AT ngày 16/10. Giữ kênh escalate với AT khi bị chặn.
- Chốt thời điểm dừng chi thủ công và thông báo cho các bên.

---

## 6. Rủi ro & phương án

| # | Rủi ro | Mức | Phương án |
|---|---|---|---|
| R1 | 2 ngày code sát; phát sinh lỗi khi tích hợp lô với AT Core DEV | Cao | Dev tập trung 100% cho dự án 16–19/10; test sớm với AT Core DEV từ chiều 19/10; nếu trễ thì báo ngay để dời M1 sang 20/10 sáng |
| R2 | **Chi trùng** giữa kỳ thủ công 21/10 và lô tự động đầu tiên | Cao | Import kết quả trước Go/No-Go 22/10; rà "Chờ lô" trước khi bật flag; AC-08 |
| R3 | Cert HSM của AT hết hạn lần nữa (đã từng xảy ra) | TB | AT xác nhận hạn cert ở bước 4.2; alert khi AT Core trả lỗi ký số |
| R4 | Tồn đọng lệnh vượt 100 GD/ngày → user chờ lâu | TB | Báo cáo lệnh dồn hằng ngày; nếu tồn đọng kéo dài, đề xuất AT/TP nâng ngưỡng |
| R5 | User nhập sai tên/số TK (không có API check) → chi thất bại | TB | Xử lý lệnh thất bại theo quy tắc đã thống nhất với AT; message hướng dẫn user |
| R6 | Phí HSM phát sinh do truy vấn trạng thái quá nhiều | TB | Giới hạn số lần truy vấn/lô; theo dõi số lần gọi qua log |
| R7 | Timeline 5 ngày làm việc rất sát, không có buffer | Cao | Release trong giờ hành chính để có buffer trong ngày; nếu M3 trễ thì dời release sang 23/10 (T6), **không** release cuối tuần |

## 7. Checklist Go/No-Go (22/10)

- [ ] Biên bản nghiệm thu E2E đã có xác nhận của AT (M3)
- [ ] 0 bug Critical/Major mở
- [ ] Kết quả kỳ chi thủ công 21/10 đã import xong
- [ ] AT Core Production sẵn sàng, cert HSM còn hạn (AT xác nhận)
- [ ] Cấu hình prod đúng: partner code, key, endpoint, cron 5 khung giờ, flag mặc định TẮT
- [ ] Đã test bật/tắt flag; kịch bản rollback rõ ràng
- [ ] Người trực ngày release và các lô tối/đêm đã chốt; AT Core xác nhận trực các lô đầu tiên
- [ ] Đã thông báo lịch release cho Biz/AT

## Lịch sử cập nhật

| Phiên bản | Ngày | Người cập nhật | Nội dung |
|---|---|---|---|
| v1.0 | 15/10/2026 | Huyền (PM) | Lập kế hoạch theo tài liệu transfer, khung 15/10 → 22/10 |
| v1.1 | 16/10/2026 | Huyền (PM) | Bỏ giai đoạn tiếp nhận & chốt batch (đã clear chi theo lô với AT); bỏ ma trận RACI |
| v1.2 | 16/10/2026 | Huyền (PM) | Bỏ bảng thông tin chung & mục ghi nhận PM; bỏ giờ ở ngày release; bỏ kênh liên lạc |
