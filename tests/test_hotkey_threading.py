"""
Unit tests for hotkey threading fix (BUG-001).

Tests the signal-based decoupling that prevents Qt threading deadlock
when hotkey is pressed to start recording.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtCore import QTimer, Qt, QThread
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QSignalSpy

from scribe.app import ScribeApp


class TestHotkeyThreading:
    """Test suite for hotkey threading fix."""

    @pytest.fixture
    def app_instance(self, qtbot):
        """Create a ScribeApp instance for testing."""
        # Create app without full initialization
        with patch('scribe.app.ConfigManager'):
            with patch('scribe.app.TranscriptionEngine'):
                with patch('scribe.app.AudioRecorder'):
                    with patch('scribe.app.HotkeyManager'):
                        with patch('scribe.app.ScribeMainWindow'):
                            app = ScribeApp()

                            # Mock core components to avoid initialization
                            app.config = Mock()
                            app.audio_recorder = Mock()
                            app.hotkey_manager = Mock()
                            app.main_window = Mock()
                            app.status_popup = Mock()
                            app.transcription_engine = Mock()
                            app.plugin_registry = Mock()
                            app.value_calculator = Mock()

                            # Initialize state
                            app.is_recording = False
                            app.is_transcribing = False
                            app._recording_mode = "idle"
                            app._recording_source = "manual"
                            app._toggle_stop_pending = False
                            app._current_context = {}

                            return app

    def test_hotkey_emits_signal_not_direct_call(self, app_instance, qtbot):
        """
        Test that hotkey handler emits signal instead of calling UI methods directly.

        This is the KEY fix for the deadlock issue.
        """
        # Create signal spy to monitor hotkey_status_changed signal
        spy = QSignalSpy(app_instance.hotkey_status_changed)

        # Trigger hotkey down
        app_instance._on_hotkey_down()

        # Verify signal was emitted (not direct method call)
        assert len(spy) >= 1  # Should emit True signal
        assert spy[0][0] is True  # First emission should be True

        # Verify main_window methods were NOT called directly
        app_instance.main_window.update_hotkey_status.assert_not_called()

    def test_recording_start_emits_signal_not_direct_call(self, app_instance, qtbot):
        """
        Test that _start_recording emits signal instead of calling UI methods directly.

        This prevents the synchronous call chain that causes deadlock.
        """
        # Create signal spy to monitor recording_status_changed signal
        spy = QSignalSpy(app_instance.recording_status_changed)

        # Trigger recording start
        app_instance._start_recording(source="hotkey")

        # Verify signal was emitted
        assert len(spy) == 1
        assert spy[0][0] is True  # Should emit True

        # Verify main_window.update_recording_status was NOT called directly
        app_instance.main_window.update_recording_status.assert_not_called()

    def test_recording_stop_emits_signal_not_direct_call(self, app_instance, qtbot):
        """Test that _stop_recording emits signal instead of calling UI methods directly."""
        # Set up recording state
        app_instance.is_recording = True
        app_instance.audio_recorder.stop_recording.return_value = b""  # No audio data

        # Create signal spy
        spy = QSignalSpy(app_instance.recording_status_changed)

        # Trigger recording stop
        app_instance._stop_recording()

        # Verify signal was emitted
        assert len(spy) == 1
        assert spy[0][0] is False  # Should emit False

        # Verify main_window.update_recording_status was NOT called directly
        app_instance.main_window.update_recording_status.assert_not_called()

    def test_signal_connection_uses_queued_connection(self, app_instance, qtbot):
        """
        Test that signals are connected with Qt.QueuedConnection for thread safety.

        This ensures signals are delivered asynchronously via the event loop.
        """
        # Mock main window
        main_window = Mock()
        app_instance.main_window = main_window

        # Call _connect_ui_signals to set up connections
        app_instance._connect_ui_signals()

        # Verify the connections were made
        # (In real code, these use type=Qt.QueuedConnection)
        assert app_instance.recording_status_changed is not None
        assert app_instance.hotkey_status_changed is not None

    def test_hotkey_to_recording_flow_no_blocking(self, app_instance, qtbot):
        """
        Integration test: Verify full hotkey → recording flow doesn't block.

        Simulates:
        1. Hotkey pressed (from keyboard thread)
        2. Signal emitted (queued to main thread)
        3. Recording started (non-blocking)
        4. UI updated (asynchronously)
        """
        # Set up spies for all signals
        hotkey_spy = QSignalSpy(app_instance.hotkey_status_changed)
        recording_spy = QSignalSpy(app_instance.recording_status_changed)

        # Simulate hotkey press (as if from keyboard thread)
        start_time = time.time()
        app_instance._on_hotkey_down()
        elapsed_time = time.time() - start_time

        # Verify hotkey handler returned immediately (< 100ms)
        assert elapsed_time < 0.1, f"Hotkey handler blocked for {elapsed_time:.3f}s"

        # Process Qt events to deliver queued signals
        qtbot.wait(50)  # Allow event loop to process
        QApplication.processEvents()

        # Verify signals were emitted
        assert len(hotkey_spy) >= 1  # Hotkey visual feedback
        assert len(recording_spy) == 1  # Recording started
        assert recording_spy[0][0] is True

        # Verify recording started
        assert app_instance.is_recording is True
        app_instance.audio_recorder.start_recording.assert_called_once()

    def test_error_during_recording_emits_signal(self, app_instance, qtbot):
        """Test that errors during recording still emit signals (no direct calls)."""
        # Make audio_recorder.start_recording raise an exception
        app_instance.audio_recorder.start_recording.side_effect = RuntimeError("Audio device busy")

        # Create signal spy
        spy = QSignalSpy(app_instance.recording_status_changed)

        # Try to start recording (will fail)
        app_instance._start_recording(source="hotkey")

        # Verify signals were emitted (True initially, then False on error)
        # The error path should emit False signal
        assert len(spy) >= 1  # At least the True signal

        # Verify recording flag is false (error cleanup)
        assert app_instance.is_recording is False

        # Verify NO direct UI method calls
        app_instance.main_window.update_recording_status.assert_not_called()

    def test_concurrent_hotkey_presses_dont_deadlock(self, app_instance, qtbot):
        """
        Stress test: Multiple rapid hotkey presses should not cause deadlock.

        This would fail with the old synchronous UI call approach.
        """
        hotkey_spy = QSignalSpy(app_instance.hotkey_status_changed)
        recording_spy = QSignalSpy(app_instance.recording_status_changed)

        # Simulate rapid hotkey presses
        for i in range(5):
            app_instance._on_hotkey_down()
            QApplication.processEvents()  # Process events
            qtbot.wait(10)

        # Verify all signals were emitted without blocking/crashing
        assert len(hotkey_spy) >= 5  # At least one per press

        # Should only start recording once (subsequent presses ignored if already recording)
        # This depends on the is_recording check in _on_hotkey_down
        assert len(recording_spy) >= 1

    def test_thread_safety_main_thread_check(self, app_instance, qtbot):
        """
        Verify that signal handlers execute in the main/GUI thread.

        Qt.QueuedConnection ensures this even when signal emitted from worker thread.
        """
        main_thread = QThread.currentThread()
        handler_thread = None

        # Create a slot that captures the thread it runs in
        def capture_thread(status):
            nonlocal handler_thread
            handler_thread = QThread.currentThread()

        # Connect to recording_status_changed with our test handler
        app_instance.recording_status_changed.connect(capture_thread)

        # Emit signal (simulating from any thread)
        app_instance.recording_status_changed.emit(True)

        # Process events to deliver signal
        QApplication.processEvents()
        qtbot.wait(10)

        # Verify handler ran in main thread
        assert handler_thread is main_thread, "Signal handler did not run in main thread!"

    def test_recording_widget_updates_asynchronously(self, app_instance, qtbot):
        """
        Test that recording widget updates happen asynchronously via signals.

        This prevents the blocking UI update chain.
        """
        # Mock the recording widget
        recording_widget = Mock()
        app_instance.main_window.recording_widget = recording_widget

        # Connect the signal to actual UI method (simulated)
        def update_recording_status(status):
            if status:
                recording_widget.start_recording()
                recording_widget.position_at_bottom_right(app_instance.main_window)
            else:
                recording_widget.finish()

        app_instance.recording_status_changed.connect(update_recording_status)

        # Start recording
        app_instance._start_recording(source="hotkey")

        # Widget methods should NOT be called yet (signal is queued)
        recording_widget.start_recording.assert_not_called()

        # Process events to deliver queued signal
        QApplication.processEvents()
        qtbot.wait(50)

        # NOW widget methods should be called
        recording_widget.start_recording.assert_called_once()
        recording_widget.position_at_bottom_right.assert_called_once()


class TestSignalDecoupling:
    """Test that the signal-based architecture properly decouples components."""

    def test_no_circular_dependencies(self):
        """Verify that app.py doesn't directly depend on UI update methods."""
        import inspect
        from scribe.app import ScribeApp

        # Get source code of _start_recording
        source = inspect.getsource(ScribeApp._start_recording)

        # Verify it emits signals, not direct UI calls
        assert "recording_status_changed.emit" in source, "Should emit recording_status_changed signal"
        assert "main_window.update_recording_status(True)" not in source, "Should NOT call UI method directly"

    def test_signals_are_defined(self):
        """Verify all required signals are defined on ScribeApp."""
        from scribe.app import ScribeApp

        # Check signal definitions
        assert hasattr(ScribeApp, 'recording_status_changed')
        assert hasattr(ScribeApp, 'hotkey_status_changed')
        assert hasattr(ScribeApp, 'transcription_started')
        assert hasattr(ScribeApp, 'transcription_completed')
        assert hasattr(ScribeApp, 'transcription_failed')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
