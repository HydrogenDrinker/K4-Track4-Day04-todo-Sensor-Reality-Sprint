# 📋 Tóm tắt Lab Ngày 4 — Sensor Reality Sprint

## 🎯 Mục tiêu tổng quan

Chọn **một bài toán sensor** trong xe ADAS / robot mặt đất / drone → tìm paper/repo liên quan → chạy demo hoặc benchmark nhỏ → giải thích kết quả trước lớp.

**Output cuối cùng cần có:**
- Báo cáo/slide ngắn
- Log/ảnh/plot chứng minh đã chạy
- Ít nhất **1 metric định lượng**, **1 failure case**, **1 đề xuất cải tiến**

> [!IMPORTANT]
> - Nhóm **đúng 5 thành viên** (hiện tại TEAMMATES.md mới có 3 người — cần bổ sung 2 người nữa)
> - **120 phút** làm việc, **3-5 phút** trình bày
> - Cả 5 dùng **chung repository**, mỗi người **nộp riêng** trên VLearn

---

## ⏱️ Quy trình 7 bước

### Bước 1 · Chuẩn bị (0-15 phút)

| Cần chốt | Nội dung |
|---|---|
| Nền tảng | Xe ADAS / robot / drone |
| Tính năng & sensor | Camera / LiDAR / radar / sonar-ToF / multi-sensor |
| Failure case | Lỗi xuất hiện trong điều kiện nào? (glare, night, fog, rain, packet loss, rolling shutter, timestamp offset, calibration drift, radar ghost, range timeout…) |
| Claim ban đầu | "Khi X thay đổi → metric Y dự kiến tăng/giảm" |
| Metric & đơn vị | Công thức/cách tính cụ thể |
| Baseline vs điều kiện lỗi | Hai cấu hình sẽ so sánh |
| Phân công 5 thành viên | Ai đọc nguồn, chạy thử, ghi số, trình bày? |

---

### Bước 2 · Tìm paper/repository (15-45 phút)

- Tìm paper/repo liên quan trực tiếp đến sensor + failure case đã chốt
- Đọc abstract/README, ghi: **input → output**, dataset, metric, yêu cầu HW/SW, lệnh chạy, limitation
- Chọn **đường chạy tối thiểu**: demo có sẵn / script nhỏ / mô phỏng
- Lưu: link, commit/version, dataset, cấu hình, lệnh chạy thực tế

> [!WARNING]
> **Tách biệt** kết luận của nguồn (paper) vs. kết quả của nhóm (tự chạy). Không biến con số trích dẫn thành kết quả tự đo.

---

### Bước 3 · Thiết kế benchmark có đối chứng (trong 45-95 phút)

1. Chọn dữ liệu mẫu nhỏ, lưu **cấu hình baseline**
2. Tạo **điều kiện lỗi** từ cùng baseline (thay 1 yếu tố có chủ đích)
3. **Định nghĩa metric** trước khi xem kết quả (chiều tốt/xấu, proxy hay thật)
4. Lưu bằng chứng tái hiện: lệnh, cấu hình, log, ảnh trước/sau, seed

| Điều kiện | Tham số | Metric | Bằng chứng | Kết luận cho phép |
|---|---|---|---|---|
| Baseline | Không gây lỗi | Giá trị đo | Log/ảnh/plot | Mốc so sánh |
| Lỗi A | Tham số cụ thể | Giá trị đo | Log/ảnh/plot | Chênh lệch với baseline |
| Lỗi B (nếu có) | Tham số cụ thể | Giá trị đo | Log/ảnh/plot | Xu hướng khi lỗi tăng |

---

### Bước 4 · Chạy một chủ đề và ghi kết quả (45-95 phút)

**Chọn 1 trong 8 chủ đề:**

| Chủ đề | Mô tả ngắn |
|---|---|
| **T1** | Camera health — blur, glare, night, rain → blur score, saturation, entropy, confidence |
| **T2** | LiDAR data loss — dropout, noise, fog → point density, object recall |
| **T3** | Calibration drift — perturb extrinsic → reprojection error, association |
| **T4** | Time sync offset — thêm 50-200ms offset → sai vị trí, ghost |
| **T5** | Radar pseudo-label — camera+LiDAR → radar association → agreement score |
| **T6** | Rangefinder drone — noise, timeout, stuck → range variance, landing risk |
| **T7** | Multi-camera bottleneck — bandwidth, FPS, latency, dropped frames |
| **T8** | Rare case mining — chọn clip khó → slice coverage, failure discovery rate |

> [!TIP]
> Ưu tiên **hoàn thành phần tối thiểu** trước. Phần mở rộng không thay thế bằng chứng chạy.

---

### Bước 5 · Giải thích failure case & chọn cải tiến (95-115 phút)

- Chọn 1 hàng kết quả/frame thể hiện lỗi rõ nhất
- Viết tách biệt: **"Nhóm quan sát được…"** vs **"Paper cho biết…"**
- Nêu **limitation** + điều chưa đo được
- Đề xuất **cải tiến/fallback** + metric kiểm chứng

---

### Bước 6 · Hoàn thiện báo cáo & pitch (115-120 phút)

**Báo cáo 5 mục:**
1. **Problem** — nền tảng, tính năng, sensor, failure
2. **Method** — paper/repo, input/output, giả định
3. **Benchmark** — dữ liệu, cấu hình, metric, kết quả số
4. **Failure case** — tình huống đã phân tích
5. **Engineering decision** — log/fallback/dữ liệu cần tiếp

**Rubric chấm điểm:**

| Tiêu chí | Tỷ trọng |
|---|---|
| Benchmark/demo chạy được | **40%** |
| Hiểu failure thực tế | **25%** |
| Giải thích thuật toán | **20%** |
| Trình bày trade-off | **15%** |

---

### Bước 7 · Nộp bài trên VLearn

- Đặt tên repo: `K4-Track4-Day04-TenNhom-Sensor-Reality-Sprint`
- File `TEAMMATES.md` ở gốc — liệt kê đủ **5 thành viên** (họ tên + MSSV)
- Mỗi thành viên nộp riêng: **bản báo cáo/slide của mình** + **URL repo chung**
- Đảm bảo: 5 tên, 5 bản báo cáo riêng, 5 lượt nộp trên VLearn

---

## ⚠️ Tình trạng hiện tại của repo

| Hạng mục | Trạng thái |
|---|---|
| TEAMMATES.md | ❌ Mới có **3/5** thành viên |
| Chủ đề đã chọn | ❌ Chưa chọn |
| Code/benchmark | ❌ Chưa có |
| Báo cáo/slide | ❌ Chưa có |

---

## 🔑 Những điều quan trọng cần nhớ

1. **Claim phải hẹp & đo được** — không nói chung chung kiểu "camera kém khi trời mưa"
2. **Giữ nguyên metric** giữa các điều kiện — không đổi cách tính giữa chừng
3. **Tách biệt rõ ràng**: quan sát (tự đo) vs. trích dẫn (từ paper) vs. suy luận (giả thuyết)
4. **Metric proxy** phải nói rõ nó thay thế cho cái gì và chưa chứng minh được gì
5. **Bằng chứng chạy được** (log/ảnh/plot) quan trọng hơn ý tưởng đẹp
