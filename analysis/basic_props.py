from analysis.base import AnalysisModule

class BasicPropertiesModule(AnalysisModule):
    def extract_properties(self):
        image = self.data_container.original
        
        properties = [
            ("Image Name", self.data_container.filepath.name, False),
            ("Full Path", self.data_container.filepath, False),
            ("Width", image.shape[1], False),
            ("Height", image.shape[0], False),
            ("Channels", self.data_container.channels, False),
            ("Data Type", str(image.dtype), False),
            ("File Size", f"{self.data_container.filepath.stat().st_size} bytes", False)
        ]
        
        return properties
    
    def get_module_name(self):
        return "Basic Properties"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]