import os
import numpy as np
from PIL import Image

def load_grayscale_frames(folder, frame_indices):
    frames = []
    for idx in frame_indices:
        frame_path = os.path.join(folder, f"{idx:04d}.png")
        img = Image.open(frame_path).convert('L')  # Convert to grayscale
        frames.append(np.array(img))
    return np.stack(frames, axis=0)  # Shape: (N, H, W)

def compute_mean_variance(frames):
    mean_img = np.mean(frames, axis=0)
    var_img = np.var(frames, axis=0)
    return mean_img, var_img

def save_image(img, path):
    # Normalize and convert to uint8 for saving
    img_min = img.min()
    img_max = img.max()
    img_norm = ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
    Image.fromarray(img_norm).save(path)

if __name__ == "__main__":
    dataset_root = "dataset"
    results_folder = "results"
    os.makedirs(results_folder, exist_ok=True)

    person3_folder = os.path.join(dataset_root, "person3")
    person1_folder = os.path.join(dataset_root, "person1")
    person3_frames = load_grayscale_frames(person3_folder, range(1, 61))
    person1_frames = load_grayscale_frames(person1_folder, range(1, 71))

    all_bg_frames = np.concatenate([person3_frames, person1_frames], axis=0)  # Shape: (N, H, W)

    mean_img, var_img = compute_mean_variance(all_bg_frames)

    save_image(mean_img, os.path.join(results_folder, "mean.png"))
    save_image(var_img, os.path.join(results_folder, "variance.png"))
