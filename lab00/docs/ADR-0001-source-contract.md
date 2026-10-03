# ADR-0001 — Nguồn ứng viên và điều kiện ký duyệt hợp đồng dữ liệu

- Ngày: 30/09/2026.
- Trạng thái: chấp nhận hướng thiết kế; tích hợp dữ liệu thật đang bị chặn bởi key/metadata.
- Phạm vi: Lab 00 trong GOLDSCOPE_PROJECT_GUIDE.md.

## Bối cảnh

Endpoint vàng được mô tả trong tài liệu Alpha Vantage, nhưng demo GOLD chỉ trả thông báo. FRED không key trả lỗi. Chưa có bằng chứng để viết adapter GOLD dựa trên trường giá/đơn vị giả định.

## Quyết định

1. Dùng Alpha Vantage làm nguồn ứng viên, không mặc định là nguồn đã được nghiệm thu.
2. Audit ba macro series DGS10, DFII10, DTWEXBGS bằng key riêng của ứng dụng.
3. Giữ bài toán 1/5 phiên dữ liệu, target lợi suất đơn và baseline zero-return như kế hoạch.
4. Price field, currency/unit đã xác minh, calendar, timezone và cutoff chỉ chốt từ bằng chứng thực tế.
5. Công cụ audit đứng riêng, dùng standard library để giảm rào cản Lab 00; ứng dụng vẫn dùng stack chính trong hướng dẫn.
6. Không tự động chấp thuận nguồn khi HTTP 200, không nối nguồn ETF/futures thay vàng mà giữ cùng asset_id.
7. Không xem forward-fill theo observation_date là giải pháp cho release/vintage leakage.

## Hệ quả

Có thể làm khung repository Lab 01 song song, nhưng cần key và audit thành công để triển khai adapter chính. Khi nguồn không đáp ứng lịch sử/quyền/ngân sách, ghi ADR thay nguồn sau một audit tương đương.

## Điều kiện xem xét lại

Nhận report authenticated; nguồn thay đổi schema/quota; không có tối thiểu độ phủ mong muốn; hoặc metadata không đủ để định nghĩa forecast origin. Mỗi lần thay đổi contract tăng version và nêu bằng chứng.
