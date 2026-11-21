# Tiến độ tích hợp Phase 4

- Ngày kiểm: 2026-11-21 (Asia/Bangkok)
- Nền `main`: `2a4b419`
- Test artifact bổ sung: `535ff19`
- Contract hiện tại: v1.2

## Regression

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

Kết quả sau khi nhập lát soak: 125/125 test đạt, 0 trượt/lỗi. Hai `ResourceWarning` cũ trong `test_p3_inventory.py` không ảnh hưởng kết quả.

## Kiểm chéo soak

```bash
python3 -m chonoi.soak --seed 17 --days 10 --out soak-qa.json
```

- Schema gốc đúng `days`, `days_completed`, `crashes`, `results`, `duration_s`.
- Hoàn thành 10/10 ngày, `crashes: 0`.
- `results[]` khớp từng phần tử với [`soak.json`](soak.json); `duration_s` được phép khác vì là thời gian thực.

## Phần còn chờ

- `game.contract.json` vẫn v1.2, chưa khai `bench_cmd`/`soak_cmd`; chưa có lát contract v1.3 và Ngày 6–10 của Phương.
- UI có cảnh báo bằng màu/thanh cho oxy, độ tươi, kiên nhẫn nhưng chưa thấy chế độ tương phản cao.
- Lát đóng gói đã có ở `origin/p4-package`, chưa nhập `main`, nên chưa chạy clone/package check trong regression chính.
