# QA baseline Phase 1

- Ngày: 2026-11-21 (Asia/Bangkok)
- Người thực hiện: Dương Thị Huyền - 2A202604077
- Phạm vi: đọc contract/README, lập ma trận truy vết, bổ sung kiểm tất định cho `gather` và `quan`.

## Lệnh

```powershell
$env:PYTHONPATH='tests;.'
.\python3.exe -m unittest discover -s tests -v
```

## Kết quả

- Python: 3.10.1.
- Tổng: 33 test.
- Đạt: 33.
- Trượt/lỗi: 0.

Máy không ánh xạ được lệnh `python3`, nên lần chạy cục bộ dùng bản sao tạm của executable Python 3.10 với `PYTHONHOME` trỏ về runtime đã cài. Các tiến trình headless vẫn được gọi bằng đúng literal `python3` trong `game.contract.json`; hai file runtime tạm không được giữ trong repo.

Test mới `tests/test_determinism.py` xác nhận hai lần chạy cùng seed cho cả `gather` và `quan` giống từng byte. Các AC công khai trong ma trận Phase 1 đều đạt ở trạng thái hiện tại.

## Việc còn mở

- `tools/check_team.py` chưa đạt vì GitHub handle của Phương, Tâm và Huyền vẫn để trống. Không tự đoán handle; từng thành viên cần cung cấp để Phương cập nhật `TEAM.md`.
- Hai skill trong `tools/skills/` đã được rà cấu trúc và YAML frontmatter thủ công. `quick_validate.py` của Codex chưa chạy được vì Python cục bộ thiếu package `yaml` (PyYAML).
