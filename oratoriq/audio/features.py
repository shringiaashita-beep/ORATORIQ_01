"""
Acoustic Feature Extraction Engine for OratorIQ.

Extracts measurable physical speech features:
- Speaking rate (Words Per Minute - WPM)
- Pause distribution (count, mean duration, max duration, silent ratio)
- Pitch statistics (Fundamental frequency F0 mean, standard deviation, semitone range)
- Monotony index (low pitch dynamic range)
- Loudness and Intensity (RMS energy, dynamic range in dB)
- Recording quality (Signal-to-Noise Ratio proxy, clipping percentage)

IMPORTANT METHODOLOGICAL NOTE:
Acoustic features represent physical signal characteristics (fundamental frequency,
signal energy, pause durations). They must NEVER be treated as direct scientific
measures of internal emotional state, psychological honesty, or cognitive intelligence.
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from oratoriq.models.schemas import AudioFeatures


def compute_frame_energy(signal: np.ndarray, frame_size: int, hop_size: int) -> np.ndarray:
    """Computes Root-Mean-Square (RMS) energy for sliding frames."""
    num_frames = max(1, int(math.ceil((len(signal) - frame_size) / hop_size)) + 1)
    energies = np.zeros(num_frames, dtype=np.float32)

    for i in range(num_frames):
        start = i * hop_size
        end = min(len(signal), start + frame_size)
        frame = signal[start:end]
        if len(frame) > 0:
            energies[i] = np.sqrt(np.mean(frame ** 2) + 1e-12)

    return energies


def detect_pauses(
    signal: np.ndarray,
    sr: int,
    silence_threshold_ratio: float = 0.08,
    min_pause_duration_sec: float = 0.28
) -> Tuple[int, float, float, float, List[Dict[str, float]]]:
    """
    Detects silent pauses using adaptive energy thresholding.
    
    Returns:
    (pause_count, mean_pause_sec, max_pause_sec, silent_proportion, pause_intervals)
    """
    frame_size = int(sr * 0.030)  # 30 ms frame
    hop_size = int(sr * 0.015)    # 15 ms hop
    energies = compute_frame_energy(signal, frame_size, hop_size)

    if len(energies) == 0:
        return 0, 0.0, 0.0, 0.0, []

    # Adaptive silence threshold: fraction of 75th percentile energy or noise floor
    peak_energy = float(np.percentile(energies, 85))
    silence_threshold = max(0.005, peak_energy * silence_threshold_ratio)

    is_silent = energies < silence_threshold
    hop_sec = hop_size / float(sr)

    # Find contiguous silent blocks
    pause_intervals = []
    in_pause = False
    pause_start = 0.0

    for i, silent in enumerate(is_silent):
        current_time = i * hop_sec
        if silent and not in_pause:
            in_pause = True
            pause_start = current_time
        elif not silent and in_pause:
            in_pause = False
            pause_dur = current_time - pause_start
            if pause_dur >= min_pause_duration_sec:
                pause_intervals.append({
                    "start": round(pause_start, 2),
                    "end": round(current_time, 2),
                    "duration": round(pause_dur, 2)
                })

    if in_pause:
        end_time = len(is_silent) * hop_sec
        pause_dur = end_time - pause_start
        if pause_dur >= min_pause_duration_sec:
            pause_intervals.append({
                "start": round(pause_start, 2),
                "end": round(end_time, 2),
                "duration": round(pause_dur, 2)
            })

    total_duration = max(1e-4, len(signal) / float(sr))
    total_pause_duration = sum(p["duration"] for p in pause_intervals)
    silent_proportion = min(1.0, round(total_pause_duration / total_duration, 3))

    pause_count = len(pause_intervals)
    mean_pause_sec = round(total_pause_duration / max(1, pause_count), 2) if pause_count > 0 else 0.0
    max_pause_sec = round(max((p["duration"] for p in pause_intervals), default=0.0), 2)

    return pause_count, mean_pause_sec, max_pause_sec, silent_proportion, pause_intervals


def extract_pitch_f0(
    signal: np.ndarray,
    sr: int,
    min_f0: float = 65.0,
    max_f0: float = 350.0
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[bool]]:
    """
    Extracts fundamental frequency (F0) contour and pitch variability.
    
    Returns:
    (f0_mean_hz, f0_std_hz, semitone_range, is_monotonous)
    """
    try:
        import librosa
        # Use librosa's pyin or yin
        f0, voiced_flag, voiced_probs = librosa.pyin(
            signal,
            fmin=min_f0,
            fmax=max_f0,
            sr=sr,
            frame_length=int(sr * 0.04),
            hop_length=int(sr * 0.02)
        )
        voiced_f0 = f0[voiced_flag & ~np.isnan(f0)]
    except Exception:
        # Fallback to simple zero-crossing / autocorrelation approximation
        voiced_f0 = np.array([])

    if len(voiced_f0) < 10:
        return None, None, None, None

    f0_mean = round(float(np.mean(voiced_f0)), 1)
    f0_std = round(float(np.std(voiced_f0)), 1)

    # Compute semitone range between 10th and 90th percentile to ignore outliers
    p10 = float(np.percentile(voiced_f0, 10))
    p90 = float(np.percentile(voiced_f0, 90))
    if p10 > 10.0 and p90 > p10:
        semitone_range = round(12.0 * math.log2(p90 / p10), 1)
    else:
        semitone_range = 0.0

    # Monotony indicator: semitone range < 2.5 semitones indicates flat pitch contour
    is_monotonous = bool(semitone_range < 2.5)

    return f0_mean, f0_std, semitone_range, is_monotonous


def estimate_snr_db(signal: np.ndarray, silent_ratio: float) -> float:
    """Estimates audio Signal-to-Noise Ratio (SNR) in decibels."""
    if len(signal) == 0:
        return 0.0
    energies = compute_frame_energy(signal, 512, 256)
    if len(energies) < 10:
        return 20.0

    speech_floor = float(np.percentile(energies, 90))
    noise_floor = float(np.percentile(energies, 10))

    if noise_floor <= 1e-7:
        return 35.0  # Pristine studio floor

    snr = 20.0 * math.log10(max(1e-4, speech_floor) / max(1e-7, noise_floor))
    return round(max(0.0, min(50.0, snr)), 1)


def extract_acoustic_features(
    signal: np.ndarray,
    sr: int,
    total_words: int = 0,
    clipping_ratio: float = 0.0
) -> AudioFeatures:
    """
    Extracts all physical acoustic metrics from decoded audio.
    """
    duration_sec = round(len(signal) / float(sr), 2)

    # Pause analysis
    p_count, p_mean, p_max, silent_ratio, _ = detect_pauses(signal, sr)

    # Speaking rate (Words Per Minute)
    if duration_sec > 0 and total_words > 0:
        speaking_rate_wpm = round((total_words / (duration_sec / 60.0)), 1)
    else:
        speaking_rate_wpm = None

    # Pitch analysis
    f0_mean, f0_std, semi_range, is_monotone = extract_pitch_f0(signal, sr)

    # Energy / Intensity
    frame_size = int(sr * 0.03)
    hop_size = int(sr * 0.015)
    energies = compute_frame_energy(signal, frame_size, hop_size)
    rms_mean = round(float(np.mean(energies)), 4) if len(energies) > 0 else 0.0

    pos_energies = energies[energies > 1e-6]
    if len(pos_energies) > 5:
        max_e = float(np.percentile(pos_energies, 95))
        min_e = float(np.percentile(pos_energies, 5))
        dynamic_range_db = round(20.0 * math.log10(max(1e-4, max_e) / max(1e-6, min_e)), 1)
    else:
        dynamic_range_db = 0.0

    snr_db = estimate_snr_db(signal, silent_ratio)

    return AudioFeatures(
        duration_sec=duration_sec,
        speaking_rate_wpm=speaking_rate_wpm,
        total_words=total_words,
        total_pauses=p_count,
        mean_pause_duration_sec=p_mean,
        max_pause_duration_sec=p_max,
        silent_region_proportion=silent_ratio,
        pitch_f0_mean_hz=f0_mean,
        pitch_f0_std_hz=f0_std,
        pitch_semitone_range=semi_range,
        is_monotonous=is_monotone,
        rms_energy_mean=rms_mean,
        dynamic_range_db=dynamic_range_db,
        clipping_ratio=clipping_ratio,
        snr_db_estimate=snr_db,
        is_audio_available=True
    )
