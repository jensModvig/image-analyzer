from core.remote_monitor import RemoteFileMonitor

class FileAccessManager:
    @staticmethod
    def resolve_path(filepath):
        if isinstance(filepath, tuple) and len(filepath) == 2:
            remote_identifier, connection_info = filepath
            return RemoteFileMonitor.get_local_path(remote_identifier, connection_info)
        return filepath