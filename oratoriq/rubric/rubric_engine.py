"""
Rubric Definition, Versioning, and Score Aggregation Engine for OratorIQ.
"""

import hashlib
import json
from typing import Dict, List, Optional, Tuple, Any
from oratoriq.models.schemas import (
    RubricDefinition,
    CriterionConfig,
    ScoringAnchor,
    CriterionScoreResult
)


def compute_rubric_hash(criteria: Dict[str, CriterionConfig], version: str) -> str:
    """Computes a deterministic SHA-256 hash of the rubric configuration."""
    canonical_rep = {
        "version": version,
        "criteria": {
            k: {
                "id": v.id,
                "name": v.name,
                "weight": round(v.weight, 4),
                "requires_audio": v.requires_audio,
                "anchors": {
                    s: {"score": a.score, "name": a.name, "description": a.description}
                    for s, a in sorted(v.anchors.items())
                }
            }
            for k, v in sorted(criteria.items())
        }
    }
    dumped = json.dumps(canonical_rep, sort_keys=True)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]


def get_default_rubric() -> RubricDefinition:
    """Returns the standard 5-axis OratorIQ speech evaluation rubric."""
    criteria = {
        "content_and_relevance": CriterionConfig(
            id="content_and_relevance",
            name="Content & Relevance",
            weight=0.25,
            description="Evaluates responsiveness to the scenario, depth of subject matter, factual premise support, and relevance.",
            requires_audio=False,
            anchors={
                "1": ScoringAnchor(
                    score=1,
                    name="Substantial Improvement Needed",
                    description="Fails to address core topic; excessive tangents; unsupported claims without reasoning.",
                    observable_indicators=["Off-topic statements", "Absence of core message", "Zero substantiation"]
                ),
                "2": ScoringAnchor(
                    score=2,
                    name="Below Target Standard",
                    description="Superficially touches the topic; weak supporting evidence; generic platitudes.",
                    observable_indicators=["Vague generalizations", "Question partially answered", "Missing depth"]
                ),
                "3": ScoringAnchor(
                    score=3,
                    name="Developing",
                    description="Directly addresses the prompt; provides basic examples; points are mostly relevant.",
                    observable_indicators=["Satisfactory coverage", "Minor tangential drift", "Adequate examples"]
                ),
                "4": ScoringAnchor(
                    score=4,
                    name="Strong",
                    description="Thorough and tailored coverage; insightful examples; clear alignment with audience and goal.",
                    observable_indicators=["Tailored messaging", "Concrete supporting facts", "High relevance"]
                ),
                "5": ScoringAnchor(
                    score=5,
                    name="Excellent",
                    description="Compelling, deeply insightful treatment; flawless topic relevance; persuasive substance throughout.",
                    observable_indicators=["Exceptional depth", "Authoritative framing", "Memorable takeaways"]
                )
            }
        ),
        "structure_and_coherence": CriterionConfig(
            id="structure_and_coherence",
            name="Structure & Coherence",
            weight=0.20,
            description="Assesses structural progression: captivating opening, roadmap, logical transitions, and purposeful conclusion.",
            requires_audio=False,
            anchors={
                "1": ScoringAnchor(
                    score=1,
                    name="Substantial Improvement Needed",
                    description="Disorganized thoughts; missing opening or conclusion; abrupt and disjointed topic jumps.",
                    observable_indicators=["No clear beginning or end", "Chaotic thought progression", "No transitions"]
                ),
                "2": ScoringAnchor(
                    score=2,
                    name="Below Target Standard",
                    description="Basic sequence present but difficult to follow; abrupt transitions; trailing conclusion.",
                    observable_indicators=["Abrupt transitions", "Weak introduction hook", "Abrupt ending"]
                ),
                "3": ScoringAnchor(
                    score=3,
                    name="Developing",
                    description="Identifiable opening, body, and conclusion; simple chronological or list transitions.",
                    observable_indicators=["Standard intro/outro", "Adequate signposting", "Followable sequence"]
                ),
                "4": ScoringAnchor(
                    score=4,
                    name="Strong",
                    description="Well-engineered logical arc; seamless thematic transitions; crisp thesis reinforcement in closing.",
                    observable_indicators=["Clear preview roadmap", "Smooth transition bridges", "Reinforced thesis"]
                ),
                "5": ScoringAnchor(
                    score=5,
                    name="Excellent",
                    description="Masterclass rhetorical architecture; compelling narrative arc; memorable, resonant call to action.",
                    observable_indicators=["Masterful hook", "Symphonic conceptual flow", "Powerful synthesis"]
                )
            }
        ),
        "fluency_and_pacing": CriterionConfig(
            id="fluency_and_pacing",
            name="Fluency & Pacing",
            weight=0.20,
            description="Evaluates cadence, speaking rate (ideal 130-160 WPM), purposeful pause placement, and filler word control.",
            requires_audio=False,
            anchors={
                "1": ScoringAnchor(
                    score=1,
                    name="Substantial Improvement Needed",
                    description="Severe disfluencies; extreme filler frequency (>8%); halting pauses or unintelligible rush.",
                    observable_indicators=["Severe filler density", "Halting unnatural stops", "WPM <100 or >195"]
                ),
                "2": ScoringAnchor(
                    score=2,
                    name="Below Target Standard",
                    description="Distracting filler words (5-8%); noticeable pacing surges or awkward mid-clause pauses.",
                    observable_indicators=["Frequent 'um'/'like'", "Rushed sections", "Mid-sentence hesitations"]
                ),
                "3": ScoringAnchor(
                    score=3,
                    name="Developing",
                    description="Steady rhythm; moderate filler presence (2-4%); pauses generally correspond to phrase endings.",
                    observable_indicators=["Moderate filler rate", "Acceptable WPM (115-175)", "Occasional hesitation"]
                ),
                "4": ScoringAnchor(
                    score=4,
                    name="Strong",
                    description="Fluent and comfortable flow; minimal fillers (<2%); deliberate pauses used for emphasis.",
                    observable_indicators=["Controlled pacing (130-160 WPM)", "Rare fillers", "Intentional dramatic pauses"]
                ),
                "5": ScoringAnchor(
                    score=5,
                    name="Excellent",
                    description="Pristine fluency; zero distracting fillers; rhythmic mastery using pauses as rhetorical instruments.",
                    observable_indicators=["Flawless cadence", "Zero noticeable fillers", "Rhetorically calibrated pauses"]
                )
            }
        ),
        "vocal_delivery": CriterionConfig(
            id="vocal_delivery",
            name="Vocal Delivery",
            weight=0.20,
            description="Evaluates pitch modulation, vocal variety, dynamic range, vocal energy, and absence of flat monotony.",
            requires_audio=True,
            anchors={
                "1": ScoringAnchor(
                    score=1,
                    name="Substantial Improvement Needed",
                    description="Extremely flat monotone delivery; barely audible or clipping/strained vocal projection.",
                    observable_indicators=["Pitch semitone range < 1.5", "Flat robotic pitch contour", "Severe audio clipping/mumble"]
                ),
                "2": ScoringAnchor(
                    score=2,
                    name="Below Target Standard",
                    description="Monotonous inflection; little dynamic range; speech sounds read rather than naturally expressed.",
                    observable_indicators=["Low pitch variation", "Muted energy", "Unvarying volume"]
                ),
                "3": ScoringAnchor(
                    score=3,
                    name="Developing",
                    description="Natural vocal inflection; adequate projection; occasional tonal emphasis on key words.",
                    observable_indicators=["Natural conversational pitch", "Audible dynamics", "Moderate vocal variety"]
                ),
                "4": ScoringAnchor(
                    score=4,
                    name="Strong",
                    description="Dynamic vocal color; pitch modulates to signal enthusiasm and question inflection; confident projection.",
                    observable_indicators=["Wide pitch range (>3.5 semitones)", "Dynamic loudness contrast", "Engaging warmth"]
                ),
                "5": ScoringAnchor(
                    score=5,
                    name="Excellent",
                    description="Virtuosic vocal command; emotive inflection, varied timbre, and pitch contour captivating listener attention.",
                    observable_indicators=["Exemplary pitch dynamism", "Vibrant expressive range", "Commanding vocal presence"]
                )
            }
        ),
        "clarity_and_conciseness": CriterionConfig(
            id="clarity_and_conciseness",
            name="Clarity & Conciseness",
            weight=0.15,
            description="Measures precision of language, avoidance of circumlocution or jargon, and syntactic economy.",
            requires_audio=False,
            anchors={
                "1": ScoringAnchor(
                    score=1,
                    name="Substantial Improvement Needed",
                    description="Dense, convoluted phrasing; excessive repetition of exact phrases; confusing jargon.",
                    observable_indicators=["Extreme phrase repetition", "Incomprehensible syntax", "Severe rambling"]
                ),
                "2": ScoringAnchor(
                    score=2,
                    name="Below Target Standard",
                    description="Wordy and roundabout sentences; repetitive phrasing; relies on filler phrases like 'in other words'.",
                    observable_indicators=["Verbose sentence loops", "Unnecessary qualifiers", "Repetitive phrasing"]
                ),
                "3": ScoringAnchor(
                    score=3,
                    name="Developing",
                    description="Clear main points; readable syntax; occasional redundancy that could be streamlined.",
                    observable_indicators=["Generally clear", "Minor repetition", "Standard vocabulary"]
                ),
                "4": ScoringAnchor(
                    score=4,
                    name="Strong",
                    description="Crisp, direct language; varied vocabulary; concepts articulated economically and vividly.",
                    observable_indicators=["Crisp articulation", "Zero unnecessary fluff", "Precise terminology"]
                ),
                "5": ScoringAnchor(
                    score=5,
                    name="Excellent",
                    description="Laser-sharp clarity; elegant concision; every single word carries weight and intent.",
                    observable_indicators=["Elegantly concise", "Potent vocabulary", "Zero redundant verbiage"]
                )
            }
        )
    }

    version = "1.0.0"
    r_hash = compute_rubric_hash(criteria, version)

    return RubricDefinition(
        rubric_id="speech_default_v1",
        name="OratorIQ Standard Speech Rubric",
        version=version,
        rubric_hash=r_hash,
        criteria=criteria
    )


