"use client";

import React from "react";

interface NavbarProps {
  currentView: string;
  onNavigate: (view: string) => void;
  engineStatus: string;
  isReady: boolean;
  onRunDemo: () => void;
}

export function Navbar({ currentView, onNavigate, engineStatus, isReady, onRunDemo }: NavbarProps) {
  const tabs = [
    {
      id: "viewHome",
      label: "Home",
      icon: (
        <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
      ),
    },
    {
      id: "viewEvaluate",
      label: "Speech Evaluation",
      icon: (
        <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="22"></line>
        </svg>
      ),
    },
    {
      id: "viewReport",
      label: "Evaluation Report",
      icon: (
        <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
          <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
        </svg>
      ),
    },
    {
      id: "viewDataset",
      label: "Dataset Explorer",
      badge: "52 Pairs",
      icon: (
        <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="3" y1="9" x2="21" y2="9"></line>
          <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>
      ),
    },
    {
      id: "viewRubrics",
      label: "Rubric Editor",
      icon: (
        <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
      ),
    },
    {
      id: "viewHistory",
      label: "History",
      icon: (
        <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
      ),
    },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[#1E2E4A] bg-[#0A0F1D]/90 backdrop-blur-md px-6 py-3.5 flex items-center justify-between">
      {/* Brand Identity */}
      <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onNavigate("viewHome")}>
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-[#6366F1] to-[#06B6D4] flex items-center justify-center text-white shadow-md">
          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
          </svg>
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-extrabold tracking-wider text-white text-base">ORATORIQ</span>
            <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-[#6366F1]/20 text-[#818CF8] border border-[#6366F1]/30">
              Evidence-Based Speech Coach
            </span>
          </div>
          <p className="text-[11px] text-[#64748B]">Acoustics • Contrastive Corpus • Versioned Rubrics</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="hidden lg:flex items-center space-x-1 bg-[#0E1626] p-1 rounded-xl border border-[#1E2E4A]">
        {tabs.map((tab) => {
          const isActive = currentView === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onNavigate(tab.id)}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? "bg-[#1E2E4A] text-white shadow-sm border border-[#2E456E]"
                  : "text-[#94A3B8] hover:text-white hover:bg-[#131E33]"
              }`}
            >
              <span className={isActive ? "text-[#06B6D4]" : "text-[#64748B]"}>{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.badge && (
                <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-[#06B6D4]/20 text-[#06B6D4]">
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Actions */}
      <div className="flex items-center space-x-3">
        {/* Engine Readiness Status */}
        <div
          className={`flex items-center space-x-2 px-2.5 py-1 rounded-full text-xs border ${
            isReady
              ? "bg-[#10B981]/10 text-[#34D399] border-[#10B981]/30"
              : "bg-[#F59E0B]/10 text-[#FBBF24] border-[#F59E0B]/30"
          }`}
          title="FastAPI Engine Health and Capabilities Probe"
        >
          <span className={`w-2 h-2 rounded-full ${isReady ? "bg-[#10B981] animate-pulse" : "bg-[#F59E0B]"}`}></span>
          <span className="font-mono text-[11px] font-medium">{engineStatus}</span>
        </div>

        {/* 1-Click Guided Demo */}
        <button
          onClick={onRunDemo}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-[#6366F1] to-[#06B6D4] text-white text-xs font-semibold hover:opacity-95 shadow-md shadow-[#6366F1]/20 transition-all cursor-pointer"
          title="Instant 1-Click Golden Speech Evaluation Demo"
        >
          <span>🚀 1-Click Demo</span>
        </button>

        {/* API Docs Link */}
        <a
          href="http://127.0.0.1:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="hidden sm:flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-[#131E33] hover:bg-[#192742] text-[#94A3B8] hover:text-white text-xs border border-[#1E2E4A] transition-colors"
        >
          <svg viewBox="0 0 24 24" className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          <span>API Docs</span>
        </a>
      </div>
    </header>
  );
}
