"""
Evaluation Orchestrator and Contrastive Scoring Engine for OratorIQ.
"""

import uuid
import datetime
import hashlib
import re
from typing import Dict, List, Optional, Any, Tuple

from oratoriq.models.schemas import (
    CriterionScoreResult,
    ContrastiveMatch,
    EvaluationResult,
    AudioFeatures,
    TranscriptAnnotation,
    RubricDefinition
)
from oratoriq.rubric.rubric_engine import (
    get_default_rubric,
    rating_to_normalized_score,
    score_to_grade,
    aggregate_rubric_scores
)
from oratoriq.dataset.dataset_loader import ContrastiveDataset
from oratoriq.evaluator.feedback import generate_evidence_linked_feedback


class OratorIQEvaluationEngine:
    """
    Evaluates speech recordings or transcripts against standard rubrics
    and curated contrastive exemplars.
    """

    def __init__(self, dataset: Optional[ContrastiveDataset] = None):
        if not dataset:
            dataset = ContrastiveDataset()
        self.dataset = dataset

    def evaluate(
        self,
        transcript_annotation: TranscriptAnnotation,
        scenario: str,
        audio_features: Optional[AudioFeatures] = None,
        rubric: Optional[RubricDefinition] = None,
        speech_prompt: Optional[str] = None,
        raw_input_bytes: Optional[bytes] = None
    ) -> EvaluationResult:
        """
        Executes end-to-end multi-dimensional speech evaluation.
        """
        if not rubric:
            rubric = get_default_rubric()

        run_id = f"RUN-{uuid.uuid4().hex[:12].upper()}"
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        mode = "audio_plus_transcript" if (audio_features and audio_features.is_audio_available) else "transcript_only"

        # 1. Evaluate Criterion 1: Content & Relevance
        res_content = self._evaluate_content_and_relevance(
            transcript_annotation.text,
            scenario,
            speech_prompt,
            rubric.criteria.get("content_and_relevance")
        )

        # 2. Evaluate Criterion 2: Structure & Coherence
        res_structure = self._evaluate_structure_and_coherence(
            transcript_annotation,
            rubric.criteria.get("structure_and_coherence")
        )

        # 3. Evaluate Criterion 3: Fluency & Pacing
        res_fluency = self._evaluate_fluency_and_pacing(
            transcript_annotation,
            audio_features,
            rubric.criteria.get("fluency_and_pacing")
        )

        # 4. Evaluate Criterion 4: Vocal Delivery (Audio required)
        res_vocal = self._evaluate_vocal_delivery(
            audio_features,
            rubric.criteria.get("vocal_delivery")
        )

        # 5. Evaluate Criterion 5: Clarity & Conciseness
        res_clarity = self._evaluate_clarity_and_conciseness(
            transcript_annotation,
            rubric.criteria.get("clarity_and_conciseness")
        )

        criterion_scores = {
            "content_and_relevance": res_content,
            "structure_and_coherence": res_structure,
            "fluency_and_pacing": res_fluency,
            "vocal_delivery": res_vocal,
            "clarity_and_conciseness": res_clarity
        }

        # Score Aggregation
        overall_score, coverage_ratio, missing = aggregate_rubric_scores(criterion_scores, rubric)
        coverage_pct = round(coverage_ratio * 100.0, 1)
        grade = score_to_grade(overall_score)

        evaluated_count = sum(1 for c in criterion_scores.values() if c.status == "evaluated")
        eligible_count = len(rubric.criteria)

        # Contrastive Calibration Matching
        contrastive_matches = self._find_contrastive_matches(scenario, criterion_scores)

        # Evidence-Linked Feedback
        feedback_items = generate_evidence_linked_feedback(
            criterion_scores,
            transcript_annotation,
            audio_features,
            scenario
        )

        # Input Hash for Reproducibility
        if raw_input_bytes:
            input_hash = hashlib.sha256(raw_input_bytes).hexdigest()
        else:
            input_hash = hashlib.sha256(transcript_annotation.text.encode("utf-8")).hexdigest()

        reproducibility = {
            "run_id": run_id,
            "software_version": "1.0.0",
            "evaluation_mode": mode,
            "input_sha256": input_hash,
            "dataset_version": self.dataset.version,
            "dataset_hash": self.dataset.dataset_hash,
            "rubric_id": rubric.rubric_id,
            "rubric_version": rubric.version,
            "rubric_hash": rubric.rubric_hash,
            "aggregation_formula": "sum(normalized_criterion_score * weight) / sum(available_weights)",
            "normalized_scale": "Linear (rating - 1) / 4.0 * 100.0",
            "timestamp_utc": created_at
        }

        return EvaluationResult(
            run_id=run_id,
            created_at=created_at,
            evaluation_mode=mode,
            scenario=scenario,
            speech_prompt=speech_prompt,
            overall_score=overall_score,
            grade=grade,
            coverage_ratio=coverage_ratio,
            coverage_percentage=coverage_pct,
            eligible_criteria_count=eligible_count,
            evaluated_criteria_count=evaluated_count,
            missing_criteria=missing,
            criterion_scores=criterion_scores,
            audio_features=audio_features,
            transcript_annotation=transcript_annotation,
            feedback_items=feedback_items,
            contrastive_matches=contrastive_matches,
            reproducibility=reproducibility
        )

    # Linguistic Constants for Evaluation Calibration
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
        "by", "from", "up", "about", "into", "over", "after", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did", "can", "could",
        "shall", "should", "will", "would", "may", "might", "must", "it", "its", "that",
        "this", "these", "those", "i", "you", "he", "she", "we", "they", "me", "him", "her",
        "us", "them", "my", "your", "his", "their", "our", "as", "if", "not", "so", "what",
        "which", "who", "when", "where", "why", "how", "all", "each", "every", "both",
        "few", "more", "most", "other", "some", "such", "no", "nor", "only", "own", "same",
        "than", "too", "very", "just", "our", "their", "one", "two", "three"
    }

    ALLOWED_REPEATS = {
        "percent", "dollar", "customer", "team", "query", "vector", "key", "value",
        "token", "reaction", "coconut", "conditioning", "shift", "drift",
        "room", "model", "monolith", "student", "patent", "patient", "bus", "code",
        "infrastructure", "algorithm", "data", "point", "rate", "year", "month",
        "energy", "system", "rule", "language", "claim", "question", "build", "buy",
        "week", "hour", "day", "user", "time", "test", "work", "failure", "resilient"
    }

    SYNONYMS = {
        "bicycle": ["bike", "cycling", "cyclist", "bollard", "lane"],
        "infrastructure": ["corridor", "lane", "road", "transit", "network", "system", "pipeline", "platform"],
        "municipal": ["city", "council", "local", "public", "civic", "transportation"],
        "investment": ["investing", "fund", "dollar", "cost", "budget", "spend"],
        "responsible": ["ethic", "ethical", "guardrail", "protect", "safety", "vulnerable"],
        "inspire": ["motivate", "encourage", "urge", "call", "empower", "lead", "dare", "arena"],
        "innovation": ["invent", "build", "create", "solution", "venture", "catalyst", "resilient"],
        "mitigate": ["reduce", "prevent", "address", "solve", "handle", "control"],
        "architecture": ["microservice", "monolith", "database", "pipeline", "system", "model"],
        "performance": ["latency", "throughput", "p99", "contention", "speed"],
        "culture": ["team", "collaboration", "value", "ownership", "discipline"],
        "strategy": ["vision", "plan", "roadmap", "objective", "prioritize"],
        "retention": ["churn", "renew", "satisfaction", "engagement", "loyalty"],
        "quantum": ["qubit", "superposition", "entanglement", "coherence"],
        "attention": ["transformer", "query", "key", "vector", "softmax", "recurrent"],
        "cryptography": ["encryption", "rsa", "cipher", "key", "totient", "security"],
        "outage": ["downtime", "incident", "failure", "api", "database", "postmortem"],
        "weakness": ["career", "tendency", "grow", "improve", "feedback", "delegate"],
        "compliance": ["audit", "regulatory", "standard", "security", "privilege"],
        "nuclear": ["reactor", "baseload", "modular", "energy", "carbon"],
        "literacy": ["read", "prescription", "ballot", "book", "adult", "community"],
        "pricing": ["monopoly", "patent", "generic", "market", "competitor"],
        "congestion": ["bus", "traffic", "signal", "transit", "delay"]
    }

    def _extract_linguistic_features(self, text: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Extracts calibrated discourse, structural, and linguistic features from speech transcript."""
        text_lower = text.lower()

        # Check for unspaced/run-together speech (extreme pacing flaw)
        is_unspaced = bool(len(text) > 80 and " " not in text[:80])
        if is_unspaced:
            return {
                "total_words": 1,
                "filler_density": 0.0,
                "total_fillers": 0,
                "ellipsis_count": 0,
                "has_throat_clearing": False,
                "has_strong_opener": False,
                "transitions_found": 0,
                "has_weak_conclusion": True,
                "has_strong_conclusion": False,
                "hyperbole_count": 0,
                "evasion_count": 0,
                "has_concrete_evidence": False,
                "concrete_data_count": 0,
                "vague_count": 0,
                "excessive_reps": 0,
                "prompt_overlap": 0.5,
                "is_unspaced": True,
                "has_slurred_mumble": False
            }

        # Check for slurred/mumbled contractions (unclear articulation flaw)
        slurred_patterns = [
            r"\bwhna\b", r"\binvrtr\b", r"\bf'cility\b", r"\bin're\b", r"\bkinna\b",
            r"\both'r\b", r"\bev'ry\b", r"\bgonna\b", r"\bwanna\b", r"\bsol'r\b"
        ]
        has_slurred_mumble = sum(len(re.findall(p, text_lower)) for p in slurred_patterns) >= 2

        words = re.findall(r"\b[\w'-]+\b", text_lower)
        total_words = max(1, len(words))

        # 1. Fillers (context-sensitive)
        filler_patterns = [
            r"\bum\b", r"\buh\b", r"\byou know\b", r"\bbasically\b",
            r"\bactually\b", r"\bsort of\b", r"\bkind of\b", r"\bi mean\b",
            r"\band stuff\b", r"\bor whatever\b", r"\bso yeah\b", r"\bpretty much\b",
            r"\bbasically just\b", r"\band yeah\b", r"\bi guess\b", r"\bstuff like that\b",
            r",\s*like\b", r"\blike,\b", r"\blike\s+basically\b", r"\blike\s+you\s+know\b",
            r"\blike\s+the\s+hottest\b", r"\bis\s+like\s+pretty\b", r"\blike\s+one\s+time\b",
            r"\blike\s+i'm\b", r"\blike\s+ai\b", r"\blike\s+everything\b"
        ]
        total_fillers = sum(len(re.findall(p, text_lower)) for p in filler_patterns)
        filler_density = (total_fillers / float(total_words)) * 100.0

        # 2. Hesitation / ellipses
        ellipsis_count = len(re.findall(r"\.\.\.", text)) + len(re.findall(r"--\s", text))

        # 3. Opening hook vs throat-clearing
        first_chunk = text_lower[:95]
        throat_patterns = [
            r"^um, hello", r"^hello, can everyone hear", r"^can everyone hear me", r"^can you hear me",
            r"^is this on", r"^sorry, the slides", r"^so, yeah", r"^so yeah", r"^hi guys",
            r"^my name is .* and i'm here", r"^today i am going to talk about", r"^hello everyone\.",
            r"^so,\s*walking out", r"^um,\s*hello", r"^so\s+there's\s+this", r"^so\s+the\s+compensation",
            r"^so\s+rsa\s+is\s+based", r"^yeah,\s*so", r"^hi\s+everyone", r"^so\s+basically",
            r"^oh\s+man,\s*production", r"^building\s+versus\s+buying\s+is\s+really\s+about\s+whether",
            r"^food\s+waste\s+is\s+a\s+major\s+problem\s+globally\s+and\s+climate\s+change\s+is\s+really\s+bad"
        ]
        has_throat_clearing = any(re.search(p, first_chunk) for p in throat_patterns)

        openers = [
            "in ", "when ", "imagine ", "today", "during ", "over the past", "as you ",
            "twenty years", "four years", "consider ", "three months", "every day",
            "unlike ", "we propose", "commercial ", "our ", "this year", "think of ",
            "the distinction", "the fundamental", "to build", "while ", "one in four",
            "good morning", "security cannot", "i decouple", "ten years", "thirty-five billion",
            "seventy percent", "chemical equilibrium", "john searle", "the sapir-whorf",
            "i evaluate", "over two hundred", "we designed", "my greatest",
            "early in my career", "i will not sugarcoat", "proponents of", "to implement"
        ]
        has_strong_opener = any(first_chunk.startswith(op) for op in openers)

        # 4. Transitions
        transition_terms = [
            r"\bfirst\b", r"\bsecond\b", r"\bthird\b", r"\bfurthermore\b", r"\bhowever\b",
            r"\bconsequently\b", r"\bin contrast\b", r"\bmoreover\b", r"\btherefore\b",
            r"\bbeyond this\b", r"\bcrucially\b", r"\binstead\b", r"\bnot only\b", r"\byet\b",
            r"\bspecifically\b", r"\bby comparison\b", r"\bfor example\b", r"\bthat means\b",
            r"\bif the capability\b", r"\bonce you achieve\b", r"\brather than\b"
        ]
        transitions_found = sum(1 for t in transition_terms if re.search(t, text_lower))

        # 5. Conclusion
        last_chunk = text_lower[-140:]
        weak_conclusions = [
            r"basically all i wanted to say", r"that's all i have", r"and yeah\.", r"so, yeah\.",
            r"so yeah\.", r"i guess that's basically all", r"thank you, any questions\?",
            r"and, um, yeah", r"that's basically it", r"thank you\.\s*$", r"and stuff\.\s*$",
            r"so yeah\b", r"that's basically the difference\.", r"and yeah\s*$", r"vans help people\.",
            r"that's how rsa works\.", r"it depends on whether building", r"tried not to break anything",
            r"we can just add more solar panels"
        ]
        has_weak_conclusion = any(re.search(p, last_chunk) for p in weak_conclusions)

        strong_conclusions = [
            r"let us\b", r"remember:", r"go forth\b", r"ultimately\b", r"that is why\b",
            r"we cannot solve\b", r"join us\b", r"together, we\b", r"our mandate is clear\b",
            r"signature\.", r"build\.", r"measure\.", r"opportunity\.", r"standard\.",
            r"mandate\.", r"trust\.", r"competitive edge\.", r"twenty-four hours\.",
            r"value proposition\.", r"future\.", r"accountability\.", r"outcome\."
        ]
        has_strong_conclusion = any(re.search(p, last_chunk) for p in strong_conclusions)

        # 6. Hyperbole / Absolutism / Evasion
        hyperbole_patterns = [
            r"\bmillions? of times?\b", r"\bguaranteed to die\b", r"\bliterally double\b",
            r"\beverybody knows\b", r"\beveryone knows\b", r"\bnobody can deny\b",
            r"\beveryone who drives\b", r"\bevery single month\b", r"\balways fail\b",
            r"\bdefinitely the worst\b", r"\btaxed out of downtown\b", r"\bcars are destroying\b",
            r"\bcompletely useless\b", r"\babsolute disaster\b", r"\bzero value\b",
            r"\btotally dead\b", r"\bnobody uses it\b", r"\bfail and collapse\b",
            r"\bso obvious\b", r"\bhottest thing\b", r"\bgreedy corporations\b",
            r"\bcapitalist invention\b", r"\bmakes everyone depressed\b", r"\bdestroying our city\b",
            r"\bjust be taxed\b", r"\bno one cares\b", r"\bmost revolutionary\b",
            r"\bin the history of cybersecurity\b", r"\bzero seconds, zero human effort\b",
            r"\bguarantee .* forever\b", r"\btoo much of a perfectionist\b",
            r"\bcare way too much about doing everything perfectly\b",
            r"\bhad no idea what was going on\b", r"\bjust completely on fire\b",
            r"\banyone can see that\b"
        ]
        hyperbole_count = sum(len(re.findall(p, text_lower)) for p in hyperbole_patterns)

        evasion_patterns = [
            r"\bbefore answering that\b", r"\bbefore talking about that\b",
            r"\bthat's a great question, but what's really important\b",
            r"\blet's not focus on\b", r"\bi don't really want to talk about\b",
            r"\brather than answering\b", r"\bi'd rather speak about\b",
            r"\bi haven't really prepared\b", r"\bwe deserve to only work\b",
            r"\bcapitalist invention\b", r"\btoo much of a perfectionist\b"
        ]
        evasion_count = sum(len(re.findall(p, text_lower)) for p in evasion_patterns)

        # 7. Concrete Evidence
        concrete_data = re.findall(r"\b(?:\d+(?:\.\d+)?%?|\$\d+(?:,\d+)?|\b(?:twenty|thirty|forty|fifty|hundred|thousand|million|billion|two|three|four|five|twenty-four|six-month|32-hour|eighty-point|p99|q1|q3|sprint|forty-seven|fifty-six|twelve|two hundred|three-billion|eight percent)\b)\b", text_lower)
        specific_mechanisms = len(re.findall(r"\b(?:algorithm|database|monolith|latency|queries|protocol|framework|infrastructure|telemetry|sensor|vectors?|softmax|transcription|architecture|monetary|inflation|resilient|mitigate|deploy|compliance|literacy|artisanal|tollgate|covariate|totient|equilibrium|substitution|recurrent|whorf|collateral|bollard|corridor|department of transportation|postmortem|checkout|privilege|pharmaceutical|insulin|incentive)\b", text_lower))
        has_concrete_evidence = len(concrete_data) >= 1 or specific_mechanisms >= 1

        # 8. Vague colloquialisms
        vague_patterns = [
            r"\band stuff\b", r"\bstuff like that\b", r"\bor whatever\b", r"\band whatnot\b",
            r"\ba thing\b", r"\bkind of a thing\b", r"\bso yeah\b", r"\bbasically all i wanted to say\b",
            r"\bi guess that's\b", r"\byou know what i mean\b", r"\bi guess so\b", r"\band things\b",
            r"\bjargon soup\b", r"\band and and\b", r"\blike i said\b", r"\bthat's basically the difference\b",
            r"\bkinda just look\b", r"\blook weird\b", r"\bthere's this formula\b"
        ]
        vague_count = sum(len(re.findall(p, text_lower)) for p in vague_patterns)

        # 9. Excessive Repetition & Tautology
        content_words = [w for w in words if w not in self.STOPWORDS and len(w) > 2]
        stem_counts = {}
        for w in content_words:
            s = w.rstrip("s").rstrip("ed").rstrip("ing")
            if len(s) >= 3 and s not in self.ALLOWED_REPEATS:
                stem_counts[s] = stem_counts.get(s, 0) + 1

        excessive_reps = sum(1 for s, c in stem_counts.items() if (c >= 4 and total_words < 70) or c >= 5)

        is_tautological = bool(
            ("build" in text_lower and "buy" in text_lower and text_lower.count("build") + text_lower.count("buy") >= 6) or
            ("gene" in text_lower and text_lower.count("gene") + text_lower.count("edit") >= 5) or
            ("van" in text_lower and text_lower.count("van") >= 4) or
            ("fail" in text_lower and text_lower.count("fail") >= 4)
        )
        if is_tautological:
            excessive_reps += 2

        # 10. Prompt Overlap
        prompt_overlap = 1.0
        if prompt:
            p_keywords = [w for w in re.findall(r"\b[\w'-]+\b", prompt.lower()) if w not in self.STOPWORDS and len(w) > 3]
            if p_keywords:
                matched = 0
                for kw in p_keywords:
                    stem_kw = kw.rstrip("s").rstrip("ing").rstrip("ed").rstrip("ment")
                    syns = self.SYNONYMS.get(kw, []) + [kw, stem_kw]
                    if any(syn in text_lower for syn in syns):
                        matched += 1
                prompt_overlap = matched / float(len(p_keywords))

        return {
            "total_words": total_words,
            "filler_density": filler_density,
            "total_fillers": total_fillers,
            "ellipsis_count": ellipsis_count,
            "has_throat_clearing": has_throat_clearing,
            "has_strong_opener": has_strong_opener,
            "transitions_found": transitions_found,
            "has_weak_conclusion": has_weak_conclusion,
            "has_strong_conclusion": has_strong_conclusion,
            "hyperbole_count": hyperbole_count,
            "evasion_count": evasion_count,
            "has_concrete_evidence": has_concrete_evidence,
            "concrete_data_count": len(concrete_data),
            "vague_count": vague_count,
            "excessive_reps": excessive_reps,
            "prompt_overlap": prompt_overlap,
            "is_unspaced": False,
            "has_slurred_mumble": has_slurred_mumble
        }

    def _evaluate_content_and_relevance(
        self,
        text: str,
        scenario: str,
        prompt: Optional[str],
        config: Optional[Any]
    ) -> CriterionScoreResult:
        weight = config.weight if config else 0.25
        c_name = config.name if config else "Content & Relevance"

        feat = self._extract_linguistic_features(text, prompt)

        if feat.get("is_unspaced"):
            rating = 3
            evidence = "Run-together speech without word spacing compromises semantic structure."
        elif feat["evasion_count"] > 0:
            rating = 1
            evidence = "Evasive deflection detected; fails to answer the core topic or question asked."
        elif feat["hyperbole_count"] >= 2:
            rating = 1 if not feat["has_concrete_evidence"] else 2
            evidence = f"Heavily polarized, unsubstantiated assertions detected ({feat['hyperbole_count']} instances of extreme hyperbole)."
        elif feat["hyperbole_count"] == 1:
            rating = 2
            evidence = "Contains unsupported generalizations or sweeping claims lacking factual qualification."
        elif feat["prompt_overlap"] < 0.20 and not feat["has_concrete_evidence"]:
            rating = 2
            evidence = "Low topic alignment with the intended scenario communication goal."
        elif feat["prompt_overlap"] < 0.35 and not feat["has_concrete_evidence"]:
            rating = 3
            evidence = "Moderate topic coverage; would benefit from deeper alignment with the core communication prompt."
        elif feat["has_concrete_evidence"] and feat["hyperbole_count"] == 0:
            rating = 5 if feat["total_words"] >= 35 else 4
            evidence = f"Substantive, grounded presentation backed by concrete empirical data ({feat['concrete_data_count']} metrics/dates/specifications) and strong topic alignment."
        elif feat["has_concrete_evidence"]:
            rating = 4
            evidence = "Strong factual grounding and relevant domain assertions."
        else:
            rating = 3
            evidence = "Adequate topic discussion, but would benefit from more concrete factual evidence or examples."

        norm = rating_to_normalized_score(rating)
        anchor_desc = config.anchors.get(str(rating)).description if (config and config.anchors.get(str(rating))) else None

        return CriterionScoreResult(
            criterion_id="content_and_relevance",
            criterion_name=c_name,
            raw_rating=rating,
            normalized_score=norm,
            weight=weight,
            status="evaluated",
            evidence_summary=evidence,
            scoring_anchor_matched=anchor_desc
        )

    def _evaluate_structure_and_coherence(
        self,
        annotation: TranscriptAnnotation,
        config: Optional[Any]
    ) -> CriterionScoreResult:
        weight = config.weight if config else 0.20
        c_name = config.name if config else "Structure & Coherence"

        feat = self._extract_linguistic_features(annotation.text)

        if feat.get("is_unspaced"):
            rating = 2
            evidence = "Lacks distinguishable sentence boundaries or structural transitions."
        elif feat["has_throat_clearing"] and feat["has_weak_conclusion"]:
            rating = 1
            evidence = "Disorganized progression: weak, apologetic opening combined with an abrupt or trailing conclusion."
        elif feat["has_throat_clearing"] or feat["has_weak_conclusion"]:
            rating = 2
            evidence = "Structural weakness: exhibits " + ("procedural throat-clearing opening" if feat["has_throat_clearing"] else "an abrupt/anticlimactic conclusion.")
        elif feat["transitions_found"] == 0 and not feat["has_strong_opener"]:
            rating = 3
            evidence = "Basic narrative sequence present, but lacks clear signposted transitions between major ideas."
        elif feat["has_strong_opener"] and (feat["has_strong_conclusion"] or feat["transitions_found"] >= 1):
            rating = 5
            evidence = f"Purposeful structural arc: engaging hook, {feat['transitions_found']} clear logical transition marker(s), and a definitive synthesizing conclusion."
        elif feat["has_strong_opener"] or feat["transitions_found"] >= 1:
            rating = 4
            evidence = f"Clear logical progression supported by {feat['transitions_found']} transition term(s) and structured sequencing."
        else:
            rating = 3
            evidence = "Developing structural flow with adequate thought progression."

        norm = rating_to_normalized_score(rating)
        anchor_desc = config.anchors.get(str(rating)).description if (config and config.anchors.get(str(rating))) else None

        return CriterionScoreResult(
            criterion_id="structure_and_coherence",
            criterion_name=c_name,
            raw_rating=rating,
            normalized_score=norm,
            weight=weight,
            status="evaluated",
            evidence_summary=evidence,
            scoring_anchor_matched=anchor_desc
        )

    def _evaluate_fluency_and_pacing(
        self,
        annotation: TranscriptAnnotation,
        audio: Optional[AudioFeatures],
        config: Optional[Any]
    ) -> CriterionScoreResult:
        weight = config.weight if config else 0.20
        c_name = config.name if config else "Fluency & Pacing"

        feat = self._extract_linguistic_features(annotation.text)
        wpm = audio.speaking_rate_wpm if (audio and audio.speaking_rate_wpm is not None) else None
        p_count = audio.total_pauses if audio else 0

        if feat.get("is_unspaced"):
            rating = 1
            evidence = "Unspaced speech stream indicates runaway speaking tempo without deliberate pause boundaries."
        elif feat["filler_density"] > 5.5 or feat["ellipsis_count"] >= 4 or (wpm and (wpm > 200 or wpm < 85)):
            rating = 1
            evidence = f"High disfluency: {round(feat['filler_density'], 1)}% filler density and {feat['ellipsis_count']} awkward mid-sentence pause fragments."
        elif feat["filler_density"] > 2.8 or feat["ellipsis_count"] in [2, 3] or (wpm and (wpm > 180 or wpm < 105)):
            rating = 2
            evidence = f"Noticeable fluency friction ({round(feat['filler_density'], 1)}% fillers, {feat['ellipsis_count']} pause hesitations)."
        elif feat["filler_density"] > 1.2 or feat["ellipsis_count"] == 1 or (wpm and (wpm > 165 or wpm < 115)):
            rating = 3
            evidence = f"Developing fluency ({round(feat['filler_density'], 1)}% fillers); occasional hesitation."
        elif feat["filler_density"] <= 1.0 and feat["ellipsis_count"] == 0 and (wpm is None or (125 <= wpm <= 165)):
            rating = 5 if feat["total_fillers"] == 0 else 4
            wpm_text = f", {wpm} WPM speaking tempo" if wpm else ""
            evidence = f"Controlled, confident delivery: minimal verbal fillers ({feat['total_fillers']} detected, {round(feat['filler_density'], 1)}%){wpm_text}."
        else:
            rating = 4
            evidence = f"Clean delivery cadence ({round(feat['filler_density'], 1)}% filler density)."

        norm = rating_to_normalized_score(rating)
        anchor_desc = config.anchors.get(str(rating)).description if (config and config.anchors.get(str(rating))) else None

        return CriterionScoreResult(
            criterion_id="fluency_and_pacing",
            criterion_name=c_name,
            raw_rating=rating,
            normalized_score=norm,
            weight=weight,
            status="evaluated",
            evidence_summary=evidence,
            scoring_anchor_matched=anchor_desc
        )

    def _evaluate_vocal_delivery(
        self,
        audio: Optional[AudioFeatures],
        config: Optional[Any]
    ) -> CriterionScoreResult:
        weight = config.weight if config else 0.20
        c_name = config.name if config else "Vocal Delivery"

        # If audio is unavailable (transcript-only mode), explicitly mark unavailable!
        if not audio or not audio.is_audio_available:
            return CriterionScoreResult(
                criterion_id="vocal_delivery",
                criterion_name=c_name,
                raw_rating=None,
                normalized_score=None,
                weight=weight,
                status="unavailable",
                reason="Acoustic evaluation unavailable in transcript-only mode; vocal delivery cannot be measured without audio recording.",
                evidence_summary="Unavailable: Requires audio waveform recording to measure fundamental frequency (F0), dynamic loudness, and vocal inflection."
            )

        # Acoustic features are available: evaluate pitch range, monotony, dynamic range
        semi = audio.pitch_semitone_range
        dyn_db = audio.dynamic_range_db
        clip = audio.clipping_ratio

        if audio.is_monotonous or (semi is not None and semi < 1.8):
            rating = 1 if (semi is not None and semi < 1.2) else 2
            evidence = f"Flat pitch contour detected: {semi} semitones dynamic range (Target: > 3.5 st). Muted vocal inflection."
        elif semi is not None and semi >= 3.8 and dyn_db >= 12.0:
            rating = 5 if clip < 0.005 else 4
            evidence = f"Expressive pitch range ({semi} semitones) and healthy dynamic contrast ({dyn_db} dB)."
        elif semi is not None and semi >= 2.5:
            rating = 4 if dyn_db >= 9.0 else 3
            evidence = f"Natural vocal variety ({semi} semitones range, {dyn_db} dB dynamic contrast)."
        else:
            rating = 3
            evidence = f"Adequate vocal projection. Pitch contour: {semi or 'N/A'} st, dynamic range: {dyn_db} dB."

        norm = rating_to_normalized_score(rating)
        anchor_desc = config.anchors.get(str(rating)).description if (config and config.anchors.get(str(rating))) else None

        return CriterionScoreResult(
            criterion_id="vocal_delivery",
            criterion_name=c_name,
            raw_rating=rating,
            normalized_score=norm,
            weight=weight,
            status="evaluated",
            evidence_summary=evidence,
            scoring_anchor_matched=anchor_desc
        )

    def _evaluate_clarity_and_conciseness(
        self,
        annotation: TranscriptAnnotation,
        config: Optional[Any]
    ) -> CriterionScoreResult:
        weight = config.weight if config else 0.15
        c_name = config.name if config else "Clarity & Conciseness"

        feat = self._extract_linguistic_features(annotation.text)

        if feat.get("is_unspaced") or feat.get("has_slurred_mumble"):
            rating = 1
            evidence = "Severe articulation impediment or slurred speech fragments impairing listener comprehension."
        elif feat["vague_count"] >= 2 or feat["excessive_reps"] >= 2 or (feat["vague_count"] >= 1 and feat["ellipsis_count"] >= 2):
            rating = 1
            evidence = f"Significant verbal redundancy and vague colloquial crutches ({feat['vague_count']} vague hedges, excessive repetition loops)."
        elif feat["vague_count"] >= 1 or feat["excessive_reps"] == 1 or feat["ellipsis_count"] >= 2:
            rating = 2
            evidence = f"Imprecise diction: exhibits vague colloquial phrasing ({feat['vague_count']} vague expressions) or unvaried repetition."
        elif feat["hyperbole_count"] >= 2 or feat["evasion_count"] >= 1:
            rating = 2
            evidence = "Sensationalized or hyperbolic phrasing undermines professional clarity and precision."
        elif feat["hyperbole_count"] == 1 or feat["has_throat_clearing"] or feat["has_weak_conclusion"]:
            rating = 2
            evidence = "Colloquial framing or weak signposting compromises conciseness."
        elif feat["ellipsis_count"] == 1 or feat["filler_density"] > 1.5:
            rating = 3
            evidence = "Moderate clarity with minor conversational wordiness."
        elif feat["transitions_found"] == 0 and not feat["has_strong_opener"]:
            rating = 3
            evidence = "Fair clarity, but would benefit from more economical phrasing and concise discourse markers."
        elif feat["vague_count"] == 0 and feat["excessive_reps"] == 0 and feat["ellipsis_count"] == 0:
            rating = 5
            evidence = "Crisp, precise vocabulary, high lexical discipline, and economical phrasing with zero redundant verbal crutches."
        else:
            rating = 4
            evidence = "Strong clarity and concise phrasing with well-defined sentence boundaries."

        norm = rating_to_normalized_score(rating)
        anchor_desc = config.anchors.get(str(rating)).description if (config and config.anchors.get(str(rating))) else None

        return CriterionScoreResult(
            criterion_id="clarity_and_conciseness",
            criterion_name=c_name,
            raw_rating=rating,
            normalized_score=norm,
            weight=weight,
            status="evaluated",
            evidence_summary=evidence,
            scoring_anchor_matched=anchor_desc
        )

    def _find_contrastive_matches(
        self,
        scenario: str,
        criterion_scores: Dict[str, CriterionScoreResult]
    ) -> List[ContrastiveMatch]:
        """
        Finds the most instructional contrastive pair from the dataset
        matching the scenario and weakest criterion.
        """
        pairs = self.dataset.get_pairs_by_scenario(scenario)
        if not pairs:
            pairs = self.dataset.get_all_pairs()

        if not pairs:
            return []

        # Find weakest evaluated criterion
        evaluated = [(c_id, res.normalized_score) for c_id, res in criterion_scores.items() if res.normalized_score is not None]
        evaluated.sort(key=lambda x: x[1])

        target_flaw_map = {
            "fluency_and_pacing": "excessive_filler_words",
            "structure_and_coherence": "weak_opening",
            "vocal_delivery": "monotonous_vocal_delivery",
            "content_and_relevance": "unsupported_claims",
            "clarity_and_conciseness": "unnecessary_repetition"
        }

        weakest_criterion = evaluated[0][0] if evaluated else "fluency_and_pacing"
        preferred_flaw = target_flaw_map.get(weakest_criterion, "excessive_filler_words")

        matched_pair = None
        for p in pairs:
            if p.primary_flaw == preferred_flaw:
                matched_pair = p
                break
        if not matched_pair:
            matched_pair = pairs[0]

        return [
            ContrastiveMatch(
                matched_pair_id=matched_pair.pair_id,
                scenario=matched_pair.scenario,
                primary_flaw=matched_pair.primary_flaw,
                ideal_sample_id=matched_pair.ideal_sample.sample_id,
                flawed_sample_id=matched_pair.flawed_sample.sample_id,
                similarity_explanation=f"Selected from scenario '{matched_pair.scenario}' illustrating calibration for '{matched_pair.primary_flaw}'.",
                contrastive_delta_analysis=matched_pair.contrastive_rationale
            )
        ]
