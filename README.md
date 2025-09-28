# Person Removal from Video

This Python project removes persons from video by processing individual frames using computer vision techniques. The system uses background modeling, change detection, and alpha blending to seamlessly remove detected persons from video footage.

## Features

- **Automated person detection** using Mahalanobis distance-based change detection
- **Background modeling** with mean and variance computation
- **Noise removal** using morphological operations
- **Connected component analysis** for blob filtering
- **Smooth person removal** using alpha blending with Gaussian blur
- **Multiple output formats**: individual processed frames, MP4 videos, and comparison videos
- **Interactive visualization** of the processing pipeline

## Requirements

- Python 3.8 or later
- Required packages (install with `pip install -r requirements.txt`):
  - numpy >= 1.21.0
  - scipy >= 1.7.0
  - matplotlib >= 3.5.0
  - imageio >= 2.19.0
  - imageio-ffmpeg >= 0.4.7
  - Pillow >= 8.3.0

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Usmanhacker2641/person-remove-from-video.git
cd person-remove-from-video
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Extract frames from your video and place them in a folder, then run:

```bash
python main.py /path/to/video/frames/
```

### Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)

### Example

```bash
# Extract frames from video (using ffmpeg)
ffmpeg -i input_video.mp4 frames/frame_%04d.png

# Process frames to remove persons
python main.py frames/

# Output files will be saved in the same directory as the frames folder
```

## Output Files

The system generates several output files:

1. **`original_with_person.mp4`** - Original video reconstruction
2. **`processed_without_person.mp4`** - Video with persons removed
3. **`comparison_combined.mp4`** - Side-by-side comparison video
4. **Interactive visualizations** - Processing pipeline steps and results

## How It Works

The person removal system follows these steps:

1. **Frame Loading**: Load and normalize all input frames
2. **Background Modeling**: Compute statistical background model (mean/variance)
3. **Change Detection**: Use Mahalanobis distance to detect foreground objects
4. **Noise Removal**: Apply morphological operations (erosion/dilation)
5. **Component Analysis**: Filter connected components by size
6. **Alpha Blending**: Smoothly blend background with original frames

## Project Structure

```
person-remove-from-video/
├── main.py                 # Main processing script
├── Alpha_blending.py       # Alpha blending and mask creation functions
├── change_detection.py     # Mahalanobis distance-based change detection
├── connected_component.py  # Connected component analysis
├── Noise_removal.py        # Morphological noise removal operations
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .gitignore            # Git ignore patterns
```

## Configuration

You can modify processing parameters in `main.py`:

- `threshold = 2.5` - Mahalanobis distance threshold for change detection
- `min_size = 100` - Minimum blob size for person detection
- `blur_ksize = 15` - Gaussian blur kernel size for smooth blending

## Examples and Testing

For testing, you can create synthetic test frames:

```python
# Create simple test data
import numpy as np
import imageio

# Create frames with moving objects for testing
# (see main_test.py for a complete example)
```

## Performance Notes

- Processing time depends on frame count, resolution, and hardware
- Large videos should be processed in chunks
- GPU acceleration is not currently implemented
- Typical processing: ~1-2 seconds per frame for 720p resolution

## Limitations

- Works best with relatively static backgrounds
- May struggle with complex scenes or multiple moving objects
- Requires sufficient frames to build accurate background model
- Currently optimized for person removal (humanoid shapes)

## Troubleshooting

**No frames found**: Ensure your folder contains supported image formats and check file permissions.

**Memory errors**: Reduce frame resolution or process in smaller batches.

**Poor detection**: Try adjusting the `threshold` parameter in the change detection step.

**Installation issues**: Ensure you have Python 3.8+ and all dependencies installed.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the system.

## License

This project is open source. Please check the repository for license details.
