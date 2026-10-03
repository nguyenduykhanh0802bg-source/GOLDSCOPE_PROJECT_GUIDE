# Môi trường và cấu hình — bản thiết kế

## 1. Hiện trạng

Có standalone audit và unittest trong `lab00/`. Chưa có package ứng dụng, uv.lock, Compose, migration hay Git remote. Các lệnh phần 2–5 là hướng dẫn cho GS-003 và các task sau, không phải thao tác đã được thực thi.

## 2. Bootstrap không làm mất tài liệu

Chọn Python 3.12 và một môi trường chính (WSL/Linux hoặc Windows). uv quản lý venv/dependency. Kiểm tra repo hiện có trước; nếu đã có pyproject/Git thì tích hợp, không `uv init`/git init chồng mà bỏ qua cấu trúc sẵn có.

Khởi tạo package `goldscope` với src layout, CLI entry point `goldscope = goldscope.cli:app`, settings, logger và tests. Nếu tạo trong thư mục kit hiện tại, bảo toàn CLAUDE/docs/lab00. Không chạy lệnh khởi tạo trỏ vào thư mục cha không liên quan.

Dependency trực tiếp theo kế hoạch:

| Nhóm | Package |
|---|---|
| App/API | fastapi, uvicorn, pydantic v2, pydantic-settings, httpx, typer |
| Database | sqlalchemy 2.x, alembic, psycopg 3 |
| Config | pyyaml nếu đọc YAML, dùng safe loader |
| Data/ML khi tới lab | pandas, numpy, pyarrow, scikit-learn, xgboost, joblib nếu import trực tiếp |
| UI khi tới lab | streamlit, plotly |
| Dev | pytest, pytest-cov, respx, ruff, mypy |
| Research optional | jupyterlab, ipykernel |

Khóa phiên bản sau install/tests. Không viết uv.lock thủ công. Không đổi Python major/minor hoặc framework chỉ để bỏ qua lỗi dependency mà không ghi quyết định.

## 3. Config contract

| Biến | Đọc bởi | Yêu cầu |
|---|---|---|
| APP_ENV | Settings | local/test/staging/production; validate enum |
| DATABASE_URL | DB app | Secret, bắt buộc khi chạy chức năng DB |
| TEST_DATABASE_URL | Tests | DB riêng; không fallback production |
| ALPHA_VANTAGE_API_KEY | Gold collector/audit | Chỉ cần khi gọi nguồn thật |
| FRED_API_KEY | Macro collector/audit | Chỉ cần khi gọi nguồn thật |
| API_BASE_URL | Dashboard | localhost ở host; service api trong Compose |
| DATA_ROOT / ARTIFACT_ROOT | Jobs/storage | Đường dẫn volume writable; không nằm trong source |
| LOG_LEVEL | Logger | Enum được validate |
| DISPLAY_TIMEZONE | UI | Asia/Ho_Chi_Minh mặc định; timestamp lưu UTC |

`.env.example` đính kèm chỉ là contract cấu hình. App future phải cấu hình rõ cách nạp `.env`; audit Lab 00 không tự nạp `.env`, chỉ dùng environment hoặc nhập ẩn. Chỉ validate key khi chức năng cần key để tests/docs vẫn chạy offline.

## 4. CLI mục tiêu

```bash
uv run goldscope sources audit --source gold
uv run goldscope collect gold --start 2016-01-01
uv run goldscope collect macro --series DGS10,DFII10,DTWEXBGS
uv run goldscope dataset build --config configs/features.yaml
uv run goldscope backtest --config configs/backtest.yaml
uv run goldscope train --config configs/training.yaml
uv run goldscope predict --horizon 5
uv run goldscope pipeline daily
uv run goldscope predictions score
```

Mỗi command được hiện thực bởi task riêng. Ngày 2016-01-01 là yêu cầu minh họa, không khẳng định nguồn có lịch sử đó. GS-003 chỉ làm help/version/doctor hoặc skeleton phản hồi not-implemented rõ ràng; không tạo command giả in “success”.

Lệnh application sau GS-006..011:

```bash
uv run alembic upgrade head
uv run uvicorn goldscope.api.main:app --reload
uv run streamlit run dashboard/app.py
docker compose up --build
```

`--reload` chỉ phát triển. Compose chưa có trong gói này. Khi các command thực sự hoạt động, chuyển chúng sang danh sách verified commands trong CLAUDE/TESTING/RUNBOOK và ghi evidence.

## 5. Config files mục tiêu

sources.yaml: endpoint/source metadata/policy, không secret. features.yaml: names/windows/missing/availability. backtest.yaml: absolute periods/fit schedule/horizons/seed/protocol. training.yaml: model family/hyperparameters/promotion policy. Không dùng ngày hoặc unit minh họa thành production default chưa kiểm chứng.

## 6. CI blueprint

Install theo lock → format/lint/type → unit/temporal → PostgreSQL integration → migration smoke → image build. Không cần key nguồn cho unit/integration thông thường. Network validation tách workflow riêng theo request/quota. CD chỉ bổ sung sau khi có remote/registry/host được chọn.

## 7. Thông tin máy cần ghi khi triển khai

OS/Python/uv/Docker versions, RAM/CPU, paths/ports, nguồn secret, database name, source quota, hostname/TLS và backup destination. Chỉ ghi cấu hình không nhạy cảm vào tài liệu; không coi mức VPS đề xuất trong guide là benchmark đã đo.
