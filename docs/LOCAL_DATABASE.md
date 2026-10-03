# Cơ sở dữ liệu local (GS-004)

**Trạng thái:** migration `0001` đã chạy và kiểm thử trên PostgreSQL 16.15 (sandbox Linux). `compose.dev-db.yaml` (PostgreSQL 17) và CI service **chưa được chạy** trong lần bàn giao này; xem `evidence/gs-004-verification.txt`.

## 1. Khởi động DB (Docker)

```bash
docker compose -f compose.dev-db.yaml up -d
docker compose -f compose.dev-db.yaml ps   # đợi healthy
```

Tạo hai database tách biệt: `goldscope_dev` (phát triển) và `goldscope_test` (chỉ cho test, tạo bởi `scripts/db/init-databases.sh` lần đầu tạo volume). Nếu volume đã tồn tại từ trước, tạo DB test thủ công: `CREATE DATABASE goldscope_test;`.

Không dùng Docker: cài PostgreSQL 16/17 trực tiếp, tạo role + hai database tương tự và đổi URL bên dưới.

## 2. Biến môi trường

Đặt trong shell hoặc file env riêng (không commit; `.env*` đã nằm trong `.gitignore`):

```bash
export DATABASE_URL="postgresql+psycopg://goldscope:goldscope_local_only@localhost:5432/goldscope_dev"
export TEST_DATABASE_URL="postgresql+psycopg://goldscope:goldscope_local_only@localhost:5432/goldscope_test"
```

Scheme `postgresql://` cũng được; code tự chuyển sang driver psycopg 3.

## 3. Migration

```bash
uv run alembic upgrade head        # tạo/cập nhật schema trên DATABASE_URL
uv run alembic check               # models và migration không lệch nhau
uv run alembic downgrade base      # CHỈ trên DB dev/test; xóa toàn bộ bảng
```

Tạo migration mới: sửa `src/goldscope/db/models.py`, chạy `uv run alembic revision --autogenerate -m "mô tả"`, **đọc và chỉnh tay** file sinh ra, rồi chạy `alembic check`. Migration đã áp dụng ở môi trường dùng chung không được sửa; thêm migration mới.

## 4. Test

```bash
uv run pytest                      # unit; integration bị SKIP nếu thiếu TEST_DATABASE_URL
uv run pytest tests/integration -rs
```

Integration test **xóa và dựng lại schema `public`** của `TEST_DATABASE_URL`. Vì vậy `resolve_test_database_url` từ chối khi: thiếu URL, trùng `DATABASE_URL`, `APP_ENV=production`, hoặc tên database không chứa `test`. Test bị SKIP là chưa chạy, không phải đã đạt.

## 5. Quy ước schema cần nhớ

- Mọi thời điểm tuyệt đối là `TIMESTAMPTZ`; luôn truyền `datetime` có timezone (datetime naive bị PostgreSQL hiểu theo timezone của session, xem test `test_naive_datetime_...`).
- `price`/`value` là `NUMERIC` không giới hạn precision cho tới khi audit nguồn xong (ADR-0006). Chuyển sang float chỉ ở ranh giới ML.
- Cùng business key + nội dung giống: no-op (`AddResult.DUPLICATE`). Cùng key + nội dung khác: `DataConflictError`; dữ liệu sửa phải dùng `revision_key` mới.
- Không xóa cascade; không `UPDATE` forecast/quan sát cũ.
