# Regression baseline Phase 2

- Ngày: 2026-11-21 (Asia/Bangkok)
- Commit được kiểm: `f8248f9`
- Môi trường: Windows, Python 3.10.1
- Contract tại thời điểm kiểm: v1.0

## Lệnh

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

## Kết quả

- Tổng: 51 test.
- Đạt: 51.
- Trượt/lỗi: 0.
- Bộ test gồm contract/smoke Phase 1, luật gather/quan, tính tất định, live server, unit starter và kiểm danh sách nhóm.

## Blocker Phase 2

`game.contract.json` chưa có Test Contract v1.1 hoặc tuning `monsters`. Theo quy ước repo, luật không được hard-code số liệu, vì vậy chưa thể triển khai và xác nhận M1/M2, patrol, chase, recoil, khoảng va chạm hoặc tốc độ. Giao diện tích hợp đã chốt trong `TEAM.md`: `MonsterSet.step(player, events)` và `snapshot()`.
