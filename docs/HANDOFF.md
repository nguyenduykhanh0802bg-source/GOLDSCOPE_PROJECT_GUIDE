# Mẫu bàn giao một phiên làm việc

Đây là mẫu, các trường trong ngoặc cần điền từ kết quả thực tế. Khi dùng, tạo note trong `docs/handoffs/` hoặc cập nhật phần nhật ký task; không thay thế PROJECT_STATUS bằng nhiều bản tiến độ riêng.

## Thông tin

- Ngày/giờ và timezone: [thực tế]
- Task ID: [GS-xxx]
- Trạng thái: [TODO/IN_PROGRESS/BLOCKED/DONE/DEFERRED]
- Branch/commit nếu có: [thực tế hoặc chưa có Git]
- Mục tiêu đã xử lý: [một đoạn ngắn]

## Thay đổi

| File/module | Thay đổi | Mục đích |
|---|---|---|
| [path] | [nội dung] | [hành vi đạt được] |

## Kiểm chứng

| Command và cwd | Kết quả thực tế | Evidence |
|---|---|---|
| [lệnh] | [exit code, test count, lỗi] | [path] |

## Giới hạn và tiếp nối

- Chưa kiểm tra: [điều gì và vì sao]
- Blocker: [credentials/contract/environment; không ghi giá trị secret]
- Quyết định mới: [ADR path hoặc không có]
- Trạng thái/contract đã cập nhật: [path]
- Bước tiếp theo: [một task và đầu ra cụ thể]

Nếu không còn blocker, ghi “không có” dựa trên phạm vi task, không suy rộng rằng toàn bộ hệ thống đã hoàn thành.
