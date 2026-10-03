# GoldScope — Bộ tài liệu bàn giao cho Claude Code

**Phiên bản:** 1.0 — 01/10/2026.  
**Phạm vi:** tài liệu và công cụ Lab 00; chưa phải ứng dụng hoàn chỉnh.

Gói này chứa các tài liệu cần để Claude Code tiếp tục phát triển GoldScope theo kế hoạch, với trạng thái hiện tại, đặc tả kỹ thuật, quy tắc theo module và task specs cụ thể.

## Bắt đầu trong 5 bước

1. Giải nén ZIP vào một thư mục mới. Giữ cả thư mục `.claude/` (có thể bị ẩn trong trình quản lý file).
2. Mở thư mục chứa `CLAUDE.md` bằng VS Code/terminal. Chưa cần cài toàn bộ stack để đọc tài liệu hoặc chạy test Lab 00.
3. Đọc [trạng thái dự án](docs/PROJECT_STATUS.md) và [mục lục tài liệu](docs/README.md).
4. Mở Claude Code tại thư mục này. Nếu chưa cài/đăng nhập Claude Code, làm theo tài liệu chính thức và quyền sử dụng tài khoản của bạn; gói không cài đặt hay cấu hình tài khoản Claude.
5. Giao một task bằng mẫu ở dưới. Khi đã có repo riêng, chuyển các file có chọn lọc và kiểm tra diff; không giải nén đè lên source đang có.

## Giao việc đầu tiên cho Claude

```text
Đọc CLAUDE.md, docs/PROJECT_STATUS.md và docs/DEVELOPMENT_WORKFLOW.md.
Kiểm tra mã nguồn và chạy kiểm thử Lab 00 từ thư mục gốc.
Đối chiếu docs/tasks/GS-001.md và GS-002.md; không tự suy ra đã có API key.
Nếu nguồn dữ liệu vẫn chưa được xác minh, ghi rõ blocker và giữ source contract ở trạng thái dự thảo.
Sau đó thực hiện GS-003: khởi tạo môi trường và khung repository theo task spec.
Không triển khai collector thật dựa trên schema chưa xác minh.
Bàn giao bằng các lệnh thực sự đã chạy, kết quả và trạng thái task cập nhật.
```

Đây là mẫu giao việc để bạn dùng sau khi nhận gói, không phải bằng chứng GS-003 đã được thực hiện.

## Có thể chạy ngay

```bash
python -m unittest discover -s lab00/tests -v
python lab00/scripts/audit_sources.py --out runtime/source-audit.json
```

Lệnh audit không có key sẽ không gọi API tài khoản. Exit code 2 là thiết kế của công cụ: cần xem report và hoàn thành sign-off thủ công. Để nhập key ẩn tại terminal của bạn, thêm `--prompt-keys`. Không đưa key vào chat.

## Những tài liệu chính

| Nhóm | File |
|---|---|
| Hướng dẫn AI | [CLAUDE.md](CLAUDE.md) và `.claude/rules/` |
| Tiến độ | [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) |
| Cách làm việc | [DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md), [HANDOFF.md](docs/HANDOFF.md) |
| Kiến trúc | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Dữ liệu/database | [DATA_CONTRACT.md](docs/DATA_CONTRACT.md), [DATABASE_DESIGN.md](docs/DATABASE_DESIGN.md) |
| API | [API_CONTRACT.md](docs/API_CONTRACT.md) |
| ML | [ML_PROTOCOL.md](docs/ML_PROTOCOL.md) |
| Kiểm thử | [TESTING.md](docs/TESTING.md) |
| Môi trường | [CONFIGURATION_BLUEPRINT.md](docs/CONFIGURATION_BLUEPRINT.md), [.env.example](.env.example) |
| Vận hành | [RUNBOOK.md](docs/RUNBOOK.md) |
| Công việc | [BACKLOG.md](docs/BACKLOG.md), GS-001 đến GS-015 trong `docs/tasks/` |
| Quyết định | [Danh mục ADR](docs/decisions/README.md) |
| Kế hoạch trước đó | Bản giữ nguyên trong `docs/reference/` |
| Bằng chứng cũ | `lab00/evidence/`; công cụ và 12 test trong `lab00/` |

## Cách bộ hướng dẫn Claude hoạt động

`CLAUDE.md` giữ các quy tắc dùng thường xuyên và chỉ dẫn đọc tài liệu theo nhiệm vụ. `.claude/rules/` dùng `paths` để gắn quy tắc với vùng source liên quan; các đường dẫn ứng dụng tương lai sẽ có hiệu lực khi các file đó được tạo. Tài liệu dài không được import hàng loạt vào CLAUDE.md.

Các Markdown này định hướng hành vi, không thay thế sandbox, quyền công cụ hoặc test. Khả năng nạp rules phụ thuộc phiên bản/cấu hình Claude Code; xem [hướng dẫn memory chính thức](https://code.claude.com/docs/en/memory) và [best practices](https://code.claude.com/docs/en/best-practices). Gói chưa được kiểm thử bằng một phiên Claude Code thực tế; đã kiểm tra cấu trúc tài liệu và mã Lab 00 theo evidence đính kèm.

## Giới hạn hiện tại

- Chưa có source `src/goldscope/`, lockfile, migrations, API, dashboard hoặc model huấn luyện.
- Không tạo pyproject/uv.lock/Compose giả để làm gói trông như ứng dụng đã chạy; GS-003 và các task sau sẽ tạo các file thực tế.
- API schema trong tài liệu là thiết kế đích, không phải endpoint đang hoạt động.
- Alpha Vantage vẫn là nguồn ứng viên, GOLD schema/unit/cutoff còn chờ xác minh.
- Gói không thay đổi project guide/technology stack đã lưu trước đó; bản reference giữ nguyên để truy nguyên.
- Khi cập nhật source, cập nhật trạng thái và các đặc tả liên quan cùng thay đổi.
