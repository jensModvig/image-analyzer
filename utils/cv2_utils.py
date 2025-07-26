import cv2
import numpy as np

def safe_normalize(image, dtype=cv2.CV_8U):
    return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=dtype)

def safe_resize(image, max_size):
    height, width = image.shape[:2]
    if width > max_size or height > max_size:
        scale = min(max_size / width, max_size / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(image, (new_width, new_height))
    return image

def convert_for_display(image):
    if len(image.shape) == 3:
        if image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
    return image