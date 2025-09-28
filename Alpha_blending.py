import numpy as np
import imageio
from scipy.ndimage import gaussian_filter

def create_alpha_mask(foreground_mask, blur_ksize=21):
    """
    Create a smooth alpha mask from a binary foreground mask.
    Args:
        foreground_mask: Binary mask (uint8, 0 or 255).
        blur_ksize: Kernel size for Gaussian blur.
    Returns:
        alpha_mask: Float mask in [0,1], blurred at edges.
    """
    # Normalize mask to [0,1]
    alpha = foreground_mask.astype(np.float32) / 255.0
    # Smooth edges using scipy.ndimage.gaussian_filter
    sigma = blur_ksize / 6.0  # Approximate conversion from kernel size to sigma
    alpha = gaussian_filter(alpha, sigma=sigma)
    # Clip to [0,1]
    alpha = np.clip(alpha, 0, 1)
    return alpha

def alpha_blend(frame, background, alpha_mask):
    """
    Blend frame and background using alpha mask.
    Args:
        frame: Original frame (H,W,3).
        background: Clean background (H,W,3).
        alpha_mask: Float mask (H,W) in [0,1].
    Returns:
        blended: Output image (H,W,3).
    """
    # Ensure alpha_mask shape is (H,W,1)
    if len(alpha_mask.shape) == 2:
        alpha_mask = alpha_mask[..., None]
    # Broadcast alpha to 3 channels
    alpha_mask = np.repeat(alpha_mask, 3, axis=2)
    # Blend
    blended = alpha_mask * frame.astype(np.float32) + (1 - alpha_mask) * background.astype(np.float32)
    blended = np.clip(blended, 0, 255).astype(np.uint8)
    return blended

def gradual_fade_sequence(frame, background, foreground_mask, steps=10, blur_ksize=21):
    """
    Generate a sequence of frames fading the person away.
    Args:
        frame: Original frame (H,W,3).
        background: Clean background (H,W,3).
        foreground_mask: Binary mask (H,W), 0/255.
        steps: Number of fade steps.
        blur_ksize: Gaussian blur kernel size.
    Returns:
        frames: List of blended frames.
    """
    base_alpha = create_alpha_mask(foreground_mask, blur_ksize)
    frames = []
    for i in range(steps):
        # Linearly decrease alpha
        fade_alpha = base_alpha * (1 - i / (steps - 1))
        blended = alpha_blend(frame, background, fade_alpha)
        frames.append(blended)
    return frames


# Example usage:
# frame = imageio.imread('frame_with_person.jpg')
# background = imageio.imread('clean_background.jpg')
# foreground_mask = imageio.imread('person_mask.png')
# if foreground_mask.ndim == 3:
#     foreground_mask = foreground_mask[..., 0]  # Use first channel if mask is RGB
# fade_frames = gradual_fade_sequence(frame, background, foreground_mask, steps=10)
# for idx, img in enumerate(fade_frames):
#     imageio.imwrite(f'fade_{idx:02d}.png', img)