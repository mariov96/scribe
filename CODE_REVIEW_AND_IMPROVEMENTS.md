# Scribe Codebase Review & Improvement Plan

## 1. Performance Optimization: Audio Pipeline
**Current State:**
The current audio pipeline involves excessive disk I/O and data conversion:
1. `AudioRecorder` captures numpy arrays.
2. `stop_recording` concatenates arrays, writes to `temp_recording.wav`, reads it back as `bytes`, and emits `bytes`.
3. `TranscriptionWorker` passes `bytes` to `TranscriptionEngine`.
4. `TranscriptionEngine` writes `bytes` to a temporary WAV file.
5. `_preprocess_audio` reads the WAV file, processes it, and writes a *new* WAV file.
6. `faster-whisper` reads the final WAV file.

**Improvement:**
Implement a fully in-memory pipeline using Numpy arrays.
1. `AudioRecorder` should emit the raw `np.ndarray` and sample rate.
2. `TranscriptionWorker` should accept and pass the `np.ndarray`.
3. `TranscriptionEngine` should accept `np.ndarray`.
4. Preprocessing (VAD, Normalization) should operate directly on the `np.ndarray`.
5. `faster-whisper` supports `np.ndarray` input directly.

**Benefit:** Eliminates 3 disk writes and 3 disk reads per transcription, significantly reducing latency and SSD wear.

## 2. Maintenance: System Tray Consolidation
**Current State:**
- `src/scribe/ui_fluent/components/system_tray.py` contains a robust `ScribeSystemTray` class.
- `src/scribe/ui_fluent/main_window.py` ignores this class and implements its own duplicate system tray logic in `_setup_system_tray`.

**Improvement:**
Refactor `ScribeMainWindow` to use the dedicated `ScribeSystemTray` component. This reduces code duplication and centralizes tray logic (menus, notifications, behavior) in one file.

## 3. Maintenance: UI Styling
**Current State:**
`src/scribe/ui_fluent/main_window.py` contains a large, hardcoded CSS string (~50 lines) for styling the application.

**Improvement:**
Move styles to `src/scribe/ui_fluent/styles.qss` or a constant in `branding.py`. This improves readability of the main window code and makes theming easier to manage.

## 4. Responsiveness: Background File Operations
**Current State:**
`AudioRecorder.stop_recording` performs file I/O (saving debug recordings) in the main thread (or the thread calling stop). For long recordings, this could briefly freeze the UI.

**Improvement:**
Offload the "Save Debug Recording" operation to a background thread or use `QtConcurrent`.

## 5. Code Structure: Transcription Engine
**Current State:**
`TranscriptionEngine` mixes initialization logic, device detection, and audio preprocessing in one file.

**Improvement:**
Extract audio preprocessing logic (VAD, Normalization) into a dedicated `AudioPreprocessor` class. This makes the engine cleaner and allows for easier unit testing of signal processing logic.

---

## Proposed Action Plan

1.  **Refactor System Tray**: Replace inline tray logic in `main_window.py` with `ScribeSystemTray`.
2.  **Optimize Audio Pipeline**:
    *   Modify `AudioRecorder` to emit `np.ndarray`.
    *   Update `TranscriptionWorker` to handle arrays.
    *   Update `TranscriptionEngine` to process arrays in memory.
3.  **Extract Styles**: Move CSS to a separate file.