class RubricRegistry:
    """Manages active and historical immutable rubric configurations."""

    def __init__(self):
        default = get_default_rubric()
        self._rubrics: Dict[str, RubricDefinition] = {
            default.rubric_id: default
        }
        self._versions: Dict[str, Dict[str, RubricDefinition]] = {
            default.rubric_id: {default.version: default}
        }

    def get_rubric(self, rubric_id: str = "speech_default_v1", version: Optional[str] = None) -> RubricDefinition:
        if rubric_id not in self._rubrics:
            # Fallback to default
            return self._rubrics["speech_default_v1"]
        if version and version in self._versions.get(rubric_id, {}):
            return self._versions[rubric_id][version]
        return self._rubrics[rubric_id]

    def register_rubric(self, rubric: RubricDefinition) -> RubricDefinition:
        """Validates and registers a rubric with immutable hash."""
        if not rubric.validate_weights():
            raise ValueError(f"Rubric criteria weights must sum to 1.0 (currently sum to {sum(c.weight for c in rubric.criteria.values())}).")
        
        # Calculate fresh hash
        rubric.rubric_hash = compute_rubric_hash(rubric.criteria, rubric.version)
        
        self._rubrics[rubric.rubric_id] = rubric
        if rubric.rubric_id not in self._versions:
            self._versions[rubric.rubric_id] = {}
        self._versions[rubric.rubric_id][rubric.version] = rubric
        return rubric

    def get_rubric_versions(self, rubric_id: str) -> List[Dict[str, Any]]:
        """Returns all registered immutable versions of a rubric."""
        versions_map = self._versions.get(rubric_id, {})
        if not versions_map:
            if rubric_id in self._rubrics:
                return [self._rubrics[rubric_id].model_dump()]
            return []
        return [r.model_dump() for r in versions_map.values()]

    def list_rubrics(self) -> List[Dict[str, Any]]:
        result = []
        for r_id, r in self._rubrics.items():
            result.append({
                "rubric_id": r.rubric_id,
                "name": r.name,
                "version": r.version,
                "rubric_hash": r.rubric_hash,
                "criteria_count": len(r.criteria),
                "criteria": [
                    {"id": c.id, "name": c.name, "weight": c.weight, "requires_audio": c.requires_audio}
                    for c in r.criteria.values()
                ]
            })
        return result


