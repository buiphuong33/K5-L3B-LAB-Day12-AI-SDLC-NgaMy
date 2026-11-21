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

## Phân công Phase 3 (TICKET-03, Test Contract v1.2, hạn tag 2:30)

Phạm vi: chỉ làm **lõi độ tươi**. Nhóm 4 người không bắt buộc làm Dòng nước lũ và Khách đặt trước. Mỗi file vẫn chỉ có một người sửa.

| Người | Lát | Việc phải giao | File sở hữu trong Phase 3 | Test của lát |
|---|---|---|---|---|
| **Phương** | 1. Schema và bàn giao | Khối `freshness`, `contract_version: "1.2"`; đọc/ghi kho cá thể, kho đếm trả mã 2; bàn giao trong `day`, id tăng xuyên pha và Ngày; HUD độ tươi; `CHANGELOG.md` | `chonoi/items.py` (mới), `chonoi/inventory.py`, `game.contract.json`, `chonoi/contract.py`, `chonoi/sim/day.py`, `chonoi/runner.py`, `chonoi/web/`, `CHANGELOG.md` | `tests/test_p3_inventory.py` |
| **Tâm** | 2. Độ tươi buổi sáng | Giỏ chứa cá thể, cấp id khi hái/bắt, hao 0.5/s từ bước sau, `spoiled` location `hold`; `lost` là mảng cá thể LIFO; `gather_end.inventory` schema mới | `chonoi/sim/gather.py`, `chonoi/sim/fish.py` | `tests/test_p3_gather.py` |
| **Nga** | 3. Độ tươi ở quán | Kho cá thể, hao 0.25/s, `spoiled` location `stock`; giữ chỗ theo id, nhả và giữ lại một lần, `unfulfillable`; giá theo độ tươi; `cook_started.items`; kiểm scenario v1.2 | `chonoi/sim/quan.py`, `chonoi/scenario.py` | `tests/test_p3_quan.py` |
| **Huyền** | 4. Migration và kiểm chứng | Đổi fixture P1–P2 sang schema mới và ghi lý do; kiểm `lost` của quái; smoke ngưỡng 30, smoke file và `day`; regression; ma trận AC-P3 | `chonoi/sim/monsters.py`, `tests/` còn lại, `docs/verification/phase-3.md`, `docs/proof/phase-3/` | `tests/test_p3_smoke.py` |

Tài liệu giữ nguyên chủ cũ: Tâm ghi `docs/clarify.md`, Nga ghi `docs/standup.md`, `docs/retro.md`, `docs/ai-usage-log.md`.

### Thứ tự tích hợp để `main` luôn chạy được

| Mốc | Việc | Người |
|---|---|---|
| 1:55–2:02 | Cả nhóm `git pull`, đọc ticket, chốt giao diện bên dưới và ghi quyết định đổi schema vào `docs/adr/` | Cả nhóm, Phương ghi |
| Trước 2:05 | Đẩy `chonoi/items.py`. Contract **vẫn giữ 1.1** để `main` không đỏ | Phương |
| 2:05–2:15 | Tâm, Nga làm trên nhánh riêng; Huyền chuẩn bị fixture v1.2 | Tâm, Nga, Huyền |
| 2:15 | Smoke bàn giao kho trên bản tích hợp, standup, điều người sang lát trễ | Huyền, Nga ghi |
| 2:15–2:22 | Gộp `gather`, `quan`, fixture trong **một lần** rồi bật `contract_version: "1.2"` | Phương |
| 2:22–2:27 | Smoke hai tiến trình và `day`, regression, chốt CHANGELOG và bằng chứng | Huyền, Phương |
| Trước 2:30 | Gắn và đẩy tag `phase-3` | Phương |

### Giao diện chốt giữa các lát

- **`chonoi/items.py` (Phương):** lưu độ tươi bằng số nguyên, 240 đơn vị mỗi điểm. Gather trừ 2 đơn vị/tick, quán trừ 1 đơn vị/tick, ươn khi dưới 7200. Có hàm tạo cá thể, đọc/xuất `{id, kind, fresh}`, hao tươi và trả danh sách vừa ươn theo id.
- **Id cá thể:** dùng chung `IdAllocator` với tiền tố `I`, nên id tăng liên tục xuyên pha và Ngày.
- **`gather` → `day` → `quan`:** truyền nguyên danh sách cá thể trong cùng tick, không hao thêm.
- **`monsters.py` (Huyền):** tiếp tục `pop` từ `player.hold`, nên `lost` tự là mảng cá thể theo LIFO.
- **`scenario.py` (Nga):** Phương gửi hàm kiểm cá thể từ `items.py`, Nga dùng cho `gather.hold`, `quan.stock`, `customers[].reserved`.

## Phân công Phase 4 (TICKET-04, Test Contract v1.3, hạn tag và Release 3:00)

Phạm vi: chỉ làm **lõi**. Nhóm 4 người không bắt buộc làm bảng xếp hạng và phụ đề SFX. Mỗi file vẫn chỉ có một người sửa.

**Điều kiện trước khi vào Phase 4:** gộp `p3-gather-fresh`, bật `contract_version: "1.2"`, toàn bộ test xanh, gắn tag `phase-3`.

