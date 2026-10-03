# GoldScope — Báo cáo Lab 00: kiểm chứng nguồn dữ liệu

**Ngày kiểm chứng:** 30/09/2026.  
**Kết luận:** hoàn thành phần nghiên cứu nguồn và công cụ kiểm chứng; **Lab 00 chưa đạt gate dữ liệu**. Thiếu key của dự án nên chưa xác nhận được dataset vàng, quyền truy cập tài khoản và metadata cần cho forecast cutoff.

## 1. Phạm vi đã thực hiện

Theo phần 6 và Lab 00 của `GOLDSCOPE_PROJECT_GUIDE.md`:

1. Đối chiếu tài liệu chính thức Alpha Vantage và FRED.
2. Gọi trực tiếp endpoint vàng với demo key và FRED với request không key.
3. Kiểm tra sự hiện diện của đúng hai biến môi trường cần cho dự án; không tìm hoặc in secret khác.
4. Tạo script audit bằng key tài khoản, hợp đồng dữ liệu dự thảo và hướng dẫn chạy.
5. Kiểm thử offline hành vi quan trọng; lưu evidence của các request thật.

Chưa đăng ký tài khoản thay người dùng, chưa chọn/mua gói dữ liệu, chưa tải lịch sử giá hợp lệ, chưa tạo dữ liệu giả thay cho kết quả API.

## 2. Bằng chứng thực tế

Các mốc dưới được lấy từ `evidence/public-probe.json`; timezone UTC, cộng 7 giờ để đối chiếu giờ Việt Nam.

| Kiểm tra | Thời điểm request UTC | HTTP | Nội dung nhận được | Kết luận |
|---|---|---|---|---|
| Gold history, symbol GOLD, daily, demo key | 2026-09-30 07:42:46 | 200 | Object chỉ có trường `Information` | Không có dữ liệu giá; không coi là thành công tải dữ liệu |
| FRED observations DGS10, không key | 2026-09-30 07:42:56 | 400 | `error_code`, `error_message` | Thiếu key; chưa kiểm chứng observations của tài khoản |
| Biến `ALPHA_VANTAGE_API_KEY` | Trong preflight | — | Chưa được cấu hình | Cần key dự án |
| Biến `FRED_API_KEY` | Trong preflight | — | Chưa được cấu hình | Cần key dự án |

Evidence lưu endpoint, tham số đã che key, thời điểm, HTTP status, số byte, SHA-256 và schema phản hồi. Không lưu response nguyên văn hoặc toàn bộ dữ liệu thương mại vào gói chia sẻ.

Đã có một lượt kiểm tra sơ bộ và một lượt ghi evidence bằng script; kết quả nhất quán. Không dùng các lượt gọi không key để suy ra key riêng chắc chắn sẽ được cấp quyền.

## 3. Audit nguồn vàng

| Thuộc tính | Kết quả | Mức xác nhận |
|---|---|---|
| Nhà cung cấp ứng viên | Alpha Vantage | Đã chọn để audit, chưa ký duyệt nguồn |
| Endpoint | `GET https://www.alphavantage.co/query` | Theo tài liệu chính thức [1] |
| Function | `GOLD_SILVER_HISTORY` | Theo tài liệu [1] |
| Symbol/tần suất dự kiến | `GOLD`, `daily` | Theo tài liệu [1] |
| Key tài khoản dự án | Chưa có trong môi trường | Đã kiểm tra |
| Request demo | HTTP 200 nhưng không có data | Đã gọi thực tế |
| Cột giá/schema GOLD | Chưa biết | Chờ response có dữ liệu |
| OHLCV | Chưa xác nhận | Không giả định đầy đủ |
| USD/troy ounce | Là đơn vị mục tiêu của dự án | Cần xác nhận từ nguồn/metadata |
| Ngày đầu/cuối và số quan sát | Chưa biết | Chờ lịch sử thật |
| Mục tiêu độ phủ | Ít nhất 5 năm | Tiêu chí dự án, không phải cam kết nhà cung cấp |
| Lịch phiên/múi giờ/giờ cập nhật | Chưa biết | Cần tài liệu nguồn và quan sát qua nhiều ngày |
| Revision lịch sử | Chưa xác minh | Không mặc định immutable |
| Quyền lưu/hiển thị/chia sẻ lại | Chưa chốt cho gói tài khoản | Xem điều khoản và gói thực tế [3] |

