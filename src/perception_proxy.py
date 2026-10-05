"""
Perception Proxy for Downstream Object Detector Confidence.
Calibrated to simulate CNN low-level feature extraction degradation under camera corruptions.
Ground truth reference: Dong et al. (CVPR 2023), Table 2 (FCOS3D mAP degradation on nuScenes-C).
"""

import cv2
import numpy as np


class DetectorConfidenceProxy:
    """
    Simulates monocular 3D detector confidence (e.g. FCOS3D / CenterNet).
    Deep learning detectors rely heavily on high-frequency edge gradients and local contrast
    for bounding box regression and classification logits.
    """

    def __init__(self, baseline_clean_conf: float = 0.980):
        self.baseline_clean_conf = baseline_clean_conf

    def estimate_confidence(self, image_bgr: np.ndarray, reference_laplacian: float = 2400.0) -> float:
        """
        Calculates proxy confidence in [0.0, 1.0].
        Under severe blur/glare, gradient suppression causes confidence collapse.
        """
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        var_lap = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # Saturation check
        over_exposed = np.mean(gray > 245)
        under_exposed = np.mean(gray < 10)
        sat_fraction = over_exposed + under_exposed

        # Log ratio of focus measure relative to clean baseline
        rel_focus = np.clip(var_lap / max(reference_laplacian, 1.0), 1e-4, 1.0)
        focus_factor = (rel_focus) ** 0.35

        # Saturation penalty
        sat_factor = np.clip(1.0 - 1.8 * sat_fraction, 0.05, 1.0)

        conf = self.baseline_clean_conf * focus_factor * sat_factor
        return float(np.clip(conf, 0.05, 0.99))
