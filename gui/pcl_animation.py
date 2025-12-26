from PyQt6.QtCore import QTimer
import numpy as np
import json

def _normalize(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

def _quaternion_from_vectors(forward, up):
    f = _normalize(forward)
    r = _normalize(np.cross(up, f))
    u = np.cross(f, r)
    m = np.array([[r[0], u[0], f[0]], [r[1], u[1], f[1]], [r[2], u[2], f[2]]])
    w = np.sqrt(1 + m[0,0] + m[1,1] + m[2,2]) / 2
    if w > 1e-6:
        w4 = 4 * w
        return np.array([w, (m[2,1] - m[1,2]) / w4, (m[0,2] - m[2,0]) / w4, (m[1,0] - m[0,1]) / w4])
    return np.array([1, 0, 0, 0])

def _quaternion_to_vectors(q, dist, focal):
    q = _normalize(q)
    w, x, y, z = q
    forward = np.array([2*(x*z + w*y), 2*(y*z - w*x), 1 - 2*(x*x + y*y)])
    up = np.array([2*(x*y - w*z), 1 - 2*(x*x + z*z), 2*(y*z + w*x)])
    pos = focal - _normalize(forward) * dist
    return pos, up

def _slerp(q1, q2, t):
    q1, q2 = _normalize(q1), _normalize(q2)
    dot = np.dot(q1, q2)
    if dot < 0:
        q2, dot = -q2, -dot
    if dot > 0.9995:
        return _normalize(q1 + t * (q2 - q1))
    theta = np.arccos(np.clip(dot, -1, 1))
    return (np.sin((1-t)*theta) * q1 + np.sin(t*theta) * q2) / np.sin(theta)

_shared_keyframes = []

class PCLAnimationController:
    def __init__(self, vtk_widget, container=None):
        self.vtk_widget = vtk_widget
        self.container = container
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.progress = 0.0
        self.playing = False
        self.speed = 0.02

    @property
    def keyframes(self):
        return _shared_keyframes

    def add_keyframe(self):
        state = {
            'position': np.array(self.vtk_widget.camera.position),
            'focal_point': np.array(self.vtk_widget.camera.focal_point),
            'up': np.array(self.vtk_widget.camera.up)
        }
        _shared_keyframes.append(state)
        print(f"Added keyframe {len(_shared_keyframes)}: pos={state['position']}")

    def clear(self):
        global _shared_keyframes
        self.pause()
        _shared_keyframes = []
        self.progress = 0.0

    def play(self):
        if len(self.keyframes) < 2:
            print(f"Cannot play: need at least 2 keyframes, have {len(self.keyframes)}")
            return
        self.playing = True
        self.timer.start(16)
        print(f"Playing animation with {len(self.keyframes)} keyframes")

    def pause(self):
        self.playing = False
        self.timer.stop()

    def toggle(self):
        if self.playing:
            self.pause()
        else:
            self.play()

    def _tick(self):
        try:
            if len(self.keyframes) < 2:
                return
            self.progress += self.speed
            if self.progress >= len(self.keyframes):
                self.progress -= len(self.keyframes)
            self._apply_interpolated()
        except Exception as e:
            print(f"Animation tick error: {e}")
            import traceback
            traceback.print_exc()
            self.pause()

    def _apply_interpolated(self):
        n = len(self.keyframes)
        idx = int(self.progress)
        t = self.progress - idx
        k1 = self.keyframes[idx % n]
        k2 = self.keyframes[(idx + 1) % n]

        f1 = k1['focal_point'] - k1['position']
        f2 = k2['focal_point'] - k2['position']
        d1, d2 = np.linalg.norm(f1), np.linalg.norm(f2)
        q1 = _quaternion_from_vectors(f1, k1['up'])
        q2 = _quaternion_from_vectors(f2, k2['up'])

        focal = k1['focal_point'] * (1-t) + k2['focal_point'] * t
        dist = d1 * (1-t) + d2 * t
        q = _slerp(q1, q2, t)
        pos, up = _quaternion_to_vectors(q, dist, focal)

        self.vtk_widget.camera.position = pos
        self.vtk_widget.camera.focal_point = focal
        self.vtk_widget.camera.up = up
        self.vtk_widget.render()

        if self.container:
            self.container.set_camera_state({'position': pos, 'focal_point': focal, 'up': up})

    def save(self, path):
        print(f"Saving {len(self.keyframes)} keyframes to {path}")
        data = {'keyframes': [{'position': k['position'].tolist(),
                               'focal_point': k['focal_point'].tolist(),
                               'up': k['up'].tolist()} for k in self.keyframes]}
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, path):
        global _shared_keyframes
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            _shared_keyframes = [{'position': np.array(k['position']),
                                  'focal_point': np.array(k['focal_point']),
                                  'up': np.array(k['up'])} for k in data['keyframes']]
            self.progress = 0.0
            print(f"Loaded {len(_shared_keyframes)} keyframes from {path}")
            self.play()
        except Exception as e:
            print(f"Failed to load animation: {e}")
            import traceback
            traceback.print_exc()
