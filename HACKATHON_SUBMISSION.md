# Hackathon Submission: OratorIQ — Evidence-Based Speech Coach

**Project Name:** OratorIQ — Evidence-Based Speech Coach  
**Problem Statement:** "Develop a speech evaluation system by constructing a custom contrastive dataset of ideal vs. flawed speeches, to generate reproducible custom evaluative rubric-based scores and actionable delivery feedback via an interactive dashboard."  
**Repository Source:** [shringiaashita-beep/portfolio](https://github.com/vibrantlabsai/ragas)  
**Live Studio URL:** `http://127.0.0.1:8000`  
**License:** Apache 2.0  

---

## Executive Summary

Public speaking, executive presentations, job interviews, and high-stakes pitches are critical determinants of career trajectory and leadership efficacy. Yet existing coaching options remain polarized between expensive human consultants and superficial AI tools that output opaque, unverified scores without empirical grounding.

**OratorIQ** introduces a technically defensible, reproducible speech evaluation and delivery coaching platform:
1. **Physical Acoustic Signal Extraction:** Ingests genuine WAV, MP3, WebM, and OGG audio streams, computing speaking rate (Words Per Minute), pause distribution, fundamental frequency ($F_0$) pitch contour, semitone variability (monotony penalty), loudness dynamic range, and recording SNR using `librosa`, `soundfile`, and `scipy.signal`.
2. **Custom Contrastive Dataset (52 Pairs / 104 Exemplars):** Curates a version-controlled, SHA-256 verified corpus of paired ideal and flawed speeches across five core communication scenarios with dimension-specific 1–5 scoring anchors and 13 distinct flaw categories.
3. **Transparent Evaluation Rubric:** Implements a configurable 5-axis rubric (Content 25%, Structure 20%, Fluency 20%, Vocal Delivery 20%, Clarity 15%) mapping 1–5 ordinal anchors to normalized 0–100 scores. Transparently reports missing coverage in transcript-only mode and refuses to fabricate scores.
4. **Evidence-Linked Actionable Recommendations:** Connects every evaluation score to grounded observed timestamps, physical measurements, explanations, and concrete vocal/structure practice drills (e.g., Metronome calibration, Thought-group sprints, Pitch staircases).
5. **Interactive Dark Navy Dashboard:** Complete 6-view single page application (Home, Speech Evaluation Studio with live microphone visualizer, Evaluation Report with Canvas radar charts, Contrastive Dataset Explorer, Rubric Configuration Editor, and Evaluation History).
6. **Reproducibility Guarantee:** Every run produces a unique run ID, SHA-256 input hash, dataset hash, rubric hash, and downloadable JSON/HTML audit report for verifiable reproducibility.

---

## Technical Architecture

```
+-----------------------------------------------------------------------------------------------------------------+
|                                        ORATORIQ SPEECH COACHING PLATFORM                                        |
+-----------------------------------------------------------------------------------------------------------------+
|  [Home / Overview]  |  [Speech Evaluation]  |  [Evaluation Report]  |  [Dataset Explorer]  |  [Rubric Editor]   |
+-----------------------------------------------------------------------------------------------------------------+
                                                        |
         +----------------------------------------------+----------------------------------------------+
         |                                                                                             |
         v                                                                                             v
 [Live Microphone Audio / File Upload]                                                   [Scenario & Rubric Selector]
 (WAV, MP3, WebM, OGG, FLAC)                                                             (Public Speaking, Interview,
                                                                                          Pitch, Presentation, Academic)
         |                                                                                             |
         v                                                                                             v
+-------------------------------------+                                                +-------------------------------------+
|      Audio Ingestion & Validation   |                                                |      Rubric Engine & Registry       |
|  - Magic byte & container probing   |                                                |  - Configurable 5-axis weights      |
|  - Max 50MB, duration bounds        |                                                |  - 1-5 scoring scale anchors        |
+-------------------------------------+                                                |  - Immutable version hash           |
         |                                                                             +-------------------------------------+
         v                                                                                             |
+-------------------------------------+                                                                |
|     Audio Preprocessing & Resample  |                                                                |
|  - Stereo-to-mono conversion        |                                                                |
|  - 16 kHz resampling via scipy      |                                                                |
|  - RMS energy, silence, clipping    |                                                                |
+-------------------------------------+                                                                |
         |                                                                                             |
         +-----------------------------------------------+                                             |
         |                                               |                                             |
         v                                               v                                             v
+-------------------------------------+  +-------------------------------------+  +-------------------------------------+
|        Speech Transcription         |  |      Acoustic Feature Extractor     |  |     Contrastive Dataset Corpus      |
|  - Word & segment timestamps        |  |  - Speaking rate (WPM)              |  |  - 52 Curated ideal vs flawed pairs |
|  - Lexical filler word detection    |  |  - Pause distribution & silence %   |  |  - 13 Distinct flaw categories      |
|  - Repetition & disfluency tracking |  |  - F0 mean, std, & semitone range   |  |  - Strict Pydantic schema auditor   |
+-------------------------------------+  |  - Dynamic range & SNR estimation   |  |  - SHA-256 content verification     |
         |                               +-------------------------------------+  +-------------------------------------+
         |                                               |                                             |
         +-----------------------------------------------+---------------------------------------------+
                                                         |
                                                         v
                                  +---------------------------------------------+
                                  |      OratorIQ Evaluation Orchestrator       |
                                  |  - 5-Axis Rubric Score Calculation          |
                                  |  - Normalization over Available Axes        |
                                  |  - Contrastive Calibration Matching         |
                                  |  - Evidence-Linked Delivery Drills          |
                                  |  - Cryptographic Reproducibility Hash       |
                                  +---------------------------------------------+
                                                         |
                         +-------------------------------+-------------------------------+
                         |                                                               |
                         v                                                               v
              [Interactive Web Studio]                                        [Persistence & API (/api/v1/)]
              - Live Web Audio visualizer                                     - POST /api/v1/evaluations/audio
              - Real-time radar canvas                                        - POST /api/v1/evaluations/transcript
              - Timestamped transcript seek                                   - GET  /api/v1/evaluations/{run_id}
              - Actionable drill cards                                        - GET  /api/v1/datasets/pairs
              - Side-by-side contrastive view                                 - GET  /api/v1/rubrics
              - Exportable JSON & HTML report                                 - GET  /api/v1/history
```

---

## The Custom Contrastive Speech Dataset

The core research artifact of OratorIQ is its **custom contrastive dataset** of ideal versus flawed speech pairs.

### Dataset Specifications
- **Total Contrastive Pairs:** 52 pairs
- **Total Individual Exemplars:** 104 genuine speech transcripts
- **Dataset Version:** `1.0.0`
- **Dataset SHA-256 Hash:** `50dfa86c3b9a9dfb39a54a6fd24ab1a4e21e3a769fdc72c402bc9644fd731db4`
- **Scenarios Covered:**
  - `public_speaking` (11 pairs): Keynotes, commencements, civic addresses, town halls
  - `interview_answers` (11 pairs): Behavioral, system design, leadership, conflict resolution
  - `persuasive_pitches` (10 pairs): Seed venture pitch, enterprise SaaS sales, grant proposals
  - `presentation_delivery` (10 pairs): QBRs, sprint retros, UI demos, security posture reviews
  - `academic_explanations` (10 pairs): Quantum cryptography, CRISPR, entropy, self-attention

### 13 Flaw Categories Implemented
1. `weak_opening`: Apologetic throat-clearing, mic checks, delayed thesis.
2. `poor_logical_structure`: Tangential leaps without roadmap or causal connective logic.
3. `excessive_filler_words`: High density (>4%) of "um", "uh", "like", "you know", "basically".
4. `unnecessary_repetition`: Circular tautological loops repeating identical phrases.
5. `excessively_fast_pacing`: >180 WPM causing cognitive overload.
6. `excessively_slow_pacing`: <110 WPM dragging momentum.
7. `poorly_placed_pauses`: Mid-phrase pauses dividing verbs from direct objects.
8. `weak_transitions`: Missing signposts ("first", "furthermore", "in contrast").
9. `unclear_articulation`: Slurred consonants and dropped syllables.
10. `monotonous_vocal_delivery`: Pitch dynamic range < 2.0 semitones (flat robotic delivery).
11. `failure_to_answer_question`: Evasive diversion away from the interviewer prompt.
12. `unsupported_claims`: Wild assertions lacking empirical or factual substantiation.
13. `weak_or_missing_conclusion`: Anticlimactic trailing finishes ("so, yeah, that's it").

---

## Transparent Rubric Scoring Scale

OratorIQ adheres to an explicit 1–5 ordinal scale mapped linearly to 0–100 normalized scores:
- **Level 1 (0 pts):** Substantial improvement needed; pervasive structural or disfluent flaws.
- **Level 2 (25 pts):** Below target standard; superficial coverage or noticeable hesitation.
- **Level 3 (50 pts):** Developing; competent baseline with room for optimization.
- **Level 4 (75 pts):** Strong; commanding delivery with clear signposting and low disfluencies.
- **Level 5 (100 pts):** Excellent; masterclass rhetoric, crisp diction, and vibrant cadence.

### Score Aggregation Formula
$$\text{overall\_score} = \frac{\sum (\text{normalized\_criterion\_score} \times \text{weight})}{\sum \text{available\_criterion\_weights}}$$

In **transcript-only mode**, `vocal_delivery` (20% weight) is marked `UNAVAILABLE` with an explanatory note. The overall score is computed over the remaining 80% available weight, and coverage is reported transparently as 80.0%. Perfect scores or fabricated numbers are never silently substituted.

---

## Evidence-Linked Delivery Drills

Each evaluation generates concrete, grounded feedback cards containing:
- **Observed Issue:** e.g., "Elevated filler word density (7.1% of total words), dominated by 'um' (6 occurrences)."
- **Measured Value:** e.g., "Filler density: 7.1% (Target: < 2.0%)"
- **Explanation:** Why this physical pattern diminishes audience retention.
- **Action:** Specific behavioural rule to adopt.
- **Concrete Practice Drill:** e.g., "Metronome Pacing Drill: Set metronome to 140 BPM, reciting one word per beat across a 40-word paragraph."

---

## Automated Test Coverage (47/47 Passing)

```bash
# 1. Run OratorIQ Core Engine & API Suite (21 tests)
python -m pytest tests/test_oratoriq_suite.py -v

# 2. Run Dashboard Scaffolding Suite (26 tests)
python -m pytest tests/dashboard/test_dashboard_suite.py -v

# 3. Validate Contrastive Dataset Schema & Hash (CLI)
python -m oratoriq.dataset.validator
```

---

## 1-Click Launch Instructions

```bash
# Clone and launch in one command
git clone https://github.com/vibrantlabsai/ragas.git
cd "ragas"

# Launch self-bootstrapping studio
python run_dashboard.py --port 8000
```
Navigate to `http://127.0.0.1:8000/`. Click **🚀 1-Click Demo** in the top navigation bar to run an instant golden evaluation!
