# Regression Phase 4

- Ngày: 2026-11-21 (Asia/Bangkok)
- Commit code QA: `4bc634e`
- Nền tích hợp: `2587be3`
- Môi trường: Windows, Python 3.10.1

## Lệnh

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

## Kết quả

- Tổng: 120 test.
- Đạt: 120.
- Trượt/lỗi: 0.
- Có 2 `ResourceWarning` từ file test kho Phase 3 chưa đóng file sau khi đọc; không làm thay đổi kết quả.

Regression bao phủ P1–P3 và 5 test contract benchmark Phase 4. Các test contract/soak/package Phase 4 chưa có trên `main` tại thời điểm chạy.
