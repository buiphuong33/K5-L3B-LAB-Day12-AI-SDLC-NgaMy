# Hợp đồng tích hợp (nên chốt sớm; hình thức do nhóm chọn)

Điền trong 15 phút kickoff (hoặc thay bằng một mục trong README / một bảng trên giấy, miễn cả nhóm cùng thống nhất):
1. **Schema file kho** — khớp mục G của PRD-0 (kho ghi khi `gather_end`) + một file kho mẫu hợp lệ: `inventory.sample.json`.
2. **Giao diện giữa `sim/*` và `client/ui`** — trạng thái nào UI được đọc, lệnh nào UI gửi vào.
3. **Danh sách sự kiện** — tên, `data`, ai phát, ai nghe (gather: `gather`, `node_regrown`, `hold_full`, `fish_caught`, `gather_end`...; quan: theo mục E của PRD-0).

Khi đổi hợp đồng sau này: báo cả nhóm và ghi lại lý do (ADR hoặc ghi chú, tùy chọn).

## Đã chốt (Phase 1)

**File kho** (PRD-0 mục G, ví dụ: `inventory.sample.json`): `{"items": {"<kind>": <số nguyên không âm>}}`. `kind` thuộc `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung`; bên ghi bỏ khóa có lượng 0; kho rỗng là `{"items": {}}`. `gather` ghi đúng một lần khi có `gather_end`, ghi nguyên tử; `quan` từ chối file sai schema bằng mã 2.

**Sim và UI:** UI chỉ đọc snapshot JSON theo mục E và gửi vào `move`, `interact`, `catch`. Sự kiện theo bảng ở mục E.
