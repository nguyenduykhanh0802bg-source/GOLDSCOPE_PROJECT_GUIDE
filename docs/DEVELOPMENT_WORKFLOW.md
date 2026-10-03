# Quy trình phát triển với Claude Code

## 1. Nhận task

Đọc trạng thái dự án và task spec; kiểm tra source thực tế. Ghi rõ đầu ra mong muốn, dependency, phạm vi file/module và những điểm chưa xác minh. Các đường dẫn cho module tương lai trong task là vùng tạo mới được dự kiến, không phải bằng chứng chúng đã tồn tại.

Với task rõ ràng và thay đổi local có thể đảo ngược, tiến hành trong phạm vi đã giao. Chỉ hỏi khi thiếu thông tin làm thay đổi đáng kể hợp đồng nghiệp vụ, quyền truy cập hoặc hành động ngoài phạm vi; hoàn thành phần không bị chặn trước.

## 2. Trước khi sửa

- Nếu có Git, xem `git status` và diff liên quan để giữ thay đổi đang có của người dùng.
- Chọn tài liệu đúng phạm vi theo docs/README.md.
- Dùng task ID làm đầu mối; không tự đổi target/horizon/provider để làm test dễ hơn.
- Chia task quá lớn thành các thay đổi kiểm chứng được, vẫn hướng tới toàn bộ tiêu chí task.
- Không thêm framework/service mới vì thấy phổ biến; cần vấn đề cụ thể và ADR nếu đổi kiến trúc.

## 3. Thực hiện

- Tách logic xử lý khỏi IO để có test xác định.
- Viết validation, failure path và logging cùng với happy path.
- Fixture lỗi/synthetic có nhãn và nguồn gốc. Response thành công chưa có thì không đặt tên fixture là real GOLD response.
- Không dùng test network mặc định. Không chứa key trong command line, exception hoặc output chia sẻ.
- Thay đổi data/API/ML contract phải cập nhật tài liệu và schema trong cùng task.
- Migration đã áp dụng ở môi trường chia sẻ phải được bổ sung bằng migration mới, không sửa lịch sử.

## 4. Kiểm chứng

Chạy test trực tiếp liên quan tới hành vi thay đổi trước; mở rộng khi có rủi ro còn lại hoặc gate CI bắt buộc. Không chạy lại toàn bộ nghiên cứu ML cho một thay đổi tài liệu.

Ghi đủ command, cwd, Python/env version cần thiết, exit code, số test và lỗi. Không ghi “pass” cho lệnh chưa chạy, timeout hoặc có fixture thay thế mà không nói rõ.

Audit CLI exit 2 cần xem ý nghĩa nghiệp vụ trong report; khác với test runner exit 0/khác 0. Collector future phải định nghĩa mã thoát riêng trong runbook.

## 5. Bàn giao

Cập nhật task bằng bảng: trạng thái; file đã đổi; evidence; test đã chạy; phần chưa kiểm tra; bước tiếp. Cập nhật PROJECT_STATUS khi thay đổi tiến độ hoặc blocker. Nếu task chưa đủ điều kiện DONE, giữ BLOCKED/IN_PROGRESS với phần đã hoàn thành.

Nếu người dùng yêu cầu commit, dùng commit nhỏ có task ID và mô tả mục đích. Không tự tạo remote, push, deploy hoặc mua dịch vụ chỉ vì đã sửa code local. Không dùng force push/reset để bỏ thay đổi người dùng.

## 6. Định nghĩa hoàn thành

- Đáp ứng hành vi và failure paths trong task.
- Các điều kiện dữ liệu/thời gian không bị yếu đi.
- Test cần thiết đạt hoặc kết quả thất bại được công bố và task chưa DONE.
- Contract/config/docs liên quan khớp code.
- Bằng chứng không chứa secret hoặc số liệu bịa.
- Người tiếp theo biết cách tái hiện và việc còn lại.

## 7. Khi context thay đổi

Đọc lại PROJECT_STATUS và task. Kiểm tra source/diff thực tế, không khôi phục theo trí nhớ cuộc trò chuyện. HANDOFF là tóm tắt để định hướng, không thay thế evidence. Khi tài liệu và code xung đột, ghi discrepancy, xác định phạm vi giải quyết và tránh sửa nhiều module không liên quan.
