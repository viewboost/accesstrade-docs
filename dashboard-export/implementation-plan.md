# Implementation Plan: Dashboard Export Page (Option C — Full-featured)

**Ngày:** 2026-02-25
**Scope:** Backend (Go) + Frontend Dashboard (Next.js)

---

## Tổng Quan Kiến Trúc

```
Dashboard User
    → GET /data-exports?type=dashboard_multi&createdBy=[auto từ token]
    → Poll status mỗi 5s khi có job running
    → GET /data-exports/:id/pre-sign → download URL
```

**Lưu ý thiết kế:**
- `createdBy` **không phải query param từ client** — backend tự lấy từ `staffId` trong JWT context, không để client tự set (security)
- Route dashboard dùng **admin JWT token** (Dashboard đang auth bằng Admin token rồi — xem `api.ts` + `auth.ts`)
- Backend cần thêm logic: nếu call `GET /data-exports` với `filterByOwner=true`, chỉ trả về jobs của chính staffId đó

---

## Phase 1: Backend

### 1.1 Thêm filter `createdBy` vào `GET /data-exports`

**File:** `pkg/admin/model/request/export.go`

Thêm field vào `DataExportAll`:
```go
type DataExportAll struct {
    Page         int64  `query:"page"`
    Limit        int64  `query:"limit"`
    Status       string `query:"status"`
    Type         string `query:"type"`
    Keyword      string `query:"keyword"`
    Sort         string `query:"sort"`
    Partner      string `query:"partner"`
    FilterByOwner bool  `query:"filterByOwner"`  // NEW: nếu true, chỉ lấy jobs của mình
}
```

**File:** `pkg/admin/service/export.go` — `GetList()`

Thêm filter trong `GetList`:
```go
if q.FilterByOwner {
    cond["createdBy"] = staffId
}
```

**File:** `internal/util/mgquery/query.go` (hoặc tương đương)

Thêm method `AssignFilterByOwner` nếu dùng pattern chung, hoặc xử lý trực tiếp trong service.

### 1.2 Verify ownership trong `GetPreSign`

`GetPreSign` đã check `e.Staff.Partner.Hex() != doc.Partner.Hex()` — đủ bảo vệ cho context Dashboard (user cùng partner). Không cần thay đổi.

Tuy nhiên, nên thêm check `createdBy` nếu muốn strict hơn:
```go
// Nếu không phải root và không phải người tạo → từ chối
if !e.Staff.IsRoot && doc.CreatedBy.Hex() != staffId.Hex() {
    return "", errors.New(locale.CommonKeyNoPermission)
}
```

### 1.3 Route validation

**File:** `pkg/admin/router/routevalidation/export.go`

Cập nhật `All()` để bind `FilterByOwner` field mới (đã tự động qua `c.Bind` nếu dùng struct tag `query`).

---

## Phase 2: Frontend — Service Layer

### 2.1 Thêm API calls vào `src/lib/api.ts` (hoặc tạo `src/lib/exports-api.ts`)

```typescript
// Types
export interface ExportJob {
  _id: string;
  name: string;
  type: string;
  status: 'waiting' | 'running' | 'completed' | 'failed';
  isScheduled: boolean;
  reason: string;
  createdAt: { value: string };
  updatedAt: { value: string };
}

export interface ExportListResponse {
  list: ExportJob[];
  total: number;
  limit: number;
}

// API functions
export async function getExports(page = 1, limit = 20): Promise<ExportListResponse> {
  const res = await api.get('/data-exports', {
    params: {
      type: 'dashboard_multi',
      filterByOwner: true,
      page,
      limit,
    },
  });
  return res.data.data;
}

export async function getExportPreSign(id: string): Promise<string> {
  const res = await api.get(`/data-exports/${id}/pre-sign`);
  return res.data.data;
}
```

---

## Phase 3: Frontend — Hook

### 3.1 `src/hooks/use-exports.ts`

```typescript
'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { getExports, getExportPreSign, type ExportJob } from '@/lib/api';

const POLL_INTERVAL = 5000;

export function useExports(page: number) {
  const [jobs, setJobs] = useState<ExportJob[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchJobs = useCallback(async () => {
    const data = await getExports(page);
    setJobs(data.list);
    setTotal(data.total);
    setIsLoading(false);

    // Auto-poll nếu có job đang chạy
    const hasRunning = data.list.some(j => j.status === 'waiting' || j.status === 'running');
    if (hasRunning && !pollRef.current) {
      pollRef.current = setInterval(fetchJobs, POLL_INTERVAL);
    } else if (!hasRunning && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, [page]);

  useEffect(() => {
    fetchJobs();
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [fetchJobs]);

  return { jobs, total, isLoading, refetch: fetchJobs };
}

export function useExportDownload() {
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const download = async (id: string) => {
    setLoadingId(id);
    try {
      const url = await getExportPreSign(id);
      if (url) window.open(url, '_blank');
    } finally {
      setLoadingId(null);
    }
  };

  return { download, loadingId };
}
```

---

## Phase 4: Frontend — Components

### 4.1 `src/components/exports/export-list.tsx`

Table columns:
| Cột | Mô tả |
|-----|-------|
| Tên file | `name` |
| Trạng thái | Badge: `waiting` (xám) / `running` (xanh, spinner) / `completed` (xanh lá) / `failed` (đỏ) |
| Thời gian tạo | `createdAt` formatted |
| Hành động | Download button (chỉ enable khi `completed`) |

### 4.2 Notification khi job done

Option: Dùng polling trong hook + so sánh status cũ/mới → toast khi job chuyển `running → completed`.

Hoặc: Thêm `useExportNotification` hook tách riêng để persist qua navigation.

---

## Phase 5: Frontend — Route

### 5.1 Tạo route `src/app/[locale]/exports/page.tsx`

```typescript
// Route sẵn sàng — sidebar sẽ link vào sau
export default function ExportsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-[1440px] mx-auto p-6">
        <ExportsContent />
      </div>
    </div>
  );
}
```

**Lưu ý:** Chưa cần link trong nav — sidebar sẽ được thêm ở nhánh khác sau.

---

## Thứ Tự Triển Khai

```
[1] Backend: thêm FilterByOwner vào request struct + service GetList
[2] Backend: (optional) strict check createdBy trong GetPreSign
[3] Frontend: thêm getExports + getExportPreSign vào api layer
[4] Frontend: viết useExports hook với polling
[5] Frontend: tạo ExportList component (table + status badge + download)
[6] Frontend: tạo route /exports/page.tsx
[7] Frontend: notification toast khi job completed
[8] Test end-to-end
```

---

## Câu Hỏi Còn Mở

| # | Câu hỏi | Đề xuất |
|---|---------|---------|
| 1 | Badge notification trên header khi có job done? | Làm cùng lúc với route, để slot sẵn cho sidebar |
| 2 | i18n keys cho trang exports? | Thêm vào messages hiện có |
| 3 | Trang exports có cần filter thêm (status, date)? | Giai đoạn 1: không, chỉ list đơn giản |

---

*Plan: 2026-02-25*
