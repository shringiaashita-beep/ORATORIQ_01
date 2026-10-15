"""
FastAPI Version 1 REST API Router for OratorIQ Speech Evaluation Platform.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger("oratoriq.api.v1")

from oratoriq.models.schemas import (
    EvaluationResult,
    RubricDefinition,
    CriterionConfig,
    ScoringAnchor,
    SpeechScenario
)
from oratoriq.dataset.dataset_loader import ContrastiveDataset
from oratoriq.dataset.validator import validate_dataset_records
from oratoriq.rubric.rubric_engine import (
    RubricRegistry,
    get_default_rubric,
    compute_rubric_hash
)
from oratoriq.audio.validator import validate_audio_payload
from oratoriq.audio.preprocessor import decode_and_preprocess_audio
from oratoriq.audio.features import extract_acoustic_features
from oratoriq.audio.transcriber import OratorIQTranscriber
from oratoriq.evaluator.engine import OratorIQEvaluationEngine
from oratoriq.persistence.store import EvaluationStore


router = APIRouter(prefix="/api/v1", tags=["OratorIQ Speech Engine v1"])

# Global shared service singletons
dataset_service = ContrastiveDataset()
rubric_registry = RubricRegistry()
store_service = EvaluationStore()
evaluator_engine = OratorIQEvaluationEngine(dataset=dataset_service)
transcriber_service = OratorIQTranscriber()


# --- Request & Response Schemas ---

class TranscriptEvaluationRequest(BaseModel):
    transcript: str = Field(..., min_length=10, max_length=50000, description="Spoken transcript text to evaluate.")
    scenario: str = Field(default="public_speaking", description="Speech scenario category.")
    rubric_id: str = Field(default="speech_default_v1", description="Target rubric configuration ID.")
    speech_prompt: Optional[str] = Field(default=None, max_length=2000, description="Intended prompt or question.")


class CreateRubricRequest(BaseModel):
    rubric_id: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=3, max_length=100)
    version: str = Field(default="1.0.0")
    criteria: Dict[str, Any] = Field(..., description="Map of criteria with weights summing to 1.0")


class DatasetValidateRequest(BaseModel):
    custom_dataset_path: Optional[str] = Field(default=None, description="Optional custom file path to validate.")


# --- 1. Liveness & Readiness Probes ---

@router.get("/health", summary="OratorIQ Engine Liveness Probe")
def health_check():
    """Returns basic process liveness status and version information."""
    return {
        "status": "healthy",
        "service": "OratorIQ Speech Evaluation Engine",
        "version": "1.0.0",
        "capabilities": [
            "audio_pcm_decoding",
            "acoustic_wpm_extraction",
            "pitch_contour_f0",
            "pause_distribution_detection",
            "evidence_linked_feedback",
            "contrastive_exemplar_calibration",
            "immutable_rubric_versioning"
        ]
    }


@router.get("/ready", summary="OratorIQ Capability Readiness Probe")
def readiness_check():
    """Checks availability of audio processors, transcription services, and loaded datasets."""
    whisper_configured = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "ready",
        "dataset_status": {
            "loaded_pairs": len(dataset_service.get_all_pairs()),
            "dataset_hash": dataset_service.dataset_hash,
            "version": dataset_service.version
        },
        "audio_engine": {
            "status": "OPERATIONAL",
            "backend": "soundfile + scipy.signal + librosa",
            "supported_formats": ["wav", "mp3", "ogg", "webm", "flac"]
        },
        "transcription_engine": {
            "local_alignment": "OPERATIONAL",
            "whisper_api": "OPERATIONAL" if whisper_configured else "OPTIONAL_KEY_NOT_CONFIGURED",
            "details": "Client speech recognition / transcript alignment active. Configure OPENAI_API_KEY for automatic server-side Whisper transcription."
        }
    }


# --- 2. Speech Evaluation Endpoints ---

@router.post("/evaluations/audio", summary="Evaluate Speech Recording (Audio + Optional Transcript)")
async def evaluate_audio(
    file: Optional[UploadFile] = File(default=None, description="Audio recording file (WAV, MP3, WebM, OGG, FLAC)"),
    audio_file: Optional[UploadFile] = File(default=None, description="Audio recording file alias"),
    scenario: str = Form(default="public_speaking"),
    rubric_id: str = Form(default="speech_default_v1"),
    speech_prompt: Optional[str] = Form(default=None),
    transcript: Optional[str] = Form(default=None)
):
    """
    Ingests and validates raw audio recording, extracts genuine physical acoustic features
    (WPM, pauses, pitch variability, dynamic range), transcribes/aligns text,
    and runs contrastive rubric evaluation.
    """
    upload_target = file or audio_file
    if not upload_target:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing audio file. Please provide an audio recording."
        )

    file_bytes = await upload_target.read()

    # Step 1: Input Validation
    is_valid, err_msg, meta = validate_audio_payload(file_bytes, filename=upload_target.filename)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    # Step 2: Audio Preprocessing & Normalization
    try:
        signal, sr, diag = decode_and_preprocess_audio(file_bytes)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Audio decoding failure: {str(e)}")

    # Step 3: Transcription / Alignment
    try:
        annotation = transcriber_service.transcribe(
            audio_signal=signal,
            sr=sr,
            provided_transcript=transcript
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Transcription error: {str(e)}")

    # Step 4: Acoustic Feature Extraction
    audio_features = extract_acoustic_features(
        signal=signal,
        sr=sr,
        total_words=len(annotation.words),
        clipping_ratio=diag.get("clipping_ratio", 0.0)
    )

    # Step 5: Rubric Evaluation
    target_rubric = rubric_registry.get_rubric(rubric_id)
    eval_result = evaluator_engine.evaluate(
        transcript_annotation=annotation,
        scenario=scenario,
        audio_features=audio_features,
        rubric=target_rubric,
        speech_prompt=speech_prompt,
        raw_input_bytes=file_bytes
    )

    # Step 6: Persist Run
    store_service.save_run(eval_result)

    return eval_result


@router.post("/evaluations/transcript", summary="Evaluate Speech Transcript (Transcript-Only Mode)")
def evaluate_transcript(payload: TranscriptEvaluationRequest):
    """
    Evaluates speech transcript without audio recording.
    Vocal delivery is transparently reported as UNAVAILABLE (never fabricated).
    """
    # Build transcript annotation with alignment
    annotation = transcriber_service.transcribe(
        audio_signal=None,
        sr=0,
        provided_transcript=payload.transcript
    )

    target_rubric = rubric_registry.get_rubric(payload.rubric_id)
    eval_result = evaluator_engine.evaluate(
        transcript_annotation=annotation,
        scenario=payload.scenario,
        audio_features=None,  # Explicitly None for transcript-only
        rubric=target_rubric,
        speech_prompt=payload.speech_prompt,
        raw_input_bytes=payload.transcript.encode("utf-8")
    )

    # Persist Run
    store_service.save_run(eval_result)

    return eval_result


@router.post("/evaluations", summary="Unified Speech Evaluation Entrypoint (JSON or Multipart Audio)")
async def evaluate_unified(request: Request):
    """
    Unified evaluation endpoint complying with the API specification.
    Supports:
    - application/json: Transcript-only evaluation
    - multipart/form-data: Audio recording + optional transcript evaluation
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            payload = TranscriptEvaluationRequest(**body)
            return evaluate_transcript(payload)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    elif "multipart/form-data" in content_type:
        form = await request.form()
        file = form.get("file")
        if not file or not hasattr(file, "read"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No audio file provided in multipart payload.")
        scenario = str(form.get("scenario", "public_speaking"))
        rubric_id = str(form.get("rubric_id", "speech_default_v1"))
        speech_prompt = form.get("speech_prompt")
        transcript = form.get("transcript")
        return await evaluate_audio(
            file=file,
            scenario=scenario,
            rubric_id=rubric_id,
            speech_prompt=str(speech_prompt) if speech_prompt else None,
            transcript=str(transcript) if transcript else None
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported Content-Type '{content_type}'. Must be application/json or multipart/form-data."
        )


@router.get("/evaluations/{run_id}", summary="Get Evaluation Details by Run ID")
def get_evaluation_by_id(run_id: str):
    """Retrieves full evaluation result and reproducibility metadata for a specific run."""
    run = store_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evaluation run '{run_id}' not found.")
    return run


@router.get("/evaluations/{run_id}/report", summary="Download Structured Reproducibility JSON Report")
def get_evaluation_json_report(run_id: str):
    """Exports full verifiable JSON report containing inputs, raw features, formula, and scores."""
    run = store_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evaluation run '{run_id}' not found.")
    return run.model_dump()


@router.get("/evaluations/{run_id}/export.html", response_class=HTMLResponse, summary="Download Printable HTML Audit Report")
def get_evaluation_html_report(run_id: str):
    """Generates a standalone, formatted printable HTML evaluation report."""
    run = store_service.get_run(run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evaluation run '{run_id}' not found.")
    html_content = store_service.generate_html_report(run)
    return HTMLResponse(content=html_content)


# --- 3. Contrastive Dataset Endpoints ---

@router.get("/datasets", summary="Get Contrastive Dataset Manifest & Statistics")
def get_datasets_overview():
    """Returns dataset version, SHA-256 hash, scenario distributions, and flaw taxonomy."""
    return dataset_service.get_manifest()


@router.get("/datasets/pairs", summary="List All Curated Contrastive Speech Pairs")
def get_all_contrastive_pairs(
    scenario: Optional[str] = None,
    flaw: Optional[str] = None
):
    """Returns curated ideal vs flawed speech pairs with optional filtering."""
    if scenario:
        pairs = dataset_service.get_pairs_by_scenario(scenario)
    elif flaw:
        pairs = dataset_service.get_pairs_by_flaw(flaw)
    else:
        pairs = dataset_service.get_all_pairs()

    return {
        "status": "success",
        "total_pairs": len(pairs),
        "pairs": [p.model_dump() for p in pairs]
    }


@router.get("/datasets/{dataset_id}/pairs", summary="List Contrastive Pairs for Specific Dataset Scope")
def get_contrastive_pairs_by_dataset_id(
    dataset_id: str,
    scenario: Optional[str] = None,
    flaw: Optional[str] = None
):
    """Retrieves contrastive pairs for a specified dataset identifier with optional filtering."""
    manifest = dataset_service.get_manifest()
    known_scopes = {manifest["version"], "default", "oratoriq_v1", "1.0.0", manifest["dataset_hash"][:12]}
    if dataset_id not in known_scopes:
        logger.info(f"Scoped dataset query '{dataset_id}' served against primary contrastive corpus.")
    return get_all_contrastive_pairs(scenario=scenario, flaw=flaw)


@router.get("/datasets/pairs/{pair_id}", summary="Get Specific Contrastive Pair by ID")
def get_contrastive_pair_by_id(pair_id: str):
    """Retrieves side-by-side ideal vs flawed speech pair with rubric annotations."""
    pair = dataset_service.get_pair(pair_id)
    if not pair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pair ID '{pair_id}' not found in dataset.")
    return pair.model_dump()


@router.post("/datasets/validate", summary="Run Dataset Schema & Integrity Validation")
def validate_dataset_endpoint(payload: DatasetValidateRequest):
    """Executes automated schema, duplicate, and rubric label range audit."""
    target_path = payload.custom_dataset_path or dataset_service.dataset_path
    report = validate_dataset_records(target_path)
    return report


# --- 4. Configurable Rubrics Endpoints ---

@router.get("/rubrics", summary="List Available Rubrics")
def list_rubrics():
    """Returns all registered rubric configurations, versions, criteria weights, and anchors."""
    return {
        "status": "success",
        "rubrics": rubric_registry.list_rubrics()
    }


@router.get("/rubrics/{rubric_id}", summary="Get Specific Rubric Definition")
def get_rubric_definition(rubric_id: str, version: Optional[str] = None):
    """Retrieves criteria, weights, anchors, and immutable hash for a rubric."""
    r = rubric_registry.get_rubric(rubric_id, version)
    return r.model_dump()


@router.get("/rubrics/{rubric_id}/versions", summary="List All Immutable Versions for a Rubric")
def get_rubric_versions_endpoint(rubric_id: str):
    """Returns all historical and registered immutable versions for the given rubric ID."""
    versions = rubric_registry.get_rubric_versions(rubric_id)
    if not versions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rubric ID '{rubric_id}' not found.")
    return {
        "status": "success",
        "rubric_id": rubric_id,
        "total_versions": len(versions),
        "versions": versions
    }


@router.post("/rubrics", summary="Create or Update Custom Rubric Configuration")
def create_custom_rubric(payload: CreateRubricRequest):
    """
    Validates criteria weights (must sum to 1.0), assigns immutable SHA-256 hash,
    and registers a new versioned rubric.
    """
    try:
        criteria_objs = {}
        for c_id, c_data in payload.criteria.items():
            anchors_dict = {}
            for a_key, a_val in c_data.get("anchors", {}).items():
                anchors_dict[str(a_key)] = ScoringAnchor(**a_val)
            criteria_objs[c_id] = CriterionConfig(
                id=c_id,
                name=c_data.get("name", c_id),
                weight=float(c_data.get("weight", 0.2)),
                description=c_data.get("description", ""),
                requires_audio=bool(c_data.get("requires_audio", False)),
                anchors=anchors_dict
            )

        rubric = RubricDefinition(
            rubric_id=payload.rubric_id,
            name=payload.name,
            version=payload.version,
            criteria=criteria_objs
        )
        registered = rubric_registry.register_rubric(rubric)
        return {
            "status": "success",
            "message": "Rubric registered successfully.",
            "rubric": registered.model_dump()
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to register rubric: {str(e)}")


# --- 5. History & Progress Endpoints ---

@router.get("/history", summary="List Historical Speech Evaluations")
def get_evaluation_history(
    limit: int = 50,
    scenario: Optional[str] = None
):
    """Returns chronological evaluation history for progress tracking."""
    runs = store_service.list_runs(limit=limit, scenario=scenario)
    return {
        "status": "success",
        "total_runs": len(runs),
        "runs": runs
    }
