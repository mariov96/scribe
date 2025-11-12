# Code Review Actions - Implementation Tracker

**Date Created**: 2024-11-08  
**Review Grade**: B+ (82/100)  
**Status**: Proposed - Awaiting Implementation

---

## 🎯 Executive Summary

Comprehensive code review identified **exceptional architecture and vision (A+)** but **incomplete core implementation (C+)**. With 5 critical fixes, project moves from alpha to usable beta. This document tracks all proposed changes for systematic implementation.

---

## 🔥 Critical Priority (Blocking v2.0 Alpha)

### 1. Implement Real Audio Recording
**File**: `src/scribe/core/audio_recorder.py`  
**Estimate**: 1-2 days  
**Status**: ⏳ Proposed  

**Current Issue**: Returns empty bytes (`b""`)

**Implementation**:
```python
import sounddevice as sd
import numpy as np
from queue import Queue

class AudioRecorder:
    def __init__(self):
        self.audio_queue = Queue()
        self.stream = None
        
    def callback(self, indata, frames, time, status):
        """Called for each audio block."""
        self.audio_queue.put(indata.copy())
        
    def start_recording(self):
        self.stream = sd.InputStream(
            callback=self.callback,
            samplerate=16000,
            channels=1,
            dtype='int16'
        )
        self.stream.start()
        
    def stop_recording(self):
        self.stream.stop()
        self.stream.close()
        
        # Collect all audio chunks
        audio_data = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())
        
        return np.concatenate(audio_data)
```

**Dependencies**: `sounddevice`, `numpy`  
**Testing**: Record 5 seconds, verify non-empty numpy array  

---

### 2. Fix Transcription Engine Initialization
**File**: `src/scribe/core/transcription_engine.py`  
**Estimate**: 1 day  
**Status**: ⏳ Proposed  

**Current Issue**: Model loading skipped with stub message

**Implementation**:
```python
def initialize(self) -> bool:
    """Initialize Whisper model."""
    try:
        # Get config values
        model_options = self.config.get('model_options', {})
        self._use_api = model_options.get('use_api', False)
        
        if not self._use_api:
            logger.info("Initializing local Whisper model...")
            
            # Import from proper location
            from faster_whisper import WhisperModel
            
            model_size = model_options.get('model', 'base')
            device = model_options.get('device', 'cpu')
            compute_type = model_options.get('compute_type', 'int8')
            
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type
            )
            logger.info(f"Local Whisper model loaded: {model_size}")
        else:
            logger.info("Using API transcription")
            self.model = None
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize: {e}", exc_info=True)
        return False
```

**Dependencies**: `faster-whisper`  
**Testing**: Load model, transcribe sample audio  

---

### 3. Implement Pattern Matching with Variable Extraction
**File**: `src/scribe/app.py`  
**Estimate**: 1 day  
**Status**: ⏳ Proposed  

**Current Issue**: Can't extract `{app}` from "switch to {app}"

**Implementation**:
```python
import re
from typing import Optional, Dict

def _extract_variables(self, text: str, pattern: str) -> Optional[Dict[str, str]]:
    """
    Extract variables from pattern.
    
    Pattern: "switch to {app}" 
    Text: "switch to chrome"
    Returns: {"app": "chrome"}
    """
    # Convert pattern to regex
    # "switch to {app}" -> "switch to (?P<app>.+)"
    regex_pattern = re.sub(
        r'\{(\w+)\}', 
        r'(?P<\1>.+?)',  # Non-greedy match
        re.escape(pattern)
    )
    
    # Make it case-insensitive and flexible with spacing
    regex_pattern = regex_pattern.replace(r'\ ', r'\s+')
    
    match = re.match(regex_pattern, text, re.IGNORECASE)
    
    return match.groupdict() if match else None

def _process_as_command(self, text: str) -> bool:
    """Execute voice command with extracted variables."""
    text_lower = text.lower().strip()
    
    for pattern, commands in self.plugin_registry._commands.items():
        variables = self._extract_variables(text_lower, pattern)
        
        if variables is not None:  # Pattern matched
            command = commands[0]
            
            try:
                logger.info(f"Executing: {pattern} with {variables}")
                result = command.execute(**variables)  # Pass variables
                
                self.value_calculator.record_command(
                    command_pattern=pattern,
                    plugin=command.plugin.name,
                    execution_time=0.05,  # Measure properly
                    success=True
                )
                
                self.plugin_command_executed.emit(
                    command.plugin.name, 
                    str(result)
                )
                
                return True
                
            except Exception as e:
                logger.error(f"Command failed: {e}")
                return False
    
    return False
```

