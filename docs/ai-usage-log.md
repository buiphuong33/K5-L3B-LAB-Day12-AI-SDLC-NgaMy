# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| 1 | Nga | Codex / GPT-6 | Đọc PRD-0 bản đầy đủ; chỉnh luật quán và kiểm scenario theo mục D–F; cập nhật ghi chép | Không có số liệu usage trong phiên | Bản HTML đầu tiên chỉ là vỏ lab; sau đó có đủ PRD-0 trong Pasted text.txt. Đã thay các suy đoán ban đầu bằng schema/order lifecycle và thứ tự xử lý ghi trong PRD |
| 1 | Nga | Claude Code / Opus 5.5 | Gộp lát 1, viết lát 2, rà luật theo Test Contract, thêm test và ghi chép | Không đo được | Bản đầu của lát 1 và quán lệch contract ở data sự kiện, `vel`, lý do `paid`; phát hiện bằng cách đối chiếu mục E, F và viết test hộp đen |
| 2 | Nga | Codex / GPT-6 | Mở rộng lọc menu theo kế hoạch ngày, kiểm scenario gather/quan/day theo Ticket-02 và cập nhật standup/retro/log | Không có số liệu usage trong phiên | Contract repo chưa lên v1.1 nên phần day và dữ liệu 6 món chưa thể smoke tích hợp; kiểm tra regression P1 chạy được bằng Python shim tạm cho lệnh `python3` trên Windows |
| 2 | Nga | Claude Code / Opus 5.5 | Ráp cá và Cá Sấu vào gather, viết lại hai module theo TICKET-02, thêm test và bằng chứng | Không đo được | Hai module dựng trước khi có ticket lệch đặc tả (waypoint, recoil, mất nửa giỏ, miền bơi); phát hiện khi đối chiếu mục 1.1–1.2 |
