# duongthuyen — phản tư cá nhân

- Tôi đã làm: kiểm tính tất định và ma trận Phase 1 ([`5a4fe5c`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/5a4fe5c)); xây Cá Sấu và regression Phase 2 ([`ee2ee05`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/ee2ee05)); chuẩn bị migration fixture Phase 3, kiểm LIFO cá thể, ngưỡng 30 và file kho v1.2. Tôi duy trì ma trận và proof từng phase; regression hiện tại đạt 92/92.
- Tôi đã review: [`game.contract.json`](../../game.contract.json), giao diện tích hợp trong [`TEAM.md`](../../TEAM.md), schema cá thể ở [`chonoi/items.py`](../../chonoi/items.py) và các test gather/day trước khi viết fixture QA.
- AI sai ở đâu và tôi phát hiện thế nào: bản Cá Sấu đầu dùng schema tạm và làm tròn lượng đồ rơi lên. Khi contract v1.1 và test tích hợp xuất hiện, tôi đối chiếu ticket, sửa sang waypoint thật, recoil 60 bước và `floor(n/2)`.
- Điều tôi học được: nên tách unit test không phụ thuộc để làm song song, nhưng chỉ kết luận đạt sau khi chạy headless trên contract đã tích hợp; proof phải ghi đúng commit và blocker.
