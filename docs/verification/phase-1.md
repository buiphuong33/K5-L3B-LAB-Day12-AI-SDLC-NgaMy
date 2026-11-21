# Ma trận truy vết Phase 1

Bằng chứng chung: [`final-verification.md`](../proof/phase-1/final-verification.md), [`qa-baseline.md`](../proof/phase-1/qa-baseline.md).

| AC | Cách kiểm chứng | Kết quả |
|---|---|---|
| Contract: snapshot, end, mã thoát, tất định | `tests/test_smoke_p1.py`, `tests/test_determinism.py` | Đạt |
| Bơi, ramp, chặn biên, hết giờ | `test_smoke_p1.Movement` | Đạt |
| Oxy, ngạt t+59, ngất, mất giỏ LIFO | `test_phase1_rules.GatherRules` | Đạt |
| Hái, mọc lại, bắt cá, hồi chiêu, `hold_full` | `test_phase1_rules.GatherRules` | Đạt |
| File kho và smoke hai tiến trình | `test_smoke_p1.Integration`, chạy tay theo PRD | Đạt |
| Khách, lịch đến, giữ chỗ, `no_dish`, kiên nhẫn | `test_phase1_rules.QuanRules` | Đạt |
| Nấu, bưng, phục vụ, trả tiền, boa, uy tín, đóng ca, điểm | `test_phase1_rules.QuanRules` | Đạt |
| HUD đọc được khi chơi | Đã có đủ trường, chưa chơi thử trên trình duyệt | **Chưa xác nhận** |
| Mỗi người ≥ 3 commit | `git shortlog` | **Chưa đạt** (Phương, Tâm còn thiếu; tính cho cả buổi lab) |
| Phản tư cá nhân | `docs/members/` | **Chưa đạt** (thiếu Phương, Tâm) |

## Đánh giá ngắn
- Lõi headless đạt theo bộ test hiện có. Ba giả định còn chờ xác nhận ở `docs/clarify.md` (mục 5–7).
- Phase sau: chơi thử HUD trên trình duyệt trước khi gắn tag.
