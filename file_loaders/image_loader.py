import cv2
from file_loaders.base import FileLoader

class ImageLoader(FileLoader):
    def load(self, filepath):
        image = cv2.imread(str(filepath), cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"Could not load image: {filepath}")
        return image, {}
    
    @property
    def extensions(self):
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    @property
    def container_type(self):
        from data_containers.image_container import ImageContainer
        return ImageContainer