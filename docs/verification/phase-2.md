# Ma trận truy vết Phase 2

Nguồn yêu cầu khả dụng: TICKET-02 và giao diện chốt trong [`TEAM.md`](../../TEAM.md). Bằng chứng hiện có: [`regression-baseline.md`](../proof/phase-2/regression-baseline.md).

| AC / phạm vi | Cách kiểm chứng dự kiến | Phụ thuộc | Kết quả |
|---|---|---|---|
| Regression toàn bộ Phase 1 | `python3 -m unittest discover -s tests -v` | Không | Đạt: 51/51 |
| Test Contract v1.1 và số chuẩn cá sấu | Đọc `contract_version`, tuning `monsters` từ `game.contract.json` | Phương đẩy contract v1.1 | **Chờ phụ thuộc** |
| Khởi tạo M1/M2 và snapshot sắp theo id | `tests/test_p2_monsters.py` | Contract v1.1 | Chưa chạy |
| Patrol, chase và recoil đúng biên/tốc độ | Fixture riêng, snapshot mỗi tick | Contract v1.1 | Chưa chạy |
| Tối đa một `monster_hit` mỗi tick | Đặt M1/M2 cùng chạm người chơi, kiểm id ưu tiên | Contract v1.1 | Chưa chạy |
| Trúng đòn mất Máu, rơi đồ LIFO, bất tử 90 tick | Kiểm event, `hp`, `hold`, `invuln_ticks` | Contract v1.1 | Chưa chạy |
| Máu về 0 phát `faint` do quái và kết thúc gather | Kiểm event, kho rỗng, `gather_end` | Tâm ráp `MonsterSet` vào `gather.py` | Chưa chạy |
| Scenario `monsters[]` sai trả mã 2 | Test hộp đen qua `headless_cmd` | Nga cập nhật `scenario.py` | Chưa chạy |
| Cùng seed cho chuyển động/snapshot giống từng byte | Chạy fixture cá sấu hai lần | Tích hợp gather hoàn tất | Chưa chạy |
| Smoke `gather --inventory-out` sang `quan --inventory` | Hai tiến trình, lưu JSONL và kho | Tâm/Nga tích hợp | Chưa chạy |
| Smoke `day --days 1` và nhiều Ngày | Headless mode `day` | Phương hoàn thiện vòng ngày | Chưa chạy |

## Đánh giá ngắn

- Phase 1 vẫn xanh sau khi pull code tích hợp.
- Không hard-code số cá sấu khi `game.contract.json` còn ở v1.0. Bắt đầu `monsters.py` và `tests/test_p2_monsters.py` ngay sau khi Phương đẩy contract v1.1.
- Khi Tâm ráp `MonsterSet.step(player, events)` vào `gather.py`, chạy lại toàn bộ regression trước smoke tích hợp.
