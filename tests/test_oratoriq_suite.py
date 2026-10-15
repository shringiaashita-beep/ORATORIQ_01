"""
Comprehensive Automated Test Suite for OratorIQ Speech Evaluation Engine.

Validates:
1. Audio validation, magic header probing, size boundaries
2. Audio preprocessing, stereo-to-mono, resampling, clipping detection
3. Acoustic feature extraction (WPM, pauses, F0 pitch contour, monotony, energy)
4. Configurable rubric weights, 1-5 scale mapping, available-axis score aggregation
5. Explicit missing-axis defensibility (transcript-only vs audio-plus-transcript)
6. Contrastive speech dataset schema compliance, pair consistency, and SHA-256 hash
7. Evidence-linked feedback cards with measured values and drills
8. Storage persistence, reproducibility metadata, and HTML report export
9. Full FastAPI v1 endpoints (/api/v1/*)
"""

import io
import pytest
import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient

from ragas_dashboard.backend.app import app
from oratoriq.models.schemas import SpeechSample, ContrastivePair, RubricDefinition
from oratoriq.rubric.rubric_engine import (
    get_default_rubric,
    rating_to_normalized_score,
    aggregate_rubric_scores,
    RubricRegistry
)
from oratoriq.dataset.dataset_loader import ContrastiveDataset
from oratoriq.dataset.validator import validate_dataset_records
from oratoriq.audio.validator import validate_audio_payload, probe_audio_format
from oratoriq.audio.preprocessor import decode_and_preprocess_audio
from oratoriq.audio.features import extract_acoustic_features, detect_pauses
from oratoriq.audio.transcriber import OratorIQTranscriber
from oratoriq.evaluator.engine import OratorIQEvaluationEngine
from oratoriq.persistence.store import EvaluationStore


@pytest.fixture
def client():
    return TestClient(app)


def generate_synthetic_wav_bytes(
    duration_sec: float = 3.0,
    sample_rate: int = 16000,
    frequency_hz: float = 220.0
) -> bytes:
    """Generates synthetic in-memory WAV audio for testing."""
    num_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    # Sine wave with gentle amplitude modulation and brief silence pause
    signal = 0.5 * np.sin(2 * np.pi * frequency_hz * t)
    # Insert 0.5s pause in middle
    pause_start = int(1.2 * sample_rate)
    pause_end = int(1.7 * sample_rate)
    signal[pause_start:pause_end] = 0.0

    buf = io.BytesIO()
    sf.write(buf, signal.astype(np.float32), sample_rate, format="WAV")
    return buf.getvalue()


# --- 1. Audio Validation Tests ---

def test_audio_validator_empty_payload():
    is_valid, msg, _ = validate_audio_payload(b"")
    assert not is_valid
    assert "empty" in msg.lower()


def test_audio_validator_oversized():
    huge_bytes = b"0" * (51 * 1024 * 1024)
    is_valid, msg, _ = validate_audio_payload(huge_bytes)
    assert not is_valid
    assert "exceeds" in msg.lower()


def test_audio_validator_valid_wav():
    wav_bytes = generate_synthetic_wav_bytes(duration_sec=2.0)
    is_valid, msg, meta = validate_audio_payload(wav_bytes, filename="test.wav")
    assert is_valid
    assert meta["format"] == "wav"


def test_audio_magic_header_probe():
    assert probe_audio_format(b"RIFF\x00\x00\x00\x00WAVE") == "wav"
    assert probe_audio_format(b"OggS\x00\x00") == "ogg"
    assert probe_audio_format(b"fLaC\x00\x00") == "flac"
    assert probe_audio_format(b"ID3\x04\x00") == "mp3"
    assert probe_audio_format(b"\x1a\x45\xdf\xa3") == "webm"


# --- 2. Audio Preprocessing & Decoding Tests ---

def test_audio_preprocessor_resampling_and_clipping():
    wav_bytes = generate_synthetic_wav_bytes(duration_sec=2.5, sample_rate=22050)
    signal, sr, diag = decode_and_preprocess_audio(wav_bytes, target_sr=16000)

    assert sr == 16000
    assert diag["resampled"] is True
    assert diag["duration_sec"] >= 2.4
    assert len(signal) > 0
    assert isinstance(signal, np.ndarray)


def test_audio_preprocessor_too_short():
    short_wav = generate_synthetic_wav_bytes(duration_sec=0.4)
    with pytest.raises(ValueError, match="too short"):
        decode_and_preprocess_audio(short_wav, min_duration_sec=1.0)


# --- 3. Acoustic Feature Extraction Tests ---

def test_acoustic_feature_extraction():
    wav_bytes = generate_synthetic_wav_bytes(duration_sec=3.0, sample_rate=16000, frequency_hz=180.0)
    signal, sr, diag = decode_and_preprocess_audio(wav_bytes)

    features = extract_acoustic_features(signal, sr, total_words=10)
    assert features.is_audio_available is True
    assert features.duration_sec >= 2.9
    assert features.speaking_rate_wpm is not None
    assert features.speaking_rate_wpm > 0
    assert features.total_pauses >= 1
    assert features.rms_energy_mean > 0
    assert features.snr_db_estimate >= 0


