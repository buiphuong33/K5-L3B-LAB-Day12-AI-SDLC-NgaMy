# Regression baseline Phase 3

- Ngày: 2026-11-21 (Asia/Bangkok)
- Commit được kiểm: `e4580e1`
- Tag nền: `phase-2` tại `a090780`
- Môi trường: Windows, Python 3.10.1
- Contract hiện tại: v1.1

## Lệnh

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

## Kết quả

- Tổng: 92 test.
- Đạt: 92.
- Trượt/lỗi: 0.
- Cá, Cá Sấu, quán v1.1, vòng ngày, regression P1–P2, schema kho cá thể, ngưỡng 30 và `lost` cá thể đều xanh.

## Trạng thái Phase 3

`chonoi/items.py`, `test_p3_inventory.py` và khối tuning độ tươi đã có; contract chủ động còn v1.1. Nhánh `origin/p3-gather-fresh` chưa nhập `main`, chưa thấy nhánh quán Phase 3. Smoke headless hai tiến trình và `day` vì vậy vẫn chờ bản tích hợp v1.2.
