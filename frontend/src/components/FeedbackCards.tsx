"use client";

import React, { useState } from "react";
import { FeedbackItem } from "@/types";

interface FeedbackCardsProps {
  items: FeedbackItem[];
  onSeek?: (seconds: number) => void;
}

export function FeedbackCards({ items, onSeek }: FeedbackCardsProps) {
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filteredItems = items.filter((item) => {
    if (filterSeverity === "ALL") return true;
    return item.severity?.toLowerCase() === filterSeverity.toLowerCase();
  });

  const getSeverityBadge = (severity: string) => {
    const s = severity?.toLowerCase();
    switch (s) {
      case "high":
        return {
          bg: "bg-[#EF4444]/15 text-[#F87171] border-[#EF4444]/30",
          dot: "bg-[#EF4444]",
          label: "High Priority",
        };
      case "medium":
        return {
          bg: "bg-[#F59E0B]/15 text-[#FBBF24] border-[#F59E0B]/30",
          dot: "bg-[#F59E0B]",
          label: "Refinement",
        };
      case "positive":
        return {
          bg: "bg-[#10B981]/15 text-[#34D399] border-[#10B981]/30",
          dot: "bg-[#10B981]",
          label: "Strength",
        };
      default:
        return {
          bg: "bg-[#64748B]/15 text-[#94A3B8] border-[#64748B]/30",
          dot: "bg-[#64748B]",
          label: "Observation",
        };
    }
  };

  return (
    <div className="space-y-4">
      {/* Header and Filter Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-1">
        <div>
          <h3 className="text-sm font-bold text-white tracking-wide flex items-center space-x-2">
            <span>Actionable Delivery & Content Feedback</span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[#6366F1]/20 text-[#818CF8] border border-[#6366F1]/30">
              {items.length} Insights
            </span>
          </h3>
          <p className="text-[11px] text-[#64748B]">
            Evidence-grounded recommendations with targeted vocal and rhetorical exercises
          </p>
        </div>

        {/* Severity Filters */}
        <div className="flex items-center space-x-1.5 bg-[#0E1626] p-1 rounded-lg border border-[#1E2E4A] text-xs">
          {["ALL", "HIGH", "MEDIUM", "POSITIVE"].map((sev) => {
            const count =
              sev === "ALL"
                ? items.length
                : items.filter((i) => i.severity?.toUpperCase() === sev).length;
            const isActive = filterSeverity === sev;
            return (
              <button
                key={sev}
                onClick={() => setFilterSeverity(sev)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${
                  isActive
                    ? "bg-[#1E2E4A] text-white shadow-sm"
                    : "text-[#94A3B8] hover:text-white"
                }`}
              >
                {sev === "ALL" ? "All" : sev.charAt(0) + sev.slice(1).toLowerCase()} ({count})
              </button>
            );
          })}
        </div>
      </div>

      {/* Cards List */}
      <div className="grid grid-cols-1 gap-4">
        {filteredItems.length === 0 ? (
          <div className="p-8 text-center rounded-2xl border border-[#1E2E4A] bg-[#0E1626]/50 text-xs text-[#94A3B8]">
            No feedback items match the selected severity filter.
          </div>
        ) : (
          filteredItems.map((item) => {
            const badge = getSeverityBadge(item.severity);
            const isExpanded = expandedId === item.feedback_id;

            return (
              <div
                key={item.feedback_id}
                className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-5 shadow-lg hover:border-[#2E456E] transition-all"
              >
                {/* Top Row: Criterion & Severity */}
                <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[#1E2E4A]/60">
                  <div className="flex items-center space-x-2.5">
                    <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                      {item.criterion_name || item.rubric_criterion.replace(/_/g, " ")}
                    </span>
                    <span className="text-xs text-[#64748B]">•</span>
                    <span className="text-xs text-[#06B6D4] font-medium">{item.observed_issue}</span>
                  </div>

                  <div className={`flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${badge.bg}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`}></span>
                    <span>{badge.label}</span>
                  </div>
                </div>

                {/* Evidence Section */}
                <div className="mt-3.5 space-y-2.5">
                  {/* Measured Value or Transcript Excerpt */}
                  {(item.measured_value || item.transcript_excerpt || item.timestamp_range) && (
                    <div className="p-3 rounded-xl bg-[#0A0F1D]/60 border border-[#1E2E4A] text-xs">
                      <div className="flex items-center justify-between text-[10px] text-[#64748B] uppercase font-semibold mb-1">
                        <span>Observed Evidence ({item.evidence_type.replace(/_/g, " ")})</span>
                        {item.timestamp_range && (
                          <button
                            onClick={() => onSeek && onSeek(item.timestamp_range!.start)}
                            className="text-[#06B6D4] hover:underline font-mono text-[10px] flex items-center space-x-1"
                          >
                            <span>▶ Seek to {item.timestamp_range.start.toFixed(1)}s</span>
                          </button>
                        )}
                      </div>

                      {item.measured_value && (
                        <div className="font-mono text-xs text-[#38BDF8] font-bold">
                          {item.measured_value}
                        </div>
                      )}

                      {item.transcript_excerpt && (
                        <blockquote className="mt-1 text-xs text-[#CBD5E1] italic border-l-2 border-[#6366F1] pl-2.5 py-0.5">
                          &quot;{item.transcript_excerpt}&quot;
                        </blockquote>
                      )}
                    </div>
                  )}

                  {/* Explanation */}
                  <p className="text-xs text-[#94A3B8] leading-relaxed">
                    {item.explanation}
                  </p>

                  {/* Recommendation Action */}
                  <div className="p-3.5 rounded-xl bg-[#6366F1]/10 border border-[#6366F1]/30">
                    <div className="flex items-center space-x-2 text-xs font-bold text-[#818CF8] mb-1">
                      <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="9 11 12 14 22 4"></polyline>
                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                      </svg>
                      <span>Recommended Adjustment</span>
                    </div>
                    <p className="text-xs text-[#E2E8F0] leading-relaxed">
                      {item.recommended_action}
                    </p>
                  </div>

                  {/* Practical Drill or Example Rewrite */}
                  {item.example_rewrite_or_exercise && (
                    <div className="p-3.5 rounded-xl bg-[#06B6D4]/10 border border-[#06B6D4]/30">
                      <div className="flex items-center space-x-2 text-xs font-bold text-[#22D3EE] mb-1">
                        <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
                          <polygon points="5 3 19 12 5 21 5 3"></polygon>
                        </svg>
                        <span>Targeted Practice Drill / Rewrite</span>
                      </div>
                      <div className="text-xs text-[#CBD5E1] font-sans leading-relaxed whitespace-pre-wrap">
                        {item.example_rewrite_or_exercise}
                      </div>
                    </div>
                  )}
                </div>

                {/* Auditability & Limitations Footer */}
                <div className="mt-3.5 pt-2.5 border-t border-[#1E2E4A]/40 flex flex-wrap items-center justify-between text-[11px] text-[#64748B] gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-[10px]">Method: {item.evaluator_method}</span>
                    <span>•</span>
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : item.feedback_id)}
                      className="text-[#64748B] hover:text-[#94A3B8] underline"
                    >
                      {isExpanded ? "Hide Limitations" : "View Evaluator Limitations"}
                    </button>
                  </div>

                  <span className="font-mono text-[10px] text-[#475569]">ID: {item.feedback_id}</span>
                </div>

                {/* Expanded Limitations Note */}
                {isExpanded && (
                  <div className="mt-2 p-2.5 rounded-lg bg-[#0A0F1D] border border-[#1E2E4A] text-[11px] text-[#94A3B8] leading-relaxed">
                    <strong className="text-[#E2E8F0]">Measurement Boundaries:</strong> {item.limitations}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
