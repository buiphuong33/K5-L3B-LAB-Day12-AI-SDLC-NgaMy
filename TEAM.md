# TEAM

**Tên nhóm:** NgaMy  **Số người:** 4  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Phương (trưởng nhóm) | buiphuong33 | `client/ui` | Integrator, Release | Huyền |
| Tâm | minhtama11qc-hash | `sim/gather` | PO | Nga |
| Nga | Ngahoang2005 | `sim/quan` | Scrum | Tâm |
| Dương Thị Huyền - 2A202604077 | duongthuyen | `qa` | QA lead | Phương |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Phân công theo file

Mỗi file chỉ có **một người sửa**. Cần đổi file của người khác thì nhắn chủ file, hoặc làm cặp và ghi `Co-authored-by:`.

| Người | Code / dữ liệu sở hữu | Tài liệu sở hữu | Kết quả phải giao |
|---|---|---|---|
| **Phương** | `chonoi/web/`, `chonoi/live.py`, `chonoi/contract.py`, `chonoi/sim/ramp.py`, `game.contract.json`, các file khung còn lại của `chonoi/` | `TEAM.md`, `README.md`, `CHANGELOG.md`, `CREDITS.md`, `docs/contracts/`, `docs/adr/`, `docs/plan/` | HUD và đồ họa, chốt hợp đồng tích hợp, gộp code, gắn tag `phase-1` … `phase-4`, Release `v1.0.0` |
| **Tâm** | `chonoi/sim/gather.py` | `docs/clarify.md`, `AGENTS.md` | Lát 1 (bơi, oxy, ngạt, Máu, ngất, giỏ LIFO), lát 2 (hái, bắt cá, cập bến, xuất kho) |
| **Nga** | `chonoi/sim/quan.py`, `chonoi/scenario.py` | `docs/standup.md`, `docs/retro.md`, `docs/ai-usage-log.md` | Lát 3 (khách, giữ chỗ, kiên nhẫn, `no_dish`), lát 4 (bếp, bưng, phục vụ, tiền, boa, uy tín, hết ca), kiểm mâu thuẫn scenario |
| **Dương Thị Huyền** | `tests/`, `tools/`, `.github/`, `.agents/skills/` | `docs/verification/`, `docs/proof/` | Test theo từng AC, kiểm tất định (cùng seed giống từng byte), ma trận truy vết, ít nhất 2 skill của nhóm |

Việc riêng của **mọi người**: tối thiểu 3 commit có nội dung và tự viết `docs/members/<handle>.md`. Nhật ký dùng AI gửi cho Nga để ghi vào một chỗ, tránh conflict.

## Điểm bàn giao giữa các module

- **Tâm → Nga:** file kho do `gather` xuất là đầu vào của `quan`. Định dạng theo `docs/contracts/`, Phương chốt trước khi hai bên code.
- **Tâm, Nga → Phương:** UI chỉ đọc snapshot. Đổi tên hoặc thêm trường snapshot thì báo Phương.
- **Tâm, Nga → Huyền:** xong mỗi lát thì báo để Huyền kiểm theo AC. Lỗi được trả về chủ module sửa, Huyền không sửa luật.
- **Mọi người → Tâm:** chỗ mơ hồ trong đề gửi Tâm ghi vào `docs/clarify.md` và hỏi giảng viên.

## Phân công Phase 2 (TICKET-02, Test Contract v1.1, hạn tag 1:55)

Phạm vi: chỉ làm **lõi**. Nhóm 4 người không bắt buộc mở rộng. Bảng này bổ sung cho bảng file ở trên, mỗi file vẫn chỉ có một người sửa.

