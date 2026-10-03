# GoldScope — Lab 00: kiểm chứng nguồn dữ liệu

**Ngày:** 30/09/2026. **Trạng thái:** đã làm phần kiểm chứng công khai và công cụ audit; **chưa vượt gate Lab 00 do thiếu API key của dự án và metadata giá vàng cần xác minh**.

Đây là kết quả thực hiện bước đầu trong `GOLDSCOPE_PROJECT_GUIDE.md`, không phải backend hay mô hình đã hoàn thành. Chưa tạo repository GitHub, chưa tải dataset dùng cho training và chưa huấn luyện model.

## 1. Trong gói có gì?

| File | Mục đích |
|---|---|
| `docs/data-source-audit.md` | Kết quả kiểm chứng thực tế, nguồn chính thức, điều kiện còn thiếu |
| `docs/ADR-0001-source-contract.md` | Quyết định đã chốt và những phần chưa chốt |
| `configs/data-contract.json` | Hợp đồng dữ liệu dạng máy đọc được; chưa xác minh thì để null/false |
| `scripts/audit_sources.py` | Công cụ chạy kiểm tra API bằng key của chính bạn |
| `tests/test_audit.py` | 12 kiểm thử quan trọng, chạy offline |
| `evidence/public-probe.json` | Kết quả request thật dùng demo/no-key, gồm thời điểm và SHA-256 response |
| `evidence/account-preflight.json` | Bằng chứng môi trường hiện chưa có key; không gọi API tài khoản |
| `evidence/test-summary.json` | Tóm tắt lần chạy kiểm thử thực tế |

Script chỉ dùng thư viện chuẩn Python để bạn chạy Lab 00 ngay, chưa cần cài FastAPI/PostgreSQL. Ứng dụng chính ở Lab 01 trở đi vẫn theo stack Python 3.12, uv, HTTPX, FastAPI và PostgreSQL của tài liệu.

## 2. Kết quả hiện tại

- Endpoint vàng với `apikey=demo` trả HTTP 200 nhưng chỉ có trường `Information`, không có chuỗi giá. Script đánh dấu `provider_message_not_data`.
- FRED API không có key trả HTTP 400. Script đánh dấu `http_error`.
- Cả hai biến môi trường API key đang thiếu. Đây là trạng thái của môi trường thực hiện Lab 00, không khẳng định tài khoản của bạn chưa từng có key.
- Các trang chính thức của DGS10, DFII10, DTWEXBGS đã được đối chiếu để xác nhận tên/đơn vị/tần suất, chưa thay thế việc gọi API bằng key của dự án.
- 12 kiểm thử đã đạt. Điều này xác minh hành vi công cụ, không xác minh quyền tải dữ liệu hay chất lượng model.

## 3. Bạn cần chuẩn bị

