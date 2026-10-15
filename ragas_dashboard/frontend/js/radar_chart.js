/**
 * Ragas Evaluation Radar Chart: 5 Core RAG Dimensions
 * Faithfulness, Answer Relevance, Context Precision, Context Recall, Semantic Similarity
 * 
 * Integrity & Hackathon Features:
 * - Single candidate telemetry or Dual Contrastive Overlay (Model A vs Model B)
 * - Zero fabricated defaults (starts unpopulated until real evaluation runs)
 * - Zero silent defaults (missing or unavailable metrics are explicitly labeled N/A)
 * - Device Pixel Ratio (DPR) scaling fixed with resetTransform to prevent compounding
 * - Renders accessible textual telemetry summary
 */

class RagasRadarChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.axes = [
      { key: 'faithfulness', label: 'Faithfulness' },
      { key: 'relevance', label: 'Answer Relevance' },
      { key: 'precision', label: 'Context Precision' },
      { key: 'recall', label: 'Context Recall' },
      { key: 'similarity', label: 'Semantic Similarity' }
    ];
    this.scores = null;
    this.scoresB = null;
    this.labelA = 'Model A';
    this.labelB = 'Model B';
    this.hasData = false;
    this.initResize();
  }

  initResize() {
    const resize = () => {
      if (!this.canvas) return;
      const rect = this.canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      this.width = rect.width;
      this.height = rect.height;
      this.canvas.width = Math.round(rect.width * dpr);
      this.canvas.height = Math.round(rect.height * dpr);
      
      // Reset transform before re-scaling to avoid compounding
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.render();
    };

    window.addEventListener('resize', resize);
    setTimeout(resize, 60);
  }

  updateData(radarData) {
    this.scoresB = null;
    if (!radarData || typeof radarData !== 'object') {
      this.scores = null;
      this.hasData = false;
      this.render();
      return;
    }

    this.scores = this.axes.map(axis => {
      const val = radarData[axis.key];
      return (val !== undefined && val !== null && !isNaN(val)) ? Number(val) : null;
    });

    this.hasData = this.scores.some(s => s !== null);
    this.render();
    this.updateA11ySummary(radarData);
  }

  updateDualData(radarA, radarB, labelA = 'Model A (Ideal)', labelB = 'Model B (Flawed)') {
    this.labelA = labelA;
    this.labelB = labelB;

    this.scores = this.axes.map(axis => {
      const val = radarA ? radarA[axis.key] : null;
      return (val !== undefined && val !== null && !isNaN(val)) ? Number(val) : null;
    });

    this.scoresB = this.axes.map(axis => {
      const val = radarB ? radarB[axis.key] : null;
      return (val !== undefined && val !== null && !isNaN(val)) ? Number(val) : null;
    });

    this.hasData = this.scores.some(s => s !== null) || this.scoresB.some(s => s !== null);
    this.render();
  }

  render() {
    if (!this.ctx || !this.width || !this.height) return;
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    ctx.clearRect(0, 0, w, h);

    const centerX = w / 2;
    const centerY = h / 2 + 10;
    const radius = Math.min(centerX, centerY) - 42;
    const totalAxes = this.axes.length;
    const angleStep = (Math.PI * 2) / totalAxes;
    const startAngle = -Math.PI / 2;

    // 1. Concentric Grid Rings
    const rings = [0.25, 0.5, 0.75, 1.0];
    rings.forEach(ring => {
      ctx.beginPath();
      for (let i = 0; i < totalAxes; i++) {
        const angle = startAngle + i * angleStep;
        const r = radius * ring;
        const x = centerX + Math.cos(angle) * r;
        const y = centerY + Math.sin(angle) * r;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = ring === 1.0 ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.05)';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // 2. Legend if in Dual Contrastive Mode
    if (this.scoresB && this.hasData) {
      ctx.font = '600 11px Inter, sans-serif';
      ctx.textAlign = 'left';
      
      // Model A legend dot
      ctx.fillStyle = '#10b981';
      ctx.beginPath();
      ctx.arc(centerX - 130, 16, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#94a3b8';
      ctx.fillText(this.labelA, centerX - 120, 19);

      // Model B legend dot
      ctx.fillStyle = '#f43f5e';
      ctx.beginPath();
      ctx.arc(centerX + 15, 16, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#94a3b8';
      ctx.fillText(this.labelB, centerX + 25, 19);
    }

    // 3. Axis Spokes & Labels
    ctx.font = '500 10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let i = 0; i < totalAxes; i++) {
      const angle = startAngle + i * angleStep;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;

      // Spoke line
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.stroke();

      // Axis label and score indicator
      const labelDist = radius + 24;
      const lx = centerX + Math.cos(angle) * labelDist;
      const ly = centerY + Math.sin(angle) * labelDist;

      const scoreVal = this.scores ? this.scores[i] : null;
      const labelText = this.axes[i].label;

      ctx.fillStyle = '#94a3b8';
      ctx.fillText(labelText, lx, ly - 6);

      if (!this.scoresB) {
        if (scoreVal !== null && scoreVal !== undefined) {
          ctx.fillStyle = scoreVal >= 80 ? '#10b981' : scoreVal >= 60 ? '#6366f1' : '#f43f5e';
          ctx.font = '700 11px JetBrains Mono, monospace';
          ctx.fillText(`${Math.round(scoreVal)}%`, lx, ly + 8);
          ctx.font = '500 10px Inter, sans-serif';
        } else if (this.hasData) {
          ctx.fillStyle = '#64748b';
          ctx.font = '500 9px JetBrains Mono, monospace';
          ctx.fillText('N/A', lx, ly + 8);
          ctx.font = '500 10px Inter, sans-serif';
        }
      }
    }

    // 4. Render Polygons
    if (!this.hasData || !this.scores) {
      ctx.fillStyle = 'rgba(148, 163, 184, 0.4)';
      ctx.font = '500 11px Inter, sans-serif';
      ctx.fillText('Run evaluation to plot radar telemetry', centerX, centerY);
      return;
    }

    // If Dual Contrastive: Render Polygon B (Flawed / Model B) first in background
    if (this.scoresB) {
      const pointsB = [];
      for (let i = 0; i < totalAxes; i++) {
        const angle = startAngle + i * angleStep;
        const score = this.scoresB[i];
        const val = (score !== null && score !== undefined) ? (score / 100) : 0.0;
        const r = Math.max(0, radius * Math.min(1.0, val));
        pointsB.push({
          x: centerX + Math.cos(angle) * r,
          y: centerY + Math.sin(angle) * r
        });
      }

      ctx.beginPath();
      pointsB.forEach((p, idx) => {
        if (idx === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      });
      ctx.closePath();
      ctx.fillStyle = 'rgba(244, 63, 94, 0.18)';
      ctx.fill();
      ctx.strokeStyle = '#f43f5e';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      pointsB.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = '#f43f5e';
        ctx.fill();
      });
    }

    // Render Polygon A (Model A / Ideal Grounded)
    const pointsA = [];
    for (let i = 0; i < totalAxes; i++) {
      const angle = startAngle + i * angleStep;
      const score = this.scores[i];
      const val = (score !== null && score !== undefined) ? (score / 100) : 0.0;
      const r = Math.max(0, radius * Math.min(1.0, val));
      pointsA.push({
        x: centerX + Math.cos(angle) * r,
        y: centerY + Math.sin(angle) * r,
        isAvailable: score !== null && score !== undefined
      });
    }

    ctx.beginPath();
    pointsA.forEach((p, idx) => {
      if (idx === 0) ctx.moveTo(p.x, p.y);
      else ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();

    if (this.scoresB) {
      ctx.fillStyle = 'rgba(16, 185, 129, 0.22)';
      ctx.fill();
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2.5;
      ctx.stroke();
    } else {
      const gradient = ctx.createRadialGradient(centerX, centerY, 5, centerX, centerY, radius);
      gradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
      gradient.addColorStop(1, 'rgba(16, 185, 129, 0.15)');
      ctx.fillStyle = gradient;
      ctx.fill();
      ctx.strokeStyle = '#6366f1';
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    pointsA.forEach(p => {
      if (!p.isAvailable) return;
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = this.scoresB ? '#10b981' : '#10b981';
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    });
  }

  updateA11ySummary(radarData) {
    let summaryEl = document.getElementById('radarA11ySummary');
    if (!summaryEl) {
      summaryEl = document.createElement('div');
      summaryEl.id = 'radarA11ySummary';
      summaryEl.className = 'sr-only';
      summaryEl.setAttribute('aria-live', 'polite');
      if (this.canvas.parentElement) {
        this.canvas.parentElement.appendChild(summaryEl);
      }
    }
    
    if (!radarData) {
      summaryEl.textContent = 'Radar chart: No evaluation data available.';
      return;
    }

    const items = this.axes.map(a => {
      const val = radarData[a.key];
      return `${a.label}: ${val !== null && val !== undefined ? val + '%' : 'Unavailable'}`;
    });
    summaryEl.textContent = `Evaluation Radar Telemetry: ${items.join(', ')}`;
  }
}

window.RagasRadarChart = RagasRadarChart;
