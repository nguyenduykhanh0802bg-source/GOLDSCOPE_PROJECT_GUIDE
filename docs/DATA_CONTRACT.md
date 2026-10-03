# Hợp đồng dữ liệu GoldScope

**Version:** 0.1-draft. **Mapping GOLD:** chưa xác minh. Đây là schema nội bộ mục tiêu; không khẳng định response nhà cung cấp có các trường bên dưới.

Nguồn trạng thái mapping hiện tại: `../configs/data-contract.json`. Bản trong `../lab00/configs/` là snapshot lịch sử của Lab 00, không cập nhật nó như bản trạng thái thứ hai.

## 1. Định danh và đơn vị

- Asset mục tiêu: `GOLD_USD`; currency/unit kỳ vọng là USD/troy ounce, chưa được xác nhận bằng dữ liệu nguồn.
- Giữ `source_id`, `source_symbol`, `price_definition`, currency và unit tách biệt.
- Không thay ETF/futures/vàng thương hiệu trong nước vào cùng chuỗi spot.
- Macro series có đơn vị riêng; yield âm có thể hợp lệ, không áp quy tắc giá vàng dương lên mọi series.
- Số phần trăm trong API forecast dùng tỷ lệ: 0.01 là 1%; macro raw giữ đúng đơn vị nguồn và chỉ chuyển đổi ở feature layer có tài liệu.

## 2. Thời gian

| Trường | Kiểu nội bộ | Null? | Ý nghĩa |
|---|---|---|---|
| `observation_date` | date | Không | Ngày/kỳ số liệu mô tả |
| `source_published_at` | UTC timestamp | Có | Publication time nếu chứng minh được |
| `available_at` | UTC timestamp | Theo trạng thái | Mốc được phép dùng; bắt buộc trước khi feature/live sử dụng |
| `ingested_at` | UTC timestamp | Không | Thời điểm thu nhận thực tế |
| `vintage_date` | date | Có | Phiên bản lịch sử do nguồn cung cấp |
| `availability_basis` | enum | Không | verified / conservative_proxy / first_seen / unknown |

Live dùng `available_at >= ingested_at` khi dữ liệu chỉ được biết từ lúc thu nhận; không backdate live. Historical reconstruction cho phép ingest hôm nay nhưng phải có evidence publication/vintage quá khứ. Nếu chỉ có vintage date, dùng chính sách bảo thủ theo timezone nguồn, ghi proxy, không tuyên bố chính xác trong ngày.

`availability_basis=unknown` được lưu raw/normalized để khảo sát nhưng không đủ điều kiện vào point-in-time features. Mọi feature origin phải có `available_at <= as_of`; mỗi mẫu train có label availability không muộn hơn fit cutoff.

## 3. Giá đã chuẩn hóa

| Trường | Kiểu | Ràng buộc |
|---|---|---|
| `id` | UUID hoặc khóa DB | Sinh khi lưu |
| `asset_id`, `source_id` | string/FK | Không rỗng |
| `observation_date` | date | Theo lịch nguồn đã xác minh |
| `price` | Decimal/NUMERIC | Hữu hạn, >0 cho GOLD |
| `currency`, `unit` | string | Khớp source contract được phê duyệt |
| `price_definition` | string | reference/close/... chỉ khi nguồn xác nhận |
| `revision_key` | string | Non-null, nguồn hoặc hash nội dung canonical |
| `raw_object_id` | FK | Truy nguyên raw |
| Nhóm timestamp ở mục 2 | datetime/date | Theo chính sách availability |

Không yêu cầu OHLCV khi nguồn chỉ có một giá tham chiếu. Không tạo open/high/low/volume giả. Nếu có OHLC đã xác minh, thêm schema có version và kiểm tra thứ tự low/high.

## 4. Macro đã chuẩn hóa

`series_id`, `observation_date`, `value` nullable, `units`, `frequency`, `vintage_date`, `revision_key`, nhóm timestamp, `raw_object_id`.

