# Mục lục và cách sử dụng tài liệu

Ngày: 01/10/2026. Đây là bộ đặc tả triển khai, không phải báo cáo tính năng đã hoàn thành.

## Đọc tài liệu nào khi nhận việc?

| Công việc | Tài liệu cần đọc |
|---|---|
| Mọi task | `../CLAUDE.md`, `PROJECT_STATUS.md`, `DEVELOPMENT_WORKFLOW.md`, task spec |
| Bootstrap | `CONFIGURATION_BLUEPRINT.md`, `ARCHITECTURE.md`, `TESTING.md` |
| Collector/data | `DATA_CONTRACT.md`, `DATABASE_DESIGN.md`, source audit |
| Database local/migration | `LOCAL_DATABASE.md`, `DATABASE_DESIGN.md`, `decisions/ADR-0006-database-baseline.md` |
| Feature/model | `ML_PROTOCOL.md`, `DATA_CONTRACT.md`, `TESTING.md` |
| API | `API_CONTRACT.md`, `ARCHITECTURE.md`, `DATABASE_DESIGN.md` |
| UI | `API_CONTRACT.md`, quy tắc hiển thị trong `ARCHITECTURE.md` |
| Deploy/job | `RUNBOOK.md`, `CONFIGURATION_BLUEPRINT.md`, task GS-013/014 |
| Thay đổi quyết định | `decisions/README.md` và ADR tương ứng |

## Nguồn đúng cho từng loại thông tin

- **Thực tế đã làm:** PROJECT_STATUS, task evidence và source/tests hiện có.
- **Hành vi mục tiêu:** hợp đồng DATA/API/ML và acceptance criteria trong task.
- **Nguyên nhân thiết kế:** ADR.
- **Nguồn thị trường đã xác minh:** audit có timestamp, payload/metadata và provider contract.
- **Tầm nhìn và roadmap gốc:** reference/GOLDSCOPE_PROJECT_GUIDE.md.
- **Bộ công nghệ:** reference/GOLDSCOPE_TECHNOLOGY_STACK.md; thay đổi mới phải có ADR.

Không coi tài liệu thiết kế là bằng chứng code đã tồn tại. Nếu code và contract khác nhau, ghi bug/design discrepancy, không tự coi phần nào “đúng” rồi sửa lan rộng. Nếu tài liệu mới và cũ mâu thuẫn về phạm vi, nêu rõ và giải quyết trước khi đổi hành vi.

## Tránh trùng nội dung

PROJECT_STATUS giữ một bản tiến độ hiện tại; task giữ yêu cầu và evidence riêng. DATA_CONTRACT giữ ý nghĩa dữ liệu; API_CONTRACT giữ wire format; ML_PROTOCOL giữ giao thức đánh giá. RUNBOOK chỉ giữ thao tác vận hành. Các file còn lại liên kết tới tài liệu chủ sở hữu thay vì chép lại nhiều lần.

## Trạng thái tài liệu

| Tài liệu | Trạng thái |
|---|---|
| CLAUDE/workflow/rules | Hướng dẫn sẵn để dùng |
| PROJECT_STATUS | Snapshot bàn giao; cập nhật sau mỗi task |
| DATA_CONTRACT | Thiết kế chuẩn hóa + provider mapping đang bị chặn |
| API_CONTRACT/DATABASE_DESIGN/ML_PROTOCOL | Đặc tả mục tiêu chờ hiện thực và kiểm chứng |
| RUNBOOK/configuration | Kế hoạch vận hành; phân biệt lệnh hiện có và lệnh tương lai |
| ADR-0001..0004 | Quyết định thiết kế đã chọn; không chứng minh triển khai |
| ADR-0005 | Đề xuất triển khai, chưa chốt hosting/proxy |

Không đặt secret vào bất kỳ tài liệu nào. Các link tới file trong gói dùng đường dẫn tương đối; tên đường dẫn source tương lai được viết dạng code và phải được tạo bởi task tương ứng.
