# BÁO CÁO CÁ NHÂN LAB NGÀY 04 — SENSOR REALITY SPRINT
**Học viên:** Võ Đức Tài  
**MSSV:** 2A202603007  
**Vai trò:** Failure Analysis & Fusion Architect  
**Đề tài:** T1 — Camera Degradation Health Score in Autonomous Driving  
**Repository chung của nhóm:** `K4-Track4-Day04-TenNhom-Sensor-Reality-Sprint`  

---

### 1. Problem (Bài toán & Bối cảnh kỹ thuật)
- **Nền tảng & Rủi ro an toàn:** Hệ thống hỗ trợ lái nâng cao ADAS Level 2+ trang bị cảm biến Camera đơn phía trước chịu trách nhiệm chính trong việc phát hiện vật thể, đo Time-to-Collision (TTC) và kích hoạt Phanh khẩn cấp tự động (AEB).
- **Rủi ro khi thiếu cơ chế Health Score:** Trong kiến trúc Late Fusion hoặc Early Fusion thông thường, luồng ảnh bị suy giảm quang học (mờ thấu kính, bão hòa ánh sáng) vẫn được nạp vào mạng nơ-ron nhận diện. Mạng nơ-ron không biết độ tin cậy của dữ liệu đầu vào bị giảm sút, dẫn đến xuất hiện các hộp bao (bounding box) sai lệch vị trí hoặc bỏ sót hoàn toàn xe phía trước, gây tai nạn đâm va đuôi xe trên cao tốc.

---

### 2. Method (Phương pháp & Kiến trúc đánh giá)
- **Cơ sở nghiên cứu:** Dựa trên công bố của Dong và cộng sự tại **CVPR 2023** (*Benchmarking Robustness of 3D Object Detection to Common Corruptions in Autonomous Driving*).
- **Cơ chế Fusion dự phòng:** Trong bài báo CVPR 2023, các tác giả chứng minh rằng mô hình đa cảm biến kết hợp Camera-LiDAR (như TransFusion) có khả năng duy trì độ chính xác cao hơn rất nhiều so với Camera-only (khi gặp Defocus Blur Severity 3, Camera-only mAP giảm từ $35.4\% \rightarrow 13.4\%$, trong khi TransFusion mAP vẫn giữ được trên $58\%$).
- **Chiến lược Dynamic Camera Down-weighting:** Chúng tôi xây dựng hàm suy giảm trọng số liên tục:
  $$W_{\text{cam}} = \max\left( W_{\min}, W_{\text{base}} - (W_{\text{base}} - W_{\min}) \times \text{DegradationIndex} \right)$$
  với $W_{\text{base}} = 0.70$, $W_{\min} = 0.05$. Trọng số của LiDAR/Radar bù trừ tự động: $W_{\text{lidar}} = 1.0 - W_{\text{cam}}$.

---

### 3. Benchmark (Kết quả đo đạc nhóm ghi nhận)
- **Chỉ số trạng thái các mức độ:**
  - Ở trạng thái sạch (Clean): $W_{\text{cam}} = 0.68$, $W_{\text{lidar}} = 0.32$, hệ thống phân loại trạng thái `HEALTHY`.
  - Ở mức Defocus Blur Severity 1: $W_{\text{cam}}$ lập tức giảm xuống $0.14$, chuyển trạng thái sang `WARNING_BLUR`.
  - Ở mức Defocus Blur Severity 3 và 5: $W_{\text{cam}}$ bị ghim chặt ở mức sàn tối thiểu $0.06$ và $0.05$, nhường toàn bộ quyền quyết định phanh khoảng cách an toàn cho LiDAR ($W_{\text{lidar}} = 0.95$).
  - Ở mức Sun Glare Severity 3 đến 5: Độ bão hòa $R_{\text{sat}}$ tăng từ $22.6\%$ lên $43.3\%$, $W_{\text{cam}}$ giảm từ $0.41 \rightarrow 0.14$, trạng thái chuyển thành `WARNING_SATURATION`.

---

