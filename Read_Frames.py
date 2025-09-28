import os
import numpy as np
from PIL import Image

def read_grayscale_frames(input_folder, extension='.png'):
    # Step 1: Get sorted list of image files with the given extension
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(extension)]
    files.sort()
    
    grayscale_frames = []
    
    for filename in files:
        filepath = os.path.join(input_folder, filename)
        # Step 2: Read image
        img = Image.open(filepath).convert('RGB')
        img_np = np.array(img, dtype=np.float32)
        
        # Step 3: Convert to grayscale using luminance formula
        gray = 0.299 * img_np[..., 0] + 0.587 * img_np[..., 1] + 0.114 * img_np[..., 2]
        # Step 4: Store grayscale frame
        grayscale_frames.append(gray.astype(np.float32))
    
    # Convert list to NumPy array: shape (N, H, W)
    frames_array = np.stack(grayscale_frames, axis=0)
    return frames_array

# Example usage:
# input_folder = 'person1'
# frames = read_grayscale_frames(input_folder)
# print(frames.shape)  # (N, H, W)