Trang hỗ trợ mô tả mức miễn phí phổ biến 25 request/ngày [2]. Đây không phải xác nhận endpoint vàng hoặc toàn bộ lịch sử sẽ mở cho key bất kỳ. Chỉ nên dùng audit ít request để kiểm tra trước khi quyết định gói.

**Quyết định:** giữ Alpha Vantage làm ứng viên số 1. Nếu key riêng không cung cấp đủ lịch sử/metadata trong ngân sách, lập audit nguồn thay thế; không lặng lẽ chuyển sang ETF/futures và gọi đó là cùng chuỗi vàng giao ngay.

## 4. Audit macro

FRED yêu cầu API key cho web service và hướng dẫn tạo key riêng theo ứng dụng [4]. Request không key thực tế trả 400, phù hợp với yêu cầu này.

| Series | Metadata đã đối chiếu từ trang chính thức | Trạng thái API bằng key dự án |
|---|---|---|
| `DGS10` | Lợi suất Treasury 10 năm; đơn vị phần trăm; tần suất ngày [6] | Chưa gọi |
| `DFII10` | Lợi suất Treasury 10 năm điều chỉnh lạm phát; phần trăm; ngày [7] | Chưa gọi |
| `DTWEXBGS` | Chỉ số USD danh nghĩa diện rộng; index Jan 2006=100; ngày [8] | Chưa gọi |

`DTWEXBGS` không đổi tên thành ICE DXY. Metadata “ngày” mô tả tần suất observations, không xác nhận giá trị ngày D được công bố trước forecast ngày D.

Script đã chuẩn bị cho từng series:

1. `/fred/series`: metadata.
2. `/fred/series/observations`: tối đa 100.000 dòng, offset 0, kiểm tra `count` so với số dòng nhận [5]. Nếu chưa đủ phải hoàn thiện pagination trước khi nói đã tải đủ.
3. `/fred/series/vintagedates`: mẫu 5 ngày vintage gần nhất [9]. Đây là kiểm tra khả năng truy cập, không phải dựng toàn bộ lịch sử revision.

Để macro vào backtest, phải bổ sung giá trị theo vintage và chính sách `available_at`. Endpoint mặc định trả observations hiện biết không tự tạo được dataset point-in-time.

## 5. Hợp đồng bài toán đã chốt và chưa chốt

**Đã chốt:** dự báo một chuỗi giá vàng theo ngày; định danh nội bộ `GOLD_USD`; 1/5 phiên dữ liệu hợp lệ; target `P(t+h)/P(t)-1`; baseline lợi suất 0; timestamp hệ thống UTC; không đặt lệnh giao dịch.

**Chưa chốt:** tên cột giá, ý nghĩa giá tham chiếu/close, unit/currency đã xác minh, timezone của nguồn, lịch observations, giờ dữ liệu sẵn sàng, forecast cutoff, quyền lưu/hiển thị và revision policy. Các trường này là null/false trong `configs/data-contract.json`.

Với live data, nếu chỉ biết thời điểm thu nhận thì dùng `first_seen`; không gán ngày quan sát làm thời điểm công bố. Với historical backtest, không dùng `ingested_at` hôm nay để giả định thông tin đã có trong quá khứ.

## 6. Công cụ và kết quả kiểm thử

`scripts/audit_sources.py` dùng Python standard library, không cài thêm package. Endpoint chỉ thuộc hai host HTTPS đã chọn, không tự theo redirect, request có timeout và giới hạn response 10 MiB.

Công cụ không lưu key, URL có key hoặc thông báo exception có thể chứa key. Report chứa cấu trúc và thống kê tổng hợp. Mặc định không có key thì đánh dấu blocked, không phát sinh request tài khoản.

