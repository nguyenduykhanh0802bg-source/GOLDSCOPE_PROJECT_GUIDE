# GoldScope — Hướng dẫn thiết kế và phát triển dự án cá nhân

> **Tên đầy đủ:** GoldScope — Gold Market Intelligence & Forecasting Platform  
> **Mục tiêu:** Xây dựng hệ thống Python thu thập dữ liệu, phân tích thị trường vàng và đánh giá khả năng dự báo bằng thực nghiệm có thể tái lập.  
> **Chủ dự án:** Nguyễn Duy Khánh  
> **Phiên bản tài liệu:** 1.0 — 30/09/2026  
> **Trạng thái:** Đã chọn bài toán; đang thiết kế. Chưa có mã nguồn ứng dụng, dữ liệu đã tải, mô hình đã huấn luyện hay kết quả benchmark được xác nhận trong tài liệu này.

Tài liệu này là bản hướng dẫn xuyên suốt để triển khai một dự án cá nhân có thể đưa vào CV. Những quyết định ghi “chốt” là cấu hình đề xuất cho lần triển khai đầu tiên; có thể thay đổi bằng một quyết định kiến trúc được ghi lại. Các mốc thời gian, ngân sách và chỉ tiêu kỹ thuật là mục tiêu lập kế hoạch, không phải kết quả đã đạt được.

## Mục lục

