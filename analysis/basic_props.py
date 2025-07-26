import os
from analysis.base import AnalysisModule

class BasicPropertiesModule(AnalysisModule):
    def extract_properties(self):
        image = self.image_container.original
        
        properties = [
            ("Width", image.shape[1], False),
            ("Height", image.shape[0], False),
            ("Channels", self.image_container.channels, False),
            ("Data Type", str(image.dtype), False),
            ("File Size", f"{os.path.getsize(self.image_container.filepath)} bytes", False)
        ]
        
        return properties
    
    def get_module_name(self):
        return "Basic Properties"