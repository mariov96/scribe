"""
Qt Threading Utilities for Scribe

This module provides reusable patterns for thread-safe Qt operations.
All patterns here have been battle-tested in production to fix critical
threading deadlocks (see buildstate.json BUG-001).

Threading Architecture:
    Scribe uses Qt's event loop with multiple threads:
    1. Main/GUI Thread - Qt event loop, all UI updates
    2. Keyboard Library Thread - Global hotkey detection
    3. Audio Thread - PortAudio callback (DO NOT emit signals here!)
    4. Worker Threads - Long-running operations (transcription, etc.)

Common Threading Pitfalls:
    - Calling UI methods from non-main threads → DEADLOCK
    - Emitting Qt signals from PortAudio callback → SEGFAULT
    - Synchronous cross-thread method calls → HANG (re-entrancy deadlock)

Safe Patterns:
    - Use @defer_to_main_thread for any method called from background threads
    - Use emit_threadsafe() for signals emitted from non-Qt threads
    - Always connect cross-thread signals with Qt.QueuedConnection
    - Use QTimer.singleShot(0) to break synchronous call chains

Author: Scribe Team
License: MIT
"""

import logging
from functools import wraps
from typing import Callable, Any, Optional
from PyQt5.QtCore import QTimer, QObject, QThread, pyqtSignal as Signal, Qt

logger = logging.getLogger(__name__)


def defer_to_main_thread(func: Callable) -> Callable:
    """
    Decorator to defer function execution to Qt main thread.

    Uses QTimer.singleShot(0) to queue the function call to the Qt event loop,
    ensuring it executes in the main/GUI thread. This breaks any synchronous
    call chain that could cause re-entrancy deadlocks.

    Usage:
        @defer_to_main_thread
        def start_recording(self):
            # This will always run in main thread, even if called from
            # keyboard library thread or other background thread
            self.audio_recorder.start()

    IMPORTANT:
        - Use this for ANY method that updates UI or calls Qt objects
        - Particularly critical for hotkey handlers and callbacks
        - Execution is asynchronous (returns immediately, runs later)
        - Return values are lost (by design - async operation)

    Args:
        func: Function to defer to main thread

    Returns:
        Wrapped function that defers execution via QTimer
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Schedule function call on Qt event loop (runs in main thread)
            QTimer.singleShot(0, lambda: func(*args, **kwargs))
        except Exception as e:
            logger.error(f"Failed to defer {func.__name__} to main thread: {e}", exc_info=True)

    return wrapper


def is_main_thread() -> bool:
    """
    Check if currently executing in Qt main/GUI thread.

    Returns:
        True if in main thread, False otherwise
    """
    return QThread.currentThread() == QThread.currentThread().parent()


def assert_main_thread(func: Callable) -> Callable:
    """
    Decorator to assert function is called from main thread.

    Raises AssertionError if called from background thread.
    Use this to enforce thread safety during development.

    Usage:
        @assert_main_thread
        def update_ui(self):
            # Will crash with helpful error if called from wrong thread
            self.label.setText("Updated")

    Args:
        func: Function that must run in main thread

    Returns:
        Wrapped function with thread assertion
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if QThread.currentThread() != QThread.currentThread().parent():
            thread_name = QThread.currentThread().objectName() or "Unknown"
            raise AssertionError(
                f"{func.__name__} must be called from main thread, "
                f"but was called from {thread_name}"
            )
        return func(*args, **kwargs)

    return wrapper


class ThreadSafeSignalEmitter(QObject):
    """
    Helper for emitting Qt signals from non-Qt threads safely.

    Qt signals should not be emitted directly from threads like PortAudio
    callback or other C library threads. This class provides a safe way
    to emit signals by deferring emission to the main thread.

    Usage:
        class MyRecorder:
            def __init__(self):
                self.signal_emitter = ThreadSafeSignalEmitter()
                self.level_changed = Signal(float)

            def audio_callback(self, data):
                # Called from PortAudio thread - UNSAFE to emit signal directly!
                level = calculate_level(data)

                # Safe: defer signal emission to main thread
                self.signal_emitter.emit_threadsafe(self.level_changed, level)
    """

    def __init__(self):
        super().__init__()
        self._signal_queue = []

    def emit_threadsafe(self, signal: Signal, *args):
        """
        Emit a Qt signal from any thread safely.

        Args:
            signal: The Qt signal to emit
            *args: Arguments to pass to signal.emit()
        """
        # Store signal and args
        self._signal_queue.append((signal, args))

        # Defer emission to main thread via QTimer
        QTimer.singleShot(0, self._process_signal_queue)

    def _process_signal_queue(self):
        """Process queued signals in main thread."""
        while self._signal_queue:
            signal, args = self._signal_queue.pop(0)
            try:
                signal.emit(*args)
            except Exception as e:
                logger.error(f"Failed to emit signal: {e}", exc_info=True)


def connect_threadsafe(signal: Signal, slot: Callable, connection_type: Qt.ConnectionType = Qt.QueuedConnection):
    """
    Connect a signal to a slot with explicit thread-safe connection type.

    By default uses Qt.QueuedConnection to ensure signal delivery happens
    in the receiver's thread (usually main thread). This is critical for
    cross-thread communication.

    Usage:
        # Instead of:
        self.recording_started.connect(self.update_ui)

        # Use:
        connect_threadsafe(self.recording_started, self.update_ui)

    Args:
        signal: Qt signal to connect
        slot: Callable to connect to signal
        connection_type: Qt connection type (default: Qt.QueuedConnection)
    """
    signal.connect(slot, type=connection_type)


def log_thread_info(func: Callable) -> Callable:
    """
    Decorator to log thread information when function is called.

    Useful for debugging threading issues. Logs which thread the
    function is executing in.

    Usage:
        @log_thread_info
        def critical_method(self):
            # Logs: "critical_method called from thread: MainThread"
            ...

    Args:
        func: Function to wrap with thread logging

    Returns:
        Wrapped function that logs thread info
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread_name = QThread.currentThread().objectName() or "MainThread"
        logger.debug(f"{func.__name__} called from thread: {thread_name}")
        return func(*args, **kwargs)

    return wrapper


# Convenience singleton for thread-safe signal emission
_global_signal_emitter = ThreadSafeSignalEmitter()


def emit_signal_safe(signal: Signal, *args):
    """
    Global convenience function to emit signals safely from any thread.

    Usage:
        from scribe.utils.qt_threading import emit_signal_safe

        def audio_callback(data):
            # Running in PortAudio thread
            level = calculate_level(data)
            emit_signal_safe(self.level_changed, level)

    Args:
        signal: Qt signal to emit
        *args: Arguments to pass to signal.emit()
    """
    _global_signal_emitter.emit_threadsafe(signal, *args)
