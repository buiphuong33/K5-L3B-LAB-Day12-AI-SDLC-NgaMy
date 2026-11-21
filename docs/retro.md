# Retro nhóm

## Ghi nhận khi bàn giao phần Nga (Phase 1)
- Điều tốt: luật quán và kiểm scenario nằm trong đúng hai file được phân công; lựa chọn món dùng RNG có seed, khách có ID ổn định.
- Điều cần cải thiện: luật ban đầu được suy ra từ TODO/tuning vì bản HTML đầu tiên chỉ là vỏ lab; sau đó đã căn chỉnh theo PRD-0 mục D–F.
- Bằng chứng: bộ test repo 32/32 đạt; smoke trực tiếp xác nhận nấu → chín → bê → phục vụ → trả tiền, phục vụ/thu tiền ở tick đóng ca và các fixture mâu thuẫn bị từ chối.
- Hành động: QA đối chiếu AC/event cho reserved/assigned/served/unfulfillable, hết kiên nhẫn và đóng ca.

## Phase 2 (nhanh)
- Điều tốt: `QuanSim` nhận danh sách món theo kế hoạch ngày và dùng menu/tuning hiện hành cho số bếp, bàn, món và nguyên liệu; kiểm scenario mở rộng theo dữ liệu thay vì khóa cứng danh sách P1.
- Điều tệ: lúc làm lát Nga, repo vẫn có `contract_version: 1.0`; chưa thể chạy scenario `day` theo v1.1 hoặc kiểm smoke cùng `day.py`.
- Điều rút ra khi tích hợp: `fish.py` và `monsters.py` viết trước khi đọc kỹ ticket nên phải sửa lại lúc ráp vào `gather`.
- 1 hành động cho Phase 3 (Nga): khi contract v1.1 và `day.py` được gộp, chạy smoke mở quán với kho bàn giao và xác nhận món ngoài kế hoạch không xuất hiện trong lựa chọn khách.

## Phase 4 (cuối)
- Rà lại hành động Phase 2: đã làm chưa? vì sao?
- Điều tốt / điều tệ:
- Số liệu: số commit theo người, cách đọc code của nhau, token theo người:
- Một lần AI sai và cách nhóm phát hiện:
- Nếu làm lại, đổi gì:
