# REST API contract

**Version:** v1 draft. **Trạng thái:** chưa có endpoint chạy thật. JSON dưới là fixture tổng hợp, không phải giá/dự báo thị trường.

## 1. Quy ước chung

- Prefix nghiệp vụ `/api/v1`; health không cần prefix.
- Timestamp ISO 8601 UTC, observation date dạng YYYY-MM-DD.
- Asset đầu: `GOLD_USD`; horizon đầu: 1 hoặc 5 valid provider observations.
- Return là tỷ lệ thập phân; price kèm currency/unit đã được source contract xác minh.
- Các giá trị chưa có trả null; không sinh default 0 cho price/forecast/outcome.
- `mode`: live / backtest / synthetic_demo. Mặc định lịch sử forecast phục vụ người dùng lọc live; demo phải chỉ rõ mode.
- Validation và lỗi đều được mô tả trong OpenAPI thực tế khi API được viết.
- MVP đọc dữ liệu; thao tác ingest/train/promote qua CLI. Không thêm POST quản trị public nếu chưa có auth/authorization design.

## 2. Endpoint

| Method/path | Input | Output chính |
|---|---|---|
| GET `/health/live` | Không | status ok nếu process sống |
| GET `/health/ready` | Không | status ready hoặc 503 khi DB/phụ thuộc phục vụ chưa sẵn sàng |
| GET `/api/v1/market/latest` | asset mặc định GOLD_USD | Price observation mới nhất, source/freshness |
| GET `/api/v1/market/history` | asset, from, to, limit, offset | List observations có thứ tự date tăng |
| GET `/api/v1/forecasts/latest` | asset, horizon_sessions, mode mặc định live | Forecast mới nhất theo issued_at |
| GET `/api/v1/forecasts/history` | asset, horizon_sessions, mode, from/to theo issued_at, limit/offset | Forecasts theo issued_at giảm, ID làm tie-break |
| GET `/api/v1/forecasts/{prediction_id}` | ID | Forecast + outcome nếu đã đến hạn |
| GET `/api/v1/models` | horizon_sessions tùy chọn, limit/offset | Model metadata/status |
| GET `/api/v1/models/{model_id}/performance` | ID | Metrics, horizon, số mẫu, period, split protocol, baseline |
| GET `/api/v1/data-quality` | source_id tùy chọn | Freshness và sự kiện quality đã làm sạch thông tin nhạy cảm |

`from/to` là inclusive. Market dùng date; forecast history dùng UTC timestamp. Tên alias `from` được map đúng trong schema Python. Với history: limit mặc định 250, tối đa 2.000, offset>=0. Unsupported asset/horizon trả 422. from>to trả 422. Page list không có hàng trả items=[], không 404.

Offset đủ cho MVP dataset nhỏ; nếu chuyển sang cursor phải tăng contract/version phù hợp và cập nhật client. Trong lúc có insert đồng thời, client không được coi offset là snapshot nhất quán của toàn bộ lịch sử.

## 3. Envelope cho danh sách

```json
{
  "items": [],
  "pagination": {"limit": 250, "offset": 0, "returned": 0, "has_more": false},
  "request_id": "synthetic-request-001"
}
```

Endpoint resource đơn trả object domain cùng `request_id`, không lồng items. HTTP header `X-Request-ID` dùng giá trị đã validate hoặc giá trị server sinh; không ghi payload người dùng tùy ý vào log identifier.

## 4. Forecast response mẫu

```json
{
  "prediction_id": "synthetic-prediction-001",
  "asset": "GOLD_USD",
  "source": "synthetic-source",
  "currency": "USD",
  "unit": "troy_ounce",
  "origin_observation_date": "2026-09-28",
  "as_of": "2026-09-29T00:00:00Z",
  "issued_at": "2026-09-29T00:01:00Z",
  "horizon_sessions": 5,
  "target_observation_date": null,
  "origin_price": 1000.0,
  "predicted_return": 0.01,
  "predicted_price": 1010.0,
  "prediction_interval": {
    "nominal_level": 0.8,
    "lower_return": -0.02,
    "upper_return": 0.04,
    "lower_price": 980.0,
    "upper_price": 1040.0,
    "method": "quantile"
  },
  "model_version": "synthetic-xgb-h5-v1",
  "feature_version": "price-v1",
  "mode": "synthetic_demo",
  "freshness_status": "fresh",
  "outcome": null,
  "request_id": "synthetic-request-001"
}
```

`prediction_interval` có thể null khi model baseline/ứng viên chưa cung cấp interval; không làm giả interval để khớp UI. Nếu outcome có, chứa target date, actual price/return, scored_at, score_revision; không cập nhật issued_at của prediction.

`target_observation_date` có thể null khi chưa thể xác định ngày đích theo calendar; phải có quy tắc h-th observation nhất quán. Live issuance vẫn phải kiểm tra origin/freshness và target chưa thành quá khứ; lịch không rõ đến mức không bảo đảm được thì chặn live.

## 5. Market/latest và performance

Market response: asset, source, observation_date, price, price_definition, currency, unit, available_at, ingested_at, freshness_status, request_id. Định nghĩa price và unit lấy từ contract đã xác minh.

Performance response: model_id, horizon_sessions, evaluation_kind, period_start/end, n_origins, dataset_hash, protocol_version, mae_return, rmse_return, mae_price, baseline_mae_return, baseline_skill, interval metrics nullable và per_fold items.

Metrics tỷ lệ giữ đơn vị rõ; muốn UI hiển thị percentage points/bps thì đổi ở presentation. Baseline skill mẫu số 0 trả null + reason, không Infinity/NaN. Không trộn live và holdout metrics trong một con số thiếu nhãn.

## 6. Error contract

```json
{
  "error": {
    "code": "FORECAST_NOT_FOUND",
    "message": "No forecast matches the requested asset and horizon.",
    "request_id": "synthetic-request-002",
    "details": null
  }
}
```

| HTTP | Code ví dụ | Hành vi |
|---|---|---|
| 404 | RESOURCE_NOT_FOUND, FORECAST_NOT_FOUND | Resource đơn không tồn tại |
| 422 | INVALID_QUERY | Input/horizon/range không hợp lệ |
| 503 | DEPENDENCY_UNAVAILABLE | DB/phụ thuộc cần thiết không phục vụ được |
| 500 | INTERNAL_ERROR | Lỗi không dự kiến; response không chứa stack/secret |

Đăng ký handler để validation errors của framework cũng theo envelope. HTTP 200 với forecast stale vẫn hợp lệ nếu ghi `freshness_status=stale` và giữ timestamp cũ. Không trả 200 “fresh” sau khi chỉ đổi ngày trên bản ghi cũ.

## 7. Nghiệm thu contract

API tests kiểm tra schema, numeric units, null, enum, ordering, paging, invalid ranges, 404/422/503 và redaction. UI contract tests dùng fixtures cùng schema. OpenAPI sinh từ code là tài liệu wire format thực tế; so nó với bản này và giải quyết mọi discrepancy trước release.

Route `/forecasts/latest` và `/forecasts/history` phải được định tuyến không bị bắt nhầm bởi `/{prediction_id}`. Load test chỉ bắt đầu khi endpoint, dataset và môi trường đã có thật; không ghi p95 chưa đo.
