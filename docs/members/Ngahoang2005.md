# Nga (Ngahoang2005)

## Phần việc

- `chonoi/sim/quan.py`: khách, đơn và giữ chỗ nguyên liệu; nấu, bưng, phục vụ; thanh toán, boa, uy tín và hết ca.
- `chonoi/scenario.py`: kiểm dữ liệu quán và các trạng thái khách/bếp mâu thuẫn.
- `docs/standup.md`, `docs/retro.md`, `docs/ai-usage-log.md`: ghi tiến độ, retrospective và cách dùng AI.

## Bàn giao Phase 1

- Mô phỏng dùng `Streams` cho lựa chọn món, `IdAllocator` cho khách sinh mới và `sort_by_id` cho thứ tự ổn định.
- Tuning (giá, thời gian, bán kính, boa, uy tín, giới hạn) đọc từ contract/menu.
- Đã nhận PRD-0 đầy đủ trong `Pasted text.txt` và căn chỉnh schema đơn, event, thứ tự timer/tương tác/đóng ca theo mục D–F.
- Lệnh test và kết quả được ghi ở phần báo cáo bàn giao của lượt làm việc này; không tự tạo commit thay cho Nga.
