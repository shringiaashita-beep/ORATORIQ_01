/* ===== PORTFOLIO SCRIPT — Aashita Shringi ===== */

/* ---- Navbar scroll effect ---- */
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
  if (window.scrollY > 60) navbar.classList.add('scrolled');
  else navbar.classList.remove('scrolled');
}, { passive: true });

/* ---- Hamburger menu ---- */
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('nav-links');
hamburger.addEventListener('click', () => {
  const isOpen = navLinks.classList.toggle('open');
  hamburger.setAttribute('aria-expanded', isOpen);
});
navLinks.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    hamburger.setAttribute('aria-expanded', false);
  });
});

/* ---- Scroll Reveal ---- */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      // Animate skill bars when section is visible
      if (e.target.id === 'skill-bars' || e.target.closest('#skill-bars')) {
        animateSkillBars();
      }
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

/* Also observe about section to trigger skill bars */
const aboutSection = document.getElementById('about');
if (aboutSection) {
  const aboutObserver = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) animateSkillBars();
  }, { threshold: 0.2 });
  aboutObserver.observe(aboutSection);
}

function animateSkillBars() {
  document.querySelectorAll('.skill-fill').forEach(fill => {
    const w = fill.dataset.w;
    fill.style.transform = `scaleX(${w})`;
    fill.classList.add('animated');
  });
}

/* ---- Certificate Filter ---- */
const filterBtns = document.querySelectorAll('.filter-btn');
const certCards = document.querySelectorAll('.cert-card');

filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.filter;
    certCards.forEach(card => {
      if (filter === 'all' || card.dataset.category === filter) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    });
  });
});

/* ---- Certificate Modal ---- */
const modal = document.getElementById('cert-modal');
const modalImg = document.getElementById('modal-img');
const modalTitle = document.getElementById('modal-title');
const modalDesc = document.getElementById('modal-desc');
const modalClose = document.getElementById('modal-close');

certCards.forEach(card => {
  card.addEventListener('click', () => {
    modalImg.src = card.dataset.img;
    modalImg.alt = card.dataset.title;
    modalTitle.textContent = card.dataset.title;
    modalDesc.textContent = card.dataset.desc;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    modalClose.focus();
  });
});

modalClose.addEventListener('click', closeModal);
modal.addEventListener('click', (e) => {
  if (e.target === modal) closeModal();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});
function closeModal() {
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

/* ---- Figma Project Image – click to enlarge ---- */
const fpImgWrap = document.getElementById('fp-img-wrap');
if (fpImgWrap) {
  fpImgWrap.addEventListener('click', () => {
    modalImg.src = 'figma-project.png';
    modalImg.alt = 'UI/UX Lab Notebook – Online Food Delivery Website';
    modalTitle.textContent = 'UI/UX Lab Notebook – Online Food Delivery Website';
    modalDesc.textContent = 'Figma project · Complete design process: user flow, wireframes, personas & 4-page layout';
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    modalClose.focus();
  });
}


/* ---- Contact Form ---- */
function handleFormSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('form-submit');
  btn.textContent = 'Sending...';
  btn.disabled = true;
  setTimeout(() => {
    btn.textContent = '✓ Sent!';
    e.target.reset();
    showToast();
    setTimeout(() => {
      btn.textContent = 'Send Message ✦';
      btn.disabled = false;
    }, 3000);
  }, 1200);
}

function showToast() {
  const toast = document.getElementById('toast');
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 4000);
}

/* ---- Resume Preview Keyboard ---- */
const resumePreview = document.getElementById('resume-preview');
if (resumePreview) {
  resumePreview.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      window.open('Intelligent CV Document.pdf', '_blank');
    }
  });
}

/* ============================================================
   FIGMA CANVAS PLAYGROUND
   ============================================================ */
const canvas = document.getElementById('figma-canvas');
const layerItems = document.querySelectorAll('.layer-item');

// State
let selectedId = 'c-rect-1';
let isDragging = false;
let dragEl = null;
let startX, startY, elStartX, elStartY;

