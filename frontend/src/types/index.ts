/**
 * TypeScript Data Models for OratorIQ — Evidence-Based Speech Coach.
 * Synchronized with backend Pydantic schemas (oratoriq/models/schemas.py).
 */

export type SpeechScenario =
  | "public_speaking"
  | "interview_answers"
  | "persuasive_pitches"
  | "presentation_delivery"
  | "academic_explanations";

export interface WordSpan {
  word: string;
  start_time?: number | null;
  end_time?: number | null;
  confidence?: number | null;
  tag?: string | null;
}

export interface SegmentSpan {
  id: number;
  text: string;
  start_time?: number | null;
  end_time?: number | null;
}

export interface FillerDetected {
  word: string;
  count: number;
  description: string;
}

export interface RepetitionDetected {
  phrase: string;
  position: number;
}

export interface TranscriptAnnotation {
  text: string;
  segments: SegmentSpan[];
  words: WordSpan[];
  filler_words_detected: FillerDetected[];
  repetitions_detected: RepetitionDetected[];
  readability_flesch_score: number;
  detected_language: string;
}

export interface AudioFeatures {
  duration_sec: number;
  speaking_rate_wpm?: number | null;
  total_words: number;
  total_pauses: number;
  mean_pause_duration_sec: number;
  max_pause_duration_sec: number;
  silent_region_proportion: number;
  pitch_f0_mean_hz?: number | null;
  pitch_f0_std_hz?: number | null;
  pitch_semitone_range?: number | null;
  is_monotonous?: boolean | null;
  rms_energy_mean: number;
  dynamic_range_db: number;
  clipping_ratio: number;
  snr_db_estimate: number;
  is_audio_available: boolean;
}

export interface ScoringAnchor {
  score: number;
  name: string;
  description: string;
  observable_indicators?: string[];
}

export interface CriterionConfig {
  id: string;
  name: string;
  weight: number;
  description: string;
  requires_audio: boolean;
  anchors: Record<string, ScoringAnchor>;
}

export interface RubricDefinition {
  rubric_id: string;
  name: string;
  version: string;
  description: string;
  criteria: Record<string, CriterionConfig>;
  rubric_hash: string;
  is_active: boolean;
  created_at: string;
}

export interface CriterionScoreResult {
  criterion_id: string;
  criterion_name: string;
  raw_rating?: number | null;
  normalized_score?: number | null;
  weight: number;
  status: "evaluated" | "unavailable" | "skipped";
  reason?: string | null;
  evidence_summary: string;
  scoring_anchor_matched?: string | null;
}

export interface FeedbackItem {
  feedback_id: string;
  rubric_criterion: string;
  criterion_name: string;
  observed_issue: string;
  evidence_type: string;
  transcript_excerpt?: string | null;
  timestamp_range?: { start: number; end: number } | null;
  measured_value?: string | null;
  explanation: string;
  recommended_action: string;
  example_rewrite_or_exercise: string;
  severity: "high" | "medium" | "low" | "positive";
  evaluator_method: string;
  limitations: string;
}

export interface ContrastiveMatch {
  matched_pair_id: string;
  scenario: string;
  primary_flaw: string;
  ideal_sample_id: string;
  flawed_sample_id: string;
  similarity_explanation: string;
  contrastive_delta_analysis: string;
}

export interface EvaluationResult {
  run_id: string;
  created_at: string;
  evaluation_mode: "audio_plus_transcript" | "transcript_only";
  scenario: string;
  speech_prompt?: string | null;
  overall_score: number;
  grade: string;
  coverage_ratio: number;
  coverage_percentage: number;
  eligible_criteria_count: number;
  evaluated_criteria_count: number;
  missing_criteria: string[];
  criterion_scores: Record<string, CriterionScoreResult>;
  audio_features?: AudioFeatures | null;
  transcript_annotation: TranscriptAnnotation;
  feedback_items: FeedbackItem[];
  contrastive_matches: ContrastiveMatch[];
  reproducibility: Record<string, any>;
}

export interface SpeechSample {
  sample_id: string;
  pair_id: string;
  scenario: string;
  language: string;
  intended_audience: string;
  communication_goal: string;
  transcript: string;
  audio_reference?: string | null;
  example_type: "ideal" | "flawed";
  flaw_categories: string[];
  severity: string;
  rubric_labels: Record<string, number>;
  annotation_rationale: string;
  provenance: string;
  annotation_status: string;
  dataset_version: string;
}

export interface ContrastivePair {
  pair_id: string;
  scenario: string;
  intended_audience: string;
  communication_goal: string;
  ideal_sample: SpeechSample;
  flawed_sample: SpeechSample;
  primary_flaw: string;
  flaw_severity: string;
  contrastive_rationale: string;
  dataset_version: string;
}

export interface DatasetManifest {
  version: string;
  dataset_hash: string;
  total_pairs: number;
  total_samples: number;
  scenarios_breakdown: Record<string, number>;
  flaw_taxonomy: Record<string, number>;
  file_path: string;
}

export interface EvaluationRunSummary {
  run_id: string;
  created_at: string;
  scenario: string;
  evaluation_mode: string;
  overall_score: number;
  grade: string;
  coverage_percentage: number;
  evaluated_criteria_count: number;
  rubric_version?: string;
  dataset_version?: string;
  transcript_preview: string;
}
