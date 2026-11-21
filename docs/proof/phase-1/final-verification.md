# Kiểm chứng cuối Phase 1

- Commit code được kiểm: `0a7955f`. Các commit sau đó đến tag `phase-1` chỉ đổi tài liệu.
- Môi trường: Windows 11, Python 3.11.9. Máy không có lệnh `python3`, nên lần chạy ánh xạ `python3` sang Python đã cài.

## Kết quả

- Toàn bộ test: **51 chạy, 0 trượt, 0 lỗi**.
- `tools/check_team.py`: OK, 4 thành viên.
- Smoke hai tiến trình theo PRD: cả hai mã thoát 0, `catch.json` là `{"items":{"bong_sung":2,"ca_loc":1}}`, snapshot quán tick 0 có `stock` `{"bong_sung":2,"ca_loc":1}`.
- Mã JavaScript của HUD qua `node --check`.

## Chưa kiểm

- Chưa chơi thử bằng tay trên trình duyệt, nên độ dễ đọc của HUD chưa được xác nhận.
- Chưa chạy trên macOS hoặc Linux.