// Element configs
const elementProps = {
  'c-rect-1': { size: '160 × 100', radius: '12', opacity: '100%' },
  'c-circle-1': { size: '80 × 80', radius: '50%', opacity: '100%' },
  'c-rect-2': { size: '200 × 60', radius: '8', opacity: '100%' },
  'c-text-1': { size: 'Auto', radius: '0', opacity: '100%' },
  'c-card-1': { size: '140 × 90', radius: '10', opacity: '100%' },
};

function updateProps(id) {
  const p = elementProps[id] || {};
  document.getElementById('prop-size').textContent = p.size || 'Auto';
  document.getElementById('prop-radius').textContent = p.radius || '0';
  document.getElementById('prop-opacity').textContent = p.opacity || '100%';
}

// Select element
function selectEl(id) {
  selectedId = id;
  document.querySelectorAll('.canvas-element').forEach(el => el.classList.remove('selected'));
  const el = document.getElementById(id);
  if (el) el.classList.add('selected');
  layerItems.forEach(item => {
    item.classList.toggle('selected', item.dataset.target === id);
  });
  updateProps(id);
}

// Click to select
document.querySelectorAll('.canvas-element').forEach(el => {
  el.addEventListener('mousedown', (e) => {
    selectEl(el.id);
    startDrag(e, el);
  });
  el.addEventListener('touchstart', (e) => {
    selectEl(el.id);
    startDragTouch(e, el);
  }, { passive: false });
});

// Layer click to select
layerItems.forEach(item => {
  item.addEventListener('click', () => selectEl(item.dataset.target));
});

// ---- Drag Logic (Mouse) ----
function startDrag(e, el) {
  e.preventDefault();
  isDragging = true;
  dragEl = el;
  startX = e.clientX;
  startY = e.clientY;
  const rect = el.getBoundingClientRect();
  const canvasRect = canvas.getBoundingClientRect();
  elStartX = rect.left - canvasRect.left;
  elStartY = rect.top - canvasRect.top;
  el.style.transition = 'none';
}

document.addEventListener('mousemove', (e) => {
  if (!isDragging || !dragEl) return;
  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
  const newX = Math.max(0, elStartX + dx);
  const newY = Math.max(0, elStartY + dy);
  dragEl.style.left = newX + 'px';
  dragEl.style.top = newY + 'px';
});

document.addEventListener('mouseup', () => {
  if (dragEl) dragEl.style.transition = '';
  isDragging = false;
  dragEl = null;
});

// ---- Drag Logic (Touch) ----
function startDragTouch(e, el) {
  e.preventDefault();
  const touch = e.touches[0];
  isDragging = true;
  dragEl = el;
  startX = touch.clientX;
  startY = touch.clientY;
  const rect = el.getBoundingClientRect();
  const canvasRect = canvas.getBoundingClientRect();
  elStartX = rect.left - canvasRect.left;
  elStartY = rect.top - canvasRect.top;
  el.style.transition = 'none';
}

document.addEventListener('touchmove', (e) => {
  if (!isDragging || !dragEl) return;
  const touch = e.touches[0];
  const dx = touch.clientX - startX;
  const dy = touch.clientY - startY;
  const newX = Math.max(0, elStartX + dx);
  const newY = Math.max(0, elStartY + dy);
  dragEl.style.left = newX + 'px';
  dragEl.style.top = newY + 'px';
}, { passive: true });

document.addEventListener('touchend', () => {
  if (dragEl) dragEl.style.transition = '';
  isDragging = false;
  dragEl = null;
});

// ---- Creativity Slider ----
const slider = document.getElementById('creativity-slider');
slider.addEventListener('input', () => {
  const val = slider.value / 100;
  applyCreativity(val);
});

