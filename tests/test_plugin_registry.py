"""
Unit tests for Plugin Registry
"""
import pytest
from scribe.plugins.registry import PluginRegistry
from scribe.plugins.base import BasePlugin, CommandDefinition, PluginError


class TestPluginRegistry:
    """Test suite for Plugin Registry"""
    
    def test_registry_initialization(self):
        """Test that registry initializes empty"""
        registry = PluginRegistry()
        assert len(registry._plugins) == 0
        assert len(registry._commands) == 0
    
    def test_register_valid_plugin(self, mock_plugin):
        """Test registering a valid plugin"""
        registry = PluginRegistry()
        result = registry.register_plugin(mock_plugin)
        
        assert result is True
        assert mock_plugin.name in registry._plugins
        assert mock_plugin.initialized is True
    
    def test_register_plugin_with_commands(self, mock_plugin):
        """Test that plugin commands are registered"""
        registry = PluginRegistry()
        registry.register_plugin(mock_plugin)
        
        # Check that commands were registered
        assert len(registry._commands) > 0
        
        # Check specific patterns
        assert "test command" in registry._commands
        assert "test {param}" in registry._commands
    
    def test_duplicate_plugin_registration(self, mock_plugin):
        """Test that duplicate plugins are rejected"""
        registry = PluginRegistry()
        
        # First registration should succeed
        assert registry.register_plugin(mock_plugin) is True
        
        # Second registration should fail
        assert registry.register_plugin(mock_plugin) is False
    
    def test_invalid_plugin_rejected(self):
        """Test that invalid plugins are rejected"""
        class InvalidPlugin(BasePlugin):
            name = ""  # Invalid: empty name
            version = "1.0.0"
            
            def commands(self):
                return []
            
            def initialize(self, config):
                return True
        
        registry = PluginRegistry()
        plugin = InvalidPlugin()
        
        with pytest.raises(PluginError):
            registry.register_plugin(plugin)
    
    def test_plugin_initialization_failure(self):
        """Test handling of plugin initialization failure"""
        class FailingPlugin(BasePlugin):
            name = "failing_plugin"
            version = "1.0.0"
            
            def commands(self):
                return []
            
            def initialize(self, config):
                return False  # Initialization fails
        
        registry = PluginRegistry()
        plugin = FailingPlugin()
        
        result = registry.register_plugin(plugin)
        assert result is False
    
    def test_plugin_initialization_exception(self):
        """Test handling of exception during plugin initialization"""
        class ExceptionPlugin(BasePlugin):
            name = "exception_plugin"
            version = "1.0.0"
            
            def commands(self):
                return []
            
            def initialize(self, config):
                raise RuntimeError("Initialization error!")
        
        registry = PluginRegistry()
        plugin = ExceptionPlugin()
        
        with pytest.raises(PluginError):
            registry.register_plugin(plugin)
    
    def test_plugin_shutdown(self, mock_plugin):
        """Test plugin shutdown"""
        registry = PluginRegistry()
        registry.register_plugin(mock_plugin)
        
        assert mock_plugin.initialized is True
        
        registry.shutdown_all()
        
        assert mock_plugin.initialized is False
    
    def test_get_plugin(self, mock_plugin):
        """Test retrieving registered plugin"""
        registry = PluginRegistry()
        registry.register_plugin(mock_plugin)
        
        retrieved = registry.get_plugin(mock_plugin.name)
        assert retrieved is mock_plugin
    
    def test_get_nonexistent_plugin(self):
        """Test retrieving non-existent plugin returns None"""
        registry = PluginRegistry()
        
        result = registry.get_plugin("nonexistent")
        assert result is None
    
    def test_list_plugins(self, mock_plugin):
        """Test listing all registered plugins"""
        registry = PluginRegistry()
        registry.register_plugin(mock_plugin)
        
        plugins = registry.list_plugins()
        assert len(plugins) == 1
        assert plugins[0] == mock_plugin.name
    
    def test_command_execution(self, mock_plugin):
        """Test executing a command through registry"""
        registry = PluginRegistry()
        registry.register_plugin(mock_plugin)
        
        # Get a registered command
        commands = registry._commands.get("test command")
        assert commands is not None
        assert len(commands) > 0
        
        # Execute command
        result = commands[0].execute()
        
        # Check that handler was called
        assert len(mock_plugin.commands_called) == 1
        assert mock_plugin.commands_called[0]["handler"] == "test_handler"
    
    def test_command_execution_with_params(self, mock_plugin):
        """Test executing a command with parameters"""
        registry = PluginRegistry()
        registry.register_plugin(mock_plugin)
        
        # Get a parametrized command
        commands = registry._commands.get("test {param}")
        assert commands is not None
        
        # Execute with parameter
        result = commands[0].execute(param="hello")
        
        # Check that handler received parameter
        assert len(mock_plugin.commands_called) == 1
        assert mock_plugin.commands_called[0]["param"] == "hello"
        assert "hello" in result
    
    def test_plugin_with_no_commands(self):
        """Test plugin with no commands"""
        class NoCommandsPlugin(BasePlugin):
            name = "no_commands"
            version = "1.0.0"
            
            def commands(self):
                return []  # No commands
            
            def initialize(self, config):
                return True
        
        registry = PluginRegistry()
        plugin = NoCommandsPlugin()
        
        result = registry.register_plugin(plugin)
        assert result is True
        assert plugin.name in registry._plugins
    
    def test_plugin_with_multiple_patterns(self):
        """Test plugin with multiple patterns for same command"""
        class MultiPatternPlugin(BasePlugin):
            name = "multi_pattern"
            version = "1.0.0"
            
            def __init__(self):
                self.called = False
            
            def commands(self):
                return [
                    CommandDefinition(
                        patterns=["start", "begin", "go"],
                        handler=self.start_handler,
                        examples=["start", "begin"],
                        description="Start something"
                    )
                ]
            
            def initialize(self, config):
                return True
            
            def start_handler(self):
                self.called = True
                return "Started"
        
        registry = PluginRegistry()
        plugin = MultiPatternPlugin()
        registry.register_plugin(plugin)
        
        # All three patterns should be registered
        assert "start" in registry._commands
        assert "begin" in registry._commands
        assert "go" in registry._commands
        
        # All should point to same handler
        registry._commands["start"][0].execute()
        assert plugin.called is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
