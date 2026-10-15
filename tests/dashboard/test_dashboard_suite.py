"""
Automated Comprehensive Test Suite for Ragas Evaluation Studio.

Validates:
- Health and Readiness Probes
- Strict Evaluation Integrity (Explicit modes, No fake 100% on missing ground truth)
- Error Isolation & Division-by-Zero Protection
- Pydantic Validation & Input Sanitization
- Domain Benchmarks & Aggregate Scoring
- Document-Grounded Synthetic Testset Generation
- Hardened CORS Headers & Static File Routing
"""

import pytest
from fastapi.testclient import TestClient

from ragas_dashboard.backend.app import app
from ragas_dashboard.backend.evaluator import (
    evaluate_rag_sample,
    evaluate_faithfulness,
    evaluate_context_recall,
    evaluate_semantic_similarity,
    split_into_claims,
    EvaluationMode,
    MetricStatus
)
from ragas_dashboard.backend.synthetic_generator import generate_synthetic_testset, chunk_document

@pytest.fixture
def client():
    return TestClient(app)

# --- 1. Liveness & Readiness Tests ---

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Ragas Evaluation Engine"
    assert "metrics_supported" in data
    assert "faithfulness" in data["metrics_supported"]

def test_readiness_check(client):
    response = client.get("/api/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "evaluation_capabilities" in data
    assert "heuristic_engine" in data["evaluation_capabilities"]
    assert data["evaluation_capabilities"]["heuristic_engine"]["status"] == "OPERATIONAL"

# --- 2. Benchmarks Exploration Tests ---

def test_get_benchmarks(client):
    response = client.get("/api/benchmarks")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["benchmarks"]) >= 2
    ids = [b["id"] for b in data["benchmarks"]]
    assert "finance_10k" in ids

