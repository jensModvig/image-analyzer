import os
import time
import threading
import paramiko
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout

class UserPasswordDialog(QDialog):
    def __init__(self, username, hostname):
        super().__init__()
        self.setWindowTitle("User Password")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Enter password for {username}@{hostname}:"))
        
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.returnPressed.connect(self.accept)
        layout.addWidget(self.password_field)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_password(self):
        return self.password_field.text()

class KeyPasswordDialog(QDialog):
    def __init__(self, key_path):
        super().__init__()
        self.setWindowTitle("Private Key Password")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Enter password for private key:\n{key_path}"))
        
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.returnPressed.connect(self.accept)
        layout.addWidget(self.password_field)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_password(self):
        return self.password_field.text()

class SSHConnectionPool:
    _connections = {}
    _key_passwords = {}
    _user_passwords = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_connection(cls, connection_info):
        key = f"{connection_info['username']}@{connection_info['hostname']}"
        
        with cls._lock:
            if key in cls._connections:
                client, _ = cls._connections[key]
                if client.get_transport() and client.get_transport().is_active():
                    cls._connections[key] = (client, time.time())
                    return client
                else:
                    del cls._connections[key]
            
            client = cls._create_connection(connection_info)
            cls._connections[key] = (client, time.time())
            return client
    
    @classmethod
    def _create_connection(cls, connection_info):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        hostname = connection_info['hostname']
        username = connection_info['username']
        identity_file = connection_info.get('identity_file')
        user_password = connection_info.get('user_password')
        
        private_key = cls._load_private_key(identity_file) if identity_file else None
        
        if not user_password:
            user_key = f"{username}@{hostname}"
            user_password = cls._user_passwords.get(user_key)
        
        try:
            client.connect(hostname=hostname, username=username, pkey=private_key, password=user_password)
        except paramiko.AuthenticationException:
            if not user_password:
                user_password = cls._get_user_password(username, hostname)
                if user_password:
                    cls._user_passwords[f"{username}@{hostname}"] = user_password
                    client.connect(hostname=hostname, username=username, pkey=private_key, password=user_password)
                else:
                    raise
            else:
                raise
        
        return client
    
    @classmethod
    def _load_private_key(cls, key_path):
        key_path = os.path.expanduser(key_path)
        password = cls._key_passwords.get(key_path)
        
        for key_class in [paramiko.RSAKey, paramiko.ECDSAKey, paramiko.Ed25519Key]:
            try:
                return key_class.from_private_key_file(key_path, password=password)
            except paramiko.PasswordRequiredException:
                if password is None:
                    password = cls._get_key_password(key_path)
                    if password:
                        cls._key_passwords[key_path] = password
                        try:
                            return key_class.from_private_key_file(key_path, password=password)
                        except:
                            continue
            except:
                continue
        
        raise ValueError(f"Unable to load private key: {key_path}")
    
    @classmethod
    def _get_user_password(cls, username, hostname):
        dialog = UserPasswordDialog(username, hostname)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_password()
        return None
    
    @classmethod
    def _get_key_password(cls, key_path):
        dialog = KeyPasswordDialog(key_path)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_password()
        return None
    
    @classmethod
    def cleanup(cls):
        with cls._lock:
            for client, _ in cls._connections.values():
                try:
                    client.close()
                except:
                    pass
            cls._connections.clear()