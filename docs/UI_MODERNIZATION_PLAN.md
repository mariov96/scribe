# Scribe UI/UX Modernization Plan

**Status**: APPROVED - Ready for implementation  
**Timeline**: 3 weeks  
**Priority**: HIGH - Addresses ugly inherited UI + fragmented config system  

---

## 🎯 Goals

### **Primary Objectives**
1. ✅ **Replace ugly PyQt5 UI** with modern Fluent Design (PySide6)
2. ✅ **Build modern config system** to replace legacy WhisperWriter coupling
3. ✅ **Expose all settings** - Analytics, plugins, audio, transcription, AI
4. ✅ **Create maintainable architecture** - Clean separation of concerns
5. ✅ **Enable extensibility** - Plugin configuration UI out of the box

### **Success Criteria**
- Modern, professional UI (9/10 aesthetics)
- All settings accessible and organized
- Plugin management interface
- Analytics dashboard with metrics
- YAML-based config with validation
- No legacy config coupling
- Easy to extend with new features

---

## 📐 Architecture Overview

### **New Structure**
```
src/scribe/
├── config/
│   ├── __init__.py
│   ├── schema.py           # Pydantic models for validation
│   ├── manager.py          # New ConfigManager (YAML-based)
│   ├── defaults.py         # Default configuration
│   └── migrations.py       # Migrate from old config
├── ui_fluent/              # NEW - Modern UI
│   ├── __init__.py
│   ├── main_window.py      # MSFluentWindow with navigation
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py         # Dashboard with metrics
│   │   ├── transcription.py # Main workflow
│   │   ├── plugins.py      # Plugin management
│   │   ├── analytics.py    # Detailed analytics
│   │   └── settings.py     # Configuration UI
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── plugin_card.py  # Reusable plugin UI
│   │   ├── value_card.py   # Metric display
│   │   ├── config_widget.py # Auto-generate UI from config schema
│   │   └── param_widget.py # Setting display
│   └── themes/
│       ├── __init__.py
│       └── scribe_theme.py # Custom theming
├── ui/                     # OLD - To be deprecated
│   └── (existing PyQt5 files)
└── app.py                  # Update to use new UI + config
```

---

## 🔧 Phase 1: Modern Config System (Week 1)

### **Goal**: Replace legacy config with YAML + Pydantic validation

### **Step 1.1: Define Config Schema** (Day 1)

**File**: `src/scribe/config/schema.py`

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from pathlib import Path

class AudioConfig(BaseModel):
    """Audio recording configuration"""
    device_index: Optional[int] = None
    sample_rate: int = Field(default=16000, ge=8000, le=48000)
    channels: int = Field(default=1, ge=1, le=2)
    chunk_size: int = Field(default=1024, ge=512, le=4096)
    noise_reduction: bool = True
    silence_threshold: float = Field(default=0.02, ge=0.0, le=1.0)
    silence_duration: float = Field(default=1.0, ge=0.1, le=5.0)

class TranscriptionConfig(BaseModel):
    """Whisper transcription configuration"""
    model_size: str = Field(default="base", pattern="^(tiny|base|small|medium|large|large-v2|large-v3)$")
    language: Optional[str] = None  # None = auto-detect
    device: str = Field(default="cpu", pattern="^(cpu|cuda)$")
    compute_type: str = Field(default="int8", pattern="^(int8|float16|float32)$")
    beam_size: int = Field(default=5, ge=1, le=10)
    vad_filter: bool = True
    condition_on_previous_text: bool = True

class HotkeyConfig(BaseModel):
    """Hotkey configuration"""
    activation_key: str = "ctrl+alt"
    activation_key_secondary: Optional[str] = None
    recording_mode: str = Field(default="voice_activity", pattern="^(voice_activity|press_to_toggle|hold_to_record)$")
    debounce_ms: int = Field(default=500, ge=0, le=2000)

class AIConfig(BaseModel):
    """AI enhancement configuration"""
    enabled: bool = True
    provider: str = Field(default="together", pattern="^(together|openai|local)$")
    model: str = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=50, le=2000)
    system_prompt: str = "Clean up this transcription, remove filler words, fix grammar."

