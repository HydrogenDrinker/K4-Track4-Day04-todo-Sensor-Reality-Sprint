# BÁO CÁO TỔNG HỢP SPRINT LAB NGÀY 04: CẢM BIẾN CHUỖI KHUNG HÌNH - THỜI GIAN
## Đề tài T1: Camera Degradation Health Score trong Xe Tự Hành ADAS
**Học phần:** Sensor Reality Sprint — K4-Track4  
**Tên nhóm:** Nhóm 03 (Camera Health ADAS)  
**Quy mô nhóm:** 3 thành viên  
**Danh sách thành viên:**
1. **Phạm Thị Ngọc Anh** (MSSV: **2A202602831**) — *Team Leader & Perception Lead*
2. **Đỗ Đình Long** (MSSV: **2A202602673**) — *Sensor Pipeline & Benchmark Engineer*
3. **Võ Đức Tài** (MSSV: **2A202603007**) — *Failure Analysis & Fusion Architect*

---

### Bảng tóm tắt thông số khởi tạo Sprint (Theo Bước 1 của Đề bài)
| Hạng mục cần chốt | Nội dung cụ thể của Nhóm |
| :--- | :--- |
| **Nền tảng, tính năng, sensor** | Xe ADAS Level 2+/L3; Tính năng AEB & Nhận diện vật thể 3D phía trước; Cảm biến: Front Monocular Camera ($1280 \times 720$ RGB @ 30 FPS). |
| **Failure case kiểm tra** | Thấu kính mất nét (Defocus blur), rung lắc nhòe hình (Motion blur), tán xạ quang học do sương mù (Fog), bão hòa cảm biến CMOS do lóa nắng (Sun glare). |
| **Claim ban đầu (Giả thuyết)** | Khi khung hình bị nhòe/suy thoái mạnh hơn ($fm$ sụp đổ), độ tin cậy của detector giảm mạnh $\rightarrow$ cần kích hoạt cơ chế giảm trọng số camera ($W_{\text{cam}} \rightarrow 0.05$) để chuyển giao an toàn cho LiDAR/Radar. |
| **Metric và đơn vị đo** | Độ nét $fm$ (Variance of Laplacian - không thứ nguyên), Năng lượng Sobel $S$, Shannon Entropy $H$ (bits/pixel), Saturation ratio $R_{\text{sat}}$ (%), Confidence proxy ($[0, 1]$), Latency ($\text{ms}$). |
| **Baseline & Điều kiện lỗi** | Baseline: Khung hình sạch (Clean Severity 0) $\leftrightarrow$ Điều kiện lỗi: 4 loại biến dạng ở 5 mức độ nghiêm trọng (Severity 1 đến 5). |
| **Phân công 3 thành viên** | 1. Ngọc Anh: Khảo sát Paper CVPR 2023, dựng Perception Proxy, Pitch mở đầu.<br>2. Đình Long: Cài đặt bộ đo 4 metric, chạy benchmark 41 lượt, đo latency, vẽ plots.<br>3. Đức Tài: Phân tích 2 Corner Cases, thiết kế luật Safe Fallback & Fusion weight. |

---

## 1. Problem (Bài toán kỹ thuật & Tác động hệ thống)
- **Nền tảng ứng dụng:** Xe thương mại thông minh ADAS Cấp độ 2+ (Level 2+ Autonomous Driving), sử dụng cụm camera đơn phía trước (Front-facing Monocular RGB Camera, chuẩn hình ảnh $1280 \times 720$ @ 30 FPS).
- **Tính năng chịu ảnh hưởng:** Phanh khẩn cấp tự động (Autonomous Emergency Braking - AEB) và Phát hiện vật thể 3D phía trước (Forward 3D Object Detection).
- **Hiện tượng lỗi cảm biến trong thực tế:**
  1. *Defocus Blur:* Ống kính bị bám bụi bẩn, ngưng tụ hơi ẩm bên trong hoặc trầy xước bề mặt thấu kính quang học làm mất tiêu cự.
  2. *Motion Blur:* Xe di chuyển trên mặt đường gồ ghề ở tốc độ cao kết hợp với thời gian phơi sáng (exposure time) lớn tạo vệt nhòe chuyển động.
  3. *Fog / Weather Corruption:* Thời tiết sương mù, mưa bụi gây tán xạ photon trong khí quyển làm suy giảm tương phản trường nhìn sâu.
  4. *Sun Glare:* Góc chiếu mặt trời thấp lúc hoàng hôn/bình minh chiếu thẳng vào cảm biến CMOS làm bão hòa hàng loạt pixel.