Giá trị thiếu như dấu chấm của FRED chuyển thành null, không thành 0. Lưu metadata series và lịch release riêng. Khi xây dataset origin: lọc phiên bản được biết → chọn revision đúng cho observation → chọn observation đã công bố phù hợp → mới forward fill nếu chính sách cho phép. Không backward fill.

## 5. Raw và provenance

Raw object lưu source/endpoint không chứa key, fetched_at, status, content type, checksum, schema version và URI nội bộ. Lưu response lỗi riêng với metadata thích hợp, không chuẩn hóa thành observation.

Audit standalone hiện chỉ lưu summary/hash, không lưu raw toàn văn. Collector production phải hiện thực raw storage theo quyền nguồn, và không đổi nhãn evidence audit cũ thành raw dataset.

## 6. Duplicate và revision

- Market key: asset + source + observation date + revision key.
- Macro key: series + observation date + revision key.
- Tải lại payload giống hệt không tạo revision mới. `ingested_at` không phải revision key.
- Dữ liệu sửa tạo revision mới; giữ lịch sử và timestamp được biết.
- Khi nhiều giá cho một ngày không thể xác định revision/source meaning: quarantine và ghi lỗi, không lấy dòng cuối ngẫu nhiên.

## 7. Chất lượng và xử lý missing

| Vấn đề | Hành vi |
|---|---|
| HTTP 200 có Information/Note/error | Ghi provider error, không tạo observations |
| Giá GOLD không hữu hạn/không dương | Quarantine; chặn forecast origin liên quan |
| Currency/unit/schema đổi | Chặn normalize; giữ raw và báo lỗi contract |
| Duplicate business key | Dedupe/upsert; kiểm tra xung đột nội dung |
| Gap calendar | Chưa gọi là missing session khi lịch nguồn chưa xác minh |
| Outlier lớn | Cảnh báo và điều tra; không tự xóa biến động thật |
| Macro quá cũ | Theo ngưỡng riêng mỗi series; không ngầm đổi feature/model |
| Không có quan sát mới ngày nghỉ | skipped nếu calendar xác minh phù hợp |

Không xóa gap chưa giải quyết rồi đếm `shift(-5)` như thể luôn là 5 phiên đúng. Feature/target cần calendar/index policy có version. V1.0 dùng valid provider observations đã audit; không tự áp lịch NYSE hoặc tạo cuối tuần.

## 8. Dataset và feature snapshot

Manifest: snapshot ID, raw/revision IDs, date range, row count, schema/hash, availability policy version, calendar version, code SHA, created_at. Snapshot đã dùng cho model không sửa trực tiếp.

Feature registry ghi tên, dtype, unit, công thức, lookback, min_periods, missing policy và required input availability. Feature builder trả cả các origin chưa có nhãn để dùng inference; target builder tách riêng.

Target: simple return `P[t+h]/P[t]-1`, h=1/5. Lưu origin price/revision, target observation/date và label_available_at. Không tạo target giả khi giá đích chưa có.

## 9. Tin tức — hợp đồng tương lai

URL canonical, source, published_at, first_seen_at, raw/reference ID, title/hash, quyền lưu, cluster ID. Tín hiệu NLP có model/version/relevance và computed_at. Tin chỉ được dùng khi khả dụng trước cutoff; bài sửa phải có revision hoặc giới hạn rõ. Lịch sử không tái dựng được thì chỉ dùng prospective/dashboard, không làm backtest giả.

## 10. Source sign-off cần evidence

- [ ] Response GOLD bằng key dự án có dữ liệu, không chỉ HTTP 200.
- [ ] Giá/đơn vị/currency/definition được xác minh.
- [ ] Đo first/last date, row count, missing/duplicate và pagination.
- [ ] Lịch nguồn/timezone/cutoff hoặc giới hạn proxy được ghi.
- [ ] Revision history và quyền lưu/hiển thị được kiểm tra.
- [ ] Contract JSON và audit cập nhật cùng nhau.

Mục tiêu 5 năm là gate lập kế hoạch nghiên cứu, không bảo đảm model hiệu quả. Không lấy series khác thay thế chỉ để đạt số năm.
