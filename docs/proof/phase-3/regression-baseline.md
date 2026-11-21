# Regression baseline Phase 3

- Ngày: 2026-11-21 (Asia/Bangkok)
- Commit được kiểm: `c42119e`
- Tag nền: `phase-2` tại `a090780`
- Môi trường: Windows, Python 3.10.1
- Contract hiện tại: v1.1

## Lệnh

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

## Kết quả

- Tổng: 79 test.
- Đạt: 79.
- Trượt/lỗi: 0.
- Cá, Cá Sấu, quán v1.1, vòng ngày, regression P1, kiểm nhóm và test migration `lost` cá thể đều xanh.

## Trạng thái Phase 3

Chưa có `chonoi/items.py`, test P3 của Phương/Tâm/Nga hoặc contract v1.2 trên remote. Test bảo toàn object cá thể trong `monster_hit.lost` đã đạt; các smoke độ tươi, file kho và `day` chờ schema v1.2 được tích hợp.
