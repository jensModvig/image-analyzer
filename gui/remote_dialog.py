import os
import socket
import threading
import paramiko
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel, QFileDialog
from PyQt6.QtCore import QTimer, pyqtSignal
from core.settings import Settings

class RemoteImageDialog(QDialog):
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Remote Image")
        self.setModal(True)
        self.resize(500, 250)
        self.settings = Settings()
        self._status_timer = QTimer()
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._check_status)
        self._checking = False
        self._last_hostname = ""
        
        layout = QVBoxLayout(self)
        
        self.host_combo = self._create_combo("SSH Config Host (optional):", layout)
        self.hostname_field = self._create_field("Hostname:", layout, self._on_hostname_changed)
        self.username_field = self._create_field("Username:", layout, self._update_form)
        self.identity_file_field = self._create_file_field("Identity File:", layout)
        self.remote_path_field = self._create_field("Remote Path:", layout)
        
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Enter hostname to check status")
        self.status_ball = QLabel()
        self.status_ball.setFixedSize(12, 12)
        self.status_ball.setStyleSheet("background-color: gray; border-radius: 6px;")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_ball)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        self._create_buttons(layout)
        self._load_ssh_hosts()
        self._load_settings()
        self.status_updated.connect(lambda text: (self._set_status_with_color(text), setattr(self, '_checking', False)))
        
        if self.hostname_field.text().strip():
            self._status_timer.start(100)
    
    def _create_combo(self, label, layout):
        layout.addWidget(QLabel(label))
        combo = QComboBox()
        combo.addItem("")
        combo.currentTextChanged.connect(self._host_selected)
        layout.addWidget(combo)
        return combo
    
    def _create_field(self, label, layout, callback=None):
        layout.addWidget(QLabel(label))
        field = QLineEdit()
        if callback:
            field.textChanged.connect(callback)
        layout.addWidget(field)
        return field
    
    def _create_file_field(self, label, layout):
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel(label))
        field = QLineEdit()
        browse = QPushButton("Browse")
        browse.clicked.connect(lambda: self._browse_file(field))
        hlayout.addWidget(field)
        hlayout.addWidget(browse)
        layout.addLayout(hlayout)
        return field
    
    def _create_buttons(self, layout):
        hlayout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._save_and_accept)
        self.connect_button.setDefault(True)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        hlayout.addStretch()
        hlayout.addWidget(self.connect_button)
        hlayout.addWidget(cancel)
        layout.addLayout(hlayout)
    
    def _set_status(self, text, color):
        self.status_label.setText(text)
        self.status_ball.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
    
    def _set_status_with_color(self, text):
        colors = {"Connecting...": "orange", "Logged in": "green", "Server online": "green", "Server offline": "red"}
        self._set_status(text, colors.get(text, "gray"))
    
    def _on_hostname_changed(self):
        self._update_form()
        hostname = self.hostname_field.text().strip()
        if hostname != self._last_hostname:
            self._status_timer.stop()
            if hostname:
                self._set_status("Connecting...", "orange")
                self._status_timer.start(1000)
            else:
                self._set_status("Enter hostname to check status", "gray")
    
    def _update_form(self):
        enabled = bool(self.hostname_field.text().strip() and self.username_field.text().strip())
        self.connect_button.setEnabled(enabled)
    
    def _check_status(self):
        if self._checking:
            return
        hostname = self.hostname_field.text().strip()
        if not hostname:
            return
        
        self._checking = True
        self._last_hostname = hostname
        self._set_status("Connecting...", "orange")
        threading.Thread(target=self._ping_server, args=(hostname,), daemon=True).start()
    
    def _ping_server(self, hostname):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            offline = sock.connect_ex((hostname, 22)) != 0
            sock.close()
            
            if offline:
                self.status_updated.emit("Server offline")
                return
            
            username = self.username_field.text().strip()
            if username:
                from core.ssh_manager import SSHConnectionPool
                key = f"{username}@{hostname}"
                with SSHConnectionPool._lock:
                    if key in SSHConnectionPool._connections:
                        client, _ = SSHConnectionPool._connections[key]
                        if client.get_transport() and client.get_transport().is_active():
                            self.status_updated.emit("Logged in")
                            return
            
            self.status_updated.emit("Server online")
        except Exception:
            self.status_updated.emit("Server offline")
    
    def _load_ssh_hosts(self):
        config_path = os.path.expanduser('~/.ssh/config')
        if not os.path.exists(config_path):
            return
        
        config = paramiko.SSHConfig()
        with open(config_path) as f:
            config.parse(f)
        
        hosts = [host for host in config.get_hostnames() if host != '*']
        self.host_combo.addItems(hosts)
    
    def _load_settings(self):
        saved = self.settings.get('remote_dialog', {})
        self.host_combo.setCurrentText(saved.get('host', ''))
        self.hostname_field.setText(saved.get('hostname', ''))
        self.username_field.setText(saved.get('username', ''))
        self.identity_file_field.setText(saved.get('identity_file', ''))
        self.remote_path_field.setText(saved.get('remote_path', ''))
        self._update_form()
    
    def _host_selected(self, host):
        if not host:
            return
        
        config_path = os.path.expanduser('~/.ssh/config')
        config = paramiko.SSHConfig()
        with open(config_path) as f:
            config.parse(f)
        
        host_config = config.lookup(host)
        self.hostname_field.setText(host_config.get('hostname', ''))
        self.username_field.setText(host_config.get('user', ''))
        identity_files = host_config.get('identityfile', [])
        if identity_files:
            self.identity_file_field.setText(identity_files[0])
        self._on_hostname_changed()
    
    def _browse_file(self, field):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Identity File", os.path.expanduser("~/.ssh"))
        if filename:
            field.setText(filename)
    
    def _save_and_accept(self):
        self.settings.set('remote_dialog', {
            'host': self.host_combo.currentText(),
            'hostname': self.hostname_field.text(),
            'username': self.username_field.text(),
            'identity_file': self.identity_file_field.text(),
            'remote_path': self.remote_path_field.text()
        })
        self.accept()
    
    def get_connection_info(self):
        return {
            'hostname': self.hostname_field.text(),
            'username': self.username_field.text(),
            'identity_file': self.identity_file_field.text() or None,
            'user_password': None,
            'config_host': self.host_combo.currentText() or None
        }
    
    def get_remote_path(self):
        return self.remote_path_field.text()