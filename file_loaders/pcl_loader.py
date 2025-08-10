import open3d as o3d
from file_loaders.base import FileLoader

class PCLLoader(FileLoader):
    def load(self, filepath):
        pcd = o3d.io.read_point_cloud(str(filepath))
        if len(pcd.points) == 0:
            raise ValueError(f"Empty point cloud: {filepath}")
        return pcd, {}
    
    @property
    def extensions(self):
        return ['.pcd', '.ply']
    
    @property
    def container_type(self):
        from data_containers.pcl_container import PCLContainer
        return PCLContainer