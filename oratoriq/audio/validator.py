"""
Audio Input Validation and File Boundary Protection for OratorIQ.
"""

import io
from typing import Tuple, Dict, Any, Optional

MAX_AUDIO_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_DURATION_SECONDS = 600.0              # 10 minutes
MIN_DURATION_SECONDS = 1.0                # 1 second

# Supported magic byte signatures
AUDIO_MAGIC_SIGNATURES = {
    "wav": [b"RIFF"],
    "ogg": [b"OggS"],
    "flac": [b"fLaC"],
    "mp3": [b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"],
    "webm": [b"\x1a\x45\xdf\xa3"]
}


def probe_audio_format(header_bytes: bytes) -> Optional[str]:
    """Probes the magic bytes of the file header to detect audio format."""
    if len(header_bytes) < 4:
        return None

    # Check WAV
    if header_bytes[:4] == b"RIFF" and len(header_bytes) >= 12 and header_bytes[8:12] == b"WAVE":
        return "wav"

    # Check Ogg
    if header_bytes[:4] == b"OggS":
        return "ogg"

    # Check FLAC
    if header_bytes[:4] == b"fLaC":
        return "flac"

    # Check WebM / Matroska
    if header_bytes[:4] == b"\x1a\x45\xdf\xa3":
        return "webm"

    # Check MP3 ID3 tag or MPEG sync word
    if header_bytes[:3] == b"ID3":
        return "mp3"
    if len(header_bytes) >= 2 and header_bytes[0] == 0xFF and (header_bytes[1] & 0xE0) == 0xE0:
        return "mp3"

    return None


def validate_audio_payload(
    file_bytes: bytes,
    filename: Optional[str] = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates audio file size, headers, and container sanity.
    Returns: (is_valid, error_message, metadata)
    """
    size_bytes = len(file_bytes)
    metadata = {
        "size_bytes": size_bytes,
        "format": None,
        "filename": filename or "recording.wav"
    }

    if size_bytes == 0:
        return False, "Audio recording payload is completely empty (0 bytes).", metadata

    if size_bytes > MAX_AUDIO_SIZE_BYTES:
        max_mb = MAX_AUDIO_SIZE_BYTES // (1024 * 1024)
        actual_mb = round(size_bytes / (1024 * 1024), 2)
        return False, f"Audio file size ({actual_mb} MB) exceeds maximum allowed limit of {max_mb} MB.", metadata

    format_detected = probe_audio_format(file_bytes[:16])
    if not format_detected:
        # Check if filename has an extension that we could attempt
        ext = (filename or "").split(".")[-1].lower()
        if ext in ["wav", "mp3", "ogg", "webm", "flac"]:
            format_detected = ext
        else:
            return False, "Unsupported or malformed audio format. Supported formats: WAV, WebM, OGG, FLAC, MP3.", metadata

    metadata["format"] = format_detected
    return True, "", metadata
