"use client";

import React, { useState } from "react";
import { ContrastiveMatch } from "@/types";

interface ContrastiveCalibrationCardProps {
  matches: ContrastiveMatch[];
  scenario: string;
}

export function ContrastiveCalibrationCard({ matches, scenario }: ContrastiveCalibrationCardProps) {
  const [expandedPairId, setExpandedPairId] = useState<string | null>(null);

  if (!matches || matches.length === 0) {
    return (
      <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 text-center text-xs text-[#94A3B8]">
        No contrastive calibration pairs were matched for this evaluation scenario.
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] overflow-hidden shadow-lg">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[#1E2E4A] bg-[#0A0F1D]/60 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-[#06B6D4]/10 border border-[#06B6D4]/30 flex items-center justify-center text-[#22D3EE]">
            <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
              <line x1="8" y1="21" x2="16" y2="21"></line>
              <line x1="12" y1="17" x2="12" y2="21"></line>
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide flex items-center space-x-2">
              <span>Curated Contrastive Calibration Anchors</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[#06B6D4]/20 text-[#22D3EE] border border-[#06B6D4]/30">
                {matches.length} Exemplar Pairs
              </span>
            </h3>
            <p className="text-[11px] text-[#64748B]">
              Ground-truth ideal vs. flawed comparative reference pairs from the OratorIQ corpus
            </p>
          </div>
        </div>

        <div className="text-[11px] text-[#94A3B8] font-mono bg-[#131E33] px-2.5 py-1 rounded-lg border border-[#1E2E4A]">
          Scenario: <span className="text-[#38BDF8] uppercase">{scenario.replace(/_/g, " ")}</span>
        </div>
      </div>

      {/* Rationale Notice */}
      <div className="px-5 py-2.5 bg-[#0D1524] border-b border-[#1E2E4A] text-[11px] text-[#94A3B8] flex items-center space-x-2">
        <svg viewBox="0 0 24 24" className="w-4 h-4 text-[#818CF8] shrink-0" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
        <span>
          <strong>Scientific Calibration Note:</strong> Contrastive exemplars are utilized to calibrate scoring boundaries and ground actionable feedback. They illustrate concrete differences in delivery and rhetoric.
        </span>
      </div>

      {/* Matches List */}
      <div className="p-5 space-y-4">
        {matches.map((m) => {
          const isExpanded = expandedPairId === m.matched_pair_id;

          return (
            <div
              key={m.matched_pair_id}
              className="rounded-xl border border-[#1E2E4A] bg-[#10192A] p-4.5 space-y-3.5 hover:border-[#2E456E] transition-all"
            >
              {/* Top row */}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold text-white">
                    {m.matched_pair_id}
                  </span>
                  <span className="text-xs text-[#64748B]">•</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-[#F59E0B]/15 text-[#FBBF24] border border-[#F59E0B]/30 font-mono">
                    {m.primary_flaw.replace(/_/g, " ")}
                  </span>
                </div>

                <div className="flex items-center space-x-2 text-[11px] font-mono text-[#64748B]">
                  <span>Ideal: <code className="text-[#34D399]">{m.ideal_sample_id}</code></span>
                  <span>|</span>
                  <span>Flawed: <code className="text-[#F87171]">{m.flawed_sample_id}</code></span>
                </div>
              </div>

              {/* Similarity Explanation */}
              <div className="text-xs text-[#CBD5E1] leading-relaxed">
                <strong className="text-white">Why This Pair Matched:</strong> {m.similarity_explanation}
              </div>

              {/* Delta Analysis */}
              <div className="p-3.5 rounded-xl bg-[#0A0F1D]/80 border border-[#1E2E4A] text-xs space-y-1.5">
                <div className="text-[10px] text-[#818CF8] uppercase font-bold tracking-wider">
                  Contrastive Delta Analysis
                </div>
                <p className="text-xs text-[#94A3B8] leading-relaxed font-sans">
                  {m.contrastive_delta_analysis}
                </p>
              </div>

              {/* Audit IDs Footer */}
              <div className="pt-2 border-t border-[#1E2E4A]/50 flex items-center justify-between text-[11px] text-[#64748B]">
                <span>Corpus Split: Speaker-Disjoint Benchmark</span>
                <span className="font-mono text-[10px]">Deterministic Anchor ID: {m.matched_pair_id}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
