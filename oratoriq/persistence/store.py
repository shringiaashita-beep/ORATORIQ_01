"""
Evaluation History, Run Persistence, and Reproducibility Store for OratorIQ.
"""

import os
import json
import glob
from typing import Dict, List, Optional, Any
from oratoriq.models.schemas import EvaluationResult


class EvaluationStore:
    """Manages persistent disk storage and retrieval of evaluation runs."""

    def __init__(self, storage_dir: Optional[str] = None):
        if not storage_dir:
            storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "runs")
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def save_run(self, result: EvaluationResult) -> str:
        """Persists evaluation result to disk keyed by run_id."""
        file_path = os.path.join(self.storage_dir, f"{result.run_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
        return file_path

    def get_run(self, run_id: str) -> Optional[EvaluationResult]:
        """Loads a stored evaluation run by run_id."""
        clean_id = os.path.basename(run_id).replace(".json", "")
        file_path = os.path.join(self.storage_dir, f"{clean_id}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return EvaluationResult(**data)

    def list_runs(self, limit: int = 50, scenario: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns indexed summaries of historical evaluation runs sorted descending by time."""
        files = glob.glob(os.path.join(self.storage_dir, "*.json"))
        # Sort by modification time desc
        files.sort(key=os.path.getmtime, reverse=True)

        runs = []
        for fp in files[:limit]:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    d = json.load(f)
                if scenario and d.get("scenario") != scenario:
                    continue
                runs.append({
                    "run_id": d.get("run_id"),
                    "created_at": d.get("created_at"),
                    "scenario": d.get("scenario"),
                    "evaluation_mode": d.get("evaluation_mode"),
                    "overall_score": d.get("overall_score"),
                    "grade": d.get("grade"),
                    "coverage_percentage": d.get("coverage_percentage"),
                    "evaluated_criteria_count": d.get("evaluated_criteria_count"),
                    "rubric_version": d.get("reproducibility", {}).get("rubric_version"),
                    "dataset_version": d.get("reproducibility", {}).get("dataset_version"),
                    "transcript_preview": (d.get("transcript_annotation", {}).get("text", "")[:100] + "...")
                })
            except Exception:
                continue

        return runs

    def generate_html_report(self, result: EvaluationResult) -> str:
        """Generates a standalone, beautifully styled printable HTML report for the evaluation."""
        c_rows = ""
        for c_id, cr in result.criterion_scores.items():
            score_str = f"{cr.normalized_score} / 100" if cr.normalized_score is not None else "UNAVAILABLE"
            rating_str = f"{cr.raw_rating} / 5" if cr.raw_rating is not None else "N/A"
            status_badge = f"<span class='badge badge-{cr.status}'>{cr.status.upper()}</span>"
            c_rows += f"""
            <tr>
              <td><strong>{cr.criterion_name}</strong></td>
              <td>{int(cr.weight * 100)}%</td>
              <td>{rating_str}</td>
              <td><strong>{score_str}</strong> {status_badge}</td>
              <td class='evidence-cell'>{cr.evidence_summary}</td>
            </tr>
            """

        fb_cards = ""
        for fb in result.feedback_items:
            fb_cards += f"""
            <div class='feedback-card severity-{fb.severity}'>
              <div class='feedback-header'>
                <span class='badge'>{fb.criterion_name}</span>
                <span class='severity-tag'>{fb.severity.upper()}</span>
              </div>
              <h4>{fb.observed_issue}</h4>
              <p><strong>Measured Value:</strong> <code>{fb.measured_value or 'N/A'}</code></p>
              <p class='explanation'>{fb.explanation}</p>
              <div class='action-box'>
                <p><strong>Action:</strong> {fb.recommended_action}</p>
                <p><strong>Practice Drill:</strong> {fb.example_rewrite_or_exercise}</p>
              </div>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OratorIQ Evaluation Report — {result.run_id}</title>
  <style>
    body {{ font-family: 'Inter', -apple-system, sans-serif; background: #070a12; color: #f8fafc; margin: 0; padding: 40px; line-height: 1.6; }}
    .report-container {{ max-width: 900px; margin: 0 auto; background: #0e1424; padding: 40px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }}
    .header {{ border-bottom: 2px solid rgba(99, 102, 241, 0.4); padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
    h1 {{ margin: 0; color: #6366f1; font-size: 26px; }}
    .badge {{ background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }}
    .badge-evaluated {{ background: rgba(16, 185, 129, 0.2); color: #34d399; }}
    .badge-unavailable {{ background: rgba(239, 68, 68, 0.2); color: #f87171; }}
    .score-banner {{ display: flex; gap: 20px; margin-bottom: 30px; }}
    .score-card {{ flex: 1; background: #161f36; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,255,255,0.05); }}
    .score-number {{ font-size: 42px; font-weight: 800; color: #06b6d4; margin: 10px 0 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th, td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.08); font-size: 14px; }}
    th {{ background: #161f36; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 11px; }}
    .evidence-cell {{ font-size: 13px; color: #cbd5e1; }}
    .feedback-card {{ background: #161f36; border-left: 4px solid #6366f1; padding: 18px; border-radius: 6px; margin-bottom: 16px; }}
    .severity-high {{ border-left-color: #ef4444; }}
    .severity-medium {{ border-left-color: #f59e0b; }}
    .severity-positive {{ border-left-color: #10b981; }}
    .action-box {{ background: rgba(0,0,0,0.25); padding: 12px; border-radius: 6px; margin-top: 10px; font-size: 13px; }}
    .audit-footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 12px; color: #64748b; font-family: monospace; }}
    @media print {{ body {{ background: #fff; color: #000; padding: 0; }} .report-container {{ border: none; background: #fff; }} }}
  </style>
</head>
<body>
  <div class="report-container">
    <div class="header">
      <div>
        <h1>OratorIQ — Evidence-Based Speech Evaluation Report</h1>
        <p style="margin: 4px 0 0; color: #94a3b8; font-size: 13px;">Run ID: <strong>{result.run_id}</strong> • Scenario: <strong>{result.scenario}</strong></p>
      </div>
      <span class="badge">{result.evaluation_mode.replace('_', ' ').title()}</span>
    </div>

    <div class="score-banner">
      <div class="score-card">
        <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Overall Rubric Score</div>
        <div class="score-number">{result.overall_score if result.overall_score is not None else 'N/A'} <span style="font-size: 20px; color: #94a3b8;">/ 100</span></div>
      </div>
      <div class="score-card">
        <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Performance Grade</div>
        <div class="score-number" style="color: #6366f1;">{result.grade}</div>
      </div>
      <div class="score-card">
        <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">Rubric Coverage</div>
        <div class="score-number" style="color: #10b981;">{result.coverage_percentage}%</div>
      </div>
    </div>

    <h3>Rubric Criterion Breakdown</h3>
    <table>
      <thead>
        <tr>
          <th>Criterion</th>
          <th>Weight</th>
          <th>Rating (1-5)</th>
          <th>Normalized Score</th>
          <th>Evidence & Observations</th>
        </tr>
      </thead>
      <tbody>
        {c_rows}
      </tbody>
    </table>

    <h3 style="margin-top: 36px;">Evidence-Linked Actionable Recommendations</h3>
    {fb_cards if fb_cards else "<p style='color: #94a3b8;'>No critical delivery issues detected.</p>"}

    <h3 style="margin-top: 36px;">Speech Transcript & Diagnostics</h3>
    <div style="background: #161f36; padding: 16px; border-radius: 8px; font-size: 13px; line-height: 1.7; border: 1px solid rgba(255,255,255,0.05);">
      {result.transcript_annotation.text}
    </div>

    <div class="audit-footer">
      <div>Reproducibility Fingerprint:</div>
      <div>Input SHA-256: {result.reproducibility.get('input_sha256')}</div>
      <div>Rubric Hash: {result.reproducibility.get('rubric_hash')} (v{result.reproducibility.get('rubric_version')})</div>
      <div>Dataset Hash: {result.reproducibility.get('dataset_hash')} (v{result.reproducibility.get('dataset_version')})</div>
      <div>Timestamp UTC: {result.created_at}</div>
    </div>
  </div>
</body>
</html>
        """
        return html
