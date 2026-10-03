# ADR-0001 — Nguồn ứng viên và sign-off dữ liệu

Ngày: 01/10/2026. Trạng thái: accepted design, verification pending.

## Bối cảnh

Alpha Vantage mô tả gold history nhưng demo GOLD trong audit chỉ trả Information. FRED request không key trả 400. Chưa có data mapping GOLD verified.

## Quyết định

Giữ Alpha Vantage làm ứng viên đầu; FRED cho macro. Chỉ viết mapping thật từ schema/metadata đã quan sát. Lưu trạng thái null/false cho price/unit/calendar/cutoff chưa biết trong contract JSON. Không thay ETF/futures vào cùng asset ID.

## Lựa chọn khác

Nguồn CSV/API khác được phép xem xét nếu cùng loại tài sản/định nghĩa và có audit về quyền/coverage/availability. Không chọn một nguồn chưa kiểm tra chỉ vì không yêu cầu key.

## Hệ quả

GS-001/002 còn blocker; GS-003/004 có thể làm phần nền độc lập. Cần evidence cho quyền tài khoản, schema, đơn vị và time policy trước collector/live claims. Quyền tải thành công không tự chứng minh quyền public toàn bộ raw history.

## Xem xét lại

Nguồn không đáp ứng dữ liệu/ngân sách/quyền hoặc schema thay đổi. Tạo ADR mới, đổi source/version và đánh giá tác động tới history/model.
