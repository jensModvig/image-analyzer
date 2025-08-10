from analysis.base import AnalysisModule

class PCLBasicPropertiesModule(AnalysisModule):
    def extract_properties(self):
        return self.image_container.get_basic_properties()
    
    def get_module_name(self):
        return "PCL Properties"
    
    @classmethod
    def get_supported_containers(cls):
        from data_containers.pcl_container import PCLContainer
        return [PCLContainer]