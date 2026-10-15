"use client";

import React, { useState, useEffect } from "react";
import {
  EvaluationResult,
  DatasetManifest,
  EvaluationRunSummary
} from "@/types";
import {
  fetchHealth,
  fetchReadiness,
  evaluateSpeechAudio,
  evaluateSpeechTranscript,
  getEvaluationById,
  getDatasetManifest,
  getEvaluationHistory,
  getHtmlReportUrl
} from "@/lib/api";

import { Navbar } from "@/components/Navbar";
import { ScoreGauge } from "@/components/ScoreGauge";
import { RadarChart } from "@/components/RadarChart";
import { AudioWaveformRecorder } from "@/components/AudioWaveformRecorder";
import { TranscriptInspector } from "@/components/TranscriptInspector";
import { FeedbackCards } from "@/components/FeedbackCards";
import { ContrastiveCalibrationCard } from "@/components/ContrastiveCalibrationCard";
import { DatasetExplorer } from "@/components/DatasetExplorer";
import { RubricEditor } from "@/components/RubricEditor";
import { EvaluationHistoryTable } from "@/components/EvaluationHistoryTable";

export default function Home() {
  const [currentView, setCurrentView] = useState<string>("viewHome");
  const [engineReady, setEngineReady] = useState<boolean>(false);
  const [engineStatus, setEngineStatus] = useState<string>("PROBING");
  const [readinessData, setReadinessData] = useState<any>(null);

  // Evaluation state
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(null);
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);
  const [evalProgressStep, setEvalProgressStep] = useState<string>("");
  const [evalError, setEvalError] = useState<string | null>(null);

  // Form options
  const [selectedScenario, setSelectedScenario] = useState<string>("persuasive_pitches");
  const [selectedRubricId, setSelectedRubricId] = useState<string>("rubric_standard_v1");
  const [speechPrompt, setSpeechPrompt] = useState<string>("Municipal investment in protected bicycle infrastructure");

  // History and Manifest
  const [recentRuns, setRecentRuns] = useState<EvaluationRunSummary[]>([]);
  const [manifest, setManifest] = useState<DatasetManifest | null>(null);

  useEffect(() => {
    initApp();
  }, []);

  const initApp = async () => {
    try {
      const ready = await fetchReadiness();
      setReadinessData(ready);
      setEngineReady(true);
      setEngineStatus("ENGINE ONLINE");
    } catch (err) {
      setEngineStatus("LIMITED MODE");
      setEngineReady(false);
    }

    try {
      const [hist, man] = await Promise.all([
        getEvaluationHistory(),
        getDatasetManifest(),
      ]);
      setRecentRuns(hist.runs || []);
      setManifest(man);
    } catch (e) {
      // Background load failed gracefully
    }
  };

  const handleEvaluateAudio = async (formData: FormData) => {
    setIsEvaluating(true);
    setEvalError(null);
    setEvalProgressStep("Validating audio format, sample rate, and headers...");

    try {
      formData.set("scenario", selectedScenario);
      formData.set("rubric_id", selectedRubricId);
      if (speechPrompt) formData.set("speech_prompt", speechPrompt);

      setTimeout(() => setEvalProgressStep("Extracting acoustic features (F0 pitch, pauses, WPM, SNR)..."), 500);
      setTimeout(() => setEvalProgressStep("Aligning transcript and detecting disfluencies..."), 1200);
      setTimeout(() => setEvalProgressStep("Evaluating 5-axis rubric & matching contrastive pairs..."), 1900);

      const result = await evaluateSpeechAudio(formData);
      setEvaluationResult(result);
      setCurrentView("viewReport");
      // refresh history
      getEvaluationHistory().then((h) => setRecentRuns(h.runs || []));
    } catch (err: any) {
      setEvalError(err.message || "Speech evaluation failed. Please check backend status.");
    } finally {
      setIsEvaluating(false);
      setEvalProgressStep("");
    }
  };

  const handleEvaluateTranscript = async (transcript: string) => {
    setIsEvaluating(true);
    setEvalError(null);
    setEvalProgressStep("Processing transcript disfluencies, lexical patterns, and readability...");

    try {
      setTimeout(() => setEvalProgressStep("Aggregating normalized rubric scores across eligible axes..."), 400);

      const result = await evaluateSpeechTranscript({
        transcript,
        scenario: selectedScenario,
        rubric_id: selectedRubricId,
        speech_prompt: speechPrompt || undefined,
      });

      setEvaluationResult(result);
      setCurrentView("viewReport");
      getEvaluationHistory().then((h) => setRecentRuns(h.runs || []));
    } catch (err: any) {
      setEvalError(err.message || "Transcript evaluation failed.");
    } finally {
      setIsEvaluating(false);
      setEvalProgressStep("");
    }
  };

  const handleRunDemo = async () => {
    const goldenTranscript =
      "Honorable members of the city council, today we face a critical choice regarding our municipal transit infrastructure. Over the past three years, separated bicycle corridors in peer cities have reduced pedestrian injuries by thirty-four percent while accelerating morning business foot traffic by twenty-two percent. By allocating eight million dollars from the urban transit fund, we will construct twelve miles of protected corridors connecting the central business district to the eastern residential wards. Independent financial audits project this will yield six million dollars in annual healthcare savings and congestion relief within twenty-four months. The data is definitive: protected transit lanes preserve lives and fuel local commerce. I urge your immediate approval of ordinance four-twelve.";

    setSelectedScenario("persuasive_pitches");
    setSpeechPrompt("Municipal investment in protected bicycle infrastructure");
    await handleEvaluateTranscript(goldenTranscript);
  };

  const handleSelectHistoryRun = async (runId: string) => {
    try {
      const fullRun = await getEvaluationById(runId);
      setEvaluationResult(fullRun);
      setCurrentView("viewReport");
    } catch (e: any) {
      alert("Failed to load historical run: " + e.message);
    }
  };

  const handleExportJson = () => {
    if (!evaluationResult) return;
    const blob = new Blob([JSON.stringify(evaluationResult, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `oratoriq_evaluation_${evaluationResult.run_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-[#070B14] text-[#F1F5F9] font-sans flex flex-col selection:bg-[#6366F1]/30">
      {/* Navbar */}
      <Navbar
        currentView={currentView}
        onNavigate={(v) => setCurrentView(v)}
        engineStatus={engineStatus}
        isReady={engineReady}
        onRunDemo={handleRunDemo}
      />

      {/* Main App Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ========================================================= */}
        {/* VIEW A: HOME PAGE                                         */}
        {/* ========================================================= */}
        {currentView === "viewHome" && (
          <div className="space-y-10 animate-fade-in">
            {/* Hero Section */}
            <div className="relative overflow-hidden rounded-3xl border border-[#1E2E4A] bg-gradient-to-b from-[#0E1626] to-[#0A0F1D] p-8 sm:p-12 shadow-2xl">
              <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 rounded-full bg-[#6366F1]/10 blur-3xl pointer-events-none"></div>
              <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 rounded-full bg-[#06B6D4]/10 blur-3xl pointer-events-none"></div>

              <div className="relative z-10 max-w-3xl space-y-6">
                <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#6366F1]/15 text-[#818CF8] border border-[#6366F1]/30 text-xs font-semibold">
                  <span className="w-2 h-2 rounded-full bg-[#6366F1] animate-pulse"></span>
                  <span>Version 1.0.0-Gold • Evidence-Based Speech Coach</span>
                </div>

                <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
                  Defensible Speech Evaluation, Grounded in{" "}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#6366F1] via-[#38BDF8] to-[#06B6D4]">
                    Real Acoustics
                  </span>{" "}
                  & Paired Exemplars.
                </h1>

                <p className="text-base sm:text-lg text-[#94A3B8] leading-relaxed">
                  OratorIQ replaces subjective feedback and fabricated LLM scores with genuine acoustic feature extraction, a custom 52-pair contrastive speech dataset, and mathematically normalized 5-axis rubric governance.
                </p>

                <div className="flex flex-wrap items-center gap-4 pt-2">
                  <button
                    onClick={() => setCurrentView("viewEvaluate")}
                    className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-[#6366F1] to-[#06B6D4] text-white text-sm font-bold shadow-lg shadow-[#6366F1]/25 hover:opacity-95 transition-all cursor-pointer"
                  >
                    <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    <span>Start Speech Evaluation</span>
                  </button>

                  <button
                    onClick={handleRunDemo}
                    className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-[#131E33] hover:bg-[#1E2E4A] text-white text-sm font-semibold border border-[#2E456E] transition-all cursor-pointer"
                  >
                    <span>🚀 1-Click Golden Speech Demo</span>
                  </button>

                  <button
                    onClick={() => setCurrentView("viewDataset")}
                    className="flex items-center space-x-2 px-5 py-3 rounded-xl bg-transparent hover:bg-[#131E33] text-[#94A3B8] hover:text-white text-sm font-medium transition-colors"
                  >
                    <span>Inspect Contrastive Corpus ({manifest?.total_pairs || 52} Pairs) →</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Core Architectural Pillars */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 space-y-3 shadow-lg">
                <div className="w-10 h-10 rounded-xl bg-[#06B6D4]/15 border border-[#06B6D4]/30 flex items-center justify-center text-[#22D3EE]">
                  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2v20M17 5v14M7 8v8M2 11v2M22 11v2"></path>
                  </svg>
                </div>
                <h2 className="text-base font-bold text-white">Genuine Acoustic Processing</h2>
                <p className="text-xs text-[#94A3B8] leading-relaxed">
                  Decodes audio via <code>librosa</code> & <code>soundfile</code>. Measures speaking rate (WPM), pause distribution, fundamental frequency F0 pitch contour, semitone variability, signal-to-noise ratio, and digital clipping.
                </p>
                <div className="text-[11px] font-mono text-[#06B6D4] pt-1">
                  Zero fabricated vocal delivery in transcript mode.
                </div>
              </div>

              <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 space-y-3 shadow-lg">
                <div className="w-10 h-10 rounded-xl bg-[#6366F1]/15 border border-[#6366F1]/30 flex items-center justify-center text-[#818CF8]">
                  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="3" y1="9" x2="21" y2="9"></line>
                    <line x1="9" y1="21" x2="9" y2="9"></line>
                  </svg>
                </div>
                <h2 className="text-base font-bold text-white">Custom Contrastive Corpus</h2>
                <p className="text-xs text-[#94A3B8] leading-relaxed">
                  Contains 52 versioned pairs (104 samples) across 5 scenarios and 13 flaw categories. Calibrates scoring boundaries and explains delta differences between ideal vs. flawed delivery.
                </p>
                <div className="text-[11px] font-mono text-[#818CF8] pt-1">
                  Cryptographically hashed: SHA-256 verified.
                </div>
              </div>

              <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 space-y-3 shadow-lg">
                <div className="w-10 h-10 rounded-xl bg-[#10B981]/15 border border-[#10B981]/30 flex items-center justify-center text-[#34D399]">
                  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  </svg>
                </div>
                <h2 className="text-base font-bold text-white">Transparent 5-Axis Rubric</h2>
                <p className="text-xs text-[#94A3B8] leading-relaxed">
                  Content (25%), Structure (20%), Fluency (20%), Vocal Delivery (20%), and Clarity (15%). Explicit 1–5 scoring anchors with documented formula aggregation across available criteria only.
                </p>
                <div className="text-[11px] font-mono text-[#34D399] pt-1">
                  100% reproducible with standalone HTML & JSON exports.
                </div>
              </div>
            </div>

            {/* System Status & Capabilities Grid */}
            <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 shadow-xl">
              <div className="flex flex-wrap items-center justify-between pb-4 border-b border-[#1E2E4A] gap-3">
                <div className="flex items-center space-x-3">
                  <span className={`w-3 h-3 rounded-full ${engineReady ? "bg-[#10B981] animate-pulse" : "bg-[#F59E0B]"}`}></span>
                  <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                    System Telemetry & Engine Manifest
                  </h2>
                </div>
                <span className="font-mono text-xs text-[#64748B]">
                  Backend: FastAPI /api/v1 • Port 8000
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mt-4">
                <div className="p-3.5 rounded-xl bg-[#0A0F1D]/70 border border-[#1E2E4A]">
                  <div className="text-[10px] text-[#64748B] uppercase font-semibold">Contrastive Dataset</div>
                  <div className="text-sm font-bold text-white font-mono mt-1">
                    {manifest?.total_pairs || 52} Pairs ({manifest?.total_samples || 104} Samples)
                  </div>
                  <div className="text-[10px] text-[#10B981] font-mono mt-0.5">100% Schema Validated</div>
                </div>

                <div className="p-3.5 rounded-xl bg-[#0A0F1D]/70 border border-[#1E2E4A]">
                  <div className="text-[10px] text-[#64748B] uppercase font-semibold">Audio Engine</div>
                  <div className="text-sm font-bold text-white font-mono mt-1">
                    {readinessData?.audio_engine?.backend || "librosa + soundfile"}
                  </div>
                  <div className="text-[10px] text-[#06B6D4] font-mono mt-0.5">WAV, FLAC, OGG, MP3</div>
                </div>

                <div className="p-3.5 rounded-xl bg-[#0A0F1D]/70 border border-[#1E2E4A]">
                  <div className="text-[10px] text-[#64748B] uppercase font-semibold">Transcription Engine</div>
                  <div className="text-sm font-bold text-white font-mono mt-1">
                    Deterministic Aligner
                  </div>
                  <div className="text-[10px] text-[#818CF8] font-mono mt-0.5">Whisper API Compatible</div>
                </div>

                <div className="p-3.5 rounded-xl bg-[#0A0F1D]/70 border border-[#1E2E4A]">
                  <div className="text-[10px] text-[#64748B] uppercase font-semibold">Rubric Governance</div>
                  <div className="text-sm font-bold text-white font-mono mt-1">
                    5-Axis Configurable
                  </div>
                  <div className="text-[10px] text-[#34D399] font-mono mt-0.5">Normalized Weights (100%)</div>
                </div>
              </div>
            </div>

            {/* Recent Evaluations Preview */}
            {recentRuns.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between px-1">
                  <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                    Recent Speech Evaluations
                  </h2>
                  <button
                    onClick={() => setCurrentView("viewHistory")}
                    className="text-xs text-[#06B6D4] hover:underline"
                  >
                    View All Runs ({recentRuns.length}) →
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {recentRuns.slice(0, 3).map((r) => (
                    <div
                      key={r.run_id}
                      onClick={() => handleSelectHistoryRun(r.run_id)}
                      className="p-4 rounded-2xl border border-[#1E2E4A] bg-[#0E1626] hover:border-[#6366F1] transition-all cursor-pointer space-y-2 shadow-lg"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-[11px] font-bold text-[#38BDF8]">
                          {r.run_id.slice(0, 18)}...
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#1E2E4A] text-white">
                          {r.grade}
                        </span>
                      </div>
                      <div className="text-xs text-[#CBD5E1] uppercase font-semibold font-mono">
                        {r.scenario.replace(/_/g, " ")}
                      </div>
                      <div className="flex items-baseline space-x-2">
                        <span className="text-xl font-bold font-mono text-white">
                          {r.overall_score.toFixed(1)}
                        </span>
                        <span className="text-xs text-[#64748B]">/100 ({r.coverage_percentage}% coverage)</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW B: SPEECH EVALUATION PAGE                            */}
        {/* ========================================================= */}
        {currentView === "viewEvaluate" && (
          <div className="space-y-6 animate-fade-in">
            {/* Header banner */}
            <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 shadow-xl">
              <h2 className="text-lg font-bold text-white tracking-wide flex items-center space-x-2">
                <span>Speech Input & Evaluation Setup</span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-[#6366F1]/20 text-[#818CF8] border border-[#6366F1]/30">
                  Step 1 of 2
                </span>
              </h2>
              <p className="text-xs text-[#94A3B8] mt-1">
                Upload a recording, use the browser microphone, or enter a speech transcript for evidence-based rubric scoring.
              </p>
            </div>

            {/* Configuration Selectors */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Scenario */}
              <div className="p-4 rounded-2xl border border-[#1E2E4A] bg-[#0E1626] space-y-2">
                <label className="text-xs font-bold text-white uppercase font-mono tracking-wider">
                  Communication Scenario
                </label>
                <select
                  value={selectedScenario}
                  onChange={(e) => setSelectedScenario(e.target.value)}
                  className="w-full bg-[#131E33] border border-[#1E2E4A] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                >
                  <option value="persuasive_pitches">Persuasive Pitches (Funding / Proposals)</option>
                  <option value="public_speaking">Public Speaking (Keynotes / Policy)</option>
                  <option value="interview_answers">Interview Answers (Behavioral / Technical)</option>
                  <option value="presentation_delivery">Presentation Delivery (Slide Decks / Reviews)</option>
                  <option value="academic_explanations">Academic Explanations (Lectures / Defenses)</option>
                </select>
                <p className="text-[11px] text-[#64748B]">
                  Selects the matching domain calibration anchors from the contrastive dataset.
                </p>
              </div>

              {/* Rubric */}
              <div className="p-4 rounded-2xl border border-[#1E2E4A] bg-[#0E1626] space-y-2">
                <label className="text-xs font-bold text-white uppercase font-mono tracking-wider">
                  Evaluation Rubric
                </label>
                <select
                  value={selectedRubricId}
                  onChange={(e) => setSelectedRubricId(e.target.value)}
                  className="w-full bg-[#131E33] border border-[#1E2E4A] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                >
                  <option value="rubric_standard_v1">Standard Speech Evaluation Rubric (v1.0.0)</option>
                </select>
                <p className="text-[11px] text-[#64748B]">
                  Standard 5-axis normalized scoring scale (1–5 ordinal anchors).
                </p>
              </div>
            </div>

            {/* Optional Speech Prompt */}
            <div className="p-4 rounded-2xl border border-[#1E2E4A] bg-[#0E1626] space-y-2">
              <label className="text-xs font-bold text-white uppercase font-mono tracking-wider flex items-center justify-between">
                <span>Intended Topic / Speech Prompt (Optional)</span>
                <span className="text-[10px] text-[#64748B] normal-case">Enables semantic content relevance checks</span>
              </label>
              <input
                type="text"
                value={speechPrompt}
                onChange={(e) => setSpeechPrompt(e.target.value)}
                placeholder="e.g. Municipal investment in protected bicycle infrastructure"
                className="w-full bg-[#131E33] border border-[#1E2E4A] rounded-xl px-3.5 py-2 text-xs text-white placeholder-[#64748B] focus:outline-none focus:border-[#6366F1]"
              />
            </div>

            {/* Evaluating Progress Indicator */}
            {isEvaluating && (
              <div className="p-6 rounded-2xl border border-[#6366F1]/50 bg-[#6366F1]/10 text-center space-y-3 shadow-xl">
                <svg viewBox="0 0 24 24" className="w-8 h-8 text-[#06B6D4] animate-spin mx-auto" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M12 2a10 10 0 0 1 10 10"></path>
                </svg>
                <div className="text-sm font-bold text-white">Evaluating Speech Sample...</div>
                <div className="text-xs font-mono text-[#38BDF8]">{evalProgressStep}</div>
              </div>
            )}

            {/* Error Message if any */}
            {evalError && (
              <div className="p-4 rounded-xl border border-[#EF4444]/40 bg-[#EF4444]/10 text-xs text-[#F87171] flex items-start space-x-2">
                <svg viewBox="0 0 24 24" className="w-4 h-4 text-[#EF4444] shrink-0 mt-0.5" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <div>
                  <strong className="font-bold">Evaluation Error: </strong>
                  <span>{evalError}</span>
                </div>
              </div>
            )}

            {/* Audio Waveform Recorder & File Ingestion */}
            <AudioWaveformRecorder
              onEvaluateAudio={handleEvaluateAudio}
              onEvaluateTranscript={handleEvaluateTranscript}
              isEvaluating={isEvaluating}
            />
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW C: DETAILED EVALUATION REPORT                        */}
        {/* ========================================================= */}
        {currentView === "viewReport" && (
          <div className="space-y-8 animate-fade-in">
            {evaluationResult ? (
              <>
                {/* Report Header Bar */}
                <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 shadow-xl flex flex-wrap items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg font-bold text-white tracking-wide">
                        Evaluation Report
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-[#6366F1]/20 text-[#818CF8] border border-[#6366F1]/30">
                        Run ID: {evaluationResult.run_id}
                      </span>
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase font-mono border ${
                          evaluationResult.evaluation_mode === "audio_plus_transcript"
                            ? "bg-[#06B6D4]/15 text-[#22D3EE] border-[#06B6D4]/30"
                            : "bg-[#8B5CF6]/15 text-[#C4B5FD] border-[#8B5CF6]/30"
                        }`}
                      >
                        {evaluationResult.evaluation_mode === "audio_plus_transcript"
                          ? "Audio + Transcript Mode"
                          : "Transcript-Only Mode"}
                      </span>
                    </div>
                    <p className="text-xs text-[#94A3B8]">
                      Scenario: <span className="text-[#38BDF8] uppercase font-mono">{evaluationResult.scenario.replace(/_/g, " ")}</span> • Evaluated {new Date(evaluationResult.created_at).toLocaleString()}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={handleExportJson}
                      className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-[#131E33] hover:bg-[#1E2E4A] text-white text-xs font-medium border border-[#1E2E4A] transition-colors cursor-pointer"
                      title="Download verifiable JSON reproducibility package"
                    >
                      <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 text-[#06B6D4]" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                      </svg>
                      <span>Export JSON</span>
                    </button>

                    <a
                      href={getHtmlReportUrl(evaluationResult.run_id)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-[#6366F1] to-[#06B6D4] text-white text-xs font-bold hover:opacity-95 shadow-md shadow-[#6366F1]/20 transition-all"
                    >
                      <svg viewBox="0 0 24 24" className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="6 9 6 2 18 2 18 9"></polyline>
                        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                        <rect x="6" y="14" width="12" height="8"></rect>
                      </svg>
                      <span>Print Standalone Report</span>
                    </a>

                    <button
                      onClick={() => setCurrentView("viewEvaluate")}
                      className="px-3 py-1.5 rounded-xl bg-[#1E2E4A] hover:bg-[#2E456E] text-white text-xs font-medium transition-colors"
                    >
                      New Evaluation
                    </button>
                  </div>
                </div>

                {/* Score Dial & 5-Axis Radar Chart */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Gauge */}
                  <ScoreGauge
                    score={evaluationResult.overall_score}
                    grade={evaluationResult.grade}
                    coverageRatio={evaluationResult.coverage_ratio}
                    coveragePercentage={evaluationResult.coverage_percentage}
                    evaluatedCount={evaluationResult.evaluated_criteria_count}
                    totalEligibleCount={evaluationResult.eligible_criteria_count}
                    missingCriteria={evaluationResult.missing_criteria}
                  />

                  {/* Radar Chart */}
                  <RadarChart criterionScores={evaluationResult.criterion_scores} />
                </div>

                {/* Individual 5-Axis Criterion Scores Grid */}
                <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 shadow-xl space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-[#1E2E4A]">
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                      Rubric Criterion Breakdown & Scoring Anchors
                    </h3>
                    <span className="text-xs text-[#64748B]">Formula: Normalized linear mapping (1–5 scale → 0–100)</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
                    {Object.entries(evaluationResult.criterion_scores).map(([critId, crit]) => {
                      const isEval = crit.status === "evaluated";

                      return (
                        <div
                          key={critId}
                          className={`p-4 rounded-xl border space-y-2 flex flex-col justify-between ${
                            isEval
                              ? "bg-[#131E33]/60 border-[#1E2E4A]"
                              : "bg-[#1E1B2E]/40 border-[#3B2D54]"
                          }`}
                        >
                          <div>
                            <div className="text-[11px] font-bold text-white uppercase font-mono tracking-wider">
                              {crit.criterion_name}
                            </div>
                            <div className="text-[10px] text-[#64748B] mt-0.5">
                              Weight: {Math.round(crit.weight * 100)}%
                            </div>
                          </div>

                          <div className="py-2">
                            {isEval ? (
                              <div className="space-y-1">
                                <div className="flex items-baseline space-x-1.5 font-mono">
                                  <span className="text-2xl font-extrabold text-white">
                                    {crit.raw_rating?.toFixed(1)}
                                  </span>
                                  <span className="text-xs text-[#64748B]">/5</span>
                                  <span className="text-xs text-[#06B6D4] font-bold ml-1">
                                    ({crit.normalized_score?.toFixed(0)} pts)
                                  </span>
                                </div>
                                <div className="text-[10px] text-[#34D399] font-medium">
                                  {crit.scoring_anchor_matched || "Evaluated"}
                                </div>
                              </div>
                            ) : (
                              <div className="space-y-1">
                                <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-[#F59E0B]/15 text-[#FBBF24] border border-[#F59E0B]/30 font-mono">
                                  UNAVAILABLE
                                </span>
                                <p className="text-[10px] text-[#94A3B8] leading-tight">
                                  {crit.reason || "Requires audio recording"}
                                </p>
                              </div>
                            )}
                          </div>

                          <div className="text-[10px] text-[#94A3B8] pt-2 border-t border-[#1E2E4A]/50 line-clamp-2" title={crit.evidence_summary}>
                            {crit.evidence_summary}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Acoustic Telemetry Grid (If audio available) */}
                {evaluationResult.audio_features && evaluationResult.audio_features.is_audio_available && (
                  <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 shadow-xl space-y-4">
                    <div className="flex items-center justify-between pb-3 border-b border-[#1E2E4A]">
                      <div className="flex items-center space-x-2">
                        <span className="w-2.5 h-2.5 rounded-full bg-[#06B6D4]"></span>
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                          Acoustic Measurements & Signal Telemetry
                        </h3>
                      </div>
                      <span className="text-xs text-[#64748B] font-mono">
                        Duration: {evaluationResult.audio_features.duration_sec.toFixed(1)}s
                      </span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                      <div className="p-3 rounded-xl bg-[#0A0F1D]/70 border border-[#1E2E4A]">
                        <div className="text-[10px] text-[#64748B] uppercase font-semibold">Speaking Rate</div>
                        <div className="text-lg font-bold font-mono text-white mt-0.5">
                          {evaluationResult.audio_features.speaking_rate_wpm?.toFixed(0) || "N/A"} <span className="text-xs text-[#64748B]">WPM</span>
                        </div>
                        <div className="text-[10px] text-[#06B6D4]">Target: 130–165 WPM</div>
                      </div>

                      <div className="p-3 rounded-xl bg-[#0A0F1D]/70 border border-[#1E2E4A]">
                        <div className="text-[10px] text-[#64748B] uppercase font-semibold">Pause Distribution</div>
                        <div className="text-lg font-bold font-mono text-white mt-0.5">
                          {evaluationResult.audio_features.total_pauses} <span className="text-xs text-[#64748B]">pauses</span>
                        </div>
                        <div className="text-[10px] text-[#94A3B8]">
                          Mean: {evaluationResult.audio_features.mean_pause_duration_sec.toFixed(2)}s
                        </div>
                      </div>

                      <div className="p-3 rounded-xl bg-[#0A0F1D]/70 border border-[#1E2E4A]">
                        <div className="text-[10px] text-[#64748B] uppercase font-semibold">Pitch Contour F0</div>
                        <div className="text-lg font-bold font-mono text-white mt-0.5">
                          {evaluationResult.audio_features.pitch_f0_mean_hz ? `${evaluationResult.audio_features.pitch_f0_mean_hz.toFixed(0)} Hz` : "N/A"}
                        </div>
                        <div className="text-[10px] text-[#818CF8]">
                          Range: {evaluationResult.audio_features.pitch_semitone_range?.toFixed(1) || "N/A"} semitones
                        </div>
                      </div>

                      <div className="p-3 rounded-xl bg-[#0A0F1D]/70 border border-[#1E2E4A]">
                        <div className="text-[10px] text-[#64748B] uppercase font-semibold">Signal Quality</div>
                        <div className="text-lg font-bold font-mono text-white mt-0.5">
                          {evaluationResult.audio_features.snr_db_estimate.toFixed(1)} <span className="text-xs text-[#64748B]">dB SNR</span>
                        </div>
                        <div className="text-[10px] text-[#34D399]">
                          Clipping: {(evaluationResult.audio_features.clipping_ratio * 100).toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Transcript Inspector */}
                <TranscriptInspector
                  transcript={evaluationResult.transcript_annotation}
                  audioFeatures={evaluationResult.audio_features}
                />

                {/* Actionable Feedback Cards */}
                <FeedbackCards items={evaluationResult.feedback_items} />

                {/* Contrastive Calibration Exemplar Pair */}
                <ContrastiveCalibrationCard
                  matches={evaluationResult.contrastive_matches}
                  scenario={evaluationResult.scenario}
                />

                {/* Reproducibility Metadata Footer */}
                <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-5 shadow-lg text-xs space-y-2 font-mono text-[#64748B]">
                  <div className="text-[11px] font-bold text-white uppercase tracking-wider">
                    Cryptographic Audit Trail & Reproducibility Fingerprint
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                    <div>Dataset Hash: <span className="text-[#38BDF8]">{evaluationResult.reproducibility?.dataset_hash?.slice(0, 24)}...</span></div>
                    <div>Rubric Hash: <span className="text-[#38BDF8]">{evaluationResult.reproducibility?.rubric_hash?.slice(0, 24)}...</span></div>
                    <div>Aggregation Formula: <span className="text-[#CBD5E1]">{evaluationResult.reproducibility?.score_aggregation_formula}</span></div>
                    <div>Evaluator Engine: <span className="text-[#CBD5E1]">{evaluationResult.reproducibility?.software_versions?.evaluator_version}</span></div>
                  </div>
                </div>
              </>
            ) : (
              <div className="rounded-3xl border border-[#1E2E4A] bg-[#0E1626] p-12 text-center space-y-4 shadow-xl">
                <div className="w-12 h-12 rounded-2xl bg-[#6366F1]/10 border border-[#6366F1]/30 flex items-center justify-center text-[#818CF8] mx-auto">
                  <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                  </svg>
                </div>
                <h3 className="text-base font-bold text-white">No Active Speech Evaluation Loaded</h3>
                <p className="text-xs text-[#94A3B8] max-w-md mx-auto">
                  Start an evaluation by recording speech, uploading an audio file, or click below for an instant 1-click evaluation of the gold standard persuasive pitch.
                </p>
                <div className="pt-2 flex justify-center gap-3">
                  <button
                    onClick={handleRunDemo}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#6366F1] to-[#06B6D4] text-white text-xs font-bold hover:opacity-95 shadow-md shadow-[#6366F1]/20 transition-all cursor-pointer"
                  >
                    🚀 Run 1-Click Golden Speech Demo
                  </button>
                  <button
                    onClick={() => setCurrentView("viewEvaluate")}
                    className="px-5 py-2.5 rounded-xl bg-[#131E33] hover:bg-[#1E2E4A] text-white text-xs font-medium border border-[#1E2E4A] transition-colors"
                  >
                    Go to Speech Evaluation
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW D: DATASET EXPLORER                                  */}
        {/* ========================================================= */}
        {currentView === "viewDataset" && (
          <div className="animate-fade-in">
            <DatasetExplorer />
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW E: RUBRIC EDITOR                                     */}
        {/* ========================================================= */}
        {currentView === "viewRubrics" && (
          <div className="animate-fade-in">
            <RubricEditor />
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW F: EVALUATION HISTORY                                */}
        {/* ========================================================= */}
        {currentView === "viewHistory" && (
          <div className="animate-fade-in">
            <EvaluationHistoryTable onSelectRun={handleSelectHistoryRun} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-[#1E2E4A] bg-[#0A0F1D] px-6 py-4 text-xs text-[#64748B] flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <span className="font-extrabold text-[#CBD5E1]">OratorIQ</span>
          <span>•</span>
          <span>Evidence-Based Speech Evaluation & Coaching Platform</span>
        </div>
        <div className="flex items-center space-x-4 font-mono text-[11px]">
          <span>Dataset: 52 Pairs (v1.0.0-gold)</span>
          <span>•</span>
          <span>Rubric: 5-Axis Normalized</span>
          <span>•</span>
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#06B6D4] hover:underline"
          >
            OpenAPI Docs
          </a>
        </div>
      </footer>
    </div>
  );
}
