# Ma trận truy vết Phase 2

Commit code: `c35b999`. Bằng chứng: [`integration.md`](../proof/phase-2/integration.md), [`regression-baseline.md`](../proof/phase-2/regression-baseline.md), [`monster-unit.md`](../proof/phase-2/monster-unit.md).

| AC / phạm vi | Cách kiểm chứng | Kết quả |
|---|---|---|
| Contract v1.1, số chuẩn, 6 nguyên liệu, 6 món | `chonoi/contract.py`, `tests/test_p2_quan.py` | Đạt |
| 8 đàn đầu ca, cá bơi, phản xạ mép, sinh mỗi 360 tick, trần 12 | `tests/test_p2_fish.py` | Đạt |
| Cá Sấu patrol, chase, recoil 60 bước | `tests/test_p2_monsters.py` | Đạt |
| Chạm mất Máu, rơi nửa giỏ LIFO, bất tử 90 tick, ngất do quái | `tests/test_p2_monsters.py` | Đạt |
| 2 bếp, 4 bàn, lịch khách, lọc món theo kế hoạch | `tests/test_p2_quan.py`, `tests/test_p2_day.py` | Đạt |
| `--mode day`, kế hoạch D1–D5, đóng Shop, nâng cấp từ Ngày kế, pause | `tests/test_p2_day.py`, `integration.md` | Đạt |
| Smoke `gather --inventory-out` → `quan --inventory` | `integration.md` | Đạt |
| Headless một Ngày ≤ 20 s | `integration.md` | Đạt trên máy nhóm |
| Regression P1 | Toàn bộ test, 78/78 | Đạt |
| Menu, pause, HUD, chữ ≥ 18 px, ≥ 30 FPS trên trình duyệt | Chưa chơi thử | **Chưa xác nhận** |

## Test đổi vì luật mới

- `test_smoke_p1`: `day` đã là mode hợp lệ, số đàn đầu ca đọc từ contract (8).
- `test_p2_monsters`: viết lại vì API cũ chưa có waypoint, recoil 60 bước và mất nửa giỏ.
- Gộp nhánh của Huyền (`ee2ee05`): giữ luật theo TICKET-02 mục 1.2, gồm rơi `floor(số đang mang / 2)`, điều kiện `d ≥ 10`, chặn theo dải độ sâu và `monster_hit.pos`; nhận thêm xử lý `stunned` và các test `from_day`, thoát chase, bất tử, scenario sai.
