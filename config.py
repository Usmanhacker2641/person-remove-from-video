"""
Configuration settings for the person removal system.
Modify these parameters to tune the detection and processing behavior.
"""

# Change Detection Parameters
MAHALANOBIS_THRESHOLD = 2.5  # Threshold for Mahalanobis distance (higher = less sensitive)
BACKGROUND_VARIANCE_OFFSET = 10.0  # Added to variance to avoid division by zero

# Morphological Operations
EROSION_KERNEL_SIZE = (3, 3)  # Kernel size for erosion (noise removal)
DILATION_KERNEL_SIZE = (5, 5)  # Kernel size for dilation (shape recovery)

# Connected Components Filtering
MIN_BLOB_SIZE = 100  # Minimum size for connected components (pixels)
CONNECTIVITY = 8  # Connectivity for component analysis (4 or 8)

# Alpha Blending
BLUR_KERNEL_SIZE = 15  # Gaussian blur kernel size for smooth edges
BLUR_SIGMA_RATIO = 6.0  # Ratio to convert kernel size to sigma (sigma = ksize/ratio)

# Video Output
DEFAULT_FPS = 30  # Frames per second for output videos
VIDEO_CODEC = 'libx264'  # Video codec for MP4 output

# Frame Processing
MAX_DISPLAY_FRAMES = 16  # Maximum frames to show in visualization grids
DISPLAY_GRID_ROWS = 4  # Rows in display grid
DISPLAY_GRID_COLS = 4  # Columns in display grid

# File Processing
SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

# Output File Names
ORIGINAL_VIDEO_NAME = "original_with_person.mp4"
PROCESSED_VIDEO_NAME = "processed_without_person.mp4"
COMPARISON_VIDEO_NAME = "comparison_combined.mp4"

# Color Conversion Weights (RGB to Grayscale)
RGB_TO_GRAY_WEIGHTS = [0.2989, 0.5870, 0.1140]  # Standard luminance weights

# Debug Settings
SAVE_DEBUG_IMAGES = False  # Set to True to save intermediate processing steps
DEBUG_OUTPUT_DIR = "debug_output"