**Testing**: Test patterns like "switch to {app}", "volume {level}", etc.

---

### 4. Add Background Threading for Operations
**File**: `src/scribe/app.py`  
**Estimate**: 1 day  
**Status**: ⏳ Proposed  

**Current Issue**: UI freezes during recording/transcription

**Implementation**:
```python
from PyQt5.QtCore import QThread, pyqtSignal

class TranscriptionWorker(QThread):
    """Background worker for transcription."""
    finished = pyqtSignal(str)  # transcribed text
    error = pyqtSignal(str)     # error message
    
    def __init__(self, audio_data, engine):
        super().__init__()
        self.audio_data = audio_data
        self.engine = engine
        
    def run(self):
        """Run in background thread."""
        try:
            result = self.engine.transcribe(self.audio_data)
            if result and result.text:
                self.finished.emit(result.text)
            else:
                self.error.emit("No speech detected")
        except Exception as e:
            self.error.emit(str(e))

# In ScribeApp._transcribe_audio():
def _transcribe_audio(self, audio_data):
    """Transcribe in background thread."""
    self.worker = TranscriptionWorker(audio_data, self.transcription_engine)
    self.worker.finished.connect(self._on_transcription_success)
    self.worker.error.connect(self._on_transcription_error)
    self.worker.start()
    
    self.transcription_started.emit()

def _on_transcription_success(self, text: str):
    """Handle successful transcription."""
    self.transcription_completed.emit(text)
    
def _on_transcription_error(self, error: str):
    """Handle transcription error."""
    self.transcription_failed.emit(error)
```

**Testing**: Verify UI remains responsive during long operations

---

### 5. Complete WindowManager Plugin Integration
**File**: `src/scribe/plugins/window_manager/plugin.py`  
**Estimate**: 0.5 days  
**Status**: ⏳ Proposed  

**Current Issue**: Plugin exists but not fully integrated with app

**Tasks**:
- ✅ Plugin code complete
- ⏳ Test command registration
- ⏳ Test actual window switching
- ⏳ Handle errors (app not found, etc.)
- ⏳ Add user feedback

---

## ⚠️ High Priority (Quality & Reliability)

### 6. Build Modern Config System
**Files**: `src/scribe/config/`  
**Estimate**: 2-3 days  
**Status**: ⏳ Proposed  

**Current Issue**: Legacy coupling with `sys.path` hacks

**Implementation Plan**:
```python
# config/manager.py
import yaml
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, Field

class ScribeConfig(BaseModel):
    """Main configuration schema."""
    recording_options: RecordingOptions
    model_options: ModelOptions
    plugins: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    analytics: AnalyticsOptions
    
class ConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load()
        
    def _load(self) -> ScribeConfig:
        """Load and validate config."""
        with open(self.config_path) as f:
            data = yaml.safe_load(f)
        return ScribeConfig(**data)
        
    def get_plugin_config(self, plugin_name: str) -> Dict:
        return self.config.plugins.get(plugin_name, {})
```

**Benefits**:
- Remove legacy coupling
- Type validation
- Profile support
- Environment variable override
- Hot reloading

---

### 7. Remove Path Manipulation
**Files**: Multiple  
**Estimate**: 1 day  
**Status**: ⏳ Proposed  

**Current Issue**: `sys.path.insert()` in multiple files

**Fix**: Use proper relative imports or move legacy code into package

---

### 8. Add Comprehensive Error Handling
**Files**: `src/scribe/app.py`, `src/scribe/core/*.py`  
**Estimate**: 1 day  
**Status**: ⏳ Proposed  

**Add try-except blocks around**:
- Config loading
- Model initialization
- Audio capture
- Transcription
- Plugin execution

**With proper user feedback**:
- Error messages in UI
- Fallback behaviors
- Logging for debugging

---

## 📦 Medium Priority (Architecture Improvements)

### 9. Event Bus Pattern
**File**: `src/scribe/core/event_bus.py`  
**Estimate**: 2 days  
**Status**: ⏳ Proposed  

