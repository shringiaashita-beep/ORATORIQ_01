"""
Evaluation Quality and Statistical Benchmark Suite for OratorIQ.

Empirically measures the evaluation engine against the 52-pair (104-sample)
curated contrastive dataset:
1. Pairwise Ranking Accuracy: overall_score(ideal) > overall_score(flawed)
2. Target Dimension Sensitivity: flawed sample rating < ideal sample rating on target flaw
3. Mean Absolute Error (MAE) against curated 1-5 ground-truth rubric labels
4. Repeat-run Determinism: exact score and hash consistency across repeated evaluations
5. Input boundary handling and missing-data safety
"""

import math
import pytest
from oratoriq.dataset.dataset_loader import ContrastiveDataset
from oratoriq.evaluator.engine import OratorIQEvaluationEngine
from oratoriq.audio.transcriber import OratorIQTranscriber


@pytest.fixture(scope="module")
def evaluation_context():
    dataset = ContrastiveDataset()
    engine = OratorIQEvaluationEngine(dataset=dataset)
    transcriber = OratorIQTranscriber()
    pairs = dataset.get_all_pairs()
    return {
        "dataset": dataset,
        "engine": engine,
        "transcriber": transcriber,
        "pairs": pairs
    }


def test_contrastive_pairwise_ranking_accuracy(evaluation_context):
    """
    Evaluates whether ideal speeches consistently rank higher than flawed speeches
    within the same contrastive communication scenario.
    """
    pairs = evaluation_context["pairs"]
    engine = evaluation_context["engine"]
    transcriber = evaluation_context["transcriber"]

    total_pairs = len(pairs)
    assert total_pairs >= 50, f"Expected at least 50 pairs, found {total_pairs}"

    correct_pairs = 0
    score_deltas = []

    for pair in pairs:
        # Ideal sample evaluation
        ideal_annot = transcriber.transcribe(
            audio_signal=None,
            sr=0,
            provided_transcript=pair.ideal_sample.transcript
        )
        ideal_res = engine.evaluate(
            ideal_annot,
            scenario=pair.scenario,
            speech_prompt=pair.communication_goal
        )

        # Flawed sample evaluation
        flawed_annot = transcriber.transcribe(
            audio_signal=None,
            sr=0,
            provided_transcript=pair.flawed_sample.transcript
        )
        flawed_res = engine.evaluate(
            flawed_annot,
            scenario=pair.scenario,
            speech_prompt=pair.communication_goal
        )

        assert ideal_res.overall_score is not None
        assert flawed_res.overall_score is not None

        delta = ideal_res.overall_score - flawed_res.overall_score
        score_deltas.append(delta)

        if delta > 0:
            correct_pairs += 1

    accuracy = (correct_pairs / total_pairs) * 100.0
    mean_delta = sum(score_deltas) / float(total_pairs)

    print(f"\n[Pairwise Ranking Benchmark] Evaluated {total_pairs} pairs.")
    print(f"Accuracy: {accuracy:.1f}% ({correct_pairs}/{total_pairs} pairs)")
    print(f"Mean Ideal-vs-Flawed Score Advantage: +{mean_delta:.2f} points (on 0-100 scale)")

    # The engine must separate ideal and flawed samples with high accuracy (>= 90%)
    assert accuracy >= 90.0, f"Pairwise ranking accuracy too low: {accuracy:.1f}%"
    assert mean_delta >= 15.0, f"Mean separation delta too low: {mean_delta:.2f} points"


