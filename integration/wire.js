/**
 * SportsLab ↔ AI Highlight Detector bridge.
 * Loaded after app.js; intercepts Generate/Download via capture phase
 * so the original mock handlers never run. Does not modify app.js.
 */
(function () {
  'use strict';

  const views = {
    landing: document.getElementById('view-landing'),
    upload: document.getElementById('view-upload'),
    result: document.getElementById('view-result'),
  };

  let highlightDownloadUrl = null;

  function getSport() {
    const app = document.getElementById('app');
    return app && app.classList.contains('sport-football') ? 'football' : 'cricket';
  }

  function isHttpUrl(value) {
    return /^https?:\/\//i.test((value || '').trim());
  }

  function showView(name) {
    Object.entries(views).forEach(([key, el]) => {
      if (!el) return;
      const isActive = key === name;
      el.classList.toggle('view-active', isActive);
      el.setAttribute('aria-hidden', !isActive);
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

  function setLoading(visible, message) {
    const overlay = document.getElementById('loading-overlay');
    if (!overlay) return;
    overlay.hidden = !visible;
    const text = overlay.querySelector('.loading-text');
    if (text && message) text.textContent = message;
  }

  function showError(message) {
    setLoading(false);
    window.alert(message);
  }

  async function onGenerate(event) {
    event.preventDefault();
    event.stopImmediatePropagation();

    const videoUrlInput = document.getElementById('video-url');
    const fileInput = document.getElementById('file-input');
    const url = videoUrlInput?.value?.trim() || '';
    const file = fileInput?.files?.[0] || null;

    if (!url && !file) {
      videoUrlInput?.focus();
      videoUrlInput?.classList.add('shake');
      setTimeout(() => videoUrlInput?.classList.remove('shake'), 500);
      return;
    }

    const formData = new FormData();
    formData.append('sport', getSport());

    if (file && !isHttpUrl(url)) {
      formData.append('source_mode', 'file');
      formData.append('video', file);
    } else if (isHttpUrl(url)) {
      formData.append('source_mode', 'url');
      formData.append('video_url', url);
    } else if (file) {
      formData.append('source_mode', 'file');
      formData.append('video', file);
    } else {
      showError('Please upload a video file or paste a valid http(s) URL.');
      return;
    }

    setLoading(true, 'Analyzing match footage…');

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Highlight generation failed. Please try again.');
      }

      highlightDownloadUrl = data.output_url;

      const videoUrlResult = document.getElementById('video-url-result');
      if (videoUrlResult) videoUrlResult.value = url || file.name;

      const resultVideo = document.getElementById('result-video');
      const resultPlaceholder = document.getElementById('result-placeholder');

      if (resultVideo && data.output_url) {
        resultVideo.src = data.output_url;
        resultVideo.hidden = false;
        if (resultPlaceholder) resultPlaceholder.hidden = true;
      }

      setLoading(false);
      navigateTo('result');
    } catch (err) {
      showError(err.message || 'Something went wrong while generating highlights.');
    }
  }

  function onDownload(event) {
    if (!highlightDownloadUrl) return;

    event.preventDefault();
    event.stopImmediatePropagation();

    const a = document.createElement('a');
    a.href = highlightDownloadUrl;
    a.download = `sportslab-highlight-${getSport()}.mp4`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  const generateBtn = document.getElementById('btn-generate');
  const downloadBtn = document.getElementById('btn-download');

  if (generateBtn) {
    generateBtn.addEventListener('click', onGenerate, true);
  }

  if (downloadBtn) {
    downloadBtn.addEventListener('click', onDownload, true);
  }
})();
