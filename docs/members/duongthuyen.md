# duongthuyen — phản tư cá nhân

- Tôi đã làm: bổ sung kiểm tra tính tất định cho cả `gather` và `quan`, hoàn thiện ma trận truy vết Phase 1, lưu bằng chứng QA và tạo hai skill kiểm thử dùng chung. Commit: [`5a4fe5c`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/5a4fe5c8cbc757707ee4c2471c20af5ea9b888b3).
- Tôi đã review: hướng dẫn trong [`README.md`](../../README.md), Test Contract trong [`game.contract.json`](../../game.contract.json), smoke test công khai trong [`tests/test_smoke_p1.py`](../../tests/test_smoke_p1.py) và ranh giới sở hữu file trong [`TEAM.md`](../../TEAM.md).
- AI sai ở đâu và tôi phát hiện thế nào: AI ban đầu kết luận máy không có Python vì `python`, `python3` và launcher đều lỗi. Tôi kiểm tra các thư mục cài đặt, tìm thấy Python 3.10, chạy lại toàn bộ suite và xác nhận 33/33 test đạt.
- Điều tôi học được: bằng chứng phải phản ánh lệnh đã chạy thật; kiểm tra tính tất định cần so sánh byte cho mọi mode, không chỉ kiểm cấu trúc JSON.
