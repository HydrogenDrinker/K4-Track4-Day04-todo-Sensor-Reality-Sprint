# BÁO CÁO CÁ NHÂN LAB NGÀY 04 — SENSOR REALITY SPRINT
**Học viên:** Đỗ Đình Long  
**MSSV:** 2A202602673  
**Vai trò:** Sensor Pipeline & Benchmark Engineer  
**Đề tài:** T1 — Camera Degradation Health Score in Autonomous Driving  
**Repository chung của nhóm:** `K4-Track4-Day04-TenNhom-Sensor-Reality-Sprint`  

---

### 1. Problem (Bài toán & Bối cảnh kỹ thuật)
- **Nền tảng kiểm thử:** Hệ thống thị giác máy tính phía trước trên xe thông minh ADAS L2+, thu nhận luồng hình ảnh RGB $1280 \times 720$ phục vụ module phát hiện vật thể và đo cự ly (Monocular 3D Perception).
- **Vấn đề thực tế của cảm biến:** Camera hoạt động trong thế giới mở liên tục chịu các tác nhân gây suy thoái quang học (Optical degradation). Các lỗi phổ biến gồm mất tiêu cự do hơi nước/bụi (Defocus blur), nhòe chuyển động do xóc nảy (Motion blur), tán xạ do sương mù (Fog), và quá bão hòa điểm ảnh do ánh nắng chiếu thẳng vào ống kính (Sun glare).
- **Mục tiêu đo đạc:** Xây dựng pipeline kiểm tra chất lượng thời gian thực (real-time health monitor) chạy trước detector để chấm điểm từng khung hình, cung cấp bằng chứng định lượng trước khi đưa frame vào mạng nơ-ron nhận diện.

---

### 2. Method (Phương pháp & Công thức tính toán)
- **Cơ sở nghiên cứu:** Benchmark chuẩn Dong et al., CVPR 2023 (*thu-ml/3D_Corruptions_AD*), bảng 2 khảo sát độ suy giảm mAP trên tập dữ liệu xe tự hành thực tế **nuScenes-C**.
- **Bộ 4 chỉ số sức khỏe cảm biến được nhóm cài đặt:**
  1. *Độ sắc nét (Variance of Laplacian - Focus Measure):*
     $$fm = \sigma^2(\nabla^2 I_{\text{gray}}) = \frac{1}{HW}\sum_{x,y} \left( \nabla^2 I(x,y) - \mu_{\nabla^2} \right)^2$$
  2. *Năng lượng vi phân Tenengrad (Sobel gradient energy):*
     $$S = \frac{1}{HW}\sum_{x,y} \left( S_x(x,y)^2 + S_y(x,y)^2 \right)$$
  3. *Entropy thông tin Shannon (đo mức độ phong phú thông tin điểm ảnh):*
     $$H = -\sum_{k=0}^{255} p_k \log_2(p_k)$$
  4. *Tỷ lệ bão hòa quang học (Saturation Ratio):*
     $$R_{\text{sat}} = \frac{N(I < 10) + N(I > 245)}{H \times W}$$
- **Lệnh chạy tái hiện:**
  ```bash
  python run_sprint_benchmark.py
  python plot_results.py
  ```

---

### 3. Benchmark (Kết quả thực nghiệm 41 lượt chạy)
- **Bảng số liệu tổng hợp các mức độ suy giảm (Trích từ `results/benchmark_table.csv`):**

| Điều kiện kiểm thử | Mức độ (Severity) | Blur Score ($fm$) | Tenengrad Energy ($S$) | Saturation ($R_{\text{sat}}$) | Shannon Entropy ($H$) | Detector Conf | Trọng số $W_{\text{cam}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Clean)** | **0** | **819.89** | **5598.04** | **1.64%** | **5.88 bits** | **0.951** | **0.68** |
| Defocus Blur | 1 | 13.37 | 1653.28 | 0.60% | 5.92 bits | 0.230 | 0.14 |
| Defocus Blur | 3 | 1.80 | 607.73 | 0.00% | 6.05 bits | 0.115 | 0.06 |
| **Defocus Blur** | **5** | **0.62** | **167.02** | **0.00%** | **6.29 bits** | **0.079** | **0.05** |
| Motion Blur | 3 | 35.37 | 1021.87 | 0.22% | 6.07 bits | 0.325 | 0.28 |
| Fog (Sương mù) | 3 | 80.07 | 679.95 | 0.00% | 5.88 bits | 0.434 | 0.57 |
| Sun Glare (Lóa nắng) | 3 | 464.47 | 2849.19 | 22.58% | 6.61 bits | 0.477 | 0.41 |
| Sun Glare (Lóa nắng) | 5 | 159.07 | 766.70 | 43.32% | 5.53 bits | 0.122 | 0.14 |

- **Đo kiểm tài nguyên & độ trễ:**
  - Độ trễ trung bình trên frame $1280 \times 720$: $\mathbf{47.59\text{ ms}}$ (tương đương $\sim 21\text{ FPS}$ ở chế độ CPU tuần tự đơn luồng không dùng OpenCL). Khi chuyển đổi sang vùng ROI trung tâm $640 \times 360$, độ trễ giảm xuống dưới $\mathbf{2.8\text{ ms}}$ ($> 350\text{ FPS}$).

---

### 4. Failure Case & Đối chứng
- **Đối chứng với bài báo Dong et al. (CVPR 2023 Table 2):**
  - Bài báo công bố FCOS3D mAP sụp đổ từ $35.4\% \rightarrow 13.4\%$ (S3, giảm $62.1\%$) và $2.1\%$ (S5, giảm $94.1\%$).
  - Nhóm tự đo: Blur Score $fm$ sụp đổ từ $819.89 \rightarrow 1.80$ (S3, giảm $99.8\%$) và $0.62$ (S5, giảm $99.9\%$), kéo theo Detector Confidence giảm từ $0.951 \rightarrow 0.115$ (S3) và $0.079$ (S5).
- **Hạn chế đo lường:** Variance of Laplacian đo biến thiên tần số cao cục bộ nên rất nhạy cảm với nhiễu ngẫu nhiên. Khi ống kính bị mờ đục nhưng cảm biến CMOS đẩy ISO lên cao tạo hạt nhiễu trắng (Gaussian noise), $fm$ tăng vọt giả tạo (đã kiểm chứng ở file `corner_case_noisy_blur.jpg`).

---

### 5. Engineering Decision (Đề xuất kỹ thuật)
- **Quy tắc chuyển mạch an toàn (Tripwire Rule):**
  - Nếu $fm < 100$ hoặc $R_{\text{sat}} > 15\%$, hệ thống ADAS bắt buộc:
    1. Giảm trọng số camera $W_{\text{cam}}$ xuống mức sàn an toàn $0.05$.
    2. Chuyển quyền quyết định phanh khoảng cách sang cảm biến LiDAR/Radar ($W_{\text{lidar}} = 0.95$).
    3. Hiển thị thông báo trên táp-lô yêu cầu tài xế chủ động cầm lái (Takeover Request).
- **Đồ thị minh chứng:** Xem biểu đồ trực quan tại [`plots/blur_score_vs_severity.png`](file:///d:/Code/VinAI/Labs/Track4/K4-Track4-Day04-todo-Sensor-Reality-Sprint/plots/blur_score_vs_severity.png) và [`plots/fusion_weight_vs_severity.png`](file:///d:/Code/VinAI/Labs/Track4/K4-Track4-Day04-todo-Sensor-Reality-Sprint/plots/fusion_weight_vs_severity.png).