| Người | Vai | Việc phải giao | File sở hữu trong Phase 4 | Test của lát |
|---|---|---|---|---|
| **Phương** | Release/Integrator, cảnh báo | Contract v1.3, khai `bench_cmd`, `soak_cmd`; kế hoạch D1–D5 lặp ở Ngày 6–10; ba cảnh báo bằng chữ hoặc biểu tượng, chế độ tương phản cao; `CHANGELOG.md`, release notes; tag `phase-4`, Release `v1.0.0` | `game.contract.json`, `chonoi/contract.py`, `chonoi/headless.py`, `chonoi/sim/day.py`, `chonoi/web/`, `CHANGELOG.md`, `docs/release-notes-v1.0.0.md` (mới) | `tests/test_p4_contract.py` |
| **Tâm** | Đóng gói | Thử clone sạch, chạy bằng tối đa 3 lệnh; script tạo bản đóng gói; README đủ môi trường, điều khiển, lệnh test, headless, bench; rà `LICENSE`, `CREDITS.md` | `tools/package_release.py` (mới), `README.md`, `LICENSE` (mới), `CREDITS.md`, `docs/clarify.md` | `tests/test_p4_package.py` |
| **Nga** | Soak, điều phối retro | `soak_cmd` chạy 10 Ngày bằng bot tất định, xuất `soak.json`; rà hành động P2; tổng hợp đóng góp từng người | `chonoi/soak.py` (mới), `docs/retro.md`, `docs/standup.md`, `docs/ai-usage-log.md` | `tests/test_p4_soak.py` |
| **Huyền** | Bench/QA | `bench_cmd` có render 1280×720, làm nóng 3 s, đo 30 s, xuất đúng 5 trường; regression P1–P3; ma trận AC-P4 và artifact | `chonoi/bench.py` (mới), `tests/` còn lại, `docs/verification/phase-4.md`, `docs/proof/phase-4/` | `tests/test_p4_bench.py` |

Việc của **mọi người** trước 2:55: viết hoặc cập nhật `docs/members/<handle>.md` (≤ 200 từ), nêu phần mình làm, đã giúp ai, AI sai ở đâu, bài học, có dẫn commit. Phương hiện chưa có file này.

### Thứ tự và phụ thuộc

| Mốc | Việc | Người |
|---|---|---|
| 2:30–2:33 | `git pull`, chốt tham số `bench_cmd`, `soak_cmd` và cách bench mở phần render | Cả nhóm |
| Trước 2:35 | Đẩy contract v1.3 và cho `day` chạy quá 5 Ngày | Phương |
| 2:33–2:45 | Làm song song bench, soak, cảnh báo, đóng gói | Cả nhóm |
| 2:45 | Standup, điều người sang lát trễ. **Khóa tính năng** sau mốc này | Nga ghi |
| 2:45–2:52 | Thử clone sạch, regression, lưu `bench.json`, `soak.json`, retro và phản tư | Tâm, Huyền, Nga |
| 2:52–2:55 | Chốt commit bàn giao trên `main`, tạo bản đóng gói từ đúng commit đó | Phương, Tâm |
| Trước 3:00 | Đẩy tag `phase-4`, công bố Release `v1.0.0` cùng commit, đính kèm bản đóng gói | Phương |

### Giao diện chốt giữa các lát

- **`bench_cmd`:** `--seed <int> --duration <giây> --out <bench.json>`, xuất `avg_fps`, `p1_low_fps`, `frames`, `measured_s`, `load_ms`.
- **`soak_cmd`:** `--seed <int> --days <N> --out <soak.json>`, xuất `days`, `days_completed`, `crashes`, `results`, `duration_s`. Mỗi `results[]` có `day`, `earned`, `reputation`, `score` lúc Shop đóng.
- **`chonoi/soak.py` → `DaySim` (Nga → Phương):** soak gọi trực tiếp `DaySim`, không đi qua giới hạn `--days` 1–5 của headless.
- **`chonoi/bench.py` → `chonoi/web/` (Huyền → Phương):** bench dùng đúng cảnh `gather` mặc định, Út Sen đứng yên ở bến. Cần thêm móc đo trong trang thì báo Phương.
- **Sau 2:45:** chỉ sửa lỗi. Mọi thay đổi trên `main` phải chạy lại regression.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: … (nhóm điền)
- Khi bất đồng về thiết kế: mỗi bên nói 2 phút, không xong thì Phương quyết và ghi lý do vào `docs/adr/`.
- Khi ai đó trễ hoặc vướng quá 10 phút: báo ngay trong kênh, người dự phòng vào làm cặp.
- Giờ standup giữa phase: 0:30, 1:20, 2:15, 2:45 (mỗi lần tối đa 3 phút, Nga ghi).
- Cách đọc code của nhau: Tâm và Nga đọc chéo phần luật, Huyền đọc UI của Phương, Phương đọc test của Huyền.
- Cách làm việc với Git: nhánh ngắn theo lát rồi PR vào `main`, chạy test trước khi gộp, Phương gộp và là người duy nhất gắn tag.
