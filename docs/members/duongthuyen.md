# duongthuyen — phản tư cá nhân

- Tôi đã làm: kiểm tính tất định Phase 1 ([`5a4fe5c`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/5a4fe5c)); xây Cá Sấu và regression Phase 2 ([`ee2ee05`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/ee2ee05)); migration fixture Phase 3; benchmark render 1280×720 và ma trận Phase 4 ([`4bc634e`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/4bc634e)). Regression hiện đạt 120/120.
- Tôi đã giúp Phương đo UI mới bằng Chrome thật và báo rủi ro 13,569 FPS; giúp Tâm, Nga phát hiện sớm fixture/phụ thuộc tích hợp qua các precheck.
- AI sai: ban đầu giả định `--window-size=1280,720` tạo đúng viewport. Tôi bắt lỗi khi browser báo 1262×624, rồi thêm bước hiệu chỉnh và xác nhận lại 1280×720 trước khi đo.
- Tôi học được: benchmark phải đo đúng renderer, commit và thời lượng; kết quả thấp vẫn là bằng chứng hữu ích, không nên che bằng vòng lặp giả hay làm tròn đẹp.