1. Một API key Alpha Vantage: [trang đăng ký chính thức](https://www.alphavantage.co/support/#api-key).
2. Một API key FRED dành cho ứng dụng GoldScope: [hướng dẫn và đường dẫn lấy key](https://fred.stlouisfed.org/docs/api/api_key.html). FRED yêu cầu đăng nhập tài khoản trước khi tạo/xem key.
3. Python 3.12 trên máy. Trong PowerShell hoặc terminal, kiểm tra bằng `python --version`. Nếu bạn dùng Windows Python Launcher, có thể dùng `py -3.12` thay cho `python` trong các lệnh dưới.

Không cần gửi API key vào cuộc trò chuyện. Script có chế độ nhập ẩn và không lưu key vào báo cáo. Chưa cần mua gói trả phí; kiểm tra quyền thực tế của key trước.

## 4. Chạy trên Windows, WSL hoặc Linux

Giải nén ZIP. Mở terminal tại thư mục chứa `README.md`, `scripts`, `tests`.

### Bước A — Kiểm tra công cụ offline

```bash
python -m unittest discover -s tests -v
```

Kết quả mong đợi: `Ran 12 tests`, `OK`.

### Bước B — Chạy audit bằng key cá nhân

```bash
python scripts/audit_sources.py --prompt-keys --out runtime/my-source-audit.json
```

Nhập hai key khi được hỏi. Ký tự không hiện trên màn hình; nhấn Enter để xác nhận. Để trống một key nếu muốn bỏ qua nguồn đó.

Nếu đã cấu hình biến môi trường `ALPHA_VANTAGE_API_KEY` và `FRED_API_KEY` bằng cơ chế bảo mật của máy, dùng:

```bash
python scripts/audit_sources.py --out runtime/my-source-audit.json
```

Script **không tự đọc file `.env`**. Chọn nhập ẩn hoặc cấu hình biến môi trường; không chỉ tạo `.env` rồi cho rằng script đã nạp.

Mỗi lần audit đầy đủ gọi tối đa 1 request vàng và 9 request FRED (metadata, observations, mẫu vintage cho mỗi series). Không tự retry và không lặp vô hạn. Thời gian chờ tối đa mặc định là 20 giây/request; dừng hoặc kiểm tra mạng nếu nguồn không phản hồi.

### Bước C — Đọc kết quả

Mở `runtime/my-source-audit.json` trong VS Code. Báo cáo không chứa toàn bộ lịch sử giá và không cần gửi key. Có thể gửi file báo cáo này để tiếp tục đối chiếu schema và chốt hợp đồng nguồn; vẫn nên kiểm tra nội dung trước khi chia sẻ.

| Trạng thái | Nghĩa là gì? | Việc tiếp theo |
|---|---|---|
| `blocked_missing_key` | Nguồn chưa được cung cấp key | Nhập/cấu hình key |
| `provider_message_not_data` | Nhà cung cấp trả thông báo thay vì data | Kiểm tra key/quota/quyền endpoint trong tài khoản |
| `http_error` | HTTP không thành công | Kiểm tra status; 400 thiếu/sai tham số, 401/403 quyền, 429 quota |
| `network_error` | Không hoàn tất request | Kiểm tra kết nối và thử lại có chủ đích |
| `non_json_response` | Response không phải JSON | Kiểm tra nguồn/proxy hoặc thay đổi endpoint |
| `candidate_tables_need_manual_mapping` | Có bảng ứng viên, chưa chốt cột giá | Đối chiếu schema, đơn vị và định nghĩa price |
| `observations_received` | Có observations theo cấu trúc FRED | Xem chất lượng, số dòng và pagination |
| `metadata_received` | Có metadata series | Đối chiếu đơn vị/tần suất |
| `vintage_sample_received` | Nhận một mẫu ngày vintage | Chưa đồng nghĩa đã dựng được lịch sử point-in-time |

**Exit code 2 là chủ đích:** công cụ không tự ký duyệt Lab 00, kể cả khi nhận được dữ liệu. Kết quả `NOT_PASSED` yêu cầu người phát triển hoàn tất các mục kiểm chứng thủ công. Nó không đồng nghĩa mọi request đều thất bại; xem trạng thái từng probe.

### Tùy chọn — Tái hiện kiểm tra không có key

```bash
python scripts/audit_sources.py --public-probe --out runtime/public-probe.json
```

Chế độ này bỏ qua key tài khoản, chỉ gọi demo vàng và một request FRED không có key. Chạy để kiểm tra cách xử lý lỗi; không dùng chế độ này để lấy dataset thật. Không cần chạy nhiều lần.

## 5. Điều kiện chuyển bước

Đọc gate trong `docs/data-source-audit.md`. Có thể làm Lab 01 (khung code/môi trường) song song, nhưng chưa được coi nguồn vàng sẵn sàng cho collector production hoặc training.

Khi có báo cáo bằng key thật, việc tiếp theo là xác minh cột giá, đơn vị, độ phủ, lịch nguồn và quyền sử dụng; cập nhật contract; sau đó mới viết adapter dựa trên schema đã quan sát.

## 6. Giới hạn công cụ

- Audit một lần không xác nhận giờ cập nhật, độ trễ thường gặp hoặc revision dài hạn.
- Các khoảng ngày giữa observations chỉ là thống kê, không tự kết luận có missing session khi chưa biết calendar.
- Số liệu âm ở real yield được đếm, không tự loại vì không phải giá vàng.
- Không lưu response nguyên văn; giữ checksum, schema, chất lượng tổng hợp và metadata. Muốn sửa adapter theo payload chi tiết cần xem response cục bộ sau khi loại key và kiểm tra quyền lưu.
- Mẫu vintage chỉ có tối đa 5 ngày, chưa tải mọi bản revision.
- Kết quả account audit hiện tại chưa có response thành công; happy-path đang được kiểm bằng fixture tổng hợp.
- Runtime reports thuộc máy chạy và bị loại khỏi Git qua `.gitignore`.
