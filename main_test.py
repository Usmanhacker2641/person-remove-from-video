#!/usr/bin/env python3
"""
Test version of main.py that runs in headless mode without displaying plots.
This version focuses on the core processing pipeline and saves intermediate results.
"""
import os
import sys
import shutil
import imageio
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from scipy import ndimage
from Alpha_blending import alpha_blend, create_alpha_mask

def main():
    if len(sys.argv) < 2:
        print("Usage: python main_test.py <folder_path>")
        sys.exit(1)

    # Original folder with frames
    folder_path = sys.argv[1]
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
    image_files.sort()  # Sort for consistent order
    num_frames = len(image_files)
    if num_frames == 0:
        print(f"No image frames found in: {folder_path}")
        sys.exit(1)
    
    print(f"Found {num_frames} frames to process")

    # Load all frames and convert to grayscale
    print("Step 1: Reading frames and converting to grayscale...")
    frames = []
    gray_frames = []
    
    for filename in image_files:
        img_path = os.path.join(folder_path, filename)
        img = imageio.imread(img_path)
        frames.append(img)
        # Convert to grayscale
        if len(img.shape) == 3:  # RGB image
            gray = np.dot(img[...,:3], [0.2989, 0.5870, 0.1140])
            gray_frames.append(gray.astype(np.uint8))
        else:  # Already grayscale
            gray_frames.append(img)
    
    # Select a subset for display
    sample_size = min(16, num_frames)
    step = num_frames // sample_size if num_frames > sample_size else 1
    selected_indices = list(range(0, num_frames, step))[:sample_size]
    
    # Ensure all frames have the same dimensions
    heights = [frame.shape[0] for frame in frames]
    widths = [frame.shape[1] for frame in frames]
    median_height = int(np.median(heights))
    median_width = int(np.median(widths))
    
    print(f"Frame dimensions: {median_height}x{median_width}")
    
    # Resize frames to median size if needed
    uniform_frames = []
    uniform_grays = []
    
    for i, (frame, gray) in enumerate(zip(frames, gray_frames)):
        if frame.shape[0] != median_height or frame.shape[1] != median_width:
            # Simple resize by cropping/padding for color frames
            new_frame = np.zeros((median_height, median_width, 3), dtype=np.uint8)
            h = min(frame.shape[0], median_height)
            w = min(frame.shape[1], median_width)
            new_frame[:h, :w] = frame[:h, :w]
            uniform_frames.append(new_frame)
            
            # Resize grayscale frames
            new_gray = np.zeros((median_height, median_width), dtype=np.uint8)
            new_gray[:h, :w] = gray[:h, :w]
            uniform_grays.append(new_gray)
        else:
            uniform_frames.append(frame)
            uniform_grays.append(gray)
    
    # Step 2: Visualize montage of original frames
    print("Step 2: Creating visualization montage...")
    
    # Step 3: Build background model (mean, variance)
    print("Step 3: Building background model (mean and variance)...")
    # Stack grayscale frames and compute mean and variance
    gray_stack = np.stack(uniform_grays)
    bg_mean = np.mean(gray_stack, axis=0).astype(np.float32)
    bg_var = np.var(gray_stack, axis=0).astype(np.float32) + 10.0  # Add small constant to avoid division by zero
    
    # Also compute RGB background for visualization
    rgb_stack = np.stack(uniform_frames)
    bg_rgb = np.median(rgb_stack, axis=0).astype(np.uint8)
    
    print(f"Background model computed. Mean range: [{bg_mean.min():.1f}, {bg_mean.max():.1f}]")
    
    # Step 4: Change detection using Mahalanobis distance
    print("Step 4: Performing change detection...")
    foreground_masks = []
    
    for gray in uniform_grays:
        # Calculate Mahalanobis distance
        diff = np.abs(gray.astype(np.float32) - bg_mean)
        mahalanobis_dist = diff / np.sqrt(bg_var)
        
        # Apply threshold to get binary mask
        threshold = 2.5  # Threshold for Mahalanobis distance
        mask = (mahalanobis_dist > threshold).astype(np.uint8) * 255
        foreground_masks.append(mask)
    
    print(f"Change detection complete. Average foreground pixels per frame: {np.mean([np.sum(mask > 0) for mask in foreground_masks]):.1f}")
    
    # Step 5: Morphological noise removal
    print("Step 5: Applying morphological operations to remove noise...")
    cleaned_masks = []
    
    for mask in foreground_masks:
        # Apply erosion to remove small noise
        eroded = ndimage.binary_erosion(mask, structure=np.ones((3,3))).astype(np.uint8) * 255
        # Apply dilation to fill holes and recover shape
        dilated = ndimage.binary_dilation(eroded, structure=np.ones((5,5))).astype(np.uint8) * 255
        cleaned_masks.append(dilated)
    
    # Step 6: Connected components analysis and blob filtering
    print("Step 6: Analyzing connected components and filtering blobs...")
    filtered_masks = []
    
    for mask in cleaned_masks:
        # Find connected components
        labeled, num_features = ndimage.label(mask)
        component_sizes = ndimage.sum(mask, labeled, range(1, num_features + 1))
        
        # Filter small components
        min_size = 100  # Minimum blob size
        filtered = np.zeros_like(mask)
        
        # Keep only large components (likely to be people)
        for i, size in enumerate(component_sizes):
            if size >= min_size:
                filtered[labeled == i + 1] = 255
                
        filtered_masks.append(filtered)
    
    print(f"Component filtering complete. Average components per frame: {np.mean([len(component_sizes) for mask in cleaned_masks for labeled, num_features in [ndimage.label(mask)] for component_sizes in [ndimage.sum(mask, labeled, range(1, num_features + 1))]]):.1f}")
    
    # Step 7: Alpha blending to remove person
    print("Step 7: Alpha blending to remove person...")
    processed_frames = []
    
    for i, (frame, mask) in enumerate(zip(uniform_frames, filtered_masks)):
        # Create smooth alpha mask from binary mask
        alpha = create_alpha_mask(mask, blur_ksize=15)
        
        # Blend background with original frame
        processed = alpha_blend(bg_rgb, frame, 1.0 - alpha)  # 1.0 - alpha to invert (remove person)
        processed_frames.append(processed)
    
    # Save intermediate results for debugging
    debug_dir = "/tmp/debug_output"
    os.makedirs(debug_dir, exist_ok=True)
    
    # Save first frame results
    idx = 0
    imageio.imwrite(f"{debug_dir}/01_original.png", uniform_frames[idx])
    imageio.imwrite(f"{debug_dir}/02_grayscale.png", uniform_grays[idx])
    imageio.imwrite(f"{debug_dir}/03_background.png", bg_rgb)
    imageio.imwrite(f"{debug_dir}/04_foreground_mask.png", foreground_masks[idx])
    imageio.imwrite(f"{debug_dir}/05_cleaned_mask.png", cleaned_masks[idx])
    imageio.imwrite(f"{debug_dir}/06_filtered_mask.png", filtered_masks[idx])
    imageio.imwrite(f"{debug_dir}/07_processed.png", processed_frames[idx])
    
    print(f"Debug images saved to: {debug_dir}")
    
    # Create MP4 video files from frames
    print("Creating MP4 video files...")
    
    # Original video with person
    original_video_path = os.path.join(os.path.dirname(folder_path), "original_with_person.mp4")
    print(f"Saving original video to: {original_video_path}")
    
    with imageio.get_writer(original_video_path, fps=5, format='mp4', codec='libx264') as writer:
        for frame in uniform_frames:
            writer.append_data(frame)
    
    # Processed video without person
    processed_video_path = os.path.join(os.path.dirname(folder_path), "processed_without_person.mp4")
    print(f"Saving processed video to: {processed_video_path}")
    
    with imageio.get_writer(processed_video_path, fps=5, format='mp4', codec='libx264') as writer:
        for frame in processed_frames:
            writer.append_data(frame)
    
    # Also create a combined comparison video
    combined_video_path = os.path.join(os.path.dirname(folder_path), "comparison_combined.mp4")
    print(f"Creating combined comparison video: {combined_video_path}")
    
    with imageio.get_writer(combined_video_path, fps=5, format='mp4', codec='libx264') as writer:
        for original, processed in zip(uniform_frames, processed_frames):
            # Create side-by-side comparison frame
            combined_frame = np.hstack((original, processed))
            writer.append_data(combined_frame)
    
    print(f"\nProcessing complete!")
    print(f"Original video: {original_video_path}")
    print(f"Processed video: {processed_video_path}")
    print(f"Combined comparison video: {combined_video_path}")

if __name__ == "__main__":
    main()