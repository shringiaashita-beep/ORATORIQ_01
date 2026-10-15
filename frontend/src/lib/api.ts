/**
 * API Client for OratorIQ Speech Evaluation Engine.
 * Connects to FastAPI backend endpoints under /api/v1.
 */

import {
  EvaluationResult,
  DatasetManifest,
  ContrastivePair,
  RubricDefinition,
  EvaluationRunSummary
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchHealth(): Promise<{ status: string; service: string; version: string; capabilities: string[] }> {
  const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchReadiness(): Promise<{
  status: string;
  dataset_status: { loaded_pairs: number; dataset_hash: string; version: string };
  audio_engine: { status: string; backend: string; supported_formats: string[] };
  transcription_engine: { local_alignment: string; whisper_api: string; details: string };
}> {
  const res = await fetch(`${API_BASE}/ready`, { cache: "no-store" });
  if (!res.ok) throw new Error("Readiness check failed");
  return res.json();
}

export async function evaluateSpeechAudio(formData: FormData): Promise<EvaluationResult> {
  const res = await fetch(`${API_BASE}/evaluations/audio`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    const detailsStr = errData.details
      ? Array.isArray(errData.details) ? errData.details.join("; ") : String(errData.details)
      : null;
    const msg = detailsStr
      ? `${errData.message || "Validation Error"}: ${detailsStr}`
      : errData.detail || errData.message || `Evaluation failed with status ${res.status}`;
    throw new Error(msg);
  }
  return res.json();
}

export async function evaluateSpeechTranscript(payload: {
  transcript: string;
  scenario: string;
  rubric_id: string;
  speech_prompt?: string;
}): Promise<EvaluationResult> {
  const res = await fetch(`${API_BASE}/evaluations/transcript`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    const detailsStr = errData.details
      ? Array.isArray(errData.details) ? errData.details.join("; ") : String(errData.details)
      : null;
    const msg = detailsStr
      ? `${errData.message || "Validation Error"}: ${detailsStr}`
      : errData.detail || errData.message || `Evaluation failed with status ${res.status}`;
    throw new Error(msg);
  }
  return res.json();
}

export async function getEvaluationById(runId: string): Promise<EvaluationResult> {
  const res = await fetch(`${API_BASE}/evaluations/${runId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Run ${runId} not found`);
  return res.json();
}

export async function getDatasetManifest(): Promise<DatasetManifest> {
  const res = await fetch(`${API_BASE}/datasets`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load dataset manifest");
  return res.json();
}

export async function getContrastivePairs(scenario?: string, flaw?: string): Promise<{ status: string; total_pairs: number; pairs: ContrastivePair[] }> {
  const params = new URLSearchParams();
  if (scenario && scenario !== "ALL") params.append("scenario", scenario);
  if (flaw && flaw !== "ALL") params.append("flaw", flaw);

  const url = `${API_BASE}/datasets/pairs${params.toString() ? `?${params.toString()}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load contrastive pairs");
  return res.json();
}

export async function validateDataset(): Promise<{
  is_valid: boolean;
  file_path: string;
  total_pairs_checked: number;
  total_samples_checked: number;
  errors: string[];
  warnings: string[];
  dataset_hash?: string;
  scenarios: Record<string, number>;
  flaw_categories: Record<string, number>;
}> {
  const res = await fetch(`${API_BASE}/datasets/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!res.ok) throw new Error("Dataset validation endpoint returned an error");
  return res.json();
}

export async function listRubrics(): Promise<{ status: string; rubrics: RubricDefinition[] }> {
  const res = await fetch(`${API_BASE}/rubrics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch rubrics");
  return res.json();
}

export async function saveRubric(payload: {
  rubric_id: string;
  name: string;
  version: string;
  criteria: Record<string, any>;
}): Promise<{ status: string; message: string; rubric: RubricDefinition }> {
  const res = await fetch(`${API_BASE}/rubrics`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Failed to register custom rubric");
  }
  return res.json();
}

export async function getEvaluationHistory(scenario?: string): Promise<{ status: string; total_runs: number; runs: EvaluationRunSummary[] }> {
  const params = new URLSearchParams();
  if (scenario) params.append("scenario", scenario);
  const url = `${API_BASE}/history${params.toString() ? `?${params.toString()}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load evaluation history");
  return res.json();
}

export function getHtmlReportUrl(runId: string): string {
  return `${API_BASE}/evaluations/${runId}/export.html`;
}
