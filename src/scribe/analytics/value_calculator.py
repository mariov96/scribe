"""
Value Calculator - Quantify the tangible value Scribe provides to users.

This module calculates measurable metrics that prove Scribe's worth:
- Time saved vs typing
- Accuracy improvements
- Productivity gains
- Command efficiency

Philosophy: Every feature should prove its value with data.
Users deserve to see exactly how Scribe helps them.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


logger = logging.getLogger(__name__)


@dataclass
class TranscriptionMetrics:
    """Metrics for a single transcription event."""
    timestamp: datetime
    audio_duration: float  # seconds
    word_count: int
    character_count: int
    transcription_time: float  # seconds
    ai_enhancement_time: float = 0.0  # seconds
    corrections_made: int = 0
    was_command: bool = False  # Was this a voice command vs dictation
    confidence: Optional[float] = None
    language: Optional[str] = None
    application: Optional[str] = None
    window_title: Optional[str] = None
    window_handle: Optional[int] = None
    text: str = ""


@dataclass
class CommandMetrics:
    """Metrics for voice command usage."""
    timestamp: datetime
    command_pattern: str
    plugin: str
    execution_time: float  # seconds
    success: bool
    error_message: Optional[str] = None


@dataclass
class SessionSummary:
    """Summary of value metrics for a session or time period."""
    start_time: datetime
    end_time: datetime

    # Transcription stats
    total_transcriptions: int = 0
    total_words: int = 0
    total_characters: int = 0
    total_audio_duration: float = 0.0  # seconds

    # Time metrics
    total_transcription_time: float = 0.0
    total_ai_enhancement_time: float = 0.0

    # Command stats
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0

    # Calculated value
    time_saved_vs_typing: float = 0.0  # seconds
    productivity_multiplier: float = 1.0
    accuracy_score: float = 0.0
    average_confidence: float = 0.0

    # Feature effectiveness
    feature_usage: Dict[str, int] = field(default_factory=dict)


class ValueCalculator:
    """
    Calculate and track the tangible value Scribe provides to users.

    This class is the foundation of Scribe's analytics-first design.
    It quantifies benefits so users can see exactly how Scribe helps them.

    Example:
        calculator = ValueCalculator()

        # Track transcription
        calculator.record_transcription(
            audio_duration=5.0,
            word_count=45,
            transcription_time=1.2
        )

        # Get value summary
        summary = calculator.get_session_summary()
        print(f"Time saved today: {summary.time_saved_vs_typing / 60:.1f} minutes")
    """

    # Constants for value calculations
    AVERAGE_TYPING_SPEED = 40  # words per minute (WPM) - conservative estimate
    AVERAGE_SPEAKING_SPEED = 150  # words per minute
    COMMAND_VALUE_MULTIPLIER = 3.0  # Commands save 3x more time than typing

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize value calculator.

        Args:
            data_dir: Directory to store analytics data (default: data/analytics)
        """
        self.data_dir = data_dir or Path("data/analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory tracking
        self._transcriptions: List[TranscriptionMetrics] = []
        self._commands: List[CommandMetrics] = []
        self._session_start = datetime.now()

        logger.info(f"ValueCalculator initialized. Data dir: {self.data_dir}")

    # ==================== Recording Methods ====================

    def record_transcription(
        self,
        audio_duration: float,
        word_count: int,
        transcription_time: float,
        ai_enhancement_time: float = 0.0,
        corrections_made: int = 0,
        was_command: bool = False,
        *,
        confidence: Optional[float] = None,
        language: Optional[str] = None,
        application: Optional[str] = None,
        window_title: Optional[str] = None,
        window_handle: Optional[int] = None,
        text: str = "",
        character_count: Optional[int] = None,
    ):
        """
        Record metrics for a transcription event.

        Args:
            audio_duration: Length of audio in seconds
            word_count: Number of words transcribed
            transcription_time: Time taken to transcribe
            ai_enhancement_time: Time spent on AI enhancement
            corrections_made: Number of corrections applied
            was_command: Whether this was a voice command
        """
        metrics = TranscriptionMetrics(
            timestamp=datetime.now(),
            audio_duration=audio_duration,
            word_count=word_count,
            character_count=character_count or word_count * 5,
            transcription_time=transcription_time,
            ai_enhancement_time=ai_enhancement_time,
            corrections_made=corrections_made,
            was_command=was_command,
            confidence=confidence,
            language=language,
            application=application,
            window_title=window_title,
            window_handle=window_handle,
            text=text,
        )

        self._transcriptions.append(metrics)
        logger.debug(f"Recorded transcription: {word_count} words in {transcription_time:.2f}s")
        return metrics

    def record_command(
        self,
        command_pattern: str,
        plugin: str,
        execution_time: float,
        success: bool,
        error_message: Optional[str] = None
    ):
        """
        Record metrics for a voice command execution.

        Args:
            command_pattern: The command pattern executed
            plugin: Plugin that handled the command
            execution_time: Time taken to execute
            success: Whether command succeeded
            error_message: Error message if failed
        """
        metrics = CommandMetrics(
            timestamp=datetime.now(),
            command_pattern=command_pattern,
            plugin=plugin,
            execution_time=execution_time,
            success=success,
            error_message=error_message
        )

        self._commands.append(metrics)
        logger.debug(f"Recorded command: {command_pattern} ({plugin}) - {'✅' if success else '❌'})")

    # ==================== Value Calculation Methods ====================

    def calculate_time_saved(
        self,
        word_count: int,
        audio_duration: float,
        was_command: bool = False
    ) -> float:
        """
        Calculate time saved vs typing.

        Args:
            word_count: Number of words
            audio_duration: Time spent speaking
            was_command: Whether this was a command (saves more time)

        Returns:
            Time saved in seconds
        """
        # Time it would take to type these words
        typing_time = (word_count / self.AVERAGE_TYPING_SPEED) * 60

        # Time it actually took to speak
        speaking_time = audio_duration

        # Base time saved
        time_saved = typing_time - speaking_time

        # Commands save additional time (no need to navigate UI)
        if was_command:
            time_saved *= self.COMMAND_VALUE_MULTIPLIER

        return max(0, time_saved)  # Never negative

    def calculate_productivity_multiplier(self, summary: SessionSummary) -> float:
        """
        Calculate productivity multiplier for a session.

        This shows how much faster the user was with Scribe vs typing.

        Args:
            summary: Session summary with metrics

        Returns:
            Multiplier (e.g., 2.5 means 2.5x faster than typing)
        """
        if summary.total_words == 0:
            return 1.0

        # Time it would have taken to type everything
        typing_time = (summary.total_words / self.AVERAGE_TYPING_SPEED) * 60

        # Time actually spent (audio + processing)
        actual_time = summary.total_audio_duration + summary.total_transcription_time

        if actual_time == 0:
            return 1.0

        multiplier = typing_time / actual_time
        return round(multiplier, 2)

    def calculate_accuracy_score(self, transcriptions: List[TranscriptionMetrics]) -> float:
        """
        Calculate accuracy score based on corrections made.

        Args:
            transcriptions: List of transcription metrics

        Returns:
            Accuracy score from 0.0 to 1.0
        """
        if not transcriptions:
            return 1.0

        total_words = sum(t.word_count for t in transcriptions)
        total_corrections = sum(t.corrections_made for t in transcriptions)

        if total_words == 0:
            return 1.0

        # Accuracy = 1 - (corrections / words)
        accuracy = 1.0 - (total_corrections / total_words)
        return max(0.0, min(1.0, accuracy))  # Clamp to [0, 1]

    # ==================== Summary Methods ====================

    def get_session_summary(self, since: Optional[datetime] = None) -> SessionSummary:
        """
        Get summary of value metrics for current session or time period.

        Args:
            since: Start time for summary (default: session start)

        Returns:
            SessionSummary with calculated metrics
        """
        start_time = since or self._session_start
        end_time = datetime.now()

        # Filter metrics by time range
        transcriptions = [t for t in self._transcriptions if t.timestamp >= start_time]
        commands = [c for c in self._commands if c.timestamp >= start_time]

        # Calculate totals
        total_words = sum(t.word_count for t in transcriptions)
        total_chars = sum(t.character_count for t in transcriptions)
        total_audio = sum(t.audio_duration for t in transcriptions)
        total_transcription_time = sum(t.transcription_time for t in transcriptions)
        total_ai_time = sum(t.ai_enhancement_time for t in transcriptions)

        # Command stats
        successful_cmds = sum(1 for c in commands if c.success)
        failed_cmds = sum(1 for c in commands if not c.success)

        # Calculate time saved
        time_saved = sum(
            self.calculate_time_saved(t.word_count, t.audio_duration, t.was_command)
            for t in transcriptions
        )

        # Create summary
        avg_confidence = 0.0
        conf_values = [t.confidence for t in transcriptions if t.confidence is not None]
        if conf_values:
            avg_confidence = sum(conf_values) / len(conf_values)

        summary = SessionSummary(
            start_time=start_time,
            end_time=end_time,
            total_transcriptions=len(transcriptions),
            total_words=total_words,
            total_characters=total_chars,
            total_audio_duration=total_audio,
            total_transcription_time=total_transcription_time,
            total_ai_enhancement_time=total_ai_time,
            total_commands=len(commands),
            successful_commands=successful_cmds,
            failed_commands=failed_cmds,
            time_saved_vs_typing=time_saved,
            accuracy_score=self.calculate_accuracy_score(transcriptions),
            average_confidence=avg_confidence,
        )

        # Calculate productivity multiplier
        summary.productivity_multiplier = self.calculate_productivity_multiplier(summary)

        # Track feature usage
        summary.feature_usage = self._calculate_feature_usage(commands)

        return summary

    def _calculate_feature_usage(self, commands: List[CommandMetrics]) -> Dict[str, int]:
        """Calculate how often each feature/plugin is used."""
        usage: Dict[str, int] = {}
        for cmd in commands:
            usage[cmd.plugin] = usage.get(cmd.plugin, 0) + 1
        return usage

    def get_recent_transcriptions(self, limit: int = 10) -> List[TranscriptionMetrics]:
        """Return the most recent transcription metrics."""
        if limit <= 0:
            return []
        return self._transcriptions[-limit:]

    # ==================== Persistence Methods ====================

    def save_session(self, filename: Optional[str] = None):
        """
        Save session metrics to JSON file.

        Args:
            filename: Custom filename (default: session_TIMESTAMP.json)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"session_{timestamp}.json"

        filepath = self.data_dir / filename

        summary = self.get_session_summary()
        data = {
            "session": {
                "start": summary.start_time.isoformat(),
                "end": summary.end_time.isoformat(),
                "duration_minutes": (summary.end_time - summary.start_time).total_seconds() / 60
            },
            "transcription": {
                "total_count": summary.total_transcriptions,
                "total_words": summary.total_words,
                "total_characters": summary.total_characters,
                "audio_duration_seconds": summary.total_audio_duration,
                "processing_time_seconds": summary.total_transcription_time,
                "ai_enhancement_time_seconds": summary.total_ai_enhancement_time
            },
            "commands": {
                "total_count": summary.total_commands,
                "successful": summary.successful_commands,
                "failed": summary.failed_commands,
                "success_rate": summary.successful_commands / summary.total_commands if summary.total_commands > 0 else 0
            },
            "value": {
                "time_saved_seconds": summary.time_saved_vs_typing,
                "time_saved_minutes": summary.time_saved_vs_typing / 60,
                "productivity_multiplier": summary.productivity_multiplier,
                "accuracy_score": summary.accuracy_score
            },
            "feature_usage": summary.feature_usage
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Session saved: {filepath}")
        return filepath

    def load_session(self, filepath: Path) -> Dict[str, Any]:
        """
        Load session metrics from JSON file.

        Args:
            filepath: Path to session file

        Returns:
            Session data dictionary
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Session loaded: {filepath}")
        return data

    def get_lifetime_stats(self) -> Dict[str, Any]:
        """
        Calculate lifetime statistics from all saved sessions.

        Returns:
            Aggregated lifetime statistics
        """
        session_files = list(self.data_dir.glob("session_*.json"))

        if not session_files:
            logger.warning("No session files found")
            return {}

        # Aggregate stats
        total_words = 0
        total_time_saved = 0.0
        total_commands = 0
        total_transcriptions = 0

        for session_file in session_files:
            data = self.load_session(session_file)

            total_transcriptions += data.get("transcription", {}).get("total_count", 0)
            total_words += data.get("transcription", {}).get("total_words", 0)
            total_time_saved += data.get("value", {}).get("time_saved_seconds", 0)
            total_commands += data.get("commands", {}).get("total_count", 0)

        return {
            "total_sessions": len(session_files),
            "total_transcriptions": total_transcriptions,
            "total_words": total_words,
            "total_commands": total_commands,
            "total_time_saved_seconds": total_time_saved,
            "total_time_saved_hours": total_time_saved / 3600,
            "average_time_saved_per_session": total_time_saved / len(session_files) if session_files else 0
        }

    # ==================== Display Methods ====================

    def print_summary(self, summary: Optional[SessionSummary] = None):
        """
        Print formatted summary to console.

        Args:
            summary: Summary to print (default: current session)
        """
        if summary is None:
            summary = self.get_session_summary()

        print("\n" + "="*60)
        print("📊 SCRIBE VALUE SUMMARY")
        print("="*60)

        # Time range
        duration = summary.end_time - summary.start_time
        print(f"\n⏱️  Session Duration: {duration.total_seconds() / 60:.1f} minutes")

        # Transcription stats
        print(f"\n📝 Transcriptions:")
        print(f"   • Total: {summary.total_transcriptions}")
        print(f"   • Words: {summary.total_words:,}")
        print(f"   • Characters: {summary.total_characters:,}")

        # Voice commands
        if summary.total_commands > 0:
            success_rate = (summary.successful_commands / summary.total_commands) * 100
            print(f"\n🎤 Voice Commands:")
            print(f"   • Total: {summary.total_commands}")
            print(f"   • Success Rate: {success_rate:.1f}%")

        # Value metrics
        print(f"\n💎 Your Value:")
        print(f"   • Time Saved: {summary.time_saved_vs_typing / 60:.1f} minutes")
        print(f"   • Productivity: {summary.productivity_multiplier:.1f}x faster than typing")
        print(f"   • Accuracy: {summary.accuracy_score * 100:.1f}%")

        # Feature usage
        if summary.feature_usage:
            print(f"\n🔧 Feature Usage:")
            for feature, count in sorted(summary.feature_usage.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {feature}: {count} uses")

        print("\n" + "="*60 + "\n")

    def __repr__(self) -> str:
        return f"<ValueCalculator transcriptions={len(self._transcriptions)} commands={len(self._commands)}>"
