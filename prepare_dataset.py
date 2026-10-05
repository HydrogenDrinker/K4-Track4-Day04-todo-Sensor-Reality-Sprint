"""
Prepare synthetic and benchmark images for ADAS Camera Degradation Sprint.
Generates:
  1. adas_highway_clean.jpg: Realistic clean highway forward camera frame (cars, lane markers, horizon, trees).
  2. corner_case_low_texture.jpg: Clean lens but uniform flat asphalt (tests false alarm on low texture).
  3. corner_case_noisy_blur.jpg: Severely blurred frame with high ISO grain noise (tests false negative failure).
"""

import os
import cv2
import numpy as np


def generate_clean_adas_frame(width=1280, height=720) -> np.ndarray:
    """Generate high-fidelity ADAS highway camera frame."""
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # 1. Sky Gradient (top 45%)
    sky_h = int(height * 0.45)
    for y in range(sky_h):
        r = int(180 + (220 - 180) * (y / sky_h))
        g = int(200 + (230 - 200) * (y / sky_h))
        b = int(240 + (255 - 240) * (y / sky_h))
        img[y, :] = (b, g, r)

    # Distant Horizon & Trees / Hills
    for x in range(width):
        hill_h = int(25 * np.sin(x * 0.015) + 15 * np.cos(x * 0.035))
        img[sky_h - 40 - hill_h : sky_h, x] = (40, 90, 50)

    # 2. Road Asphalt (bottom 55%)
    for y in range(sky_h, height):
        factor = (y - sky_h) / (height - sky_h)
        base_gray = int(75 + 25 * factor)
        img[y, :] = (base_gray, base_gray, base_gray)

    # Road grain texture
    road_noise = np.random.normal(0, 4, (height - sky_h, width, 3)).astype(np.int16)
    road_area = img[sky_h:height, :].astype(np.int16) + road_noise
    img[sky_h:height, :] = np.clip(road_area, 0, 255).astype(np.uint8)

    # 3. Perspective Lane Markings
    vp_x, vp_y = width // 2, sky_h - 10
    # Left solid line
    cv2.line(img, (vp_x - 30, vp_y), (int(width * 0.15), height), (255, 255, 255), 7)
    # Right solid line
    cv2.line(img, (vp_x + 30, vp_y), (int(width * 0.85), height), (255, 255, 255), 7)
    # Dashed center line
    dash_segments = 12
    for i in range(dash_segments):
        t0 = (i + 0.2) / dash_segments
        t1 = (i + 0.8) / dash_segments
        if i % 2 == 0:
            p0 = (int(vp_x + (width * 0.50 - vp_x) * t0), int(vp_y + (height - vp_y) * t0))
            p1 = (int(vp_x + (width * 0.50 - vp_x) * t1), int(vp_y + (height - vp_y) * t1))
            thickness = max(2, int(6 * t1))
            cv2.line(img, p0, p1, (50, 240, 255), thickness)

    # 4. Lead Vehicles (Forward 3D Targets)
    # Lead Car 1 (Center Lane)
    car1_x, car1_y, c_w, c_h = vp_x - 55, int(height * 0.58), 120, 80
    cv2.rectangle(img, (car1_x, car1_y), (car1_x + c_w, car1_y + c_h), (30, 30, 180), -1)  # Red Car
    cv2.rectangle(img, (car1_x + 10, car1_y - 25), (car1_x + c_w - 10, car1_y), (60, 60, 60), -1)  # Cabin
    cv2.rectangle(img, (car1_x + 15, car1_y - 22), (car1_x + c_w - 15, car1_y - 2), (180, 220, 240), -1)  # Window
    cv2.circle(img, (car1_x + 18, car1_y + c_h - 15), 10, (20, 20, 220), -1)  # Tail light
    cv2.circle(img, (car1_x + c_w - 18, car1_y + c_h - 15), 10, (20, 20, 220), -1)
    cv2.rectangle(img, (car1_x + 40, car1_y + c_h - 18), (car1_x + c_w - 40, car1_y + c_h - 4), (240, 240, 240), -1)  # License plate

    # Lead Car 2 (Right Lane ahead)
    car2_x, car2_y, c2_w, c2_h = int(width * 0.65), int(height * 0.53), 70, 48
    cv2.rectangle(img, (car2_x, car2_y), (car2_x + c2_w, car2_y + c2_h), (160, 150, 50), -1)  # Blue/cyan car
    cv2.rectangle(img, (car2_x + 8, car2_y - 16), (car2_x + c2_w - 8, car2_y), (50, 50, 50), -1)

    # Overhead Highway Sign
    cv2.rectangle(img, (int(width * 0.35), int(height * 0.12)), (int(width * 0.65), int(height * 0.28)), (30, 120, 40), -1)
    cv2.rectangle(img, (int(width * 0.35), int(height * 0.12)), (int(width * 0.65), int(height * 0.28)), (255, 255, 255), 2)
    cv2.putText(img, "VINFAST ADAS HWY 01", (int(width * 0.37), int(height * 0.22)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return img


def generate_corner_cases(clean_frame: np.ndarray, out_dir: str):
    """Generate 2 anomaly corner cases."""
    # Corner Case A: Low Texture (Flat Asphalt)
    h, w = clean_frame.shape[:2]
    low_tex = np.full((h, w, 3), 110, dtype=np.uint8)
    smooth_gradient = np.linspace(100, 120, h)[:, None, None].astype(np.uint8)
    low_tex = np.repeat(smooth_gradient, w, axis=1)
    # Extremely subtle smooth gradient, no sharp edges
    cv2.imwrite(os.path.join(out_dir, "corner_case_low_texture.jpg"), low_tex)

    # Corner Case B: Severe Blur with High ISO Sensor Noise
    blurred = cv2.GaussianBlur(clean_frame, (45, 45), 18.0)
    noise = np.random.normal(0, 32, (h, w, 3)).astype(np.float32)
    noisy_blur = np.clip(blurred.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(out_dir, "corner_case_noisy_blur.jpg"), noisy_blur)


def main():
    out_dir = os.path.join("data", "sample_images")
    os.makedirs(out_dir, exist_ok=True)

    clean_img = generate_clean_adas_frame()
    clean_path = os.path.join(out_dir, "adas_highway_clean.jpg")
    cv2.imwrite(clean_path, clean_img)
    print(f"Generated clean baseline: {clean_path}")

    generate_corner_cases(clean_img, out_dir)
    print("Generated corner case images (low_texture and noisy_blur).")


if __name__ == "__main__":
    main()
