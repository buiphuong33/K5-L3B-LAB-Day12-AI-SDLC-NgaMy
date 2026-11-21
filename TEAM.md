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

## Phase 2–4

Yêu cầu mở theo mốc giờ trên lab board. Khi phase mở, Tâm đọc yêu cầu, Phương chia việc trong 5 phút theo nguyên tắc: tính năng thuộc module nào thì chủ module đó làm, tính năng mới đặt ở **file mới có đúng một chủ** và ghi thêm vào bảng trên.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: … (nhóm điền)
- Khi bất đồng về thiết kế: mỗi bên nói 2 phút, không xong thì Phương quyết và ghi lý do vào `docs/adr/`.
- Khi ai đó trễ hoặc vướng quá 10 phút: báo ngay trong kênh, người dự phòng vào làm cặp.
- Giờ standup giữa phase: 0:30, 1:30, 2:15, 2:45 (mỗi lần tối đa 3 phút, Nga ghi).
- Cách đọc code của nhau: Tâm và Nga đọc chéo phần luật, Huyền đọc UI của Phương, Phương đọc test của Huyền.
- Cách làm việc với Git: nhánh ngắn theo lát rồi PR vào `main`, chạy test trước khi gộp, Phương gộp và là người duy nhất gắn tag.
