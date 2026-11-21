---
name: phase-verification
description: Chạy kiểm chứng cuối phase và cập nhật ma trận truy vết bằng bằng chứng thật. Dùng trước mỗi tag phase-n và sau khi tích hợp các lát luật.
---

# Phase Verification

1. Đọc yêu cầu phase đang mở, `game.contract.json`, và `docs/verification/phase-n.md`.
2. Chạy toàn bộ suite từ thư mục gốc:

   ```bash
   PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
   ```

3. Chạy smoke headless cho từng mode liên quan:

   ```bash
   python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out out.jsonl
   python3 -m chonoi.headless --mode quan --seed 1 --ticks 600 --out out-quan.jsonl
   ```

4. Tạo `docs/proof/phase-n/qa.md` gồm commit, môi trường, lệnh, số test đạt/trượt và lỗi còn lại. Không ghi “đạt” nếu chưa chạy được.
5. Cập nhật mỗi AC trong `docs/verification/phase-n.md` bằng test cụ thể và đường dẫn proof. Lỗi luật gửi chủ module; QA không sửa luật để làm test xanh.
