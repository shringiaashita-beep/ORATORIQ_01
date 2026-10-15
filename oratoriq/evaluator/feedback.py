"""
Evidence-Linked Actionable Feedback Generator for OratorIQ.
"""

import uuid
from typing import Dict, List, Optional, Any
from oratoriq.models.schemas import (
    FeedbackItem,
    AudioFeatures,
    TranscriptAnnotation,
    CriterionScoreResult
)


def generate_evidence_linked_feedback(
    criterion_results: Dict[str, CriterionScoreResult],
    annotation: TranscriptAnnotation,
    audio_features: Optional[AudioFeatures],
    scenario: str
) -> List[FeedbackItem]:
    """
    Synthesizes grounded, evidence-linked feedback cards from actual measurements.
    Prioritizes top high-impact recommendations rather than generic boilerplate.
    """
    items: List[FeedbackItem] = []
    text = annotation.text
    total_words = len(annotation.words)

    # 1. Fluency & Pacing: Filler Words
    total_fillers = sum(f["count"] for f in annotation.filler_words_detected)
    filler_density = (total_fillers / max(1, total_words)) * 100.0

    if filler_density > 4.0:
        top_filler = max(annotation.filler_words_detected, key=lambda x: x["count"])
        items.append(FeedbackItem(
            feedback_id=f"FB-{uuid.uuid4().hex[:8].upper()}",
            rubric_criterion="fluency_and_pacing",
            criterion_name="Fluency & Pacing",
            observed_issue=f"Elevated filler word density ({round(filler_density, 1)}% of total words), dominated by '{top_filler['word']}' ({top_filler['count']} occurrences).",
            evidence_type="transcript_pattern",
            transcript_excerpt=f"Observed pattern: ...{top_filler['word']}...",
            timestamp_range=None,
            measured_value=f"Filler density: {round(filler_density, 1)}% (Target: < 2.0%)",
            explanation="Frequent filler words act as verbal crutches while thinking, which interrupts listener focus and diminishes perceived authority.",
            recommended_action="Replace the verbal filler with an intentional silent pause. Embrace 1-2 seconds of silence while formulating your next clause.",
            example_rewrite_or_exercise=f"Drill: Read the first two sentences aloud. Whenever you feel the urge to say '{top_filler['word']}', close your lips firmly and hold silence for one full second before speaking the next word.",
            severity="high" if filler_density > 6.0 else "medium",
            evaluator_method="lexical_pattern_density_analyzer",
            limitations="Measures English filler terms in lexical token stream; does not classify dialectal discourse particles."
        ))

    # 2. Fluency & Pacing: Speaking Rate (WPM)
    if audio_features and audio_features.speaking_rate_wpm is not None:
        wpm = audio_features.speaking_rate_wpm
        if wpm > 175.0:
            items.append(FeedbackItem(
                feedback_id=f"FB-{uuid.uuid4().hex[:8].upper()}",
                rubric_criterion="fluency_and_pacing",
                criterion_name="Fluency & Pacing",
                observed_issue=f"Rapid speaking tempo ({wpm} WPM). High tempo risks cognitive overload for the audience.",
                evidence_type="acoustic_measurement",
                transcript_excerpt=None,
                timestamp_range={"start": 0.0, "end": min(60.0, audio_features.duration_sec)},
                measured_value=f"{wpm} WPM (Ideal professional range: 130 - 160 WPM)",
                explanation="Pacing above 175 WPM leaves insufficient time for key points and data assertions to be absorbed.",
                recommended_action="Anchor your delivery by consciously inserting a 1-second pause after every completed thesis statement or comma clause.",
                example_rewrite_or_exercise="Metronome Pacing Exercise: Set a metronome to 140 BPM. Speak one word per beat across a 40-word paragraph to physically calibrate internal cadence.",
                severity="medium",
                evaluator_method="speech_duration_word_ratio_calculator",
                limitations="Assumes continuous speech without multi-speaker turn taking."
            ))
        elif wpm < 115.0 and wpm > 0.0:
            items.append(FeedbackItem(
                feedback_id=f"FB-{uuid.uuid4().hex[:8].upper()}",
                rubric_criterion="fluency_and_pacing",
                criterion_name="Fluency & Pacing",
                observed_issue=f"Subdued speaking tempo ({wpm} WPM). May cause listener attention to drift.",
                evidence_type="acoustic_measurement",
                transcript_excerpt=None,
                timestamp_range={"start": 0.0, "end": min(60.0, audio_features.duration_sec)},
                measured_value=f"{wpm} WPM (Target: 130 - 160 WPM)",
                explanation="Pacing below 115 WPM can project hesitancy or lack of conversational momentum.",
                recommended_action="Group words into short 4-to-6 word thought chunks and deliver each chunk with sustained forward momentum.",
                example_rewrite_or_exercise="Thought-Group Sprints: Mark your script with slash marks every 5 words (e.g., 'In third quarter / our team deployed / three microservices'). Read chunk-by-chunk briskly.",
                severity="medium",
                evaluator_method="speech_duration_word_ratio_calculator",
                limitations="Cultural and language norms vary; calculated on standard North American/British business speech benchmarks."
            ))

    # 3. Vocal Delivery: Pitch Monotony
    if audio_features and audio_features.is_monotonous:
        semi = audio_features.pitch_semitone_range or 0.0
        items.append(FeedbackItem(
            feedback_id=f"FB-{uuid.uuid4().hex[:8].upper()}",
            rubric_criterion="vocal_delivery",
            criterion_name="Vocal Delivery",
            observed_issue=f"Narrow fundamental frequency pitch variation ({semi} semitones). Speech exhibits flat tonal contour.",
            evidence_type="acoustic_measurement",
            transcript_excerpt=None,
            timestamp_range=None,
            measured_value=f"Pitch range: {semi} semitones (Target: > 3.5 semitones)",
            explanation="A flat pitch contour sounds like a mechanical recital and causes audience disengagement.",
            recommended_action="Elevate pitch by 2-3 semitones on the focal operative word in each sentence (nouns, action verbs, contrast words).",
            example_rewrite_or_exercise="Pitch Staircase Exercise: Speak the sentence 'We increased revenue by thirty percent'. Step your pitch upward on 'increased' and peak on 'thirty', before resolving downward on 'percent'.",
            severity="high",
            evaluator_method="fundamental_frequency_pyin_contour_analyzer",
            limitations="Calculates fundamental vocal fold vibration (F0); influenced by microphone frequency response and room reverberation."
        ))

    # 4. Structure: Opening Hook
    first_sentence = annotation.segments[0].text if annotation.segments else text[:120]
    first_lower = first_sentence.lower()
    throat_clearing = any(ph in first_lower for ph in ["um, hello", "can you hear me", "so, yeah", "sorry, the slides", "my name is and i"])
    if throat_clearing:
        items.append(FeedbackItem(
            feedback_id=f"FB-{uuid.uuid4().hex[:8].upper()}",
            rubric_criterion="structure_and_coherence",
            criterion_name="Structure & Coherence",
            observed_issue="Weak or apologetic opening; throat-clearing dilutes the critical first 15 seconds.",
            evidence_type="structural_check",
            transcript_excerpt=f"Opening: \"{first_sentence[:80]}...\"",
            timestamp_range={"start": 0.0, "end": 10.0} if audio_features else None,
            measured_value="Detected throat-clearing / procedural greeting in opening segment",
            explanation="The audience forms their primary engagement impression in the first 10-15 seconds. Apologies or setup commentary dissipate credibility.",
            recommended_action="Open directly with a high-stakes fact, an intriguing dilemma, or a vivid story before introducing yourself or your slides.",
            example_rewrite_or_exercise="Opening Hook Formula: Replace 'Hello, can everyone hear me' with: 'Three months ago, forty percent of our enterprise customers faced a critical blocker...'",
            severity="medium",
            evaluator_method="discourse_opening_classifier",
            limitations="Heuristic boundary check for rhetorical hooks."
        ))

    # 5. Clarity: Runaway Sentences / Low Readability
    if annotation.readability_flesch_score < 40.0:
        items.append(FeedbackItem(
            feedback_id=f"FB-{uuid.uuid4().hex[:8].upper()}",
            rubric_criterion="clarity_and_conciseness",
            criterion_name="Clarity & Conciseness",
            observed_issue=f"Dense, convoluted syntactic complexity (Flesch score: {annotation.readability_flesch_score}).",
            evidence_type="transcript_pattern",
            transcript_excerpt=first_sentence[:100],
            timestamp_range=None,
            measured_value=f"Flesch Reading Ease: {annotation.readability_flesch_score} / 100 (Target: > 55.0 for spoken clarity)",
            explanation="Spoken language requires shorter syntactic clauses than written text. Overly long compound sentences lose listeners who cannot re-read.",
            recommended_action="Split compound clauses joined by 'and', 'which', or 'because' into two distinct declarative sentences.",
            example_rewrite_or_exercise="The Two-Breath Rule: If you cannot comfortably utter a sentence in a single calm breath, insert a period and begin a new sentence.",
            severity="medium",
            evaluator_method="flesch_kincaid_syntactic_analyzer",
            limitations="Flesch formula is based on syllable count and sentence length; specialized domain terminology naturally lowers the index."
        ))

    # 6. Positive Feedback: Celebrate Strengths
    if total_fillers <= 2 and total_words > 40:
        items.append(FeedbackItem(
            feedback_id=f"FB-{uuid.uuid4().hex[:8].upper()}",
            rubric_criterion="fluency_and_pacing",
            criterion_name="Fluency & Pacing",
            observed_issue="Exemplary fluency control; minimal verbal fillers detected.",
            evidence_type="transcript_pattern",
            transcript_excerpt=None,
            timestamp_range=None,
            measured_value=f"Only {total_fillers} filler(s) in {total_words} words ({round(filler_density, 1)}%)",
            explanation="You demonstrated discipline by maintaining clean transitions between thoughts.",
            recommended_action="Continue using this calm cadence across higher-pressure speaking scenarios.",
            example_rewrite_or_exercise="Maintenance drill: Challenge yourself to maintain this clean delivery in unscripted Q&A sessions.",
            severity="positive",
            evaluator_method="lexical_pattern_density_analyzer",
            limitations="Verified against standard filler dictionary."
        ))

    return items
