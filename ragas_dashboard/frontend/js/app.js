/**
 * OratorIQ — Evidence-Based Speech Coach: Frontend Application Controller
 * Manages audio recording, acoustic visualizer, evaluation orchestration,
 * radar charts, contrastive dataset explorer, rubric editor, and history persistence.
 */

class OratorIQApp {
  constructor() {
    this.currentView = 'viewHome';
    this.currentRunResult = null;
    this.datasetPairs = [];
    this.activeRubric = null;
    this.inputMode = 'mic'; // 'mic', 'upload', 'text'

    // Audio Recording state
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.recordedAudioBlob = null;
    this.isRecording = false;
    this.recordTimerInterval = null;
    this.recordSeconds = 0;
    this.audioContext = null;
    this.analyser = null;
    this.animFrameId = null;

    // Web Speech Recognition
    this.recognition = null;
    this.isRecognizing = false;

    // Selected file
    this.selectedFile = null;

    // DOM Elements
    this.engineStatusPill = document.getElementById('engineStatusPill');
    this.engineStatusText = document.getElementById('engineStatusText');

    this.init();
  }

  async init() {
    this.setupNavigation();
    this.setupDropZone();
    this.setupSpeechRecognition();
    await this.checkEngineReadiness();
    await this.loadDatasetExplorer();
    await this.loadRubricEditor();
    await this.loadEvaluationHistory();

    // Setup 1-Click Demo Button
    const demoBtn = document.getElementById('quickDemoBtn');
    if (demoBtn) {
      demoBtn.addEventListener('click', () => this.runGoldenDemo());
    }

    // Setup Transcript counter
    const transcriptInput = document.getElementById('evalTranscriptInput');
    if (transcriptInput) {
      transcriptInput.addEventListener('input', () => this.updateWordCount());
    }
  }

