# Bằng chứng benchmark Phase 4

- Ngày: 2026-11-21 (Asia/Bangkok)
- Code benchmark: `4bc634e`
- UI được đo: `2587be3`
- Trình duyệt: Google Chrome 157.0.8103.79, headless
- Cảnh: gather mặc định, seed 1, Út Sen đứng ở bến
- Viewport: 1280×720, device scale factor 1

## Lệnh

```bash
python3 -m chonoi.bench --seed 1 --duration 30 --out docs/proof/phase-4/bench.json
```

Benchmark dùng đúng `chonoi/web/index.html` và API state của `LiveGame`. Browser báo viewport về harness; nếu kích thước cửa sổ và viewport khác nhau, harness hiệu chỉnh rồi mới bắt đầu 3 giây làm nóng. Sau đó số frame được lấy từ `requestAnimationFrame` trong đủ khoảng đo.

## Kết quả

| Chỉ số | Giá trị |
|---|---:|
| `avg_fps` | 13,569 |
| `p1_low_fps` | 8,351 |
| `frames` | 408 |
| `measured_s` | 30,068 |
| `load_ms` | 162,1 |

Artifact máy đọc: [`bench.json`](bench.json). Kết quả hợp lệ về contract nhưng cho thấy renderer chi tiết hiện có rủi ro hiệu năng; QA không đặt ngưỡng đạt khi ticket chưa quy định ngưỡng FPS.