**Benefits**:
- Loose coupling between components
- Plugins can communicate
- Analytics listens to all events
- Easier testing

---

### 10. State Machine for App State
**File**: `src/scribe/core/state_machine.py`  
**Estimate**: 1 day  
**Status**: ⏳ Proposed  

**States**:
- IDLE
- LISTENING
- RECORDING
- TRANSCRIBING
- EXECUTING_COMMAND
- ERROR

**Benefits**:
- Prevent invalid transitions
- Better UI feedback
- Easier debugging

---

### 11. Command Queue with Retry Logic
**File**: `src/scribe/core/command_queue.py`  
**Estimate**: 2 days  
**Status**: ⏳ Proposed  

**Features**:
- Queue commands
- Retry on failure
- Priority system
- Execution history

---

## 🧪 Testing Infrastructure

### 12. Plugin System Unit Tests
**Files**: `tests/test_plugin_*.py`  
**Estimate**: 2 days  
**Status**: ⏳ Proposed  

**Coverage**:
- BasePlugin validation
- PluginRegistry registration
- Command routing
- Lifecycle management

---

### 13. Integration Tests
**Files**: `tests/test_integration_*.py`  
**Estimate**: 2 days  
**Status**: ⏳ Proposed  

**Scenarios**:
- End-to-end transcription flow
- Plugin command execution
- Error handling paths

---

### 14. UI Tests with qtbot
**Files**: `tests/test_ui_*.py`  
**Estimate**: 2 days  
**Status**: ⏳ Proposed  

**Coverage**:
- Window creation
- Button clicks
- Status updates
- Signal/slot connections

---

## 🎨 Polish & Features

### 15. First-Run Setup Wizard
**File**: `src/scribe/ui/setup_wizard.py`  
**Estimate**: 3 days  
**Status**: ⏳ Proposed  

**Steps**:
1. Welcome & introduction
2. Microphone selection & test
3. API key configuration (optional)
4. Privacy settings
5. Profile creation
6. Quick tutorial

---

### 16. Wake Word Detection
**Files**: `src/scribe/core/wake_word.py`  
**Estimate**: 3-4 days  
**Status**: ⏳ Proposed  

**Implementation**:
- Use `pvporcupine` or similar
- Train custom "Hey Scribe"
- Background listening
- Activation flow

---

### 17. MediaControl Plugin
**File**: `src/scribe/plugins/media_control/`  
**Estimate**: 2 days  
**Status**: ⏳ Proposed  

**Commands**:
- play / pause
- next / previous
- volume up / down
- mute / unmute

---

### 18. MemoryScribe Plugin
**File**: `src/scribe/plugins/memory_scribe/`  
**Estimate**: 5 days  
**Status**: ⏳ Proposed  

**Features**:
- Save conversations with context
- Search by content
- Recall with window/URL
- Timeline view

---

## 📋 v2.0 Release Checklist

### Week 1-2: Core Functionality ✅
- [ ] Implement audio recording
- [ ] Fix transcription engine
- [ ] Add background threading
- [ ] Improve pattern matching
- [ ] Complete WindowManager

### Week 3-4: Plugin System
- [ ] Test plugin loading/unloading
- [ ] Build MediaControl plugin
- [ ] Document plugin API
- [ ] Create plugin examples

### Week 5-6: Config & Setup
- [ ] Build modern config system
- [ ] First-run setup wizard
- [ ] Profile management
- [ ] Migration guide

### Week 7-8: Testing & Polish
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Documentation review
- [ ] Beta testing (10 users)

### Week 9-10: Release
- [ ] Fix critical bugs
- [ ] Deployment guide
- [ ] Announcement post
- [ ] Community setup

---

## 📊 Progress Tracking

**Critical Issues Resolved**: 0 / 5  
**High Priority Complete**: 0 / 3  
**Medium Priority Complete**: 0 / 3  
**Tests Written**: 0 / 3  
**Polish Features**: 0 / 4  

**Overall Progress**: 0% (0 / 18 tasks)

---

## 🔄 Update Log

- **2024-11-08**: Initial document created from code review
- **Future**: Track implementation progress here

---

*This document should be updated as tasks are completed. Move completed items to BUILDSTATE.json session_log.*
