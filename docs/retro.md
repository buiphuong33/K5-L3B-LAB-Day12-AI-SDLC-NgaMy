# Retro nhóm

## Ghi nhận khi bàn giao phần Nga (Phase 1)
- Điều tốt: luật quán và kiểm scenario nằm trong đúng hai file được phân công; lựa chọn món dùng RNG có seed, khách có ID ổn định.
- Điều cần cải thiện: luật ban đầu được suy ra từ TODO/tuning vì bản HTML đầu tiên chỉ là vỏ lab; sau đó đã căn chỉnh theo PRD-0 mục D–F.
- Bằng chứng: bộ test repo 32/32 đạt; smoke trực tiếp xác nhận nấu → chín → bê → phục vụ → trả tiền, phục vụ/thu tiền ở tick đóng ca và các fixture mâu thuẫn bị từ chối.
- Hành động: QA đối chiếu AC/event cho reserved/assigned/served/unfulfillable, hết kiên nhẫn và đóng ca.

## Phase 2 (nhanh)
- Điều tốt: `QuanSim` nhận danh sách món theo kế hoạch ngày và dùng menu/tuning hiện hành cho số bếp, bàn, món và nguyên liệu; kiểm scenario mở rộng theo dữ liệu thay vì khóa cứng danh sách P1.
- Điều tệ: lúc làm lát Nga, repo vẫn có `contract_version: 1.0`; chưa thể chạy scenario `day` theo v1.1 hoặc kiểm smoke cùng `day.py`.
- Điều rút ra khi tích hợp: `fish.py` và `monsters.py` viết trước khi đọc kỹ ticket nên phải sửa lại lúc ráp vào `gather`.
- 1 hành động cho Phase 3 (Nga): khi contract v1.1 và `day.py` được gộp, chạy smoke mở quán với kho bàn giao và xác nhận món ngoài kế hoạch không xuất hiện trong lựa chọn khách.

## Phase 3 (nhanh)
- Điều tốt: dùng `Freshness`, `freshest`, `decay` và `fresh_price` chung để so ngưỡng 30 và floor giá chính xác; đơn giữ cá thể tươi nhất theo ID và có một lần thử giữ lại khi hàng ươn.
- Điều tệ: adapter và `DaySim` cá thể đã được gộp, nhưng contract vẫn v1.1, gather còn xuất kho đếm và chưa có test quán P3; chưa xác nhận được tích hợp end-to-end.
- 1 hành động cho Phase 4 (Nga): sau khi gộp adapter v1.2, đối chiếu snapshot/event của `stock`, reservation và `cook_started.items` với smoke hai tiến trình.

## Phase 3 (nhanh, về lần đổi kho)
- Điều tốt: giữ contract 1.1 trong lúc chuyển nên `main` không đỏ; ADR 0001 chốt schema trước khi các lát làm song song.
- Điều tệ: lỗi chỉ lộ khi bật v1.2 trên bản gộp, vì mỗi lát chỉ kiểm riêng.
- 1 hành động cho Phase 4 (Huyền): chạy smoke trên bản tích hợp ngay khi có hai lát trở lên, không chờ cuối phase.

## Phase 4 (cuối)
- **Hành động Phase 2:** tag `phase-2` có trong repo; standup vẫn ghi chưa xác nhận HUD qua chơi thử trình duyệt. Hành động chơi thử còn mở, không coi là hoàn tất chỉ vì mã HUD có mặt.
- **Hành động Phase 3 của Nga:** hoàn tất sau khi v1.2 được gộp; smoke file và `day` được ghi trong [`docs/proof/phase-3/integration.md`](proof/phase-3/integration.md).
- **Điều tốt:** soak gọi trực tiếp `DaySim`, dùng seed cố định, chạy 10 ngày trong khoảng 4 giây; D1–D5 lặp lại chính xác cho D6–D10. Artifact ghi 10/10 ngày, 0 crash. Fixture gather cấp đúng nguyên liệu kế hoạch rồi bot tự điều khiển bếp/phục vụ; đây là soak luồng ngày, không đo kỹ năng tự tìm cá.
- **Lệnh tái tạo:** `python3 -m chonoi.soak --seed 17 --days 10 --out docs/proof/phase-4/soak.json`.
- **Điều cần cải thiện:** ban đầu bot dùng lại lượng nguyên liệu D1 cho cả buổi, không khớp kế hoạch từng ngày. So sánh fixture với `day_plan` phát hiện lỗi; runner hiện thay fixture trước khi mở mỗi ngày.
- **Đóng góp đã bàn giao:** Phương — tích hợp contract, `DaySim`, giao diện và release; Tâm — luật gather, PO và đổi kho ngày; Huyền — QA, regression, fixture và proof; Nga — luật quán/scenario, kiểm tích hợp, soak và điều phối retro. Căn cứ: `TEAM.md`, lịch sử commit và hồ sơ từng thành viên.
- **AI sai và cách phát hiện:** lần chạy đầu hoàn thành 10 ngày nhưng dùng sai fixture lặp lại. Test so lượng mỗi nguyên liệu với kế hoạch của từng ngày đã bắt lỗi trước khi tạo artifact cuối.
- **Bài học:** kiểm cả dữ liệu đầu vào chuyển giữa các ngày lặp, không chỉ trạng thái kết thúc và số ngày hoàn thành.
- **Số liệu AI:** token theo người không được công cụ ghi lại; không suy đoán con số.
