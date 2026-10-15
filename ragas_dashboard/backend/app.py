"""
FastAPI Server for Ragas Evaluation Studio.

Provides production-oriented REST endpoints for:
- Live RAG Metric Evaluations (Faithfulness, Relevance, Precision, Recall, Similarity, Aspect Critiques)
- Explicit Provenance & Evaluation Modes (Real, Heuristic, Unavailable)
- Domain Benchmark Suites & Aggregate Telemetry
- Document-Grounded Synthetic Testset Generation
- Process Health and Evaluation Readiness Probes
- Strict Pydantic Validation, Hardened CORS, and Centralized Error Handling
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from ragas_dashboard.backend.evaluator import (
    evaluate_rag_sample,
    is_ragas_real_supported,
    EvaluationMode
)
from ragas_dashboard.backend.synthetic_generator import generate_synthetic_testset
from ragas_dashboard.backend.benchmark_data import DOMAIN_BENCHMARKS, CONTRASTIVE_BENCHMARKS
from oratoriq.api.v1 import router as oratoriq_v1_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("oratoriq.api")

app = FastAPI(
    title="OratorIQ — Evidence-Based Speech Evaluation Platform API",
    description="Production-grade REST API for Audio Processing, Acoustic Feature Extraction, Contrastive Speech Evaluation, and Configurable Rubric Scoring.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount OratorIQ Version 1 Core Speech API
app.include_router(oratoriq_v1_router)

# Hardened CORS configuration
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    # Explicit localhost and local loopback origins for secure development
    allowed_origins = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Centralized Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append(f"{loc}: {err.get('msg', 'Invalid input')}")
    logger.warning(f"Validation failure on {request.url.path}: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error_type": "ValidationError",
            "message": "Request payload failed schema validation.",
            "details": errors
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception on {request.url.path}: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_type": "HTTPException",
            "message": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the full exception internally, but do not leak raw stack traces to client
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_type": "InternalServerError",
            "message": "An unexpected server error occurred during evaluation processing."
        }
    )

# --- Pydantic Schemas ---

class EvaluateSampleRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000, description="The user query or question evaluated.")
    answer: str = Field(..., min_length=1, max_length=10000, description="The RAG system's generated response.")
    contexts: Union[List[str], str] = Field(default_factory=list, description="List of retrieved contexts or newline-separated text.")
    ground_truth: Optional[str] = Field(default="", max_length=10000, description="Optional reference answer. Required for Context Recall and Semantic Similarity.")
    mode: Literal["auto", "heuristic", "real"] = Field(default="auto", description="Target evaluation mode.")
    custom_weights: Optional[Dict[str, float]] = Field(default=None, description="Optional custom weights for composite score.")

    @field_validator("question", "answer")
    @classmethod
    def validate_non_whitespace(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return v.strip()

    @field_validator("contexts")
    @classmethod
    def normalize_contexts(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            return [c.strip() for c in v.split("\n\n") if c.strip()]
        elif isinstance(v, list):
            return [str(c).strip() for c in v if str(c).strip()]
        return []

class BenchmarkEvaluateRequest(BaseModel):
    benchmark_id: str = Field(default="finance_10k", description="Identifier of the domain benchmark to evaluate.")
    mode: Literal["auto", "heuristic", "real"] = Field(default="auto", description="Evaluation execution mode.")

class SyntheticGenerateRequest(BaseModel):
    document_text: str = Field(..., min_length=50, max_length=100000, description="Source document text for chunking and test generation.")
    num_samples: int = Field(default=3, ge=1, le=10, description="Number of synthetic test cases to generate (1-10).")
    mode: Literal["auto", "heuristic", "real"] = Field(default="auto", description="Target generation mode.")

    @field_validator("document_text")
    @classmethod
    def validate_doc_content(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 50:
            raise ValueError("Document text must contain at least 50 non-whitespace characters.")
        return cleaned

class ContrastiveEvaluateRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000, description="The user query or prompt.")
    contexts: Union[List[str], str] = Field(default_factory=list, description="Retrieved contexts.")
    ground_truth: Optional[str] = Field(default="", max_length=10000, description="Optional reference answer.")
    candidate_a_name: str = Field(default="Model A (Ideal Grounded)", max_length=100)
    candidate_a_answer: str = Field(..., min_length=1, max_length=10000)
    candidate_b_name: str = Field(default="Model B (Flawed / Hallucinating)", max_length=100)
    candidate_b_answer: str = Field(..., min_length=1, max_length=10000)
    mode: Literal["auto", "heuristic", "real"] = Field(default="auto")

    @field_validator("question", "candidate_a_answer", "candidate_b_answer")
    @classmethod
    def validate_non_whitespace(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return v.strip()

    @field_validator("contexts")
    @classmethod
    def normalize_contexts(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            return [c.strip() for c in v.split("\n\n") if c.strip()]
        elif isinstance(v, list):
            return [str(c).strip() for c in v if str(c).strip()]
        return []

# --- API Endpoints ---

@app.get("/api/health", summary="Basic Process Liveness Probe")
def health_check():
    """Returns basic process liveness status and version info."""
    return {
        "status": "healthy",
        "service": "Ragas Evaluation Engine",
        "version": "2.1.0",
        "metrics_supported": [
            "faithfulness",
            "answer_relevance",
            "context_precision",
            "context_recall",
            "semantic_similarity",
            "aspect_critiques"
        ]
    }

@app.get("/api/ready", summary="Evaluation Readiness Probe")
def readiness_check():
    """
    Distinguishes basic process health from actual evaluation readiness.
    Checks availability of Ragas library, optional dependencies, and credentials.
    """
    real_supported, reason = is_ragas_real_supported()
    return {
        "status": "ready",
        "evaluation_capabilities": {
            "heuristic_engine": {
                "available": True,
                "status": "OPERATIONAL",
                "description": "Deterministic rule-based approximations for offline evaluation without external credentials."
            },
            "real_ragas_llm_engine": {
                "available": real_supported,
                "status": "OPERATIONAL" if real_supported else "DEPENDENCIES_MISSING",
                "detail": reason
            }
        },
        "default_mode": "real" if real_supported else "heuristic"
    }

@app.get("/api/benchmarks", summary="List Available Domain Benchmarks")
def get_benchmarks():
    """Returns available pre-loaded domain benchmarks and their test samples."""
    overview = []
    for b_id, b in DOMAIN_BENCHMARKS.items():
        overview.append({
            "id": b["id"],
            "title": b["title"],
            "category": b["category"],
            "description": b["description"],
            "sample_count": len(b.get("samples", [])),
            "samples": b.get("samples", [])
        })
    return {"status": "success", "benchmarks": overview}

@app.post("/api/evaluate/sample", summary="Evaluate a Single RAG Sample")
def evaluate_sample(payload: EvaluateSampleRequest):
    """
    Evaluates a single RAG sample across Ragas core dimensions.
    Returns per-metric results with explicit evaluation mode, scale, provenance, and diagnostic breakdown.
    """
    eval_result = evaluate_rag_sample(
        question=payload.question,
        contexts=payload.contexts,
        answer=payload.answer,
        ground_truth=payload.ground_truth or "",
        mode=payload.mode,
        custom_weights=payload.custom_weights
    )

    return {
        "status": "success",
        "schema_version": "2.1.0",
        "sample": {
            "question": payload.question,
            "answer": payload.answer,
            "contexts_count": len(payload.contexts),
            "ground_truth_provided": bool(payload.ground_truth and payload.ground_truth.strip())
        },
        "evaluation": eval_result
    }

@app.post("/api/evaluate/benchmark", summary="Evaluate Full Domain Benchmark Suite")
def evaluate_benchmark(payload: BenchmarkEvaluateRequest):
    """
    Evaluates all samples in a selected domain benchmark and returns aggregate metrics.
    """
    if payload.benchmark_id not in DOMAIN_BENCHMARKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark dataset '{payload.benchmark_id}' not found."
        )

    benchmark = DOMAIN_BENCHMARKS[payload.benchmark_id]
    samples = benchmark.get("samples", [])
    if not samples:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark dataset '{payload.benchmark_id}' contains no test samples."
        )

    sample_results = []
    metric_accumulators = {
        "faithfulness": {"sum": 0.0, "count": 0},
        "answer_relevance": {"sum": 0.0, "count": 0},
        "context_precision": {"sum": 0.0, "count": 0},
        "context_recall": {"sum": 0.0, "count": 0},
        "semantic_similarity": {"sum": 0.0, "count": 0}
    }
    composite_sum = 0.0
    composite_count = 0

    for s in samples:
        res = evaluate_rag_sample(
            question=s["question"],
            contexts=s.get("contexts", []),
            answer=s["answer"],
            ground_truth=s.get("ground_truth", ""),
            mode=payload.mode
        )

        sample_entry = {
            "id": s.get("id", "SAMPLE"),
            "question": s["question"],
            "type": s.get("type", "STANDARD"),
            "composite_score": res["composite_score"],
            "grade": res["grade"],
            "metrics": {},
            "diagnosis": res["diagnosis"]
        }

        for m_name, m_data in res["metrics"].items():
            if m_name in metric_accumulators:
                score_val = m_data.get("score")
                sample_entry["metrics"][m_name] = score_val
                if score_val is not None:
                    metric_accumulators[m_name]["sum"] += score_val
                    metric_accumulators[m_name]["count"] += 1

        if res["composite_score"] is not None:
            composite_sum += res["composite_score"]
            composite_count += 1

        sample_results.append(sample_entry)

    aggregates = {
        "mean_composite_score": round(composite_sum / max(1, composite_count), 1) if composite_count > 0 else None,
        "mean_faithfulness": round(metric_accumulators["faithfulness"]["sum"] / max(1, metric_accumulators["faithfulness"]["count"]), 3) if metric_accumulators["faithfulness"]["count"] > 0 else None,
        "mean_answer_relevance": round(metric_accumulators["answer_relevance"]["sum"] / max(1, metric_accumulators["answer_relevance"]["count"]), 3) if metric_accumulators["answer_relevance"]["count"] > 0 else None,
        "mean_context_precision": round(metric_accumulators["context_precision"]["sum"] / max(1, metric_accumulators["context_precision"]["count"]), 3) if metric_accumulators["context_precision"]["count"] > 0 else None,
        "mean_context_recall": round(metric_accumulators["context_recall"]["sum"] / max(1, metric_accumulators["context_recall"]["count"]), 3) if metric_accumulators["context_recall"]["count"] > 0 else None,
        "mean_semantic_similarity": round(metric_accumulators["semantic_similarity"]["sum"] / max(1, metric_accumulators["semantic_similarity"]["count"]), 3) if metric_accumulators["semantic_similarity"]["count"] > 0 else None,
    }

    return {
        "status": "success",
        "schema_version": "2.1.0",
        "benchmark_id": benchmark["id"],
        "benchmark_title": benchmark["title"],
        "total_samples_evaluated": len(sample_results),
        "aggregates": aggregates,
        "sample_results": sample_results
    }

@app.post("/api/synthetic/generate", summary="Generate Document-Grounded Synthetic Testset")
def generate_synthetic(payload: SyntheticGenerateRequest):
    """
    Transforms user-supplied text into grounded test cases with supporting context and reference ground truth.
    Reports the actual generation mode (real vs heuristic template fallback).
    """
    try:
        result = generate_synthetic_testset(
            document_text=payload.document_text,
            requested_count=payload.num_samples,
            mode=payload.mode
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Synthetic generation error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Synthetic generation pipeline error.")

# --- Contrastive Evaluation (A/B) Endpoints ---

@app.get("/api/contrastive/scenarios", summary="List Pre-loaded Contrastive Evaluation Scenarios")
def get_contrastive_scenarios():
    """
    Returns curated enterprise scenarios contrasting Ideal Grounded RAG against Flawed/Hallucinated RAG.
    """
    scenarios = []
    for s_id, s in CONTRASTIVE_BENCHMARKS.items():
        scenarios.append({
            "id": s["id"],
            "title": s["title"],
            "domain": s.get("domain", "General"),
            "question": s["question"],
            "contexts": s["contexts"],
            "ground_truth": s["ground_truth"],
            "candidate_a": s["candidate_a"],
            "candidate_b": s["candidate_b"]
        })
    return {"status": "success", "total_scenarios": len(scenarios), "scenarios": scenarios}

@app.post("/api/evaluate/contrastive", summary="Evaluate Model A vs Model B Side-by-Side")
def evaluate_contrastive(payload: ContrastiveEvaluateRequest):
    """
    Runs unified Ragas evaluation simultaneously on two candidate responses (A vs B).
    Computes comparative metrics, quality delta, hallucination disparity, and overlay telemetry.
    """
    eval_a = evaluate_rag_sample(
        question=payload.question,
        contexts=payload.contexts,
        answer=payload.candidate_a_answer,
        ground_truth=payload.ground_truth or "",
        mode=payload.mode
    )

    eval_b = evaluate_rag_sample(
        question=payload.question,
        contexts=payload.contexts,
        answer=payload.candidate_b_answer,
        ground_truth=payload.ground_truth or "",
        mode=payload.mode
    )

    score_a = eval_a.get("composite_score")
    score_b = eval_b.get("composite_score")
    delta_score = round(score_a - score_b, 1) if (score_a is not None and score_b is not None) else None

    faith_a = eval_a["metrics"]["faithfulness"].get("score") or 0.0
    faith_b = eval_b["metrics"]["faithfulness"].get("score") or 0.0
    faith_delta = round((faith_a - faith_b) * 100, 1)

    hallucinations_a = eval_a["metrics"]["faithfulness"].get("hallucination_count", 0)
    hallucinations_b = eval_b["metrics"]["faithfulness"].get("hallucination_count", 0)

    if delta_score is not None:
        if delta_score > 0:
            winner = payload.candidate_a_name
            verdict = f"{payload.candidate_a_name} outperforms {payload.candidate_b_name} by +{delta_score}% composite health, showing +{faith_delta}% higher faithfulness grounding with {hallucinations_b - hallucinations_a} fewer hallucinated claims."
        elif delta_score < 0:
            winner = payload.candidate_b_name
            verdict = f"{payload.candidate_b_name} outperforms {payload.candidate_a_name} by +{abs(delta_score)}% composite health points."
        else:
            winner = "Equivalent Performance"
            verdict = "Both candidate responses achieve equal composite health scores."
    else:
        winner = "Undetermined"
        verdict = "Insufficient metrics available to compute contrastive delta."

    return {
        "status": "success",
        "schema_version": "2.1.0",
        "contrastive_summary": {
            "winner": winner,
            "delta_composite_score": delta_score,
            "faithfulness_delta_pct": faith_delta,
            "hallucination_disparity": hallucinations_b - hallucinations_a,
            "verdict": verdict
        },
        "candidate_a": {
            "name": payload.candidate_a_name,
            "answer": payload.candidate_a_answer,
            "evaluation": eval_a
        },
        "candidate_b": {
            "name": payload.candidate_b_name,
            "answer": payload.candidate_b_answer,
            "evaluation": eval_b
        },
        "radar_overlay": {
            "axes": ["faithfulness", "relevance", "precision", "recall", "similarity"],
            "candidate_a": eval_a["radar_data"],
            "candidate_b": eval_b["radar_data"]
        }
    }

# --- Repository Codebase Explorer Endpoints ---
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".css", ".html", ".toml", ".md", ".yml", ".yaml", ".json", ".txt", ".bat", ".sh"
}

IGNORED_DIRS = {
    ".git", ".github", ".pytest_cache", "__pycache__", ".venv", "venv", "node_modules", ".cursor", ".claude"
}

def detect_language(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".css": "css",
        ".html": "html",
        ".toml": "toml",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
        ".bat": "bat"
    }
    return mapping.get(ext, "text")

@app.get("/api/repo/tree", summary="List Repository Source Code Tree")
def get_repository_tree():
    """
    Returns curated file hierarchy of the Ragas framework, Studio backend, tests, and examples.
    """
    file_entries = []

    # Target key subdirectories
    target_dirs = [
        ("Core Ragas Metrics", "src/ragas/metrics"),
        ("Core Ragas Engine", "src/ragas"),
        ("Studio Backend", "ragas_dashboard/backend"),
        ("Studio Frontend", "ragas_dashboard/frontend"),
        ("Automated Tests", "tests"),
        ("Examples & Scenarios", "examples"),
        ("Documentation", "docs")
    ]

    for category, rel_dir in target_dirs:
        abs_dir = os.path.join(REPO_ROOT, rel_dir)
        if not os.path.exists(abs_dir):
            continue

        for root, dirs, files in os.walk(abs_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            
            for f in sorted(files):
                ext = os.path.splitext(f)[1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                abs_file = os.path.join(root, f)
                rel_file = os.path.relpath(abs_file, REPO_ROOT).replace("\\", "/")
                
                # Exclude metrics sub-listing when walking parent src/ragas to avoid duplicate categorization
                if category == "Core Ragas Engine" and rel_file.startswith("src/ragas/metrics/"):
                    continue

                file_entries.append({
                    "category": category,
                    "filename": f,
                    "path": rel_file,
                    "size_bytes": os.path.getsize(abs_file),
                    "language": detect_language(f)
                })

    # Add key root files
    root_files = ["pyproject.toml", "README.md", "run_dashboard.py", "start_dashboard.bat", "mkdocs.yml"]
    for rf in root_files:
        abs_rf = os.path.join(REPO_ROOT, rf)
        if os.path.exists(abs_rf):
            file_entries.append({
                "category": "Project Configuration",
                "filename": rf,
                "path": rf,
                "size_bytes": os.path.getsize(abs_rf),
                "language": detect_language(rf)
            })

    return {
        "status": "success",
        "total_files": len(file_entries),
        "files": file_entries
    }

@app.get("/api/repo/file", summary="Fetch File Content for Code Viewer")
def get_repository_file(path: str):
    """
    Safely retrieves the content of a source file within the repository for in-app code inspection.
    Enforces strict path traversal boundaries and size caps.
    """
    clean_path = path.strip().replace("\\", "/").lstrip("/")
    abs_target = os.path.realpath(os.path.join(REPO_ROOT, clean_path))

    # Path traversal protection
    if not abs_target.startswith(os.path.realpath(REPO_ROOT)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path: Directory traversal not permitted.")

    # Disallow hidden files or credentials
    parts = clean_path.split("/")
    if any(p.startswith(".") for p in parts if p not in (".", "..")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to hidden or dotfiles is restricted.")

    if not os.path.isfile(abs_target):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File '{clean_path}' not found in repository.")

    ext = os.path.splitext(abs_target)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File extension '{ext}' is not supported for in-browser viewing.")

    file_size = os.path.getsize(abs_target)
    if file_size > 500000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds maximum in-browser display limit (500KB).")

    try:
        with open(abs_target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        lines = content.splitlines()
        return {
            "status": "success",
            "path": clean_path,
            "filename": os.path.basename(abs_target),
            "language": detect_language(abs_target),
            "size_bytes": file_size,
            "line_count": len(lines),
            "content": content
        }
    except Exception as e:
        logger.error(f"Error reading repository file {clean_path}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to read file contents.")

# Mount static frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    logger.warning(f"Frontend directory not found at {FRONTEND_DIR}")
