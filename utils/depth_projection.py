import numpy as np

def project_depth_to_pointcloud(depth_array, focal_length=None, intrinsic_matrix=None):
    h, w = depth_array.shape
    
    if np.issubdtype(depth_array.dtype, np.integer):
        if np.any(depth_array < 0):
            raise ValueError("Negative depth values found in integer depth array")
        depth_shift = 1000.0
    else:
        depth_shift = 1.0
    
    if focal_length is None:
        focal_length = 50.0
    
    f_px = focal_length * np.sqrt(w**2 + h**2) / np.sqrt(36**2 + 24**2)
    
    if intrinsic_matrix is None:
        intrinsic = np.array([
            [f_px, 0, w/2, 0],
            [0, f_px, h/2, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    else:
        if intrinsic_matrix.shape == (3, 3):
            intrinsic = np.eye(4)
            intrinsic[:3, :3] = intrinsic_matrix
        elif intrinsic_matrix.shape == (3, 4):
            intrinsic = np.eye(4)
            intrinsic[:3, :] = intrinsic_matrix
        else:
            intrinsic = intrinsic_matrix
    
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    mask = depth_array != 0
    
    uv_depth = np.stack([x, y, depth_array / depth_shift], axis=-1)
    uv_depth = uv_depth[mask]
    
    fx, fy = intrinsic[0, 0], intrinsic[1, 1]
    cx, cy = intrinsic[0, 2], intrinsic[1, 2]
    bx, by = intrinsic[0, 3], intrinsic[1, 3]
    
    X = (uv_depth[:, 0] - cx) * uv_depth[:, 2] / fx + bx
    Y = (uv_depth[:, 1] - cy) * uv_depth[:, 2] / fy + by
    points = np.column_stack([X, Y, uv_depth[:, 2]])
    
    return points, mask