"use client";

import React from "react";

export interface ScoreGaugeProps {
  score: number;
  grade: string;
  coveragePercentage: number;
  coverageRatio?: number;
  evaluatedCount?: number;
  totalEligibleCount?: number;
  missingCriteria?: string[];
  mode?: string;
}

export function ScoreGauge({
  score,
  grade,
  coveragePercentage,
  coverageRatio,
  evaluatedCount,
  totalEligibleCount,
  missingCriteria,
  mode,
}: ScoreGaugeProps) {
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset =
    circumference - (Math.min(100, Math.max(0, score)) / 100) * circumference;

  const getScoreColor = (s: number) => {
    if (s >= 85) return "#10B981"; // Emerald
    if (s >= 70) return "#06B6D4"; // Cyan
    if (s >= 55) return "#6366F1"; // Indigo
    if (s >= 40) return "#F59E0B"; // Amber
    return "#F43F5E"; // Rose
  };

  const getGradeBadgeClass = (g: string) => {
    if (g.startsWith("A")) return "bg-[#10B981]/20 text-[#34D399] border-[#10B981]/30";
    if (g.startsWith("B")) return "bg-[#06B6D4]/20 text-[#38BDF8] border-[#06B6D4]/30";
    if (g.startsWith("C")) return "bg-[#6366F1]/20 text-[#818CF8] border-[#6366F1]/30";
    if (g.startsWith("D")) return "bg-[#F59E0B]/20 text-[#FBBF24] border-[#F59E0B]/30";
    return "bg-[#F43F5E]/20 text-[#FB7185] border-[#F43F5E]/30";
  };

  const scoreColor = getScoreColor(score);

  return (
    <div className="bg-[#131E33] border border-[#1E2E4A] rounded-2xl p-6 flex flex-col items-center justify-center text-center shadow-lg">
      <div className="relative w-36 h-36 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r={radius}
            className="text-[#1E2E4A]"
            strokeWidth="9"
            stroke="currentColor"
            fill="transparent"
          />
          <circle
            cx="60"
            cy="60"
            r={radius}
            stroke={scoreColor}
            strokeWidth="9"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
          />
        </svg>

        <div className="absolute flex flex-col items-center">
          <span className="text-3xl font-extrabold text-white tracking-tight">
            {Math.round(score)}
          </span>
          <span className="text-[11px] font-semibold text-[#64748B] uppercase tracking-wider">
            / 100
          </span>
        </div>
      </div>

      <div className="mt-4 flex flex-col items-center space-y-2">
        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getGradeBadgeClass(grade)}`}>
          GRADE {grade}
        </span>
        <div className="flex items-center space-x-1.5 text-xs text-[#94A3B8]">
          <span className="w-2 h-2 rounded-full bg-[#06B6D4]"></span>
          <span>{coveragePercentage}% Criteria Coverage</span>
          {evaluatedCount !== undefined && totalEligibleCount !== undefined && (
            <span className="text-[#64748B] font-mono text-[11px]">
              ({evaluatedCount}/{totalEligibleCount} evaluated)
            </span>
          )}
        </div>

        {missingCriteria && missingCriteria.length > 0 && (
          <div className="text-[10px] text-[#FBBF24] bg-[#F59E0B]/10 border border-[#F59E0B]/30 px-2 py-0.5 rounded-full font-mono">
            Missing: {missingCriteria.join(", ")}
          </div>
        )}

        <p className="text-[11px] text-[#64748B] max-w-xs mt-1">
          Normalized weighted sum computed over available criteria; missing measurements are never treated as zero.
        </p>
      </div>
    </div>
  );
}
