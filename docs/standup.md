# Standup giữa phase (mỗi người một dòng, 2–3 phút)

| Phase | Người | Đã xong | Sắp làm | Vướng gì |
|---|---|---|---|---|
| 1 | Nga | Đọc PRD-0 bản đầy đủ; chỉnh vòng đời đơn, payload món, thứ tự timer/tương tác/đóng ca và kiểm mâu thuẫn scenario | Nhờ QA đối chiếu AC khách/bếp/phục vụ và xác nhận event | Không có |
| 2 | Nga | Lọc thực đơn theo kế hoạch ngày; kiểm scenario gather/quan/day; phần quán được gộp trong tag `phase-2` | Hoàn tất; đối chiếu lại regression trên main | Không còn blocker Phase 2 |
| 2 | Nga | Ráp cá, Cá Sấu vào `gather`; 73/73 test; smoke `day` 1 và 5 Ngày | Chơi thử trên trình duyệt, gắn tag `phase-2` | HUD chưa được xác nhận trên trình duyệt |
| 3 | Nga | Gộp gather, quán, bật v1.2; 115/115 test; smoke file và `day` | Hoàn tất; tag `phase-3` đã có | HUD độ tươi chưa chơi thử trên trình duyệt |
| 4 | Nga | Thêm `chonoi.soak`, bot tất định chạy 10 ngày; lưu `docs/proof/phase-4/soak.json`; 4 test soak và regression 119/119 đạt | Bàn giao artifact cho QA/release | Hành động P2: tag `phase-2` đã có; HUD chưa được xác nhận bằng chơi thử trình duyệt |
