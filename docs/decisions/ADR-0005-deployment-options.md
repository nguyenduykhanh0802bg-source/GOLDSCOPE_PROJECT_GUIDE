# ADR-0005 — Phương án triển khai

Ngày: 01/10/2026. Trạng thái: proposed.

## Đề xuất

Local Compose trước; sau đó một VPS Linux, registry image bất biến, reverse proxy/TLS và backup ngoài host. Có thể dùng GHCR cho registry, Caddy cho HTTPS; Nginx là lựa chọn thay thế nếu phù hợp kỹ năng/hạ tầng.

## Chưa chốt

Nhà cung cấp, CPU/RAM thực tế, domain, proxy, quyền truy cập demo, registry và chi phí. Chưa có tài khoản/host/image/URL production được tạo.

## Tiêu chí chấp nhận

Đo tài nguyên, kiểm tra quyền dữ liệu public, chọn audience và secret mechanism, backup/restore rehearsal, rollout/rollback smoke. Chỉ chuyển accepted sau quyết định triển khai; docs không tự cấp quyền mua/deploy.

## Hệ quả

GS-014 phải hoàn thiện các quyết định này trước khi chạy thao tác ngoài môi trường local. Hạ tầng không đủ RAM training thì cân nhắc train riêng, không tuyên bố cấu hình VPS minh họa đã benchmark.
