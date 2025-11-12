"""
QThread worker for background transcription.

Prevents UI freezing during 2-3 second transcription operations.
"""

import logging
from typing import Optional
from PyQt5.QtCore import QThread, pyqtSignal as Signal

from scribe.core.transcription_engine import TranscriptionEngine, TranscriptionResult

logger = logging.getLogger(__name__)


class TranscriptionWorker(QThread):
    """
    Background worker for transcription operations.
    
    Runs transcription in separate thread to keep UI responsive.
    Emits signals when complete or on error.
    """
    
    # Signals
    transcription_complete = Signal(TranscriptionResult)  # Result with text, duration, confidence
    transcription_failed = Signal(str)  # Error message
    progress_update = Signal(str)  # Status update (optional, for future use)
    
    def __init__(self, transcription_engine: TranscriptionEngine, audio_data: bytes):
        """
        Initialize worker.
        
        Args:
            transcription_engine: Engine to use for transcription
            audio_data: Audio bytes to transcribe
        """
        super().__init__()
        self.transcription_engine = transcription_engine
        self.audio_data = audio_data
        self._is_cancelled = False
    
    def run(self):
        """
        Execute transcription in background thread.
        
        This runs in a separate thread - do NOT touch UI here!
        Use signals to communicate with main thread.
        """
        try:
            logger.debug("TranscriptionWorker: Starting transcription...")
            
            if self._is_cancelled:
                logger.debug("TranscriptionWorker: Cancelled before starting")
                return
            
            # Perform transcription (this takes 2-3 seconds)
            result = self.transcription_engine.transcribe(self.audio_data)
            
            if self._is_cancelled:
                logger.debug("TranscriptionWorker: Cancelled after transcription")
                return
            
            if result and result.text:
                logger.debug(f"TranscriptionWorker: Success - '{result.text[:50]}...'")
                self.transcription_complete.emit(result)
            else:
                logger.warning("TranscriptionWorker: No speech detected")
                self.transcription_failed.emit("No speech detected")
                
        except Exception as e:
            logger.error(f"TranscriptionWorker: Error - {e}", exc_info=True)
            self.transcription_failed.emit(str(e))
    
    def cancel(self):
        """Cancel the transcription operation."""
        self._is_cancelled = True
        logger.debug("TranscriptionWorker: Cancellation requested")
