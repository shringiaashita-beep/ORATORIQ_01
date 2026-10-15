"use client";

import React, { useState } from "react";
import { TranscriptAnnotation, AudioFeatures } from "@/types";

interface TranscriptInspectorProps {
  transcript: TranscriptAnnotation;
  audioFeatures?: AudioFeatures | null;
  onSeek?: (seconds: number) => void;
}

export function TranscriptInspector({ transcript, audioFeatures, onSeek }: TranscriptInspectorProps) {
  const [viewMode, setViewMode] = useState<"annotated" | "raw" | "segments">("annotated");
  const [copied, setCopied] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string | null>(null);

  const fillerSet = new Set(
    (transcript.filler_words_detected || []).map((f) => f.word.toLowerCase())
  );

  const copyTranscript = () => {
    navigator.clipboard.writeText(transcript.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const totalFillerCount = (transcript.filler_words_detected || []).reduce(
    (acc, cur) => acc + cur.count,
    0
  );

  return (
    <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] overflow-hidden shadow-lg">
      {/* Header bar */}
      <div className="px-5 py-3.5 border-b border-[#1E2E4A] bg-[#0A0F1D]/60 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-7 h-7 rounded-lg bg-[#6366F1]/10 border border-[#6366F1]/30 flex items-center justify-center text-[#818CF8]">
            <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">Transcript & Disfluency Inspector</h3>
            <p className="text-[11px] text-[#64748B]">
              Aligned tokens • Detected filler disfluencies • Readability index
            </p>
          </div>
        </div>

        {/* View Mode Pills & Actions */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center bg-[#131E33] p-0.5 rounded-lg border border-[#1E2E4A]">
            <button
              onClick={() => setViewMode("annotated")}
              className={`px-2.5 py-1 text-xs rounded-md font-medium transition-colors ${
                viewMode === "annotated"
                  ? "bg-[#1E2E4A] text-white shadow-sm"
                  : "text-[#94A3B8] hover:text-white"
              }`}
            >
              Annotated
            </button>
            <button
              onClick={() => setViewMode("segments")}
              className={`px-2.5 py-1 text-xs rounded-md font-medium transition-colors ${
                viewMode === "segments"
                  ? "bg-[#1E2E4A] text-white shadow-sm"
                  : "text-[#94A3B8] hover:text-white"
              }`}
            >
              Timed Segments
            </button>
            <button
              onClick={() => setViewMode("raw")}
              className={`px-2.5 py-1 text-xs rounded-md font-medium transition-colors ${
                viewMode === "raw"
                  ? "bg-[#1E2E4A] text-white shadow-sm"
                  : "text-[#94A3B8] hover:text-white"
              }`}
            >
              Raw Text
            </button>
          </div>

          <button
            onClick={copyTranscript}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-[#131E33] hover:bg-[#1E2E4A] text-[#94A3B8] hover:text-white border border-[#1E2E4A] transition-colors"
            title="Copy entire transcript to clipboard"
          >
            <svg viewBox="0 0 24 24" className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            <span>{copied ? "Copied!" : "Copy"}</span>
          </button>
        </div>
      </div>

      {/* Metrics strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 p-3 bg-[#0A0F1D]/30 border-b border-[#1E2E4A] text-xs">
        <div className="p-2 rounded-lg bg-[#131E33]/50 border border-[#1E2E4A]/60">
          <div className="text-[10px] text-[#64748B] uppercase font-semibold">Total Word Count</div>
          <div className="text-base font-bold text-white font-mono mt-0.5">
            {transcript.words?.length || transcript.text.split(/\s+/).filter(Boolean).length}
          </div>
        </div>

        <div className="p-2 rounded-lg bg-[#131E33]/50 border border-[#1E2E4A]/60">
          <div className="text-[10px] text-[#64748B] uppercase font-semibold">Disfluency Count</div>
          <div className="flex items-baseline space-x-1.5 mt-0.5">
            <span className={`text-base font-bold font-mono ${totalFillerCount > 5 ? "text-[#F59E0B]" : "text-[#34D399]"}`}>
              {totalFillerCount}
            </span>
            <span className="text-[10px] text-[#64748B]">fillers</span>
          </div>
        </div>

        <div className="p-2 rounded-lg bg-[#131E33]/50 border border-[#1E2E4A]/60">
          <div className="text-[10px] text-[#64748B] uppercase font-semibold">Flesch Readability</div>
          <div className="flex items-baseline space-x-1.5 mt-0.5">
            <span className="text-base font-bold font-mono text-[#06B6D4]">
              {transcript.readability_flesch_score ? transcript.readability_flesch_score.toFixed(1) : "N/A"}
            </span>
            <span className="text-[10px] text-[#64748B]">
              {transcript.readability_flesch_score >= 60 ? "Standard" : "Dense"}
            </span>
          </div>
        </div>

        <div className="p-2 rounded-lg bg-[#131E33]/50 border border-[#1E2E4A]/60">
          <div className="text-[10px] text-[#64748B] uppercase font-semibold">Detected Language</div>
          <div className="text-base font-bold text-white uppercase font-mono mt-0.5">
            {transcript.detected_language || "en"}
          </div>
        </div>
      </div>

      {/* Disfluency Filters (if fillers present) */}
      {(transcript.filler_words_detected || []).length > 0 && (
        <div className="px-5 py-2.5 bg-[#0F1829] border-b border-[#1E2E4A] flex flex-wrap items-center gap-2 text-xs">
          <span className="text-[11px] font-semibold text-[#94A3B8]">Detected Fillers:</span>
          <button
            onClick={() => setActiveFilter(null)}
            className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
              activeFilter === null
                ? "bg-[#6366F1] text-white"
                : "bg-[#1E2E4A] text-[#94A3B8] hover:text-white"
            }`}
          >
            All Fillers ({totalFillerCount})
          </button>
          {transcript.filler_words_detected.map((filler) => {
            const isSelected = activeFilter === filler.word.toLowerCase();
            return (
              <button
                key={filler.word}
                onClick={() => setActiveFilter(isSelected ? null : filler.word.toLowerCase())}
                className={`px-2 py-0.5 rounded text-[11px] font-medium border flex items-center space-x-1 transition-colors ${
                  isSelected
                    ? "bg-[#F59E0B] text-black font-bold border-[#F59E0B]"
                    : "bg-[#F59E0B]/10 text-[#FBBF24] border-[#F59E0B]/30 hover:bg-[#F59E0B]/20"
                }`}
              >
                <span>&quot;{filler.word}&quot;</span>
                <span className="px-1 py-0.1 text-[9px] rounded-full bg-black/30 font-mono">
                  {filler.count}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Main Content Area */}
      <div className="p-6 max-h-[380px] overflow-y-auto font-sans leading-relaxed text-[#CBD5E1] text-sm selection:bg-[#6366F1]/30">
        {viewMode === "raw" && (
          <p className="whitespace-pre-wrap font-sans text-sm leading-7 text-[#E2E8F0]">
            {transcript.text}
          </p>
        )}

        {viewMode === "annotated" && (
          <div className="flex flex-wrap gap-x-1.5 gap-y-1.5 items-center">
            {transcript.words && transcript.words.length > 0 ? (
              transcript.words.map((w, idx) => {
                const clean = w.word.toLowerCase().replace(/[^a-z0-9]/g, "");
                const isFiller = fillerSet.has(clean);
                const isFiltered = activeFilter ? clean === activeFilter : isFiller;
                const hasTime = typeof w.start_time === "number";

                return (
                  <span
                    key={idx}
                    onClick={() => {
                      if (hasTime && onSeek) onSeek(w.start_time!);
                    }}
                    title={
                      hasTime
                        ? `Time: ${w.start_time!.toFixed(2)}s - ${w.end_time?.toFixed(2)}s (Click to seek)`
                        : undefined
                    }
                    className={`inline-block px-1 py-0.5 rounded transition-all ${
                      hasTime ? "cursor-pointer" : ""
                    } ${
                      isFiltered
                        ? "bg-[#F59E0B]/25 text-[#FBBF24] font-semibold border border-[#F59E0B]/40 ring-1 ring-[#F59E0B]/40"
                        : "hover:bg-[#1E2E4A]/80 text-[#E2E8F0]"
                    }`}
                  >
                    {w.word}
                  </span>
                );
              })
            ) : (
              // Fallback if words tokens were not individually timestamped
              <p className="whitespace-pre-wrap leading-7 text-[#E2E8F0]">
                {transcript.text}
              </p>
            )}
          </div>
        )}

        {viewMode === "segments" && (
          <div className="space-y-3">
            {transcript.segments && transcript.segments.length > 0 ? (
              transcript.segments.map((seg) => {
                const hasTime = typeof seg.start_time === "number";
                return (
                  <div
                    key={seg.id}
                    onClick={() => {
                      if (hasTime && onSeek) onSeek(seg.start_time!);
                    }}
                    className={`p-3 rounded-xl border border-[#1E2E4A] bg-[#131E33]/40 flex items-start space-x-3 transition-colors ${
                      hasTime ? "cursor-pointer hover:border-[#6366F1]/50 hover:bg-[#131E33]/70" : ""
                    }`}
                  >
                    {hasTime && (
                      <span className="font-mono text-[11px] text-[#06B6D4] font-bold shrink-0 pt-0.5 bg-[#06B6D4]/10 px-2 py-0.5 rounded border border-[#06B6D4]/20">
                        {seg.start_time!.toFixed(1)}s
                      </span>
                    )}
                    <div className="text-sm text-[#E2E8F0] leading-relaxed">
                      {seg.text}
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-xs text-[#94A3B8] italic p-4 text-center">
                Continuous speech segment (no sub-segment boundaries detected).
              </div>
            )}
          </div>
        )}
      </div>

      {/* Repetitions footer warning if detected */}
      {(transcript.repetitions_detected || []).length > 0 && (
        <div className="px-5 py-2.5 bg-[#10192A] border-t border-[#1E2E4A] text-xs flex items-center space-x-2 text-[#94A3B8]">
          <span className="text-[#06B6D4] font-bold">Unnecessary Repetitions:</span>
          <div className="flex flex-wrap gap-1.5">
            {transcript.repetitions_detected.map((rep, i) => (
              <span key={i} className="px-2 py-0.5 rounded bg-[#06B6D4]/10 text-[#22D3EE] font-mono text-[11px] border border-[#06B6D4]/25">
                &quot;{rep.phrase}&quot;
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
