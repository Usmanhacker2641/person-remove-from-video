#!/usr/bin/env python3
"""
Example usage script for the person removal system.
This demonstrates how to use the system with synthetic test data.
"""

import os
import numpy as np
import imageio.v2 as imageio
import subprocess
import sys

def create_sample_frames(output_dir="sample_frames", num_frames=20):
    """
    Create sample video frames with a moving person for demonstration.
    
    Args:
        output_dir (str): Directory to save frames
        num_frames (int): Number of frames to generate
    """
    print(f"Creating {num_frames} sample frames in '{output_dir}'...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Frame parameters
    height, width = 480, 640
    
    # Create static background (simple gradient pattern)
    background = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            background[y, x] = [
                min(255, (x // 4) % 256),  # Red gradient
                min(255, (y // 4) % 256),  # Green gradient  
                min(255, ((x + y) // 6) % 256)  # Blue gradient
            ]
    
    # Add some "scenery" rectangles
    background[100:150, 200:300] = [150, 100, 50]  # Brown rectangle
    background[300:400, 450:550] = [100, 150, 100]  # Green rectangle
    
    # Generate frames with moving person
    for frame_num in range(num_frames):
        frame = background.copy()
        
        # Person parameters (simple rectangle representing a person)
        person_width, person_height = 60, 120
        
        # Move person from left to right across the scene
        person_x = 50 + int((frame_num / (num_frames - 1)) * (width - person_width - 100))
        person_y = height // 2 - person_height // 2
        
        # Draw person as colored rectangle
        person_color = [200, 80, 80]  # Reddish color
        frame[person_y:person_y + person_height, 
              person_x:person_x + person_width] = person_color
        
        # Add some variation (head)
        head_size = 20
        head_y = person_y - head_size
        head_x = person_x + (person_width - head_size) // 2
        if head_y >= 0:
            frame[head_y:head_y + head_size, 
                  head_x:head_x + head_size] = [220, 100, 100]
        
        # Save frame
        frame_path = os.path.join(output_dir, f"frame_{frame_num:04d}.png")
        imageio.imwrite(frame_path, frame)
    
    print(f"✓ Sample frames created in '{output_dir}'")
    return output_dir

def run_person_removal(frames_dir):
    """
    Run the person removal system on the given frames directory.
    
    Args:
        frames_dir (str): Directory containing input frames
    """
    print(f"Running person removal on frames in '{frames_dir}'...")
    
    try:
        # Run the main processing script
        result = subprocess.run([
            sys.executable, "main.py", frames_dir
        ], capture_output=True, text=True, check=True)
        
        print("✓ Person removal completed successfully!")
        print("Output:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running person removal: {e}")
        print("Error output:")
        print(e.stderr)
        return False
    
    return True

def main():
    """Main example function"""
    print("Person Removal System - Example Usage")
    print("=" * 50)
    
    # Step 1: Create sample frames
    frames_dir = create_sample_frames()
    
    # Step 2: Run person removal
    success = run_person_removal(frames_dir)
    
    if success:
        print("\n" + "=" * 50)
        print("Example completed successfully!")
        print(f"Check the output videos in the current directory:")
        print("- original_with_person.mp4")  
        print("- processed_without_person.mp4")
        print("- comparison_combined.mp4")
        print(f"\nInput frames are in: {frames_dir}/")
    else:
        print("\n" + "=" * 50)
        print("Example failed. Please check the error messages above.")

if __name__ == "__main__":
    main()