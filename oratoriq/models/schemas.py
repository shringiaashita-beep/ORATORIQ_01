"""
Data models and schemas for OratorIQ Speech Evaluation and Coaching Platform.
"""

from typing import Dict, List, Optional, Any, Literal, Union
from pydantic import BaseModel, Field, field_validator


class SpeechScenario(str):
    PUBLIC_SPEAKING = "public_speaking"
    INTERVIEW_ANSWERS = "interview_answers"
    PERSUASIVE_PITCHES = "persuasive_pitches"
    PRESENTATION_DELIVERY = "presentation_delivery"
    ACADEMIC_EXPLANATIONS = "academic_explanations"

    ALL = [
        PUBLIC_SPEAKING,
        INTERVIEW_ANSWERS,
        PERSUASIVE_PITCHES,
        PRESENTATION_DELIVERY,
        ACADEMIC_EXPLANATIONS
    ]


class FlawCategory(str):
    WEAK_OPENING = "weak_opening"
    POOR_LOGICAL_STRUCTURE = "poor_logical_structure"
    EXCESSIVE_FILLER_WORDS = "excessive_filler_words"
    UNNECESSARY_REPETITION = "unnecessary_repetition"
    EXCESSIVELY_FAST_PACING = "excessively_fast_pacing"
    EXCESSIVELY_SLOW_PACING = "excessively_slow_pacing"
    POORLY_PLACED_PAUSES = "poorly_placed_pauses"
    WEAK_TRANSITIONS = "weak_transitions"
    UNCLEAR_ARTICULATION = "unclear_articulation"
    MONOTONOUS_VOCAL_DELIVERY = "monotonous_vocal_delivery"
    FAILURE_TO_ANSWER_QUESTION = "failure_to_answer_question"
    UNSUPPORTED_CLAIMS = "unsupported_claims"
    WEAK_OR_MISSING_CONCLUSION = "weak_or_missing_conclusion"


