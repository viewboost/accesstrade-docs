# Overview: Bỏ lọc thống kê theo event ở API public (Ambassador)

**Date:** 2026-05-26
**Project:** Ambassador (codename `viewboost`)
**Status:** Draft

## Vấn đề

API public `GET /events/statistic` cho phép truyền `event_id` (cùng `category`, `partner`, `fromAt/toAt`) để lấy thống kê **của riêng một event**: số video được duyệt (`totalContent`), tổng view (`totalView`), tổng hoa hồng (`totalCommission`), số user có content (`totalUserWithContent`).

Endpoint này là **public** (middleware `auth.Auth` chỉ parse JWT nếu có, không bắt buộc login, không enforce API key cứng). Bất kỳ ai biết một `event_id` đều gọi được và đọc số liệu business chi tiết của campaign đó — thậm chí có thể enumerate nhiều event_id để gom số liệu toàn bộ.

**Số liệu theo từng event là thông tin business nhạy cảm** (hoa hồng đã chi, độ phủ content của campaign) — không nên để public user biết.

> Đây là vấn đề **chung của cả 3 sản phẩm fork cùng nguồn** (vcreator, ambassador, techcombank). Ambassador có cùng pattern.

## Mục tiêu

Public user **không** xem được thống kê theo từng event. API chỉ trả số liệu **tổng hợp** (theo domain / partner / category nếu có).

## Phạm vi

- **CÓ:** Gỡ tác dụng param `event` ở endpoint public `/events/statistic`.
- **KHÔNG:** Đụng API admin (admin xem chi tiết theo event — hợp lệ).
- **KHÔNG:** Đổi shape response, không thêm yêu cầu login.
- **KHÔNG:** Đụng các filter hợp lệ khác (`partner`, `category`, `fromAt/toAt`).

## Quyết định

Chi tiết kỹ thuật: xem [`tech-spec.md`](./tech-spec.md).

Tóm tắt: bỏ gán `param.Event` vào query trong handler `GetStatistic` → `AssignEvent` tự no-op → số liệu thành tổng hợp. Giữ nguyên struct/validation chung (vì `/events/user-newest` còn dùng). Bỏ chiều `event` khỏi cache key.
