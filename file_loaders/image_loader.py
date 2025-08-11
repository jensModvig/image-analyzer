import cv2
from file_loaders.base import FileLoader

class ImageLoader(FileLoader):
    def create_container(self, filepath):
        from data_containers.image_container import ImageContainer
        image = cv2.imread(str(filepath), cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"Could not load image: {filepath}")
        self.stored_params = {}
        return ImageContainer(filepath, image, {}, self)
    
    @property
    def extensions(self):
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']