- **Hậu quả hệ thống:** Nếu hệ thống perception tiếp tục nạp các khung hình suy thoái vào mạng nơ-ron nhận diện (Deep Neural Network) mà không có cơ chế tự đánh giá chất lượng (Sensor Health Monitoring), mô hình sẽ suy giảm độ tin cậy nghiêm trọng, dẫn đến bỏ sót chướng ngại vật (False Negative) hoặc tính toán sai khoảng cách Time-to-Collision (TTC), gây nguy cơ tai nạn nghiêm trọng.


---

## 2. Method (Cơ sở nghiên cứu & Thuật toán đề xuất)

### 2.1. Cơ sở lý thuyết và công bố khoa học tham chiếu
- **Nguồn nghiên cứu chuẩn:** Dong và cộng sự, *"Benchmarking Robustness of 3D Object Detection to Common Corruptions in Autonomous Driving"*, công bố tại hội nghị thị giác máy tính hàng đầu **CVPR 2023**.
- **Mã nguồn chính thức:** [thu-ml/3D_Corruptions_AD](https://github.com/thu-ml/3D_Corruptions_AD).
- **Bộ dữ liệu chuẩn:** **nuScenes-C** (tập dữ liệu xe tự hành thực tế với 1000 scenes đường phố đô thị và cao tốc).
- **Kết quả công bố gốc trong bài báo (Table 2 - FCOS3D trên nuScenes-C):**
  - Mạng FCOS3D trên ảnh sạch đạt $\text{mAP} = 35.4\%$ ($0.354$), điểm $\text{NDS} = 0.415$.
  - Dưới tác động của **Defocus Blur**:
    - Severity 1: $\text{mAP} = 28.5\%$ (giảm $-19.5\%$)
    - Severity 2: $\text{mAP} = 21.0\%$ (giảm $-40.7\%$)
    - Severity 3: $\text{mAP} = 13.4\%$ (giảm $-62.1\%$)
    - Severity 4: $\text{mAP} = 7.2\%$
    - Severity 5: $\text{mAP} = 2.1\%$ (sụp đổ $-94.1\%$)
  - Dưới tác động của **Motion Blur**: $\text{mAP}$ giảm từ $35.4\% \rightarrow 15.8\%$ (S3) $\rightarrow 3.5\%$ (S5).
  - Dưới tác động của **Fog**: $\text{mAP}$ giảm từ $35.4\% \rightarrow 12.1\%$ (S3) $\rightarrow 4.8\%$ (S5).
  - *Quan sát mấu chốt của bài báo:* Mô hình kết hợp đa cảm biến LiDAR-Camera (TransFusion) chỉ bị giảm mAP từ $64.9\% \rightarrow 58.2\%$ ở Severity 3, chứng minh tính cấp thiết của việc hạ tỷ trọng Camera để nhường quyền quyết định cho LiDAR.

### 2.2. Thuật toán đo kiểm sức khỏe cảm biến thời gian thực (Camera Health Monitor)
Thuật toán chạy tiền xử lý trước mạng nơ-ron nhận diện, tính toán 4 chỉ số cơ bản trên ma trận điểm ảnh:
1. **Variance of Laplacian (Focus Measure - $fm$):**
   $$fm = \sigma^2(\nabla^2 I) = \frac{1}{HW} \sum_{x,y} \left( \nabla^2 I(x,y) - \mu_{\nabla^2} \right)^2$$
   Toán tử Laplacian phát hiện biến thiên tần số cao. Ảnh nét có $fm$ lớn, ảnh mờ có $fm$ tiệm cận $0$. Ngưỡng an toàn quy định: $\tau_{\text{blur}} = 100.0$.
2. **Tenengrad Gradient Energy ($S$):** Tích lũy bình phương đạo hàm Sobel theo 2 trục $x, y$ để đo độ dốc biên cạnh quang học.
3. **Shannon Information Entropy ($H$):**
   $$H = -\sum_{k=0}^{255} p_k \log_2(p_k)$$
   Đo lượng thông tin và phân bố mức xám. Giá trị bình thường nằm trong khoảng $5.5 - 7.0\text{ bits/pixel}$.
4. **Saturation Ratio ($R_{\text{sat}}$):** Tỷ lệ điểm ảnh bị bão hòa đen kiệt ($I < 10$) hoặc trắng xóa ($I > 245$). Ngưỡng cảnh báo: $R_{\text{sat}} > 15\%$.

### 2.3. Chính sách phân bổ trọng số kết hợp động (Dynamic Sensor Fusion Weighting)
Dựa trên chỉ số suy thoái tổng hợp $\text{DegradationIndex} \in [0.0, 1.0]$, trọng số của camera $W_{\text{cam}}$ được điều chỉnh tự động:
$$W_{\text{cam}} = \max\left( W_{\min}, W_{\text{base}} - (W_{\text{base}} - W_{\min}) \times \text{DegradationIndex} \right)$$
Trong điều kiện chuẩn: $W_{\text{cam}} = 0.70, W_{\text{lidar}} = 0.30$. Khi camera suy thoái nghiêm trọng, $W_{\text{cam}}$ hạ xuống sàn $0.05$ và $W_{\text{lidar}}$ tăng vọt lên $0.95$.

---

## 3. Benchmark (Kết quả thực nghiệm có đối chứng)

### 3.1. Thiết kế thực nghiệm
- **Dữ liệu kiểm thử:** Khung hình ADAS độ phân giải cao $1280 \times 720$ với đầy đủ làn đường, phương tiện phía trước và biển báo chỉ dẫn.
- **Không gian biến thiên:** 4 loại biến dạng quang học chuẩn CVPR 2023 (Defocus Blur, Motion Blur, Fog, Sun Glare) ở 5 cấp độ nghiêm trọng (Severity 1 đến 5), tổng cộng 41 lượt chạy benchmark có đo lường độ trễ lặp lại.
- **Lệnh thực thi:**
  ```bash
  python run_sprint_benchmark.py
  python plot_results.py
  ```

### 3.2. Bảng số liệu đối chứng chi tiết (Trích xuất từ `results/benchmark_table.csv`)

| Điều kiện kiểm thử | Cấp độ (Severity) | Blur Score ($fm$) | Tenengrad Energy ($S$) | Saturation ($R_{\text{sat}}$) | Shannon Entropy ($H$) | Detector Confidence | Trọng số $W_{\text{cam}}$ | Trạng thái ADAS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline (Sạch)** | **0** | **819.89** | **5598.04** | **1.64%** | **5.88 bits** | **0.951** | **0.68** | `HEALTHY` |
| Defocus Blur | 1 | 13.37 | 1653.28 | 0.60% | 5.92 bits | 0.230 | 0.14 | `WARNING_BLUR` |
| Defocus Blur | 2 | 3.63 | 931.65 | 0.03% | 6.01 bits | 0.147 | 0.07 | `WARNING_BLUR` |
| **Defocus Blur** | **3** | **1.80** | **607.73** | **0.00%** | **6.05 bits** | **0.115** | **0.06** | `WARNING_BLUR` |
| Defocus Blur | 4 | 0.86 | 340.60 | 0.00% | 6.16 bits | 0.089 | 0.06 | `WARNING_BLUR` |
| **Defocus Blur** | **5** | **0.62** | **167.02** | **0.00%** | **6.29 bits** | **0.079** | **0.05** | `WARNING_BLUR` |
| Motion Blur | 1 | 49.65 | 1976.19 | 0.48% | 5.95 bits | 0.364 | 0.37 | `WARNING_BLUR` |
| Motion Blur | 3 | 35.37 | 1021.87 | 0.22% | 6.07 bits | 0.325 | 0.28 | `WARNING_BLUR` |
| Motion Blur | 5 | 18.53 | 544.60 | 0.00% | 6.21 bits | 0.260 | 0.17 | `WARNING_BLUR` |
| Fog (Sương mù) | 1 | 395.18 | 2894.58 | 1.44% | 6.34 bits | 0.739 | 0.68 | `HEALTHY` |
| Fog (Sương mù) | 3 | 80.07 | 679.95 | 0.00% | 5.88 bits | 0.434 | 0.57 | `WARNING_BLUR` |
| Fog (Sương mù) | 5 | 5.56 | 55.68 | 0.00% | 3.75 bits | 0.171 | 0.09 | `WARNING_BLUR` |
| Sun Glare (Lóa nắng)| 1 | 792.04 | 5328.36 | 8.62% | 6.31 bits | 0.818 | 0.59 | `HEALTHY` |
| Sun Glare (Lóa nắng)| 3 | 464.47 | 2849.19 | 22.58% | 6.61 bits | 0.477 | 0.41 | `WARNING_SATURATION`|
| Sun Glare (Lóa nắng)| 5 | 159.07 | 766.70 | 43.32% | 5.53 bits | 0.122 | 0.14 | `WARNING_SATURATION`|

### 3.3. Đối chứng số liệu công bố của Paper vs Số liệu nhóm tự đo đạc
| Yếu tố đối chứng | Báo cáo công bố của Dong et al. (CVPR 2023 Table 2) | Kết quả nhóm tự đo đạc thực tế tại lớp | Nhận xét tương quan |
| :--- | :--- | :--- | :--- |
| **Defocus S3 vs Clean** | FCOS3D mAP giảm từ $35.4\% \rightarrow 13.4\%$ (**giảm $-62.1\%$**) | Focus Measure giảm $99.8\%$; Detector Conf giảm từ $0.951 \rightarrow 0.115$ (**giảm tương đối $-87.9\%$**) | Độ nét sụp đổ kéo theo độ tin cậy nhận diện biên cạnh suy giảm đồng pha cực mạnh. |
| **Defocus S5 vs Clean** | FCOS3D mAP sụp đổ còn $2.1\%$ (**giảm $-94.1\%$**) | Focus Measure $= 0.62$, Detector Conf $= 0.079$ (**giảm $-91.7\%$**) | Khớp hoàn toàn xu hướng mất khả năng nhận diện 3D khi thấu kính mờ đục hoàn toàn. |
| **Motion Blur S3** | FCOS3D mAP giảm còn $15.8\%$ (giảm $-55.4\%$) | Detector Conf giảm xuống $0.325$ (giảm tương đối $-65.8\%$) | Nhòe phương ngang làm mất cạnh đứng xe cộ phía trước. |

---

## 4. Failure Case Phân Tích Chuyên Sâu (2 Anomaly Corner Cases)
Nhóm đã chủ động tạo dựng 2 tình huống đặc biệt để phân tích giới hạn của thuật toán (lưu tại `results/corner_case_analysis.json`):

```
                                  [KHUNG HÌNH ĐẦU VÀO]
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
        [Trường hợp A: Mặt đường phẳng]             [Trường hợp B: Mờ + Nhiễu ISO cao]
          Thấu kính: SẠCH HOÀN TOÀN                   Thấu kính: MỜ ĐỤC HOÀN TOÀN
          Khung cảnh: Mặt nhựa không texture          Khung cảnh: Nhiễu hạt cảm biến ban đêm
                    │                                             │
          Toán tử Laplacian: fm = 0.0597             Toán tử Laplacian: fm = 8768.12
                    │                                             │
                    ▼                                             ▼
         [HẬU QUẢ: FALSE POSITIVE]                     [HẬU QUẢ: FALSE NEGATIVE]
        Báo động giả camera bị mờ,                   Bỏ sót lỗi nguy hiểm, báo HEALTHY
         hạ nhầm trọng số an toàn                     dù xe không thể nhìn thấy vật cản
```

1. **Failure Case 1 (False Positive - Báo động giả do thiếu Texture):**
   - *Nguyên nhân:* Thấu kính hoàn toàn sạch sẽ, nhưng xe chạy vào đoạn đường cao tốc mới rải nhựa phẳng lì, không có vạch kẻ đường hay phương tiện khác.
   - *Số liệu đo:* $fm = 0.0597$ (thấp hơn cả Defocus Blur Severity 5 là $0.62$).
   - *Hệ quả:* Hệ thống nhận định sai là thấu kính bị bẩn/mờ nặng, tự động tước quyền của camera và phát cảnh báo không cần thiết đến tài xế.
   - *Khắc phục:* Bổ sung kiểm tra Shannon Entropy ($H = 4.33\text{ bits}$ - cảnh báo cảnh nghèo thông tin `ADVISORY_LOW_TEXTURE`) thay vì chỉ nhìn vào một chỉ số $fm$.
2. **Failure Case 2 (False Negative - Bỏ sót lỗi do nhiễu hạt che giấu độ mờ):**
   - *Nguyên nhân:* Ống kính bị đọng nước mờ mịt hoàn toàn nhưng xe chạy ban đêm khiến cảm biến CMOS đẩy gain/ISO lên tối đa, sinh ra vô số hạt nhiễu sắc nhọn (sensor grain noise).
   - *Số liệu đo:* Toán tử vi phân bậc hai phản ứng mạnh với các bước nhảy đơn lẻ giữa các pixel nhiễu, làm $fm$ tăng vọt lên **$8768.12$** (cao gấp 10 lần ảnh sạch $819.89$).
   - *Hệ quả:* Hệ thống thông báo trạng thái `HEALTHY`, bỏ sót tình trạng mất thị lực quang học thực tế, cực kỳ nguy hiểm.
   - *Khắc phục:* Bắt buộc áp dụng bộ lọc làm mịn thông thấp (Gaussian Blur hoặc Bilateral Filter) trước khi tính toán $fm$, hoặc kiểm tra tính nhất quán gradient trong miền thời gian (Temporal Gradient Consistency).

---

## 5. Engineering Decision & Trade-offs

### 5.1. Quyết định phân luồng và chuyển giao an toàn (Safe Fallback Policy)
Dựa trên kết quả đo đạc thực nghiệm, nhóm kiến nghị chính sách điều khiển phân tầng cho hệ thống ADAS:
1. **Vùng an toàn (Green Tier - Severity $\le 1$, $fm \ge 100$ và $R_{\text{sat}} \le 15\%$):**
   - Camera vận hành bình thường, gán trọng số $W_{\text{cam}} = 0.70$.
   - Tính năng AEB và LKA (Lane Keeping Assist) được kích hoạt toàn phần.
2. **Vùng cảnh báo (Yellow Tier - Severity 2, $50 \le fm < 100$):**
   - Giảm dần trọng số camera xuống $0.30 - 0.40$, tăng trọng số Radar/LiDAR lên $0.60 - 0.70$.
   - Phát cảnh báo bằng âm thanh nhẹ và biểu tượng camera đọng sương trên màn hình ODO.
3. **Vùng ngắt an toàn (Red Tier - Severity $\ge 3$, $fm < 50$ hoặc $R_{\text{sat}} > 20\%$):**
   - Lập tức ngắt trọng số camera xuống sàn an toàn $W_{\text{cam}} = 0.05$.
   - Chuyển giao toàn bộ quyền tính toán khoảng cách phanh AEB sang cảm biến bước sóng mm (Automotive mmWave Radar) và LiDAR ($W_{\text{lidar}} = 0.95$).
   - Phát lệnh yêu cầu người lái tiếp quản phương tiện (Takeover Request - TOR) trong vòng 5 giây.

### 5.2. Đánh giá Trade-off hệ thống
| Tiêu chí | Ưu điểm của giải pháp nhóm | Hạn chế & Cái giá phải trả |
| :--- | :--- | :--- |
| **Tài nguyên tính toán** | Độ trễ trung bình chỉ $\mathbf{47.59\text{ ms}}$ (tính trên toàn khung hình $1280 \times 720$) và dưới $\mathbf{2.8\text{ ms}}$ nếu tính trên vùng ROI trung tâm, không cần GPU đồ sộ. | Không phân biệt được các loại biến dạng ngữ nghĩa phức tạp (như vết bùn loang lổ cục bộ trên góc cảm biến). |
| **Độ tin cậy chuyển mạch** | Ngăn chặn triệt để hiện tượng phanh ma (phantom braking) do ảo giác của mạng nơ-ron nhận diện khi ảnh bị mờ. | Có thể phát sinh báo động giả khi xe đi qua đoạn hầm tối hoặc đường nhựa đen phẳng không vạch kẻ nếu không kết hợp lọc Entropy. |

### 5.3. Minh chứng trực quan (Artifacts & Plots)
Toàn bộ đồ thị phục vụ thẩm định đã được tạo tự động trong thư mục `plots/`:
- [`plots/blur_score_vs_severity.png`](file:///d:/Code/VinAI/Labs/Track4/K4-Track4-Day04-todo-Sensor-Reality-Sprint/plots/blur_score_vs_severity.png): Đồ thị hàm logarit biểu diễn độ sụp đổ của Variance of Laplacian theo mức độ biến dạng.
- [`plots/detector_confidence_vs_severity.png`](file:///d:/Code/VinAI/Labs/Track4/K4-Track4-Day04-todo-Sensor-Reality-Sprint/plots/detector_confidence_vs_severity.png): Đồ thị đối sánh trực tiếp giữa đường cong mAP công bố trong bài báo CVPR 2023 và độ tin cậy detector đo tại lớp.
- [`plots/fusion_weight_vs_severity.png`](file:///d:/Code/VinAI/Labs/Track4/K4-Track4-Day04-todo-Sensor-Reality-Sprint/plots/fusion_weight_vs_severity.png): Biểu đồ hạ trọng số camera và tiếp quản của LiDAR qua các ngưỡng cảnh báo.
- [`plots/latency_distribution.png`](file:///d:/Code/VinAI/Labs/Track4/K4-Track4-Day04-todo-Sensor-Reality-Sprint/plots/latency_distribution.png): Phân phối thời gian thực thi của thuật toán.
- [`plots/visual_comparison_collage.png`](file:///d:/Code/VinAI/Labs/Track4/K4-Track4-Day04-todo-Sensor-Reality-Sprint/plots/visual_comparison_collage.png): Bảng ảnh trực quan HUD chẩn đoán qua các trạng thái suy thoái và tình huống góc.

### 5.4. Thử thách mở rộng (Extended Challenge theo Đề bài)
Theo gợi ý thử thách mở rộng của đề tài T1 trong `reference.txt`:
1. **Ngưỡng thích nghi động theo Ngày / Đêm (Adaptive Daytime/Nighttime Thresholds):**
   - *Ban ngày (Daytime - Chiếu sáng đầy đủ $\mu_{\text{gray}} \ge 80$):* Cảnh vật giàu chi tiết, năng lượng biên cạnh cao ($fm_{\text{clean}} \approx 800 - 2500$). Ngưỡng an toàn được đặt nghiêm ngặt $\tau_{\text{blur}} = 100.0$ và $\tau_{\text{sat}} = 15.0\%$.
   - *Ban đêm (Nighttime - Ánh sáng yếu $\mu_{\text{gray}} < 80$):* Phần lớn khung cảnh là nền đen không chứa cạnh, trong khi vùng chiếu đèn pha lại có độ chói cục bộ. Ngưỡng Laplacian cố định sẽ gây báo động giả liên tục. Nhóm đề xuất công thức thích nghi động:
     $$\tau_{\text{adaptive}} = \tau_{\text{base}} \times \max\left(0.25, \frac{\mu_{\text{gray}}}{128.0}\right)$$
     Khi trời tối ($\mu_{\text{gray}} \approx 30$), ngưỡng $\tau_{\text{adaptive}}$ tự động hạ xuống $\approx 23.4$, kết hợp lọc song phương (Bilateral filter) để triệt tiêu nhiễu hạt trước khi đo độ nét.
2. **So sánh với Độ tin cậy của Mô hình Thị giác Lớn (VLM / Foundation Vision Model):**
   - *Mô hình VLM (như CLIP / Qwen2-VL):* Có ưu thế vượt trội trong việc hiểu ngữ nghĩa toàn cục (Global semantic understanding). Khi đưa prompt: *"Is the front camera lens obstructed, foggy or blurred?"*, VLM có thể nhận biết chính xác các dị vật bám trên kính mà thuật toán Laplacian không phát hiện được (như giọt nước trong suốt hoặc vết lá cây che khuất góc nhìn).
   - *Rào cản thực tế trong ADAS:* VLM đòi hỏi tài nguyên tính toán GPU cực lớn và độ trễ phản hồi từ $150 - 500\text{ ms}$, hoàn toàn không khả thi để chạy trên từng khung hình của hệ thống an toàn (vốn yêu cầu phản ứng dưới $33.3\text{ ms}$).
   - *Mô hình kiến trúc Hybrid đề xuất:* Dùng bộ đo nhẹ Laplacian + Entropy ($< 3\text{ ms}$) làm bộ lọc tuyến đầu (Gatekeeper) ở tần số $30\text{ FPS}$. Chỉ khi phát hiện bất thường kéo dài quá $1.0\text{ giây}$ mà không phân loại được nguyên nhân, hệ thống mới gửi khung hình sang VLM chạy nền ($1\text{ FPS}$) để chẩn đoán ngữ nghĩa chuyên sâu và tự động làm sạch ống kính (bơm nước rửa kính / sấy kính).

