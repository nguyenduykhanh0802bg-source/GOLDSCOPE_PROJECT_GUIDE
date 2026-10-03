# Kiểm thử GoldScope

## 1. Các lệnh chạy được hiện tại

Từ thư mục gốc chứa CLAUDE.md:

```bash
python -m unittest discover -s lab00/tests -v
```

Đây là 12 test offline của audit tool. Kết quả thực thi khi đóng gói được lưu trong `../evidence/kit-validation.json`; kết quả ngày 30/09 nằm trong `../lab00/evidence/test-summary.json`.

```bash
python lab00/scripts/audit_sources.py --out runtime/source-audit.json
```

Lệnh thứ hai là audit, không phải unit test. Không có key thì report blocked, không network. Exit 2 có nghĩa chưa đủ manual sign-off. Không diễn giải exit 2 đó thành “API thành công” hoặc “test runner lỗi”. Network probe cần được yêu cầu riêng, không dùng mặc định trong CI.

## 1b. Lệnh đã chạy được sau GS-003/GS-004

```bash
uv sync --locked && uv run pytest            # unit; integration SKIP nếu thiếu TEST_DATABASE_URL
TEST_DATABASE_URL=... uv run pytest tests/integration -rs
uv run ruff format --check . && uv run ruff check . && uv run mypy
```

Test bị SKIP không được báo là đã đạt. Hướng dẫn DB: `LOCAL_DATABASE.md`.

## 2. Cấu trúc test mục tiêu

| Thư mục dự kiến | Kiểm tra |
|---|---|
| `tests/unit/` | Hàm/validation có đầu vào xác định |
| `tests/integration/` | PostgreSQL, transaction, migration, API/repository |
| `tests/temporal/` | Feature/target, vintage, cutoff, label maturity |
| `tests/fixtures/` | Synthetic hoặc response được phép lưu và đã làm sạch |

pytest, pytest-cov và respx là công cụ dự kiến. GS-003 tạo cấu hình, migration/API tests được thêm khi code tương ứng tồn tại. Test integration dùng PostgreSQL, không dùng SQLite để kết luận semantics NUMERIC/timezone/unique/locking giống nhau.

## 3. Test matrix bắt buộc

| ID | Tình huống | Kết quả kỳ vọng |
|---|---|---|
| COL-01 | HTTP 200 body quota/error | Không có observations mới, run ghi lỗi |
| COL-02 | Timeout/5xx/429 | Retry giới hạn theo policy, không loop vô hạn |
| COL-03 | Schema hoặc unit đổi | Raw giữ được, normalize bị chặn |
| DAT-01 | Retry cùng payload | Business rows không tăng, không revision giả |
| DAT-02 | Payload revision thực sự | Giữ bản cũ và tạo revision mới |
| DAT-03 | Giá GOLD âm/NaN và macro yield âm | GOLD bị loại; macro âm không bị loại tự động |
| TMP-01 | Sửa toàn bộ dữ liệu sau D | Feature tại D không đổi |
| TMP-02 | CPI kỳ tháng trước công bố sau D | Không có trong feature tại D |
| TMP-03 | Label h=5 chưa sẵn sàng | Mẫu không có trong train ở cutoff đó |
| TMP-04 | Revision chỉ xuất hiện sau D | Không làm đổi snapshot point-in-time tại D |
| FTR-01 | Dòng cuối thiếu target | Giữ để inference nếu feature đủ |
| MOD-01 | Feature thiếu/sai schema | Model từ chối rõ, không dự báo ngầm sai |
| MOD-02 | Interval crossing/non-finite | Theo policy có version; không công bố số vô nghĩa |
| API-01 | Range/horizon/asset sai | 422 theo error envelope |
| API-02 | Resource thiếu/DB mất/stale | 404/503/200+stale đúng trường hợp |
| API-03 | Paging/order/mode filter | Nhất quán với contract |
| JOB-01 | Hai job trùng cửa sổ | Không có prediction/observation trùng |
| STO-01 | Fail giữa transaction | Không có dữ liệu nghiệp vụ nửa chừng |
| OPS-01 | Backup rồi restore | Đọc được forecast và artifact hash đúng |

## 4. Fixture policy

Mỗi fixture ghi source hoặc synthetic, mục đích, ngày tạo và lý do được phép giữ. Không có API key/token/credential. Chưa có GOLD response hợp lệ thì chỉ tạo synthetic schema test hoặc error fixture, không gắn nhãn provider_verified.

Mock HTTPX bằng respx; mock clock khi cần. Không gọi Internet ở unit/temporal tests. Random seed cố định cho test có ngẫu nhiên; không test “model phải thắng baseline” trên thị trường thật.

## 5. Lệnh tương lai sau bootstrap

```bash
uv run pytest tests/unit tests/temporal
uv run pytest tests/integration
uv run ruff check .
uv run ruff format --check .
uv run mypy src/goldscope
```

Chỉ dùng khi GS-003 đã tạo package/config và các thư mục tương ứng. Integration cần TEST_DATABASE_URL hoặc cơ chế fixture đã ghi; không tự dùng DATABASE_URL production khi thiếu test config.

## 6. Gates và evidence

Task nhỏ: test hành vi bị tác động. API/database: thêm integration/migration tests. Feature/ML: temporal tests và experiment evidence. Release: full configured CI + smoke Compose + restore rehearsal + đọc một forecast end-to-end.

Evidence gồm command/cwd/env, exit code, test count, duration nếu đo, log/report path và giới hạn. Coverage là chỉ số hỗ trợ, không thay acceptance criteria. Không mở rộng test vô tận khi rủi ro đã được giải quyết.

## 7. Chưa được kiểm chứng trong bộ tài liệu

Chưa có provider happy-path authenticated, app API/DB integration, model quality, tải production, deploy/restore thực tế hoặc Claude Code session end-to-end. Những bước đó phải được test trong task triển khai tương ứng.
