# ADR-0004 — Storage và batch jobs

Ngày: 01/10/2026. Trạng thái: accepted design.

## Quyết định

PostgreSQL cho observations/registry/predictions/outcomes; raw/Parquet/model files trong volume với manifest/hash. Một scheduler ngoài API gọi CLI; DB lock và unique constraints chống trùng. Không dựng queue broker ở MVP.

## Lý do

Tác vụ theo ngày phù hợp batch; lưu raw/snapshot giúp tái lập. DB transaction bảo vệ nghiệp vụ còn artifacts không cần nhét vào row lớn. Scheduler trong từng API worker dễ sinh job trùng.

## Hệ quả

Cần quản lý orphan files, retention và backup cả DB lẫn artifacts. Queue không tự giải quyết idempotency. Redis/Celery chỉ thêm khi job volume/duration/concurrency yêu cầu.

## Xem xét lại

Nhiều worker/máy chia sẻ artifact hoặc retry/queue vượt điều phối hiện tại; xem object storage và broker bằng ADR mới.