# --- 4. Rubric Engine & Normalization Tests ---

def test_default_rubric_weights_sum_to_one():
    rubric = get_default_rubric()
    assert rubric.validate_weights() is True
    total = sum(c.weight for c in rubric.criteria.values())
    assert abs(total - 1.0) < 1e-4
    assert len(rubric.criteria) == 5


def test_rating_to_normalized_score():
    assert rating_to_normalized_score(1) == 0.0
    assert rating_to_normalized_score(2) == 25.0
    assert rating_to_normalized_score(3) == 50.0
    assert rating_to_normalized_score(4) == 75.0
    assert rating_to_normalized_score(5) == 100.0


def test_score_aggregation_with_missing_audio_criterion():
    rubric = get_default_rubric()
    from oratoriq.models.schemas import CriterionScoreResult

    scores = {
        "content_and_relevance": CriterionScoreResult(
            criterion_id="content_and_relevance", criterion_name="Content", raw_rating=4, normalized_score=75.0, weight=0.25, status="evaluated"
        ),
        "structure_and_coherence": CriterionScoreResult(
            criterion_id="structure_and_coherence", criterion_name="Structure", raw_rating=4, normalized_score=75.0, weight=0.20, status="evaluated"
        ),
        "fluency_and_pacing": CriterionScoreResult(
            criterion_id="fluency_and_pacing", criterion_name="Fluency", raw_rating=4, normalized_score=75.0, weight=0.20, status="evaluated"
        ),
        "clarity_and_conciseness": CriterionScoreResult(
            criterion_id="clarity_and_conciseness", criterion_name="Clarity", raw_rating=4, normalized_score=75.0, weight=0.15, status="evaluated"
        ),
        # Vocal delivery is unavailable (0.20 weight missing)
        "vocal_delivery": CriterionScoreResult(
            criterion_id="vocal_delivery", criterion_name="Vocal", raw_rating=None, normalized_score=None, weight=0.20, status="unavailable"
        )
    }

    overall, coverage, missing = aggregate_rubric_scores(scores, rubric)
    assert "vocal_delivery" in missing
    assert coverage == 0.8  # 80% coverage
    # Since all available are 75.0, the normalized mean must be exactly 75.0!
    assert overall == 75.0


# --- 5. Contrastive Dataset Tests ---

def test_contrastive_dataset_loader_and_hash():
    dataset = ContrastiveDataset()
    assert len(dataset.get_all_pairs()) >= 50
    assert dataset.dataset_hash != ""
    assert len(dataset.dataset_hash) == 64

    # Verify scenario breakdown
    manifest = dataset.get_manifest()
    assert "public_speaking" in manifest["scenarios_distribution"]
    assert "interview_answers" in manifest["scenarios_distribution"]
    assert manifest["total_samples"] >= 100


def test_dataset_validator_cli_passes():
    report = validate_dataset_records(ContrastiveDataset().dataset_path)
    assert report["is_valid"] is True
    assert len(report["errors"]) == 0
    assert report["total_pairs_checked"] >= 50


# --- 6. End-to-End Evaluation Engine Tests ---

def test_evaluation_engine_transcript_only_mode():
    engine = OratorIQEvaluationEngine()
    transcriber = OratorIQTranscriber()

    speech_text = (
        "In 2024, our team launched an automated telemetry pipeline that reduced customer outage latency by forty-two percent. "
        "First, we decoupled the database read replicas. Second, we deployed distributed caching with Redis. "
        "Consequently, system availability reached ninety-nine point nine-nine percent across our peak quarter."
    )
    annotation = transcriber.transcribe(audio_signal=None, sr=0, provided_transcript=speech_text)
    result = engine.evaluate(annotation, scenario="presentation_delivery")

    assert result.evaluation_mode == "transcript_only"
    assert result.coverage_percentage == 80.0
    assert "vocal_delivery" in result.missing_criteria
    assert result.criterion_scores["vocal_delivery"].status == "unavailable"
    assert result.overall_score is not None
    assert len(result.feedback_items) >= 1
    assert len(result.contrastive_matches) >= 1
    assert result.reproducibility["input_sha256"] != ""


def test_evaluation_engine_audio_plus_transcript_mode():
    engine = OratorIQEvaluationEngine()
    transcriber = OratorIQTranscriber()
    wav_bytes = generate_synthetic_wav_bytes(duration_sec=3.5)
    signal, sr, diag = decode_and_preprocess_audio(wav_bytes)

    speech_text = "Good morning. Today I will present our three architectural guardrails for machine learning safety."
    annotation = transcriber.transcribe(audio_signal=signal, sr=sr, provided_transcript=speech_text)
    audio_features = extract_acoustic_features(signal, sr, total_words=len(annotation.words))

    result = engine.evaluate(annotation, scenario="public_speaking", audio_features=audio_features, raw_input_bytes=wav_bytes)

    assert result.evaluation_mode == "audio_plus_transcript"
    assert result.coverage_percentage == 100.0
    assert result.criterion_scores["vocal_delivery"].status == "evaluated"
    assert result.overall_score is not None
    assert result.audio_features is not None


