"""
Audio Preprocessing, Decoding, Resampling, and Signal Normalization Engine.
"""

import io
import math
import tempfile
import os
import numpy as np
import soundfile as sf
import scipy.signal
from typing import Tuple, Dict, Any, Optional

TARGET_SAMPLE_RATE = 16000


def decode_and_preprocess_audio(
    file_bytes: bytes,
    target_sr: int = TARGET_SAMPLE_RATE,
    max_duration_sec: float = 600.0,
    min_duration_sec: float = 1.0
) -> Tuple[np.ndarray, int, Dict[str, Any]]:
    """
    Decodes audio bytes into a normalized 1D mono float32 numpy array.
    
    Returns:
    (audio_signal, sample_rate, diagnostics)
    """
    diagnostics: Dict[str, Any] = {
        "original_sample_rate": None,
        "channels": 1,
        "duration_sec": 0.0,
        "clipping_detected": False,
        "clipping_ratio": 0.0,
        "peak_amplitude": 0.0,
        "resampled": False
    }

    # 1. First attempt in-memory soundfile decoding
    decoded = False
    data = None
    sr = None
    e_mem = None

    try:
        data, sr = sf.read(io.BytesIO(file_bytes), dtype="float32")
        decoded = True
    except Exception as err:
        e_mem = err

    # 2. If soundfile failed but bytes have RIFF header, try scipy.io.wavfile
    if not decoded and file_bytes[:4] == b"RIFF":
        try:
            import scipy.io.wavfile as wavfile
            sr_wav, raw_data = wavfile.read(io.BytesIO(file_bytes))
            if raw_data.dtype == np.int16:
                data = (raw_data / 32768.0).astype(np.float32)
            elif raw_data.dtype == np.int32:
                data = (raw_data / 2147483648.0).astype(np.float32)
            elif raw_data.dtype == np.uint8:
                data = ((raw_data - 128) / 128.0).astype(np.float32)
            else:
                data = raw_data.astype(np.float32)
            sr = sr_wav
            decoded = True
        except Exception:
            pass

    # 3. Fallback to tempfile with proper extension for librosa/audioread
    if not decoded:
        suffix = ".wav"
        if len(file_bytes) >= 4:
            header4 = file_bytes[:4]
            if header4 == b"RIFF":
                suffix = ".wav"
            elif header4 == b"OggS":
                suffix = ".ogg"
            elif header4 == b"\x1a\x45\xdf\xa3":
                suffix = ".webm"
            elif header4 == b"fLaC":
                suffix = ".flac"
            elif file_bytes[:3] == b"ID3" or file_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xfa"):
                suffix = ".mp3"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            import librosa
            data, sr = librosa.load(tmp_path, sr=None, mono=False)
            if data.ndim == 2:
                data = data.T
            decoded = True
        except Exception as e_disk:
            raise ValueError(
                f"Failed to decode audio stream: {str(e_mem)} | {str(e_disk)}. "
                f"Please ensure the recording contains valid PCM WAV, MP3, or OGG audio."
            )
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    diagnostics["original_sample_rate"] = sr

    # Convert multi-channel to mono
    if data.ndim > 1:
        diagnostics["channels"] = data.shape[1]
        data = np.mean(data, axis=1)
    else:
        diagnostics["channels"] = 1

    # Check clipping (> 0.99 or < -0.99)
    total_samples = len(data)
    if total_samples == 0:
        raise ValueError("Audio recording contains no audible samples.")

    clipping_samples = int(np.sum(np.abs(data) >= 0.99))
    clipping_ratio = round(clipping_samples / max(1, total_samples), 4)
    diagnostics["clipping_ratio"] = clipping_ratio
    diagnostics["clipping_detected"] = clipping_ratio > 0.005  # > 0.5% samples clipped
    diagnostics["peak_amplitude"] = round(float(np.max(np.abs(data))), 4)

    # Resample to target_sr if required
    if sr != target_sr:
        num_target_samples = int(round(len(data) * target_sr / sr))
        data = scipy.signal.resample(data, num_target_samples).astype(np.float32)
        sr = target_sr
        diagnostics["resampled"] = True

    duration_sec = round(len(data) / float(sr), 2)
    diagnostics["duration_sec"] = duration_sec

    if duration_sec < min_duration_sec:
        raise ValueError(f"Audio recording duration ({duration_sec}s) is too short. Minimum duration is {min_duration_sec}s.")

    if duration_sec > max_duration_sec:
        raise ValueError(f"Audio recording duration ({duration_sec}s) exceeds maximum allowed duration of {max_duration_sec}s.")

    return data, sr, diagnostics
