# Smoke tích hợp Phase 3

- Commit code được kiểm: `3973760`. Các commit sau đó đến tag `phase-3` chỉ đổi tài liệu.
- Môi trường: Windows 11, Python 3.11.9. Máy không có lệnh `python3`, nên lần chạy ánh xạ `python3` sang Python đã cài.
- Contract: v1.2. Toàn bộ test: **115 chạy, 0 trượt, 0 lỗi**.

## Ngưỡng ươn theo ticket
- Mã 0; event: `{"type":"event","tick":1,"phase":"gather","name":"spoiled","data":{"item_id":"I1","kind":"ca_linh","location":"hold"}}`

## Bàn giao qua file
- Mã 0, 0; file `{"items":[{"id":"I1","kind":"ca_linh","fresh":99.99166666666666}]}`
- Snapshot quán tick 0 khớp chính xác file: True
- Kho đếm cũ trả mã 2

## Một lượt day có nấu và phục vụ
- Mã 0; chuỗi event: ['cook_started', 'dish_ready', 'dish_picked', 'served', 'paid']
- Nấu bằng ['I1'], giá chốt 59; trả 59 + boa 11 = 70

## Nhiều Ngày và tất định
- Mã 0; Ngày 2 cấp id mới cho mẫu giỏ: I2
- 5 Ngày chạy hai lần: mã 0, 0; giống từng byte: True (af72a6d633ad31a3)

## Chưa kiểm

- Chưa mở trình duyệt để xác nhận HUD độ tươi hiển thị đúng khi chơi.
- Chưa chạy trên macOS hoặc Linux.
