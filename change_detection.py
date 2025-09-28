import numpy as np
import os
from PIL import Image

def load_grayscale_image(path):
    """Load image as grayscale float32 numpy array."""
    img = Image.open(path).convert('L')
    return np.array(img, dtype=np.float32)

def save_binary_mask(mask, path):
    """Save binary mask (0/1) as black/white PNG."""
    img = Image.fromarray((mask * 255).astype(np.uint8))
    img.save(path)

def detect_foreground_mahalanobis(new_frame, mean_frame, var_frame, threshold=5.0, epsilon=1e-6):
    """
    Detect foreground pixels using Mahalanobis distance.

    Args:
        new_frame (np.ndarray): Current frame (grayscale, shape HxW).
        mean_frame (np.ndarray): Background mean (HxW).
        var_frame (np.ndarray): Background variance (HxW).
        threshold (float): Mahalanobis threshold.
        epsilon (float): Small value to avoid divide-by-zero.

    Returns:
        np.ndarray: Binary mask (HxW), 1=foreground, 0=background.
    """
    mahalanobis = np.abs(new_frame - mean_frame) / (np.sqrt(var_frame) + epsilon)
    mask = (mahalanobis > threshold).astype(np.uint8)
    return mask

if __name__ == "__main__":
    # Load background model (mean, variance) and new frame
    mean_frame = load_grayscale_image("background_mean.png")
    var_frame = load_grayscale_image("background_var.png")
    new_frame = load_grayscale_image("new_frame.png")

    thresholds = [2.0, 5.0, 8.0]
    output_dir = "output_masks"
    os.makedirs(output_dir, exist_ok=True)

    for T in thresholds:
        mask = detect_foreground_mahalanobis(new_frame, mean_frame, var_frame, threshold=T)
        out_path = os.path.join(output_dir, f"mask_T{int(T)}.png")
        save_binary_mask(mask, out_path)

    print("Masks saved for thresholds:", thresholds)