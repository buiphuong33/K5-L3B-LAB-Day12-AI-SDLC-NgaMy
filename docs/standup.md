# Standup giữa phase (mỗi người một dòng, 2–3 phút)

| Phase | Người | Đã xong | Sắp làm | Vướng gì |
|---|---|---|---|---|
| 1 | Nga | Đọc PRD-0 bản đầy đủ; chỉnh vòng đời đơn, payload món, thứ tự timer/tương tác/đóng ca và kiểm mâu thuẫn scenario | Nhờ QA đối chiếu AC khách/bếp/phục vụ và xác nhận event | Không có |
| 2 | Nga | Mở rộng `QuanSim` để nhận danh sách món theo kế hoạch; kiểm scenario gather/quan/day theo schema v1.1, gồm nguyên liệu động, quái, day plan và kho bàn giao | Tích hợp với `game.contract.json` v1.1 và `day.py`; chạy lại khi Phương/Huyền đưa phần giao diện và fixture vào repo | Contract hiện trong repo vẫn là v1.0; chưa có `day.py` hoặc `tests/test_p2_quan.py` nên cần smoke tích hợp sau khi các phần phụ thuộc được gộp |
| 2 | Nga | Ráp cá, Cá Sấu vào `gather`; 73/73 test; smoke `day` 1 và 5 Ngày | Chơi thử trên trình duyệt, gắn tag `phase-2` | HUD chưa được xác nhận trên trình duyệt |
