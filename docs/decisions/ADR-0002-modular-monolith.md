# ADR-0002 — Một repo, ứng dụng chia module

Ngày: 01/10/2026. Trạng thái: accepted design.

## Bối cảnh

Dự án một người, dữ liệu ngày, yêu cầu demo được cả pipeline và API. Vận hành phân tán sớm làm tăng thời gian mà chưa có nhu cầu quy mô đo được.

## Quyết định

Python package src/goldscope với modules collectors/data/features/ml/db/services/api/jobs. Streamlit client nằm trong dashboard. API/dashboard/job là tiến trình riêng dùng chung source/contracts; một PostgreSQL.

## Lựa chọn khác và hệ quả

Microservices bị hoãn; monolithic notebook không đáp ứng test/reuse. Chọn modular monolith giúp dùng chung feature và có test boundary. Phải giữ ranh giới import để về sau tách worker không viết lại toàn bộ logic.

## Xem xét lại

Có bottleneck/concurrency/deployment isolation đo được hoặc nhóm phát triển lớn hơn; không tách chỉ để thêm từ khóa vào CV.
