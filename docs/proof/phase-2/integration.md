# Smoke tích hợp Phase 2

- Commit code được kiểm: `c35b999`. Các commit sau đó đến tag `phase-2` chỉ đổi tài liệu.
- Môi trường: Windows 11, Python 3.11.9. Máy không có lệnh `python3`, nên lần chạy ánh xạ `python3` sang Python đã cài.
- Toàn bộ test: **73 chạy, 0 trượt, 0 lỗi**.

## Smoke hai tiến trình
- Mã thoát: gather 0, quan 0
- File kho: {"items":{"bong_sung":2,"ca_loc":1}}
- Stock quán tick 0: {"bong_sung": 2, "ca_loc": 1}

## Một Ngày và năm Ngày
- 1 Ngày: mã 0, 1.90 s, 22200 tick, reason days_complete, days_completed 1, số kế hoạch công bố 1
- 5 Ngày: mã 0, 8.68 s, 111000 tick, reason days_complete, days_completed 5, số kế hoạch công bố 5

## Nâng cấp từ Ngày kế
- Mã 0; mua ['oxygen', 'hp']; Ngày 2 oxy tối đa 2700 tick, Máu tối đa 4

## Cá, Cá Sấu và tất định
- Đàn đầu ca 8; fish_spawned tại tick [360, 720, 1080, 1440]; quái ['M1']
- Hai lần cùng seed giống từng byte: True (4602a53acb81f957)

## Chưa kiểm

- Chưa chơi trên trình duyệt: menu, pause, HUD, cỡ chữ 18 px và 30 FPS chưa được xác nhận.
- Chưa chạy trên macOS hoặc Linux.