def test_evaluate_benchmark_success(client):
    response = client.post("/api/evaluate/benchmark", json={"benchmark_id": "finance_10k", "mode": "heuristic"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["benchmark_id"] == "finance_10k"
    assert "aggregates" in data
    assert data["aggregates"]["mean_composite_score"] is not None
    assert len(data["sample_results"]) >= 3

def test_evaluate_benchmark_unknown_id(client):
    response = client.post("/api/evaluate/benchmark", json={"benchmark_id": "non_existent_suite_id"})
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()

# --- 3. Evaluation Integrity & Missing Input Defensibility Tests ---

def test_evaluate_sample_complete(client):
    payload = {
        "question": "What was Cloud Infrastructure revenue growth?",
        "contexts": [
            "Cloud Infrastructure segment revenue reached $14.2 billion for fiscal year 2025, representing a 28% year-over-year increase compared to $11.1 billion in 2024."
        ],
        "answer": "Cloud Infrastructure grew 28% year-over-year to $14.2 billion in fiscal 2025.",
        "ground_truth": "Cloud Infrastructure revenue increased by 28% year-over-year to $14.2 billion.",
        "mode": "heuristic"
    }
    response = client.post("/api/evaluate/sample", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "evaluation" in data
    ev = data["evaluation"]

    assert ev["evaluation_mode"] == "heuristic"
    assert ev["composite_score"] is not None
    assert ev["composite_score"] > 80.0
    assert ev["grade"] in ("A+", "A")

    # Verify per-metric results
    m = ev["metrics"]
    assert m["faithfulness"]["score"] == 1.0
    assert m["faithfulness"]["mode"] == "heuristic"
    assert m["answer_relevance"]["score"] > 0.7
    assert m["context_precision"]["score"] == 1.0
    assert m["context_recall"]["score"] == 1.0
    assert m["semantic_similarity"]["score"] > 0.7

def test_evaluate_sample_missing_ground_truth_integrity(client):
    """
    CRITICAL EVALUATION INTEGRITY REQUIREMENT:
    When ground_truth is not supplied, Context Recall and Semantic Similarity
    MUST be marked UNAVAILABLE with score None, NOT falsely reported as 1.0 or 100%!
    """
    payload = {
        "question": "What was the capital expenditure?",
        "contexts": ["The company spent $4.9 billion on data center infrastructure."],
        "answer": "The company invested $4.9 billion on data center infrastructure.",
        "ground_truth": "",  # Empty reference answer!
        "mode": "heuristic"
    }
    response = client.post("/api/evaluate/sample", json=payload)
    assert response.status_code == 200
    data = response.json()
    ev = data["evaluation"]
    m = ev["metrics"]

    # Context Recall must be UNAVAILABLE with None score
    assert m["context_recall"]["score"] is None
    assert m["context_recall"]["mode"] == EvaluationMode.UNAVAILABLE.value
    assert m["context_recall"]["status"] == MetricStatus.UNAVAILABLE.value
    assert "ground_truth" in m["context_recall"]["reason"]

    # Semantic Similarity must be UNAVAILABLE with None score
    assert m["semantic_similarity"]["score"] is None
    assert m["semantic_similarity"]["mode"] == EvaluationMode.UNAVAILABLE.value
    assert m["semantic_similarity"]["status"] == MetricStatus.UNAVAILABLE.value

    # Radar data should have None for unavailable metrics
    assert ev["radar_data"]["recall"] is None
    assert ev["radar_data"]["similarity"] is None

    # Composite score must normalize over available metrics only
    assert ev["composite_score"] is not None

def test_evaluate_sample_empty_contexts(client):
    """Verifies that empty contexts do not cause division-by-zero or crash."""
    payload = {
        "question": "Where is the data stored?",
        "contexts": [],
        "answer": "Data is encrypted in European transit hubs.",
        "ground_truth": "Stored in transit hubs."
    }
    response = client.post("/api/evaluate/sample", json=payload)
    assert response.status_code == 200
    data = response.json()
    ev = data["evaluation"]
    assert ev["metrics"]["faithfulness"]["score"] == 0.0
    assert ev["metrics"]["context_precision"]["score"] == 0.0

# --- 4. Input Validation & Security Tests ---

def test_validation_empty_question(client):
    response = client.post("/api/evaluate/sample", json={
        "question": "   ",
        "answer": "Valid answer",
        "contexts": ["Valid context"]
    })
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert data["error_type"] == "ValidationError"

def test_validation_empty_answer(client):
    response = client.post("/api/evaluate/sample", json={
        "question": "Valid question?",
        "answer": "",
        "contexts": ["Valid context"]
    })
    assert response.status_code == 422

def test_validation_excessive_payload_length(client):
    response = client.post("/api/evaluate/sample", json={
        "question": "Q" * 6000,  # Exceeds max_length=5000
        "answer": "Valid answer",
        "contexts": ["Valid context"]
    })
    assert response.status_code == 422

# --- 5. Synthetic Generation Tests ---

def test_synthetic_generation_valid(client):
    doc = (
        "Distributed query planning in OmniSync decouples partition discovery from shard execution. "
        "When a query is initiated, the coordinator queries the metadata catalog to identify all nodes housing active partitions. "
        "Nodes execute localized map reductions and push intermediate aggregates back through an asynchronous RPC channel. "
        "This architecture limits cross-region latency to under 45 milliseconds."
    )
    response = client.post("/api/synthetic/generate", json={
        "document_text": doc,
        "num_samples": 3,
        "mode": "heuristic"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["generation_mode"] == "heuristic_template"
    assert len(data["testset"]) == 3

    for item in data["testset"]:
        assert item["test_id"].startswith("SYNTH-")
        assert len(item["synthesized_question"]) > 10
        assert len(item["extracted_context"]) >= 1
        assert len(item["reference_ground_truth"]) > 5
        assert "source_provenance" in item
        assert item["source_provenance"]["generator_mode"] == "heuristic_template"

def test_synthetic_generation_too_short(client):
    response = client.post("/api/synthetic/generate", json={
        "document_text": "Too short snippet.",
        "num_samples": 2
    })
    assert response.status_code == 422

# --- 6. Hardened CORS & Static File Routing Tests ---

def test_cors_preflight(client):
    headers = {
        "Origin": "http://127.0.0.1:8000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    response = client.options("/api/evaluate/sample", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:8000"

def test_static_index_serving(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "ORATORIQ" in response.text.upper()

def test_static_css_serving(client):
    response = client.get("/css/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers.get("content-type", "")

# --- 7. Unit Evaluator Claim Splitting & Hallucination Tests ---

def test_evaluator_claim_splitting():
    text = "OmniSync latency is under 45ms. It uses distributed RPC. High density."
    claims = split_into_claims(text)
    assert len(claims) == 3
    assert "45ms" in claims[0]

def test_evaluator_hallucination_detection():
    answer = "The company allocated $4.9 billion to data center infrastructure. The forecasted 2026 budget is $7.5 billion."
    contexts = ["The company allocated $4.9 billion to data center infrastructure."]
    result = evaluate_faithfulness(answer, contexts)
    assert result["total_claims"] == 2
    assert result["supported_claims"] == 1
    assert result["hallucination_count"] == 1
    assert result["score"] == 0.5

# --- 8. In-App Repository Codebase Explorer Tests ---

def test_repo_tree_endpoint(client):
    response = client.get("/api/repo/tree")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_files"] >= 15
    paths = [f["path"] for f in data["files"]]
    assert "src/ragas/metrics/_faithfulness.py" in paths
    assert "pyproject.toml" in paths

def test_repo_file_endpoint_valid(client):
    response = client.get("/api/repo/file?path=src/ragas/metrics/_faithfulness.py")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["filename"] == "_faithfulness.py"
    assert data["language"] == "python"
    assert data["line_count"] > 50
    assert len(data["content"]) > 500

def test_repo_file_directory_traversal_blocked(client):
    response = client.get("/api/repo/file?path=../../windows/system32/cmd.exe")
    assert response.status_code == 400
    data = response.json()
    assert "traversal" in data["message"].lower()

def test_repo_file_hidden_file_blocked(client):
    response = client.get("/api/repo/file?path=.git/config")
    assert response.status_code == 403
    data = response.json()
    assert "restricted" in data["message"].lower()

def test_repo_file_not_found(client):
    response = client.get("/api/repo/file?path=src/non_existent_file.py")
    assert response.status_code == 404

# --- 9. Contrastive A/B Grounding & Evaluation Tests ---

def test_contrastive_scenarios_endpoint(client):
    response = client.get("/api/contrastive/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_scenarios"] >= 3
    scenarios = data["scenarios"]
    assert any(s["id"] == "fin_capex_contrastive" for s in scenarios)
    first = scenarios[0]
    assert "candidate_a" in first
    assert "candidate_b" in first
    assert "contexts" in first
    assert len(first["contexts"]) > 0

def test_contrastive_evaluate_endpoint(client):
    payload = {
        "question": "What is the compute allocation and power capacity?",
        "contexts": [
            "We provisioned 12,000 H100 GPUs drawing 8.5 MW peak load at the Dallas datacenter."
        ],
        "ground_truth": "12,000 H100 GPUs and 8.5 MW peak load in Dallas.",
        "candidate_a_name": "Candidate A (Grounded)",
        "candidate_a_answer": "We provisioned 12,000 H100 GPUs drawing 8.5 MW peak load at the Dallas datacenter.",
        "candidate_b_name": "Candidate B (Flawed/Hallucinated)",
        "candidate_b_answer": "We provisioned 12,000 H100 GPUs drawing 8.5 MW peak load at Dallas. We also opened a 20 MW campus in Iceland."
    }
    response = client.post("/api/evaluate/contrastive", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "contrastive_summary" in data
    summary = data["contrastive_summary"]
    assert "Candidate A" in summary["winner"]
    assert summary["faithfulness_delta_pct"] > 0
    assert summary["hallucination_disparity"] >= 1

    # Check candidates structure
    assert "candidate_a" in data
    assert "candidate_b" in data
    assert data["candidate_a"]["evaluation"]["metrics"]["faithfulness"]["score"] == 1.0
    assert data["candidate_b"]["evaluation"]["metrics"]["faithfulness"]["score"] < 1.0
    assert data["candidate_b"]["evaluation"]["metrics"]["faithfulness"]["hallucination_count"] >= 1

    # Check radar telemetry
    assert "radar_overlay" in data
    assert len(data["radar_overlay"]["axes"]) == 5
    assert "faithfulness" in data["radar_overlay"]["candidate_a"]
    assert "relevance" in data["radar_overlay"]["candidate_b"]


def test_contrastive_validation_missing_candidate(client):
    payload = {
        "question": "What is the speed?",
        "contexts": ["Speed is 100 mph."],
        "candidate_a_name": "Candidate A",
        "candidate_a_answer": "Speed is 100 mph."
        # missing candidate_b_answer
    }
    response = client.post("/api/evaluate/contrastive", json=payload)
    assert response.status_code == 422


