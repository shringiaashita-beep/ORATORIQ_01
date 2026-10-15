"""
Dataset Loader, Indexer, and Manifest Engine for OratorIQ Contrastive Speech Dataset.
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Any
from oratoriq.models.schemas import ContrastivePair, SpeechSample


class ContrastiveDataset:
    """Manages loading, hashing, and indexing of the contrastive speech dataset."""

    def __init__(self, dataset_path: Optional[str] = None):
        if not dataset_path:
            dataset_path = os.path.join(os.path.dirname(__file__), "starter_pairs.json")
        self.dataset_path = dataset_path
        self._pairs: Dict[str, ContrastivePair] = {}
        self._by_scenario: Dict[str, List[ContrastivePair]] = {}
        self._by_flaw: Dict[str, List[ContrastivePair]] = {}
        self.version = "1.0.0"
        self.dataset_hash = ""
        self.load()

    def load(self):
        """Loads and parses the dataset from disk, building indexes and computing hash."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Contrastive dataset file not found at: {self.dataset_path}")

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        pairs_dict: Dict[str, ContrastivePair] = {}
        by_scenario: Dict[str, List[ContrastivePair]] = {}
        by_flaw: Dict[str, List[ContrastivePair]] = {}

        # Compute deterministic hash over sorted canonical JSON
        canonical_str = json.dumps(raw_data, sort_keys=True)
        self.dataset_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        for item in raw_data:
            # Validate through Pydantic
            pair = ContrastivePair(**item)
            pairs_dict[pair.pair_id] = pair

            scenario = pair.scenario
            if scenario not in by_scenario:
                by_scenario[scenario] = []
            by_scenario[scenario].append(pair)

            flaw = pair.primary_flaw
            if flaw not in by_flaw:
                by_flaw[flaw] = []
            by_flaw[flaw].append(pair)

            self.version = pair.dataset_version

        self._pairs = pairs_dict
        self._by_scenario = by_scenario
        self._by_flaw = by_flaw

    def get_pair(self, pair_id: str) -> Optional[ContrastivePair]:
        return self._pairs.get(pair_id)

    def get_all_pairs(self) -> List[ContrastivePair]:
        return list(self._pairs.values())

    def get_pairs_by_scenario(self, scenario: str) -> List[ContrastivePair]:
        return self._by_scenario.get(scenario, [])

    def get_pairs_by_flaw(self, flaw: str) -> List[ContrastivePair]:
        return self._by_flaw.get(flaw, [])

    def get_manifest(self) -> Dict[str, Any]:
        """Returns structured metadata and telemetry for dataset integrity."""
        return {
            "dataset_name": "OratorIQ Contrastive Speech Corpus",
            "version": self.version,
            "dataset_hash": self.dataset_hash,
            "total_pairs": len(self._pairs),
            "total_samples": len(self._pairs) * 2,
            "scenarios_distribution": {
                sc: len(pairs) for sc, pairs in self._by_scenario.items()
            },
            "primary_flaws_distribution": {
                fl: len(pairs) for fl, pairs in self._by_flaw.items()
            },
            "provenance": "authored_expert_curated",
            "annotation_status": "reviewed",
            "acoustic_grounding": "transcript_only_starter_with_audio_alignment_ready"
        }
