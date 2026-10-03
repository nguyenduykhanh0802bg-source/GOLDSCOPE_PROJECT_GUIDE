# Nhật ký quyết định kiến trúc

ADR ghi lý do thiết kế, không đánh dấu code đã tồn tại. Trạng thái: proposed, accepted, superseded. Khi thay quyết định accepted, tạo ADR mới tham chiếu ADR cũ, không xóa lịch sử.

| ID | Quyết định | Trạng thái |
|---|---|---|
| [0001](ADR-0001-source-contract.md) | Nguồn ứng viên và sign-off dữ liệu | Accepted design; provider verification pending |
| [0002](ADR-0002-modular-monolith.md) | Modular monolith, một repo | Accepted design |
| [0003](ADR-0003-forecast-protocol.md) | Return target, 1/5 phiên, baseline và time-aware evaluation | Accepted design |
| [0004](ADR-0004-storage-and-jobs.md) | PostgreSQL + artifacts, scheduler ngoài API | Accepted design |
| [0005](ADR-0005-deployment-options.md) | Lựa chọn hosting/proxy/registry | Proposed, chưa chọn nhà cung cấp |
| [0006](ADR-0006-database-baseline.md) | UUID PK, NUMERIC chưa chốt precision, FK metadata macro | Accepted cho migration 0001 |
| [Template](ADR-TEMPLATE.md) | Mẫu quyết định tiếp theo | Template |

Snapshot quyết định nguồn Lab 00 ban đầu giữ trong `../../lab00/docs/ADR-0001-source-contract.md`; bản ở đây mở rộng hướng dẫn cho package bàn giao, không xác nhận nguồn đã được phê duyệt.