class SpeechSample(BaseModel):
    sample_id: str = Field(..., description="Unique sample identifier")
    pair_id: str = Field(..., description="Identifier of the contrastive pair")
    scenario: str = Field(..., description="Scenario category")
    language: str = Field(default="en", description="Spoken language ISO code")
    intended_audience: str = Field(..., description="Target audience description")
    communication_goal: str = Field(..., description="Goal of the speech")
    transcript: str = Field(..., min_length=10, description="Full speech transcript")
    audio_reference: Optional[str] = Field(default=None, description="Path or URI to audio recording if exists")
    example_type: Literal["ideal", "flawed"] = Field(..., description="Type of speech exemplar")
    flaw_categories: List[str] = Field(default_factory=list, description="List of observed flaws")
    severity: Literal["none", "minor", "moderate", "severe"] = Field(default="none")
    rubric_labels: Dict[str, int] = Field(..., description="1-5 rating per rubric criterion")
    annotation_rationale: str = Field(..., description="Detailed explanation of the rating")
    provenance: str = Field(..., description="Source: authored, public_domain, or synthetic")
    annotation_status: Literal["reviewed", "synthetic_verified", "draft"] = Field(default="reviewed")
    dataset_version: str = Field(default="1.0.0")

    @field_validator("transcript")
    @classmethod
    def validate_transcript(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Transcript cannot be empty.")
        return v.strip()


class ContrastivePair(BaseModel):
    pair_id: str = Field(..., description="Unique contrastive pair ID")
    scenario: str = Field(..., description="Communication scenario")
    intended_audience: str = Field(...)
    communication_goal: str = Field(...)
    ideal_sample: SpeechSample = Field(..., description="High-performing ideal speech")
    flawed_sample: SpeechSample = Field(..., description="Flawed speech exemplar")
    primary_flaw: str = Field(..., description="Primary flaw highlighted in the pair")
    flaw_severity: Literal["minor", "moderate", "severe"] = Field(...)
    contrastive_rationale: str = Field(..., description="Explanation of why this contrast is instructive")
    dataset_version: str = Field(default="1.0.0")


class ScoringAnchor(BaseModel):
    score: int = Field(..., ge=1, le=5)
    name: str = Field(..., description="e.g. Excellent, Strong, Developing")
    description: str = Field(...)
    observable_indicators: List[str] = Field(default_factory=list)


class CriterionConfig(BaseModel):
    id: str = Field(..., description="Unique criterion slug")
    name: str = Field(..., description="Display title")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight proportion (sum to 1.0)")
    description: str = Field(...)
    requires_audio: bool = Field(default=False, description="Whether criterion needs audio recording")
    anchors: Dict[str, ScoringAnchor] = Field(..., description="Keys '1'..'5' representing scoring anchors")


class RubricDefinition(BaseModel):
    rubric_id: str = Field(default="speech_default_v1")
    name: str = Field(default="OratorIQ Standard Speech Rubric")
    version: str = Field(default="1.0.0")
    rubric_hash: str = Field(default="")
    criteria: Dict[str, CriterionConfig] = Field(...)

    def validate_weights(self) -> bool:
        total_weight = sum(c.weight for c in self.criteria.values())
        return abs(total_weight - 1.0) < 1e-4


class AudioFeatures(BaseModel):
    duration_sec: float = Field(default=0.0, ge=0.0)
    speaking_rate_wpm: Optional[float] = Field(default=None, description="Words per minute")
    total_words: int = Field(default=0, ge=0)
    total_pauses: int = Field(default=0, ge=0)
    mean_pause_duration_sec: float = Field(default=0.0, ge=0.0)
    max_pause_duration_sec: float = Field(default=0.0, ge=0.0)
    silent_region_proportion: float = Field(default=0.0, ge=0.0, le=1.0)
    pitch_f0_mean_hz: Optional[float] = Field(default=None)
    pitch_f0_std_hz: Optional[float] = Field(default=None)
    pitch_semitone_range: Optional[float] = Field(default=None)
    is_monotonous: Optional[bool] = Field(default=None)
    rms_energy_mean: float = Field(default=0.0)
    dynamic_range_db: float = Field(default=0.0)
    clipping_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    snr_db_estimate: float = Field(default=0.0)
    is_audio_available: bool = Field(default=True)


class WordSpan(BaseModel):
    word: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    tag: Optional[str] = None  # e.g. "filler", "repetition", "key_point"


class SegmentSpan(BaseModel):
    id: int
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class TranscriptAnnotation(BaseModel):
    text: str
    segments: List[SegmentSpan] = Field(default_factory=list)
    words: List[WordSpan] = Field(default_factory=list)
    filler_words_detected: List[Dict[str, Any]] = Field(default_factory=list)
    repetitions_detected: List[Dict[str, Any]] = Field(default_factory=list)
    readability_flesch_score: float = Field(default=60.0)
    detected_language: str = Field(default="en")


class FeedbackItem(BaseModel):
    feedback_id: str
    rubric_criterion: str
    criterion_name: str
    observed_issue: str
    evidence_type: Literal["acoustic_measurement", "transcript_pattern", "structural_check", "contrastive_calibrator"]
    transcript_excerpt: Optional[str] = None
    timestamp_range: Optional[Dict[str, float]] = None
    measured_value: Optional[str] = None
    explanation: str
    recommended_action: str
    example_rewrite_or_exercise: str
    severity: Literal["high", "medium", "low", "positive"]
    evaluator_method: str
    limitations: str


class CriterionScoreResult(BaseModel):
    criterion_id: str
    criterion_name: str
    raw_rating: Optional[int] = Field(None, ge=1, le=5)
    normalized_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    weight: float
    status: Literal["evaluated", "unavailable", "skipped"] = "evaluated"
    reason: Optional[str] = None
    evidence_summary: str = ""
    scoring_anchor_matched: Optional[str] = None


class ContrastiveMatch(BaseModel):
    matched_pair_id: str
    scenario: str
    primary_flaw: str
    ideal_sample_id: str
    flawed_sample_id: str
    similarity_explanation: str
    contrastive_delta_analysis: str


class EvaluationResult(BaseModel):
    run_id: str
    created_at: str
    evaluation_mode: Literal["audio_plus_transcript", "transcript_only"]
    scenario: str
    speech_prompt: Optional[str] = None
    overall_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    grade: str = Field(default="N/A")
    coverage_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    coverage_percentage: float = Field(default=100.0)
    eligible_criteria_count: int = 5
    evaluated_criteria_count: int = 5
    missing_criteria: List[str] = Field(default_factory=list)
    criterion_scores: Dict[str, CriterionScoreResult]
    audio_features: Optional[AudioFeatures] = None
    transcript_annotation: TranscriptAnnotation
    feedback_items: List[FeedbackItem] = Field(default_factory=list)
    contrastive_matches: List[ContrastiveMatch] = Field(default_factory=list)
    reproducibility: Dict[str, Any]
