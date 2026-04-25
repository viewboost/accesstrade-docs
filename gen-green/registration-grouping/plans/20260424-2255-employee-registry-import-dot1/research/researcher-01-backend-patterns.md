# Gen-Green Employee Registry Import — Backend Patterns Research

**Date:** 2026-04-24 | **Project:** vcreator backend (Go) | **Scope:** MongoDB, MinIO, Asynq, Audit patterns

---

## 1. MongoDB Model + DAO Pattern

**Files đã đọc:**
- `internal/model/mg/user.go` (UserRaw, UserDAO interface)
- `internal/model/mg/audit.go` (AuditRaw, AuditDAO interface)  
- `internal/module/database/mongodb/collection.go` (collection constants)
- `internal/module/database/mongodb/dao/audit.go` (AuditDAO implementation)

**Convention:**
- Model struct: `XxxRaw` suffix (e.g., `UserRaw`, `AuditRaw`), uses `bson` tags for DB field mapping
- DAO interface: minimal, only requires `GetShare()` returning `databasemongodb.IDatabase`
- Collection name: const `Collection<Name>` in `mongodb/collection.go`
- Primary key: `_id` → `primitive.ObjectID` hoặc `modelmg.AppID` (custom type)
- Methods on model: `DbModelName()` returns collection constant; helper methods like `IsProfileCompleted()` for logic
- DAO registration: factory function `XxxDAO()` returns interface impl, injected via `databasemongodb.GetDBShare()`

**Code snippet (EmployeeRegistry model example):**
```go
type EmployeeRegistryRaw struct {
	ID              modelmg.AppID `bson:"_id"`
	EmployeeCode    string        `bson:"employeeCode"`
	Email           string        `bson:"email"`
	RegisteredAt    time.Time     `bson:"registeredAt"`
	VerifiedAt      *time.Time    `bson:"verifiedAt,omitempty"`
	Status          string        `bson:"status"` // pending, approved, rejected
}

func (e *EmployeeRegistryRaw) DbModelName() string {
	return databasemongodb.CollectionEmployeeRegistry // = "employee-registries"
}

type EmployeeRegistryDAO interface {
	GetShare() databasemongodb.IDatabase
}
```

**Index creation:** Defined in `mongodb/index.go` using `process()` method, called on module init

**Ứng dụng cho Employee Registry:**
- Tạo `EmployeeRegistryRaw` struct với fields: employeeCode, email, phone, workplaceBrandCode, unit, status
- Thêm const `CollectionEmployeeRegistry = "employee-registries"` vào `collection.go`
- Tạo DAO factory: `func EmployeeRegistryDAO() modelmg.EmployeeRegistryDAO`
- Index trên (employeeCode, email) để avoid duplicates

---

## 2. MinIO File Upload

**Files đã đọc:**
- `internal/echo/upload_file.go` (UploadSingle, UploadArray middleware)
- `pkg/file/service/file.go` (FileInterface, bucket handling, presigned URLs)

**Convention:**
- Middleware nhận multipart form field `"file"` hoặc `"files"`, extract to local temp folder (`constants.FolderUpload`)
- File info struct: `modelmg.FileInfo{Filename, FileNameOrigin, Path, Ext, Size, ContentType}`
- Bucket abstraction: `modelmg.BucketName{Minio: bucketName, IsPreSigned: bool}`
- Upload flow: local temp → validate (ext, size) → resize (if image) → MinIO PutObject → save DB → cleanup
- Validation constants: `constants.ExtensionPhotoValid`, `constants.MaxSizePhoto`
- URL generation: presigned if `IsPreSigned=true`, else direct `config.GetENV().FileHost/bucketName/filename`

**Code snippet (file service pattern):**
```go
const (
	FolderUpload         = "/uploads/"
	ExtensionPhotoValid  = ".jpg,.png,.jpeg"
	MaxSizePhoto         = 10 * 1024 * 1024 // 10MB
)

// Bucket config
var BucketEmployeeRegistry = modelmg.BucketName{
	Minio:      "employee-registry",
	IsPreSigned: false, // public access
}

// Upload in service
result, err := fileService.UploadFile(ctx, modelmg.FileInfo{
	Filename:       "registry_001.csv",
	FileNameOrigin: "registry.csv",
	Path:           "/tmp/uploads/registry.csv",
	Ext:            "csv",
	Size:           15000,
})
```

