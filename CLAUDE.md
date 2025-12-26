# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

```bash
# Create and activate conda environment
conda env create -f environment.yml
conda activate image-analyzer

# Update environment after changes
conda env update -f environment.yml --prune
```

## Running the Application

```bash
# Start GUI (from src/ directory)
python main.py

# Open specific file on startup
python main.py [image_file]
```

## Architecture Overview

This is a PyQt6-based modular image and point cloud analysis application with a plugin-style architecture.

### Core Flow

1. **Entry Point**: `main.py` creates `ImageAnalyzerApp` and loads optional file argument
2. **Main Application**: `core/app.py` orchestrates UI, file loading, and analysis
3. **File Loading**: Factory pattern in `file_loaders/factory.py` routes file extensions to appropriate loaders
4. **Data Containers**: Loaders create typed containers (`ImageContainer` or `PCLContainer`) that wrap data
5. **Module System**: `core/module_manager.py` dispatches containers to compatible visualization and analysis modules
6. **Display**: Results shown in `GridDisplay` (visualizations) and `AnalysisTable` (properties)

### Module System

The application uses a registration-based module system. Both visualization and analysis modules:
- Inherit from base classes (`VisualizationModule` or `AnalysisModule`)
- Declare supported container types via `get_supported_containers()` classmethod
- Are automatically registered in `core/module_manager.py`

**Adding New Modules**:
1. Create module class inheriting from appropriate base (`visualization/base.py` or `analysis/base.py`)
2. Implement required abstract methods
3. Register in `ModuleManager.__init__()` by adding to `visualization_modules` or `analysis_modules` list

### Data Container System

Two container types extend `BaseContainer`:
- **ImageContainer**: Wraps NumPy arrays with channel detection, stores loader metadata
- **PCLContainer**: Wraps Open3D point clouds, tracks camera state, handles color channels

Containers must implement `reload()` method for file watching functionality.

### File Loader System

Loaders extend `FileLoader` base class and:
- Declare supported extensions in `extensions` property
- Create appropriate containers via `create_container(filepath)`
- Support reload functionality via `reload_container(filepath)`
- Can store custom metadata in `loader_data` dict passed to containers

**Special Cases**:
- **NPZ files**: Interactive dialog for array selection (see `file_loaders/npz_loader.py`)
- **NPY files**: Column selection dialog for multi-channel data (see `file_loaders/npy_loader.py`)
- **Remote files**: SSH support via tuple format `(remote_identifier, connection_info)` handled by `FileAccessManager`

### Remote File Support

Remote images accessed via SSH are cached locally and monitored:
- `core/ssh_manager.py`: Connection pooling with paramiko
- `core/remote_monitor.py`: Background file monitoring and local caching
- `core/file_access.py`: Unified path resolution (local or remote)
- Format: `filepath` can be tuple `(remote_identifier, connection_info)`

### Keybind System

Custom keybinding system in `core/keybind_manager.py`:
- Platform-specific defaults in `keybinds_default.json`
- User overrides in `~/.config/image-analyzer/keybinds.json`
- Actions created with `create_action(action_id, label, callback)`

## Development Guidelines

### Adding Visualization Module

```python
from visualization.base import VisualizationModule
from data_containers.image_container import ImageContainer

class NewVisualizationModule(VisualizationModule):
    @classmethod
    def get_supported_containers(cls):
        return [ImageContainer]  # or PCLContainer

    def get_module_name(self):
        return "Module Name"

    def generate_visualizations(self):
        # Return list of (widget, title) tuples
        return [(widget, "Display Title")]
```

Then register in `core/module_manager.py`.

### Adding Analysis Module

```python
from analysis.base import AnalysisModule
from data_containers.image_container import ImageContainer

class NewAnalysisModule(AnalysisModule):
    @classmethod
    def get_supported_containers(cls):
        return [ImageContainer]

    def get_module_name(self):
        return "Module Name"

    def extract_properties(self):
        # Return list of (property_name, value) tuples
        return [("Property", "Value")]
```

Then register in `core/module_manager.py`.

### Adding File Loader

```python
from file_loaders.base import FileLoader
from data_containers.image_container import ImageContainer

class NewFileLoader(FileLoader):
    def __init__(self):
        self.extensions = ['.ext']

    def create_container(self, filepath):
        data = self._load_file(filepath)
        loader_data = {}  # Custom metadata
        return ImageContainer(filepath, data, loader_data, self)

    def reload_container(self, filepath):
        return self.create_container(filepath)
```

No registration needed - loaders are auto-discovered via `FileLoader.__subclasses__()`.

## Key Dependencies

- **OpenCV**: Image I/O and processing (accessed as `cv2`)
- **NumPy**: Numerical operations on image arrays
- **Pillow**: EXIF data extraction
- **PyQt6**: GUI framework
- **Open3D**: Point cloud I/O and processing
- **PyVista/PyVistaQt**: 3D visualization in Qt
- **scikit-learn**: Color clustering analysis
- **watchdog**: File change monitoring
- **paramiko**: SSH connections for remote files
