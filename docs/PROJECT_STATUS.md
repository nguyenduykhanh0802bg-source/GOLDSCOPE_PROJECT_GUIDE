# GoldScope — Trạng thái thực tế

**Cập nhật:** 01/10/2026. **Mốc:** bàn giao bộ tài liệu Claude Code, trước bootstrap ứng dụng.

## Đã hoàn thành

| Hạng mục | Bằng chứng |
|---|---|
| Chọn bài toán và roadmap | `reference/GOLDSCOPE_PROJECT_GUIDE.md` |
| Tổng hợp stack | `reference/GOLDSCOPE_TECHNOLOGY_STACK.md` |
| Audit tài liệu và public/no-key probes | `reference/GOLDSCOPE_LAB00_DATA_SOURCE_AUDIT.md`, `../lab00/evidence/public-probe.json` |
| Công cụ audit standalone | `../lab00/scripts/audit_sources.py` |
| 12 kiểm thử offline của công cụ | `../lab00/tests/test_audit.py`, evidence test-summary cũ |
| Bộ tài liệu, task specs và scoped rules | README gốc, file này, hợp đồng và backlog |
| GS-004 database + migration 0001 (01/10/2026) | `src/goldscope/db/`, `migrations/`, `tests/integration/`, `evidence/gs-004-verification.txt` (PostgreSQL 16.15) |
| GS-003 bootstrap package (01/10/2026) | `pyproject.toml`, `uv.lock`, `src/goldscope/`, `tests/`, `evidence/gs-003-verification.txt` |

Việc đóng gói không biến Lab 00 thành DONE. Kết quả request cũ có timestamp 30/09/2026, không phải dữ liệu được tải lại hôm nay.

## Đang bị chặn

- GS-001: chưa có authenticated GOLD response bằng key dự án.
- GS-002: chưa xác minh price field, unit, currency, lịch nguồn, publication time, revision và quyền dùng.
- Trạng thái key phản ánh kiểm tra ở lượt audit trước. Chưa kiểm tra lại secret trên máy người dùng; không kết luận họ chưa sở hữu key.
- Ba FRED series đã khảo sát tài liệu, chưa có evidence account audit thành công.

## Chưa triển khai

dataset/feature/model/prediction tables, collector production, dataset training, ML artifacts, REST API, Streamlit dashboard, Compose, CI/CD và hosting.

Không có model performance, giá dự báo thật hoặc benchmark hệ thống để đưa vào CV lúc này.

## Công việc tiếp theo

1. GS-001 và GS-002: hoàn tất bằng key và evidence nguồn khi có thể.
2. GS-003: DONE (01/10/2026). Tiếp theo: tạo Git repo/remote để CI chạy thật.
3. GS-004: database với cấu trúc metadata/versioning; mapping provider vẫn có thể chờ.
4. GS-004: DONE (01/10/2026), chạy trên PostgreSQL 16.15; cần chạy lại trên PostgreSQL 17/Compose.
5. GS-005 chỉ tích hợp GOLD thật sau khi các field cần thiết được xác minh; nếu giờ công bố chưa rõ, historical/live claims phải giữ giới hạn đã ghi.

## Quy tắc cập nhật file này

Sau mỗi task ghi ngày, task ID, trạng thái, evidence path, lệnh thực sự đã chạy và blocker còn lại. Không tự đổi task tương lai thành DONE vì đã viết tài liệu. Dùng các trạng thái: TODO, IN_PROGRESS, BLOCKED, DONE, DEFERRED; chỉ DONE khi có evidence đạt toàn bộ acceptance criteria.

## Nhật ký bàn giao

| Ngày | Thay đổi | Giới hạn |
|---|---|---|
| 30/09/2026 | Source audit và standalone tool, 12 test đạt | Không có key/dataset thật |
| 01/10/2026 | Bộ Claude docs + task specs; kiểm tra gói trong `../evidence/kit-validation.json` | Chưa chạy Claude Code end-to-end; chưa bootstrap app |
| 01/10/2026 | GS-003: package, settings, logging redact, CLI skeleton, 29 test, lock, CI file | CI chưa chạy trên GitHub; chưa thử Windows/WSL |
| 01/10/2026 | GS-004: migration 0001, session/repositories, 43 integration test trên PostgreSQL thật | PG 16.15 thay vì 17; Compose/CI chưa chạy; precision NUMERIC chờ audit |