**Ứng dụng cho Employee Registry:**
- CSV upload: khởi tạo separate bucket `employee-registry-uploads` hoặc reuse existing
- Validation: `.csv` extension + size limit (e.g., 50MB)
- File stored with timestamp prefix: `20260424_001_registry.csv`
- Presigned URL không cần (internal admin import)

---

## 3. Asynq Background Job

**Files đã đọc:**
- grep search: `TaskType`, `asynq.Task`, `HandleFunc` — **không tìm thấy ví dụ cụ thể trong codebase này**
- Nhưng pattern sẽ tương tự như other Go projects

**Inferred Convention (từ codebase best practices):**
- Task type: const string `TaskTypeEmployeeRegistryImport = "employee:registry:import"`
- Payload struct: JSON-serializable, e.g., `ImportRegistryPayload{FileID string, BatchID string}`
- Enqueue: `client.Enqueue(asynq.NewTask(TaskTypeEmployeeRegistryImport, payload))`
- Handler register: `mux.HandleFunc(TaskTypeEmployeeRegistryImport, HandleEmployeeRegistryImport)`
- Handler signature: `func(ctx context.Context, t *asynq.Task) error`

**Code snippet (Asynq pattern):**
```go
const TaskTypeEmployeeRegistryImport = "employee:registry:import"

type ImportRegistryPayload struct {
	FileID  string `json:"fileId"`
	BatchID string `json:"batchId"`
}

// Enqueue
payload, _ := json.Marshal(ImportRegistryPayload{FileID: fileID, BatchID: batchID})
client.Enqueue(asynq.NewTask(TaskTypeEmployeeRegistryImport, payload))

// Handler
func HandleEmployeeRegistryImport(ctx context.Context, t *asynq.Task) error {
	var p ImportRegistryPayload
	json.Unmarshal(t.Payload(), &p)
	// process CSV, insert to DB
	return nil
}
```

**Ứng dụng cho Employee Registry:**
- Task type: `employee:registry:import` chạy CSV parse + batch insert
- Priority queue: có thể dùng retry mechanism nếu parse fail
- Audit log: emit event khi task complete/fail

---

## 4. Audit + Root Account Pattern

**Files đã đọc:**
- `internal/service/audit.go` (CreateAudits, CreatePayload methods)
- `internal/model/mg/audit.go` (AuditRaw struct)

**Convention:**
- Audit payload: `TargetId` (user ID), `Data` (stringified), `Message` (human), `ActionBy` (staff ID), optional `BatchId`
- Service: batch create via `CreateAudits()` → insert many to DB
- Caller layer: build payload array via `CreatePayload()` helper, then pass to service
- Timestamp: auto-set to `time.Now()` in service

**Code snippet (audit propagation):**
```go
// In user verification service
func VerifyStaff(ctx context.Context, staffID modelmg.AppID, userID modelmg.AppID) error {
	auditPayloads := internalservice.Audit().CreatePayload(
		userID, 
		staffID, 
		map[string]string{"status": "verified"},
		"Staff verified via employee registry",
	)
	return internalservice.Audit().CreateAudits(ctx, auditPayloads)
}
```

**Root staff query pattern:** Lấy staff từ constant hoặc config (e.g., system admin ID)

**Ứng dụng cho Employee Registry:**
- Mỗi successful import: create audit với `ActionBy = system_admin_id`, `Message = "Bulk import from CSV"`
- Per-user approve/reject: create separate audit entries
- Batch tracking: use `BatchId` để group related audits

---

## Unresolved Questions

1. **Asynq** — Không tìm thấy concrete queue configuration. Có queue riêng cho import jobs không? Max retries?
2. **MinIO bucket staging** — CSV upload tới bucket nào trước khi process? Separate staging bucket hay main bucket?
3. **Workplace hierarchies** — UserRaw có fields: `WorkplaceBrandCode`, `WorkplaceCompanyCode`, `WorkplaceUnitCode`. Này có models/DAOs riêng không?
4. **Bulk verification** — Staff verification workflow: admin duyệt list từ CSV? Hay tự động approve base on rules?
5. **CSV schema** — Expected columns: EmployeeCode, Email, Phone, Name, Brand, Company, Unit?
