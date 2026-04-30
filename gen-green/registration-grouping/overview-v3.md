# Overview V3 — Registration Grouping (Shipped Summary)

**Date:** 2026-04-30
**Status:** ✅ V3 hoàn thành toàn bộ scope
**Source:**
- PRD V1: [prd-registration-v1-2026-04-12.md](prd-registration-v1-2026-04-12.md)
- PRD V2: [prd-registration-v2-2026-04-12.md](prd-registration-v2-2026-04-12.md)
- PRD V3: [prd-registration-v3-2026-04-30.md](prd-registration-v3-2026-04-30.md)
- Meeting 0410: [meeting-notes/0410.md](../meeting-notes/0410.md)

---

## Trạng thái tổng kết

| Module | Items | Status |
|---|---|---|
| 🎥 Tab Nội dung (`/content`) | 4 | ✅ 4/4 |
| 👤 Tab Creator (`/user-partner`) | 6 | ✅ 6/6 |
| 📤 Export (Column Picker) | 4 | ✅ 4/4 |
| 🔧 Backend V2 (Employee Registry) | 2 | ✅ 2/2 |

**Tất cả tasks V3 đã ship.**

---

## 🎥 Module 1: Tab Nội dung (`/content`)

| FR | Item |
|---|---|
| FR-V3-001 | Filter 3-tier workplace cascading |
| FR-V3-002 | Cột Loại tài khoản (CBNV) |
| FR-V3-003 | Cột Cơ sở làm việc (gộp Phân loại) |
| FR-V3-004 | Cột Hashtag cá nhân |

---

## 👤 Module 2: Tab Creator (`/user-partner`)

| FR | Item |
|---|---|
| FR-V3-005 | Filter 3-tier workplace |
| FR-V3-006 | Filter Phân loại CBNV |
| FR-V3-007 | Cột Cơ sở làm việc (gộp Phân loại) + Hashtag |
| FR-V3-008 | Ẩn cột Ngày tạo, giữ Ngày tham gia |
| FR-V3-009 | Cột Tổng view |
| FR-V3-010 | Cột Tổng video đã nộp |

Layout fix: scroll x=1450, Tên + STT pin trái, Action pin phải.

---

## 📤 Module 3: Export Column Picker

| FR | Item |
|---|---|
| FR-V3-011 | Column picker UI Tab Nội dung (25 cột, default tất cả tick) |
| FR-V3-012 | Backend `/content` subset columns |
| FR-V3-013 | Column picker UI Tab Creator (full 19 / brief 8 cột) |
| FR-V3-014 | Backend `/user-partner` subset + 2 cột mới (Phân loại / Cơ sở) |

Pattern positional indexing sync giữa BE (Go switch case) và FE (CONTENT_COLUMNS / USER_PARTNER_COLUMNS).

---

## 🔧 Module 4: Backend V2 (Employee Registry)

| FR | Item |
|---|---|
| FR-V3-018 | Workplace Group Derive — exact match `workplace_units.name` |
| FR-V3-019 | Scope filter rà soát 3-tier (Brand / Company / Unit), apply cấp nhỏ nhất |

Apply ở 5 paths: NewRecord insert/revive, upsertRegistryAndLink, WorkplaceUpdated, RegistryUpdated. Thêm index `workplaceBrandCode` cho perf detect missing.

Demo files: [sample-step1-initial.xlsx](sample-step1-initial.xlsx), [sample-step2-missing-detect.xlsx](sample-step2-missing-detect.xlsx).

---

## Mapping tới spec gốc

| Module | EPIC | PRD ref |
|---|---|---|
| Tab Nội dung | EPIC-005 (V1) / EPIC-V3-A | [prd-v1](prd-registration-v1-2026-04-12.md#EPIC-005) |
| Tab Creator | EPIC-006 (V1) / EPIC-V3-B | [prd-v1](prd-registration-v1-2026-04-12.md#EPIC-006) |
| Export | EPIC-007 (V1) / EPIC-V3-C | [prd-v1](prd-registration-v1-2026-04-12.md#EPIC-007) |
| Backend V2 | EPIC-001 (V2) / EPIC-V3-D | [prd-v2](prd-registration-v2-2026-04-12.md), [prd-v3](prd-registration-v3-2026-04-30.md) |
