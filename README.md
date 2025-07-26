# Image Analyzer

A modular Python image analysis application with visual representations and detailed metadata extraction.

## Features

- **Visual Representations**: Original image, golden ratio HSV mapping, per-channel heatmaps
- **Detailed Analysis**: Resolution, channel statistics, EXIF data, color analysis
- **Multi-format Support**: RGB, RGBA, Grayscale, and other formats
- **Modular Architecture**: Easy to extend with new visualization and analysis modules

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py [image_file]
```

Or run without arguments to open a file dialog.

## File Structure

```
image_analyzer/
├── main.py                 # Entry point
├── core/                   # Core application logic
├── visualization/          # Visual representation modules
├── analysis/              # Data analysis modules
├── gui/                   # GUI components
└── utils/                 # Utility functions
```

## Dependencies

- OpenCV (cv2) - Primary image processing
- NumPy - Numerical operations
- Pillow (PIL) - EXIF data extraction
- scikit-learn - Color clustering (optional)
- tkinter - GUI (built-in with Python)