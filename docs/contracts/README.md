# Hợp đồng tích hợp — Phase 1 (chủ: Phương / Integrator)

Đổi hợp đồng: báo cả nhóm, ghi lý do vào `docs/adr/`, cần Tâm + Nga đồng ý.

## 1. File kho (gather → quan) — PRD-0 mục G

```json
{"items": {"bong_sung": 2, "ca_loc": 1}}
```

| Quy tắc | Nội dung |
|---|---|
| Gốc | Chỉ một khóa `items` |
| `items` | object `kind → số nguyên ≥ 0`; kind ∈ `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung` |
| Lượng 0 | Bên ghi **bỏ khóa**; bên đọc coi kind vắng = 0 |
| Kho rỗng | `{"items":{}}` (cũng là kho khi ngất) |
| Bên đọc (`quan --inventory`) | Sai schema / kind lạ / giá trị âm hoặc không nguyên → **mã 2** |
| Bên ghi (`gather --inventory-out`) | Ghi **đúng 1 lần** khi `gather_end`, nội dung = `data.inventory` của event đó; ghi file tạm rồi thay thế nguyên tử; chạm `--ticks` trước khi xong buổi sáng → không ghi |
| Trần giỏ | Không áp lên kho quán |

Ví dụ hợp lệ: [`inventory.sample.json`](inventory.sample.json). Code đọc/ghi: `chonoi/inventory.py`.

## 2. Giao diện sim ↔ UI

- **UI chỉ đọc snapshot** (`GET /state`, cùng trường với snapshot JSONL mục E) và **chỉ gửi lệnh** `{"move":[x,y],"interact":bool,"catch":bool}` (`POST /input`), `POST /restart`.
- UI không sửa trạng thái, không dùng RNG mô phỏng. Thêm/đổi tên trường snapshot → báo Phương.

| Pha | Trường UI dùng cho HUD |
|---|---|
| gather | `time_left_ticks`, `player.{pos,oxygen_ticks,oxygen_max_ticks,hp,hp_max}`, `hold`, `hold_capacity`, `nodes[]`, `fish[]` |
| quan | `time_left_ticks`, `money`, `reputation`, `score`, `stock`, `customers[].{table_id,dish_id,state,patience_ticks_left,reserved}`, `stoves[].{id,state,dish,cook_ticks_left}`, `hand` |

Kho khả dụng trên HUD = `stock` − tổng `customers[].reserved`.

## 3. Sự kiện (PRD-0 mục E)

| Event | Phát bởi | `data` |
|---|---|---|
| `gather`, `node_regrown` | gather (Tâm) | `node_id,kind,amount` / `node_id` |
| `hold_full` | gather | `action,node_id\|fish_id,required,free` |
| `fish_caught` | gather | `fish_id,kind,yield` |
| `dive`, `surface` | gather | `pos` |
| `oxygen_empty`, `choke`, `faint` | gather | `oxygen_ticks:0` / `hp` / `cause,lost,hp:0` |
| `gather_end` | gather | `reason,inventory` → **đầu vào của quan** |
| `customer_arrived`, `no_dish` | quan (Nga) | `order_id,table_id,dish_id` / `{}` |
| `cook_started`, `dish_ready`, `dish_picked` | quan | `stove_id,order_id,dish_id` (+`items,base_price`) |
| `served`, `paid`, `customer_left` | quan | theo mục E |
| `quan_end` | quan | `reason,money,earned,shift_earned,reputation` |

Người nghe: UI (hiển thị), QA (Huyền) kiểm theo AC.

## 4. Smoke hai tiến trình

```bash
python3 -m chonoi.headless --mode gather --seed 42 --scenario dock.json --inputs dock-inputs.json --ticks 1 --out gather.jsonl --inventory-out catch.json
python3 -m chonoi.headless --mode quan --seed 42 --inventory catch.json --ticks 600 --out quan.jsonl
```
Kỳ vọng snapshot quán tick 0: `stock:{"bong_sung":2,"ca_loc":1}`.
