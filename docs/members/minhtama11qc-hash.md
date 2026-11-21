# minhtama11qc-hash (Phạm Minh Tâm) — phản tư cá nhân

- **Tôi đã làm:** module `sim/gather` và vai PO (giữ `docs/clarify.md`).
  - Lát 1: oxy, ngạt, Máu, ngất, giỏ LIFO. Commit [`29d6750`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/29d6750), đã gộp qua PR [#1](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/pull/1).
  - Lát 2: làm ở PR [#2](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/pull/2) nhưng đã đóng. Nhóm dùng bản của Nga ([`dc106c7`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/dc106c7)), vì bản đó bám đúng PRD-0.
  - Ghi các giả định của gather vào `docs/clarify.md`.
- **Tôi đã review:** chưa review PR của ai. Theo thỏa thuận nhóm, tôi sẽ đọc chéo phần luật `quan` của Nga.
- **AI sai ở đâu và tôi phát hiện thế nào:**
  - Khi chưa có PRD-0, AI tự đoán `data` của các sự kiện (`oxygen_empty`, `faint`, `hold_full`...) và hồi chiêu khi bắt trượt. Đối chiếu với PRD-0 thì thấy sai.
  - Script kiểm do AI viết gọi sai API `InputPlayer`, và có một ca FAIL chỉ vì cho chạy quá ít tick. Khi in từng tick ra thì thấy code đúng.
  - AI gắn `@Huyền` trong PR, trong khi đó không phải tên đăng nhập GitHub thật.
- **Điều tôi học được:** PO phải đọc đặc tả trước khi để AI code. Test xanh chưa chứng minh được luật đúng.