| Người | Lát | Việc phải giao | File sở hữu trong Phase 2 | Test của lát |
|---|---|---|---|---|
| **Phương** | 4. Vòng ngày | Chốt `game.contract.json` v1.1 (số chuẩn, `day_plan`, `shop`, `monsters`); `--mode day`, `--days`; đổi pha, Shop, pause, `buy`, `shop_done`; menu, DayIntro, EveningIntro, DayResult, Summary, HUD | `game.contract.json`, `chonoi/sim/day.py` (mới), `chonoi/runner.py`, `chonoi/headless.py`, `chonoi/inputs.py`, `chonoi/contract.py`, `chonoi/live.py`, `chonoi/web/` | `tests/test_p2_day.py` |
| **Tâm** | 1. Cá và buổi sáng | Cá bơi, phản xạ mép, đổi hướng theo seed; 8 đàn đầu ca, sinh cá mỗi 360 tick, trần 12; cá kèo, nút N5/N6; ráp cá và quái vào đúng thứ tự một bước của `gather`; `fish_spawned` | `chonoi/sim/fish.py` (mới), `chonoi/sim/gather.py` | `tests/test_p2_fish.py` |
| **Huyền** | 2. Cá Sấu và kiểm chứng | M1/M2, patrol, chase, recoil; chạm mất Máu, rơi đồ LIFO, bất tử 90 tick; `monster_hit`, `faint` do quái; regression P1, smoke tích hợp, ma trận Phase 2 | `chonoi/sim/monsters.py` (mới), `tests/` còn lại, `docs/verification/phase-2.md`, `docs/proof/phase-2/` | `tests/test_p2_monsters.py` |
| **Nga** | 3. Quán | 2 bếp, 4 bàn, 6 món, 6 nguyên liệu; lọc món theo kế hoạch ngày; kiểm scenario `gather`, `quan`, `day` theo v1.1 | `chonoi/sim/quan.py`, `chonoi/scenario.py` | `tests/test_p2_quan.py` |

Tài liệu giữ nguyên chủ cũ: Tâm ghi `docs/clarify.md`, Nga ghi `docs/standup.md`, `docs/retro.md`, `docs/ai-usage-log.md`, Phương cập nhật README và `docs/contracts/`.

### Thứ tự và phụ thuộc

| Mốc | Việc | Người |
|---|---|---|
| 1:00–1:05 | Cả nhóm `git pull` từ `main`, chốt giao diện bên dưới. Không dùng nhánh `gather-lat2` cũ | Cả nhóm |
| Trước 1:10 | Đẩy `game.contract.json` v1.1 để các lát đọc số chuẩn | Phương |
| 1:05–1:20 | Làm song song bốn lát bằng fixture riêng | Cả nhóm |
| 1:20 | Smoke `gather --inventory-out` → `quan --inventory`, lưu `docs/proof/phase-2/integration.*`, standup | Huyền, Nga ghi |
| 1:20–1:35 | Ráp `monsters` và `fish` vào `gather`, ráp `gather` và `quan` vào `day` | Tâm, Phương |
| 1:35–1:45 | Smoke `day --days 1`, chạy nhiều Ngày kiểm cấp nâng cấp, regression P1 | Huyền |
| 1:45–1:50 | Retro nhanh, một hành động có người nhận | Nga |
| Trước 1:55 | Gắn và đẩy tag `phase-2` | Phương |

### Giao diện chốt giữa các lát

- **`fish.py` → `gather.py` (Tâm):** cá nhận `Streams`, `IdAllocator`; có hàm bơi và sinh cá theo `phase_tick`.
- **`monsters.py` → `gather.py` (Huyền → Tâm):** `MonsterSet.step(player, events)` cập nhật quái theo id và xét tối đa một hit; `snapshot()` trả `monsters[]`. Huyền không sửa `gather.py`, Tâm gọi đúng thứ tự mục 4.5.
- **`gather`, `quan` → `day.py` (Tâm, Nga → Phương):** `day.py` dựng hai sim từ tuning, truyền `active_upgrades` và `dishes` của Ngày, nhận kho từ `gather_end.inventory`.
- **`scenario.py` (Nga):** Tâm và Huyền gửi Nga quy tắc kiểm cho `fish[]`, `monsters[]`, Phương gửi quy tắc cho khối `day`.
- **Test cũ cần đổi vì số chuẩn:** báo Huyền sửa và ghi lý do trong commit.

## Phase 3–4

Yêu cầu mở theo mốc giờ trên lab board. Khi phase mở, Tâm đọc yêu cầu, Phương chia việc trong 5 phút theo nguyên tắc: tính năng thuộc module nào thì chủ module đó làm, tính năng mới đặt ở **file mới có đúng một chủ** và ghi thêm vào bảng trên.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: … (nhóm điền)
- Khi bất đồng về thiết kế: mỗi bên nói 2 phút, không xong thì Phương quyết và ghi lý do vào `docs/adr/`.
- Khi ai đó trễ hoặc vướng quá 10 phút: báo ngay trong kênh, người dự phòng vào làm cặp.
- Giờ standup giữa phase: 0:30, 1:20, 2:15, 2:45 (mỗi lần tối đa 3 phút, Nga ghi).
- Cách đọc code của nhau: Tâm và Nga đọc chéo phần luật, Huyền đọc UI của Phương, Phương đọc test của Huyền.
- Cách làm việc với Git: nhánh ngắn theo lát rồi PR vào `main`, chạy test trước khi gộp, Phương gộp và là người duy nhất gắn tag.
