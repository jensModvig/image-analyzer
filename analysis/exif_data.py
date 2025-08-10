from analysis.base import AnalysisModule

class EXIFDataModule(AnalysisModule):
    def extract_properties(self):
        properties = []
        
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            with Image.open(self.data_container.filepath) as img:
                exif_data = img.getexif()
                
                if exif_data:
                    exif_dict = {}
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = value
                    
                    focal_length = exif_dict.get('FocalLength', 'N/A')
                    camera_make = exif_dict.get('Make', 'N/A')
                    camera_model = exif_dict.get('Model', 'N/A')
                    
                    properties.extend([
                        ("Camera Make", str(camera_make), False),
                        ("Camera Model", str(camera_model), False),
                        ("Focal Length", str(focal_length), False),
                        ("All EXIF Data", exif_dict, True)
                    ])
                else:
                    properties.append(("EXIF Data", "No EXIF data found", False))
                    
        except ImportError:
            properties.append(("EXIF Data", "PIL not available for EXIF extraction", False))
        except Exception as e:
            properties.append(("EXIF Data", f"Error reading EXIF: {str(e)}", False))
        
        return properties
    
    def get_module_name(self):
        return "EXIF Data"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.image_container import ImageContainer
        return [ImageContainer]