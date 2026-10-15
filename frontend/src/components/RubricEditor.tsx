"use client";

import React, { useState, useEffect } from "react";
import { RubricDefinition, CriterionConfig } from "@/types";
import { listRubrics, saveRubric } from "@/lib/api";

export function RubricEditor() {
  const [rubrics, setRubrics] = useState<RubricDefinition[]>([]);
  const [selectedRubricId, setSelectedRubricId] = useState<string>("rubric_standard_v1");
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Editable state
  const [rubricName, setRubricName] = useState<string>("Standard Speech Evaluation Rubric");
  const [newVersion, setNewVersion] = useState<string>("v1.1.0");
  const [weights, setWeights] = useState<Record<string, number>>({
    content_and_relevance: 25,
    structure_and_coherence: 20,
    fluency_and_pacing: 20,
    vocal_delivery: 20,
    clarity_and_conciseness: 15,
  });

  const [expandedAnchorCriterion, setExpandedAnchorCriterion] = useState<string | null>(null);

  useEffect(() => {
    loadRubrics();
  }, []);

  const loadRubrics = async () => {
    setLoading(true);
    try {
      const data = await listRubrics();
      setRubrics(data.rubrics || []);
      if (data.rubrics && data.rubrics.length > 0) {
        const active = data.rubrics[0];
        setSelectedRubricId(active.rubric_id);
        setRubricName(active.name);
        const curWeights: Record<string, number> = {};
        Object.entries(active.criteria).forEach(([k, c]) => {
          curWeights[k] = Math.round(c.weight * 100);
        });
        setWeights(curWeights);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRubric = (rId: string) => {
    setSelectedRubricId(rId);
    const found = rubrics.find((r) => r.rubric_id === rId);
    if (found) {
      setRubricName(found.name);
      const curWeights: Record<string, number> = {};
      Object.entries(found.criteria).forEach(([k, c]) => {
        curWeights[k] = Math.round(c.weight * 100);
      });
      setWeights(curWeights);
    }
  };

  const handleWeightChange = (key: string, val: number) => {
    setWeights((prev) => ({
      ...prev,
      [key]: val,
    }));
  };

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);
  const isWeightValid = totalWeight === 100;

  const currentRubric = rubrics.find((r) => r.rubric_id === selectedRubricId);

  const handleSave = async () => {
    if (!isWeightValid) {
      setSaveError("Weights must sum to exactly 100% before registering a rubric version.");
      return;
    }
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(null);

    try {
      // Build updated criteria
      const baseCriteria = currentRubric?.criteria || {};
      const updatedCriteria: Record<string, any> = {};

      Object.entries(weights).forEach(([critKey, weightInt]) => {
        const existing = baseCriteria[critKey] || {
          id: critKey,
          name: critKey.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
          description: "Configured speech evaluation criterion.",
          requires_audio: critKey === "vocal_delivery",
          anchors: {},
        };
        updatedCriteria[critKey] = {
          ...existing,
          weight: weightInt / 100,
        };
      });

      const res = await saveRubric({
        rubric_id: `rubric_${Date.now()}`,
        name: rubricName,
        version: newVersion,
        criteria: updatedCriteria,
      });

      setSaveSuccess(`Rubric version ${newVersion} created successfully (Hash: ${res.rubric.rubric_hash.slice(0, 16)}...)`);
      await loadRubrics();
    } catch (err: any) {
      setSaveError(err.message || "Failed to save rubric version.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-3">
              <span className="text-lg font-bold text-white tracking-wide">
                Evaluation Rubric & Weight Governance
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-[#6366F1]/20 text-[#818CF8] border border-[#6366F1]/30">
                5-Axis Normalized
              </span>
            </div>
            <p className="text-xs text-[#94A3B8]">
              Configure criteria weights, inspect 1–5 scoring anchors, and issue immutable rubric versions
            </p>
          </div>

          {/* Active Rubric Selector */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-[#64748B]">Select Rubric:</span>
            <select
              value={selectedRubricId}
              onChange={(e) => handleSelectRubric(e.target.value)}
              className="bg-[#131E33] border border-[#1E2E4A] rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-[#6366F1]"
            >
              {rubrics.map((r) => (
                <option key={r.rubric_id} value={r.rubric_id}>
                  {r.name} ({r.version})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Rubric Hash & Version Metadata */}
        {currentRubric && (
          <div className="mt-4 p-3.5 rounded-xl bg-[#0A0F1D]/60 border border-[#1E2E4A] flex flex-wrap items-center justify-between text-xs gap-3 font-mono">
            <div>
              <span className="text-[#64748B]">Rubric Hash: </span>
              <span className="text-[#38BDF8]">{currentRubric.rubric_hash}</span>
            </div>
            <div>
              <span className="text-[#64748B]">Status: </span>
              <span className="text-[#34D399]">Immutable Active Version ({currentRubric.version})</span>
            </div>
          </div>
        )}
      </div>

      {/* Weight Editor Card */}
      <div className="rounded-2xl border border-[#1E2E4A] bg-[#0E1626] p-6 shadow-xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[#1E2E4A]">
          <div>
            <h3 className="text-sm font-bold text-white">Criterion Weights & Acoustic Boundaries</h3>
            <p className="text-[11px] text-[#64748B]">
              Weights must sum exactly to 100%. In transcript-only mode, weights normalize exclusively across available criteria.
            </p>
          </div>

          {/* Real-time sum indicator */}
          <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-xl border text-xs font-mono font-bold ${
            isWeightValid
              ? "bg-[#10B981]/15 text-[#34D399] border-[#10B981]/30"
              : "bg-[#EF4444]/15 text-[#F87171] border-[#EF4444]/30"
          }`}>
            <span>Total Weight: {totalWeight}%</span>
            <span>{isWeightValid ? "✓ Valid (100%)" : "✗ Must equal 100%"}</span>
          </div>
        </div>

        {/* Criteria Sliders */}
        <div className="space-y-5">
          {Object.entries(weights).map(([critKey, weight]) => {
            const isAudioReq = critKey === "vocal_delivery";
            const isExpanded = expandedAnchorCriterion === critKey;
            const critConfig = currentRubric?.criteria[critKey];

            return (
              <div key={critKey} className="p-4 rounded-xl bg-[#131E33]/50 border border-[#1E2E4A] space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                      {critKey.replace(/_/g, " ")}
                    </span>
                    {isAudioReq && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#06B6D4]/15 text-[#22D3EE] border border-[#06B6D4]/30 uppercase font-mono">
                        Requires Audio Waveform
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className="text-base font-bold font-mono text-[#38BDF8]">{weight}%</span>
                    <button
                      onClick={() => setExpandedAnchorCriterion(isExpanded ? null : critKey)}
                      className="text-xs text-[#94A3B8] hover:text-white underline font-sans"
                    >
                      {isExpanded ? "Hide Anchors" : "View 1–5 Anchors"}
                    </button>
                  </div>
                </div>

                {/* Slider */}
                <input
                  type="range"
                  min="5"
                  max="50"
                  step="5"
                  value={weight}
                  onChange={(e) => handleWeightChange(critKey, parseInt(e.target.value, 10))}
                  className="w-full h-1.5 bg-[#1E2E4A] rounded-lg appearance-none cursor-pointer accent-[#6366F1]"
                />

                {/* Expanded Scoring Anchors */}
                {isExpanded && critConfig?.anchors && (
                  <div className="mt-3 pt-3 border-t border-[#1E2E4A] space-y-2">
                    <div className="text-[11px] font-bold text-[#818CF8] uppercase tracking-wider">
                      Documented 1–5 Scoring Anchors
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
                      {[1, 2, 3, 4, 5].map((lvl) => {
                        const anchor = critConfig.anchors[lvl.toString()];
                        return (
                          <div key={lvl} className="p-2.5 rounded-lg bg-[#0A0F1D] border border-[#1E2E4A] text-[11px] space-y-1">
                            <div className="flex items-center justify-between font-mono font-bold">
                              <span className="text-[#06B6D4]">Score {lvl}</span>
                              <span className="text-[#64748B] text-[10px]">{anchor?.name || ""}</span>
                            </div>
                            <p className="text-[10px] text-[#94A3B8] leading-tight line-clamp-3" title={anchor?.description}>
                              {anchor?.description || "Defined standard"}
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Save New Version Form */}
        <div className="pt-4 border-t border-[#1E2E4A] space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Publish New Rubric Version</h4>
              <p className="text-[11px] text-[#64748B]">
                Creates an immutable snapshot with a cryptographic SHA-256 fingerprint
              </p>
            </div>

            <div className="flex items-center space-x-3">
              <input
                type="text"
                value={newVersion}
                onChange={(e) => setNewVersion(e.target.value)}
                placeholder="v1.1.0"
                className="w-24 bg-[#131E33] border border-[#1E2E4A] rounded-xl px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-[#6366F1]"
              />
              <button
                onClick={handleSave}
                disabled={!isWeightValid || saving}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#6366F1] to-[#06B6D4] text-white text-xs font-semibold hover:opacity-95 shadow-md shadow-[#6366F1]/20 transition-all cursor-pointer disabled:opacity-40"
              >
                {saving ? "Registering Version..." : "Save Immutable Rubric"}
              </button>
            </div>
          </div>

          {saveSuccess && (
            <div className="p-3 rounded-xl bg-[#10B981]/15 border border-[#10B981]/30 text-xs text-[#34D399]">
              ✓ {saveSuccess}
            </div>
          )}

          {saveError && (
            <div className="p-3 rounded-xl bg-[#EF4444]/15 border border-[#EF4444]/30 text-xs text-[#F87171]">
              ✗ {saveError}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
