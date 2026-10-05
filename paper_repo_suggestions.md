# 🔬 Đề xuất Paper/Repo cho 8 chủ đề Lab Sensor Reality Sprint

> [!TIP]
> **Ưu tiên chọn repo có ⭐ (Recommended)** — đây là những repo có code chạy được nhanh, dữ liệu mẫu nhỏ, phù hợp thời gian 120 phút trong lớp.

---

## T1 · Camera Health — Sức khỏe camera thay đổi ra sao?

| # | Tên | Link | Mô tả | Khả thi trong lớp |
|---|---|---|---|---|
| ⭐1 | **Image-Blur-Detection** (Laplacian + BRISQUE) | [github.com/hamzasafdar01/Image-Blur-detection-and-image-quality-check-python](https://github.com/hamzasafdar01/Image-Blur-detection-and-image-quality-check-python) | Tính blur score (Laplacian variance) + BRISQUE quality score cho ảnh. **Input:** ảnh. **Output:** blur score, quality score. | ✅ Rất cao — Python thuần, không cần GPU, chạy ngay trên ảnh bất kỳ. Dễ tạo 3-5 mức blur bằng OpenCV `GaussianBlur`. |
| 2 | **RoboBEV** — BEV Perception Robustness | [github.com/Daniel-xsy/RoboBEV](https://github.com/Daniel-xsy/RoboBEV) | Benchmark đánh giá robustness của các model BEV perception dưới corruption (blur, brightness, fog, snow…). **Input:** nuScenes images + corruption. **Output:** mAP, NDS dưới các mức corruption. | ⚠️ Trung bình — cần tải nuScenes mini (~4GB), cần GPU. Nhưng framework rõ ràng, metric chuẩn. |
| 3 | **Spatially-Varying-Blur-Detection** (CVPR) | [github.com/Utkarsh-Deshmukh/Spatially-Varying-Blur-Detection-python](https://github.com/Utkarsh-Deshmukh/Spatially-Varying-Blur-Detection-python) | Phát hiện vùng blur cục bộ trong ảnh (motion blur trên vật di chuyển). **Input:** ảnh. **Output:** blur map per-pixel. | ✅ Cao — Python, không cần GPU. Có thể visualize vùng blur trên ảnh ADAS. |

---

## T2 · LiDAR Data Loss — LiDAR mất thông tin ở mức nào?

| # | Tên | Link | Mô tả | Khả thi trong lớp |
|---|---|---|---|---|
| ⭐1 | **Robo3D** (CVPR 2023) — 3D Corruption Benchmark | [github.com/thu-ml/3D_Corruptions_AD](https://github.com/thu-ml/3D_Corruptions_AD) | Benchmark corruption cho LiDAR: dropout, noise, fog, rain, motion blur trên KITTI-C, nuScenes-C. **Input:** point cloud. **Output:** mAP, mCE dưới các mức corruption. Paper: Dong et al., CVPR 2023. | ⚠️ Trung bình — cần dataset KITTI/nuScenes. Nhưng script tạo corruption chạy được riêng trên point cloud mẫu nhỏ → đo point density. |
| 2 | **MultiCorrupt** — Multi-modal Corruption | [github.com/ericyinyzy/MultiCorrupt](https://github.com/ericyinyzy/MultiCorrupt) | Tạo corruption đồng thời cho LiDAR + Camera. Có `lidar_converter.py` để generate corrupted point cloud. **Input:** nuScenes point cloud. **Output:** corrupted point cloud + detection metrics. | ⚠️ Trung bình — tương tự Robo3D, nhưng thêm multi-modal. |
| 3 | **Mô phỏng đơn giản bằng Python** (tự viết) | Không cần repo — dùng `numpy` + `open3d` | Tải 1 file `.pcd`/`.bin` mẫu từ KITTI → thêm dropout (random remove % points), Gaussian noise, missing beams. Đo point density theo khoảng cách. | ✅ Rất cao — hoàn toàn tự chủ, không phụ thuộc repo bên ngoài. Dùng KITTI sample (vài MB). |

---

## T3 · Calibration Drift — Lệch calibration ảnh hưởng fusion thế nào?

| # | Tên | Link | Mô tả | Khả thi trong lớp |
|---|---|---|---|---|
| ⭐1 | **direct_visual_lidar_calibration** | [github.com/koide3/direct_visual_lidar_calibration](https://github.com/koide3/direct_visual_lidar_calibration) | Targetless LiDAR-camera calibration, hỗ trợ nhiều loại LiDAR/camera. **Input:** ảnh + point cloud. **Output:** extrinsic matrix, reprojection visualization. | ⚠️ Trung bình — cần build C++/ROS. Nhưng ý tưởng benchmark: perturb extrinsic → đo reprojection error thì có thể tự viết bằng Python. |
| 2 | **CalibRefine** (2025) — Automatic Calibration | [github.com/radar-lab/Lidar_Camera_Automatic_Calibration](https://github.com/radar-lab/Lidar_Camera_Automatic_Calibration) | Online calibration tự động, iterative refinement. **Input:** LiDAR scan + camera image. **Output:** refined extrinsic. Paper gốc đề lab đề cập. | ⚠️ Trung bình — cần dữ liệu LiDAR-camera pairs. |
| ⭐3 | **Mô phỏng calibration perturbation bằng Python** | Không cần repo — dùng `numpy` + `opencv` | Lấy extrinsic matrix mẫu (từ KITTI calib files) → perturb yaw/pitch ±0.5°-2° hoặc translation ±2-10cm → project LiDAR points lên ảnh → đo reprojection error. | ✅ Rất cao — KITTI cung cấp calib files miễn phí. Script ~50 dòng Python. Metric rõ ràng: reprojection error (pixels). |

---

## T4 · Time Sync Offset — Lệch thời gian tạo sai số vị trí bao nhiêu?

| # | Tên | Link | Mô tả | Khả thi trong lớp |
|---|---|---|---|---|
| ⭐1 | **Mô phỏng timestamp offset bằng Python** | Không cần repo — dùng `numpy` + `matplotlib` | Tạo chuyển động 2D/3D đơn giản (vật đi thẳng ở v km/h), thêm offset 50-200ms, tính sai vị trí = v × Δt. Plot error vs offset. | ✅ Rất cao — script <30 dòng. Metric cực rõ: position error (m). Đúng với yêu cầu đề lab. |
| 2 | **lidar_undistortion** (ROS2) | [github.com/ori-drs/lidar_undistortion](https://github.com/ori-drs/lidar_undistortion) | Motion compensation cho LiDAR point cloud bằng pose interpolation. **Input:** raw LiDAR scan + odometry. **Output:** undistorted point cloud. | ❌ Khó — cần ROS2 + hardware setup. Nhưng có thể đọc paper + nêu method trong báo cáo. |
| 3 | **Kalibr** (ETH Zurich) — rolling shutter calibration | [github.com/ethz-asl/kalibr](https://github.com/ethz-asl/kalibr) | Toolbox chuẩn cho visual-inertial calibration, hỗ trợ rolling shutter camera. Huai et al. 2021 mở rộng từ đây. **Input:** camera + IMU data. **Output:** extrinsic, time offset, RS readout time. | ⚠️ Trung bình — cần ROS + calibration target video. Phần mở rộng (rolling shutter) có thể chỉ đọc + trình bày. |

---

## T5 · Radar Pseudo-Label — Kiểm tra pseudo-label radar thế nào?

| # | Tên | Link | Mô tả | Khả thi trong lớp |
|---|---|---|---|---|
| ⭐1 | **autolabelling_radar** | [github.com/radar-lab/autolabelling_radar](https://github.com/radar-lab/autolabelling_radar) | Auto-annotation radar từ camera + LiDAR reference. Pipeline: camera detection → LiDAR 3D box → radar target association. **Input:** multi-sensor data. **Output:** annotated radar targets. | ⚠️ Trung bình — cần dataset đa sensor. Nhưng pipeline logic có thể mô phỏng bằng data giả. |
| 2 | **K-Radar** dataset + tools | [github.com/kaist-avelab/K-Radar](https://github.com/kaist-avelab/K-Radar) | Dataset 4D radar 35K frames với LiDAR + camera. Có tools auto-labeling workflow. **Input:** 4D radar tensor + LiDAR + camera. **Output:** 3D bounding boxes. | ❌ Khó — dataset lớn (~300GB). Nhưng có thể dùng mini split nếu có. |
| ⭐3 | **Mô phỏng pipeline association bằng Python** | Không cần repo | Tạo dataframe: camera class labels + LiDAR 3D box → giả lập radar target → tính agreement score giữa pseudo-label và "ground truth". | ✅ Cao — tự chủ hoàn toàn. Đúng với đề lab: "mô phỏng pipeline camera class + LiDAR 3D box → radar target association". |

---

## T6 · Rangefinder Drone — Báo lỗi khi nào?

| # | Tên | Link | Mô tả | Khả thi trong lớp |
|---|---|---|---|---|
| ⭐1 | **Mô phỏng rangefinder fault bằng Python** | Không cần repo | Tạo chuỗi range giả (altitude hold ~2m) → inject: noise, timeout (NaN), stuck value, out-of-range. So sánh raw vs median filter vs MAD/z-score. **Metric:** range variance, timeout rate. | ✅ Rất cao — script ~80 dòng. Đúng yêu cầu đề lab. Rất trực quan với plot. |
| 2 | **PX4-Autopilot** (SITL simulation) | [github.com/PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) | Firmware PX4. Có SITL với rangefinder model (`gz_x500_lidar_down`). Dùng PyMAVLink đọc `DISTANCE_SENSOR`. | ⚠️ Trung bình — cần cài PX4 SITL + Gazebo (nặng). Nhưng nếu đã có sẵn thì rất tốt. |
| 3 | **PX4 Distance Sensors documentation** | [docs.px4.io/main/en/sensor/rangefinders.html](https://docs.px4.io/main/en/sensor/rangefinders.html) | Tài liệu chính thức về LiDAR-Lite, sonar, TeraRanger trên drone PX4. Ghi rõ hạn chế từng loại sensor. | ✅ Dùng làm reference — nêu spec, limitation trong báo cáo. Kết hợp với mô phỏng ở mục 1. |

---

## T7 · Multi-Camera Bottleneck — Nghẽn ở đâu?

| # | Tên | Link | Mô tả | Khả thi trong lớp |
|---|---|---|---|---|
| ⭐1 | **Benchmark webcam bằng OpenCV** | Không cần repo — dùng `opencv-python` | Mở webcam ở 2-3 resolution (640×480, 1280×720, 1920×1080) → đo FPS thực tế, latency (timestamp delta), CPU load (`psutil`). Tính bandwidth = W×H×FPS×bytes/pixel. | ✅ Rất cao — cần 1 webcam. Script ~40 dòng. Metric cực rõ: FPS, latency, bandwidth. |
| 2 | **jetson-multicamera-pipelines** (NVIDIA) | [github.com/NVIDIA-AI-IOT/jetson-multicamera-pipelines](https://github.com/NVIDIA-AI-IOT/jetson-multicamera-pipelines) | Pipeline multi-camera trên Jetson: capture → preprocess → DNN → encode. Dùng GStreamer + DeepStream. | ❌ Khó — cần Jetson hardware. Nhưng tốt để reference architecture trong báo cáo. |
| ⭐3 | **Ước lượng bandwidth bằng bảng tính** | Không cần repo — dùng spreadsheet/Python | Tính: bandwidth = N_cam × W × H × FPS × bit_per_pixel. So sánh với bandwidth giới hạn: USB3 (5Gbps), CSI-2 (per lane), GigE (1Gbps), GMSL2 (6Gbps). | ✅ Rất cao — đúng yêu cầu đề lab. Kết hợp với benchmark webcam thực tế. |

---

## T8 · Rare Case Mining — Clip hiếm nào đáng gán nhãn trước?

| # | Tên | Link | Mô tả | Khả thi trong lớp |
|---|---|---|---|---|
| ⭐1 | **Mô phỏng data loop bằng pandas** | Không cần repo | Tạo dataframe log: weather, time_of_day, blur_score, lidar_density, detector_confidence, near_miss_flag. Viết rules/query chọn top-k clip. **Metric:** slice coverage, % rare cases captured. | ✅ Rất cao — đúng yêu cầu đề lab: "Tạo dataframe log giả lập". Script ~60 dòng. |
| 2 | **Awesome-Data-Centric-Autonomous-Driving** | [github.com/LincanLi-X/Awesome-Data-Centric-Autonomous-Driving](https://github.com/LincanLi-X/Awesome-Data-Centric-Autonomous-Driving) | Survey toàn diện về data-centric AD: data mining, auto-labeling, closed-loop. Có danh sách paper + code. | ✅ Tốt làm reference — tìm paper/method cụ thể trong danh sách này. |
| 3 | **nuScenes mini dataset + metadata query** | [nuscenes.org/nuscenes](https://www.nuscenes.org/nuscenes) | nuScenes mini (~4GB) có metadata: weather, time_of_day, location. Có thể query scene attributes → chọn rare scenes. | ⚠️ Trung bình — cần tải ~4GB. Nhưng metadata query rất phù hợp với đề bài. |

---

## 📊 Tổng hợp: Chủ đề nào dễ chạy nhất trong 120 phút?

| Chủ đề | Độ khả thi | Lý do |
|---|---|---|
| **T1** Camera Health | ⭐⭐⭐⭐⭐ | Chỉ cần Python + ảnh bất kỳ. Blur score bằng Laplacian. |
| **T4** Time Sync | ⭐⭐⭐⭐⭐ | Mô phỏng thuần toán, script cực ngắn. |
| **T6** Rangefinder | ⭐⭐⭐⭐⭐ | Mô phỏng chuỗi range + filter, rất trực quan. |
| **T8** Rare Case Mining | ⭐⭐⭐⭐ | Tạo dataframe + query, không cần GPU. |
| **T7** Multi-Camera | ⭐⭐⭐⭐ | Cần webcam, nhưng code đơn giản. |
| **T3** Calibration | ⭐⭐⭐ | Cần hiểu extrinsic matrix, KITTI calib files. |
| **T2** LiDAR | ⭐⭐⭐ | Cần point cloud data, nhưng corruption script đơn giản. |
| **T5** Radar | ⭐⭐ | Khó nhất vì ít dữ liệu radar công khai nhỏ. |
