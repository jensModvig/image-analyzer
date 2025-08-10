# Image Analyzer

A modular Python image analysis application with visual representations and detailed metadata extraction.

## Features

- **Visual Representations**: Original image, golden ratio HSV mapping, per-channel heatmaps
- **Detailed Analysis**: Resolution, channel statistics, EXIF data, color analysis
- **Multi-format Support**: RGB, RGBA, Grayscale, and other formats
- **Point Cloud Support**: RGB and black point cloud visualization
- **Modular Architecture**: Easy to extend with new visualization and analysis modules

## Installation

```bash
conda env create -f environment.yml
conda activate image-analyzer
```

## Usage

```bash
python main.py [image_file]
```

## Update Environment

```bash
conda env update -f environment.yml --prune
```

## File Structure

```
image_analyzer/
├── main.py                 # Entry point
├── core/                   # Core application logic
├── visualization/          # Visual representation modules
├── analysis/              # Data analysis modules
├── gui/                   # GUI components (PyQt6)
├── data_containers/       # Data container classes
├── file_loaders/          # File loading modules
└── utils/                 # Utility functions
```

## Dependencies

- OpenCV - Image processing
- NumPy - Numerical operations
- Pillow - EXIF data extraction
- scikit-learn - Color clustering
- PyQt6 - GUI framework
- VTK/PyVista - 3D visualization
- Open3D - Point cloud processing