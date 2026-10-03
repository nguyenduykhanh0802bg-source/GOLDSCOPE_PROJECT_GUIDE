# Giao thức nghiên cứu và đánh giá ML

**Version:** 0.1-design. Chưa có dataset hoặc model đã fit. Mọi con số dưới đây là tham số kế hoạch, không phải kết quả thực nghiệm.

## 1. Bài toán

Một model mỗi horizon h=1/5 valid provider observations. Target lợi suất đơn `y[t,h]=P[t+h]/P[t]-1`; giá dự báo `P[t]*(1+y_hat)`. Baseline `y_hat=0`. Phân loại xác suất, h=20 và model sâu chỉ ở nhánh mở rộng.

Origin có giá đã biết, as_of là cutoff dữ liệu, issued_at là thời điểm phát hành. Fit cutoff có nghĩa thời điểm model được phép biết labels. Giá tương lai không được dùng trong feature.

## 2. Data eligibility

- Source contract đủ metadata và availability policy.
- Dữ liệu giá lỗi/gap chưa giải quyết không bị âm thầm xóa để tạo horizon giả.
- Với mỗi origin, chọn đúng vintage/revision đã sẵn sàng.
- Train row hợp lệ khi mọi feature khả dụng đúng origin và label_available_at<=fit_cutoff.
- Historical source chỉ có current revision phải nêu hạn chế; không gọi phép đánh giá là point-in-time chính xác khi không chứng minh được.
- Loại macro/tin khỏi backtest nghiêm ngặt nếu không biết lịch sử công bố; có thể để dashboard/prospective.

## 3. Feature v1

Returns 1/5/20; lag return 1/2/5; relative MA5/MA20; rolling volatility 5/20/60. Mỗi feature có tên/dtype/unit/formula/lookback/min_periods/missing policy/schema version.

Feature builder là pure transformation sau lựa chọn dữ liệu. Dùng chung trong train/live. Target builder tách riêng để giữ origin cuối chưa có label cho inference. Không fit imputer/scaler trên toàn dataset trước split.

RSI/MACD được thêm sau ablation có mục tiêu; không tạo hàng trăm feature rồi chọn theo holdout.

## 4. Split và retrain

Nếu đủ >=5 năm: giữ 12 tháng cuối làm final holdout; phần trước là development; train đầu khoảng 2 năm; validation block khoảng 3 tháng. Mốc tuyệt đối được chốt sau audit và lưu trong config, không lấy ngày ví dụ làm ngày thật.

Trong mỗi block mô phỏng fit theo tháng và predict theo từng origin; mẫu train chỉ dùng label đã trưởng thành. TimeSeriesSplit/gap là công cụ hỗ trợ, không thay kiểm tra timestamp. Khởi đầu gap>=h theo index đã audit; độ trễ nguồn có thể cần lớn hơn.

Train, validation/calibration và final holdout khác mục đích. Nếu dùng holdout để chọn/tune, đổi trạng thái nó thành development và cần cửa sổ tương lai mới để đánh giá độc lập.

## 5. Model và tuning

1. Zero-return baseline.
2. Ridge với preprocessing fit riêng mỗi training window.
3. XGBoost point forecast, tập khoảng 10–20 cấu hình đầu có giới hạn.
4. Quantile q10/q90; q50 nếu cần trung vị.

Hyperparameters, seed, library versions, early stopping window và số thí nghiệm phải được ghi. Không dùng test làm early stopping set. Không gọi quantile median là expectation.

## 6. Khoảng dự báo

Interval 80% danh nghĩa từ q10/q90. Đánh giá pinball loss, coverage và width ngoài mẫu. Nếu quantile crossing, ghi tần suất, chính sách xử lý có version và chấm metrics sau xử lý. Interval bị thiếu trả null; không lấy độ chính xác quá khứ làm confidence của một forecast.

Calibration dùng quá khứ riêng. Không tự tuyên bố bảo đảm thống kê của conformal trong chuỗi thời gian phụ thuộc nếu chưa nêu và kiểm tra giả định.

## 7. Metrics

| Metric | Quy ước |
|---|---|
| MAE/RMSE return | Primary/secondary, cùng origins và horizon |
| MAE price | USD/đơn vị đã xác minh; phụ thuộc mức giá |
| Baseline skill | 1 - MAE_model/MAE_baseline, null nếu mẫu số 0 |
| Direction accuracy | Nêu cách xử lý return=0; baseline hướng riêng |
| Pinball/coverage/width | Cho quantile/interval; nêu nominal level |

Không dùng MAPE return làm metric chính khi mẫu số gần 0. Label h=5 chồng lấn nên sai số không độc lập; nếu tính CI dùng phương pháp có cấu trúc thời gian, chẳng hạn block bootstrap đã thiết kế trước hoặc origins không chồng lấn. Không diễn giải hàng nghìn rows là hàng nghìn mẫu độc lập.

## 8. Experiments và promotion

E00 zero-return; E01 Ridge price-only; E02 XGBoost price-only; E03 price+macro; E04 price+macro+news; E05 intervals. So sánh trên cùng origins, split, horizon và chế độ availability. Nếu news history ngắn, giới hạn cả hai model vào phần giao nhau.

Promotion dựa vào validation gate đăng ký trước và các kiểm tra kỹ thuật. Ngưỡng cải thiện 2% MAE tương đối trong guide chỉ là tiêu chí ứng viên ban đầu, không tự là bằng chứng ý nghĩa thống kê. Model không tốt hơn baseline thì giữ baseline active, báo model nghiên cứu như thực tế.

Final holdout chỉ dùng đánh giá release đã chốt; không lấy làm leaderboard tune mỗi tháng. Retrain monthly dùng validation/shadow mới theo giao thức riêng.

## 9. Model manifest tối thiểu

Model ID/family/horizon; feature schema/hash; snapshot/raw/revision IDs; code SHA; Python/library versions; seed/config; fit cutoff; train/validation periods; protocol version; prediction path; per-fold/aggregate metrics; artifact hash; interval method; calibration window; promotion decision/reason.

Manifest thiếu phần trọng yếu thì model chưa eligible live. Native model file không đủ để khôi phục preprocessing pipeline.

## 10. Kiểm thử và báo cáo

Temporal tests phải chứng minh: sửa tương lai không đổi feature quá khứ; release sau cutoff không lọt vào origin; nhãn chưa có không vào fit; train/live cùng đầu vào cho cùng feature/schema.

Báo cáo phải có cả model kém baseline, số cấu hình đã thử và giới hạn nguồn. SHAP nếu thêm chỉ giải thích model, không chứng minh nhân quả. Forecast backtest không phải trading backtest; không suy PnL từ MAE.
