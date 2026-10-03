# ADR-0003 — Target và giao thức đánh giá

Ngày: 01/10/2026. Trạng thái: accepted design.

## Quyết định

Model riêng cho h=1/5 valid provider observations; target simple return; baseline zero-return; price chuyển từ origin price. Chọn Ridge rồi XGBoost và quantile interval. Walk-forward theo fit schedule, label maturity và availability; final holdout giữ riêng.

## Lý do

Định nghĩa horizon rõ hơn “7/30 ngày” khi calendar nguồn chưa chốt. Baseline tạo thước đo trung thực; khoảng dự báo thể hiện bất định. Độ phức tạp ML chỉ tăng nếu thực nghiệm có mục tiêu.

## Hệ quả

Phải kiểm tra nhãn chồng lấn và release timing; random split không dùng làm kết quả chính. H=20/classification/deep learning cần protocol cập nhật. ML không thắng baseline vẫn có thể nghiệm thu kỹ thuật; không có bảo đảm lợi nhuận.

## Xem xét lại

Nguồn/time definition thay đổi hoặc user chọn bài toán khác. Dataset/model/protocol versions phải được cập nhật đồng bộ.
