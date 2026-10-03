# Runbook — kế hoạch vận hành và thao tác hiện có

**Trạng thái:** chưa deploy ứng dụng. Mọi phần production dưới đây là quy trình cần hiện thực/diễn tập trong GS-013/014, không phải dịch vụ đang chạy.

## 1. Đang có thể làm

Chạy unittest Lab 00 từ root theo TESTING.md. Chạy audit nhập ẩn theo README nếu người dùng có key. Giữ report trong runtime và so trạng thái từng probe; đừng coi exit 2 của audit là test failure hoặc data success.

## 2. Checklist trước lần chạy ứng dụng đầu

- Package/lockfile có thật, CI tương ứng đạt.
- PostgreSQL và migrations chạy trên database đúng môi trường.
- Source contract đã audit, keys có quyền và được nạp qua cơ chế secret.
- Paths/volumes có quyền ghi, backup destination có đủ dung lượng.
- Có model artifact/hash/schema tương thích, hoặc baseline đã đăng ký.
- Lịch nguồn và forecast cutoff đã chốt hoặc giới hạn được công bố.
- Health, freshness, error logs và người vận hành đã được xác định.

Không làm checklist thành các giá trị “true” mặc định trong code. Mỗi mục cần evidence cụ thể.

## 3. Daily pipeline mục tiêu

Acquire lock → ingest → raw/quality → commit observations → create feature snapshot → check model/input eligibility → issue forecast → score matured predictions → finalize run → release lock.

Ghi status success/partial/failed/skipped, run_id, timestamps, counts, error code, model/snapshot IDs. Nếu một nguồn optional lỗi, chỉ tiếp tục với model vốn được thiết kế cho bộ feature sẵn có; không bỏ feature khỏi model active tùy ý.

Retry có giới hạn cho timeout/5xx/429, tôn trọng Retry-After. 401/403/schema mismatch cần điều tra, không loop retry. Một scheduler ngoài API; lock và unique constraints bảo vệ trùng job.

## 4. Forecast và scoring

Forecast live cần origin mới/hợp lệ, target chưa xảy ra, snapshot và model đúng schema. Giữ forecast cũ với nhãn stale nếu không có đầu vào mới; không đổi issued_at. Backfill luôn có mode riêng.

Score chỉ khi target observation h-th và availability đã đến; gắn actual revision. Không tự chọn giá gần nhất khác target để lấp outcome. Actual revision thay đổi tạo score_revision mới, giữ prediction nguyên trạng.

## 5. Training và promotion

Thực hiện giao thức ML_PROTOCOL. Candidate được kiểm tra load/hash/schema và metrics trên cửa sổ validation/shadow đã đăng ký. Promotion đầu do người quản trị kích hoạt bằng CLI, transaction registry giữ lịch sử. Nếu thua baseline/model hiện hành, giữ bản đang hoạt động và báo kết quả.

Không train lại ngay sau mỗi cảnh báo drift nếu chưa điều tra. Không tune bằng final holdout của release cũ lặp đi lặp lại.

## 6. Deploy mục tiêu

1. Xác định commit/image bất biến và môi trường đích đã được cho phép.
2. Kiểm tra secrets, config, hostname/network và backup.
3. Backup trước migration có rủi ro; chạy migration một lần.
4. Cập nhật image, readiness check, smoke market/forecast/UI.
5. Ghi release ID, image/model versions, thời gian và kết quả.

Ứng dụng rollback bằng image trước chỉ khi schema tương thích. Model rollback bằng deployment record trước. Database destructive migration không tự đảo ngược an toàn; phải có kế hoạch đã diễn tập.

Không có host, domain, registry, SSH target hay command deploy production đã được kiểm chứng trong gói hiện tại. GS-014 điền các mục này sau khi chọn hạ tầng; không tự điền IP hoặc credentials giả.

## 7. Backup và restore mục tiêu

- Dump PostgreSQL và sao lưu artifact/manifest được tham chiếu.
- Giữ backup ngoài host/ổ đĩa vận hành, checksum và retention policy.
- Diễn tập restore vào môi trường riêng, không ghi đè DB đang chạy.
- Kiểm tra row counts/FK, artifact hashes, model load và một forecast đọc được qua API.
- Ghi thời gian phục hồi thực đo, phạm vi dữ liệu mất nếu có. RPO/RTO chỉ chốt khi đã đo và chọn lịch backup.

`pg_dump`/`pg_restore` là công cụ dự kiến; connection/config thực tế phải do GS-013/014 tạo. Không ghi connection string có password vào tài liệu hay shell history.

## 8. Sự cố

| Triệu chứng | Kiểm tra | Hành động |
|---|---|---|
| API nguồn trả thông báo/429 | Quota/key/Retry-After | Dừng hoặc retry giới hạn; không ghi price=0 |
| Schema nguồn đổi | Raw sample/schema version | Chặn adapter, cập nhật/test mapping rồi backfill có log |
| Dữ liệu stale | Lịch nguồn/last success/availability | Giữ timestamp thật, chưa issue forecast mới |
| Model load lỗi | Version/hash/schema/dependency | Rollback model đã xác minh; ghi unavailable nếu không có |
| DB down | Connectivity/storage/health | Khôi phục phụ thuộc; không xóa DB để app khởi động |
| Job trùng | Scheduler/lock/idempotency | Loại lịch trùng; giữ unique constraints |
| Ổ đĩa đầy | Log/raw retention/artifact references | Dọn có chính sách; không xóa artifact còn dùng |
| Metric xấu | Outcome maturity/data quality/split | Điều tra, so baseline; không sửa lịch sử dự báo |

## 9. Metrics tối thiểu

Last successful ingestion, source freshness, rejected/duplicate/revision counts, job duration/status, API latency/error rate, model MAE/coverage/width khi outcomes đủ. Không gộp data freshness với process health để restart loop ngày nghỉ.

Trước release cần >=10 lượt job theo lịch có log (gồm skipped đúng nghĩa), một lỗi được diễn tập và một restore thành công. Đây là tiêu chí mục tiêu, chưa đạt trong gói docs.
