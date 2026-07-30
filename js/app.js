(function () {
  'use strict';

  const app = document.getElementById('app');
  const views = {
    landing: document.getElementById('view-landing'),
    upload: document.getElementById('view-upload'),
    result: document.getElementById('view-result'),
  };

  const state = {
    sport: 'cricket',
    videoUrl: '',
    videoFile: null,
  };

  const DESCRIPTIONS = {
    cricket:
      'Analyze your cricket match with the power of Artificial Intelligence. Upload a cricket match video, and our AI-based analyzer automatically detects key match events by examining player actions, crowd reactions, commentary intensity, scene transitions, and audio spikes. The system identifies exciting moments such as boundaries, sixes, wickets, catches, run-outs, and match-winning plays, then combines them into a concise highlight reel.',
    football:
      'Analyze your football match with the power of Artificial Intelligence. Upload a football match video, and our AI-based analyzer automatically detects key match events by examining player actions, crowd reactions, commentary intensity, scene transitions, and audio spikes. The system identifies exciting moments such as goals, assists, saves, tackles, free kicks, penalties, and match-winning plays, then combines them into a concise highlight reel.',
  };

  /* ---- Sport switching ---- */
  function setSport(sport) {
    if (sport !== 'cricket' && sport !== 'football') return;
    state.sport = sport;

    app.classList.remove('sport-cricket', 'sport-football');
    app.classList.add(`sport-${sport}`);

    document.querySelectorAll('.sport-icon').forEach((btn) => {
      const isActive = btn.dataset.sport === sport;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive);
    });

    document.querySelectorAll('.hero-ball').forEach((ball) => {
      ball.classList.toggle('active', ball.classList.contains(`hero-ball--${sport}`));
    });

    const heroLabel = document.getElementById('hero-sport-label');
    if (heroLabel) {
      const labelText = sport === 'cricket' ? 'CRICKET' : 'FOOTBALL';
      if (heroLabel.textContent !== labelText) {
        heroLabel.style.opacity = '0';
        setTimeout(() => {
          heroLabel.textContent = labelText;
          heroLabel.style.opacity = '1';
        }, 200);
      } else {
        heroLabel.textContent = labelText;
        heroLabel.style.opacity = '1';
      }
    }

    const descEl = document.getElementById('upload-description');
    if (descEl) {
      descEl.style.opacity = '0';
      setTimeout(() => {
        descEl.textContent = DESCRIPTIONS[sport];
        descEl.style.opacity = '1';
      }, 200);
    }

    const placeholderIcon = document.getElementById('result-placeholder-icon');
    if (placeholderIcon) {
      placeholderIcon.src = sport === 'cricket' ? 'assets/cricket-ball.png' : 'assets/football.png';
    }
  }

  document.querySelectorAll('.sport-icon').forEach((btn) => {
    btn.addEventListener('click', () => setSport(btn.dataset.sport));
  });

  /* ---- View navigation ---- */
  function showView(name) {
    Object.entries(views).forEach(([key, el]) => {
      if (!el) return;
      const isActive = key === name;
      el.classList.toggle('view-active', isActive);
      el.setAttribute('aria-hidden', !isActive);
      if (!isActive) el.classList.remove('view-exit');
    });
  }

  function navigateTo(name) {
    const current = Object.entries(views).find(([, el]) => el?.classList.contains('view-active'));
    if (current && current[0] !== name) {
      current[1].classList.add('view-exit');
      setTimeout(() => {
        current[1].classList.remove('view-exit');
        showView(name);
      }, 300);
    } else {
      showView(name);
    }
  }

  /* ---- Get Started ---- */
  document.getElementById('btn-get-started')?.addEventListener('click', () => {
    navigateTo('upload');
  });

  /* ---- Logo home links ---- */
  document.getElementById('logo-home')?.addEventListener('click', (e) => {
    e.preventDefault();
    navigateTo('landing');
  });

  document.getElementById('logo-home-result')?.addEventListener('click', (e) => {
    e.preventDefault();
    navigateTo('landing');
  });

  /* ---- File upload handling ---- */
  function handleFileSelect(file, urlInput) {
    if (!file) return;
    state.videoFile = file;
    state.videoUrl = file.name;
    if (urlInput) urlInput.value = file.name;
  }

  const fileInput = document.getElementById('file-input');
  const fileInputResult = document.getElementById('file-input-result');
  const videoUrlInput = document.getElementById('video-url');
  const videoUrlResult = document.getElementById('video-url-result');

  fileInput?.addEventListener('change', (e) => {
    handleFileSelect(e.target.files[0], videoUrlInput);
  });

  fileInputResult?.addEventListener('change', (e) => {
    handleFileSelect(e.target.files[0], videoUrlResult);
    if (videoUrlInput) videoUrlInput.value = state.videoUrl;
  });

  videoUrlInput?.addEventListener('input', (e) => {
    state.videoUrl = e.target.value;
    state.videoFile = null;
  });

  /* ---- Generate ---- */
  const loadingOverlay = document.getElementById('loading-overlay');
  const resultVideo = document.getElementById('result-video');
  const resultPlaceholder = document.getElementById('result-placeholder');

  document.getElementById('btn-generate')?.addEventListener('click', () => {
    const url = videoUrlInput?.value?.trim();
    if (!url && !state.videoFile) {
      videoUrlInput?.focus();
      videoUrlInput?.classList.add('shake');
      setTimeout(() => videoUrlInput?.classList.remove('shake'), 500);
      return;
    }

    if (url) state.videoUrl = url;

    loadingOverlay.hidden = false;

    setTimeout(() => {
      loadingOverlay.hidden = true;

      if (videoUrlResult) videoUrlResult.value = state.videoUrl;

      if (state.videoFile) {
        const objectUrl = URL.createObjectURL(state.videoFile);
        if (resultVideo) {
          resultVideo.src = objectUrl;
          resultVideo.hidden = false;
          if (resultPlaceholder) resultPlaceholder.hidden = true;
        }
      } else {
        if (resultVideo) resultVideo.hidden = true;
        if (resultPlaceholder) resultPlaceholder.hidden = false;
      }

      navigateTo('result');
    }, 2200);
  });

  /* ---- Download ---- */
  document.getElementById('btn-download')?.addEventListener('click', () => {
    if (state.videoFile && resultVideo?.src) {
      const a = document.createElement('a');
      a.href = resultVideo.src;
      a.download = `sportslab-highlight-${state.sport}.mp4`;
      a.click();
    } else {
      const blob = new Blob(
        [`SportsLab AI Highlight Reel\nSport: ${state.sport}\nSource: ${state.videoUrl}\nGenerated successfully.`],
        { type: 'text/plain' }
      );
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `sportslab-highlight-${state.sport}.txt`;
      a.click();
      URL.revokeObjectURL(a.href);
    }
  });

  /* ---- Canvas scale (reliable in all browsers / embedded previews) ---- */
  const DESIGN_W = 1440;
  const DESIGN_H = 1024;

  function updateCanvasScale() {
    const w = window.innerWidth || document.documentElement.clientWidth || DESIGN_W;
    const h = window.innerHeight || document.documentElement.clientHeight || DESIGN_H;
    const scale = Math.min(w / DESIGN_W, h / DESIGN_H);
    document.documentElement.style.setProperty('--ui-scale', String(scale));
  }

  window.addEventListener('resize', updateCanvasScale);
  window.addEventListener('orientationchange', updateCanvasScale);
  updateCanvasScale();
  requestAnimationFrame(updateCanvasScale);

  /* ---- Init ---- */
  setSport('cricket');
})();
