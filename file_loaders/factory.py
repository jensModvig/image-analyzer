from pathlib import Path
from file_loaders.base import FileLoader
from file_loaders.image_loader import ImageLoader
from file_loaders.npz_loader import NPZLoader

def get_loader(filepath):
    ext = Path(filepath).suffix.lower()
    
    for loader_class in FileLoader.__subclasses__():
        if ext in loader_class().extensions:
            return loader_class()
    
    raise ValueError(f"Unsupported file type: {ext}")

def get_all_extensions():
    extensions = []
    for loader_class in FileLoader.__subclasses__():
        extensions.extend(loader_class().extensions)
    return extensions