  // --- 1. Navigation Controller ---
  setupNavigation() {
    const tabBtns = document.querySelectorAll('.nav-tab-btn');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetView = btn.getAttribute('data-view');
        this.navigateTo(targetView);
      });
    });
  }

  navigateTo(viewId) {
    this.currentView = viewId;

    // Update nav tab active states
    document.querySelectorAll('.nav-tab-btn').forEach(b => {
      if (b.getAttribute('data-view') === viewId) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });

    // Show target section
    document.querySelectorAll('.view-section').forEach(sec => {
      if (sec.id === viewId) {
        sec.classList.add('active');
      } else {
        sec.classList.remove('active');
      }
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Refresh context if needed
    if (viewId === 'viewHistory') {
      this.loadEvaluationHistory();
    }
  }

  // --- 2. Engine Readiness Probe ---
  async checkEngineReadiness() {
    try {
      const res = await fetch('/api/v1/ready');
      if (!res.ok) throw new Error('Ready probe returned non-200');
      const data = await res.json();
      if (this.engineStatusText && this.engineStatusPill) {
        this.engineStatusText.textContent = 'Audio & Rubric Engine Ready';
        this.engineStatusPill.style.borderColor = 'rgba(16, 185, 129, 0.4)';
      }
    } catch (err) {
      if (this.engineStatusText) {
        this.engineStatusText.textContent = 'Limited Engine Mode';
      }
    }
  }

  // --- 3. Input Mode Selector (Mic vs Upload vs Text) ---
  setInputMode(mode) {
    this.inputMode = mode;
    const btnMic = document.getElementById('modeBtnMic');
    const btnUpload = document.getElementById('modeBtnUpload');
    const btnText = document.getElementById('modeBtnText');
    const secMic = document.getElementById('sectionMicRecorder');
    const secUpload = document.getElementById('sectionFileUpload');
    const modeBadge = document.getElementById('evalStudioModeBadge');

    [btnMic, btnUpload, btnText].forEach(b => b.classList.remove('active'));
    [secMic, secUpload].forEach(s => s.classList.remove('active'));

    if (mode === 'mic') {
      btnMic.classList.add('active');
      secMic.classList.add('active');
      modeBadge.textContent = 'MODE: LIVE AUDIO RECORDING';
    } else if (mode === 'upload') {
      btnUpload.classList.add('active');
      secUpload.classList.add('active');
      modeBadge.textContent = 'MODE: AUDIO FILE UPLOAD';
    } else {
      btnText.classList.add('active');
      modeBadge.textContent = 'MODE: TRANSCRIPT ONLY (VOCAL DELIVERY UNAVAILABLE)';
    }
  }

  // --- 4. Browser Microphone Recording & Waveform Visualizer ---
  async startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.audioChunks = [];
      this.recordedAudioBlob = null;
      this.mediaRecorder = new MediaRecorder(stream);

      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) this.audioChunks.push(e.data);
      };

      this.mediaRecorder.onstop = () => {
        this.recordedAudioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        const previewPlayer = document.getElementById('audioPreviewPlayer');
        const previewContainer = document.getElementById('recordingPreviewContainer');
        if (previewPlayer && previewContainer) {
          previewPlayer.src = URL.createObjectURL(this.recordedAudioBlob);
          previewContainer.style.display = 'block';
        }
      };

      this.mediaRecorder.start(100);
      this.isRecording = true;

      // Start Web Audio visualizer
      this.setupVisualizer(stream);

      // Start timer
      this.recordSeconds = 0;
      const timeDisplay = document.getElementById('recordingTimeDisplay');
      this.recordTimerInterval = setInterval(() => {
        this.recordSeconds++;
        const mins = String(Math.floor(this.recordSeconds / 60)).padStart(2, '0');
        const secs = String(this.recordSeconds % 60).padStart(2, '0');
        if (timeDisplay) timeDisplay.textContent = `${mins}:${secs}`;
      }, 1000);

      // Update buttons
      document.getElementById('recordStartBtn').disabled = true;
      document.getElementById('recordStopBtn').disabled = false;
      document.getElementById('recordResetBtn').disabled = false;
      document.getElementById('recordBtnText').textContent = 'Recording in Progress...';

      // Optionally start Web Speech recognition if enabled
      if (this.recognition && !this.isRecognizing) {
        try { this.recognition.start(); } catch (e) {}
      }

    } catch (err) {
      alert(`Could not access microphone: ${err.message}. Please verify browser microphone permissions or use Audio File Upload mode.`);
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.mediaRecorder.stream.getTracks().forEach(t => t.stop());
      this.isRecording = false;
    }

    if (this.recordTimerInterval) {
      clearInterval(this.recordTimerInterval);
    }

    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
    }

    document.getElementById('recordStartBtn').disabled = false;
    document.getElementById('recordStopBtn').disabled = true;
    document.getElementById('recordBtnText').textContent = 'Record Again';

    if (this.recognition && this.isRecognizing) {
      try { this.recognition.stop(); } catch (e) {}
    }
  }

  resetRecording() {
    this.stopRecording();
    this.recordedAudioBlob = null;
    this.audioChunks = [];
    document.getElementById('recordingTimeDisplay').textContent = '00:00';
    document.getElementById('recordingPreviewContainer').style.display = 'none';
    document.getElementById('recordResetBtn').disabled = true;
  }

  setupVisualizer(stream) {
    const canvas = document.getElementById('micWaveformCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    this.audioContext = new AudioContextClass();
    const source = this.audioContext.createMediaStreamSource(stream);
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 256;
    source.connect(this.analyser);

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      this.animFrameId = requestAnimationFrame(draw);
      this.analyser.getByteFrequencyData(dataArray);

      ctx.fillStyle = '#04060b';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 2.2;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height * 0.85;
        const grad = ctx.createLinearGradient(0, canvas.height, 0, 0);
        grad.addColorStop(0, '#6366f1');
        grad.addColorStop(1, '#06b6d4');

        ctx.fillStyle = grad;
        ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
        x += barWidth;
      }
    };
    draw();
  }

  // --- 5. Drag & Drop File Upload ---
  setupDropZone() {
    const dropZone = document.getElementById('fileDropZone');
    const fileInput = document.getElementById('audioFileInput');
    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        this.handleSelectedFile(e.target.files[0]);
      }
    });

    ['dragenter', 'dragover'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#06b6d4';
        dropZone.style.background = 'rgba(6, 182, 212, 0.05)';
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'rgba(99, 102, 241, 0.35)';
        dropZone.style.background = 'transparent';
      });
    });

    dropZone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.handleSelectedFile(e.dataTransfer.files[0]);
      }
    });
  }

  handleSelectedFile(file) {
    this.selectedFile = file;
    document.getElementById('selectedFileName').textContent = file.name;
    const mb = (file.size / (1024 * 1024)).toFixed(2);
    document.getElementById('selectedFileSize').textContent = `${mb} MB`;
    document.getElementById('selectedFileInfo').style.display = 'flex';
  }

  clearSelectedFile() {
    this.selectedFile = null;
    document.getElementById('audioFileInput').value = '';
    document.getElementById('selectedFileInfo').style.display = 'none';
  }

  // --- 6. Live Speech-to-Text Recognition Integration ---
  setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';

      this.recognition.onresult = (event) => {
        let transcript = '';
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript + ' ';
        }
        const textInput = document.getElementById('evalTranscriptInput');
        if (textInput) {
          textInput.value = transcript.trim();
          this.updateWordCount();
        }
      };

      this.recognition.onstart = () => {
        this.isRecognizing = true;
        const btn = document.getElementById('webSpeechToggleBtn');
        if (btn) btn.innerHTML = '<span>🔴 Listening...</span>';
      };

      this.recognition.onend = () => {
        this.isRecognizing = false;
        const btn = document.getElementById('webSpeechToggleBtn');
        if (btn) btn.innerHTML = '<span>🎙️ Live Speech-to-Text</span>';
      };
    }
  }

  toggleWebSpeechRecognition() {
    if (!this.recognition) {
      alert('Browser speech recognition is not supported in this browser. Please use Chrome/Edge, or paste your transcript manually.');
      return;
    }
    if (this.isRecognizing) {
      this.recognition.stop();
    } else {
      this.recognition.start();
    }
  }

  updateWordCount() {
    const text = document.getElementById('evalTranscriptInput').value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    const chars = text.length;
    document.getElementById('wordCountLabel').textContent = `${words} words • ${chars} characters`;
  }

  // --- 7. Execution: Run Speech Evaluation ---
  async executeEvaluation() {
    const scenario = document.getElementById('evalScenarioSelect').value;
    const rubricId = document.getElementById('evalRubricSelect').value;
    const promptText = document.getElementById('evalPromptInput').value.trim();
    const transcriptText = document.getElementById('evalTranscriptInput').value.trim();

    // Determine payload
    let audioPayload = null;
    if (this.inputMode === 'mic' && this.recordedAudioBlob) {
      audioPayload = this.recordedAudioBlob;
    } else if (this.inputMode === 'upload' && this.selectedFile) {
      audioPayload = this.selectedFile;
    }

    if (this.inputMode !== 'text' && !audioPayload && !transcriptText) {
      alert('Please record speech, upload an audio file, or enter a speech transcript.');
      return;
    }

    // Show Progress Box
    const progressBox = document.getElementById('evalProgressBox');
    const progressBar = document.getElementById('evalProgressBar');
    const progressText = document.getElementById('evalProgressStepText');
    const progressPercent = document.getElementById('evalProgressPercentText');
    progressBox.style.display = 'block';

    const updateStep = (pct, msg) => {
      progressBar.style.width = `${pct}%`;
      progressPercent.textContent = `${pct}%`;
      progressText.textContent = msg;
    };

    updateStep(20, 'Validating payload and audio containers...');

    try {
      let result = null;

      if (audioPayload) {
        updateStep(40, 'Decoding PCM signal & extracting acoustic telemetry (WPM, pitch, pauses)...');
        const formData = new FormData();
        const ext = audioPayload.type && audioPayload.type.includes('webm') ? 'webm' : 'wav';
        formData.append('file', audioPayload, `speech_recording.${ext}`);
        formData.append('scenario', scenario);
        formData.append('rubric_id', rubricId);
        if (promptText) formData.append('speech_prompt', promptText);
        if (transcriptText) formData.append('transcript', transcriptText);

        updateStep(65, 'Scoring multi-axis rubric & matching contrastive exemplars...');
        const res = await fetch('/api/v1/evaluations/audio', {
          method: 'POST',
          body: formData
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Server error: ${res.status}`);
        }
        result = await res.json();

      } else {
        updateStep(50, 'Analyzing transcript syntax, discourse markers, and lexical disfluencies...');
        const payload = {
          transcript: transcriptText,
          scenario: scenario,
          rubric_id: rubricId,
          speech_prompt: promptText || null
        };

        updateStep(75, 'Scoring available rubric axes & generating actionable feedback...');
        const res = await fetch('/api/v1/evaluations/transcript', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Server error: ${res.status}`);
        }
        result = await res.json();
      }

      updateStep(100, 'Evaluation complete! Preparing interactive dashboard report...');
      setTimeout(() => {
        progressBox.style.display = 'none';
        this.renderEvaluationReport(result);
        this.navigateTo('viewReport');
      }, 500);

    } catch (err) {
      progressBox.style.display = 'none';
      alert(`Evaluation failed: ${err.message}`);
    }
  }

  resetEvaluationForm() {
    this.resetRecording();
    this.clearSelectedFile();
    document.getElementById('evalTranscriptInput').value = '';
    document.getElementById('evalPromptInput').value = '';
    this.updateWordCount();
  }

  // --- 8. Render Evaluation Report ---
  renderEvaluationReport(result) {
    this.currentRunResult = result;

    document.getElementById('reportEmptyState').style.display = 'none';
    document.getElementById('reportContentContainer').style.display = 'block';

    // Header info
    document.getElementById('reportRunIdDisplay').textContent = result.run_id;
    document.getElementById('reportScenarioTitle').textContent = this.formatScenarioName(result.scenario);
    document.getElementById('reportModeTag').textContent = result.evaluation_mode === 'audio_plus_transcript' ? '🎙️ Audio + Transcript' : '📝 Transcript-Only Mode';
    document.getElementById('reportTimestampTag').textContent = result.created_at.replace('T', ' ').slice(0, 19) + ' UTC';
    document.getElementById('reportRubricVerTag').textContent = `Rubric v${result.reproducibility.rubric_version}`;

    // Score Dial & Grade
    const scoreNum = result.overall_score !== null ? result.overall_score : 'N/A';
    document.getElementById('reportOverallScoreNum').textContent = scoreNum;
    document.getElementById('reportGradeBadge').textContent = `GRADE ${result.grade}`;
    document.getElementById('reportCoverageBadge').textContent = `${result.coverage_percentage}% Coverage (${result.evaluated_criteria_count} of ${result.eligible_criteria_count} criteria)`;

    // Dial animation
    if (result.overall_score !== null) {
      const circle = document.getElementById('reportScoreGaugeCircle');
      const circumference = 2 * Math.PI * 52; // ~326.7
      const offset = circumference - (result.overall_score / 100) * circumference;
      circle.style.strokeDashoffset = offset;
    }

    // Acoustic Stats Box
    const af = result.audio_features;
    const acAlert = document.getElementById('reportAcousticUnavailableAlert');
    const acGrid = document.getElementById('reportAcousticStatsGrid');

    if (af && af.is_audio_available) {
      acAlert.style.display = 'none';
      acGrid.style.display = 'grid';
      document.getElementById('acStatWpm').textContent = af.speaking_rate_wpm ? `${af.speaking_rate_wpm} WPM` : '--';
      document.getElementById('acStatPauses').textContent = `${af.total_pauses} pauses (${(af.silent_region_proportion * 100).toFixed(0)}% silence)`;
      document.getElementById('acStatPitch').textContent = af.pitch_semitone_range ? `${af.pitch_semitone_range} st` : 'N/A';
      document.getElementById('acStatSnr').textContent = `${af.snr_db_estimate} dB`;
    } else {
      acGrid.style.display = 'none';
      acAlert.style.display = 'block';
    }

    // Draw Radar Chart
    this.renderRadarChart(result.criterion_scores);

    // Render Transcript Segments
    this.renderTranscriptSegments(result.transcript_annotation);

    // Render Criterion Breakdown Table
    this.renderCriterionTable(result.criterion_scores);

    // Render Feedback Cards
    this.renderFeedbackCards(result.feedback_items);

    // Render Contrastive Matches
    this.renderContrastiveMatches(result.contrastive_matches);

    // Render Reproducibility Grid
    this.renderReproducibilityGrid(result.reproducibility);
  }

  renderRadarChart(criterionScores) {
    const canvas = document.getElementById('rubricRadarCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    // Filter only evaluated axes
    const axes = [];
    const values = [];

    const labelMap = {
      content_and_relevance: 'Content',
      structure_and_coherence: 'Structure',
      fluency_and_pacing: 'Fluency',
      vocal_delivery: 'Vocal',
      clarity_and_conciseness: 'Clarity'
    };

    for (const [cId, cr] of Object.entries(criterionScores)) {
      if (cr.status === 'evaluated' && cr.normalized_score !== null) {
        axes.push(labelMap[cId] || cId);
        values.push(cr.normalized_score);
      }
    }

    if (axes.length < 3) {
      // Bar chart fallback if fewer than 3 axes
      ctx.fillStyle = '#94a3b8';
      ctx.font = '12px Inter';
      ctx.fillText('Insufficient axes for radar polygon', 20, 30);
      return;
    }

    const centerX = W / 2;
    const centerY = H / 2 + 5;
    const radius = Math.min(centerX, centerY) - 40;
    const totalAxes = axes.length;
    const angleSlice = (Math.PI * 2) / totalAxes;

    // Draw concentric polygon rings (25, 50, 75, 100)
    [0.25, 0.5, 0.75, 1.0].forEach(level => {
      ctx.beginPath();
      for (let i = 0; i < totalAxes; i++) {
        const r = radius * level;
        const angle = i * angleSlice - Math.PI / 2;
        const x = centerX + r * Math.cos(angle);
        const y = centerY + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // Draw axis lines and labels
    ctx.font = '11px Outfit, sans-serif';
    ctx.fillStyle = '#94a3b8';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let i = 0; i < totalAxes; i++) {
      const angle = i * angleSlice - Math.PI / 2;
      const xEnd = centerX + radius * Math.cos(angle);
      const yEnd = centerY + radius * Math.sin(angle);

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(xEnd, yEnd);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
      ctx.stroke();

      const xLabel = centerX + (radius + 20) * Math.cos(angle);
      const yLabel = centerY + (radius + 20) * Math.sin(angle);
      ctx.fillText(axes[i], xLabel, yLabel);
    }

    // Draw score polygon
    ctx.beginPath();
    for (let i = 0; i < totalAxes; i++) {
      const val = values[i] / 100.0;
      const r = radius * val;
      const angle = i * angleSlice - Math.PI / 2;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fillStyle = 'rgba(6, 182, 212, 0.25)';
    ctx.fill();
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Draw points
    for (let i = 0; i < totalAxes; i++) {
      const val = values[i] / 100.0;
      const r = radius * val;
      const angle = i * angleSlice - Math.PI / 2;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);

      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#fff';
      ctx.fill();
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth = 2;
      ctx.stroke();
    }
  }

  renderTranscriptSegments(annotation) {
    const feed = document.getElementById('reportTranscriptSegmentsFeed');
    feed.innerHTML = '';

    const fillerCount = annotation.filler_words_detected.reduce((acc, f) => acc + f.count, 0);
    document.getElementById('reportFillerCountBadge').textContent = `${fillerCount} Fillers Detected`;
    document.getElementById('reportReadabilityBadge').textContent = `Flesch Ease: ${annotation.readability_flesch_score} / 100`;

    if (!annotation.segments || annotation.segments.length === 0) {
      feed.innerHTML = `<div class="transcript-segment-row"><span class="segment-text">${annotation.text}</span></div>`;
      return;
    }

    annotation.segments.forEach(seg => {
      const row = document.createElement('div');
      row.className = 'transcript-segment-row';

      const tsText = (seg.start_time !== null && seg.end_time !== null)
        ? `[${seg.start_time.toFixed(1)}s - ${seg.end_time.toFixed(1)}s]`
        : `[#${seg.id}]`;

      // Highlight filler words inside segment
      let highlighted = seg.text;
      ['um', 'uh', 'like', 'you know', 'basically'].forEach(filler => {
        const regex = new RegExp(`\\b(${filler})\\b`, 'gi');
        highlighted = highlighted.replace(regex, `<span class="tag-filler">$1</span>`);
      });

      row.innerHTML = `
        <span class="segment-ts">${tsText}</span>
        <span class="segment-text">${highlighted}</span>
      `;

      // Click to seek audio
      row.addEventListener('click', () => {
        const audio = document.getElementById('reportAudioElement');
        if (audio && seg.start_time !== null) {
          audio.currentTime = seg.start_time;
          audio.play();
        }
      });

      feed.appendChild(row);
    });
  }

  renderCriterionTable(criterionScores) {
    const tbody = document.getElementById('reportCriterionTableBody');
    tbody.innerHTML = '';

    for (const [cId, cr] of Object.entries(criterionScores)) {
      const tr = document.createElement('tr');
      const scoreStr = cr.normalized_score !== null ? `<strong>${cr.normalized_score}</strong> / 100` : '<span style="color: var(--accent-coral)">N/A</span>';
      const ratingStr = cr.raw_rating !== null ? `${cr.raw_rating} / 5` : '--';
      const statusClass = cr.status === 'evaluated' ? 'badge-evaluated' : 'badge-unavailable';

      tr.innerHTML = `
        <td><strong>${cr.criterion_name}</strong></td>
        <td>${(cr.weight * 100).toFixed(0)}%</td>
        <td>${ratingStr}</td>
        <td>${scoreStr}</td>
        <td><span class="${statusClass}">${cr.status.toUpperCase()}</span></td>
        <td style="font-size: 12px; color: #cbd5e1;">${cr.evidence_summary}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  renderFeedbackCards(items) {
    const grid = document.getElementById('reportFeedbackCardsGrid');
    grid.innerHTML = '';

    if (!items || items.length === 0) {
      grid.innerHTML = '<div class="card"><p style="color: #94a3b8;">No critical issues detected. Excellent speech delivery!</p></div>';
      return;
    }

    items.forEach(fb => {
      const card = document.createElement('div');
      card.className = `feedback-card severity-${fb.severity}`;

      card.innerHTML = `
        <div class="feedback-top-row">
          <span class="fb-criterion">${fb.criterion_name}</span>
          <span class="fb-severity">${fb.severity.toUpperCase()}</span>
        </div>
        <h4>${fb.observed_issue}</h4>
        ${fb.measured_value ? `<div class="fb-measured">${fb.measured_value}</div>` : ''}
        <p class="fb-explanation">${fb.explanation}</p>
        <div class="fb-action-box">
          <p><strong>Recommended Action:</strong> ${fb.recommended_action}</p>
          <p style="margin-top: 6px;"><strong>Practice Drill:</strong> ${fb.example_rewrite_or_exercise}</p>
        </div>
      `;
      grid.appendChild(card);
    });
  }

  renderContrastiveMatches(matches) {
    const container = document.getElementById('reportContrastiveMatchCard');
    if (!matches || matches.length === 0) {
      container.innerHTML = '<p style="color: #94a3b8;">No contrastive pair matched.</p>';
      return;
    }

    const match = matches[0];
    const pair = this.datasetPairs.find(p => p.pair_id === match.matched_pair_id) || null;

    let columnsHtml = '';
    if (pair) {
      columnsHtml = `
        <div class="contrastive-columns">
          <div class="c-col c-col-ideal">
            <div class="c-col-header">
              <span class="c-badge-ideal">IDEAL SPEECH EXEMPLAR (${pair.ideal_sample.sample_id})</span>
              <span class="badge-mini">Rating 5/5</span>
            </div>
            <p class="c-transcript">"${pair.ideal_sample.transcript}"</p>
            <div class="c-analysis-box">${pair.ideal_sample.annotation_rationale}</div>
          </div>

          <div class="c-col c-col-flawed">
            <div class="c-col-header">
              <span class="c-badge-flawed">FLAWED SPEECH EXEMPLAR (${pair.flawed_sample.sample_id})</span>
              <span class="badge-mini" style="background: rgba(239, 68, 68, 0.2); color: #f87171;">Flaw: ${pair.primary_flaw}</span>
            </div>
            <p class="c-transcript">"${pair.flawed_sample.transcript}"</p>
            <div class="c-analysis-box">${pair.flawed_sample.annotation_rationale}</div>
          </div>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="card-header">
        <h4>Matched Reference Pair: <code>${match.matched_pair_id}</code></h4>
        <span class="badge-mini">${match.primary_flaw}</span>
      </div>
      <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 12px;"><strong>Pedagogical Calibration:</strong> ${match.contrastive_delta_analysis}</p>
      ${columnsHtml}
    `;
  }

  renderReproducibilityGrid(repro) {
    const grid = document.getElementById('reportReproGrid');
    grid.innerHTML = `
      <div class="repro-item">
        <span>Run ID</span>
        <code>${repro.run_id}</code>
      </div>
      <div class="repro-item">
        <span>Input SHA-256</span>
        <code>${repro.input_sha256 ? repro.input_sha256.slice(0, 16) + '...' : 'N/A'}</code>
      </div>
      <div class="repro-item">
        <span>Dataset Hash</span>
        <code>${repro.dataset_hash ? repro.dataset_hash.slice(0, 16) + '...' : 'N/A'}</code>
      </div>
      <div class="repro-item">
        <span>Rubric Hash</span>
        <code>${repro.rubric_hash || 'speech_default_v1'}</code>
      </div>
      <div class="repro-item">
        <span>Score Aggregation Formula</span>
        <code>sum(norm_score * weight) / sum(avail_weights)</code>
      </div>
    `;
  }

  exportJsonReport() {
    if (!this.currentRunResult) return;
    const blob = new Blob([JSON.stringify(this.currentRunResult, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `oratoriq_report_${this.currentRunResult.run_id}.json`;
    a.click();
  }

  exportHtmlReport() {
    if (!this.currentRunResult) return;
    window.open(`/api/v1/evaluations/${this.currentRunResult.run_id}/export.html`, '_blank');
  }

  // --- 9. 1-Click Guided Golden Demo ---
  async runGoldenDemo() {
    // Navigate to evaluation studio
    this.navigateTo('viewEvaluate');

    // Load rich sample transcript
    const sampleText = "In 2018, a single line of automated pricing code bankrupted three independent clinics in rural Ohio overnight. Not through malice, but through unexamined optimization. When we write algorithms that touch human lives, efficiency cannot be our sole metric. Today, I want to share three architectural guardrails that ensure our machine learning models protect the vulnerable before they optimize the bottom line.";


    document.getElementById('evalTranscriptInput').value = sampleText;
    document.getElementById('evalPromptInput').value = "Inspire developers to build ethically responsible AI systems";
    document.getElementById('evalScenarioSelect').value = "public_speaking";
    this.setInputMode('text');
    this.updateWordCount();

    // Trigger evaluation
    await this.executeEvaluation();
  }

  // --- 10. Dataset Explorer View ---
  async loadDatasetExplorer() {
    try {
      const res = await fetch('/api/v1/datasets/pairs');
      if (!res.ok) return;
      const data = await res.json();
      this.datasetPairs = data.pairs || [];

      // Manifest
      const manifestRes = await fetch('/api/v1/datasets');
      if (manifestRes.ok) {
        const m = await manifestRes.json();
        document.getElementById('datasetManifestVersion').textContent = m.version;
        document.getElementById('datasetManifestPairs').textContent = `${m.total_pairs} Pairs`;
        document.getElementById('datasetManifestSamples').textContent = `${m.total_samples} Samples`;
        document.getElementById('datasetManifestHash').textContent = m.dataset_hash;
      }

      this.filterDatasetPairs();
    } catch (e) {
      console.error('Error loading dataset pairs:', e);
    }
  }

  filterDatasetPairs() {
    const scFilter = document.getElementById('datasetScenarioFilter').value;
    const flFilter = document.getElementById('datasetFlawFilter').value;
    const query = document.getElementById('datasetSearchInput').value.toLowerCase().trim();

    const feed = document.getElementById('datasetPairsFeed');
    feed.innerHTML = '';

    const filtered = this.datasetPairs.filter(p => {
      if (scFilter !== 'ALL' && p.scenario !== scFilter) return false;
      if (flFilter !== 'ALL' && p.primary_flaw !== flFilter) return false;
      if (query) {
        const matchIdeal = p.ideal_sample.transcript.toLowerCase().includes(query);
        const matchFlawed = p.flawed_sample.transcript.toLowerCase().includes(query);
        const matchId = p.pair_id.toLowerCase().includes(query);
        if (!matchIdeal && !matchFlawed && !matchId) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      feed.innerHTML = '<div class="card empty-state">No contrastive pairs match the active filter criteria.</div>';
      return;
    }

    filtered.forEach(p => {
      const card = document.createElement('div');
      card.className = 'dataset-pair-card';

      card.innerHTML = `
        <div class="pair-card-header">
          <div class="pair-meta">
            <span class="pair-id">${p.pair_id}</span>
            <span class="meta-tag">${this.formatScenarioName(p.scenario)}</span>
            <span class="flaw-tag">Flaw: ${p.primary_flaw}</span>
            <span class="meta-tag" style="color: var(--accent-coral);">Severity: ${p.flaw_severity}</span>
          </div>
          <button class="btn btn-sm btn-secondary" onclick="app.loadPairIntoEvaluator('${p.pair_id}')">Load into Evaluator</button>
        </div>

        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px;"><strong>Contrastive Rationale:</strong> ${p.contrastive_rationale}</p>

        <div class="contrastive-columns">
          <div class="c-col c-col-ideal">
            <div class="c-col-header">
              <span class="c-badge-ideal">IDEAL SPEECH EXEMPLAR (${p.ideal_sample.sample_id})</span>
              <span class="badge-mini">Rating 5/5</span>
            </div>
            <p class="c-transcript">"${p.ideal_sample.transcript}"</p>
            <div class="c-analysis-box">${p.ideal_sample.annotation_rationale}</div>
          </div>

          <div class="c-col c-col-flawed">
            <div class="c-col-header">
              <span class="c-badge-flawed">FLAWED SPEECH EXEMPLAR (${p.flawed_sample.sample_id})</span>
              <span class="badge-mini" style="background: rgba(239, 68, 68, 0.2); color: #f87171;">Flawed Variant</span>
            </div>
            <p class="c-transcript">"${p.flawed_sample.transcript}"</p>
            <div class="c-analysis-box">${p.flawed_sample.annotation_rationale}</div>
          </div>
        </div>
      `;
      feed.appendChild(card);
    });
  }

  loadPairIntoEvaluator(pairId) {
    const pair = this.datasetPairs.find(p => p.pair_id === pairId);
    if (!pair) return;
    this.navigateTo('viewEvaluate');
    document.getElementById('evalScenarioSelect').value = pair.scenario;
    document.getElementById('evalTranscriptInput').value = pair.flawed_sample.transcript;
    document.getElementById('evalPromptInput').value = pair.communication_goal;
    this.setInputMode('text');
    this.updateWordCount();
  }

  async runDatasetValidation() {
    const modal = document.getElementById('datasetValidationModal');
    const body = document.getElementById('datasetValidationModalBody');
    modal.style.display = 'flex';
    body.innerHTML = '<p>Running schema validation on 52 pairs...</p>';

    try {
      const res = await fetch('/api/v1/datasets/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await res.json();

      let errorHtml = '';
      if (!data.is_valid && data.errors.length > 0) {
        errorHtml = `<div class="alert-box alert-unavailable"><strong>Validation Errors:</strong><ul>${data.errors.map(e => `<li>${e}</li>`).join('')}</ul></div>`;
      }

      body.innerHTML = `
        <div style="font-size: 14px; line-height: 1.7;">
          <p><strong>Status:</strong> <span class="badge-evaluated">${data.is_valid ? 'PASSED (100% VALID)' : 'FAILED'}</span></p>
          <p><strong>Pairs Verified:</strong> ${data.total_pairs_checked}</p>
          <p><strong>Samples Verified:</strong> ${data.total_samples_checked}</p>
          <p><strong>Dataset Hash:</strong> <code style="color: var(--accent-cyan);">${data.dataset_hash}</code></p>
          <p><strong>Scenarios:</strong> ${Object.keys(data.scenarios).length} distinct categories</p>
          <p><strong>Primary Flaws:</strong> ${Object.keys(data.flaw_categories).length} flaw categories</p>
          ${errorHtml}
        </div>
      `;
    } catch (e) {
      body.innerHTML = `<p style="color: var(--accent-coral);">Validation error: ${e.message}</p>`;
    }
  }

  // --- 11. Rubric Configuration Editor View ---
  async loadRubricEditor() {
    try {
      const res = await fetch('/api/v1/rubrics/speech_default_v1');
      if (!res.ok) return;
      this.activeRubric = await res.json();
      document.getElementById('activeRubricHashDisplay').textContent = `${this.activeRubric.rubric_hash} (v${this.activeRubric.version})`;
      this.renderRubricEditor();
    } catch (e) {
      console.error('Error loading rubric:', e);
    }
  }

  renderRubricEditor() {
    if (!this.activeRubric) return;
    const grid = document.getElementById('rubricCriteriaEditorGrid');
    grid.innerHTML = '';

    for (const [cId, conf] of Object.entries(this.activeRubric.criteria)) {
      const card = document.createElement('div');
      card.className = 'criterion-editor-card';

      const weightPct = Math.round(conf.weight * 100);

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <strong>${conf.name}</strong>
            <span style="font-size: 11px; color: var(--text-dim); margin-left: 8px;">(${cId})</span>
          </div>
          <span class="meta-tag">${conf.requires_audio ? 'Requires Audio' : 'Transcript Eligible'}</span>
        </div>
        <p style="font-size: 12px; color: var(--text-muted); margin: 4px 0 10px;">${conf.description}</p>

        <div class="slider-row">
          <label style="font-size: 11px; color: var(--text-muted);">Weight:</label>
          <input type="range" min="0" max="100" step="1" value="${weightPct}" id="slider_${cId}" oninput="app.updateRubricSlider('${cId}')">
          <span class="slider-val" id="val_${cId}">${weightPct}%</span>
        </div>

        <button class="anchors-accordion-toggle" onclick="app.toggleAnchorsAccordion('${cId}')">
          <span>▶ View 1-5 Scoring Anchors</span>
        </button>

        <div class="anchors-editor-body" id="anchors_${cId}" style="display: none;">
          ${Object.entries(conf.anchors).map(([score, anchor]) => `
            <div class="anchor-box">
              <div class="anchor-score">Level ${score}: ${anchor.name}</div>
              <p style="color: #cbd5e1; margin-bottom: 4px;">${anchor.description}</p>
            </div>
          `).join('')}
        </div>
      `;
      grid.appendChild(card);
    }

    this.checkWeightSum();
  }

  updateRubricSlider(cId) {
    const slider = document.getElementById(`slider_${cId}`);
    const valDisplay = document.getElementById(`val_${cId}`);
    valDisplay.textContent = `${slider.value}%`;
    this.checkWeightSum();
  }

  checkWeightSum() {
    let total = 0;
    for (const cId of Object.keys(this.activeRubric.criteria)) {
      const slider = document.getElementById(`slider_${cId}`);
      if (slider) total += parseInt(slider.value, 10);
    }

    const sumDisplay = document.getElementById('rubricWeightSumDisplay');
    const sumStatus = document.getElementById('rubricWeightSumStatus');
    const banner = document.getElementById('rubricWeightValidatorBanner');

    sumDisplay.textContent = `${total}%`;
    if (total === 100) {
      sumStatus.textContent = 'VALID (100.0%)';
      sumStatus.style.color = 'var(--accent-emerald)';
      banner.classList.remove('invalid');
    } else {
      sumStatus.textContent = `INVALID (${total}% != 100%)`;
      sumStatus.style.color = 'var(--accent-coral)';
      banner.classList.add('invalid');
    }
  }

  toggleAnchorsAccordion(cId) {
    const body = document.getElementById(`anchors_${cId}`);
    if (body.style.display === 'none') {
      body.style.display = 'grid';
    } else {
      body.style.display = 'none';
    }
  }

  async saveCustomRubric() {
    let total = 0;
    const newCriteria = JSON.parse(JSON.stringify(this.activeRubric.criteria));

    for (const [cId, conf] of Object.entries(newCriteria)) {
      const slider = document.getElementById(`slider_${cId}`);
      if (slider) {
        const val = parseInt(slider.value, 10);
        total += val;
        conf.weight = val / 100.0;
      }
    }

    if (total !== 100) {
      alert(`Criteria weights must sum to exactly 100% (currently ${total}%).`);
      return;
    }

    const newVersion = (parseFloat(this.activeRubric.version) + 0.1).toFixed(1);
    const payload = {
      rubric_id: this.activeRubric.rubric_id,
      name: this.activeRubric.name,
      version: newVersion,
      criteria: newCriteria
    };

    try {
      const res = await fetch('/api/v1/rubrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Failed to register rubric');
      const data = await res.json();
      this.activeRubric = data.rubric;
      document.getElementById('activeRubricHashDisplay').textContent = `${this.activeRubric.rubric_hash} (v${this.activeRubric.version})`;
      alert(`Rubric v${newVersion} saved successfully with immutable hash: ${this.activeRubric.rubric_hash}`);
    } catch (e) {
      alert(`Error saving rubric: ${e.message}`);
    }
  }

  resetRubricToDefaults() {
    this.loadRubricEditor();
  }

  // --- 12. History Persistence View ---
  async loadEvaluationHistory() {
    const sc = document.getElementById('historyScenarioFilter')?.value || '';
    const query = sc ? `?scenario=${sc}` : '';

    try {
      const res = await fetch(`/api/v1/history${query}`);
      if (!res.ok) return;
      const data = await res.json();
      const runs = data.runs || [];

      // Update Home Table
      const homeBody = document.getElementById('homeRecentRunsBody');
      if (homeBody) {
        if (runs.length === 0) {
          homeBody.innerHTML = '<tr><td colspan="7" class="empty-state">No evaluations recorded yet.</td></tr>';
        } else {
          homeBody.innerHTML = runs.slice(0, 5).map(r => `
            <tr>
              <td><code>${r.run_id}</code></td>
              <td>${r.created_at.slice(0, 16).replace('T', ' ')}</td>
              <td>${this.formatScenarioName(r.scenario)}</td>
              <td><span class="badge-mini">${r.evaluation_mode === 'audio_plus_transcript' ? 'Audio' : 'Text'}</span></td>
              <td><strong>${r.overall_score || 'N/A'}</strong> / 100</td>
              <td>${r.coverage_percentage}%</td>
              <td><button class="btn btn-sm btn-secondary" onclick="app.inspectHistoricalRun('${r.run_id}')">Inspect</button></td>
            </tr>
          `).join('');
        }
      }

      // Update History Page Table
      const histBody = document.getElementById('evaluationHistoryTableBody');
      if (histBody) {
        if (runs.length === 0) {
          histBody.innerHTML = '<tr><td colspan="9" class="empty-state">No evaluations recorded yet.</td></tr>';
        } else {
          histBody.innerHTML = runs.map(r => `
            <tr>
              <td><code>${r.run_id}</code></td>
              <td>${r.created_at.slice(0, 16).replace('T', ' ')}</td>
              <td>${this.formatScenarioName(r.scenario)}</td>
              <td><span class="badge-mini">${r.evaluation_mode}</span></td>
              <td><strong>${r.overall_score || 'N/A'}</strong></td>
              <td><span class="badge-evaluated">${r.grade}</span></td>
              <td>${r.coverage_percentage}%</td>
              <td style="font-size: 11px; color: #94a3b8; max-width: 250px;">${r.transcript_preview}</td>
              <td>
                <button class="btn btn-sm btn-secondary" onclick="app.inspectHistoricalRun('${r.run_id}')">Inspect</button>
              </td>
            </tr>
          `).join('');
        }
      }
    } catch (e) {
      console.error('Error loading history:', e);
    }
  }

  async inspectHistoricalRun(runId) {
    try {
      const res = await fetch(`/api/v1/evaluations/${runId}`);
      if (!res.ok) throw new Error('Run not found');
      const data = await res.json();
      this.renderEvaluationReport(data);
      this.navigateTo('viewReport');
    } catch (e) {
      alert(`Could not load run: ${e.message}`);
    }
  }

  // --- Helper Utilities ---
  formatScenarioName(sc) {
    const map = {
      public_speaking: 'Public Speaking',
      interview_answers: 'Job Interview',
      persuasive_pitches: 'Persuasive Pitch',
      presentation_delivery: 'Presentation Delivery',
      academic_explanations: 'Academic Explanation'
    };
    return map[sc] || sc;
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
  }
}

// Global App Instance
window.addEventListener('DOMContentLoaded', () => {
  window.app = new OratorIQApp();
});
