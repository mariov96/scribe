"""
Device selector component with proper icon handling.
"""

from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal as Signal, QSize

class DeviceSelector(QComboBox):
    """Audio device selection combo box with proper icon handling."""
    
    deviceSelected = Signal(dict)  # Emits device info when selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize UI components."""
        self.setMinimumWidth(200)
        self.setIconSize(QIcon().actualSize(QSize(16, 16)))  # Set reasonable icon size
        
        # Add default "System Default" option
        self.add_device("System Default", None)
    
    def add_device(self, name: str, device_id):
        """
        Add a device to the combo box.
        
        Args:
            name: Display name of the device
            device_id: Device identifier (index or name)
        """
        # Create standard icon for audio devices
        icon = QIcon.fromTheme("audio-input-microphone")
        
        # Add item with proper icon
        self.addItem(icon, name, userData={'id': device_id, 'name': name})
    
    def clear_devices(self):
        """Remove all devices except system default."""
        self.clear()
        self.add_device("System Default", None)
    
    def set_devices(self, devices: list):
        """
        Set available devices.
        
        Args:
            devices: List of device dictionaries with 'name' and 'index' keys
        """
        self.clear_devices()
        
        for device in devices:
            self.add_device(device['name'], device['index'])
    
    def current_device(self) -> dict:
        """Get currently selected device info."""
        return self.currentData()
    
    def select_device(self, device_id):
        """Select device by ID."""
        for i in range(self.count()):
            data = self.itemData(i)
            if data and data['id'] == device_id:
                self.setCurrentIndex(i)
                return True
        return False