def test_target_dimension_sensitivity(evaluation_context):
    """
    Verifies that the specific flaw targeted in the pair is detected
    on its corresponding rubric criterion.
    """
    pairs = evaluation_context["pairs"]
    engine = evaluation_context["engine"]
    transcriber = evaluation_context["transcriber"]

    flaw_to_criterion = {
        "weak_opening": "structure_and_coherence",
        "poor_logical_structure": "structure_and_coherence",
        "weak_transitions": "structure_and_coherence",
        "weak_or_missing_conclusion": "structure_and_coherence",
        "excessive_filler_words": "fluency_and_pacing",
        "unnecessary_repetition": "clarity_and_conciseness",
        "unclear_articulation": "clarity_and_conciseness",
        "unsupported_claims": "content_and_relevance",
        "failure_to_answer_question": "content_and_relevance",
    }

    evaluated_flaw_checks = 0
    detected_flaw_checks = 0

    for pair in pairs:
        target_criterion = flaw_to_criterion.get(pair.primary_flaw)
        if not target_criterion:
            continue

        ideal_annot = transcriber.transcribe(
            audio_signal=None,
            sr=0,
            provided_transcript=pair.ideal_sample.transcript
        )
        ideal_res = engine.evaluate(ideal_annot, scenario=pair.scenario, speech_prompt=pair.communication_goal)

        flawed_annot = transcriber.transcribe(
            audio_signal=None,
            sr=0,
            provided_transcript=pair.flawed_sample.transcript
        )
        flawed_res = engine.evaluate(flawed_annot, scenario=pair.scenario, speech_prompt=pair.communication_goal)

        ideal_rating = ideal_res.criterion_scores[target_criterion].raw_rating
        flawed_rating = flawed_res.criterion_scores[target_criterion].raw_rating

        if ideal_rating is not None and flawed_rating is not None:
            evaluated_flaw_checks += 1
            if flawed_rating < ideal_rating:
                detected_flaw_checks += 1

    sensitivity = (detected_flaw_checks / max(1, evaluated_flaw_checks)) * 100.0
    print(f"\n[Target Flaw Sensitivity] Evaluated {evaluated_flaw_checks} text-flaw instances.")
    print(f"Sensitivity: {sensitivity:.1f}% ({detected_flaw_checks}/{evaluated_flaw_checks})")

    assert sensitivity >= 80.0, f"Target flaw sensitivity too low: {sensitivity:.1f}%"


def test_mean_absolute_error_vs_ground_truth(evaluation_context):
    """
    Computes the Mean Absolute Error (MAE) between engine 1-5 ratings
    and human curated ground-truth ratings across all 104 samples.
    """
    pairs = evaluation_context["pairs"]
    engine = evaluation_context["engine"]
    transcriber = evaluation_context["transcriber"]

    evaluated_criteria = ["content_and_relevance", "structure_and_coherence", "fluency_and_pacing", "clarity_and_conciseness"]
    criterion_errors = {c: [] for c in evaluated_criteria}

    all_samples = []
    for p in pairs:
        all_samples.append((p.ideal_sample, p.scenario, p.communication_goal))
        all_samples.append((p.flawed_sample, p.scenario, p.communication_goal))

    for sample, scenario, prompt in all_samples:
        annot = transcriber.transcribe(audio_signal=None, sr=0, provided_transcript=sample.transcript)
        res = engine.evaluate(annot, scenario=scenario, speech_prompt=prompt)

        for c in evaluated_criteria:
            predicted_rating = res.criterion_scores[c].raw_rating
            ground_truth_rating = sample.rubric_labels.get(c)
            if predicted_rating is not None and ground_truth_rating is not None:
                err = abs(predicted_rating - ground_truth_rating)
                criterion_errors[c].append(err)

    overall_errors = []
    print("\n[Mean Absolute Error vs Ground Truth Labels (1-5 Scale)]")
    for c, errs in criterion_errors.items():
        if errs:
            mae = sum(errs) / float(len(errs))
            overall_errors.extend(errs)
            print(f"  {c:<26}: MAE = {mae:.2f} rating points (N={len(errs)})")

    overall_mae = sum(overall_errors) / float(len(overall_errors))
    print(f"  Overall Combined MAE     : {overall_mae:.2f} rating points (N={len(overall_errors)})")

    # The MAE should be within ~0.85 rating points on a 1-5 ordinal scale
    assert overall_mae <= 0.85, f"Overall MAE {overall_mae:.2f} exceeds tolerance (0.85)"


def test_evaluation_repeat_run_determinism(evaluation_context):
    """
    Verifies that running evaluation on the same input multiple times
    produces identical ratings, normalized scores, and input hashes.
    """
    engine = evaluation_context["engine"]
    transcriber = evaluation_context["transcriber"]

    text = "We achieved fifty percent reduction in latency by refactoring our SQL queries."
    annot1 = transcriber.transcribe(audio_signal=None, sr=0, provided_transcript=text)
    res1 = engine.evaluate(annot1, scenario="presentation_delivery")

    annot2 = transcriber.transcribe(audio_signal=None, sr=0, provided_transcript=text)
    res2 = engine.evaluate(annot2, scenario="presentation_delivery")

    assert res1.overall_score == res2.overall_score
    assert res1.reproducibility["input_sha256"] == res2.reproducibility["input_sha256"]
    assert res1.reproducibility["dataset_hash"] == res2.reproducibility["dataset_hash"]
    assert res1.reproducibility["rubric_hash"] == res2.reproducibility["rubric_hash"]
    for c_id in res1.criterion_scores:
        assert res1.criterion_scores[c_id].raw_rating == res2.criterion_scores[c_id].raw_rating
        assert res1.criterion_scores[c_id].normalized_score == res2.criterion_scores[c_id].normalized_score
