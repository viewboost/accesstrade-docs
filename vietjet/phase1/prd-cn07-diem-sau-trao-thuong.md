# CN-07 · Điều chỉnh trừ điểm sau đối soát

**Date:** 2026-11-17 · **Author:** Vinh Nguyễn · **Version:** 0.4 · **Status:** Không làm

**Mục lục chung:** [README.md](./README.md)

## CN-07.1 Kết luận

**Không làm chức năng này.** Chốt ngày 17/11/2026.

Lý do:
- Điểm là điểm **bên trong chương trình** (thống kê người dùng theo sự kiện). Mỗi tháng là một chương trình riêng, bảng xếp hạng và đối soát đều lấy điểm trong chương trình đó.
- Đối soát trao giải làm **một lần ở cuối chương trình**. Gian lận phát hiện trước lúc đó xử lý bằng cách **từ chối bài**: khoản thưởng của bài về trạng thái từ chối, điểm không còn tính, bảng xếp hạng và file kết quả cuối chương trình tự đúng.
- Sau khi đối soát cuối chương trình và xuất file, Operation trao quà bên ngoài hệ thống; việc xử lý sai sót sau đó làm tay bên ngoài.

Không còn quy tắc nào của chức năng này. Quy tắc "điểm chỉ tích lũy trong chương trình của nó, không cộng qua chương trình khác" nằm ở [CN-06](./prd-cn06-muc-thuong-cuoi-ky.md) (CN06-BR12).
