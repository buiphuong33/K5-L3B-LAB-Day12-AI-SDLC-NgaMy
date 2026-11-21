# Changelog
## Unreleased

### Phase 3 (Test Contract v1.2 — "Mùa Nước Nổi")
- **Breaking — file kho:** kho đếm `{"items":{"ca_loc":1}}` → kho cá thể
  `{"items":[{"id":"I1","kind":"ca_loc","fresh":100}]}`, sắp theo id. Với contract v1.2, file kho đếm,
  sai schema, kind lạ, id trùng, `fresh` ngoài [0,100] → **mã 2**. Kho rỗng: `{"items":[]}`.
- **Breaking — scenario:** `gather.hold`, `quan.stock` là mảng cá thể; `customers[].reserved` là mảng id cá thể.
- **Breaking — JSONL:** `hold`, `stock`, `reserved`, `cook_started.items`, `lost` là cá thể; event mới `spoiled`.
- **Breaking — giá:** `base_price = floor(giá niêm yết × trung bình fresh / 100)`, boa tính trên giá đã chốt.
- Thêm `tuning.freshness` {initial 100, gather 0.5/s, quan 0.25/s, ươn < 30}; `chonoi/items.py` (độ tươi chính xác
  bằng `Fraction`); id cá thể họ `I` tăng xuyên pha và Ngày; bàn giao `day` trong cùng tick, không hao thêm.
- HUD: thanh độ tươi trên từng ô giỏ, gạch chéo hàng ươn, độ tươi thấp nhất / số hàng ươn ở kho quán.
- **Cách cập nhật fixture:** mảng kind `["ca_loc","bong_sung"]` → `[{"id":"I1","kind":"ca_loc","fresh":100},
  {"id":"I2","kind":"bong_sung","fresh":100}]`; object đếm `{"ca_loc":2}` → hai cá thể có id riêng;
  `reserved: {"ca_loc":1}` → `reserved: ["I1"]` (id phải nằm trong `quan.stock`, chưa ươn).

### Phase 2 (Test Contract v1.1)
- **Breaking:** `fish_initial` là số đàn (8), vị trí lấy từ điểm sinh theo seed.
- Thêm cá bơi và sinh cá, Cá Sấu, Máu và ngất do quái, 2 bếp, 4 bàn, 6 món.
- Thêm `--mode day`, kế hoạch 5 Ngày, Shop, nâng cấp và pause.
