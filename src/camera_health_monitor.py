"""
Camera Degradation Health Monitor for ADAS Perception Stack.
Topic: T1 - Camera Degradation Health Score.
Reference Paper: Dong et al., CVPR 2023 (Benchmarking Robustness of 3D Object Detection to Common Corruptions in Autonomous Driving).
"""

import time
import cv2
import numpy as np


class CameraHealthMonitor:
    """
    Lightweight, real-time sensor health monitor for front-facing automotive camera.
    Measures:
      1. Blur Score (Variance of Laplacian - Focus Measure)
      2. Tenengrad Gradient Energy (Sobel)
      3. Shannon Information Entropy (bits/pixel)
      4. Saturation Ratio (under/over-exposed pixel fraction)
      5. Execution Latency (ms)
      6. Dynamic Camera Weight (W_cam in [0.05, 0.70])
    """

    def __init__(
        self,
        blur_threshold: float = 100.0,
        entropy_low_threshold: float = 5.0,
        sat_ratio_threshold: float = 0.15,
        base_camera_weight: float = 0.70,
        min_camera_weight: float = 0.05,
    ):
        self.blur_threshold = blur_threshold
        self.entropy_low_threshold = entropy_low_threshold
        self.sat_ratio_threshold = sat_ratio_threshold
        self.base_camera_weight = base_camera_weight
        self.min_camera_weight = min_camera_weight

    def evaluate_frame(self, frame_bgr: np.ndarray) -> dict:
        """
        Evaluate single frame health.
        Returns detailed metrics and camera fusion weight.
        """
        t_start = time.perf_counter()

        if frame_bgr is None or frame_bgr.size == 0:
            raise ValueError("Input frame is empty or invalid.")

        # Convert to Grayscale
        if len(frame_bgr.shape) == 3 and frame_bgr.shape[2] == 3:
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame_bgr

        # 1. Variance of Laplacian (Focus Measure)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        var_laplacian = float(laplacian.var())

        # 2. Tenengrad Gradient Energy (Sobel)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        tenengrad = float(np.mean(sobel_x**2 + sobel_y**2))

        # 3. Shannon Entropy
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
        hist_norm = hist / (hist.sum() + 1e-12)
        nonzero = hist_norm[hist_norm > 0]
        entropy = float(-np.sum(nonzero * np.log2(nonzero)))

        # 4. Saturation Ratio (Under-exposed < 10 or Over-exposed > 245)
        total_pixels = float(gray.size)
        under_exposed = np.sum(gray < 10)
        over_exposed = np.sum(gray > 245)
        saturation_ratio = float((under_exposed + over_exposed) / total_pixels)

        # 5. Sensor Health Assessment & Dynamic Weighting
        is_blurred = var_laplacian < self.blur_threshold
        is_saturated = saturation_ratio > self.sat_ratio_threshold
        is_low_info = entropy < self.entropy_low_threshold

        # Degradation Severity Proxy [0.0 (clean) -> 1.0 (dead)]
        blur_penalty = np.clip(1.0 - (var_laplacian / max(self.blur_threshold, 1e-3)), 0.0, 1.0)
        sat_penalty = np.clip(saturation_ratio / 0.50, 0.0, 1.0)
        degradation_index = float(max(blur_penalty, sat_penalty))

        # Dynamic Camera Fusion Weight: W_cam
        # Drops from base_camera_weight (0.70) down to min_camera_weight (0.05)
        w_cam = float(
            self.base_camera_weight - (self.base_camera_weight - self.min_camera_weight) * degradation_index
        )
        w_cam = np.clip(w_cam, self.min_camera_weight, self.base_camera_weight)

        status = "HEALTHY"
        if is_blurred and is_saturated:
            status = "CRITICAL_BLUR_SATURATED"
        elif is_blurred:
            status = "WARNING_BLUR"
        elif is_saturated:
            status = "WARNING_SATURATION"
        elif is_low_info:
            status = "ADVISORY_LOW_TEXTURE"

        latency_ms = (time.perf_counter() - t_start) * 1000.0

        return {
            "status": status,
            "blur_score_laplacian": var_laplacian,
            "tenengrad_energy": tenengrad,
            "shannon_entropy": entropy,
            "saturation_ratio": saturation_ratio,
            "degradation_index": degradation_index,
            "camera_fusion_weight": w_cam,
            "lidar_fusion_weight": 1.0 - w_cam,
            "latency_ms": latency_ms,
            "is_blurred": bool(is_blurred),
            "is_saturated": bool(is_saturated),
        }