**12 kiểm thử đã đạt:** HTTP 200 chứa thông báo; thông báo kèm data một phần; FRED HTTP error; kiểm tra phân trang; không tự suy schema GOLD; dữ liệu rỗng; ngày sai/trùng/giá trị thiếu; real yield âm; che secret trong lỗi mạng; không gọi mạng khi thiếu key; payload không phải object; chặn host ngoài cấu hình.

Các test dùng dữ liệu tổng hợp để kiểm tra logic. Chúng không thay thế authenticated integration test, kiểm chứng history coverage hoặc độ mới của nguồn.

## 7. Gate Lab 00

| Điều kiện | Trạng thái hiện tại |
|---|---|
| Xác định endpoint và ba macro series | Đạt phần tài liệu |
| Có công cụ audit chạy được và kiểm thử | Đạt |
| Có evidence của request công khai | Đạt |
| Tải được giá GOLD bằng key dự án | Chưa đạt — thiếu key |
| Xác nhận price field, currency, unit | Chưa đạt |
| Đo độ phủ lịch sử, missing, duplicate | Chưa đạt |
| Xác nhận lịch nguồn, thời điểm công bố, cutoff | Chưa đạt |
| Kiểm tra revision và quyền sử dụng phù hợp | Chưa đạt |
| Gọi thành công ba series macro bằng key dự án | Chưa đạt — thiếu key |

**Lab 00 = IN PROGRESS / BLOCKED ON CREDENTIALS AND SOURCE VERIFICATION.** Không chuyển trạng thái sang DONE chỉ vì script chạy không crash hoặc một endpoint trả 200.

Khung repo/môi trường ở Lab 01 có thể triển khai song song. Tuy nhiên, collector chính và pipeline dự báo phải dựa trên schema/contract đã kiểm chứng.

## 8. Hành động tiếp theo

1. Người dùng lấy key của riêng mình tại [Alpha Vantage](https://www.alphavantage.co/support/#api-key) và [FRED](https://fred.stlouisfed.org/docs/api/api_key.html).
2. Chạy script với `--prompt-keys` trên máy cá nhân, theo README. Không gửi key trong chat.
3. Đọc hoặc cung cấp report `runtime/my-source-audit.json`, đã được thiết kế không chứa key.
4. Đối chiếu schema/dữ liệu nhận được; nếu trường giá chưa rõ, xem payload cục bộ và ghi tên trường cùng metadata sau khi loại secret.
5. Cập nhật contract và source audit. Lập kế hoạch quan sát thời điểm cập nhật qua nhiều ngày, không ký duyệt một giờ scheduler tùy ý.

Không có nhu cầu mua gói, tạo tài khoản thay người dùng hoặc đăng tải dữ liệu công khai trong bước đã thực hiện này.

## 9. Nguồn tham khảo đã đối chiếu

1. [Alpha Vantage — API Documentation](https://www.alphavantage.co/documentation/), mục Gold & Silver Historical Prices.
2. [Alpha Vantage — Support](https://www.alphavantage.co/support/), API key và giới hạn sử dụng.
3. [Alpha Vantage — Terms of Service](https://www.alphavantage.co/terms_of_service/). Cần đối chiếu với quyền tài khoản cụ thể; tài liệu này chưa ký duyệt quyền tái phân phối.
4. [FRED — API Key](https://fred.stlouisfed.org/docs/api/api_key.html).
5. [FRED — Series Observations](https://fred.stlouisfed.org/docs/api/fred/series_observations.html).
6. [FRED — DGS10](https://fred.stlouisfed.org/series/DGS10).
7. [FRED — DFII10](https://fred.stlouisfed.org/series/DFII10).
8. [FRED — DTWEXBGS](https://fred.stlouisfed.org/series/DTWEXBGS).
9. [FRED — Vintage Dates](https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html).

Trang tài liệu chứng minh thông tin được nhà cung cấp công bố. Chỉ evidence request của dự án mới chứng minh môi trường đã gọi được gì; hai loại bằng chứng được tách riêng trong báo cáo này.
