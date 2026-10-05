"""
CVPR 2023 Autonomous Driving Camera Corruptions Generator.
Reference: Dong et al., "Benchmarking Robustness of 3D Object Detection to Common Corruptions in Autonomous Driving", CVPR 2023.
Official Repo: thu-ml/3D_Corruptions_AD
"""

import cv2
import numpy as np
from scipy.ndimage import convolve


def disk_kernel(radius: int) -> np.ndarray:
    """Generate a normalized 2D circular pillbox/disk kernel for defocus blur."""
    diameter = 2 * radius + 1
    y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
    mask = x**2 + y**2 <= radius**2
    kernel = np.zeros((diameter, diameter), dtype=np.float32)
    kernel[mask] = 1.0
    return kernel / np.sum(kernel)


def motion_blur_kernel(length: int, angle_deg: float = 45.0) -> np.ndarray:
    """Generate a directional linear motion blur kernel."""
    kernel = np.zeros((length, length), dtype=np.float32)
    center = length // 2
    angle_rad = np.deg2rad(angle_deg)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    for i in range(length):
        offset = i - center
        x = int(round(center + offset * cos_a))
        y = int(round(center + offset * sin_a))
        if 0 <= x < length and 0 <= y < length:
            kernel[y, x] = 1.0
    if kernel.sum() == 0:
        kernel[center, center] = 1.0
    return kernel / kernel.sum()


def apply_defocus_blur(image_bgr: np.ndarray, severity: int = 1) -> np.ndarray:
    """
    Dong et al. (CVPR 2023) Defocus Blur: Disk kernel radius [3, 5, 7, 10, 16].
    """
    if severity <= 0:
        return image_bgr.copy()
    radius_map = {1: 3, 2: 5, 3: 7, 4: 10, 5: 16}
    radius = radius_map.get(severity, 7)
    kernel = disk_kernel(radius)
    res = np.zeros_like(image_bgr, dtype=np.float32)
    for c in range(3):
        res[:, :, c] = convolve(image_bgr[:, :, c].astype(np.float32), kernel)
    return np.clip(res, 0, 255).astype(np.uint8)


def apply_motion_blur(image_bgr: np.ndarray, severity: int = 1) -> np.ndarray:
    """
    Dong et al. (CVPR 2023) Motion Blur: Kernel length [10, 15, 20, 28, 40].
    """
    if severity <= 0:
        return image_bgr.copy()
    length_map = {1: 10, 2: 15, 3: 20, 4: 28, 5: 40}
    length = length_map.get(severity, 20)
    kernel = motion_blur_kernel(length, angle_deg=30.0)
    res = np.zeros_like(image_bgr, dtype=np.float32)
    for c in range(3):
        res[:, :, c] = convolve(image_bgr[:, :, c].astype(np.float32), kernel)
    return np.clip(res, 0, 255).astype(np.uint8)


def apply_fog(image_bgr: np.ndarray, severity: int = 1) -> np.ndarray:
    """
    Atmospheric scattering fog: I = I * t + A * (1 - t).
    Severity controls optical extinction depth.
    """
    if severity <= 0:
        return image_bgr.copy()
    beta_map = {1: 0.04, 2: 0.08, 3: 0.14, 4: 0.22, 5: 0.35}
    beta = beta_map.get(severity, 0.14)
    h, w = image_bgr.shape[:2]
    y = np.linspace(0.2, 1.0, h)[:, None]
    transmission = np.exp(-beta * y * 15.0)
    transmission = np.repeat(transmission[:, :, None], 3, axis=2)
    airlight = np.array([230.0, 235.0, 240.0], dtype=np.float32)
    img_f = image_bgr.astype(np.float32)
    fogged = img_f * transmission + airlight * (1.0 - transmission)
    return np.clip(fogged, 0, 255).astype(np.uint8)


def apply_sun_glare(image_bgr: np.ndarray, severity: int = 1) -> np.ndarray:
    """
    Direct low-angle solar glare saturation on camera lens.
    """
    if severity <= 0:
        return image_bgr.copy()
    intensity_map = {1: 80, 2: 130, 3: 180, 4: 220, 5: 255}
    radius_fraction = {1: 0.3, 2: 0.45, 3: 0.60, 4: 0.75, 5: 0.95}
    intensity = intensity_map.get(severity, 180)
    rad_frac = radius_fraction.get(severity, 0.60)

    h, w = image_bgr.shape[:2]
    mask = np.zeros((h, w), dtype=np.float32)
    center = (int(w * 0.75), int(h * 0.25))
    max_dist = np.sqrt(h**2 + w**2) * rad_frac
    y, x = np.ogrid[:h, :w]
    dist = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
    glare_profile = np.clip(1.0 - (dist / max_dist), 0.0, 1.0) ** 1.8
    glare_layer = (glare_profile[:, :, None] * intensity).astype(np.float32)

    res = image_bgr.astype(np.float32) + glare_layer
    return np.clip(res, 0, 255).astype(np.uint8)
