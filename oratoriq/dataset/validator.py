"""
Dataset Validation Tool for OratorIQ Contrastive Speech Corpus.
Run via: python -m oratoriq.dataset.validator [optional_path]
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any
from pydantic import ValidationError

from oratoriq.models.schemas import (
    ContrastivePair,
    SpeechScenario,
    FlawCategory
)
from oratoriq.dataset.dataset_loader import ContrastiveDataset


def validate_dataset_records(file_path: str) -> Dict[str, Any]:
    """
    Performs comprehensive structural, semantic, and integrity validation
    on the contrastive speech dataset file.
    """
    report = {
        "is_valid": True,
        "file_path": file_path,
        "total_pairs_checked": 0,
        "total_samples_checked": 0,
        "errors": [],
        "warnings": [],
        "dataset_hash": None,
        "scenarios": {},
        "flaw_categories": {}
    }

    if not os.path.exists(file_path):
        report["is_valid"] = False
        report["errors"].append(f"File not found: {file_path}")
        return report

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        report["is_valid"] = False
        report["errors"].append(f"JSON parsing error: {str(e)}")
        return report

    if not isinstance(data, list):
        report["is_valid"] = False
        report["errors"].append("Dataset root must be a JSON array of contrastive pairs.")
        return report

    seen_pair_ids = set()
    seen_sample_ids = set()
    seen_transcripts = set()

    for idx, raw_pair in enumerate(data):
        report["total_pairs_checked"] += 1
        pair_id = raw_pair.get("pair_id", f"INDEX-{idx}")

        # Check duplicate pair ID
        if pair_id in seen_pair_ids:
            report["errors"].append(f"Duplicate pair_id detected: '{pair_id}' at index {idx}.")
            report["is_valid"] = False
        seen_pair_ids.add(pair_id)

        # Validate with Pydantic
        try:
            pair = ContrastivePair(**raw_pair)
        except ValidationError as ve:
            report["is_valid"] = False
            for err in ve.errors():
                loc = " -> ".join(str(l) for l in err.get("loc", []))
                report["errors"].append(f"Pair '{pair_id}' Schema Error: {loc} - {err.get('msg')}")
            continue

        # Check pair consistency: exactly one ideal and one flawed
        if pair.ideal_sample.example_type != "ideal":
            report["errors"].append(f"Pair '{pair_id}': ideal_sample must have example_type='ideal'.")
            report["is_valid"] = False

        if pair.flawed_sample.example_type != "flawed":
            report["errors"].append(f"Pair '{pair_id}': flawed_sample must have example_type='flawed'.")
            report["is_valid"] = False

        # Validate scenario against known scenarios
        if pair.scenario not in SpeechScenario.ALL:
            report["warnings"].append(f"Pair '{pair_id}': Scenario '{pair.scenario}' is not in standard SpeechScenario enum.")

        # Check sample IDs
        for sample in [pair.ideal_sample, pair.flawed_sample]:
            report["total_samples_checked"] += 1
            if sample.sample_id in seen_sample_ids:
                report["errors"].append(f"Duplicate sample_id detected: '{sample.sample_id}' in pair '{pair_id}'.")
                report["is_valid"] = False
            seen_sample_ids.add(sample.sample_id)

            # Check transcript duplication / leakage
            clean_text = " ".join(sample.transcript.lower().split())
            if clean_text in seen_transcripts:
                report["warnings"].append(f"Near-duplicate transcript detected for sample '{sample.sample_id}'.")
            seen_transcripts.add(clean_text)

            # Validate rubric ratings (1 to 5)
            required_rubric_keys = [
                "content_and_relevance",
                "structure_and_coherence",
                "fluency_and_pacing",
                "vocal_delivery",
                "clarity_and_conciseness"
            ]
            for r_key in required_rubric_keys:
                if r_key not in sample.rubric_labels:
                    report["errors"].append(f"Sample '{sample.sample_id}': Missing rubric label '{r_key}'.")
                    report["is_valid"] = False
                else:
                    score = sample.rubric_labels[r_key]
                    if not (1 <= score <= 5):
                        report["errors"].append(f"Sample '{sample.sample_id}': Rubric score for '{r_key}' must be between 1 and 5 (got {score}).")
                        report["is_valid"] = False

        # Accumulate metrics
        sc = pair.scenario
        report["scenarios"][sc] = report["scenarios"].get(sc, 0) + 1

        fl = pair.primary_flaw
        report["flaw_categories"][fl] = report["flaw_categories"].get(fl, 0) + 1

    # Load via dataset loader to get canonical content hash
    try:
        ds = ContrastiveDataset(file_path)
        report["dataset_hash"] = ds.dataset_hash
    except Exception as e:
        report["errors"].append(f"Failed to load dataset via loader: {str(e)}")
        report["is_valid"] = False

    return report


def main():
    parser = argparse.ArgumentParser(description="Validate OratorIQ Contrastive Speech Dataset")
    parser.add_argument("path", nargs="?", default=None, help="Path to starter_pairs.json (defaults to built-in)")
    args = parser.parse_args()

    target_path = args.path
    if not target_path:
        target_path = os.path.join(os.path.dirname(__file__), "starter_pairs.json")

    print("=" * 72)
    print("  ORATORIQ CONTRASTIVE SPEECH DATASET: SCHEMA & INTEGRITY AUDITOR")
    print(f"  Target File: {target_path}")
    print("=" * 72)

    report = validate_dataset_records(target_path)

    print(f"\n[Validation Status]: {'PASSED (OK)' if report['is_valid'] else 'FAILED (ERRORS DETECTED)'}")
    print(f"Total Pairs Verified  : {report['total_pairs_checked']}")
    print(f"Total Samples Verified: {report['total_samples_checked']}")
    print(f"Dataset SHA-256 Hash  : {report['dataset_hash']}")
    print(f"Scenarios Breakdown   : {report['scenarios']}")
    print(f"Primary Flaws         : {len(report['flaw_categories'])} distinct categories")

    if report["warnings"]:
        print(f"\n[Warnings ({len(report['warnings'])})]:")
        for w in report["warnings"][:10]:
            print(f"  - {w}")

    if not report["is_valid"]:
        print(f"\n[CRITICAL ERRORS ({len(report['errors'])})]:")
        for err in report["errors"]:
            print(f"  [ERROR] {err}")
        sys.exit(1)
    else:
        print("\nAll schema boundaries, duplicate checks, pair consistencies, and rubric ranges validated successfully!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
