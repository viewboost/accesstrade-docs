# Overview: Bỏ lọc thống kê theo event ở API public

**Date:** 2026-05-26
**Project:** Gen-Green (vcreator)
**Status:** Draft

## Vấn đề

API public `GET /events/statistic` cho phép truyền `event_id` để lấy thống kê **của riêng một event**: số video được duyệt (`totalContent`), tổng view, tổng hoa hồng (`totalCommission`), số user có content.

Endpoint này là **public** (chỉ cần API key mức app, không cần login). Ai biết một `event_id` đều đọc được số liệu chi tiết của campaign đó — đây là **thông tin business nhạy cảm không nên để public user biết**.

## Mục tiêu

Public user **không** xem được thống kê theo từng event. API chỉ trả số liệu **tổng hợp toàn hệ thống** (theo domain / partner).

## Phạm vi

- **CÓ:** Gỡ tác dụng param `event` ở endpoint public `/events/statistic` (backend-public).
- **KHÔNG:** Đụng API admin (admin vẫn xem chi tiết theo event — hợp lệ).
- **KHÔNG:** Đổi shape response, không thêm yêu cầu login.

## Quyết định

Cách xử lý kỹ thuật chi tiết: xem [`tech-spec.md`](./tech-spec.md).

Tóm tắt: bỏ gán `param.Event` vào query trong handler `GetStatistic` → `AssignEvent` tự no-op → số liệu thành tổng hợp. Giữ nguyên struct/validation chung (vì `/events/user-newest` còn dùng). Bỏ chiều `event` khỏi cache key.
