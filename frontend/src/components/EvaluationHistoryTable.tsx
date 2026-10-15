"use client";

import React, { useState, useEffect } from "react";
import { EvaluationRunSummary } from "@/types";
import { getEvaluationHistory, getHtmlReportUrl } from "@/lib/api";

interface EvaluationHistoryTableProps {
  onSelectRun: (runId: string) => void;
}

export function EvaluationHistoryTable({ onSelectRun }: EvaluationHistoryTableProps) {
  const [runs, setRuns] = useState<EvaluationRunSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedScenario, setSelectedScenario] = useState<string>("ALL");

  useEffect(() => {
    loadHistory();
  }, [selectedScenario]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getEvaluationHistory(selectedScenario === "ALL" ? undefined : selectedScenario);
      setRuns(data.runs || []);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const scenarios = [
    { id: "ALL", label: "All Scenarios" },
    { id: "public_speaking", label: "Public Speaking" },
    { id: "interview_answers", label: "Interview Answers" },
    { id: "persuasive_pitches", label: "Persuasive Pitches" },
    { id: "presentation_delivery", label: "Presentation Delivery" },
    { id: "academic_explanations", label: "Academic Explanations" },
  ];

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white tracking-wide flex items-center space-x-2">
              <span>Historical Evaluation Runs</span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-[#6366F1]/20 text-[#818CF8] border border-[#6366F1]/30">
                {runs.length} Saved Evaluations
              </span>
            </h2>
            <p className="text-xs text-[#94A3B8] mt-1">
              Verifiable audit trail of speech evaluations with rubric versions, mode transparency, and exportable reports
            </p>
          </div>

          {/* Refresh button */}
          <button
            onClick={loadHistory}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-[#131E33] hover:bg-[#1E2E4A] text-[#94A3B8] hover:text-white text-xs border border-[#1E2E4A] transition-colors"
          >
            <svg viewBox="0 0 24 24" className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 4v6h-6"></path>
              <path d="M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            <span>Refresh</span>
          </button>
        </div>

        {/* Filter pills */}
        <div className="flex flex-wrap items-center gap-1.5 mt-5 pt-4 border-t border-[#1E2E4A]">
          {scenarios.map((sc) => (
            <button
              key={sc.id}
              onClick={() => setSelectedScenario(sc.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedScenario === sc.id
                  ? "bg-[#6366F1] text-white shadow-sm"
                  : "bg-[#131E33] text-[#94A3B8] hover:text-white hover:bg-[#1E2E4A]"
              }`}
            >
              {sc.label}
            </button>
          ))}
        </div>
      </div>

      {/* Runs Table */}
      <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-12 text-center text-xs text-[#94A3B8]">
            <svg viewBox="0 0 24 24" className="w-6 h-6 text-[#6366F1] animate-spin mx-auto mb-2" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 2a10 10 0 0 1 10 10"></path>
            </svg>
            Loading evaluation history...
          </div>
        ) : runs.length === 0 ? (
          <div className="p-12 text-center text-xs text-[#94A3B8] space-y-2">
            <p>No evaluations recorded yet under this filter.</p>
            <p className="text-[11px] text-[#64748B]">
              Run an evaluation or click the &quot;1-Click Demo&quot; button in the header to evaluate a sample.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0A0F1D]/80 border-b border-[#1E2E4A] text-[#64748B] uppercase font-mono text-[10px] tracking-wider">
                <tr>
                  <th className="px-5 py-3.5">Run Identifier & Date</th>
                  <th className="px-4 py-3.5">Scenario</th>
                  <th className="px-4 py-3.5">Mode</th>
                  <th className="px-4 py-3.5">Coverage</th>
                  <th className="px-4 py-3.5">Overall Score</th>
                  <th className="px-4 py-3.5">Grade</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E2E4A]/60">
                {runs.map((r) => {
                  const isAudio = r.evaluation_mode === "audio_plus_transcript";

                  return (
                    <tr
                      key={r.run_id}
                      className="hover:bg-[#131E33]/50 transition-colors cursor-pointer"
                      onClick={() => onSelectRun(r.run_id)}
                    >
                      {/* ID and Date */}
                      <td className="px-5 py-4">
                        <div className="font-mono text-xs font-bold text-white">
                          {r.run_id}
                        </div>
                        <div className="text-[11px] text-[#64748B] mt-0.5 font-mono">
                          {new Date(r.created_at).toLocaleString()}
                        </div>
                      </td>

                      {/* Scenario */}
                      <td className="px-4 py-4">
                        <span className="font-medium text-[#CBD5E1] uppercase font-mono text-[11px]">
                          {r.scenario.replace(/_/g, " ")}
                        </span>
                      </td>

                      {/* Mode */}
                      <td className="px-4 py-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono border ${
                            isAudio
                              ? "bg-[#06B6D4]/15 text-[#22D3EE] border-[#06B6D4]/30"
                              : "bg-[#8B5CF6]/15 text-[#C4B5FD] border-[#8B5CF6]/30"
                          }`}
                        >
                          {isAudio ? "Audio + Transcript" : "Transcript Only"}
                        </span>
                      </td>

                      {/* Coverage */}
                      <td className="px-4 py-4">
                        <div className="font-mono text-xs font-bold text-[#E2E8F0]">
                          {r.coverage_percentage}%
                        </div>
                        <div className="text-[10px] text-[#64748B]">
                          {r.evaluated_criteria_count} criteria
                        </div>
                      </td>

                      {/* Score */}
                      <td className="px-4 py-4 font-mono">
                        <span className={`text-base font-bold ${
                          r.overall_score >= 80
                            ? "text-[#34D399]"
                            : r.overall_score >= 65
                            ? "text-[#38BDF8]"
                            : r.overall_score >= 50
                            ? "text-[#FBBF24]"
                            : "text-[#F87171]"
                        }`}>
                          {r.overall_score.toFixed(1)}
                        </span>
                        <span className="text-[10px] text-[#64748B]">/100</span>
                      </td>

                      {/* Grade */}
                      <td className="px-4 py-4">
                        <span className="px-2.5 py-1 rounded-lg text-xs font-bold font-mono bg-[#1E2E4A] text-white border border-[#2E456E]">
                          {r.grade}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="px-5 py-4 text-right space-x-2" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => onSelectRun(r.run_id)}
                          className="px-2.5 py-1 rounded-lg bg-[#1E2E4A] hover:bg-[#2E456E] text-white text-[11px] font-medium transition-colors"
                        >
                          Inspect
                        </button>

                        <a
                          href={getHtmlReportUrl(r.run_id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2.5 py-1 rounded-lg bg-[#131E33] hover:bg-[#1E2E4A] text-[#06B6D4] hover:text-white text-[11px] font-medium border border-[#1E2E4A] inline-block transition-colors"
                          title="Open standalone printable HTML evaluation report"
                        >
                          Print Report
                        </a>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
