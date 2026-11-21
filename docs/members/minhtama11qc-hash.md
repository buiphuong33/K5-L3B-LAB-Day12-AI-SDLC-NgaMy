# minhtama11qc-hash (Phạm Minh Tâm) — phản tư cá nhân

**Vai:** PO (giữ `docs/clarify.md`), module `sim/gather`, đóng gói P4.

- **Tôi đã làm:**
  - P1 lát 1 gather: oxy, ngạt, Máu, giỏ LIFO — [`29d6750`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/29d6750), PR [#1](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/pull/1).
  - P2 khung `FishSchool` — [`4402050`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/4402050).
  - P3 độ tươi buổi sáng + `test_p3_gather` — [`47c467b`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/47c467b), PR [#4](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/pull/4).
  - P4 README, LICENSE, CREDITS, `tools/package_release.py` — PR [#5](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/pull/5).
- **Đã giúp ai:** phân tích tác động gather cho Phương (P3); phát hiện gather cần `contract_version` trong tuning, Nga thêm ở [`3973760`](https://github.com/buiphuong33/K5-L3B-LAB-Day12-AI-SDLC-NgaMy/commit/3973760). Đọc `items.py`/ADR 0001 và `quan.py` của Nga để khớp bàn giao.
- **AI sai ở đâu:** AI code trước khi pull `main`, nên lát 2 và cá P2 trùng việc Nga đã làm (PR #2, #3 phải đóng). Ở P3, AI bật kho cá thể theo khối `freshness` thay vì version; merge `main` vào thì 10 test P1/P2 đỏ, phát hiện trước khi gộp.
- **Bài học:** pull và đọc ADR trước khi làm. Test xanh chưa đủ, phải đối chiếu đặc tả.
