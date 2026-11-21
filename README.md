# Quán Ăn Chợ Nổi — nhóm NgaMy (v1.0.0)

Game 2D chơi trên trình duyệt: buổi sáng Út Sen **lặn bắt cá, hái rau** trên sông (oxy, Máu, Cá Sấu, độ tươi),
buổi tối **mở quán** nấu và phục vụ khách, cuối Ngày ghé **Shop** mua nâng cấp. Một lượt chuẩn gồm 5 Ngày.
Sản phẩm của Lab Day 12 — AI SDLC (4 phase, Test Contract v1.3). Thành viên và phân công: [`TEAM.md`](TEAM.md).

## Chạy nhanh

Từ clone sạch trên macOS hoặc Linux, **3 lệnh**:

```bash
git clone https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy.git
cd K5-L3B-LAB-Day12-AI-SDLC-NgaMy
python3 -m chonoi.live --mode day
```

Lệnh cuối in địa chỉ (mặc định `http://127.0.0.1:8000/`); mở địa chỉ đó bằng trình duyệt để chơi.
Không cần cài thêm gói nào. Bản đóng gói đính kèm GitHub Release `v1.0.0` chạy giống hệt: giải nén,
`cd` vào thư mục rồi chạy lệnh thứ 3.

Tùy chọn của `chonoi.live`: `--mode gather|quan|day`, `--days 1..5`, `--seed N`, `--port N` (0 = cổng ngẫu nhiên).
Chơi riêng hai buổi: `python3 -m chonoi.live --mode gather --inventory-out kho.json` (cập bến để ghi kho),
rồi `python3 -m chonoi.live --mode quan --inventory kho.json`.

## Yêu cầu môi trường

- **Python 3.10 trở lên**, chỉ dùng thư viện chuẩn (không `pip install`). Lệnh trong README dùng `python3`.
- **Trình duyệt** hiện đại (Chrome, Firefox, Safari, Edge) để chơi bản có giao diện.
- **Chromium / Google Chrome / Microsoft Edge** để chạy benchmark: bench mở game ở chế độ headless và tự tìm
  lệnh `chromium`, `chromium-browser`, `google-chrome`, `chrome`, `msedge` hoặc đường dẫn cài đặt mặc định trên
  macOS/Windows. Firefox/Safari không dùng được cho bench.
- **git** để clone và để chạy script đóng gói.
- Đã thử trên Windows 11 (Python 3.13): dùng `python` thay `python3` nếu máy không có lệnh `python3`, và
  `PYTHONPATH=tests;.` thay cho `tests:.` khi chạy test.

## Điều khiển

| Phím | Tác dụng |
|---|---|
| WASD / mũi tên | Bơi (buổi sáng) / đi lại (quán) |
| E | Hái ở mặt nước, cập bến khi ở vùng bến; ở quán: nấu, lấy món, phục vụ |
| Space | Bắt cá khi đang lặn |
| Esc / P | Tạm dừng; khi tạm dừng, M về menu |
| Enter | Mode day: bắt đầu / qua màn; trong Shop: đóng Shop |
| 1 / 2 | Trong Shop: mua Bình oxy / Áo phao |
| R | Chơi lại |

**Điểm:** `earned + 100 × floor(uy tín)`, với `earned` là tổng tiền thu trong lượt (nghìn đồng).
Nguyên liệu hao độ tươi (giỏ 0.5/s, kho quán 0.25/s); dưới 30 là ươn, không dùng nấu được; giá món
tính theo độ tươi trung bình của nguyên liệu.

## Chạy test

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

Gồm smoke test hộp đen của Test Contract, regression P1–P3 và test từng lát P4 (`tests/test_p4_*.py`).

## Headless

Chế độ không giao diện theo Test Contract (dùng để chấm tự động, ghi JSONL tất định: cùng seed → giống từng byte):

```bash
python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out out.jsonl
python3 -m chonoi.headless --mode gather --seed 1 --ticks 12000 --out g.jsonl --inventory-out kho.json
python3 -m chonoi.headless --mode quan --seed 1 --ticks 600 --inventory kho.json --out q.jsonl
python3 -m chonoi.headless --mode day --days 5 --seed 1 --ticks 200000 --out day.jsonl
```

Tham số khác: `--scenario <file.json>`, `--inputs <file.json>`, `--snapshot-every N`. Đầu vào sai trả mã 2.
Lệnh chuẩn khai trong [`game.contract.json`](game.contract.json) (`headless_cmd`, `run_cmd`).

## Benchmark

Lệnh khai ở `bench_cmd` trong `game.contract.json` (cảnh buổi sáng mặc định, seed 42, cửa sổ 1280×720,
làm nóng 3 s rồi đo 30 s):

```bash
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json
```

Cần Chromium, Chrome hoặc Edge (xem **Yêu cầu môi trường**). Nếu trình duyệt nằm ở chỗ khác, chỉ đường dẫn bằng
biến môi trường, ví dụ `CHONOI_BROWSER=/usr/bin/chromium python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json`.

`bench.json` có `avg_fps`, `p1_low_fps`, `frames`, `measured_s`, `load_ms`. Kết quả đo trên commit phát hành:
[`docs/proof/phase-4/`](docs/proof/phase-4/).

**Soak** (10 Ngày headless bằng bot tất định), lệnh khai ở `soak_cmd`:

```bash
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
```

`soak.json` có `days`, `days_completed`, `crashes`, `results`, `duration_s`.

## Đóng gói bản phát hành

```bash
python3 tools/package_release.py --ref phase-4 --check
```

Tạo `dist/quan-an-cho-noi-v1.0.0.zip` (+ `.sha256`) bằng `git archive` từ đúng commit `--ref`, rồi giải nén
vào thư mục tạm và chạy thử headless từ bản đó. File zip này đính kèm GitHub Release `v1.0.0`.

## Sáng tạo của nhóm

Nhóm 4 người, ưu tiên làm đúng lõi; không làm mục mở rộng (bảng xếp hạng, phụ đề SFX, dòng nước lũ,
khách đặt trước). Phần tự thêm trên giao diện (HUD độ tươi, màn chuyển Ngày) không đổi kết quả headless.

## Tài liệu của nhóm

- Quy ước cho agent AI: [`AGENTS.md`](AGENTS.md) · skill nhóm: [`tools/skills/`](tools/skills/)
- Hợp đồng tích hợp: [`docs/contracts/`](docs/contracts/) · quyết định: [`docs/adr/`](docs/adr/)
- Kiểm chứng: [`docs/verification/`](docs/verification/), [`docs/proof/`](docs/proof/)
- Làm rõ yêu cầu: [`docs/clarify.md`](docs/clarify.md) · nhật ký AI: [`docs/ai-usage-log.md`](docs/ai-usage-log.md)
- Standup, retro, phản tư: [`docs/standup.md`](docs/standup.md), [`docs/retro.md`](docs/retro.md), [`docs/members/`](docs/members/)
- Thay đổi theo phase: [`CHANGELOG.md`](CHANGELOG.md) · giấy phép: [`LICENSE`](LICENSE) · nguồn: [`CREDITS.md`](CREDITS.md)

## Về lab

Đề và khung starter: [VinUni-AI20k/K5-L3B-LAB-Day12-AI-SDLC](https://github.com/VinUni-AI20k/K5-L3B-LAB-Day12-AI-SDLC)
(chi tiết khung: [`docs/STARTER.md`](docs/STARTER.md)). Yêu cầu từng phase trên lab board
[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg).
