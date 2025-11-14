"""
Meeting data model
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Meeting:
    """Represents a single meeting recording"""
    
    id: str
    title: str
    date: datetime
    duration: float  # seconds
    audio_file: str
    transcript: str = ""
    status: str = "recorded"  # recorded, transcribing, complete
    
    @classmethod
    def create_new(cls, title: str = "Untitled Meeting") -> 'Meeting':
        """Create a new meeting"""
        meeting_id = str(uuid.uuid4())[:8]
        return cls(
            id=meeting_id,
            title=title,
            date=datetime.now(),
            duration=0.0,
            audio_file="",
            transcript="",
            status="recording"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['date'] = self.date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Meeting':
        """Load from dictionary"""
        data['date'] = datetime.fromisoformat(data['date'])
        return cls(**data)
    
    def save(self, meetings_dir: Path):
        """Save meeting metadata to JSON"""
        meeting_dir = meetings_dir / self.id
        meeting_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_file = meeting_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, meeting_dir: Path) -> 'Meeting':
        """Load meeting from directory"""
        metadata_file = meeting_dir / "metadata.json"
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


class MeetingStorage:
    """Manages meeting storage and retrieval"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save_meeting(self, meeting: Meeting):
        """Save a meeting"""
        meeting.save(self.base_dir)
    
    def load_all_meetings(self) -> list[Meeting]:
        """Load all meetings"""
        meetings = []
        for meeting_dir in sorted(self.base_dir.iterdir(), reverse=True):
            if meeting_dir.is_dir():
                try:
                    meeting = Meeting.load(meeting_dir)
                    meetings.append(meeting)
                except Exception as e:
                    print(f"Error loading meeting {meeting_dir.name}: {e}")
        return meetings
    
    def get_meeting_dir(self, meeting_id: str) -> Path:
        """Get directory path for a meeting"""
        return self.base_dir / meeting_id
