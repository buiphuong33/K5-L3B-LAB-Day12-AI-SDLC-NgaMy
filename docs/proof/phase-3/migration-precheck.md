# Precheck migration fixture Phase 3

- Ngày: 2026-11-21 (Asia/Bangkok)
- Nền: `origin/main` tại `d625ac6`
- Nhánh ghép tạm: `origin/p3-gather-fresh` tại `8a7fc37`
- Cách kiểm: worktree tạm, `git merge --no-commit --no-ff`, không thay đổi lịch sử `main`.

## Phát hiện

Bản ghép chạy 103 test: 9 trượt, 1 lỗi, 2 bỏ qua. Mười lỗi đều chỉ ra fixture P1–P2 còn dùng giỏ chuỗi hoặc assertion kho đếm. Các nhóm bị ảnh hưởng: starter unit, luật gather Phase 1, smoke kho và test Cá Sấu Phase 2.

## Xử lý

- Thêm helper fixture chọn schema theo `contract_version`.
- Khi v1.2, giỏ dùng cá thể có id liên tục và `fresh: 100`; assertion LIFO đọc `kind` từ cá thể.
- Giữ nhánh chính v1.1 chạy được cho tới lần tích hợp nguyên tử do `TEAM.md` quy định.
- Thêm smoke độc lập cho ngưỡng 30 và file kho v1.2.

Sau thay đổi, `main` v1.1 đạt 92/92. Việc xác nhận toàn bộ fixture ở v1.2 và smoke `gather -> quan`/`day` còn chờ gather, quan và contract được nhập cùng lần.

Precheck lần hai ghép commit QA `e4580e1` với nhánh gather, tạm bật contract 1.2 trong worktree và chạy các lớp không phụ thuộc quán/scenario: 21/21 đạt (starter unit, smoke migration và 11 unit gather). Worktree đã được xóa sau khi kiểm.
