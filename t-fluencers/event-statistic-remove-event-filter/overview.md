# Overview: Bỏ lọc thống kê theo thử thách (event) ở API public (T-Fluencers)

**Date:** 2026-05-26
**Project:** T-Fluencers (Techcombank)
**Status:** Draft

## Vấn đề

API public `GET /events/statistic` cho phép truyền `event_id` (mã thử thách) để lấy thống kê **của riêng một thử thách**: số video được duyệt (`totalContent`), tổng lượt xem (`totalView`), tổng hoa hồng (`totalCommission`), số influencer có bài đăng (`totalUserWithContent`).

Endpoint này là **public** (middleware `auth.Auth` chỉ parse JWT optional, không bắt buộc login). Bất kỳ ai biết một `event_id` đều gọi được và đọc số liệu chi tiết của thử thách đó — có thể enumerate nhiều `event_id` để gom số liệu toàn bộ.

**Số liệu theo từng thử thách là thông tin business nhạy cảm** (hoa hồng đã chi, độ phủ bài đăng của thử thách) — không nên để public user biết.

> Đây là vấn đề **chung của cả 3 sản phẩm fork cùng nguồn** (vcreator, ambassador, techcombank). T-Fluencers là fork của vcreator (vcreator gốc 2024-10, TCB fork 2025-10) nên có cùng pattern và chưa cherry-pick fix nếu vcreator sửa.

## Mục tiêu

Public user **không** xem được thống kê theo từng thử thách. API chỉ trả số liệu **tổng hợp** (theo domain / partner).

## Phạm vi

- **CÓ:** Gỡ tác dụng param `event` ở endpoint public `/events/statistic`.
- **KHÔNG:** Đụng API admin (admin xem chi tiết theo thử thách — hợp lệ).
- **KHÔNG:** Đổi shape response, không thêm yêu cầu login.
- **KHÔNG:** Đụng filter `partner` (hợp lệ).

## Quyết định

Chi tiết kỹ thuật: xem [`tech-spec.md`](./tech-spec.md).

Tóm tắt: bỏ gán `param.Event` vào query trong handler `GetStatistic` → `AssignEvent` tự no-op → số liệu thành tổng hợp. Giữ nguyên struct/validation chung (vì `/events/user-newest` còn dùng). Bỏ chiều `event` khỏi cache key.