class PluginConfig(BaseModel):
    """Plugin system configuration"""
    enabled_plugins: List[str] = Field(default_factory=list)
    plugin_configs: Dict[str, Dict] = Field(default_factory=dict)

class AnalyticsConfig(BaseModel):
    """Analytics and telemetry configuration"""
    enabled: bool = True
    track_usage: bool = True
    track_accuracy: bool = True
    session_tracking: bool = True
    telemetry_opt_in: bool = False  # Explicit opt-in for external telemetry

class UIConfig(BaseModel):
    """UI preferences"""
    theme: str = Field(default="auto", pattern="^(auto|light|dark)$")
    accent_color: str = "#6751A1"  # Scribe purple
    start_minimized: bool = False
    minimize_to_tray: bool = True
    show_notifications: bool = True
    window_width: int = 1200
    window_height: int = 800

class ScribeConfig(BaseModel):
    """Complete Scribe configuration"""
    version: str = "2.0"
    audio: AudioConfig = Field(default_factory=AudioConfig)
    transcription: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    hotkey: HotkeyConfig = Field(default_factory=HotkeyConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    
    class Config:
        extra = "forbid"  # Reject unknown fields
```

### **Step 1.2: Build Config Manager** (Day 2)

**File**: `src/scribe/config/manager.py`

```python
import yaml
from pathlib import Path
from typing import Optional
from .schema import ScribeConfig
from pydantic import ValidationError

class ConfigManager:
    """Modern YAML-based configuration manager"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._default_config_path()
        self.config: ScribeConfig = self._load_or_create()
    
    def _default_config_path(self) -> Path:
        """Get default config path"""
        from ..config.paths import get_config_dir
        return get_config_dir() / "config.yaml"
    
    def _load_or_create(self) -> ScribeConfig:
        """Load existing config or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                return ScribeConfig(**data)
            except (yaml.YAMLError, ValidationError) as e:
                # Log error, fall back to defaults
                print(f"Config error: {e}. Using defaults.")
                return ScribeConfig()
        else:
            # Create default config
            config = ScribeConfig()
            self.save(config)
            return config
    
    def save(self, config: Optional[ScribeConfig] = None) -> None:
        """Save configuration to YAML"""
        if config:
            self.config = config
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(
                self.config.dict(),
                f,
                default_flow_style=False,
                sort_keys=False
            )
    
    def get(self, key_path: str, default=None):
        """Get nested config value by dot notation"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            value = getattr(value, key, None)
            if value is None:
                return default
        return value
    
    def update(self, **kwargs) -> None:
        """Update config values"""
        data = self.config.dict()
        data.update(kwargs)
        self.config = ScribeConfig(**data)
        self.save()
    
    def reset_to_defaults(self) -> None:
        """Reset to default configuration"""
        self.config = ScribeConfig()
        self.save()
```

### **Step 1.3: Migration from Legacy** (Day 2)

**File**: `src/scribe/config/migrations.py`

```python
def migrate_from_legacy() -> ScribeConfig:
    """Migrate from old WhisperWriter config to new YAML"""
    try:
        # Import old config system
        from whisperwriter import config as old_config
        
        # Map old values to new schema
        new_config = ScribeConfig(
            audio=AudioConfig(
                sample_rate=old_config.sample_rate,
                # ... map other audio settings
            ),
            transcription=TranscriptionConfig(
                model_size=old_config.model_size,
                # ... map other transcription settings
            ),
            # ... etc
        )
        
        return new_config
    except Exception as e:
        print(f"Migration failed: {e}. Using defaults.")
        return ScribeConfig()
```

### **Deliverables - Week 1**
- ✅ Pydantic schema with full validation
- ✅ YAML-based ConfigManager
- ✅ Migration from legacy config
- ✅ Unit tests for config system
- ✅ Documentation

---

## 🎨 Phase 2: Fluent UI Core (Week 2)

### **Goal**: Build main window + navigation + core pages

### **Step 2.1: Main Window** (Day 3-4)

**File**: `src/scribe/ui_fluent/main_window.py`

```python
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import (
    MSFluentWindow,
    NavigationItemPosition,
    FluentIcon as FIF,
)
from .pages import HomePage, TranscriptionPage, PluginsPage, AnalyticsPage, SettingsPage

class ScribeMainWindow(MSFluentWindow):
    """Main application window with Fluent Design"""
    
    # Signals
    recording_started = Signal()
    recording_stopped = Signal()
    transcription_complete = Signal(str)
    
    def __init__(self, config_manager, plugin_registry, value_calculator):
        super().__init__()
        
        self.config_manager = config_manager
        self.plugin_registry = plugin_registry
        self.value_calculator = value_calculator
        
        self._setup_window()
        self._create_pages()
        self._add_navigation()
        self._connect_signals()
    
    def _setup_window(self):
        """Configure main window"""
        config = self.config_manager.config.ui
        
        self.setWindowTitle("Scribe - Voice Control")
        self.resize(config.window_width, config.window_height)
        
        # Apply theme
        from qfluentwidgets import setTheme, Theme, setThemeColor
        theme_map = {"auto": Theme.AUTO, "light": Theme.LIGHT, "dark": Theme.DARK}
        setTheme(theme_map[config.theme])
        setThemeColor(config.accent_color)
    
    def _create_pages(self):
        """Create all UI pages"""
        self.home_page = HomePage(
            self.config_manager,
            self.value_calculator,
            self
        )
        
        self.transcription_page = TranscriptionPage(
            self.config_manager,
            self
        )
        
        self.plugins_page = PluginsPage(
            self.config_manager,
            self.plugin_registry,
            self
        )
        
        self.analytics_page = AnalyticsPage(
            self.value_calculator,
            self
        )
        
        self.settings_page = SettingsPage(
            self.config_manager,
            self
        )
    
    def _add_navigation(self):
        """Add navigation items"""
        self.addSubInterface(self.home_page, FIF.HOME, "Home")
        self.addSubInterface(self.transcription_page, FIF.MICROPHONE, "Transcribe")
        self.addSubInterface(self.plugins_page, FIF.GAME, "Plugins")
        self.addSubInterface(self.analytics_page, FIF.CHART, "Analytics")
        
        # Settings at bottom
        self.addSubInterface(
            self.settings_page,
            FIF.SETTING,
            "Settings",
            position=NavigationItemPosition.BOTTOM
        )
    
    def _connect_signals(self):
        """Connect internal signals"""
        # Connect transcription page signals to app logic
        self.transcription_page.start_recording.connect(self._on_start_recording)
        self.transcription_page.stop_recording.connect(self._on_stop_recording)
        
        # Connect settings changes to apply immediately
        self.settings_page.config_changed.connect(self._on_config_changed)
    
    def _on_start_recording(self):
        """Handle recording start"""
        self.recording_started.emit()
    
    def _on_stop_recording(self):
        """Handle recording stop"""
        self.recording_stopped.emit()
    
    def _on_config_changed(self, section: str):
        """Handle configuration changes"""
        if section == "ui":
            # Reapply theme
            self._setup_window()
```

### **Step 2.2: Settings Page with Auto-Generated UI** (Day 5)

**File**: `src/scribe/ui_fluent/widgets/config_widget.py`

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    SwitchButton, ComboBox, LineEdit, SpinBox, Slider,
    BodyLabel, SubtitleLabel, CardWidget
)
from pydantic import BaseModel
from typing import Any, Dict

class ConfigWidget(QWidget):
    """Auto-generate UI from Pydantic model"""
    
    def __init__(self, model: BaseModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.widgets: Dict[str, QWidget] = {}
        self._build_ui()
    
    def _build_ui(self):
        """Generate UI from model fields"""
        layout = QVBoxLayout(self)
        
        for field_name, field in self.model.__fields__.items():
            widget = self._create_widget_for_field(field_name, field)
            if widget:
                self.widgets[field_name] = widget
                layout.addWidget(widget)
    
    def _create_widget_for_field(self, name: str, field) -> QWidget:
        """Create appropriate widget based on field type"""
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        
        # Label
        label = SubtitleLabel(self._format_label(name))
        card_layout.addWidget(label)
        
        # Description (from field description)
        if field.field_info.description:
            desc = BodyLabel(field.field_info.description)
            desc.setWordWrap(True)
            card_layout.addWidget(desc)
        
        # Control based on type
        if field.type_ == bool:
            control = SwitchButton()
            control.setChecked(getattr(self.model, name))
        elif hasattr(field.type_, '__origin__') and field.type_.__origin__ is list:
            # List type - use ComboBox for string lists
            control = ComboBox()
            # ... populate from options
        elif field.field_info.ge is not None:
            # Numeric with bounds - use Slider
            control = Slider(Qt.Horizontal)
            control.setRange(field.field_info.ge, field.field_info.le or 100)
            control.setValue(getattr(self.model, name))
        else:
            # Default to LineEdit
            control = LineEdit()
            control.setText(str(getattr(self.model, name)))
        
        card_layout.addWidget(control)
        return card
    
    def _format_label(self, field_name: str) -> str:
        """Convert field_name to Title Case"""
        return field_name.replace('_', ' ').title()
    
    def get_values(self) -> Dict[str, Any]:
        """Extract values from all widgets"""
        values = {}
        for name, widget in self.widgets.items():
            if isinstance(widget, SwitchButton):
                values[name] = widget.isChecked()
            elif isinstance(widget, LineEdit):
                values[name] = widget.text()
            # ... etc for other types
        return values
```

**File**: `src/scribe/ui_fluent/pages/settings.py`

```python
class SettingsPage(ScrollArea):
    """Settings page with auto-generated config UI"""
    
    config_changed = Signal(str)  # section name
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self._build_ui()
    
    def _build_ui(self):
        """Build settings UI from config schema"""
        layout = QVBoxLayout()
        
        # Audio Settings
        audio_section = SubtitleLabel("Audio")
        audio_widget = ConfigWidget(self.config_manager.config.audio)
        layout.addWidget(audio_section)
        layout.addWidget(audio_widget)
        
        # Transcription Settings
        transcription_section = SubtitleLabel("Transcription")
        transcription_widget = ConfigWidget(self.config_manager.config.transcription)
        layout.addWidget(transcription_section)
        layout.addWidget(transcription_widget)
        
        # AI Settings
        ai_section = SubtitleLabel("AI Enhancement")
        ai_widget = ConfigWidget(self.config_manager.config.ai)
        layout.addWidget(ai_section)
        layout.addWidget(ai_widget)
        
        # Save button
        save_btn = PrimaryPushButton("Save Changes")
        save_btn.clicked.connect(self._save_config)
        layout.addWidget(save_btn)
    
    def _save_config(self):
        """Save all config changes"""
        # Collect values from all ConfigWidgets
        # Update config_manager
        # Emit signal for each changed section
        self.config_changed.emit("all")
```

### **Deliverables - Week 2**
- ✅ Main window with navigation
- ✅ Home page (dashboard)
- ✅ Transcription page
- ✅ Plugins page
- ✅ Settings page (auto-generated from config schema)
- ✅ All pages connected to config manager

---

## 📊 Phase 3: Analytics & Polish (Week 3)

### **Goal**: Analytics dashboard, plugin UI integration, testing

### **Step 3.1: Analytics Dashboard** (Day 6-7)

**File**: `src/scribe/ui_fluent/pages/analytics.py`

- Detailed charts (time saved over time, accuracy trends, command usage)
- Export analytics data
- Per-plugin metrics
- Session history viewer

### **Step 3.2: Plugin Configuration UI** (Day 7-8)

**File**: `src/scribe/ui_fluent/pages/plugins.py`

- Plugin cards with enable/disable
- Configuration dialogs per plugin
- Status indicators
- Install/uninstall UI

### **Step 3.3: Integration & Testing** (Day 9-10)

- Connect UI to real app logic
- Replace old UI in `app.py`
- System tray integration
- Hotkey feedback in UI
- Testing all workflows
- Bug fixes

### **Deliverables - Week 3**
- ✅ Complete analytics dashboard
- ✅ Plugin management fully functional
- ✅ All settings exposed and working
- ✅ Old UI deprecated
- ✅ Testing complete

---

## 🎯 Benefits

### **Immediate Wins**
- ✅ **Modern UI** - 6/10 → 9/10 aesthetics (+50%)
- ✅ **All settings accessible** - No more buried config
- ✅ **Plugin management** - Enable/disable/configure from UI
- ✅ **Analytics visible** - Prove value to users
- ✅ **Maintainable** - Clean architecture, easy to extend

### **Technical Improvements**
- ✅ **No legacy coupling** - Clean break from WhisperWriter config
- ✅ **Type-safe config** - Pydantic validation prevents errors
- ✅ **Auto-generated UI** - Settings pages build themselves from schema
- ✅ **YAML config** - Human-readable, version-controllable
- ✅ **Plugin configs** - Each plugin can have its own settings

### **User Experience**
- ✅ **One place for everything** - Settings, analytics, plugins all accessible
- ✅ **Visual feedback** - Status indicators, notifications, progress
- ✅ **Theme customization** - Dark/light mode, accent colors
- ✅ **Professional polish** - Matches modern desktop apps

---

## 📋 Implementation Checklist

### **Week 1: Config System**
- [ ] Create `src/scribe/config/schema.py` with Pydantic models
- [ ] Build `src/scribe/config/manager.py` with YAML support
- [ ] Create `src/scribe/config/migrations.py` for legacy migration
- [ ] Write unit tests for config system
- [ ] Update `app.py` to use new ConfigManager
- [ ] Test migration from old config

### **Week 2: Core UI**
- [ ] Create `src/scribe/ui_fluent/` directory structure
- [ ] Build `main_window.py` with navigation
- [ ] Create `pages/home.py` (dashboard)
- [ ] Create `pages/transcription.py` (main workflow)
- [ ] Create `pages/plugins.py` (plugin management)
- [ ] Create `widgets/config_widget.py` (auto-gen UI)
- [ ] Create `pages/settings.py` (all settings)
- [ ] Connect signals between pages and app logic

### **Week 3: Analytics & Polish**
- [ ] Create `pages/analytics.py` (detailed dashboard)
- [ ] Implement plugin configuration dialogs
- [ ] Connect UI to real audio/transcription
- [ ] System tray integration
- [ ] Hotkey feedback in UI
- [ ] Testing all workflows
- [ ] Deprecate old UI
- [ ] Documentation
- [ ] Bug fixes

---

## 🚀 Migration Strategy

### **Gradual Rollout**
1. **Config first** - New config system works alongside old UI
2. **UI parallel** - Run new UI in parallel, fallback to old if issues
3. **Feature parity** - All old UI features work in new UI
4. **Deprecation** - Remove old UI code
5. **Polish** - Refinements and improvements

### **Risk Mitigation**
- Keep old UI until new UI is feature-complete
- Extensive testing before deprecating old code
- Migration script for users' existing configs
- Documentation for troubleshooting

---

## 🎉 Expected Outcome

**After 3 weeks**:
- ✅ Modern, professional UI (9/10 aesthetics)
- ✅ All settings exposed and organized
- ✅ Plugin management interface
- ✅ Analytics dashboard
- ✅ YAML-based config with validation
- ✅ No legacy coupling
- ✅ Maintainable, extensible architecture
- ✅ Users can see and control everything

**This addresses**:
- User complaint: "UI/UX could use a big overhaul, it's ugly by inheritance"
- Code review: "Build modern config system (replace legacy)"
- Extensibility: "Access to all relevant settings, analytics, configurations"

**Ready to start?** We begin with Week 1: Config System. 🚀
