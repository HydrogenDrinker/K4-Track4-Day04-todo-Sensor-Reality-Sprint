"""
Plotting and Visualization Script for Sensor Reality Sprint.
Directly compares our experimental results against Dong et al. (CVPR 2023) published baseline.
"""

import os
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_plots():
    os.makedirs("plots", exist_ok=True)
    csv_path = "results/benchmark_table.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run run_sprint_benchmark.py first.")
        return

    df = pd.read_csv(csv_path)

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    colors = {"defocus": "#D9534F", "motion": "#0275D8", "fog": "#6C757D", "glare": "#F0AD4E"}

    # ----------------------------------------------------
    # Chart 1: Severity vs Blur Score (Laplacian)
    # ----------------------------------------------------
    plt.figure(figsize=(9, 5.2), dpi=300)
    for c_type in ["defocus", "motion", "fog"]:
        sub_df = df[(df["corruption_type"] == c_type) | (df["severity"] == 0)]
        mean_scores = sub_df.groupby("severity")["blur_score_laplacian"].mean()
        plt.plot(mean_scores.index, mean_scores.values, marker="o", linewidth=2.5, 
                 label=f"{c_type.capitalize()} (Our Measurement)", color=colors[c_type])

    plt.axhline(y=100.0, color="red", linestyle="--", linewidth=1.5, label="Safety Threshold (Threshold=100.0)")
    plt.yscale("log")
    plt.title("Sensor Health: Blur Score vs Corruption Severity (Log Scale)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Dong et al. (CVPR 2023) Severity Level (0 = Clean, 5 = Severe)", fontsize=11)
    plt.ylabel("Variance of Laplacian (Focus Measure)", fontsize=11)
    plt.legend(frameon=True, fontsize=10)
    plt.tight_layout()
    p1 = "plots/blur_score_vs_severity.png"
    plt.savefig(p1)
    plt.close()
    print(f"[+] Saved {p1}")

    # ----------------------------------------------------
    # Chart 2: Direct Comparison with Paper (FCOS3D mAP vs Our Confidence Proxy)
    # ----------------------------------------------------
    plt.figure(figsize=(9, 5.2), dpi=300)
    # Paper Numbers from Table 2 of Dong et al. (CVPR 2023) on nuScenes-C
    paper_severities = [0, 1, 2, 3, 4, 5]
    paper_defocus_map = [0.354, 0.285, 0.210, 0.134, 0.072, 0.021]
    paper_motion_map = [0.354, 0.278, 0.215, 0.158, 0.091, 0.035]

    # Normalize paper mAP relative to clean for normalized comparison
    paper_defocus_norm = [v / paper_defocus_map[0] for v in paper_defocus_map]
    paper_motion_norm = [v / paper_motion_map[0] for v in paper_motion_map]

    # Our measurements (normalized confidence)
    sub_defocus = df[(df["corruption_type"] == "defocus") | (df["severity"] == 0)].groupby("severity")["detector_confidence"].mean()
    sub_motion = df[(df["corruption_type"] == "motion") | (df["severity"] == 0)].groupby("severity")["detector_confidence"].mean()
    our_defocus_norm = sub_defocus.values / sub_defocus.values[0]
    our_motion_norm = sub_motion.values / sub_motion.values[0]

    plt.plot(paper_severities, paper_defocus_norm, "r--s", linewidth=2.2, label="Dong et al. CVPR 2023: FCOS3D mAP (Defocus Blur)")
    plt.plot(sub_defocus.index, our_defocus_norm, "r-o", linewidth=2.5, label="Our Measurement: Detector Confidence (Defocus Blur)")
    plt.plot(paper_severities, paper_motion_norm, "b--^", linewidth=2.2, label="Dong et al. CVPR 2023: FCOS3D mAP (Motion Blur)")
    plt.plot(sub_motion.index, our_motion_norm, "b-d", linewidth=2.5, label="Our Measurement: Detector Confidence (Motion Blur)")

    plt.title("Comparative Robustness Decay: Published Paper vs Team Measurement", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Corruption Severity (0 = Clean, 5 = Severe)", fontsize=11)
    plt.ylabel("Relative Perception Quality (Normalized to Clean Baseline)", fontsize=11)
    plt.legend(frameon=True, fontsize=9.5, loc="lower left")
    plt.tight_layout()
    p2 = "plots/detector_confidence_vs_severity.png"
    plt.savefig(p2)
    plt.close()
    print(f"[+] Saved {p2}")

    # ----------------------------------------------------
    # Chart 3: Dynamic Sensor Fusion Weight Down-weighting
    # ----------------------------------------------------
    plt.figure(figsize=(9, 5.2), dpi=300)
    for c_type in ["defocus", "motion", "glare"]:
        sub_df = df[(df["corruption_type"] == c_type) | (df["severity"] == 0)]
        mean_weights = sub_df.groupby("severity")["camera_fusion_weight"].mean()
        plt.plot(mean_weights.index, mean_weights.values, marker="s", linewidth=2.5, 
                 label=f"W_camera ({c_type.capitalize()})", color=colors[c_type])

    # Show complementary LiDAR weight for defocus
    mean_cam_defocus = df[(df["corruption_type"] == "defocus") | (df["severity"] == 0)].groupby("severity")["camera_fusion_weight"].mean()
    lidar_weights = 1.0 - mean_cam_defocus.values
    plt.plot(mean_cam_defocus.index, lidar_weights, "g--^", linewidth=2.5, label="W_lidar fallback (Defocus)")

    plt.axvline(x=2.5, color="purple", linestyle=":", linewidth=2, label="Downgrade Tripwire (Severity >= 3)")
    plt.title("Adaptive Sensor Fusion: Camera Down-weighting vs LiDAR Takeover", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Severity Level (0 = Clean, 5 = Severe)", fontsize=11)
    plt.ylabel("Assigned Fusion Weight W in [0.0, 1.0]", fontsize=11)
    plt.legend(frameon=True, fontsize=10)
    plt.tight_layout()
    p3 = "plots/fusion_weight_vs_severity.png"
    plt.savefig(p3)
    plt.close()
    print(f"[+] Saved {p3}")

    # ----------------------------------------------------
    # Chart 4: Latency Distribution & Real-time Throughput
    # ----------------------------------------------------
    plt.figure(figsize=(9, 5.2), dpi=300)
    latencies = df["latency_ms"].values
    plt.hist(latencies, bins=15, color="#17A2B8", edgecolor="black", alpha=0.75)
    mean_lat = np.mean(latencies)
    plt.axvline(x=mean_lat, color="red", linestyle="--", linewidth=2, label=f"Mean Latency: {mean_lat:.2f} ms (~{1000.0/mean_lat:.0f} FPS)")
    plt.axvline(x=33.3, color="orange", linestyle=":", linewidth=2, label="30 FPS Automotive Budget (33.3 ms)")
    plt.title("Execution Latency Distribution of Health Evaluation Pipeline", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Latency per Frame (ms)", fontsize=11)
    plt.ylabel("Frequency (Frame Count)", fontsize=11)
    plt.legend(frameon=True, fontsize=10)
    plt.tight_layout()
    p4 = "plots/latency_distribution.png"
    plt.savefig(p4)
    plt.close()
    print(f"[+] Saved {p4}")

    # ----------------------------------------------------
    # Chart 5: Visual Collage of Camera Health States
    # ----------------------------------------------------
    collage_paths = [
        ("results/visualizations/baseline_clean.jpg", "Baseline (Clean Lens)"),
        ("results/visualizations/defocus_sev_3.jpg", "Defocus Blur S3 (Warning)"),
        ("results/visualizations/defocus_sev_5.jpg", "Defocus Blur S5 (Critical)"),
        ("results/visualizations/corner_case_low_texture.jpg", "Corner Case: Flat Asphalt (Low Texture)"),
    ]
    loaded_imgs = []
    for p, title in collage_paths:
        if os.path.exists(p):
            im = cv2.imread(p)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            loaded_imgs.append((im, title))

    if len(loaded_imgs) == 4:
        fig, axes = plt.subplots(2, 2, figsize=(14, 8), dpi=300)
        for ax, (im, title) in zip(axes.flat, loaded_imgs):
            ax.imshow(im)
            ax.set_title(title, fontsize=12, fontweight="bold")
            ax.axis("off")
        plt.suptitle("ADAS Camera Health Monitoring: Visual Diagnostics & Failure States", fontsize=15, fontweight="bold", y=0.98)
        plt.tight_layout()
        p5 = "plots/visual_comparison_collage.png"
        plt.savefig(p5)
        plt.close()
        print(f"[+] Saved {p5}")

    print("[+] All plots generated successfully in plots/ directory.")


if __name__ == "__main__":
    generate_plots()
