# Thiết kế database và artifacts

**Trạng thái:** migration `0001` (sources, ingestion_runs, raw_objects, market/macro observations, macro_series, data_quality_events) đã hiện thực và kiểm thử trên PostgreSQL 16.15; dataset/feature/model/prediction/news vẫn là thiết kế mục tiêu (migration 2-4). Chi tiết quyết định: ADR-0006. PostgreSQL 17, SQLAlchemy 2.x, Psycopg 3, Alembic.

## Bảng và khóa

| Bảng | Nội dung | Key/ràng buộc |
|---|---|---|
| `data_sources` | Provider metadata, endpoint key, time/unit/license policy | Unique provider + dataset key + policy version |
| `ingestion_runs` | Start/end, status, counts, error, source | ID riêng mỗi lần chạy |
| `raw_objects` | URI, checksum, schema/content type, fetched time | FK run/source; checksum có index |
| `market_observations` | GOLD price + revision + timestamps | Unique asset/source/date/revision_key |
| `macro_series` | Units/frequency/release metadata | Series ID + metadata version |
| `macro_observations` | Value/period/vintage/availability | Unique series/date/revision_key |
| `dataset_snapshots` | Manifest/hash/time-policy/calendar | ID bất biến, hash theo snapshot |
| `feature_snapshots` | Dataset ID, feature version/schema/hash, artifact path | FK dataset; giữ schema tương thích |
| `model_versions` | Family/horizon/artifacts/training data/metrics/git SHA | ID bất biến; artifact hash bắt buộc khi ready |
| `model_deployments` | Active model theo asset/horizon, activation/retirement | Partial unique asset/horizon với retired_at null |
| `predictions` | Origin, as_of, issued_at, horizon, outputs, mode, model/snapshot | Unique asset/origin/as_of/horizon/model/feature_snapshot/mode |
| `prediction_outcomes` | Target, actuals, source revision, score revision | Unique prediction/score_revision |
| `data_quality_events` | Rule/severity/count/context/run | FK run, timestamp |
| `news_articles`, `news_signals` | Tương lai Lab 09 | Tạo migration khi chọn nhánh tin |

Revision key dùng non-null canonical source ID/hash để tránh semantics unique với null. Chọn UUID hoặc bigint nhất quán khi hiện thực; API serialization phải ổn định.

## Kiểu và index

- `TIMESTAMPTZ` cho thời điểm tuyệt đối, `DATE` cho kỳ/ngày quan sát.
- Giá/value raw dùng NUMERIC với precision/scale chốt sau audit nguồn; chuyển float ở ML boundary.
- JSONB cho metadata linh hoạt, không thay cột có type/ràng buộc cho dữ liệu cốt lõi.
- Index asset/source/observation_date; series/available_at; model/as_of; prediction target/date khi chấm điểm.
- Check constraints phù hợp: price GOLD >0, horizon >0, interval_level trong (0,1), lower<=upper, ended_at>=started_at.
- Không áp yield>0 lên macro. Không cascade xóa model/snapshot còn được predictions tham chiếu.

## Tính bất biến và transaction

Prediction gồm point/interval/origin/model/snapshot là bất biến sau phát hành. Outcomes được thêm và version hóa khi underlying actual thay đổi. API truy vấn outcome mới nhất phải thể hiện revision/score timestamp.

Promotion model thực hiện transaction đóng deployment cũ và tạo deployment mới; giữ lịch sử rollback. Không thay artifact tại đường dẫn của version cũ.

Job retries dựa vào unique constraints; xử lý conflict bằng so sánh record tương đương, không update forecast cũ sang số mới. Khóa job không thay unique key.

## Migration plan

1. Sources/ingestion/raw/observations/quality.
2. Dataset/feature/model registry.
3. Predictions/outcomes/deployments.
4. News tables khi nhánh đã được chấp thuận.

Mỗi migration có test từ DB sạch và upgrade từ schema trước. Kiểm tra autogenerate trước khi áp dụng. Migration có thể mất dữ liệu phải có kế hoạch backup/compatibility; không thử trên DB production trong task local.

## File storage

Raw JSON nén, snapshot Parquet, model native artifact và manifest nằm trong volume/storage riêng. DB chỉ lưu URI nội bộ/hash và metadata. API không trả local path hoặc storage credential ra client.

Backup gồm dump database + bộ artifacts được manifest tham chiếu. Restore cần kiểm tra file hash, FK, model load và đọc được một forecast. Chỉ restore DB mà thiếu artifacts chưa phải phục hồi hoàn chỉnh.
