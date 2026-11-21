# Standup giữa phase (mỗi người một dòng, 2–3 phút)

| Phase | Người | Đã xong | Sắp làm | Vướng gì |
|---|---|---|---|---|
| 1 | Nga | Đọc PRD-0 bản đầy đủ; chỉnh vòng đời đơn, payload món, thứ tự timer/tương tác/đóng ca và kiểm mâu thuẫn scenario | Nhờ QA đối chiếu AC khách/bếp/phục vụ và xác nhận event | Không có |
| 2 | Nga | Lọc thực đơn theo kế hoạch ngày; kiểm scenario gather/quan/day; phần quán được gộp trong tag `phase-2` | Hoàn tất; đối chiếu lại regression trên main | Không còn blocker Phase 2 |
| 2 | Nga | Ráp cá, Cá Sấu vào `gather`; 73/73 test; smoke `day` 1 và 5 Ngày | Chơi thử trên trình duyệt, gắn tag `phase-2` | HUD chưa được xác nhận trên trình duyệt |
| 3 | Nga | Thêm kho cá thể trong quán, hao tươi và `spoiled`; giữ chỗ theo ID, thử giữ lại một lần, tính giá theo độ tươi và kiểm fixture v1.2; regression hiện có 92/92 và smoke luật quán đạt | Ráp khi gather chuyển sang cá thể; chạy `tests/test_p3_quan.py` khi Huyền đưa vào | Adapter `items.py`/`DaySim` đã có, nhưng contract vẫn v1.1 và gather còn kho đếm; chưa thể smoke end-to-end |
| 3 | Nga | Gộp gather, quan, bật v1.2; 115/115 test; smoke file và `day` | Gắn tag `phase-3`, sang Phase 4 | HUD độ tươi chưa chơi thử trên trình duyệt |