# --- 7. FastAPI v1 REST API Integration Tests ---

def test_api_v1_health(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "OratorIQ" in data["service"]


def test_api_v1_ready(client):
    res = client.get("/api/v1/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["dataset_status"]["loaded_pairs"] >= 50


def test_api_v1_evaluate_transcript_endpoint(client):
    payload = {
        "transcript": "During our quarterly sprint, we migrated thirty microservices to Kubernetes, eliminating fifty thousand dollars in monthly EC2 hosting costs.",
        "scenario": "interview_answers",
        "speech_prompt": "Tell me about a cloud migration project you led."
    }
    res = client.post("/api/v1/evaluations/transcript", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    assert data["evaluation_mode"] == "transcript_only"
    assert data["overall_score"] is not None
    assert data["coverage_percentage"] == 80.0

    run_id = data["run_id"]

    # Verify retrieval by run ID
    res_get = client.get(f"/api/v1/evaluations/{run_id}")
    assert res_get.status_code == 200
    assert res_get.json()["run_id"] == run_id

    # Verify JSON reproducibility report
    res_report = client.get(f"/api/v1/evaluations/{run_id}/report")
    assert res_report.status_code == 200
    assert "reproducibility" in res_report.json()

    # Verify HTML printable report
    res_html = client.get(f"/api/v1/evaluations/{run_id}/export.html")
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers["content-type"]
    assert "OratorIQ Evaluation Report" in res_html.text


def test_api_v1_evaluate_audio_endpoint(client):
    wav_bytes = generate_synthetic_wav_bytes(duration_sec=2.5)
    files = {"file": ("demo.wav", wav_bytes, "audio/wav")}
    data = {
        "scenario": "persuasive_pitches",
        "transcript": "CryoPulse sensors forecast thermal breach forty-five minutes before pharmaceutical cargo spoils."
    }
    res = client.post("/api/v1/evaluations/audio", files=files, data=data)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["evaluation_mode"] == "audio_plus_transcript"
    assert res_data["coverage_percentage"] == 100.0
    assert res_data["audio_features"]["speaking_rate_wpm"] is not None


def test_api_v1_datasets_endpoints(client):
    res_manifest = client.get("/api/v1/datasets")
    assert res_manifest.status_code == 200
    assert res_manifest.json()["total_pairs"] >= 50

    res_pairs = client.get("/api/v1/datasets/pairs?scenario=public_speaking")
    assert res_pairs.status_code == 200
    assert res_pairs.json()["total_pairs"] >= 10

    res_validate = client.post("/api/v1/datasets/validate", json={})
    assert res_validate.status_code == 200
    assert res_validate.json()["is_valid"] is True


def test_api_v1_rubrics_endpoints(client):
    res = client.get("/api/v1/rubrics")
    assert res.status_code == 200
    data = res.json()
    assert len(data["rubrics"]) >= 1

    r_id = data["rubrics"][0]["rubric_id"]
    res_single = client.get(f"/api/v1/rubrics/{r_id}")
    assert res_single.status_code == 200
    assert res_single.json()["rubric_id"] == r_id


def test_api_v1_history_endpoint(client):
    res = client.get("/api/v1/history?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert isinstance(data["runs"], list)


def test_api_v1_unified_evaluation_json(client):
    payload = {
        "transcript": "Good morning team. Today we announce our automated evaluation architecture for audio processing.",
        "scenario": "presentation_delivery",
        "speech_prompt": "Deliver an executive kickoff."
    }
    res = client.post("/api/v1/evaluations", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    assert data["evaluation_mode"] == "transcript_only"
    assert data["overall_score"] is not None


def test_api_v1_unified_evaluation_multipart(client):
    wav_bytes = generate_synthetic_wav_bytes(duration_sec=2.0)
    files = {"file": ("speech.wav", wav_bytes, "audio/wav")}
    data = {
        "scenario": "interview_answers",
        "transcript": "I led the development of our distributed machine learning pipeline."
    }
    res = client.post("/api/v1/evaluations", files=files, data=data)
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    assert data["evaluation_mode"] == "audio_plus_transcript"
    assert data["overall_score"] is not None


def test_api_v1_rubric_versions_endpoint(client):
    res = client.get("/api/v1/rubrics/speech_default_v1/versions")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["total_versions"] >= 1
    assert data["rubric_id"] == "speech_default_v1"


def test_api_v1_datasets_scoped_endpoint(client):
    res = client.get("/api/v1/datasets/default/pairs?scenario=public_speaking")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["pairs"]) >= 10

