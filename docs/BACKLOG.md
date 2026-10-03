# Backlog triển khai GoldScope

Ngày: 01/10/2026. Đây là trạng thái bàn giao, cập nhật sau mỗi task cùng PROJECT_STATUS. GS-xxx giữ các ID trong project guide gốc.

| Task | Nội dung | Trạng thái | Giai đoạn |
|---|---|---|---|
| [GS-001](tasks/GS-001.md) | Kiểm chứng quyền và dữ liệu nguồn | BLOCKED | Lab 00 · P0 |
| [GS-002](tasks/GS-002.md) | Chốt hợp đồng nguồn và thời gian | BLOCKED | Lab 00 · P0 |
| [GS-003](tasks/GS-003.md) | Bootstrap package và môi trường phát triển | TODO | Lab 01 · P0 |
| [GS-004](tasks/GS-004.md) | Database nền và migration đầu | TODO | Lab 02 · P0 |
| [GS-005](tasks/GS-005.md) | Collector giá vàng và raw ingestion | TODO | Lab 02 · P0 |
| [GS-006](tasks/GS-006.md) | EDA và dataset snapshot | TODO | Lab 03 · P0 |
| [GS-007](tasks/GS-007.md) | Feature và target có kiểm soát thời gian | TODO | Lab 04 · P0 |
| [GS-008](tasks/GS-008.md) | Baseline, Ridge và walk-forward | TODO | Lab 04 · P0 |
| [GS-009](tasks/GS-009.md) | XGBoost, interval và model registry | TODO | Lab 05 · P0 |
| [GS-010](tasks/GS-010.md) | FastAPI và lịch sử forecast/outcome | TODO | Lab 06 · P0 |
| [GS-011](tasks/GS-011.md) | Dashboard, Compose và bản MVP | TODO | Lab 07 · P0 |
| [GS-012](tasks/GS-012.md) | Macro point-in-time và ablation | TODO | Lab 08 · P1 |
| [GS-013](tasks/GS-013.md) | Daily jobs, scoring và phục hồi | TODO | Lab 10 phần vận hành · P1 |
| [GS-014](tasks/GS-014.md) | Portfolio release và triển khai được phép | TODO | Lab 10 phần release · P1 |
| [GS-015](tasks/GS-015.md) | Các nhánh mở rộng có điều kiện | DEFERRED | Lab 09 và nghiên cứu sau MVP · P2 |

## Thứ tự thực hiện

GS-001/002 hoàn tất source gate; GS-003 có thể chạy song song với việc chuẩn bị key. Sau nền package là GS-004; collector thật GS-005 cần mapping đã xác minh. Tiếp GS-006→007→008→009→010→011. GS-012 là nhánh macro có điều kiện dữ liệu. GS-013/014 hoàn thiện vận hành/release. GS-015 chỉ mở nhánh được chọn.

Không hiểu dependency graph là ủy quyền tự dùng nhiều agent hoặc tác động external. Trong một phiên làm việc, thực hiện task cụ thể được người dùng giao và giữ tiến độ trung thực.