1. [Tầm nhìn và giá trị dự án](#s01)
2. [Phạm vi và các phiên bản](#s02)
3. [Định nghĩa chính xác bài toán dự báo](#s03)
4. [Công nghệ và lý do lựa chọn](#s04)
5. [Kiến trúc hệ thống](#s05)
6. [Nguồn dữ liệu và bước kiểm chứng](#s06)
7. [Quy tắc thời gian và chống rò rỉ dữ liệu](#s07)
8. [Thiết kế cơ sở dữ liệu và lưu trữ](#s08)
9. [Thiết kế pipeline thu thập và xử lý](#s09)
10. [Khám phá dữ liệu và tạo đặc trưng](#s10)
11. [Mô hình, khoảng dự báo và giải thích](#s11)
12. [Walk-forward và đánh giá mô hình](#s12)
13. [Backend và hợp đồng API](#s13)
14. [Dashboard và các luồng sử dụng](#s14)
15. [Cấu trúc repository và quy ước lập trình](#s15)
16. [Thiết lập môi trường phát triển](#s16)
17. [Lộ trình triển khai theo từng lab](#s17)
18. [Kiểm thử và tiêu chí nghiệm thu](#s18)
19. [Docker, CI/CD và triển khai](#s19)
20. [Vận hành, giám sát và huấn luyện lại](#s20)
21. [Bảo mật, quyền dữ liệu và chi phí](#s21)
22. [Các hướng phát triển mở rộng](#s22)
23. [Đưa dự án vào CV và trình bày phỏng vấn](#s23)
24. [Backlog và công việc bắt đầu ngay](#s24)
25. [Từ điển thuật ngữ và nhật ký quyết định](#s25)
26. [Tài liệu tham khảo chính thức](#s26)

<a id="s01"></a>
## 1. Tầm nhìn và giá trị dự án

### 1.1. Dự án giải quyết vấn đề gì?

Thông tin về giá vàng, lãi suất, đồng USD và tin tức nằm ở nhiều nguồn khác nhau. Người nghiên cứu cần một hệ thống gom dữ liệu, bảo toàn lịch sử, tạo dự báo và đối chiếu dự báo với kết quả thực tế.

GoldScope cần trả lời được:

- Giá vàng đã biến động như thế nào trong khoảng thời gian được chọn?
- Những dữ liệu nào thực sự có sẵn tại thời điểm đưa ra dự báo?
- Mô hình ước lượng mức thay đổi sau một số phiên dữ liệu là bao nhiêu?
- Khoảng dự báo rộng đến mức nào và trong quá khứ bao phủ kết quả thực tế ra sao?
- Mô hình có tốt hơn cách dự báo đơn giản “giá tương lai bằng giá hiện tại” không?
- Những nhóm dữ liệu nào giúp cải thiện kết quả, nhóm nào chỉ làm hệ thống phức tạp thêm?

Đầu ra phục vụ nghiên cứu và học kỹ thuật. Phiên bản đầu không đặt lệnh giao dịch, không quản lý tiền, không phát tín hiệu mua/bán cá nhân hóa.

### 1.2. Giá trị đối với CV

| Nhóm năng lực | Bằng chứng cần tạo ra |
|---|---|
| Python backend | API có validation, migration, xử lý lỗi và test tích hợp |
| Data engineering | Collector chạy lặp an toàn, snapshot dữ liệu, theo dõi chất lượng |
| Machine learning | Baseline, mô hình ứng viên, thực nghiệm theo thời gian |
| Time series | Kiểm soát thời điểm công bố và nhãn dự báo nhiều phiên |
| Software engineering | Module rõ trách nhiệm, cấu hình riêng, dependency được khóa |
| Vận hành | Docker, CI, backup, log, phục hồi lỗi |
| Tư duy nghiên cứu | Báo cáo cả kết quả tốt, kém và giới hạn dữ liệu |

Một kết quả ML không vượt baseline vẫn có giá trị nếu phép đánh giá đúng và hệ thống hoạt động tốt. Không thay đổi tập test hoặc lựa chọn biểu đồ chỉ để làm kết quả trông đẹp hơn.

### 1.3. Nguyên tắc triển khai

1. Hoàn thiện một luồng nhỏ từ dữ liệu đến dự báo trước khi tăng số công nghệ.
2. Mọi dự báo phải truy được về model, bộ đặc trưng, dữ liệu và thời điểm phát hành.
3. Dữ liệu không đủ hoặc quá cũ phải được thể hiện thành trạng thái cụ thể.
4. Giữ một mã nguồn nghiệp vụ dùng chung giữa backtest và dự báo thật.
5. Đánh giá cải tiến bằng số liệu trên các giai đoạn chưa dùng để huấn luyện.

<a id="s02"></a>
## 2. Phạm vi và các phiên bản

### 2.1. Các quyết định chốt cho lần triển khai đầu

| Hạng mục | Quyết định |
|---|---|
| Tài sản | Một chuỗi giá vàng quốc tế, đơn vị USD/troy ounce sau khi xác minh metadata |
| Định danh nội bộ | `GOLD_USD`; provider và loại giá lưu riêng |
| Tần suất | Dữ liệu ngày; không làm intraday |
| Điểm giá | Giá tham chiếu ngày của nhà cung cấp; chỉ gọi “close” khi nguồn xác nhận |
| Bài toán đầu | Dự báo lợi suất đơn sau 1 và 5 phiên dữ liệu hợp lệ |
| Bài toán tiếp | Sau 20 phiên; phân loại xu hướng và tin tức ở phiên bản mở rộng |
| Cách xây dựng | Một repository, một ứng dụng chia module; job chạy thành tiến trình riêng |
| Backend | FastAPI |
| Database | PostgreSQL |
| Dashboard | Streamlit + Plotly |
| Mô hình | Zero-return baseline, Ridge, XGBoost |
| Tự động hóa đầu | Một scheduler bên ngoài API gọi CLI |
| Triển khai đầu | Docker Compose trên máy cá nhân, sau đó một máy chủ Linux |

**Lý do đổi mốc 1/7/30 ngày trong ý tưởng ban đầu:** 1/5/20 phiên dữ liệu gần với một ngày, một tuần và một tháng làm việc, nhưng vẫn là các khái niệm khác nhau. API sẽ dùng `horizon_sessions`, không ghi “7 ngày” khi thực chất đếm 7 dòng dữ liệu. Nếu sau này muốn đúng 7 hoặc 30 ngày lịch, tạo target và phép đánh giá riêng.

### 2.2. Phân chia phiên bản

| Phiên bản | Phạm vi bắt buộc | Điều kiện hoàn thành |
|---|---|---|
| v0.1 — Research baseline | Giá vàng, snapshot, EDA, baseline, Ridge, backtest 1/5 phiên | Chạy lại được báo cáo từ một snapshot cố định |
| v0.2 — MVP ứng dụng | PostgreSQL, XGBoost, khoảng dự báo, FastAPI, Streamlit, Docker, CI | Demo được toàn bộ luồng; đọc được lịch sử dự báo và sai số |
| v0.3 — Dữ liệu đa biến | Tối thiểu 3 chuỗi macro có chính sách thời gian hợp lệ, so sánh có/không macro | Chứng minh pipeline không dùng dữ liệu chưa công bố |
| v0.4 — Tin tức | Thu thập tin, chống trùng, relevance, sentiment, đo đóng góp | Báo cáo có/không tin trên cùng giai đoạn đánh giá |
| v1.0 — Portfolio release | Tự động cập nhật, theo dõi model, backup, demo, tài liệu đầy đủ | Nghiệm thu kỹ thuật và công bố rõ giới hạn nghiên cứu |

v0.2 vẫn có thể hoàn thành khi macro hoặc tin tức chưa đủ lịch sử. Không tạo dữ liệu macro/tin giả để làm đầy pipeline chạy thật.

### 2.3. Chưa làm ở MVP

- Dự báo vàng SJC/DOJI hoặc tự quy đổi thành giá mua bán vàng tại Việt Nam.
- Dự báo nhiều cổ phiếu, futures hay tiền mã hóa cùng lúc.
- LSTM, Transformer, agent, RAG và LLM giải thích tự động.
- Microservices, Kubernetes, Kafka, RabbitMQ, Redis nếu chưa có nhu cầu đo được.
- Tài khoản người dùng, phân quyền nhiều tổ chức và thanh toán.

Các mục này có đường mở rộng tại phần 22. Việc chưa triển khai là chủ động giới hạn phạm vi, không phải thiếu sót của MVP.

<a id="s03"></a>
## 3. Định nghĩa chính xác bài toán dự báo

### 3.1. Đơn vị thời gian

- `t`: vị trí của một quan sát ngày hợp lệ trong chuỗi của nguồn đã chọn.
- `P_t`: giá tham chiếu tại quan sát đó, đã có sẵn khi phát hành dự báo.
- `h`: số quan sát tương lai; khởi đầu bằng 1 và 5.
- `as_of`: mốc đóng dữ liệu dùng cho dự báo, lưu UTC.
- `issued_at`: thời điểm hệ thống thực sự lưu/phát hành dự báo.
- `origin_observation_date`: ngày của `P_t`.
- `target_observation_date`: ngày đích theo lịch nguồn; có thể để trống khi lịch chưa được xác minh, rồi xác định bằng quan sát hợp lệ thứ h.

Vàng giao ngay không có một phiên giao dịch tập trung duy nhất giống mọi sở giao dịch chứng khoán. Trong tài liệu, “phiên dữ liệu” là quy ước của chuỗi đã chọn. Không tự thêm cuối tuần, xóa cuối tuần hoặc áp lịch NYSE cho dữ liệu vàng mà chưa kiểm tra.

### 3.2. Target của mô hình

Lợi suất đơn:

```text
target_return_h(t) = P_(t+h) / P_t - 1
predicted_price_h(t) = P_t × (1 + predicted_return_h(t))
```

Huấn luyện một model cho mỗi horizon trong phiên bản đầu. Không dự báo 1 phiên rồi lặp kết quả 20 lần để thay thế mô hình 20 phiên.

Baseline:

```text
predicted_return_h = 0
predicted_price_h = P_t
```

Đầu ra số dùng tỷ lệ thập phân: `0.01` nghĩa là `1%`. Schema/API phải ghi rõ quy ước này.

### 3.3. Ba loại đầu ra cần phân biệt

| Đầu ra | Ý nghĩa | Phiên bản |
|---|---|---|
| Point forecast | Một ước lượng trung tâm của lợi suất/giá | MVP |
| Prediction interval | Khoảng dự báo cho kết quả tương lai, có kiểm tra coverage | MVP |
| Direction probability | Xác suất cho các lớp tăng/đi ngang/giảm, cần model và calibration riêng | Mở rộng |

Không lấy accuracy trong quá khứ để ghi “độ tin cậy dự báo hôm nay”. Không gọi quantile 0.5 là kỳ vọng toán học; đó là trung vị ước lượng. Khi mô hình dùng squared loss, đặt tên `predicted_return`, tránh hứa hẹn đó là kỳ vọng được hiệu chuẩn hoàn hảo.

### 3.4. Hợp lệ khi phát hành

Dự báo mới chỉ được phát hành nếu origin còn đủ mới, target vẫn ở tương lai so với `issued_at`, dữ liệu qua kiểm tra chất lượng và artifact tương thích. Nếu job chạy muộn đến khi target đã xuất hiện, ghi là backfill nghiên cứu, không ghi thành dự báo live.

<a id="s04"></a>
## 4. Công nghệ và lý do lựa chọn

### 4.1. Stack chính

Các dòng phiên bản sau là lựa chọn khởi đầu; không phải tuyên bố “mới nhất”. Patch version chính xác phải được khóa sau khi cài và chạy kiểm thử tương thích.

| Thành phần | Lựa chọn | Vai trò |
|---|---|---|
| Ngôn ngữ | Python 3.12 | Một ngôn ngữ cho API, ETL và ML |
| Dependency | uv, `pyproject.toml`, `uv.lock` | Môi trường nhất quán giữa máy cá nhân và CI |
| API | FastAPI + Uvicorn | Endpoint, validation và OpenAPI |
| Schema/settings | Pydantic v2 + pydantic-settings | Kiểu dữ liệu và cấu hình từ môi trường |
| HTTP client | HTTPX | Timeout, gọi API nguồn, thuận tiện test bằng mock |
| ORM/migration | SQLAlchemy 2.x + Alembic + psycopg | Truy cập PostgreSQL và quản lý schema |
| Database | PostgreSQL 17 | Dữ liệu nghiệp vụ, trạng thái pipeline, phiên bản dự báo |
| Dữ liệu | Pandas + NumPy + PyArrow | Làm sạch, feature, snapshot Parquet |
| Mô hình nền | scikit-learn | Ridge, pipeline preprocessing, metrics |
| Mô hình cây | XGBoost bản stable tương thích đã khóa | Ứng viên phi tuyến và quantile regression |
| Giao diện | Streamlit + Plotly | Dashboard nhanh, biểu đồ tương tác |
| CLI | Typer | Collector, backtest, training, daily pipeline |
| Test | pytest + pytest-cov + respx | Unit, integration, mock HTTP |
| Chất lượng code | Ruff + mypy | Format, lint và type checking |
| Đóng gói | Docker + Docker Compose | API, dashboard, database, job từ cùng source |
| CI/CD | GitHub Actions | Test, build image, deployment workflow |

`uv` quản lý dependency và lockfile theo dự án [R04]. Chọn một công cụ dependency chính, tránh duy trì cả Poetry, requirements thủ công và uv cùng lúc.

### 4.2. Công nghệ thêm khi có nhu cầu

| Công nghệ | Chỉ thêm khi | Giá trị cần chứng minh |
|---|---|---|
| SHAP | XGBoost và backtest đã ổn | Giải thích hành vi model |
| MLflow | Nhiều thí nghiệm khó tra cứu bằng manifest | Tracking và registry dễ sử dụng |
| Celery + Redis | Job dài, cần queue/retry và nhiều worker | Quản lý tác vụ bền vững hơn |
| Prometheus + Grafana | Có dịch vụ chạy lâu dài | Quan sát lỗi, độ trễ và freshness |
| Object storage tương thích S3 | Artifact vượt khả năng quản lý bằng volume | Backup và chia sẻ giữa môi trường |
| PyTorch | Có giả thuyết ML rõ ràng và dữ liệu phù hợp | So sánh mô hình sâu với baseline |

Nếu chỉ chạy một pipeline mỗi ngày, PostgreSQL + CLI + scheduler ngoài API là đủ cho bản đầu. Streamlit gọi API; không được train model khi người dùng tải lại trang [R05].

<a id="s05"></a>
## 5. Kiến trúc hệ thống

### 5.1. Cách tổ chức

Ứng dụng là **modular monolith**: cùng repository và cùng bộ module, nhưng có các tiến trình riêng cho API, dashboard và batch job. Chưa tách thành nhiều dịch vụ có database riêng.

```mermaid
flowchart TD
    A["API dữ liệu bên ngoài"] --> B["Collector và kiểm tra dữ liệu"]
    B --> C["Raw snapshot"]
    B --> D["PostgreSQL"]
    C --> E["Dataset và feature theo thời điểm"]
    D --> E
    E --> F["Backtest và huấn luyện"]
    F --> G["Model registry và artifacts"]
    E --> H["Batch dự báo"]
    G --> H
    H --> D
    D --> I["FastAPI"]
    I --> J["Streamlit dashboard"]
```

### 5.2. Ranh giới trách nhiệm

| Module | Chịu trách nhiệm | Không đặt ở module này |
|---|---|---|
| `collectors` | Gọi nguồn, nhận raw payload và metadata | Tính feature hoặc train |
| `data` | Chuẩn hóa, kiểm tra, chọn phiên bản theo thời điểm | HTTP response của API |
| `features` | Feature và target với hợp đồng thời gian | Tự tải dữ liệu ngoài |
| `ml` | Baseline, train, evaluate, predict | UI và cron |
| `db` | Table, repository, transaction | Thuật toán ML |
| `services` | Điều phối nghiệp vụ, dùng các module | Render biểu đồ |
| `api` | Xác thực tham số, gọi service, serialize | Training trong request |
| `jobs` | Điểm vào các tác vụ batch | Lặp lại logic feature |

### 5.3. Các luồng chính

**Luồng nghiên cứu:** chọn snapshot → dựng dataset tại từng thời điểm → chia fold → train/validate → lưu báo cáo → chọn model.

**Luồng hằng ngày:** collector → raw → validation → transaction chuẩn hóa → feature hiện tại → model đang hoạt động → forecast → đối chiếu forecast cũ đã đến hạn.

**Luồng xem dữ liệu:** dashboard → API đọc dữ liệu đã lưu. API không tự gọi nhà cung cấp theo từng lượt tải trang, giúp kiểm soát quota và khả năng tái lập.

<a id="s06"></a>
## 6. Nguồn dữ liệu và bước kiểm chứng

### 6.1. Giá vàng

Nguồn ứng viên đầu tiên là Alpha Vantage. Tài liệu chính thức có endpoint `GOLD_SILVER_HISTORY`, hỗ trợ `GOLD`/`XAU` và các khoảng `daily`, `weekly`, `monthly` [R01].

Tham số dự kiến:

```text
GET https://www.alphavantage.co/query
function=GOLD_SILVER_HISTORY
symbol=GOLD
interval=daily
apikey=<đọc từ biến môi trường>
```

Điều này xác nhận endpoint được mô tả, **chưa xác nhận tài khoản của dự án có quyền lấy đầy đủ lịch sử**. Không mặc định có OHLCV, một số năm lịch sử cố định hoặc truy cập miễn phí không giới hạn. Adapter sẽ dựa trên response thực tế đã kiểm tra, không dựa trên schema tưởng tượng.

### 6.2. Macro từ FRED

| Series ID | Nội dung | Tần suất quan sát | Ưu tiên |
|---|---|---|---|
| `DGS10` | Lợi suất trái phiếu kho bạc Mỹ kỳ hạn 10 năm | Ngày | Cao |
| `DFII10` | Lợi suất trái phiếu kho bạc Mỹ 10 năm điều chỉnh lạm phát | Ngày | Cao |
| `DTWEXBGS` | Chỉ số USD danh nghĩa diện rộng | Ngày | Cao |
| `DFF` | Lãi suất federal funds hiệu lực | Ngày | Sau 3 chuỗi đầu |
| `CPIAUCSL` | Chỉ số giá tiêu dùng toàn phần, đã điều chỉnh mùa vụ | Tháng | Sau khi xử lý vintage |
| `DCOILWTICO` | Giá dầu WTI tại Cushing | Ngày | Thử nghiệm thêm |

Metadata từng series phải được lưu; xem [R07]–[R12]. `DTWEXBGS` không được đổi nhãn thành chỉ số ICE DXY. `CPIAUCSL` là mức chỉ số CPI; muốn lạm phát theo năm phải tính biến đổi trên dữ liệu hợp lệ tại thời điểm đó. Tần suất quan sát ngày không có nghĩa số liệu được công bố cùng ngày.

FRED có cơ chế real-time period và vintage để truy hồi phiên bản theo thời gian [R02][R03]. Tuy vậy, cần kiểm tra từng series; metadata theo ngày không tự giải quyết được thời điểm công bố trong ngày.

### 6.3. Tin tức

Tin tức triển khai ở v0.4. Có thể khảo sát `NEWS_SENTIMENT` của Alpha Vantage [R01], sau đó đánh giá độ phủ và quyền dùng. Chỉ lưu những trường được phép: nguồn, URL, tiêu đề, thời gian, tóm tắt/điểm số nếu quyền truy cập cho phép.

Không mặc định “tin tích cực” tương đương “giá vàng tăng”. Sentiment của văn bản, chủ đề tin và tác động kỳ vọng đối với vàng là các khái niệm khác nhau. Hiệu quả dự báo phải được đo riêng.

### 6.4. Lab kiểm chứng nguồn — bắt buộc trước thiết kế collector hoàn chỉnh

Tạo `docs/data-source-audit.md`, ghi kết quả thực tế cho từng nguồn:

| Cần kiểm tra | Bằng chứng phải lưu |
|---|---|
| Quyền truy cập | Tài khoản/gói được phép gọi endpoint; không ghi secret |
| Schema | Payload mẫu đã bỏ thông tin nhạy cảm |
| Độ phủ | Ngày đầu/cuối, số dòng, khoảng trống |
| Ý nghĩa giá | Spot/reference/close, tiền tệ, đơn vị, múi giờ |
| Cập nhật | Thời điểm thường có dữ liệu, độ trễ quan sát thực tế |
| Giới hạn | Quota, giới hạn lịch sử, pagination, hành vi lỗi |
| Revision | Dữ liệu cũ có đổi không, có vintage hay không |
| Quyền lưu/chia sẻ | Những gì được giữ nội bộ và được đưa lên repo/demo |

**Gate dữ liệu:** mục tiêu có ít nhất 5 năm giá ngày; 8–10 năm là mong muốn để thử nhiều giai đoạn thị trường. Đây là yêu cầu dự án, không phải lời hứa của nguồn. Nếu chỉ có ít dữ liệu, giảm phạm vi thí nghiệm và ghi rõ độ yếu của kết luận.

Nếu nguồn chính không đáp ứng, chọn một nguồn khác hoặc CSV có nguồn gốc và quyền sử dụng rõ ràng, qua cùng audit. Chưa coi phương án dự phòng là đã sẵn sàng. ETF/futures chỉ được dùng như bài toán khác với định danh khác, không nối vào chuỗi spot.

<a id="s07"></a>
## 7. Quy tắc thời gian và chống rò rỉ dữ liệu

### 7.1. Các timestamp bắt buộc

| Trường | Ý nghĩa |
|---|---|
| `observation_date` | Kỳ/ngày mà số liệu mô tả |
| `source_published_at` | Thời điểm nguồn công bố, nếu xác minh được |
| `available_at` | Mốc sớm nhất dữ liệu được phép tham gia forecast theo chính sách dự án |
| `ingested_at` | Thời điểm hệ thống tải dữ liệu |
| `vintage_date` | Ngày phiên bản có hiệu lực, nếu nguồn hỗ trợ |
| `availability_basis` | `verified`, `conservative_proxy` hoặc `first_seen` |

Ví dụ: CPI của tháng 1 công bố giữa tháng 2 thì không được xuất hiện trong feature đầu tháng 2. Dữ liệu macro tải hôm nay đã được sửa lại có thể khác số liệu mà người dùng biết tại một ngày trong quá khứ.

### 7.2. Hai chế độ dữ liệu

**Live:** chỉ dùng bản ghi đã được hệ thống thu nhận trước `as_of`; `available_at` không sớm hơn thời điểm thực sự có thể dùng. Nếu không biết thời điểm nguồn công bố, dùng `first_seen`.

**Historical backtest:** có thể dùng dữ liệu tải sau này nếu truy hồi được phiên bản từng tồn tại và chứng minh thời điểm công bố. `ingested_at` hiện tại không cần nhỏ hơn mốc backtest, nhưng `available_at` lịch sử phải có cơ sở.

Nếu chỉ có ngày vintage, dùng chính sách bảo thủ: đưa dữ liệu vào mốc forecast kế tiếp sau khi ngày vintage đã kết thúc tại múi giờ nguồn xác minh. Lưu là proxy và thử thêm các độ trễ. Không mô tả kết quả đó là tái hiện chính xác từng phút lịch sử.

Nếu không tái dựng được lịch sử công bố, cho macro vào dashboard trước; hoãn đưa vào backtest nghiêm ngặt. Nguyên tắc này cũng áp dụng cho dữ liệu giá có revision.

### 7.3. Ghép dữ liệu theo thời điểm

Ở mỗi origin:

1. Chỉ xét phiên bản có `available_at <= as_of`.
2. Chọn phiên bản hợp lệ mới nhất cho từng observation.
3. Chọn observation mới nhất đã công bố của mỗi series.
4. Tính feature từ tập dữ liệu mà origin đó được phép biết.
5. Lưu lineage tới snapshot, vintage và chính sách availability.

Có thể dùng as-of join, nhưng phải xử lý vintage trước khi join; ghép gần nhất theo ngày quan sát là chưa đủ. Forward fill chỉ được thực hiện sau khi số liệu đã có sẵn. Không backward fill từ tương lai.

### 7.4. Quy tắc nhãn nhiều phiên

Với target 5 phiên, nhãn tại `t` cần giá `t+5`. Mẫu đó chỉ được huấn luyện nếu nhãn đã có trước lúc model được fit. Tách train/test theo origin thôi chưa đủ.

Điều kiện bắt buộc:

```text
label_available_at của mọi mẫu train <= model_fit_cutoff
feature_available_at của mọi mẫu <= forecast_as_of tương ứng
```

`TimeSeriesSplit` có tham số `gap` [R06]. Dự án có thể dùng `gap >= h` như lớp bảo vệ ban đầu cho dữ liệu đều theo phiên, nhưng vẫn phải kiểm tra timestamp nhãn; độ trễ công bố có thể yêu cầu khoảng cách lớn hơn.

### 7.5. Những lỗi phải ngăn bằng test

- Fit scaler/imputer trên cả dataset rồi mới chia fold.
- Chọn feature hoặc tham số bằng tập test cuối.
- Dùng rolling window có tâm hoặc `shift(-h)` làm feature.
- Điền giá mất bằng giá tương lai; tạo nhãn giả cho ngày mất dữ liệu.
- Ghép macro theo observation date mà bỏ qua release/vintage.
- Gộp tin được công bố sau cutoff vào feature cùng ngày.
- Đổi dữ liệu lịch sử nhưng không đổi snapshot và mã dataset.
- Dùng model train hôm nay để tính dự báo quá khứ rồi gọi đó là walk-forward.

Pipeline preprocessing phải được fit riêng trong từng fold [R13].

<a id="s08"></a>
## 8. Thiết kế cơ sở dữ liệu và lưu trữ

### 8.1. Ba lớp dữ liệu

| Lớp | Nội dung | Nơi lưu ban đầu |
|---|---|---|
| Raw | Payload gốc, metadata request đã bỏ key, checksum | File JSON nén trong volume |
| Normalized | Quan sát, phiên bản, trạng thái và metadata | PostgreSQL |
| Research artifacts | Snapshot Parquet, model, metrics, dự báo từng fold | Volume riêng, manifest trong PostgreSQL |

Raw và model lớn không đưa vào Git. Repo chỉ chứa fixture nhỏ được phép chia sẻ hoặc dữ liệu tổng hợp đánh dấu `synthetic` để test.

### 8.2. Các bảng chính

| Bảng | Trường chính dự kiến | Ràng buộc đáng chú ý |
|---|---|---|
| `data_sources` | id, name, endpoint_key, unit, timezone, license_note, availability_policy | Một cấu hình xác định rõ một loại nguồn |
| `ingestion_runs` | id, source_id, started_at, ended_at, status, rows_received, rows_rejected, error_code | Mỗi lần chạy có run ID |
| `raw_objects` | id, run_id, object_path, sha256, fetched_at, schema_version | Lưu lại payload đã dùng |
| `market_observations` | id, asset, source_id, observation_date, price, currency, unit, available_at, ingested_at, revision_key, raw_object_id | Unique theo nguồn + tài sản + ngày + revision |
| `macro_observations` | id, series_id, observation_date, value, vintage_date, available_at, availability_basis, revision_key, raw_object_id | Unique theo series + kỳ + revision |
| `dataset_snapshots` | id, manifest_path, sha256, data_start, data_end, created_at, time_policy_version | Dataset đã tạo không sửa trực tiếp |
| `feature_snapshots` | id, dataset_id, feature_version, schema_hash, parquet_path, row_count | Phân biệt dataset nguồn và bộ feature |
| `model_versions` | id, family, horizon_sessions, feature_snapshot_id, trained_at, fit_cutoff, artifact_path, git_sha, metrics_path, status | Model chứa đủ metadata tái lập |
| `predictions` | id, model_id, feature_snapshot_id, origin_date, as_of, issued_at, horizon_sessions, point_return, lower_return, upper_return, interval_level, mode | Unique theo model + origin + horizon + snapshot + mode |
| `prediction_outcomes` | prediction_id, target_date, actual_price, actual_return, observation_revision_id, scored_at, score_revision | Kết quả có revision; không ghi đè prediction |
| `model_deployments` | id, horizon_sessions, model_id, activated_at, retired_at | Tối đa một model active trên mỗi horizon |
| `data_quality_events` | id, run_id, rule_code, severity, count, details, created_at | Phân biệt cảnh báo và lỗi chặn |
| `news_articles` | id, canonical_url, title_hash, published_at, first_seen_at, source_id, cluster_id | v0.4; chống trùng nhưng không mất nguồn |
| `news_signals` | article_id, model_version, relevance, sentiment, computed_at | v0.4; thay NLP model tạo phiên bản mới |

Thiết kế khóa, index và kiểu dữ liệu chi tiết được hiện thực ở migration. Với revision chưa có ID từ nguồn, dùng khóa/hash nội dung đã chuẩn hóa. Không dùng timestamp ingestion để biến mọi lần tải lại thành một revision mới.

### 8.3. Quy tắc lưu trữ

- PostgreSQL dùng `TIMESTAMPTZ` cho thời điểm; API trả ISO 8601 UTC.
- Giá thô dùng `NUMERIC`; NumPy/ML chuyển sang float trong pipeline.
- Có index theo `asset, observation_date`, `series_id, available_at`, `model_id, as_of`.
- Upsert dữ liệu trùng hệt phải giữ nguyên số quan sát chuẩn hóa; payload mới vẫn có thể có log ingestion riêng.
- Dự báo đã phát hành không bị sửa để khớp thực tế. Đổi model hoặc dữ liệu tạo bản ghi mới.
- Foreign key từ prediction tới model/snapshot không cho xóa vô tình lịch sử.

<a id="s09"></a>
## 9. Thiết kế pipeline thu thập và xử lý

### 9.1. Quy trình hằng ngày

1. Lấy khóa job để tránh hai tiến trình xử lý cùng nguồn/cửa sổ.
2. Ghi `ingestion_run` trạng thái `running`.
3. Gọi nguồn với timeout, kiểm tra HTTP và cả thông báo lỗi trong body.
4. Lưu raw payload và checksum.
5. Chuẩn hóa kiểu dữ liệu; đưa bản ghi lỗi vào quarantine.
6. Kiểm tra chất lượng và độ mới.
7. Ghi observations trong transaction; bảo toàn revision.
8. Tạo feature theo model contract.
9. Nếu origin hợp lệ, tạo prediction bằng model active.
10. Chấm điểm những prediction cũ có nhãn đã xuất hiện.
11. Ghi thống kê, kết thúc run và giải phóng khóa.

Job có các trạng thái `success`, `partial`, `failed`, `skipped`. Ngày không có quan sát mới có thể là `skipped`, không mặc định là lỗi.

### 9.2. Chính sách lỗi

| Tình huống | Xử lý |
|---|---|
| HTTP 429 | Tôn trọng `Retry-After`; retry giới hạn, không gọi dồn |
| Timeout/5xx | Retry có backoff và jitter, ví dụ tối đa 3 lần |
| 401/403 | Dừng, kiểm tra key/quyền truy cập; không retry vô hạn |
| HTTP 200 nhưng body báo quota/lỗi | Đánh dấu lỗi nguồn, không đưa vào bảng dữ liệu |
| Schema thay đổi | Lưu raw, chặn normalize, báo lỗi rõ |
| Thiếu giá origin | Không phát hành forecast mới |
| Macro quá cũ | Giữ metadata tuổi dữ liệu; không chuyển sang model khác ngầm |
| Model thiếu/hỏng | Báo unavailable; chỉ dùng baseline nếu có bản baseline đã đăng ký |
| Database tạm mất | Retry theo chính sách; không đánh dấu run thành công |

Tác vụ được thiết kế idempotent: chạy lại cùng đầu vào không tạo dự báo hoặc quan sát nghiệp vụ trùng lặp. Sau này thêm queue vẫn phải giữ thuộc tính này; queue không tự bảo đảm đúng một lần thực thi [R16].

### 9.3. Kiểm tra chất lượng

- Giá phải là số hữu hạn và dương; ngày và đơn vị phải hợp lệ.
- Không có duplicate trên business key.
- Phân biệt nghỉ theo lịch nguồn với dữ liệu bị mất.
- Giá biến động lớn tạo cảnh báo; không tự xóa biến động thật vì “outlier”.
- Khi có OHLC đã xác minh, kiểm tra `low <= open/close <= high`; nếu chỉ có giá tham chiếu thì bỏ quy tắc này.
- FRED trả giá trị thiếu phải được chuẩn hóa thành null, không thành 0.
- Đặt freshness riêng từng nguồn; dữ liệu tháng không dùng ngưỡng freshness của dữ liệu ngày.

### 9.4. Tái lập và lineage

Mỗi experiment có manifest chứa: dataset hash, raw IDs, source policy, feature version, training window, random seed, library versions, git SHA, tham số model, metrics và artifact hashes. Một báo cáo không có thông tin này chưa đủ điều kiện dùng làm kết quả chính trong CV.

<a id="s10"></a>
## 10. Khám phá dữ liệu và tạo đặc trưng

### 10.1. EDA cần thực hiện

- Thống kê thời gian bao phủ, số mẫu, gap, duplicate và revision.
- Vẽ giá theo thời gian và phân phối lợi suất; đánh dấu các đoạn thiếu.
- Đo độ biến động trượt, autocorrelation và mức mất cân bằng lớp nếu có classification.
- Kiểm tra tương quan giữa các feature để phát hiện trùng lặp.
- Kiểm tra thời điểm nguồn thực sự sẵn sàng, không chỉ tính missing rate.

EDA phục vụ lựa chọn model chỉ được dùng trên phần development. Tập test cuối chỉ mở khi thiết kế đã được chốt. EDA toàn chuỗi cho vận hành phải được phân biệt với EDA dùng để chọn feature.

### 10.2. Feature ban đầu

| Nhóm | Feature đề xuất | Điều kiện |
|---|---|---|
| Lợi suất | 1, 5, 20 phiên gần nhất | Dùng giá đã biết ở origin |
| Lag | Lợi suất trễ 1, 2, 5 phiên | Không trộn với target tương lai |
| Xu hướng | `P_t / MA_5 - 1`, `P_t / MA_20 - 1` | Rolling chỉ kết thúc ở t |
| Biến động | Std lợi suất 5, 20, 60 phiên | Ghi rõ `min_periods`, công thức và số mẫu |
| Động lượng | RSI 14, MACD chuẩn hóa theo giá | Thêm sau bộ cơ bản, kiểm chứng giá trị |
| Macro | Mức/delta yield, return chỉ số USD, tuổi số liệu | As-of/vintage hợp lệ |
| Tin tức | Số tin, relevance, sentiment, độ phân tán | Có timestamp và cửa sổ trước cutoff |

Tránh bắt đầu bằng hàng trăm chỉ báo. Mỗi feature phải có tên, kiểu, công thức, cửa sổ, đơn vị, chính sách missing và thời điểm sẵn sàng.

### 10.3. Minh họa feature/target

Đoạn dưới minh họa công thức, chưa phải pipeline hoàn chỉnh:

```python
# Điều kiện: một chuỗi giá đã kiểm tra lịch nguồn, sắp xếp tăng dần,
# mỗi dòng là một quan sát hợp lệ và không có gap chưa giải quyết.
price = df["price"]
df["return_1"] = price.pct_change(fill_method=None)
df["return_5"] = price.pct_change(periods=5, fill_method=None)
df["return_1_lag_1"] = df["return_1"].shift(1)
df["relative_ma_20"] = price / price.rolling(20, min_periods=20).mean() - 1
df["volatility_20"] = df["return_1"].rolling(20, min_periods=20).std()
df["target_return_5"] = price.shift(-5) / price - 1
```

`target_return_5` chỉ là nhãn. Cuối chuỗi chưa có target vẫn phải giữ để suy luận; không `dropna()` toàn bảng khiến mất chính những ngày cần forecast. Tách hàm tạo feature và hàm tạo target.

Nếu dự báo phát hành sau khi `P_t` đã sẵn sàng, feature dùng `P_t` là hợp lệ. Nếu chuyển sang dự báo trước khi giá đó công bố, phải dịch cửa sổ tương ứng. Không áp dụng `.shift(1)` máy móc để thay thế định nghĩa cutoff.

<a id="s11"></a>
## 11. Mô hình, khoảng dự báo và giải thích

### 11.1. Thứ tự triển khai

| Bước | Mô hình | Mục đích |
|---|---|---|
| 1 | Zero-return / last-price baseline | Mốc so sánh bắt buộc |
| 2 | Ridge regression | Kiểm tra tín hiệu tuyến tính và preprocessing |
| 3 | XGBoost regression | Thử quan hệ phi tuyến với độ phức tạp kiểm soát |
| 4 | Quantile models | Tạo khoảng dự báo |
| 5 | Random Forest, LightGBM hoặc mô hình thống kê | Chỉ thêm để kiểm tra một giả thuyết cụ thể |
| 6 | LSTM/GRU/Transformer | Nhánh nghiên cứu sau MVP |

Không cần triển khai tất cả trước khi demo. Với XGBoost, bắt đầu bằng một tập thử nhỏ trên `max_depth`, `learning_rate`, số cây, subsampling và regularization. Ghi số cấu hình đã thử; giới hạn khoảng 10–20 cấu hình đầu để tránh tìm kiếm vô hạn và quá khớp validation.

### 11.2. Khoảng dự báo

Chọn mức danh nghĩa 80% cho lần đầu:

- Model quantile thấp: q10.
- Model trung vị tùy chọn: q50.
- Model quantile cao: q90.
- Khoảng giá: biến đổi hai đầu mút bằng `P_t × (1 + return_quantile)`.

XGBoost có objective quantile trong tài liệu tham số [R14]. Kiểm tra hỗ trợ ở phiên bản đã khóa. Nếu gặp quantile crossing, ghi tần suất và áp dụng chính sách sắp lại đầu mút có version; đánh giá coverage sau xử lý.

“Khoảng 80%” là mục tiêu danh nghĩa, không phải đảm bảo từng dự báo có xác suất đúng 80%. Báo cáo coverage thực nghiệm và độ rộng trên các giai đoạn chưa train. Calibration dùng cửa sổ quá khứ riêng. Nếu thử conformal cho chuỗi thời gian, phải nêu rõ giả định phụ thuộc thời gian và nguy cơ mất hiệu chuẩn khi thị trường đổi chế độ.

### 11.3. Classification ở phiên bản sau

Tạo ba lớp theo lợi suất và ngưỡng `epsilon_h`:

```text
UP       : return_h > epsilon_h
SIDEWAYS : -epsilon_h <= return_h <= epsilon_h
DOWN     : return_h < -epsilon_h
```

Ngưỡng phải cố định trước đánh giá hoặc được fit từ training window; không chọn bằng kết quả test. Báo cáo balanced accuracy, macro-F1, log loss và calibration. Không suy xác suất tăng/giảm từ dấu của point forecast.

### 11.4. Giải thích bằng SHAP

Sau khi pipeline ổn, lưu các feature ảnh hưởng lớn tới prediction. SHAP giải thích cách model phân bổ đóng góp, không chứng minh tác động nhân quả của USD/lãi suất lên vàng [R15]. Feature tương quan có thể chia sẻ hoặc làm thay đổi cách phân bổ.

Trên dashboard ghi “Đóng góp theo mô hình”. Nếu model dự báo lợi suất, đóng góp cũng ở đơn vị output đó; không tự biến thành mức USD làm thay đổi giá mà thiếu phép biến đổi rõ ràng.

<a id="s12"></a>
## 12. Walk-forward và đánh giá mô hình

### 12.1. Chốt giao thức trước khi thử model

Lập `configs/backtest.yaml`, ghi thời gian development, holdout cuối, forecast cutoff, lịch retrain, horizons và metrics. Mốc tuyệt đối chỉ chốt sau khi biết độ phủ dữ liệu.

Đề xuất nếu có ít nhất 5 năm dữ liệu:

1. Giữ 12 tháng cuối làm final holdout, không dùng để chọn feature/tham số.
2. Phần trước đó là development; cần tối thiểu khoảng 2 năm cho cửa sổ train đầu.
3. Tạo các khối validation nối tiếp, ví dụ 3 tháng/khối, expanding window.
4. Bên trong mỗi khối, mô phỏng retrain hàng tháng và phát hành forecast theo ngày.
5. Chỉ train trên mẫu có nhãn đã sẵn sàng tại từng lần fit.
6. Sau khi chọn cấu hình, chạy final holdout theo đúng lịch đã chốt.

Nếu dữ liệu ngắn hơn, thu nhỏ số fold hoặc phạm vi; không chia ngẫu nhiên để tăng điểm. Fold được tính theo lịch phiên nguồn, nên độ dài ngày lịch có thể khác nhau.

### 12.2. Ba cửa sổ có mục đích khác nhau

| Phần dữ liệu | Được phép dùng để |
|---|---|
| Train | Fit model và các transform |
| Validation/calibration trong development | Chọn cấu hình, early stopping, hiệu chuẩn khoảng/xác suất |
| Final holdout | Đánh giá cuối cùng cấu hình đã chốt |

Nếu đọc kết quả holdout rồi sửa model theo nó, holdout đó trở thành dữ liệu development cho lần tiếp theo. Phải ghi lại việc này và cần một giai đoạn tương lai mới để đánh giá độc lập.

### 12.3. Metrics bắt buộc

| Metric | Dùng cho | Cách diễn giải |
|---|---|---|
| MAE lợi suất | Chỉ tiêu chính của point forecast | Sai số tuyệt đối trung bình; báo theo điểm phần trăm hoặc bps |
| RMSE lợi suất | Nhạy với sai số lớn | So sánh cùng horizon và cùng origin |
| MAE giá | Khả năng hiểu bằng USD/ounce | Chỉ tiêu phụ, chịu ảnh hưởng mức giá |
| Baseline skill | `1 - MAE_model / MAE_baseline` | >0 tốt hơn baseline; nếu mẫu số 0, báo không xác định |
| Direction accuracy | Đúng dấu tăng/giảm | Ghi rõ cách xử lý lợi suất bằng 0 và tỷ lệ mẫu được tính |
| Pinball loss | Quantile forecast | Đánh giá từng quantile |
| Empirical coverage | Khoảng dự báo | Tỷ lệ kết quả thực nằm trong khoảng |
| Mean interval width | Độ hữu ích của khoảng | Khoảng quá rộng có thể coverage tốt nhưng ít giá trị |

Baseline lợi suất bằng 0 không phải một classifier có hướng tăng/giảm. Khi so sánh direction accuracy, bổ sung baseline hướng như lớp phổ biến trên train và công bố tỷ lệ lớp. Không tuyên bố model tốt chỉ vì accuracy vượt 50%.

Không lấy MAPE lợi suất làm metric chính vì mẫu số có thể gần 0. Với h=5/20, nhãn nhiều origin chồng lấn; khi ước lượng độ bất định của metrics cần dùng block bootstrap theo thời gian hoặc tập origin không chồng lấn. Không coi mọi hàng là mẫu độc lập.

### 12.4. Bảng thực nghiệm bắt buộc

| Experiment | Dữ liệu | Mô hình | Câu hỏi |
|---|---|---|---|
| E00 | Giá | Zero-return | Sai số khi không dự báo thay đổi là bao nhiêu? |
| E01 | Giá | Ridge | Feature cơ bản có tín hiệu tuyến tính không? |
| E02 | Giá | XGBoost | Phi tuyến có cải thiện ổn định không? |
| E03 | Giá + macro | Cấu hình ứng viên | Macro có cải thiện trên cùng origin không? |
| E04 | Giá + macro + tin | Cấu hình ứng viên | Tin có đóng góp ngoài giá và macro không? |
| E05 | Cùng dữ liệu | Quantile models | Khoảng dự báo có coverage/width hợp lý không? |

Khi bộ tin ngắn hơn lịch sử giá, E03 và E04 phải so trên phần thời gian giao nhau. Không so một model trên giai đoạn dễ với model khác trên giai đoạn biến động mạnh.

### 12.5. Quy tắc chọn model active

- Model phải qua kiểm tra schema, leakage, artifact và thời gian suy luận.
- Chỉ thay baseline/model hiện hành nếu cải thiện trên validation theo tiêu chí đã đăng ký trước, đủ ổn định qua nhiều khối và không làm khoảng dự báo xuống cấp rõ rệt.
- Ngưỡng cải thiện có thể đặt ban đầu là 2% MAE tương đối; đây là tiêu chí kỹ thuật thử nghiệm, không phải bằng chứng chắc chắn về ý nghĩa thống kê.
- Ghi cả độ biến thiên của chênh lệch metrics và số thí nghiệm đã thử.
- Nếu không có model tốt hơn, baseline vẫn là model active hợp lệ; XGBoost được hiển thị là model nghiên cứu.

**Forecast backtest không phải trading backtest.** Chỉ khi bổ sung quy tắc giao dịch, thời điểm khớp lệnh, spread, phí, slippage và thanh khoản mới đánh giá PnL. Không suy lợi nhuận trực tiếp từ MAE thấp.

<a id="s13"></a>
## 13. Backend và hợp đồng API

### 13.1. Endpoint MVP

| Method | Endpoint | Nội dung |
|---|---|---|
| GET | `/health/live` | Tiến trình còn hoạt động |
| GET | `/health/ready` | Database và cấu hình phục vụ đã sẵn sàng |
| GET | `/api/v1/market/latest` | Giá tham chiếu mới nhất, source, freshness |
| GET | `/api/v1/market/history` | Lịch sử theo asset, from, to và giới hạn số dòng |
| GET | `/api/v1/forecasts/latest` | Forecast mới nhất theo horizon |
| GET | `/api/v1/forecasts/history` | Các forecast thực sự đã lưu |
| GET | `/api/v1/forecasts/{prediction_id}` | Forecast, nguồn gốc, interval, outcome nếu có |
| GET | `/api/v1/models` | Các phiên bản và trạng thái |
| GET | `/api/v1/models/{model_id}/performance` | Metrics, thời gian test, baseline và số mẫu |
| GET | `/api/v1/data-quality` | Độ mới và sự kiện chất lượng được phép hiển thị |

Ở v0.3 thêm `/api/v1/macro`; ở v0.4 thêm `/api/v1/news` và `/api/v1/news/signals`. MVP quản trị qua CLI, chưa cần API public để trigger train hoặc collect.

### 13.2. Minh họa response

Toàn bộ số liệu dưới đây là **fixture minh họa**, không phải giá thị trường hay kết quả dự báo thật:

```json
{
  "prediction_id": "example-prediction-001",
  "asset": "GOLD_USD",
  "source": "configured-provider",
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
  "model_version": "example-xgb-h5-v1",
  "feature_version": "price-v1",
  "mode": "synthetic_demo",
  "freshness_status": "fresh",
  "actual_return": null
}
```

### 13.3. Quy ước API

- `horizon_sessions` chỉ nhận 1 hoặc 5 ở MVP; 20 mở sau.
- `from <= to`; số dòng phải có giới hạn, mặc định 250 và tối đa 2.000 trong thiết kế đầu.
- Dùng datetime UTC; phần hiển thị có thể đổi sang `Asia/Ho_Chi_Minh`.
- `404` khi không có resource; `422` khi tham số sai; `503` khi phụ thuộc thiết yếu không sẵn sàng.
- Forecast cũ vẫn có thể trả `200` kèm `freshness_status=stale`; không đổi `issued_at` thành hôm nay.
- Lỗi trả `code`, `message`, `request_id`; không trả stack trace hoặc secret.
- `/health/ready` phản ánh khả năng phục vụ; freshness dữ liệu có endpoint riêng, tránh restart loop vì nguồn dữ liệu nghỉ lễ.
- API test bằng fixture xác định; unit test không phụ thuộc API thị trường thật.

### 13.4. Yêu cầu hiệu năng dự kiến

Mục tiêu tham khảo: p95 dưới 500 ms với các endpoint đọc đã có index, trên bộ dữ liệu demo và khoảng 10 người dùng đồng thời. Ghi rõ máy, số dòng và công cụ đo khi công bố kết quả; chưa coi đây là SLA.

<a id="s14"></a>
## 14. Dashboard và các luồng sử dụng

### 14.1. Các trang

| Trang | Nội dung |
|---|---|
| Tổng quan | Giá gần nhất, thời điểm cập nhật, nguồn, forecast 1/5 phiên, trạng thái |
| Lịch sử thị trường | Biểu đồ giá, lợi suất, vùng missing và bộ lọc thời gian |
| Dự báo | Point forecast, interval, định nghĩa horizon, kết quả thật khi đến hạn |
| Đánh giá model | Baseline và ứng viên, metrics từng fold, train/test period, số mẫu |
| Chất lượng dữ liệu | Lần chạy gần nhất, độ mới, bản ghi bị loại, nguồn gặp lỗi |
| Macro/tin tức | Chỉ xuất hiện khi module tương ứng đã có dữ liệu |

### 14.2. Quy tắc trình bày

- Phân biệt lịch sử giá thật, forecast đã lưu và fixture demo.
- Biểu đồ h=5 thể hiện dự báo tại đích, không vẽ thành đường đi 5 ngày nếu model chỉ dự báo điểm cuối.
- Interval có nhãn “khoảng dự báo 80% danh nghĩa”, kèm coverage thực nghiệm ở trang model.
- Không hiển thị “AI chắc chắn tăng”, điểm confidence tùy ý hoặc lợi nhuận cam kết.
- Với dữ liệu stale, chỉ rõ lần cập nhật và giữ trạng thái nhìn thấy được.
- Biểu đồ backtest ghi rõ các điểm là out-of-sample hay in-sample.
- Lỗi nguồn/không có dữ liệu là một trạng thái UI đầy đủ, không hiển thị mặc định 0 USD.

### 14.3. Demo cần làm được

Người xem mở trang tổng quan, chọn 5 phiên, xem forecast và khoảng dự báo, mở lịch sử một forecast cũ, đối chiếu với thực tế rồi sang trang performance để so model với baseline. Có thể kiểm tra model version và snapshot tạo ra forecast đó.

<a id="s15"></a>
## 15. Cấu trúc repository và quy ước lập trình

### 15.1. Cấu trúc dự kiến

```text
goldscope/
  README.md
  GOLDSCOPE_PROJECT_GUIDE.md
  pyproject.toml
  uv.lock
  .python-version
  .env.example
  .gitignore
  Dockerfile
  compose.yaml
  alembic.ini
  migrations/
  configs/
    sources.yaml
    features.yaml
    backtest.yaml
    training.yaml
  src/goldscope/
    __init__.py
    cli.py
    core/                 # settings, logging, exceptions, time policy
    collectors/           # base, gold, fred, news về sau
    data/                 # normalization, quality, vintages, snapshots
    features/             # price, macro, news, targets, registry
    ml/                   # baseline, train, predict, intervals, evaluation
    db/                   # engine, models, repositories
    services/             # forecast, market, model, quality
    api/                  # main, routers, schemas, dependencies
    jobs/                 # daily, backfill, retrain, score
  dashboard/
    app.py
    pages/
    api_client.py
  tests/
    unit/
    integration/
    temporal/             # kiểm tra thời điểm và leakage
    fixtures/
  notebooks/              # khám phá; không là nguồn logic production duy nhất
  docs/
    data-source-audit.md
    data-dictionary.md
    model-card.md
    runbook.md
    experiment-log.md
    decisions/
  reports/                # báo cáo được phép công bố
  .github/workflows/
    ci.yml
    deploy.yml
```

Các thư mục runtime như `data/raw`, `data/snapshots`, `artifacts/models`, `logs` nằm ngoài Git và mount bằng volume khi chạy container.

### 15.2. Quy ước code

- Dùng type hints ở hàm công khai và schema ở biên nhập/xuất.
- Ưu tiên function rõ đầu vào/đầu ra cho feature và metrics.
- Chỉ dùng class khi có trạng thái hoặc abstraction cần thiết, ví dụ collector/model adapter.
- Không hard-code API key, ngày test, absolute path hay URL database.
- Tách cấu hình, không nhét logic vào notebook hoặc route handler.
- Với SQLAlchemy bản đầu, dùng sync session và route/service phù hợp; không đặt thao tác DB blocking trực tiếp trong `async def` mà bỏ qua điều phối.
- Tên biến/code bằng tiếng Anh; hướng dẫn có thể bằng tiếng Việt, README CV nên có bản tiếng Anh ngắn.
- Mỗi commit giải quyết một thay đổi có thể mô tả và kiểm tra.

### 15.3. Definition of Done cho một task

- Có đầu ra đúng với mô tả issue.
- Có cách kiểm chứng hành vi chính và tình huống lỗi đáng kể.
- Không lộ secret, không thêm dữ liệu thiếu quyền chia sẻ.
- Cập nhật tài liệu/config khi đổi contract.
- Đã kiểm tra tương thích với dữ liệu và model version liên quan.

<a id="s16"></a>
## 16. Thiết lập môi trường phát triển

### 16.1. Môi trường đề xuất

Trên máy Windows, dùng VS Code với WSL2 Ubuntu để thao tác nhất quán với Linux khi deploy. Có thể dùng Python trực tiếp trên Windows, nhưng chọn một môi trường chính; không dùng chung `.venv` giữa Windows và WSL.

Cần chuẩn bị Git, uv và Docker có Docker Compose. CPU đủ cho MVP; chưa cần GPU. RAM 8 GB có thể bắt đầu với tập nhỏ và ít tiến trình; 16 GB thuận tiện hơn. Đây là ước lượng, phải đo khi có dataset thực tế.

### 16.2. Lệnh khởi tạo dự kiến

Các lệnh dưới là hướng dẫn bootstrap khi bắt đầu viết code, **chưa được thực thi để tạo ứng dụng trong lần soạn tài liệu này**. Dùng terminal Linux/WSL tại thư mục dự định chứa dự án, không chạy đè vào repo sẵn có.

```bash
uv init --package --python 3.12 goldscope
cd goldscope
uv add fastapi uvicorn pydantic-settings sqlalchemy alembic "psycopg[binary]"
uv add httpx pandas numpy pyarrow scikit-learn xgboost typer
uv add streamlit plotly
uv add --dev pytest pytest-cov respx ruff mypy
uv lock
uv sync --locked
```

Sau lần cài thành công, commit `pyproject.toml`, `uv.lock` và `.python-version`. Không nâng tất cả dependency giữa một chuỗi thí nghiệm mà không tạo lại môi trường và ghi phiên bản.

### 16.3. `.env.example` dự kiến

```dotenv
APP_ENV=local
DATABASE_URL=postgresql+psycopg://goldscope:CHANGE_ME@localhost:5432/goldscope
ALPHA_VANTAGE_API_KEY=
FRED_API_KEY=
API_BASE_URL=http://localhost:8000
DATA_ROOT=./data
ARTIFACT_ROOT=./artifacts
FORECAST_HORIZONS=1,5
LOG_LEVEL=INFO
DISPLAY_TIMEZONE=Asia/Ho_Chi_Minh
```

Các giá trị trên là ví dụ cấu hình. Khi chạy trong Compose, host database là tên service `db`, API client trong container dùng `http://api:8000`. File `.env` thật bị loại khỏi Git. Không dùng mật khẩu mẫu khi deploy.

### 16.4. Giao diện CLI cần xây dựng

Những lệnh này là **hợp đồng chức năng dự kiến**; chỉ chạy được sau khi đã viết CLI và thêm entry point `goldscope` trong `pyproject.toml`:

```bash
uv run goldscope sources audit --source gold
uv run goldscope collect gold --start 2016-01-01
uv run goldscope collect macro --series DGS10,DFII10,DTWEXBGS
uv run goldscope dataset build --config configs/features.yaml
uv run goldscope backtest --config configs/backtest.yaml
uv run goldscope train --config configs/training.yaml
uv run goldscope predict --horizon 5
uv run goldscope pipeline daily
uv run goldscope predictions score
```

Ngày bắt đầu ở ví dụ là yêu cầu tải thử, không khẳng định nguồn có dữ liệu từ năm đó. Các lệnh train/backtest phải xuất run ID và đường dẫn report; không chỉ in một số accuracy rồi kết thúc.

Lệnh ứng dụng sau khi đã có module/migration:

```bash
uv run alembic upgrade head
uv run uvicorn goldscope.api.main:app --reload
uv run streamlit run dashboard/app.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

<a id="s17"></a>
## 17. Lộ trình triển khai theo từng lab

### 17.1. Lịch dự kiến

Ước lượng cho một người làm khoảng 12–15 giờ/tuần, đã biết Python cơ bản. Tổng khung 12 tuần là kế hoạch ban đầu, không phải deadline cứng. Nếu vừa học Python từ đầu, cần thêm thời gian cho package, typing, HTTP, SQL, test và Pandas.

| Tuần | Trọng tâm | Phiên bản |
|---|---|---|
| 1 | Xác minh nguồn và bootstrap repo | Nền tảng |
| 2–3 | Collector, dataset, feature và baseline | v0.1 |
| 4 | XGBoost, walk-forward, interval | Chuẩn bị v0.2 |
| 5–6 | API, dashboard, Docker và CI | v0.2 |
| 7–8 | Macro theo thời điểm và ablation | v0.3 |
| 9–10 | Tin tức nếu đủ quyền/độ phủ | v0.4 tùy điều kiện |
| 11–12 | Vận hành, demo, tài liệu và release | v1.0 |

Khi trễ tiến độ, hoãn tin tức hoặc SHAP trước; giữ baseline, thời gian dữ liệu và kiểm thử. Không cắt phần chống leakage để thêm một công nghệ dễ trình diễn hơn.

### Lab 00 — Chốt nguồn dữ liệu và hợp đồng bài toán

**Mục tiêu:** xác định bài toán có dữ liệu thực sự dùng được.

**Thực hiện:** tạo source audit; thử một request giá và ba series macro; xem payload, thời gian, đơn vị, độ phủ, quota; xác định nguồn có revision không; chốt origin/horizon và lịch nguồn.

**Đầu ra:** `data-source-audit.md`, metadata nguồn, fixture hợp lệ đã loại secret, quyết định chọn nguồn.

**Nghiệm thu:** biết chính xác trường giá nào được dùng, gói truy cập làm được gì và hạn chế nào còn mở. Nếu chưa có key, đánh dấu blocked ở bước gọi thật; chỉ có thể viết adapter dựa trên fixture có nguồn gốc rõ ràng.

### Lab 01 — Bootstrap và môi trường tái lập

**Mục tiêu:** clone source có thể cài và chạy test.

**Thực hiện:** package `src/`, settings, logger, CLI skeleton, `.env.example`, uv lock, Git và CI lint/test cơ bản; cấu hình PostgreSQL local.

**Đầu ra:** repository khởi tạo, test smoke cho config/CLI, README quick start.

**Nghiệm thu:** `uv sync --locked` thành công trong môi trường sạch; thiếu cấu hình cần thiết tạo lỗi dễ hiểu; không có key thật trong commit.

### Lab 02 — Collector giá vàng và lưu trữ

**Mục tiêu:** tải giá có thể chạy lại an toàn.

**Thực hiện:** migration nguồn/ingestion/raw/market; collector có timeout và xử lý quota; lưu raw; normalize; unique key; kiểm tra đơn vị và revision; hỗ trợ tải lịch sử và cập nhật.

**Đầu ra:** dataset giá thật ban đầu, run log, báo cáo gap và rejected rows.

**Nghiệm thu:** chạy lại cùng payload không tăng số quan sát nghiệp vụ; mô phỏng 429/timeout/body lỗi không ghi dữ liệu giả; bản ghi sai được tách ra.

### Lab 03 — EDA và snapshot

**Mục tiêu:** hiểu dữ liệu và cố định đầu vào thí nghiệm.

**Thực hiện:** thống kê coverage; xác định lịch nguồn; phân tích missing; vẽ giá/lợi suất; tạo snapshot bất biến với manifest; chia development/holdout.

**Đầu ra:** notebook ngắn, report EDA, snapshot Parquet và hash.

**Nghiệm thu:** cùng raw/version/policy tạo dataset tương đương; mọi sửa dữ liệu đều truy nguyên được; final holdout không dùng để chọn feature.

### Lab 04 — Feature, target và baseline

**Mục tiêu:** hoàn thành v0.1 với một phép đánh giá đúng.

**Thực hiện:** feature price-only; target 1/5 phiên; test cutoff/label availability; baseline zero-return và Ridge; preprocessing fit từng fold; lưu dự báo từng origin.

**Đầu ra:** feature registry, report baseline, bảng prediction và metric theo fold.

**Nghiệm thu:** có thể tự tính một vài dòng để đối chiếu; thay dữ liệu tương lai không làm đổi feature quá khứ; mọi mẫu train có nhãn đã biết trước fit.

### Lab 05 — XGBoost, interval và lựa chọn ứng viên

**Mục tiêu:** đo một mô hình phi tuyến và độ bất định.

**Thực hiện:** tập tham số nhỏ; walk-forward theo cùng lịch của baseline; quantile q10/q90; kiểm tra crossing; báo cáo MAE/RMSE/coverage/width; đăng ký artifacts.

**Đầu ra:** experiment log, model card, bảng E00–E02/E05 và model active theo tiêu chí.

**Nghiệm thu:** báo cáo trung thực cả khi XGBoost kém baseline; artifact chứa feature schema; không dùng holdout để tìm tham số; suy luận trả finite values.

### Lab 06 — FastAPI và lịch sử dự báo

**Mục tiêu:** đưa kết quả nghiên cứu ra giao diện dịch vụ.

**Thực hiện:** repository/service/router; migration model/prediction/outcome; API contract; phân trang; freshness; health; lỗi có mã; integration test trên PostgreSQL.

**Đầu ra:** OpenAPI, endpoint hoạt động và fixture API.

**Nghiệm thu:** không train trong request; truy được một forecast đến model và dataset; dữ liệu chưa đến hạn có outcome null; forecast đã phát hành không bị sửa.

### Lab 07 — Dashboard, Docker và MVP release

**Mục tiêu:** người khác chạy và hiểu được hệ thống.

**Thực hiện:** các trang MVP; Dockerfile từ image Python chính thức; Compose database/API/dashboard; job one-shot; CI lint/test/build; README demo.

**Đầu ra:** v0.2, ảnh giao diện, video demo ngắn, hướng dẫn chạy máy sạch.

**Nghiệm thu:** API và dashboard dùng cùng dữ liệu; Compose có healthcheck; thiếu key vẫn chạy được chế độ fixture có nhãn rõ; đã chạy collector thật ít nhất một lần trước khi gọi là demo dữ liệu thật.

### Lab 08 — Macro point-in-time

**Mục tiêu:** thêm dữ liệu đa biến mà không nhìn trước tương lai.

**Thực hiện:** FRED collector; metadata/vintage; availability policy; as-of join; feature tuổi dữ liệu; kiểm tra release delay; so price-only với price+macro.

**Đầu ra:** v0.3, tối thiểu ba series khi có dữ liệu hợp lệ, report E03, tài liệu limitations.

**Nghiệm thu:** CPI không xuất hiện trước công bố; revision mới không sửa feature lịch sử; dữ liệu theo ngày nhưng công bố trễ được xử lý đúng. Nếu chưa chứng minh được, chỉ bật macro trên dashboard.

### Lab 09 — News signal và kiểm tra đóng góp

**Mục tiêu:** đánh giá tin tức có giúp dự báo không.

**Thực hiện:** thu thập và dedup URL/nội dung; lưu published/first-seen time; nhóm bài cùng sự kiện; lọc relevance; aggregate trước cutoff; version NLP model; ablation cùng giai đoạn.

**Đầu ra:** v0.4, dashboard tin và report E04.

**Nghiệm thu:** không dùng bài xuất bản sau forecast; không nhân nhiều bản sao một tin thành nhiều tín hiệu độc lập; không gán tác động lên vàng chỉ từ cảm xúc tích cực/tiêu cực.

Nếu lịch sử tin quá ngắn, bắt đầu thu thập prospective và chỉ hiển thị tin. Không coi vài tuần dữ liệu là cơ sở mạnh để khẳng định hiệu quả ML.

### Lab 10 — Tự động hóa, vận hành và release CV

**Mục tiêu:** một hệ thống có thể vận hành và giải thích được.

**Thực hiện:** daily job, khóa chống trùng, scoring dự báo đến hạn, backup/restore, lịch retrain, metrics pipeline, deploy và rollback; quay demo; hoàn thiện README/model card.

**Đầu ra:** v1.0, runbook, log chạy theo lịch, báo cáo final holdout và tài liệu CV.

**Nghiệm thu:** tối thiểu 10 lượt chạy theo lịch được ghi trạng thái, gồm cả ngày không có dữ liệu mới; có thử lỗi và phục hồi; restore được một backup; thông tin CV dựa trên kết quả đo thật.

<a id="s18"></a>
## 18. Kiểm thử và tiêu chí nghiệm thu

### 18.1. Ma trận kiểm thử trọng tâm

| Nhóm | Trường hợp cần kiểm tra | Lỗi cần ngăn |
|---|---|---|
| Collector | 200 hợp lệ, 200 body lỗi, 429, timeout, schema đổi | Coi response lỗi là dữ liệu |
| Normalization | Null, ngày sai, currency sai, giá âm | Chuỗi giá bị hỏng |
| Idempotency | Chạy lại payload, job chạy song song | Duplicate và forecast trùng |
| Feature | Rolling/lags khớp tính tay, future perturbation | Leakage |
| Target | Horizon đúng số phiên, ngày cuối thiếu nhãn | Off-by-one, nhãn giả |
| Macro | Vintage thay đổi, công bố sau origin | Revision/release leakage |
| Backtest | Mọi nhãn train có trước fit cutoff | Học bằng kết quả tương lai |
| Model | Feature sai thứ tự/thiếu cột, artifact không tương thích | Dự báo âm thầm sai |
| API | Tham số sai, không có dữ liệu, stale, phân trang | Response gây hiểu nhầm |
| Storage | Transaction thất bại giữa chừng, backup/restore | Dữ liệu nửa chừng hoặc mất lịch sử |
| UI | API mất, interval null, outcome chưa có | Hiển thị giá 0 hoặc kết quả giả |

Test có giá trị cao: sửa tất cả dữ liệu sau ngày D rồi xác nhận feature và prediction đã tái dựng tại D không đổi; tạo CPI công bố ngày D+10 và xác nhận origin D không dùng được; với h=5 xác nhận mẫu có label chưa sẵn sàng không lọt vào train.

### 18.2. Gate nghiệm thu MVP

- [ ] Nguồn giá, đơn vị và lịch nguồn được kiểm chứng.
- [ ] Có raw snapshot, normalized dataset và provenance.
- [ ] Collector chạy lại không sinh dữ liệu nghiệp vụ trùng.
- [ ] Có baseline và ít nhất một model ứng viên.
- [ ] Walk-forward mô phỏng đúng lịch fit/predict đã đăng ký.
- [ ] Có metrics theo từng horizon và từng fold.
- [ ] Có khoảng dự báo với coverage/width ngoài mẫu.
- [ ] API/dashboard phân biệt fresh, stale, unavailable và synthetic demo.
- [ ] Dự báo có model/snapshot ID và outcome riêng.
- [ ] Docker chạy được; CI không cần key thị trường cho unit/integration tests.
- [ ] README cho phép người khác tái hiện luồng demo.
- [ ] Không dùng kết quả chưa đo làm thành tích CV.

Không đặt điều kiện “phải đạt 90% accuracy” hoặc “phải thắng thị trường” để nghiệm thu dự án. Chất lượng kỹ thuật và hiệu quả thống kê là hai kết quả cần báo cáo riêng.

<a id="s19"></a>
## 19. Docker, CI/CD và triển khai

### 19.1. Container MVP

| Service | Vai trò | Ghi chú |
|---|---|---|
| `db` | PostgreSQL | Volume bền vững, healthcheck |
| `api` | FastAPI | Đọc DB; không chạy scheduler nội bộ |
| `dashboard` | Streamlit | Gọi `api`; không giữ secret nguồn |
| `job` | Cùng image Python, entry point CLI | Chạy one-shot hoặc qua scheduler ngoài |

Không cần một container ML thường trực chỉ để predict một lần mỗi ngày. Training chạy qua CLI/job với tài nguyên giới hạn. FastAPI có hướng dẫn chính thức cho container từ Python image [R17].

### 19.2. Pipeline CI

Khi push/PR:

1. Checkout source và cài dependency theo lockfile.
2. Ruff format/lint, mypy theo phạm vi đã cấu hình.
3. Unit và temporal tests với fixture nhỏ.
4. Integration tests bằng PostgreSQL service.
5. Smoke test migration và API.
6. Build Docker image; có thể chạy thêm smoke container.

CI không gọi API bên ngoài mặc định; điều này tránh quota, thiếu secret trên fork và kết quả biến động. Kiểm tra nguồn thật chạy theo workflow riêng có secrets và lịch hạn chế.

### 19.3. CD khi đã có máy chủ

Tag phiên bản → build image bất biến theo commit → push registry → backup trước migration có rủi ro → chạy migration một lần → cập nhật service → readiness check → kiểm tra một API đọc và dashboard.

Ứng dụng rollback bằng image trước. Model rollback bằng đổi bản active. Database migration không phải lúc nào cũng rollback an toàn; ưu tiên thay đổi tương thích ngược và có kế hoạch restore cụ thể.

### 19.4. Môi trường triển khai

- Local: Compose để phát triển và demo.
- Staging: cùng image/config schema, dữ liệu thử hoặc snapshot được phép sử dụng.
- Personal deployment: một máy chủ Linux, reverse proxy và HTTPS khi truy cập từ Internet.
- Không mở PostgreSQL trực tiếp ra Internet; endpoint quản trị nếu thêm phải có xác thực.

Máy chủ 2 vCPU/4 GB RAM là cấu hình thử nghiệm ban đầu cho API/dashboard và tác vụ nhẹ, không phải bảo đảm đủ tài nguyên training. Đo peak RAM trước khi cho training chạy cùng lúc với ứng dụng; nếu cần train ở máy cá nhân rồi chuyển artifact đã kiểm tra.

<a id="s20"></a>
## 20. Vận hành, giám sát và huấn luyện lại

### 20.1. Lịch chạy

Không chốt giờ lấy dữ liệu trước source audit. Quy trình đầu:

1. Quan sát thời điểm dữ liệu nguồn thường sẵn sàng qua một số ngày.
2. Chọn giờ job sau mốc đó, thêm khoảng đệm.
3. Dùng UTC cho scheduler và timestamp; ghi chính sách timezone/DST của nguồn.
4. Nếu chưa có observation mới, retry có giới hạn hoặc `skipped` theo lịch.
5. Khi phát hành chậm, kiểm tra target còn ở tương lai.

Scheduler ban đầu có thể là systemd timer hoặc cron trên máy chủ, chỉ có một nơi chịu trách nhiệm gọi job. Dùng PostgreSQL advisory lock hoặc bảng khóa để ngăn trùng. Không nhúng scheduler vào nhiều worker Uvicorn.

### 20.2. Metrics vận hành

| Nhóm | Theo dõi |
|---|---|
| Thu thập | Lần thành công cuối, latency, quota errors, số dòng mới |
| Chất lượng | Missing, rejected, duplicates, revision count |
| Dữ liệu | Tuổi observation và tuổi publication theo từng nguồn |
| Job | Duration, success/partial/failed, lock contention |
| API | Error rate, p50/p95 latency, request count |
| Model | MAE lăn, baseline skill, coverage, width, số outcome đã trưởng thành |

Chỉ tính performance live khi target đã có kết quả thật. Với h=20, phải chờ đủ horizon và độ trễ công bố; không đánh giá ngay ngày phát hành.

### 20.3. Retrain và model promotion

- Mục tiêu lịch ban đầu: đánh giá retrain mỗi tháng, không train lại theo từng request.
- Candidate dùng dữ liệu/nhãn đã trưởng thành và validation gần đây chưa dùng để fit candidate.
- Model hiện hành và candidate được so trên cùng tập origin hoặc theo chế độ shadow.
- Promotion cần qua gate kỹ thuật và tiêu chí validation; phiên bản cá nhân đầu duyệt thủ công bằng CLI.
- Sau khi promotion, theo dõi live; giữ model trước để rollback.
- Data drift là dấu hiệu cần điều tra, không tự chứng minh model đã kém hoặc model mới tốt hơn.

Final holdout của một release không được tái dùng hàng tháng làm bảng xếp hạng để tối ưu liên tục. Mỗi release ghi rõ giao thức đánh giá và dữ liệu nào đã bị quan sát.

### 20.4. Runbook sự cố

| Sự cố | Hành động |
|---|---|
| Nguồn dữ liệu ngừng hoạt động | Giữ forecast cũ với nhãn stale, dừng phát hành mới thiếu đầu vào |
| Schema nguồn thay đổi | Giữ raw, sửa adapter và test fixture, backfill có log |
| Model lỗi tải | Dừng suy luận, rollback artifact đã xác minh |
| Dữ liệu cũ được sửa | Tạo revision/snapshot mới; không thay prediction đã công bố |
| Ổ đĩa sắp đầy | Áp retention cho raw tạm/log; bảo vệ artifacts còn được tham chiếu |
| Database mất | Khôi phục backup đã thử; đối chiếu manifest và pipeline run gần nhất |

Backup database và artifact manifest theo ngày trong giai đoạn deploy; giữ số bản theo dung lượng thực tế. Trước release v1.0 phải thử restore tối thiểu một lần, không chỉ kiểm tra file backup tồn tại.

<a id="s21"></a>
## 21. Bảo mật, quyền dữ liệu và chi phí

### 21.1. Cấu hình và bí mật

- Secret nằm trong `.env` local hoặc secret store của môi trường deploy/CI.
- Log HTTP phải che `apikey`, token và connection string chứa password.
- DB role ứng dụng có quyền vừa đủ; tài khoản migration quản lý riêng khi deploy.
- API public chỉ đọc ở MVP; backfill/train/promotion dùng kênh quản trị.
- Chỉ tải model artifact do chính dự án tạo và đã kiểm tra hash; không deserialize pickle/joblib không tin cậy.
- Nếu key bị commit, thu hồi và cấp lại; xóa file trong commit mới không làm key cũ hết lộ.

### 21.2. Quyền dữ liệu

Trước khi public repo hoặc dashboard, kiểm tra quyền lưu, hiển thị và phân phối lại của từng nguồn. Giấy phép mã nguồn không tự cấp quyền chia sẻ raw data. Tài liệu này không kết luận một gói API cụ thể cho phép mọi cách tái sử dụng.

Mặc định repo chứa downloader, data dictionary, fixture được phép chia sẻ và báo cáo; không upload toàn bộ dữ liệu tài chính hoặc bài báo. Nếu chưa xác minh quyền hiển thị, dùng demo synthetic được đánh dấu rõ cho phần public.

### 21.3. Ngân sách lập kế hoạch

| Khoản | Phương án ban đầu | Khi phát sinh chi phí |
|---|---|---|
| Phát triển | Máy cá nhân, công cụ nguồn mở | Nâng RAM/ổ đĩa nếu cần |
| Dữ liệu giá | Kiểm tra quyền trong gói hiện có | Lịch sử hoặc quota không đủ |
| Macro | Xác minh điều kiện API và series | Nhu cầu dữ liệu ngoài nguồn hiện có |
| Tin tức | Hoãn nếu ngân sách/độ phủ chưa phù hợp | Lịch sử dài hoặc nguồn chuyên biệt |
| Hosting | Local trước | Cần demo truy cập thường xuyên |
| LLM/GPU | Không dùng ở MVP | Nhánh mở rộng có lợi ích đo được |

Có thể tự đặt trần thử nghiệm 0–500.000 VND/tháng cho dữ liệu và hạ tầng ngoài máy cá nhân. Đây là hạn mức đề xuất để quản lý phạm vi, **không phải báo giá hoặc khẳng định đủ cho mọi nhà cung cấp**. Nếu nguồn vượt trần, ưu tiên đổi phạm vi trước khi mua gói.

<a id="s22"></a>
## 22. Các hướng phát triển mở rộng

### 22.1. Bản đồ mở rộng có điều kiện

| Hướng | Nội dung | Điều kiện bắt đầu | Thước đo thành công |
|---|---|---|---|
| Horizon 20 phiên | Model riêng, khoảng dự báo riêng | 1/5 phiên và label timing ổn | Báo cáo ngoài mẫu theo h=20 |
| Macro đa biến | Yield, USD, CPI và biến đổi | Có vintage/release policy | Ablation trên cùng thời gian |
| Tin tức NLP | Chủ đề, relevance, clustering, sentiment | Đủ quyền và lịch sử tin | Chứng minh lợi ích hoặc kết luận không có lợi ích |
| SHAP | Giải thích local/global | Model ổn định | Giải thích nhất quán với schema/output |
| Xác suất xu hướng | UP/SIDEWAYS/DOWN | Ngưỡng lớp và calibration rõ | Log loss, calibration, macro-F1 |
| Volatility forecasting | Dự báo mức biến động thay vì hướng | Định nghĩa volatility target riêng | So với volatility baseline |
| Regime analysis | Phân tích giai đoạn biến động/thị trường | Quy tắc không sử dụng tương lai khi gán live | So metrics theo regime |
| LSTM/GRU | Cửa sổ chuỗi thay cho feature bảng | Có câu hỏi nghiên cứu, ngân sách tính toán | So cùng data/split và chi phí |
| Transformer | Mô hình chuỗi phức tạp hơn | Dữ liệu và baseline đủ mạnh | Cải thiện tái lập; tránh thêm chỉ để ghi CV |
| Experiment tracking | MLflow, artifact registry | Manifest thủ công trở nên khó quản lý | Tra cứu và rollback dễ hơn |
| Queue/worker | Celery + Redis | Job nhiều, dài, cần concurrency | Retry/idempotency/giới hạn tài nguyên rõ |
| Multi-user | Login, role, watchlist | Có nhu cầu sử dụng thật | Bảo vệ dữ liệu và quản trị |

### 22.2. Mở sang vàng Việt Nam

Cần bài toán dữ liệu riêng: giá mua/bán theo thương hiệu, thời gian báo giá, loại sản phẩm, đơn vị, chênh lệch mua-bán, tỷ giá và mức chênh với quốc tế. Không dùng phép đổi USD/ounce sang VND/lượng làm dự báo SJC và không nối các thương hiệu vào cùng chuỗi.

Mỗi loại vàng có `asset_id` riêng, thêm trường `bid`, `ask`, `brand`, `product_type`. Nguồn phải qua audit về lịch sử và quyền dùng trước. Bài toán có thể là dự báo chênh lệch giá trong nước–quốc tế hoặc spread, thay vì chỉ dự báo giá tuyệt đối.

### 22.3. Mở sang chứng khoán

Giữ khung collector/feature/backtest nhưng bổ sung lịch sở giao dịch, chia tách/cổ tức, mã hủy niêm yết, thay đổi thành phần chỉ số và survivorship bias. Khi dùng adjusted prices, kiểm tra cách điều chỉnh có làm thay đổi dữ liệu quá khứ và feature point-in-time không.

Không coi việc thay `symbol=GOLD` bằng mã cổ phiếu là đủ để có mô hình thị trường chứng khoán đáng tin cậy. Nếu làm nhiều mã, tách tập dữ liệu và phép đánh giá theo tài sản/thời gian có chủ đích.

### 22.4. LLM giải thích hoặc trợ lý nghiên cứu

Chỉ thêm sau khi số liệu có nguồn gốc rõ ràng. LLM có thể viết bản diễn giải từ metrics/feature đã tính, dẫn nguồn tin và giải thích giới hạn. LLM không tự tạo giá dự báo thay cho forecast engine, không được bịa số liệu hoặc biến SHAP thành nguyên nhân kinh tế đã chứng minh.

Trước khi thêm agent/RAG, trả lời: chức năng này giúp người dùng làm việc gì mà API/dashboard hiện tại chưa giải quyết? Nếu chưa có câu trả lời cụ thể, chưa triển khai.

### 22.5. Mô phỏng giao dịch

Đây là nhánh riêng sau forecasting: định nghĩa chiến lược trước đánh giá, dùng giá có thể khớp sau lúc phát hành, tính phí/spread/slippage và giới hạn thanh khoản. Báo cáo drawdown, turnover, risk-adjusted metrics và phân biệt paper trading với giao dịch thật. Bản phát triển này không tự động cho phép kết nối tài khoản giao dịch hoặc đặt lệnh.

<a id="s23"></a>
## 23. Đưa dự án vào CV và trình bày phỏng vấn

### 23.1. Bộ đầu ra portfolio

- Repository có README, quick start, kiến trúc và hướng dẫn cấu hình key.
- Source audit và data dictionary.
- Báo cáo baseline/model/ablation, có kỳ đánh giá và số mẫu.
- Model card: mục tiêu, dữ liệu, hạn chế, metrics và cách sử dụng.
- Dashboard demo; khi offline có video 3–5 phút.
- CI chạy được và một bản release có tag.
- Runbook backup/restore và xử lý sự cố.

### 23.2. Kịch bản demo 5 phút

| Thời gian | Nội dung |
|---|---|
| 0:00–0:40 | Nêu bài toán, tài sản và horizon |
| 0:40–1:30 | Nguồn, thời gian công bố, pipeline và chất lượng dữ liệu |
| 1:30–2:30 | Forecast, interval, lịch sử dự báo và kết quả thật |
| 2:30–3:30 | Baseline, walk-forward và một kết quả ablation |
| 3:30–4:20 | API, Docker/CI và khả năng tái lập |
| 4:20–5:00 | Giới hạn, thất bại đã gặp và hướng cải thiện |

### 23.3. Mẫu ghi CV sau khi đã có kết quả

> Developed GoldScope, a Python market research platform that ingests gold-price and macroeconomic data, evaluates forecasting models with point-in-time walk-forward validation, and serves versioned forecasts through FastAPI and a Streamlit dashboard.

Chỉ giữ “macroeconomic” và “point-in-time” khi đã triển khai/kiểm chứng tương ứng. Có thể thêm các dòng số liệu sau khi đo thật:

- Processed **[N]** observations from **[K]** verified data series with idempotent ingestion and dataset versioning.
- Evaluated **[M]** models across **[F]** time-based folds; reported **[metric]** against a last-price baseline over **[period]**.
- Containerized the application and automated **[verified checks]** using GitHub Actions.

Không điền số đẹp ước đoán; không gọi là production-grade chỉ vì có Docker. Nếu model không vượt baseline, mô tả kết quả và lý do một cách thẳng thắn.

### 23.4. Câu hỏi phỏng vấn cần trả lời được

1. Vì sao dự báo lợi suất và quy đổi ra giá?
2. Vì sao không chia train/test ngẫu nhiên?
3. Observation date khác publication time và vintage thế nào?
4. Vì sao h=5 cần kiểm soát thời gian nhãn?
5. Vì sao accuracy hoặc MAE tốt chưa đủ để kết luận kiếm được tiền?
6. Khi nguồn giá trả lỗi nhưng HTTP 200 thì hệ thống làm gì?
7. Khi model kém baseline, sản phẩm hoạt động như thế nào?
8. Làm sao tái hiện forecast đã phát hành cách đây một tháng?
9. Vì sao bắt đầu bằng modular monolith và scheduler đơn giản?
10. Tin tức hoặc macro đã cải thiện kết quả bao nhiêu trên cùng giai đoạn?

<a id="s24"></a>
## 24. Backlog và công việc bắt đầu ngay

### 24.1. Backlog khởi đầu

| ID | Ưu tiên | Công việc | Phụ thuộc |
|---|---|---|---|
| GS-001 | P0 | Xác minh endpoint/quyền dữ liệu giá | Key/gói nguồn |
| GS-002 | P0 | Chốt giá, đơn vị, lịch và forecast cutoff | GS-001 |
| GS-003 | P0 | Bootstrap repo, lockfile và CI | Không |
| GS-004 | P0 | PostgreSQL và migration đầu | GS-003 |
| GS-005 | P0 | Collector giá, raw, idempotency | GS-001, GS-004 |
| GS-006 | P0 | Quality report và dataset snapshot | GS-005 |
| GS-007 | P0 | Feature/target với temporal tests | GS-002, GS-006 |
| GS-008 | P0 | Baseline + Ridge + backtest | GS-007 |
| GS-009 | P0 | XGBoost, interval, model manifest | GS-008 |
| GS-010 | P0 | API, predictions, outcomes | GS-004, GS-009 |
| GS-011 | P0 | Dashboard + Compose + MVP release | GS-010 |
| GS-012 | P1 | FRED vintage và ablation | GS-008, nguồn macro |
| GS-013 | P1 | Daily job, scoring và backup | GS-011 |
| GS-014 | P1 | Model card, demo và portfolio release | GS-011, GS-013 |
| GS-015 | P2 | Tin tức, SHAP, h=20 và các mở rộng | Theo gate phần 22 |

P0 là cần cho MVP; P1 là nâng chất lượng nghiên cứu/vận hành; P2 là mở rộng có điều kiện. Trong lần triển khai tiếp theo nên bắt đầu GS-001 và GS-003, không bắt đầu bằng giao diện hoặc LSTM.

### 24.2. Công việc trong tuần đầu

**Buổi 1:** đọc phần 2, 3, 6, 7; xác nhận tài khoản API và thử payload; ghi source audit.

**Buổi 2:** bootstrap repo, uv, settings, logger, test fixture và CI.

**Buổi 3:** migration, collector vàng và lưu raw.

**Buổi 4:** kiểm tra duplicate/missing/đơn vị, retry, bắt đầu snapshot.

**Buổi 5:** tổng kết kết quả thực tế; cập nhật giới hạn và điều chỉnh kế hoạch tuần sau.

### 24.3. Những điểm cần quyết định bằng bằng chứng

| Điểm còn mở | Cách giải quyết | Khi cần chốt |
|---|---|---|
| Quyền lấy lịch sử vàng và độ sâu | Gọi thử bằng key của dự án, xem điều kiện nguồn | Trước GS-005 |
| Giờ cập nhật và calendar nguồn | Metadata + quan sát response thực tế | Trước GS-007 |
| Lịch sử revision của giá | Audit và so snapshot; công bố hạn chế nếu không có vintage | Trước báo cáo chính |
| Macro có availability đủ tin cậy không | Kiểm chứng từng series | Trước E03 |
| News có đủ lịch sử/quyền dùng không | Audit riêng | Trước Lab 09 |
| Nơi deploy và ngân sách | Đo RAM/CPU, chọn hạ tầng phù hợp | Sau MVP local |

Không cần trả lời tất cả ngay để bắt đầu. Những điểm còn mở phải được ghi đúng trạng thái, không biến thành giả định ngầm trong code.

<a id="s25"></a>
## 25. Từ điển thuật ngữ và nhật ký quyết định

### 25.1. Thuật ngữ

| Thuật ngữ | Giải thích ngắn |
|---|---|
| MVP | Bản nhỏ nhất chạy được luồng chính và có thể kiểm chứng |
| ETL | Thu thập, biến đổi và nạp dữ liệu |
| Feature | Biến đầu vào dùng cho mô hình |
| Target/label | Kết quả tương lai mô hình cần dự báo |
| Horizon | Khoảng từ origin đến kết quả đích |
| Baseline | Phương pháp đơn giản làm mốc so sánh |
| Leakage | Dữ liệu không được phép biết lọt vào quá trình học/đánh giá |
| Point-in-time | Tái dựng đúng thông tin sẵn có tại một thời điểm |
| Vintage | Phiên bản lịch sử của dữ liệu đã công bố |
| Walk-forward | Đánh giá tiến về tương lai, train chỉ từ quá khứ hợp lệ |
| Holdout | Phần dữ liệu giữ riêng để đánh giá cuối |
| Ablation | Bỏ/thêm một thành phần để đo đóng góp của nó |
| Coverage | Tỷ lệ kết quả thực nằm trong khoảng dự báo |
| Idempotency | Chạy lại cùng thao tác không sinh hiệu ứng nghiệp vụ trùng |
| Lineage | Chuỗi nguồn gốc từ raw data đến kết quả |
| Drift | Phân phối dữ liệu hoặc quan hệ dự báo thay đổi theo thời gian |

### 25.2. Các quyết định ban đầu cần đưa vào ADR

| ADR | Quyết định | Khi xem xét lại |
|---|---|---|
| 001 | Dự báo vàng quốc tế price-only trước | Khi MVP và nguồn dữ liệu ổn |
| 002 | Horizon 1/5 phiên, h=20 sau | Khi có đủ nhãn và thí nghiệm |
| 003 | Modular monolith | Khi đo được nhu cầu tách dịch vụ |
| 004 | PostgreSQL + file artifacts | Khi dung lượng/triển khai đòi hỏi storage khác |
| 005 | FastAPI + Streamlit | Khi UX nhiều người dùng vượt nhu cầu dashboard |
| 006 | Baseline → Ridge → XGBoost | Khi có giả thuyết model khác cần kiểm chứng |
| 007 | Scheduler ngoài API | Khi cần queue và nhiều worker |
| 008 | Snapshot/vintage và temporal tests bắt buộc | Luôn giữ; chỉ cải tiến cách triển khai |

Mẫu ADR gồm: bối cảnh, các lựa chọn, quyết định, lý do, hệ quả, ngày và bằng chứng. Khi thay đổi kiến trúc, cập nhật ADR và tài liệu này cùng commit.

<a id="s26"></a>
## 26. Tài liệu tham khảo chính thức

Các nguồn dưới được tra cứu khi soạn tài liệu ngày 30/09/2026. Endpoint/gói truy cập và tài liệu theo nhánh stable có thể thay đổi; lúc triển khai cần đối chiếu lại phiên bản thực tế. Kiến trúc, backlog, lịch và tiêu chí nghiệm thu trong tài liệu là thiết kế đề xuất riêng cho GoldScope.

| Mã | Nguồn | Dùng để kiểm chứng |
|---|---|---|
| R01 | [Alpha Vantage API Documentation](https://www.alphavantage.co/documentation/) | Endpoint giá vàng và news/sentiment; cần kiểm tra quyền tài khoản |
| R02 | [FRED Real-Time Periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) | Ý nghĩa thông tin theo thời gian thực lịch sử |
| R03 | [FRED Series Observations](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) và [Vintage Dates](https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html) | Quan sát và phiên bản dữ liệu |
| R04 | [uv — Working on projects](https://docs.astral.sh/uv/guides/projects/) và [Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) | Quản lý dependency và lockfile |
| R05 | [Streamlit Documentation](https://docs.streamlit.io/) | Phát triển dashboard Python |
| R06 | [scikit-learn — TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) | Chia theo thời gian và gap |
| R07 | [FRED DGS10](https://fred.stlouisfed.org/series/DGS10) | Metadata lợi suất danh nghĩa 10 năm |
| R08 | [FRED DFII10](https://fred.stlouisfed.org/series/DFII10) | Metadata lợi suất điều chỉnh lạm phát 10 năm |
| R09 | [FRED DTWEXBGS](https://fred.stlouisfed.org/series/DTWEXBGS) | Metadata chỉ số USD diện rộng |
| R10 | [FRED DFF](https://fred.stlouisfed.org/series/DFF) | Metadata lãi suất federal funds hiệu lực |
| R11 | [FRED CPIAUCSL](https://fred.stlouisfed.org/series/CPIAUCSL) | Metadata chỉ số CPI |
| R12 | [FRED DCOILWTICO](https://fred.stlouisfed.org/series/DCOILWTICO) | Metadata giá dầu WTI |
| R13 | [scikit-learn — Common pitfalls](https://scikit-learn.org/dev/common_pitfalls.html) | Preprocessing, pipeline và data leakage; khi triển khai đối chiếu bản stable đã khóa |
| R14 | [XGBoost Parameters](https://xgboost.readthedocs.io/en/stable/parameter.html) | Objective và tham số, gồm quantile regression |
| R15 | [SHAP — Predictive models and causal insights](https://shap.readthedocs.io/en/latest/example_notebooks/overviews/Be%20careful%20when%20interpreting%20predictive%20models%20in%20search%20of%20causal%20insights.html) | Giới hạn khi diễn giải nhân quả |
| R16 | [Celery — Tasks](https://docs.celeryq.dev/en/stable/userguide/tasks.html) | Retry, task execution và idempotency |
| R17 | [FastAPI — Containers and Docker](https://fastapi.tiangolo.com/deployment/docker/) | Đóng gói và triển khai API |

---

**Bước triển khai tiếp theo:** thực hiện Lab 00 và Lab 01, ghi kết quả source audit, sau đó xây collector vàng đầu tiên. Tài liệu này là kế hoạch phát triển; chỉ chuyển từng mục sang “đã hoàn thành” khi có code, dữ liệu hoặc kết quả kiểm chứng tương ứng.