function applyCreativity(val) {
  const elements = document.querySelectorAll('.canvas-element');
  elements.forEach((el, i) => {
    const hue = Math.round(val * 360 + i * 60) % 360;
    const sat = Math.round(60 + val * 40);
    const rotDeg = (val * 20 - 10) * (i % 2 === 0 ? 1 : -1);
    const scale = 1 + val * 0.08;
    if (el.id !== 'c-text-1') {
      el.style.filter = `hue-rotate(${hue * val}deg) saturate(${sat}%)`;
      el.style.transform = `rotate(${rotDeg}deg) scale(${scale})`;
    }
    el.style.borderRadius = `${Math.round(val * 50)}px`;
  });
  // Also shift canvas grid colour
  canvas.style.backgroundImage = `radial-gradient(circle, hsla(${Math.round(val * 300)},70%,60%,0.08) 1px, transparent 1px)`;
}

// ---- Toolbar tool buttons ----
const toolBtns = document.querySelectorAll('.figma-tool-btn');
toolBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    toolBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

// ---- Add Shape Buttons ----
let shapeCount = 0;
const colors = [
  'linear-gradient(135deg,#8b5cf6,#22d3ee)',
  'linear-gradient(135deg,#f472b6,#fbbf24)',
  'linear-gradient(135deg,#34d399,#22d3ee)',
  'rgba(139,92,246,0.3)',
  'rgba(244,114,182,0.3)',
];

document.getElementById('add-rect-btn').addEventListener('click', () => addShape('rect'));
document.getElementById('add-circle-btn').addEventListener('click', () => addShape('circle'));
document.getElementById('add-text-btn').addEventListener('click', () => addShape('text'));

function addShape(type) {
  shapeCount++;
  const id = `custom-${type}-${shapeCount}`;
  const el = document.createElement('div');
  el.classList.add('canvas-element');
  el.id = id;
  el.dataset.id = id;
  const col = colors[shapeCount % colors.length];
  const canvasRect = canvas.getBoundingClientRect();
  const x = Math.max(20, Math.random() * (canvasRect.width - 160));
  const y = Math.max(20, Math.random() * (canvasRect.height - 80));
  el.style.left = x + 'px';
  el.style.top = y + 'px';
  el.style.position = 'absolute';
  el.style.cursor = 'move';

  if (type === 'rect') {
    el.style.width = '120px';
    el.style.height = '70px';
    el.style.background = col;
    el.style.borderRadius = '8px';
    elementProps[id] = { size: '120 × 70', radius: '8', opacity: '100%' };
  } else if (type === 'circle') {
    el.style.width = '70px';
    el.style.height = '70px';
    el.style.background = col;
    el.style.borderRadius = '50%';
    elementProps[id] = { size: '70 × 70', radius: '50%', opacity: '100%' };
  } else {
    el.style.background = 'none';
    el.style.color = '#e2e8f0';
    el.style.fontFamily = 'Outfit, sans-serif';
    el.style.fontWeight = '700';
    el.style.fontSize = '14px';
    el.style.whiteSpace = 'nowrap';
    el.textContent = 'New Text ✦';
    elementProps[id] = { size: 'Auto', radius: '0', opacity: '100%' };
  }

  canvas.appendChild(el);

  // Add to layers
  const layersList = document.getElementById('layers-list');
  const layerItem = document.createElement('div');
  layerItem.classList.add('layer-item');
  layerItem.dataset.target = id;
  const icon = type === 'rect' ? '▭' : type === 'circle' ? '◯' : 'T';
  layerItem.innerHTML = `<span class="layer-icon">${icon}</span> ${type.charAt(0).toUpperCase() + type.slice(1)} ${shapeCount}`;
  layerItem.addEventListener('click', () => selectEl(id));
  layersList.appendChild(layerItem);

  // Bind drag
  el.addEventListener('mousedown', (e) => {
    selectEl(id);
    startDrag(e, el);
  });
  el.addEventListener('touchstart', (e) => {
    selectEl(id);
    startDragTouch(e, el);
  }, { passive: false });

  selectEl(id);

  // Re-apply creativity level
  const val = slider.value / 100;
  if (val > 0) applyCreativity(val);
}

/* ---- Initial state ---- */
selectEl('c-rect-1');
