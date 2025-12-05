"""
Pydantic models for Scribe configuration.

These models provide type safety, validation, and clear documentation
for all configuration options.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class AudioConfig(BaseModel):
    """Audio recording configuration."""
    
    model_config = {"validate_assignment": True}
    
    device_id: Optional[int] = Field(
        default=None,
        description="Audio input device ID. None = use default device"
    )
    sample_rate: int = Field(
        default=16000,
        ge=8000,
        le=48000,
        description="Sample rate in Hz (16000 optimal for Whisper)"
    )
    channels: int = Field(
        default=1,
        ge=1,
        le=2,
        description="Number of audio channels (1=mono, 2=stereo)"
    )
    silence_duration: int = Field(
        default=1200,
        ge=100,
        le=5000,
        description="Silence duration in ms before stopping recording"
    )
    min_duration: int = Field(
        default=800,
        ge=100,
        le=2000,
        description="Minimum recording duration in ms"
    )
    noise_suppression: bool = Field(
        default=True,
        description="Apply basic noise gating before transcription"
    )
    vad_aggressiveness: int = Field(
        default=2,
        ge=0,
        le=3,
        description="Voice activity detection aggressiveness (0-3, higher = more strict)"
    )
    noise_gate_db: int = Field(
        default=-40,
        ge=-80,
        le=-10,
        description="Noise gate threshold in dBFS (samples below are attenuated)"
    )
    level_normalization: bool = Field(
        default=False,
        description="Normalize audio level to a target RMS before transcription"
    )
    target_level_dbfs: int = Field(
        default=-20,
        ge=-30,
        le=-12,
        description="Target RMS level in dBFS for normalization"
    )


class HotkeyConfig(BaseModel):
    """Hotkey configuration."""
    
    model_config = {"validate_assignment": True}
    
    activation_key: str = Field(
        default="ctrl+alt",
        description="Keyboard shortcut to start/stop recording (e.g., 'ctrl+alt', 'ctrl+shift')"
    )
    recording_mode: Literal["continuous", "voice_activity_detection", "press_to_toggle", "hold_to_record"] = Field(
        default="voice_activity_detection",
        description="Recording behavior mode"
    )
    
    @field_validator('activation_key')
    @classmethod
    def validate_hotkey(cls, v: str) -> str:
        """Validate hotkey format."""
        valid_keys = {'ctrl', 'alt', 'shift', 'meta', 'cmd', 'win', 'super'}
        keys = {k.strip().lower() for k in v.split('+')}
        
        if not keys or len(keys) < 1:
            raise ValueError("Hotkey must contain at least one modifier key")
        
        # At least one key should be a valid modifier
        if not keys.intersection(valid_keys):
            raise ValueError(f"Hotkey must contain at least one of: {', '.join(valid_keys)}")
        
        return '+'.join(sorted(keys))


class WhisperConfig(BaseModel):
    """Whisper transcription model configuration."""
    
    use_api: bool = Field(
        default=False,
        description="Use OpenAI API instead of local model"
    )
    model: Literal[
        "tiny", "tiny.en", "base", "base.en", "small", "small.en", 
        "medium", "medium.en", "large", "large-v1", "large-v2", "large-v3",
        "distil-medium.en", "distil-large-v3"
    ] = Field(
        default="base",
        description="Whisper model size (larger = more accurate, slower). Distil models are 6x faster."
    )
    language: Optional[str] = Field(
        default=None,
        description="ISO-639-1 language code (e.g., 'en', 'es'). None = auto-detect"
    )
    device: Literal["auto", "cpu", "cuda"] = Field(
        default="auto",
        description="Compute device for local model"
    )
    compute_type: Literal["auto", "default", "float32", "float16", "int8"] = Field(
        default="auto",
        description="Compute precision (auto = GPU:float16, CPU:int8; int8 = faster, less accurate)"
    )
    temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Sampling temperature (0 = deterministic)"
    )
    
    # API settings (only used when use_api=True)
    api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    api_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="API base URL"
    )


class AIFormattingConfig(BaseModel):
    """AI text enhancement configuration."""
    
    enable_ai_cleanup: bool = Field(
        default=True,
        description="Remove filler words and enhance clarity"
    )
    enable_voice_commands: bool = Field(
        default=True,
        description="Support voice formatting commands (bullet point, new paragraph, etc.)"
    )
    enable_smart_punctuation: bool = Field(
        default=True,
        description="Auto-detect questions vs statements"
    )
    enable_number_conversion: bool = Field(
        default=True,
        description="Convert spoken numbers to digits"
    )
    phantom_recording_protection: bool = Field(
        default=True,
        description="Prevent accidental empty recordings"
    )


class PostProcessingConfig(BaseModel):
    """Text post-processing configuration."""
    
    add_trailing_space: bool = Field(
        default=True,
        description="Add space after transcribed text"
    )
    remove_trailing_period: bool = Field(
        default=False,
        description="Remove period at end of transcription"
    )
    remove_capitalization: bool = Field(
        default=False,
        description="Convert to lowercase"
    )
    writing_key_press_delay: float = Field(
        default=0.002,
        ge=0.0,
        le=0.1,
        description="Delay between keystrokes when typing out text (seconds)"
    )
    auto_insert_mode: str = Field(
        default="paste",
        description="How transcriptions are injected into the originating app (paste|type|both)",
        pattern="^(paste|type|both)$"
    )


class PluginConfig(BaseModel):
    """Plugin system configuration."""
    
    enabled_plugins: list[str] = Field(
        default_factory=lambda: ["window_manager"],
        description="List of enabled plugin names"
    )
    plugin_config: dict[str, dict] = Field(
        default_factory=dict,
        description="Plugin-specific configuration"
    )


class UIConfig(BaseModel):
    """User interface configuration."""
    
    theme: Literal["light", "dark", "auto"] = Field(
        default="auto",
        description="UI theme"
    )
    show_system_tray: bool = Field(
        default=True,
        description="Show icon in system tray"
    )
    minimize_to_tray: bool = Field(
        default=False,
        description="Minimize to tray instead of taskbar"
    )
    start_minimized: bool = Field(
        default=False,
        description="Start application minimized"
    )


class AppConfig(BaseModel):
    """Complete application configuration."""
    
    version: str = Field(
        default="2.0.0",
        description="Config file format version"
    )
    profile_name: str = Field(
        default="default",
        description="Active profile name"
    )
    
    # Sub-configurations
    audio: AudioConfig = Field(default_factory=AudioConfig)
    hotkey: HotkeyConfig = Field(default_factory=HotkeyConfig)
    whisper: WhisperConfig = Field(default_factory=WhisperConfig)
    ai_formatting: AIFormattingConfig = Field(default_factory=AIFormattingConfig)
    post_processing: PostProcessingConfig = Field(default_factory=PostProcessingConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True  # Validate on field assignment
        extra = "forbid"  # Raise error on unknown fields
