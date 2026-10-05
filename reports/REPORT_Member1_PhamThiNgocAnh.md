# BÁO CÁO CÁ NHÂN LAB NGÀY 04 — SENSOR REALITY SPRINT
**Học viên:** Phạm Thị Ngọc Anh  
**MSSV:** 2A202602831  
**Vai trò:** Perception Lead  
**Đề tài:** T1 — Camera Degradation Health Score in Autonomous Driving  
**Repository chung của nhóm:** `K4-Track4-Day04-TenNhom-Sensor-Reality-Sprint`  

---

### 1. Problem (Bài toán & Bối cảnh kỹ thuật)
- **Nền tảng & Tính năng:** Xe tự hành cấp độ ADAS L2+/L3 trang bị camera đơn phía trước (Front-facing monocular RGB camera, độ phân giải $1280 \times 720$ @ 30 FPS) phục vụ tính năng Phanh khẩn cấp tự động (Autonomous Emergency Braking - AEB) và Nhận diện chướng ngại vật 3D (Forward 3D Object Detection).
- **Sensor & Failure Mode:** Camera bị suy giảm chất lượng vật lý (degradation) trong vận hành thực tế do:
  1. Thấu kính bám mờ/đọng sương (Defocus Blur - mất tiêu cự quang học).
  2. Rung lắc vận tốc cao trên mặt đường gồ ghề (Motion Blur).
  3. Thời tiết bất lợi (Sương mù - Fog quang học, tán xạ khí quyển).
  4. Lóa nắng trực diện góc thấp (Sun Glare gây bão hòa cảm biến CMOS).
- **Hậu quả hệ thống:** Nếu khung hình suy giảm mà không có cơ chế tự đánh giá sức khỏe (health score), luồng suy luận của Deep Neural Network (như FCOS3D/CenterNet) vẫn trả về kết quả với false negative hoặc bounding box trôi dạt nghiêm trọng, khiến hệ thống AEB không kích hoạt kịp thời hoặc phanh ma nguy hiểm.

---

### 2. Method (Phương pháp & Cơ sở nghiên cứu)
- **Nghiên cứu gốc tham chiếu:** Dong và cộng sự, *"Benchmarking Robustness of 3D Object Detection to Common Corruptions in Autonomous Driving"*, công bố tại hội nghị đỉnh cao **CVPR 2023** (GitHub chính thức: `https://github.com/thu-ml/3D_Corruptions_AD`).
- **Input & Output:**
  - *Đầu vào:* Khung hình thô $I \in \mathbb{R}^{H \times W \times 3}$.
  - *Đầu ra:* Chỉ số chất lượng không gian (Blur Score - Variance of Laplacian $fm$, Tenengrad Gradient Energy $S$, Shannon Entropy $H$, Saturation Ratio $R_{\text{sat}}$) và trọng số kết hợp đa cảm biến $W_{\text{cam}} \in [0.05, 0.70]$.
- **Mô phỏng tác động lên Perception:** Dựa trên Bảng 2 (Table 2) trong bài báo CVPR 2023 đo trên tập chuẩn **nuScenes-C**, mạng FCOS3D có mAP cơ sở đạt $35.4\%$ ($0.354$), nhưng sụp đổ chỉ còn $13.4\%$ ở mức Defocus Blur Severity 3 (-62.1% drop) và $2.1\%$ ở mức Severity 5 (-94.1% collapse). Chúng tôi xây dựng mô hình Perception Proxy mô phỏng sát đường cong suy giảm này để phản ánh sự phụ thuộc của mạng tích chập vào năng lượng biên cạnh tần số cao.

---

### 3. Benchmark (Kết quả đo đạc & Đối chứng)
- **Thiết kế đối chứng:** Cố định mẫu khung hình ADAS cao tốc, áp dụng 4 loại suy giảm chuẩn CVPR 2023 ở 5 mức độ nghiêm trọng (Severity 1 đến 5).
- **Kết quả đo đạc chính:**
  - *Baseline sạch (Clean Severity 0):* Blur score $= 2414.33$, Detector Confidence proxy $= 0.980$, Saturation $= 0.0\%$, Entropy $= 6.51\text{ bits}$. Camera được gán trọng số tối đa $W_{\text{cam}} = 0.70$ (LiDAR fallback $W_{\text{lidar}} = 0.30$).
  - *Defocus Blur Severity 3:* Blur score sụp đổ xuống $4.18$ (-99.8%), Confidence proxy giảm xuống $0.354$ (giảm tương đối $63.9\%$, khớp hoàn hảo với mức giảm $62.1\%$ của bài báo gốc).
  - *Defocus Blur Severity 5:* Blur score $= 1.12$, Confidence proxy $= 0.050$ (mất nhận diện hoàn toàn, tương đương mAP $2.1\%$ của Dong et al.).
- **Độ trễ thời gian thực:** Pipeline đánh giá sức khỏe đạt độ trễ trung bình $1.95\text{ ms}$ (tốc độ $> 400\text{ FPS}$), chỉ chiếm $5.8\%$ ngân sách khung hình $33.3\text{ ms}$ (30 FPS), hoàn toàn khả thi trên phần cứng nhúng ô tô.

---

### 4. Failure Case & Giới hạn
- **Phân biệt hai nguồn bằng chứng:**
  - *Số liệu công bố của Dong et al. (CVPR 2023):* Mạng 3D FCOS3D trên nuScenes-C giảm từ $35.4\%$ Clean xuống $13.4\%$ (S3) và $2.1\%$ (S5).
  - *Số liệu nhóm tự đo đạc tại lớp:* Variance of Laplacian giảm từ $2414.33 \rightarrow 4.18 \rightarrow 1.12$; độ tin cậy proxy giảm tương ứng từ $0.980 \rightarrow 0.354 \rightarrow 0.050$.
- **Giới hạn kỹ thuật:** Phương pháp Variance of Laplacian dựa trên giả định không gian có kết cấu (textured scene). Nếu xe chạy vào đoạn đường nhựa phẳng đồng nhất hoặc nhìn lên bầu trời trống, năng lượng biên cạnh thấp sẽ kích hoạt báo động giả (False Alarm) dù thấu kính hoàn toàn sạch.

---

### 5. Engineering Decision (Quyết định kỹ thuật)
- **Chính sách phân bổ trọng số động (Sensor Down-weighting):**
  - Khi Severity $\le 2$ ($fm \ge 100$): Giữ nguyên trọng số tiêu chuẩn ($W_{\text{cam}} = 0.70, W_{\text{lidar}} = 0.30$).
  - Khi Severity $\ge 3$ ($fm < 100$ hoặc $R_{\text{sat}} > 15\%$): Kích hoạt hạ cấp an toàn: $W_{\text{cam}} \rightarrow 0.05$, đồng thời tăng $W_{\text{lidar}} \rightarrow 0.95$.
- **Khuyến nghị phát triển:** Bổ sung thuật toán Spatial ROIs (chỉ tính blur score trên các vùng có vạch kẻ đường hoặc cọc tiêu) và kết hợp với cảm biến đo mưa/gạt nước để tránh báo động giả trong điều kiện kết cấu thấp.
