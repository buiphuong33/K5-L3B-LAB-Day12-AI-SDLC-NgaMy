---
name: determinism-check
description: Kiểm đầu ra headless có giống từng byte với cùng seed ở cả gather và quan. Dùng trước khi gắn tag hoặc sau khi sửa RNG, thứ tự entity, snapshot và JSONL.
---

# Determinism Check

1. Đọc `game.contract.json` và không hard-code tuning vào test.
2. Chạy test tập trung:

   ```bash
   PYTHONPATH=tests:. python3 -m unittest tests.test_determinism -v
   ```

3. Nếu lỗi, so sánh hai file JSONL theo tick đầu tiên khác nhau. Kiểm tra mọi ngẫu nhiên đi qua `Streams`, entity được sắp bằng `sort_by_id`, và dữ liệu map được ghi theo khóa ổn định.
4. Không sửa hoặc nới test để che sai khác. Gửi lỗi về chủ module tạo ra trạng thái không tất định.
5. Ghi lệnh, commit và kết quả thật vào `docs/proof/phase-n/`.
