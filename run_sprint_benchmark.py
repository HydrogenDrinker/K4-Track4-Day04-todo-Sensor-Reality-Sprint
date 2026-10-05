"""
Main Benchmark Runner for Sensor Reality Sprint.
Topic: T1 - Camera Degradation Health Score.
Corruptions Grounded in: Dong et al., CVPR 2023 (nuScenes-C Benchmark).
"""

import os
import json
import cv2
import numpy as np
import pandas as pd

from src.camera_health_monitor import CameraHealthMonitor
from src.cvpr2023_corruptions import (
    apply_defocus_blur,
    apply_motion_blur,
    apply_fog,
    apply_sun_glare,
)
from src.perception_proxy import DetectorConfidenceProxy


def draw_hud_overlay(image_bgr: np.ndarray, metrics: dict, corruption_title: str) -> np.ndarray:
    """Draw professional automotive ADAS HUD diagnostics banner."""
    canvas = image_bgr.copy()
    h, w = canvas.shape[:2]

    # Top overlay bar
    overlay = canvas.copy()
    cv2.rectangle(overlay, (0, 0), (w, 85), (20, 20, 25), -1)
    cv2.addWeighted(overlay, 0.78, canvas, 0.22, 0, canvas)

    # Status color
    status = metrics["status"]
    if "HEALTHY" in status:
        status_color = (0, 220, 0)
    elif "WARNING" in status or "ADVISORY" in status:
        status_color = (0, 200, 255)
    else:
        status_color = (0, 0, 255)

    # Text headers
    cv2.putText(canvas, f"CONDITION: {corruption_title.upper()}", (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    cv2.putText(canvas, f"STATUS: {status}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, status_color, 2)

    # Diagnostic numbers
    col2_x = int(w * 0.45)
    col3_x = int(w * 0.72)

    cv2.putText(canvas, f"Blur Score (Laplacian): {metrics['blur_score_laplacian']:.2f}", (col2_x, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)
    cv2.putText(canvas, f"Detector Confidence:    {metrics['detector_confidence']:.3f}", (col2_x, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)

    cv2.putText(canvas, f"Sat Ratio:  {metrics['saturation_ratio'] * 100:.1f}%", (col3_x, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (200, 200, 200), 1)
    cv2.putText(canvas, f"Entropy:    {metrics['shannon_entropy']:.2f} bits", (col3_x, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (200, 200, 200), 1)
    cv2.putText(canvas, f"Cam Weight: {metrics['camera_fusion_weight']:.2f} (LiDAR: {metrics['lidar_fusion_weight']:.2f})", (col3_x, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2)

    return canvas


def main():
    print("=" * 70)
    print("SENSOR REALITY SPRINT: CAMERA DEGRADATION HEALTH BENCHMARK")
    print("Reference: Dong et al., CVPR 2023 (thu-ml/3D_Corruptions_AD)")
    print("=" * 70)

    # Ensure dataset exists
    img_path = os.path.join("data", "sample_images", "adas_highway_clean.jpg")
    if not os.path.exists(img_path):
        import prepare_dataset
        prepare_dataset.main()

    clean_img = cv2.imread(img_path)
    if clean_img is None:
        raise FileNotFoundError(f"Cannot load image from {img_path}")

    monitor = CameraHealthMonitor(blur_threshold=100.0, sat_ratio_threshold=0.15)
    detector = DetectorConfidenceProxy(baseline_clean_conf=0.980)

    # Evaluate Clean Baseline first
    base_metrics = monitor.evaluate_frame(clean_img)
    clean_ref_lap = base_metrics["blur_score_laplacian"]
    base_conf = detector.estimate_confidence(clean_img, reference_laplacian=clean_ref_lap)
    base_metrics["detector_confidence"] = base_conf

    os.makedirs("results/visualizations", exist_ok=True)
    hud_clean = draw_hud_overlay(clean_img, base_metrics, "Baseline Clean Frame")
    cv2.imwrite("results/visualizations/baseline_clean.jpg", hud_clean)

    records = []
    # Add Clean Baseline record
    records.append({
        "run_id": 1,
        "corruption_type": "clean",
        "severity": 0,
        "condition_name": "Baseline Clean",
        "blur_score_laplacian": base_metrics["blur_score_laplacian"],
        "tenengrad_energy": base_metrics["tenengrad_energy"],
        "shannon_entropy": base_metrics["shannon_entropy"],
        "saturation_ratio": base_metrics["saturation_ratio"],
        "detector_confidence": base_conf,
        "camera_fusion_weight": base_metrics["camera_fusion_weight"],
        "lidar_fusion_weight": base_metrics["lidar_fusion_weight"],
        "latency_ms": base_metrics["latency_ms"],
        "status": base_metrics["status"],
    })

    corruption_funcs = {
        "defocus": apply_defocus_blur,
        "motion": apply_motion_blur,
        "fog": apply_fog,
        "glare": apply_sun_glare,
    }

    run_id = 2
    for c_name, c_func in corruption_funcs.items():
        for sev in range(1, 6):
            # Run 2 passes to evaluate latency stability
            for pass_idx in range(2):
                degraded_img = c_func(clean_img, severity=sev)
                m = monitor.evaluate_frame(degraded_img)
                conf = detector.estimate_confidence(degraded_img, reference_laplacian=clean_ref_lap)
                m["detector_confidence"] = conf

                records.append({
                    "run_id": run_id,
                    "corruption_type": c_name,
                    "severity": sev,
                    "condition_name": f"{c_name}_sev_{sev}",
                    "blur_score_laplacian": m["blur_score_laplacian"],
                    "tenengrad_energy": m["tenengrad_energy"],
                    "shannon_entropy": m["shannon_entropy"],
                    "saturation_ratio": m["saturation_ratio"],
                    "detector_confidence": conf,
                    "camera_fusion_weight": m["camera_fusion_weight"],
                    "lidar_fusion_weight": m["lidar_fusion_weight"],
                    "latency_ms": m["latency_ms"],
                    "status": m["status"],
                })
                run_id += 1

            # Save sample HUD visualization
            hud_img = draw_hud_overlay(degraded_img, m, f"{c_name.capitalize()} Severity {sev}")
            cv2.imwrite(f"results/visualizations/{c_name}_sev_{sev}.jpg", hud_img)

    # ----------------------------------------------------
    # Evaluate Corner Cases
    # ----------------------------------------------------
    corner_cases = {}
    low_tex_path = os.path.join("data", "sample_images", "corner_case_low_texture.jpg")
    if os.path.exists(low_tex_path):
        low_tex_img = cv2.imread(low_tex_path)
        m_lt = monitor.evaluate_frame(low_tex_img)
        conf_lt = detector.estimate_confidence(low_tex_img, reference_laplacian=clean_ref_lap)
        m_lt["detector_confidence"] = conf_lt
        hud_lt = draw_hud_overlay(low_tex_img, m_lt, "Corner Case: Flat Low Texture")
        cv2.imwrite("results/visualizations/corner_case_low_texture.jpg", hud_lt)
        corner_cases["low_texture_asphalt"] = {
            "description": "Clean camera lens viewing uniform asphalt (false positive blur alarm).",
            "blur_score_laplacian": m_lt["blur_score_laplacian"],
            "shannon_entropy": m_lt["shannon_entropy"],
            "status": m_lt["status"],
            "failure_mode": "False Alarm (Triggered WARNING_BLUR on clean lens due to lack of edge gradients).",
        }

    noisy_blur_path = os.path.join("data", "sample_images", "corner_case_noisy_blur.jpg")
    if os.path.exists(noisy_blur_path):
        noisy_blur_img = cv2.imread(noisy_blur_path)
        m_nb = monitor.evaluate_frame(noisy_blur_img)
        conf_nb = detector.estimate_confidence(noisy_blur_img, reference_laplacian=clean_ref_lap)
        m_nb["detector_confidence"] = conf_nb
        hud_nb = draw_hud_overlay(noisy_blur_img, m_nb, "Corner Case: Noisy Blur")
        cv2.imwrite("results/visualizations/corner_case_noisy_blur.jpg", hud_nb)
        corner_cases["noisy_blur_masking"] = {
            "description": "Severe optical blur with high ISO sensor noise (false negative failure).",
            "blur_score_laplacian": m_nb["blur_score_laplacian"],
            "shannon_entropy": m_nb["shannon_entropy"],
            "status": m_nb["status"],
            "failure_mode": "Missed Failure (Noise grain creates false high Laplacian variance despite unreadable scene).",
        }

    # Save DataFrame
    df = pd.DataFrame(records)
    csv_path = "results/benchmark_table.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[+] Saved complete benchmark table to {csv_path} ({len(df)} total runs).")

    # Save Summaries
    with open("results/corner_case_analysis.json", "w") as f:
        json.dump(corner_cases, f, indent=2)
    print("[+] Saved corner case analysis to results/corner_case_analysis.json.")

    summary = {
        "baseline_clean": {
            "blur_score_laplacian": clean_ref_lap,
            "detector_confidence": base_conf,
            "shannon_entropy": base_metrics["shannon_entropy"],
            "saturation_ratio": base_metrics["saturation_ratio"],
            "camera_fusion_weight": base_metrics["camera_fusion_weight"],
        },
        "mean_latency_ms": float(df["latency_ms"].mean()),
        "max_latency_ms": float(df["latency_ms"].max()),
        "throughput_fps": float(1000.0 / df["latency_ms"].mean()),
    }
    with open("results/metrics_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[+] Average Latency: {summary['mean_latency_ms']:.2f} ms (~{summary['throughput_fps']:.1f} FPS)")
    print("=" * 70)


if __name__ == "__main__":
    main()
