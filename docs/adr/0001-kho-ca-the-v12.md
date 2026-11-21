# ADR 0001 — Kho cá thể và độ tươi (Test Contract v1.2)

- **Trạng thái:** Đã chốt (Phase 3, 1:55–2:02). Người ghi: Phương.
- **Bối cảnh:** TICKET-03 thay kho đếm bằng kho cá thể có `fresh`; cả gather, quán, day, scenario, file kho và HUD bị ảnh hưởng. Bốn người sửa song song nên cần một điểm chung và thứ tự gộp để `main` không đỏ.

## Quyết định
1. **Một module chung `chonoi/items.py`** (Phương) — dạng nội bộ `{"id","kind","fresh": Fraction}`; hàm `new_item`, `decay` (trả cá thể vừa ươn theo id), `freshest`, `fresh_price`, `from_json`/`to_json`, `list_from_json` (bắt id trùng giữa các nơi chứa).
2. **Độ tươi lưu bằng `Fraction`** thay vì float: 0.5/s = 1/120 mỗi tick, 0.25/s = 1/240 → so ngưỡng 30 và `floor` giá chính xác tuyệt đối (tương đương 240 đơn vị/điểm của ticket, nhưng nhận cả fresh lẻ trong fixture). Xuất JSON là float, đọc lại bằng `Fraction(str(x))`.
3. **Id cá thể** cấp bằng `IdAllocator` chung, tiền tố `I` → tăng xuyên pha và Ngày; kho nạp từ file được `reserve` trước.
4. **Bàn giao trong bộ nhớ** (`day`): gather → quán truyền nguyên list cá thể nội bộ, cùng tick, không hao thêm. File kho chỉ cho hai mode độc lập.
5. **Chọn schema theo `contract_version`** (`inventory.read_inventory(..., version)`): v1.1 đọc kho đếm, v1.2 đọc kho cá thể. Nhờ vậy gộp code mới trước, **bật 1.2 sau cùng**.

## Thứ tự tích hợp
| Mốc | Việc |
|---|---|
| 2:05 | Đẩy `items.py`, `inventory.py` hai phiên bản, khối `freshness`; contract **vẫn 1.1** |
| 2:05–2:15 | Tâm (gather), Nga (quán + scenario) làm trên nhánh, dùng `items.py`; Huyền đổi fixture |
| 2:15–2:22 | Gộp một lần, rồi đổi `contract_version` → `"1.2"` |
| 2:22–2:27 | Smoke file + day, regression, bằng chứng |

## Hệ quả
- Test cũ dùng kho đếm/hold mảng kind phải đổi fixture (Huyền ghi lý do trong commit).
- Kho đếm vẫn đọc được khi contract < 1.2 → chuyển đổi không làm hỏng `main` giữa chừng.
