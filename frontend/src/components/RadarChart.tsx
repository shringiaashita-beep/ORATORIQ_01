"use client";

import React from "react";
import { CriterionScoreResult } from "@/types";

interface RadarChartProps {
  criterionScores: Record<string, CriterionScoreResult>;
}

export function RadarChart({ criterionScores }: RadarChartProps) {
  const axes = [
    { id: "content_and_relevance", label: "Content & Relevance" },
    { id: "structure_and_coherence", label: "Structure" },
    { id: "fluency_and_pacing", label: "Fluency & Pacing" },
    { id: "vocal_delivery", label: "Vocal Delivery" },
    { id: "clarity_and_conciseness", label: "Clarity" },
  ];

  const size = 300;
  const center = size / 2;
  const maxRadius = 95;
  const numAxes = axes.length;

  // Grid levels (20%, 40%, 60%, 80%, 100%)
  const levels = [0.2, 0.4, 0.6, 0.8, 1.0];

  const getCoordinates = (index: number, valueRatio: number) => {
    const angle = (Math.PI * 2 * index) / numAxes - Math.PI / 2;
    const r = maxRadius * valueRatio;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  // Build polygon path points from actual normalized scores
  const points: { x: number; y: number; isAvailable: boolean }[] = axes.map((axis, i) => {
    const scoreResult = criterionScores[axis.id];
    const isAvailable = scoreResult && scoreResult.status === "evaluated" && scoreResult.normalized_score !== null;
    const scoreVal = isAvailable ? scoreResult.normalized_score! : 0;
    const ratio = Math.max(0, Math.min(1.0, scoreVal / 100.0));
    const coords = getCoordinates(i, ratio);
    return { ...coords, isAvailable };
  });

  const polygonPath = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ") + " Z";

  return (
    <div className="bg-[#131E33] border border-[#1E2E4A] rounded-2xl p-5 flex flex-col items-center justify-center shadow-lg">
      <div className="w-full flex items-center justify-between mb-2">
        <h4 className="text-xs font-bold text-white uppercase tracking-wider">Rubric Telemetry Radar</h4>
        <span className="text-[11px] text-[#06B6D4] font-medium">Actual Measured Axes</span>
      </div>

      <div className="relative w-[300px] h-[260px] flex items-center justify-center">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="overflow-visible">
          {/* Circular / Polygonal Grid Lines */}
          {levels.map((lvl) => {
            const gridPoints = axes
              .map((_, i) => {
                const c = getCoordinates(i, lvl);
                return `${i === 0 ? "M" : "L"} ${c.x} ${c.y}`;
              })
              .join(" ") + " Z";
            return (
              <path
                key={lvl}
                d={gridPoints}
                fill="none"
                stroke="#1E2E4A"
                strokeWidth="1"
                strokeDasharray={lvl === 1.0 ? "none" : "2 2"}
              />
            );
          })}

          {/* Spokes radiating from center */}
          {axes.map((_, i) => {
            const end = getCoordinates(i, 1.0);
            return (
              <line
                key={i}
                x1={center}
                y1={center}
                x2={end.x}
                y2={end.y}
                stroke="#1E2E4A"
                strokeWidth="1.2"
              />
            );
          })}

          {/* Evaluated Area Polygon */}
          <path
            d={polygonPath}
            fill="rgba(6, 182, 212, 0.25)"
            stroke="#06B6D4"
            strokeWidth="2.5"
            strokeLinejoin="round"
          />

          {/* Data Points */}
          {points.map((p, i) => {
            const axis = axes[i];
            const scoreResult = criterionScores[axis.id];
            const isAvail = scoreResult && scoreResult.status === "evaluated";

            return (
              <circle
                key={i}
                cx={p.x}
                cy={p.y}
                r={isAvail ? 4.5 : 3}
                fill={isAvail ? "#06B6D4" : "#64748B"}
                stroke="#0E1626"
                strokeWidth="2"
              />
            );
          })}

          {/* Axis Labels */}
          {axes.map((axis, i) => {
            const labelCoord = getCoordinates(i, 1.25);
            const scoreResult = criterionScores[axis.id];
            const isAvail = scoreResult && scoreResult.status === "evaluated";
            const scoreDisplay = isAvail ? `${Math.round(scoreResult.normalized_score || 0)}` : "N/A";

            return (
              <g key={axis.id} transform={`translate(${labelCoord.x}, ${labelCoord.y})`}>
                <text
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="text-[10px] fill-[#94A3B8] font-medium"
                >
                  {axis.label}
                </text>
                <text
                  y="12"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className={`text-[10px] font-bold ${isAvail ? "fill-[#06B6D4]" : "fill-[#F59E0B]"}`}
                >
                  {scoreDisplay}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <div className="w-full mt-3 flex items-center justify-between text-[11px] text-[#64748B] pt-2 border-t border-[#1E2E4A]">
        <span>Scale: 0 – 100 Normalized</span>
        <span>Polygon area = balanced delivery</span>
      </div>
    </div>
  );
}
