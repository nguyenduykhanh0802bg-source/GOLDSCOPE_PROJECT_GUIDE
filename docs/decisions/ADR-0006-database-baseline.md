# ADR-0006 — Nền tảng database: khóa, kiểu số và phiên bản metadata

- Ngày: 01/10/2026
- Trạng thái: accepted (cho migration 0001; xem lại sau GS-002)
- Task liên quan: GS-004
- ADR tham chiếu: ADR-0004 (storage and jobs)

## Bối cảnh

DATABASE_DESIGN để ngỏ ba điểm: loại khóa chính, precision của NUMERIC và cách liên kết observation macro với metadata có phiên bản. Schema/đơn vị của nguồn GOLD chưa được xác minh (GS-001/002).

## Các lựa chọn

- Khóa: UUID sinh bởi PostgreSQL (`gen_random_uuid()`, có sẵn từ PG13) hoặc bigint identity. UUID tránh lộ thứ tự/số lượng qua API và dễ sinh phía job; đổi lại index lớn hơn, chấp nhận được ở quy mô ngày.
- NUMERIC: chọn precision/scale ngay (đoán) hoặc để không giới hạn. Đoán có thể cắt dữ liệu thật hoặc cố định đơn vị chưa kiểm chứng.
- Macro: observation trỏ `macro_series.id` (một dòng metadata) hoặc trỏ cặp (series_id, metadata_version).

## Quyết định

- UUID primary key cho mọi bảng của migration 0001.
- `NUMERIC` không precision/scale cho `price` và `value`; CHECK loại NaN/±Infinity (PostgreSQL cho phép và coi NaN lớn hơn mọi số, nên `price > 0` một mình không đủ). Precision được chốt bằng migration riêng sau khi có evidence nguồn.
- `macro_observations` có FK tổng hợp (series_id, metadata_version) tới `macro_series`; khóa nghiệp vụ là (series_id, observation_date, revision_key), không gồm metadata_version, nên đổi metadata không tạo bản sao quan sát.
- Mọi FK dùng RESTRICT mặc định; không cascade. `revision_key` NOT NULL và không rỗng.
- Chưa tạo bảng dataset/feature/model/prediction (migration 2 và 3 theo kế hoạch).

## Hệ quả và kiểm chứng

Test tích hợp PostgreSQL kiểm tra: schema từ DB sạch, upgrade/downgrade/upgrade, không lệch autogenerate, unique/check/FK, NUMERIC khứ hồi chính xác, TIMESTAMPTZ, rollback. Chưa kiểm chứng: PostgreSQL 17 (test chạy trên 16.15), upgrade từ schema cũ (mới có một revision).

## Điều kiện xem xét lại

Sau GS-002: chốt precision/scale và đơn vị nếu nguồn đòi hỏi. Nếu dung lượng/index UUID trở thành vấn đề đo được.
