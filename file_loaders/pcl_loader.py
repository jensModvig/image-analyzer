import open3d as o3d
from file_loaders.base import FileLoader

class PCLLoader(FileLoader):
    def create_container(self, filepath):
        from data_containers.pcl_container import PCLContainer
        pcd = o3d.io.read_point_cloud(str(filepath))
        if len(pcd.points) == 0:
            raise ValueError(f"Empty point cloud: {filepath}")
        self.stored_params = {}
        return PCLContainer(filepath, pcd, {}, self)
    
    @property
    def extensions(self):
        return ['.pcd', '.ply']