### 4. Failure Case Phân Tích Chuyên Sâu (2 Corner Cases Bắt Buộc)
Nhóm đã tạo ra 2 trường hợp biên cực kỳ nguy hiểm để thử thách thuật toán đánh giá sức khỏe cảm biến (Lưu tại `results/corner_case_analysis.json`):

1. **Trường hợp A: Báo động giả do mặt đường thiếu kết cấu (False Alarm on Low Texture):**
   - *Tình huống:* Thấu kính hoàn toàn sạch sẽ, nhưng xe chạy vào đoạn đường nhựa đen phẳng lì, không có vạch kẻ đường hoặc vật thể phía trước (`data/sample_images/corner_case_low_texture.jpg`).
   - *Kết quả đo:* Năng lượng biên cạnh triệt tiêu, Variance of Laplacian sụp đổ xuống chỉ còn **$0.0597$** (thấp hơn cả mức Defocus Blur Severity 5 là $0.62$).
   - *Hệ quả:* Thuật toán nhận diện nhầm là camera bị mờ nghiêm trọng và hạ trọng số camera xuống mức tối thiểu (False Positive Blur Alarm).
   - *Giải pháp khắc phục:* Kiểm tra kết hợp Shannon Entropy ($H = 4.33\text{ bits}$ - dưới ngưỡng thông tin bình thường $5.0\text{ bits}$) và chỉ áp dụng đo độ nét trên các vùng có gradient tự nhiên (vùng chân trời, mép nắp ca-pô xe).

2. **Trường hợp B: Bỏ sót lỗi do nhiễu hạt che giấu độ mờ (Missed Failure via High Noise):**
   - *Tình huống:* Thấu kính bị đọng hơi nước mờ mịt hoàn toàn, nhưng trong điều kiện ban đêm cảm biến CMOS tự động đẩy gain/ISO lên cao tạo ra vô số hạt nhiễu trắng (`data/sample_images/corner_case_noisy_blur.jpg`).
   - *Kết quả đo:* Các hạt nhiễu sắc nhọn tạo ra đạo hàm bậc hai cực lớn, khiến Variance of Laplacian tăng vọt lên **$8768.12$** (cao gấp 10 lần so với ảnh sạch bình thường là $819.89$).
   - *Hệ quả:* Thuật toán báo trạng thái `HEALTHY` dù mắt người và detector hoàn toàn không nhìn thấy vật thể phía trước (False Negative - Bỏ sót lỗi chết người).
   - *Giải pháp khắc phục:* Áp dụng bộ lọc thông thấp (Gaussian/Bilateral filter) để làm mịn nhiễu cao tần trước khi tính toán Laplacian, hoặc theo dõi tính nhất quán thời gian (Temporal Consistency Check) giữa các khung hình liên tiếp.

---

### 5. Engineering Decision & Trade-offs
- **Khi nào NÊN dùng phương án Health Score này:**
  - Áp dụng trên mọi xe ADAS thương mại L2+ chạy vi xử lý nhúng (như NVIDIA Jetson Orin hoặc TI TDA4VM) vì thuật toán tính toán ma trận cổ điển cực kỳ nhẹ, không tiêu tốn tài nguyên GPU dành riêng cho mô hình học sâu.
- **Khi nào KHÔNG NÊN tin tưởng tuyệt đối:**
  - Không thể dùng đơn lẻ một chỉ số Variance of Laplacian trong điều kiện thiếu sáng ban đêm (nhiễu ISO cao) hoặc trên đường cao tốc mới rải nhựa (thiếu texture).
  - Bắt buộc phải kết hợp theo bộ ba: **(Laplacian Blur + Shannon Entropy + Saturation Ratio)** để tự động kiểm tra chéo lẫn nhau.
- **Đồ thị và minh chứng trực quan:** Chi tiết tại collage so sánh trực quan [`plots/visual_comparison_collage.png`](file:///d:/Code/VinAI/Labs/Track4/K4-Track4-Day04-todo-Sensor-Reality-Sprint/plots/visual_comparison_collage.png) và phân phối độ trễ [`plots/latency_distribution.png`](file:///d:/Code/VinAI/Labs/Track4/K4-Track4-Day04-todo-Sensor-Reality-Sprint/plots/latency_distribution.png).
