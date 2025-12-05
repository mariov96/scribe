"""
Modern configuration manager for Scribe with YAML and Pydantic support.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Any
from PySide6.QtCore import QObject, Signal

from .models import AppConfig


class ConfigManager(QObject):
    """
    Modern configuration manager with:
    - Pydantic validation
    - YAML persistence
    - Profile support
    - Signal emissions on changes
    """
    
    # Signals for config changes
    config_changed = Signal(str)  # section name
    config_loaded = Signal()
    config_saved = Signal()
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize config manager.
        
        Args:
            config_dir: Directory for config files. Defaults to project root /config/
        """
        super().__init__()
        
        if config_dir is None:
            # Default to project_root/config/
            project_root = Path(__file__).parent.parent.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._config: Optional[AppConfig] = None
        self._config_file: Optional[Path] = None
    
    @property
    def config(self) -> AppConfig:
        """Get current configuration (loads default if not loaded)."""
        if self._config is None:
            self.load_or_create_default()
        return self._config
    
    def config_exists(self, profile: str = "default") -> bool:
        """Check if configuration file exists for given profile."""
        config_file = self.config_dir / f"{profile}.yaml"
        return config_file.exists()
    
    def load_or_create_default(self, profile: str = "default") -> AppConfig:
        """Load config from file or create default if it doesn't exist."""
        if self.config_exists(profile):
            return self.load(profile)
        else:
            return self.create_default(profile)
    
    def load(self, profile: str = "default") -> AppConfig:
        """
        Load configuration from YAML file.
        
        Args:
            profile: Profile name to load
            
        Returns:
            Loaded AppConfig instance
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValidationError: If config is invalid
        """
        config_file = self.config_dir / f"{profile}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Validate and load with Pydantic
        self._config = AppConfig(**data)
        self._config_file = config_file
        
        self.config_loaded.emit()
        return self._config
    
    def save(self, profile: Optional[str] = None) -> Path:
        """
        Save current configuration to YAML file.
        
        Args:
            profile: Profile name to save to. If None, uses current profile.
            
        Returns:
            Path to saved config file
        """
        if self._config is None:
            raise RuntimeError("No configuration loaded to save")
        
        if profile is None:
            profile = self._config.profile_name
        
        config_file = self.config_dir / f"{profile}.yaml"
        
        # Convert Pydantic model to dict
        data = self._config.model_dump(mode='python', exclude_none=False)
        
        # Write to YAML
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, indent=2)
        
        self._config_file = config_file
        self.config_saved.emit()
        
        return config_file
    
    def create_default(self, profile: str = "default") -> AppConfig:
        """
        Create default configuration.
        
        Args:
            profile: Profile name for the new config
            
        Returns:
            New AppConfig instance with defaults
        """
        self._config = AppConfig(profile_name=profile)
        self._config_file = self.config_dir / f"{profile}.yaml"
        
        # Save default config to file
        self.save(profile)
        
        return self._config
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value by section and optional key.
        
        Args:
            section: Config section (e.g., 'audio', 'hotkey')
            key: Optional key within section (e.g., 'device_id')
            default: Default value if not found
            
        Returns:
            Config value or default
            
        Example:
            >>> config.get('audio', 'sample_rate')
            16000
            >>> config.get('audio')
            AudioConfig(device_id=None, sample_rate=16000, ...)
        """
        if self._config is None:
            self.load_or_create_default()
        
        try:
            section_obj = getattr(self._config, section, None)
            if section_obj is None:
                return default
            
            if key is None:
                return section_obj
            
            return getattr(section_obj, key, default)
        except AttributeError:
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            section: Config section (e.g., 'audio')
            key: Key within section (e.g., 'device_id')
            value: New value
            
        Raises:
            ValidationError: If value is invalid for the field
        """
        if self._config is None:
            self.load_or_create_default()
        
        section_obj = getattr(self._config, section)
        setattr(section_obj, key, value)
        
        self.config_changed.emit(section)
    
    def get_plugin_config(self, plugin_name: str) -> dict:
        """
        Get plugin-specific configuration.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin config dict
        """
        return self.config.plugins.plugin_config.get(plugin_name, {})
    
    def set_plugin_config(self, plugin_name: str, config: dict) -> None:
        """
        Set plugin-specific configuration.
        
        Args:
            plugin_name: Name of the plugin
            config: Plugin configuration dict
        """
        self.config.plugins.plugin_config[plugin_name] = config
        self.config_changed.emit('plugins')
    
    def list_profiles(self) -> list[str]:
        """List all available configuration profiles."""
        yaml_files = self.config_dir.glob("*.yaml")
        return [f.stem for f in yaml_files]
    
    def switch_profile(self, profile: str) -> AppConfig:
        """
        Switch to a different configuration profile.
        
        Args:
            profile: Profile name to switch to
            
        Returns:
            Loaded AppConfig instance
        """
        return self.load(profile)
    
    def delete_profile(self, profile: str) -> bool:
        """
        Delete a configuration profile.
        
        Args:
            profile: Profile name to delete
            
        Returns:
            True if deleted, False if it didn't exist
            
        Raises:
            ValueError: If trying to delete the currently active profile
        """
        if self._config and self._config.profile_name == profile:
            raise ValueError("Cannot delete the currently active profile")
        
        config_file = self.config_dir / f"{profile}.yaml"
        if config_file.exists():
            config_file.unlink()
            return True
        return False
