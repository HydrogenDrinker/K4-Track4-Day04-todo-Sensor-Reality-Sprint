# THÀNH VIÊN NHÓM THỰC HIỆN LAB NGÀY 04
## Topic: T1 - Camera Degradation Health Score in Autonomous Driving
**Khoa / Lớp:** K4-Track4  
**Học phần:** Cảm biến chuỗi khung hình - thời gian (Sensor Reality Sprint)  
**Tên nhóm:** Nhóm 03 (Camera Health ADAS)  
**Quy mô nhóm:** 3 thành viên  

---

### Danh sách thành viên và phân công nhiệm vụ

| STT | Họ và tên | MSSV | Vai trò chính trong Sprint | Nhiệm vụ cụ thể |
| :---: | :--- | :---: | :--- | :--- |
| **1** | **Phạm Thị Ngọc Anh** | **2A202602831** | **Team Leader & Perception Lead** | Khảo sát nghiên cứu gốc Dong et al. (CVPR 2023 Table 2 FCOS3D nuScenes-C), xây dựng Perception Proxy mô phỏng độ suy giảm confidence của detector 3D, viết phần Problem & Method trong báo cáo, đại diện Pitching mở đầu. |
| **2** | **Đỗ Đình Long** | **2A202602673** | **Sensor Pipeline & Benchmark Engineer** | Triển khai module đo Laplacian Blur Score, Sobel Tenengrad, Shannon Entropy và Saturation Ratio; chạy benchmark 42 điều kiện và đo kiểm tra độ trễ (latency < 2ms), vẽ đồ thị đối sánh. |
| **3** | **Võ Đức Tài** | **2A202603007** | **Failure Analysis & Fusion Architect** | Phân tích 2 trường hợp ngoại lệ (Corner Cases: Low-texture asphalt False Positive và Noise-masked Blur False Negative); thiết kế chính sách Dynamic Camera Down-weighting và chuyển giao LiDAR/Radar fallback. |

---

### Thông tin Repository chung
- **Đường dẫn thư mục dự án:** `K4-Track4-Day04-todo-Sensor-Reality-Sprint/`
- **Mã nguồn chính:** `src/camera_health_monitor.py`, `src/cvpr2023_corruptions.py`, `src/perception_proxy.py`
- **Tập lệnh chạy đối chứng:** `run_sprint_benchmark.py`, `plot_results.py`
- **Báo cáo chung:** `REPORT.md`
- **Báo cáo cá nhân nộp VLearn:** `reports/REPORT_Member1_PhamThiNgocAnh.md`, `reports/REPORT_Member2_DoDinhLong.md`, `reports/REPORT_Member3_VoDucTai.md`
