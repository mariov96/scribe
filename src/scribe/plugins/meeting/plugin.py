"""
Meeting Note Taker Plugin - Main Implementation
"""

import logging
from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QListWidgetItem, QLabel, QSplitter
)
from qfluentwidgets import (
    PushButton, PrimaryPushButton, TitleLabel, SubtitleLabel, 
    BodyLabel, CardWidget, FluentIcon as FIF,
    InfoBar, InfoBarPosition
)

from .models import Meeting, MeetingStorage
from .recorder import MeetingRecorder

logger = logging.getLogger(__name__)


class MeetingsPage(QWidget):
    """Main meetings page UI"""
    
    def __init__(self, storage: MeetingStorage, recorder: MeetingRecorder):
        super().__init__()
        self.setObjectName("MeetingsPage")  # Required for QFluentWidgets navigation
        self.storage = storage
        self.recorder = recorder
        self.current_meeting = None
        
        self._setup_ui()
        self._load_meetings()
        
        # Connect recorder signals
        self.recorder.recording_started.connect(self._on_recording_started)
        self.recorder.recording_stopped.connect(self._on_recording_stopped)
    
    def _setup_ui(self):
        """Create the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        title = TitleLabel("🎙️ Meeting Recorder")
        header.addWidget(title)
        header.addStretch()
        
        # Recording controls
        self.start_btn = PrimaryPushButton(FIF.MICROPHONE, "Start Meeting Recording")
        self.start_btn.setFixedWidth(220)
        self.start_btn.clicked.connect(self._start_recording)
        
        self.stop_btn = PushButton(FIF.PAUSE, "Stop Recording")
        self.stop_btn.setFixedWidth(160)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_recording)
        
        header.addWidget(self.start_btn)
        header.addWidget(self.stop_btn)
        
        layout.addLayout(header)
        
        # Status label
        self.status_label = BodyLabel("Ready to record")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Main content - split view
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Meeting list
        list_container = CardWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(12, 12, 12, 12)
        
        list_header = SubtitleLabel("Recent Meetings")
        list_layout.addWidget(list_header)
        
        self.meeting_list = QListWidget()
        self.meeting_list.itemClicked.connect(self._on_meeting_selected)
        list_layout.addWidget(self.meeting_list)
        
        splitter.addWidget(list_container)
        
        # Right: Meeting details
        self.detail_panel = self._create_detail_panel()
        splitter.addWidget(self.detail_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter, 1)
    
    def _create_detail_panel(self):
        """Create meeting detail panel"""
        panel = CardWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        self.detail_title = SubtitleLabel("Select a meeting")
        layout.addWidget(self.detail_title)
        
        self.detail_info = BodyLabel("No meeting selected")
        self.detail_info.setWordWrap(True)
        layout.addWidget(self.detail_info)
        
        # Transcribe button
        self.transcribe_btn = PrimaryPushButton(FIF.CHAT, "Transcribe Meeting")
        self.transcribe_btn.setEnabled(False)
        self.transcribe_btn.clicked.connect(self._transcribe_meeting)
        layout.addWidget(self.transcribe_btn)
        
        # Transcript display
        self.transcript_label = BodyLabel("Transcript:")
        self.transcript_label.setVisible(False)
        layout.addWidget(self.transcript_label)
        
        self.transcript_text = BodyLabel("")
        self.transcript_text.setWordWrap(True)
        self.transcript_text.setVisible(False)
        layout.addWidget(self.transcript_text)
        
        layout.addStretch()
        
        return panel
    
    def _load_meetings(self):
        """Load and display all meetings"""
        self.meeting_list.clear()
        meetings = self.storage.load_all_meetings()
        
        for meeting in meetings:
            item_text = f"{meeting.title}\n{meeting.date.strftime('%Y-%m-%d %H:%M')} • {meeting.duration:.1f}s"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, meeting)
            self.meeting_list.addItem(item)
        
        logger.info(f"Loaded {len(meetings)} meetings")
    
    def _start_recording(self):
        """Start recording a new meeting"""
        try:
            # Create new meeting
            self.current_meeting = Meeting.create_new(
                title=f"Meeting {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            # Get audio file path
            meeting_dir = self.storage.get_meeting_dir(self.current_meeting.id)
            meeting_dir.mkdir(parents=True, exist_ok=True)
            audio_file = meeting_dir / "audio.wav"
            
            self.current_meeting.audio_file = str(audio_file)
            
            # Start recording
            self.recorder.start_recording(str(audio_file))
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}", exc_info=True)
            InfoBar.error(
                title="Recording Error",
                content=f"Failed to start: {e}",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP
            )
    
    def _stop_recording(self):
        """Stop current recording"""
        try:
            duration = self.recorder.stop_recording()
            
            if self.current_meeting:
                self.current_meeting.duration = duration
                self.current_meeting.status = "recorded"
                
                # Save meeting
                self.storage.save_meeting(self.current_meeting)
                
                logger.info(f"Meeting saved: {self.current_meeting.id} ({duration:.1f}s)")
                
                # Refresh list
                self._load_meetings()
                
                InfoBar.success(
                    title="Recording Saved",
                    content=f"Meeting recorded: {duration:.1f} seconds",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.TOP
                )
                
                self.current_meeting = None
                
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}", exc_info=True)
            InfoBar.error(
                title="Save Error",
                content=f"Failed to save: {e}",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP
            )
    
    def _on_recording_started(self):
        """Handle recording started"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("🔴 Recording in progress...")
        self.status_label.setStyleSheet("color: #F44336; font-size: 11px; font-weight: bold;")
    
    def _on_recording_stopped(self):
        """Handle recording stopped"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Ready to record")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
    
    def _on_meeting_selected(self, item: QListWidgetItem):
        """Handle meeting selection"""
        meeting = item.data(Qt.UserRole)
        
        self.detail_title.setText(meeting.title)
        self.detail_info.setText(
            f"Date: {meeting.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Duration: {meeting.duration:.1f} seconds\n"
            f"Status: {meeting.status}\n"
            f"Audio: {Path(meeting.audio_file).name if meeting.audio_file else 'N/A'}"
        )
        
        # Show transcript if available
        if meeting.transcript:
            self.transcript_label.setVisible(True)
            self.transcript_text.setText(meeting.transcript)
            self.transcript_text.setVisible(True)
            self.transcribe_btn.setEnabled(False)
        else:
            self.transcript_label.setVisible(False)
            self.transcript_text.setVisible(False)
            self.transcribe_btn.setEnabled(True)
        
        self.selected_meeting = meeting
    
    def _transcribe_meeting(self):
        """Transcribe the selected meeting"""
        if not hasattr(self, 'selected_meeting'):
            return
        
        meeting = self.selected_meeting
        
        InfoBar.info(
            title="Transcribing",
            content="Transcription feature coming in next iteration...",
            parent=self,
            duration=2000,
            position=InfoBarPosition.TOP
        )
        
        # TODO: Implement transcription using existing Whisper engine


class MeetingNoteTakerPlugin:
    """Meeting Note Taker Plugin - Main Class"""
    
    def __init__(self, app):
        self.app = app
        
        # Setup storage
        meetings_dir = Path.home() / ".scribe" / "meetings"
        self.storage = MeetingStorage(meetings_dir)
        
        # Setup recorder
        self.recorder = MeetingRecorder()
        
        # Create page
        self.meetings_page = MeetingsPage(self.storage, self.recorder)
        
        logger.info("✅ Meeting Note Taker plugin initialized")
    
    def get_page(self):
        """Get the meetings page widget"""
        return self.meetings_page
