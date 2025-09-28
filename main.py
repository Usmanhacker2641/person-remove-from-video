import os
import sys
import shutil
import imageio.v2 as imageio  # Use v2 to avoid deprecation warnings
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from scipy import ndimage
from Alpha_blending import alpha_blend, create_alpha_mask

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <folder_path>")
        print("Example: python main.py /path/to/video/frames/")
        sys.exit(1)

    # Original folder with frames
    folder_path = sys.argv[1]
    
    # Validate input folder
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a directory")
        sys.exit(1)
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    try:
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
    except PermissionError:
        print(f"Error: Permission denied accessing folder '{folder_path}'")
        sys.exit(1)
    
    image_files.sort()  # Sort for consistent order
    num_frames = len(image_files)
    if num_frames == 0:
        print(f"No image frames found in: {folder_path}")
        print(f"Supported formats: {', '.join(image_extensions)}")
        sys.exit(1)
    
    print(f"Found {num_frames} frames to process")

    # Load all frames and convert to grayscale
    print("Step 1: Reading frames and converting to grayscale...")
    frames = []
    gray_frames = []
    
    for i, filename in enumerate(image_files):
        img_path = os.path.join(folder_path, filename)
        try:
            img = imageio.imread(img_path)
            frames.append(img)
            # Convert to grayscale
            if len(img.shape) == 3:  # RGB image
                gray = np.dot(img[...,:3], [0.2989, 0.5870, 0.1140])
                gray_frames.append(gray.astype(np.uint8))
            else:  # Already grayscale
                gray_frames.append(img)
        except Exception as e:
            print(f"Warning: Could not read frame {filename}: {e}")
            continue
    
    if len(frames) == 0:
        print("Error: No valid frames could be loaded")
        sys.exit(1)
    
    print(f"Successfully loaded {len(frames)} frames")
    
    # Select a subset for display
    sample_size = min(16, num_frames)
    step = num_frames // sample_size if num_frames > sample_size else 1
    selected_indices = list(range(0, num_frames, step))[:sample_size]
    
    # Ensure all frames have the same dimensions
    heights = [frame.shape[0] for frame in frames]
    widths = [frame.shape[1] for frame in frames]
    median_height = int(np.median(heights))
    median_width = int(np.median(widths))
    
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
    
    # Step 7: Alpha blending to remove person
    print("Step 7: Alpha blending to remove person...")
    processed_frames = []
    
    for i, (frame, mask) in enumerate(zip(uniform_frames, filtered_masks)):
        # Create smooth alpha mask from binary mask
        alpha = create_alpha_mask(mask, blur_ksize=15)
        
        # Blend background with original frame
        processed = alpha_blend(bg_rgb, frame, 1.0 - alpha)  # 1.0 - alpha to invert (remove person)
        processed_frames.append(processed)
    
    # Display frames in two figures side by side
    rows = 4
    cols = 4
    fig_size = (cols*2, rows*2)
    
    # Display intermediate results for the first selected frame for debugging
    plt.figure(figsize=(12, 10))
    plt.suptitle("Change Detection Pipeline (First Frame)", fontsize=16)
    
    # Get the first frame for visualization
    idx = selected_indices[0]
    plt.subplot(2, 3, 1)
    plt.imshow(uniform_frames[idx])
    plt.title("Original Frame")
    plt.axis('off')
    
    plt.subplot(2, 3, 2)
    plt.imshow(uniform_grays[idx], cmap='gray')
    plt.title("Grayscale")
    plt.axis('off')
    
    plt.subplot(2, 3, 3)
    plt.imshow(foreground_masks[idx], cmap='gray')
    plt.title("Change Detection")
    plt.axis('off')
    
    plt.subplot(2, 3, 4)
    plt.imshow(cleaned_masks[idx], cmap='gray')
    plt.title("After Morphology")
    plt.axis('off')
    
    plt.subplot(2, 3, 5)
    plt.imshow(filtered_masks[idx], cmap='gray')
    plt.title("After Blob Filtering")
    plt.axis('off')
    
    plt.subplot(2, 3, 6)
    plt.imshow(processed_frames[idx])
    plt.title("Final Result")
    plt.axis('off')
    
    # Figure 1: Original frames
    plt.figure(figsize=fig_size)
    plt.suptitle("Figure 1: Original Frames with Person", fontsize=16)
    for i, idx in enumerate(selected_indices):
        if i >= rows * cols:
            break
        plt.subplot(rows, cols, i+1)
        plt.imshow(uniform_frames[idx])
        plt.title(f"Frame {idx+1}")
        plt.axis('off')
    
    # Figure 2: Processed frames (person removed)
    plt.figure(figsize=fig_size)
    plt.suptitle("Figure 2: Frames with Person Removed", fontsize=16)
    for i, idx in enumerate(selected_indices):
        if i >= rows * cols:
            break
        plt.subplot(rows, cols, i+1)
        plt.imshow(processed_frames[idx])
        plt.title(f"Frame {idx+1}")
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # Create MP4 video files from frames
    print("Creating MP4 video files...")
    
    # Ensure output directory exists and is writable
    output_dir = os.path.dirname(folder_path) if os.path.dirname(folder_path) else "."
    try:
        if not os.access(output_dir, os.W_OK):
            print(f"Warning: Output directory '{output_dir}' is not writable, using current directory")
            output_dir = "."
    except:
        output_dir = "."
    
    # Original video with person
    original_video_path = os.path.join(output_dir, "original_with_person.mp4")
    print(f"Saving original video to: {original_video_path}")
    
    try:
        with imageio.get_writer(original_video_path, fps=30, format='mp4', codec='libx264') as writer:
            for frame in uniform_frames:
                writer.append_data(frame)
        print(f"✓ Original video saved successfully")
    except Exception as e:
        print(f"Error saving original video: {e}")
    
    # Processed video without person
    processed_video_path = os.path.join(output_dir, "processed_without_person.mp4")
    print(f"Saving processed video to: {processed_video_path}")
    
    try:
        with imageio.get_writer(processed_video_path, fps=30, format='mp4', codec='libx264') as writer:
            for frame in processed_frames:
                writer.append_data(frame)
        print(f"✓ Processed video saved successfully")
    except Exception as e:
        print(f"Error saving processed video: {e}")
    
    print(f"Video creation complete!")
    if os.path.exists(original_video_path):
        print(f"Original video: {original_video_path}")
    if os.path.exists(processed_video_path):
        print(f"Processed video: {processed_video_path}")
    
    # Display videos on screen using matplotlib animation
    print("Displaying videos on screen...")
    
    def animate_original(frame_num):
        """Animation function for original video"""
        ax1.clear()
        ax1.imshow(uniform_frames[frame_num % len(uniform_frames)])
        ax1.set_title(f'Original Video - Frame {frame_num + 1}')
        ax1.axis('off')
    
    def animate_processed(frame_num):
        """Animation function for processed video"""
        ax2.clear()
        ax2.imshow(processed_frames[frame_num % len(processed_frames)])
        ax2.set_title(f'Processed Video - Frame {frame_num + 1}')
        ax2.axis('off')
    
    # Create side-by-side video display
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle('Video Playback: Original vs Processed', fontsize=16)
    
    # Create animations
    anim1 = animation.FuncAnimation(fig, animate_original, frames=len(uniform_frames), 
                                   interval=100, repeat=True, blit=False)
    anim2 = animation.FuncAnimation(fig, animate_processed, frames=len(processed_frames), 
                                   interval=100, repeat=True, blit=False)
    
    plt.tight_layout()
    plt.show()
    
    # Also create a combined comparison video
    combined_video_path = os.path.join(output_dir, "comparison_combined.mp4")
    print(f"Creating combined comparison video: {combined_video_path}")
    
    try:
        with imageio.get_writer(combined_video_path, fps=30, format='mp4', codec='libx264') as writer:
            for original, processed in zip(uniform_frames, processed_frames):
                # Create side-by-side comparison frame
                combined_frame = np.hstack((original, processed))
                writer.append_data(combined_frame)
        print(f"✓ Combined comparison video saved: {combined_video_path}")
    except Exception as e:
        print(f"Error saving combined video: {e}")

if __name__ == "__main__":
    main()