def rating_to_normalized_score(rating: int) -> float:
    """Maps 1-5 ordinal rating linearly to 0.0 - 100.0."""
    if rating < 1:
        return 0.0
    if rating > 5:
        return 100.0
    return round(((rating - 1) / 4.0) * 100.0, 2)


def score_to_grade(score: Optional[float]) -> str:
    """Converts a 0-100 score to a standard letter grade."""
    if score is None:
        return "N/A"
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def aggregate_rubric_scores(
    criterion_scores: Dict[str, CriterionScoreResult],
    rubric: RubricDefinition
) -> Tuple[Optional[float], float, List[str]]:
    """
    Computes overall score using the formula:
    overall_score = sum(normalized_score * weight) / sum(available_weights)

    Returns:
    (overall_score, coverage_ratio, missing_criteria)
    """
    weighted_sum = 0.0
    available_weight_sum = 0.0
    missing_criteria = []

    for c_id, config in rubric.criteria.items():
        res = criterion_scores.get(c_id)
        if res and res.status == "evaluated" and res.normalized_score is not None:
            weighted_sum += res.normalized_score * config.weight
            available_weight_sum += config.weight
        else:
            missing_criteria.append(c_id)

    total_weight = sum(c.weight for c in rubric.criteria.values())
    coverage_ratio = round(available_weight_sum / max(1e-4, total_weight), 4)

    if available_weight_sum <= 0:
        return None, 0.0, missing_criteria

    overall_score = round(weighted_sum / available_weight_sum, 1)
    return overall_score, coverage_ratio, missing_criteria
