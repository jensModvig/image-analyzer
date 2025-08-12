import os
import hashlib
import threading
from pathlib import Path
from core.ssh_manager import SSHConnectionPool

class RemoteFileMonitor:
    _monitors = {}
    _stored_connections = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_local_path(cls, remote_identifier, connection_info=None):
        if connection_info:
            cls._stored_connections[remote_identifier] = connection_info
        
        cache_dir = Path.home() / '.image-analyzer-cache'
        cache_dir.mkdir(exist_ok=True)
        
        if remote_identifier.startswith('ssh://'):
            remote_identifier = remote_identifier[6:]
        
        if ':' not in remote_identifier or '/' not in remote_identifier:
            raise ValueError(f"Invalid remote path format: {remote_identifier}")
        
        host_part, remote_path = remote_identifier.split(':', 1)
        original_ext = Path(remote_path).suffix
        path_hash = hashlib.md5(remote_identifier.encode()).hexdigest()
        local_path = cache_dir / f"{path_hash}{original_ext}"
        
        connection_info = cls._stored_connections.get(remote_identifier)
        if not connection_info:
            raise ValueError(f"No connection info for: {remote_identifier}")
        
        ssh_client = SSHConnectionPool.get_connection(connection_info)
        sftp = ssh_client.open_sftp()
        try:
            remote_stat = sftp.stat(remote_path)
            remote_mtime = remote_stat.st_mtime
            
            if not local_path.exists() or local_path.stat().st_mtime < remote_mtime:
                temp_path = local_path.with_name(f"{local_path.stem}_downloading{local_path.suffix}")
                sftp.get(remote_path, str(temp_path))
                temp_path.rename(local_path)
                os.utime(local_path, (remote_mtime, remote_mtime))
        finally:
            sftp.close()
        
        cls._start_monitor(remote_identifier, remote_path, local_path, connection_info)
        return str(local_path)
    
    @classmethod
    def _start_monitor(cls, remote_identifier, remote_path, local_path, connection_info):
        with cls._lock:
            if remote_identifier not in cls._monitors:
                monitor = MonitorThread(remote_identifier, remote_path, local_path, connection_info)
                monitor.daemon = True
                monitor.start()
                cls._monitors[remote_identifier] = monitor
    
    @classmethod
    def cleanup(cls):
        with cls._lock:
            for monitor in cls._monitors.values():
                monitor.stop()
            cls._monitors.clear()

class MonitorThread(threading.Thread):
    def __init__(self, remote_identifier, remote_path, local_path, connection_info):
        super().__init__()
        self.remote_identifier = remote_identifier
        self.remote_path = remote_path
        self.local_path = Path(local_path)
        self.connection_info = connection_info
        self.stop_event = threading.Event()
    
    def stop(self):
        self.stop_event.set()
    
    def run(self):
        while not self.stop_event.wait(2.0):
            try:
                ssh_client = SSHConnectionPool.get_connection(self.connection_info)
                sftp = ssh_client.open_sftp()
                
                try:
                    remote_stat = sftp.stat(self.remote_path)
                    remote_mtime = remote_stat.st_mtime
                    local_mtime = self.local_path.stat().st_mtime
                    
                    if remote_mtime > local_mtime:
                        temp_path = self.local_path.with_name(f"{self.local_path.stem}_downloading{self.local_path.suffix}")
                        sftp.get(self.remote_path, str(temp_path))
                        temp_path.rename(self.local_path)
                        os.utime(self.local_path, (remote_mtime, remote_mtime))
                finally:
                    sftp.close()
            except Exception:
                pass