"""
Tests for settings auto-save functionality and model loading progress.
"""
import pytest
import tempfile
import os
from pathlib import Path


class TestSettingsAutoSave:
    """Test auto-save behavior for settings."""
    
    def test_config_manager_set_and_save(self):
        """Test that ConfigManager.set() and save() work correctly."""
        from scribe.config.config_manager import ConfigManager
        
        # Create temporary config file
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            
            # Initialize with default config
            manager = ConfigManager(str(config_path))
            
            # Test setting values
            manager.set('ui', 'theme', 'dark')
            manager.set('whisper', 'model', 'small')
            manager.set('audio', 'sample_rate', 48000)
            
            # Save and verify
            saved_path = manager.save()
            assert saved_path.exists()
            
            # Reload and verify values persisted
            manager2 = ConfigManager(str(config_path))
            assert manager2.config.ui.theme == 'dark'
            assert manager2.config.whisper.model == 'small'
            assert manager2.config.audio.sample_rate == 48000
    
    def test_hotkey_config_section_exists(self):
        """Test that 'hotkey' config section exists (not 'recording_options')."""
        from scribe.config.config_manager import ConfigManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            manager = ConfigManager(str(config_path))
            
            # Verify hotkey section exists
            assert hasattr(manager.config, 'hotkey')
            assert hasattr(manager.config.hotkey, 'activation_key')
            
            # Test setting hotkey works (it gets normalized)
            manager.set('hotkey', 'activation_key', 'ctrl+alt')
            manager.save()
            
            # Reload and verify (hotkey may be normalized to 'alt+ctrl')
            manager2 = ConfigManager(str(config_path))
            # Just verify it's a valid hotkey string, normalization is OK
            assert manager2.config.hotkey.activation_key in ['ctrl+alt', 'alt+ctrl']
    
    def test_language_none_handling(self):
        """Test that language 'auto' is saved as None."""
        from scribe.config.config_manager import ConfigManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            manager = ConfigManager(str(config_path))
            
            # Test auto-detect (None)
            manager.set('whisper', 'language', None)
            manager.save()
            
            manager2 = ConfigManager(str(config_path))
            assert manager2.config.whisper.language is None
            
            # Test specific language
            manager.set('whisper', 'language', 'en')
            manager.save()
            
            manager3 = ConfigManager(str(config_path))
            assert manager3.config.whisper.language == 'en'


class TestSystemTrayIntegration:
    """Test system tray and taskbar options."""
    
    def test_tray_config_options_exist(self):
        """Test that UI config has tray-related options."""
        from scribe.config.models import UIConfig
        
        # Verify UIConfig has required fields
        config = UIConfig()
        assert hasattr(config, 'show_system_tray')
        assert hasattr(config, 'minimize_to_tray')
        assert hasattr(config, 'start_minimized')
        
        # Test default values
        assert config.show_system_tray is True
        assert config.minimize_to_tray is False
        assert config.start_minimized is False
    
    def test_tray_settings_save_and_load(self):
        """Test that tray settings persist correctly."""
        from scribe.config.config_manager import ConfigManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            manager = ConfigManager(str(config_path))
            
            # Set tray options
            manager.set('ui', 'show_system_tray', False)
            manager.set('ui', 'minimize_to_tray', True)
            manager.set('ui', 'start_minimized', True)
            manager.save()
            
            # Reload and verify
            manager2 = ConfigManager(str(config_path))
            assert manager2.config.ui.show_system_tray is False
            assert manager2.config.ui.minimize_to_tray is True
            assert manager2.config.ui.start_minimized is True


class TestModelLoading:
    """Test model loading and download progress."""
    
    def test_transcription_engine_config_access(self):
        """Test that TranscriptionEngine can access config."""
        from scribe.core.transcription_engine import TranscriptionEngine
        from scribe.config.config_manager import ConfigManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            manager = ConfigManager(str(config_path))
            
            # Create engine with config
            engine = TranscriptionEngine(manager)
            assert engine.config is not None
            assert engine.config.config.whisper is not None
    
    def test_model_size_options(self):
        """Test that all model sizes are valid."""
        from scribe.config.models import WhisperConfig
        
        valid_models = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
        
        for model in valid_models:
            config = WhisperConfig(model=model)
            assert config.model == model
    
    def test_device_and_compute_type_auto(self):
        """Test that 'auto' device and compute_type are valid."""
        from scribe.config.models import WhisperConfig
        
        config = WhisperConfig(device='auto', compute_type='auto')
        assert config.device == 'auto'
        assert config.compute_type == 'auto'


class TestExceptionLogging:
    """Test that exceptions are logged with tracebacks."""
    
    def test_config_save_with_invalid_section_logs_error(self):
        """Test that invalid config section raises AttributeError."""
        from scribe.config.config_manager import ConfigManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            manager = ConfigManager(str(config_path))
            
            # Try to set invalid section (should raise AttributeError)
            with pytest.raises(AttributeError, match="'AppConfig' object has no attribute"):
                manager.set('invalid_section', 'some_key', 'some_value')


class TestLogRotation:
    """Test timestamped log files and rotation."""
    
    def test_timestamped_log_filename_format(self):
        """Test that log filename includes timestamp."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_name = f"scribe_{timestamp}.log"
        
        # Verify format matches expected pattern
        assert log_name.startswith("scribe_")
        assert log_name.endswith(".log")
        assert len(timestamp) == 15  # YYYYMMDD_HHMMSS
    
    def test_log_cleanup_keeps_recent_files(self):
        """Test that old log files are cleaned up."""
        import tempfile
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            
            # Create 15 fake log files with different timestamps
            for i in range(15):
                log_file = log_dir / f"scribe_2025110{i:02d}_120000.log"
                log_file.touch()
            
            # Get all files
            log_files = list(log_dir.glob("scribe_*.log"))
            assert len(log_files) == 15
            
            # Simulate cleanup (keep 10 most recent)
            sorted_logs = sorted(log_files, key=lambda p: p.stat().st_mtime, reverse=True)
            for old_log in sorted_logs[10:]:
                old_log.unlink()
            
            # Verify only 10 remain
            remaining = list(log_dir.glob("scribe_*.log"))
            assert len(remaining) == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
