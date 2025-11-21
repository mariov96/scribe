"""
Transcription Engine - Whisper integration.

Wraps faster-whisper with clean interface.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Result from transcription."""
    text: str
    duration: float  # Audio duration in seconds
    language: Optional[str] = None
    confidence: Optional[float] = None


class TranscriptionEngine:
    """
    Modern transcription engine.

    Wraps faster-whisper with clean interface.
    """

    def __init__(self, config):
        """Initialize transcription engine."""
        self.config = config
        self.model = None
        self._use_api = False
    
    def _detect_best_device(self):
        """
        Detect the best available device (GPU or CPU) for transcription.
        
        Returns:
            tuple: (device, compute_type)
        """
        try:
            import torch
            
            if torch.cuda.is_available():
                # NVIDIA GPU available
                gpu_name = torch.cuda.get_device_name(0)
                logger.info(f"🎮 CUDA GPU detected: {gpu_name}")
                
                # Check GPU memory
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logger.info(f"💾 GPU Memory: {gpu_memory:.1f} GB")
                
                # Use float16 for better performance on GPU
                return "cuda", "float16"
            else:
                logger.info("⚠️  No CUDA GPU detected, using CPU")
                return "cpu", "int8"
                
        except ImportError:
            logger.info("⚠️  PyTorch not installed, defaulting to CPU")
            return "cpu", "int8"
        except Exception as e:
            logger.warning(f"⚠️  Error detecting GPU: {e}, defaulting to CPU")
            return "cpu", "int8"

    def initialize(self) -> bool:
        """
        Initialize Whisper model with GPU acceleration if available.

        Returns:
            True if successful
        """
        try:
            logger.info("Initializing Whisper transcription engine...")
            
            # Import required packages
            try:
                from faster_whisper import WhisperModel
            except ImportError as e:
                logger.error(f"faster-whisper not installed: {e}")
                logger.error("Please install with: pip install faster-whisper")
                return False
            
            # Get model configuration
            model_size = self.config.config.whisper.model
            device = self.config.config.whisper.device
            compute_type = self.config.config.whisper.compute_type
            
            # Smart device detection
            if device == "auto" or compute_type == "auto":
                detected_device, detected_compute = self._detect_best_device()
                if device == "auto":
                    device = detected_device
                if compute_type == "auto":
                    compute_type = detected_compute
            
            logger.info(f"🚀 Using device: {device} with compute type: {compute_type}")
            logger.info(f"📦 Loading Whisper model: {model_size}")
            
            # Load model with optimized settings
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                download_root="models",
                num_workers=4,  # Parallel CPU threads for faster processing
                cpu_threads=4   # Number of CPU threads per worker
            )
            
            logger.info(f"✅ Whisper model '{model_size}' loaded successfully on {device}")
            return True

            # Real model initialization (commented out for now)
            # # Ensure legacy ConfigManager is initialized
            # from src.utils import ConfigManager as LegacyConfigManager
            # if LegacyConfigManager._instance is None:
            #     LegacyConfigManager.initialize()
            #
            # model_options = self.config.get('model_options', {})
            # self._use_api = model_options.get('use_api', False)
            #
            # if not self._use_api:
            #     logger.info("Initializing local Whisper model...")
            #     self.model = create_local_model()
            #     logger.info("Local Whisper model initialized")
            # else:
            #     logger.info("Using API transcription")
            #
            # return True

        except Exception as e:
            logger.error(f"Failed to initialize transcription engine: {e}", exc_info=True)
            return False

    def transcribe(self, audio_data) -> Optional[TranscriptionResult]:
        """
        Transcribe audio data with optimized settings.

        Args:
            audio_data: Audio bytes or file path

        Returns:
            TranscriptionResult or None if failed
        """
        try:
            import io
            import tempfile
            
            # Convert input to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                if isinstance(audio_data, bytes):
                    # Direct bytes from recording
                    temp_file.write(audio_data)
                elif isinstance(audio_data, np.ndarray):
                    # Numpy array from sounddevice
                    sf.write(temp_file.name, audio_data, 16000)
                else:
                    # Copy existing file
                    with open(audio_data, 'rb') as src:
                        temp_file.write(src.read())
                audio_path = temp_file.name
            
            # Optional preprocessing: VAD/noise gate
            try:
                audio_path = self._preprocess_audio(Path(audio_path))
            except Exception as e:
                logger.debug(f"Preprocess skipped/error: {e}")

            logger.info(f"🎤 Transcribing audio file: {audio_path}")
            
            # Optimized transcription parameters for speed
            # Note: vad_filter explicitly disabled by default as it requires onnxruntime
            transcribe_params = {
                "audio": audio_path,
                "beam_size": 1,  # Reduced from 5 for 5x speed boost (greedy decoding)
                "best_of": 1,    # Single pass instead of multiple attempts
                "word_timestamps": False,  # Disabled for faster processing
                "condition_on_previous_text": False,  # Faster for short clips
                "language": "en",  # Pre-specify language (skip detection)
                "vad_filter": False,  # Explicitly disable VAD (requires onnxruntime)
            }
            
            # Only enable VAD if onnxruntime is available
            try:
                import onnxruntime
                transcribe_params["vad_filter"] = True
                transcribe_params["vad_parameters"] = dict(
                    min_silence_duration_ms=500,
                    threshold=0.5
                )
                logger.debug("VAD filter enabled (onnxruntime available)")
            except ImportError:
                logger.debug("onnxruntime not available, VAD filter disabled")
            except Exception as e:
                logger.debug(f"onnxruntime error: {e}, VAD filter disabled")
            
            segments, info = self.model.transcribe(**transcribe_params)
            
            # Combine segments efficiently
            text_parts = []
            total_duration = 0
            total_confidence = 0
            segment_count = 0
            
            for segment in segments:
                text_parts.append(segment.text)
                total_duration = max(total_duration, segment.end)
                total_confidence += segment.avg_logprob
                segment_count += 1
            
            text = " ".join(text_parts).strip()
            avg_confidence = np.exp(total_confidence / segment_count) if segment_count > 0 else 0
            
            logger.info(f"✅ Transcription complete: {len(text)} chars, {total_duration:.1f}s, conf: {avg_confidence:.2%}")
            
            # Clean up resources
            if isinstance(audio_data, (bytes, np.ndarray)):
                try:
                    Path(audio_path).unlink(missing_ok=True)
                except Exception:
                    pass
            
            return TranscriptionResult(
                text=text,
                duration=total_duration,
                language=info.language,
                confidence=avg_confidence
            )

        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            return None

    # --- Audio preprocessing (simple, fast, optional) ---
    def _preprocess_audio(self, wav_path: Path) -> str:
        """Apply a light noise gate and optional VAD-based trimming.

        Returns the path to the processed file (may be the same as input).
        """
        cfg = getattr(self.config, 'config', None)
        if not cfg or not getattr(cfg.audio, 'noise_suppression', True):
            return str(wav_path)

        try:
            data, sr = sf.read(str(wav_path))
            if data.ndim > 1:
                data = np.mean(data, axis=1)
            # Normalize to float32 [-1,1]
            if data.dtype != np.float32:
                data = data.astype(np.float32)
            max_abs = np.max(np.abs(data)) + 1e-9
            # dBFS threshold
            gate_db = getattr(cfg.audio, 'noise_gate_db', -40)
            thresh = max(1e-6, 10 ** (gate_db / 20.0))
            # Compute short-time energy envelope
            frame = max(256, int(sr * 0.02))  # ~20ms
            hop = frame // 2
            padded = np.pad(data, (0, (frame - len(data) % frame) % frame))
            frames = padded.reshape(-1, frame)
            rms = np.sqrt(np.mean(frames**2, axis=1))
            # Build mask where energy is above threshold fraction of max
            rms_norm = rms / (np.max(rms) + 1e-9)
            mask = rms_norm >= thresh
            # Expand mask back to samples
            mask_samples = np.repeat(mask, frame)[:len(padded)]
            gated = np.where(mask_samples[:len(data)], data, 0.0)

            # Optional VAD trim using webrtcvad if available (mono, 16k recommended)
            try:
                import webrtcvad
                vad_level = int(getattr(cfg.audio, 'vad_aggressiveness', 2))
                vad = webrtcvad.Vad(vad_level)
                # Ensure 16k mono 16-bit PCM chunks
                import struct
                if sr != 16000:
                    # Lightweight resample to 16k using numpy (nearest)
                    ratio = 16000 / float(sr)
                    idx = (np.arange(int(len(gated) * ratio)) / ratio).astype(np.int64)
                    gated = gated[idx]
                    sr = 16000
                pcm16 = np.clip(gated * 32767, -32768, 32767).astype(np.int16)
                bytes_ = pcm16.tobytes()
                win_ms = 30
                step = int(16000 * win_ms / 1000) * 2  # bytes per 30ms
                voiced_bits = []
                for i in range(0, len(bytes_), step):
                    chunk = bytes_[i:i+step]
                    if len(chunk) < step:
                        break
                    voiced_bits.append(vad.is_speech(chunk, 16000))
                # Keep only voiced frames
                mask_vad = np.repeat(np.array(voiced_bits, dtype=bool), int(step/2))
                mask_vad = mask_vad[:len(pcm16)]
                pcm16 = np.where(mask_vad, pcm16, 0)
                gated = pcm16.astype(np.float32) / 32768.0
            except Exception:
                pass

            # Optional level normalization to target RMS dBFS
            try:
                if getattr(cfg.audio, 'level_normalization', False):
                    target_db = float(getattr(cfg.audio, 'target_level_dbfs', -20))
                    # Compute RMS
                    rms = float(np.sqrt(np.mean(gated ** 2)) + 1e-9)
                    rms_db = 20.0 * np.log10(max(rms, 1e-9))
                    gain_db = target_db - rms_db
                    gain = 10 ** (gain_db / 20.0)
                    # Apply soft limiter to avoid clipping
                    normalized = np.tanh(gated * gain * 2.0) / 2.0
                    gated = normalized.astype(np.float32)
            except Exception:
                pass

            out_path = wav_path.with_suffix('.pre.wav')
            sf.write(str(out_path), gated, sr)
            return str(out_path)
        except Exception as e:
            logger.debug(f"Audio preprocess failed: {e}")
            return str(wav_path)
