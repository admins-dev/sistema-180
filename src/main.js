/** UGC Avatar Hub — Main Application Router & Bootstrap */

import { renderDashboard } from './pages/dashboard.js';
import { renderScripts, initScripts } from './pages/scripts.js';
import { renderAvatars, initAvatars } from './pages/avatars.js';
import { renderVideos, initVideos } from './pages/videos.js';
import { renderAds, initAds } from './pages/ads.js';
import { renderSettings, initSettings } from './pages/settings.js';
import { freepikAPI } from './services/freepik-api.js';

// --- Page Registry ---
const pages = {
  dashboard: { render: renderDashboard, init: null },
  scripts: { render: renderScripts, init: initScripts },
  avatars: { render: renderAvatars, init: initAvatars },
  videos: { render: renderVideos, init: initVideos },
  ads: { render: renderAds, init: initAds },
  settings: { render: renderSettings, init: initSettings },
};

let currentPage = 'dashboard';

// --- Router ---
function navigate(pageName) {
  const page = pages[pageName];
  if (!page) return;

  currentPage = pageName;

  // Render page
  const container = document.getElementById('page-container');
  container.innerHTML = page.render();

  // Re-animate
  container.style.animation = 'none';
  container.offsetHeight; // trigger reflow
  container.style.animation = 'fadeIn 300ms ease';

  // Init page-specific handlers
  if (page.init) {
    setTimeout(() => page.init(), 50);
  }

  // Update sidebar active state
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.page === pageName);
  });

  // Update URL hash
  window.location.hash = pageName;

  // Scroll to top
  document.getElementById('main-content').scrollTo(0, 0);
}

// --- Toast Notifications ---
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOutToast 300ms ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// --- Update API Status ---
function updateApiStatus() {
  const statusDot = document.querySelector('.status-dot');
  const statusText = document.querySelector('.status-text');
  const isConfigured = freepikAPI.isConfigured();

  if (statusDot) {
    statusDot.classList.toggle('connected', isConfigured);
  }
  if (statusText) {
    statusText.textContent = isConfigured ? 'Freepik API ✓' : 'API sin configurar';
  }
}

// --- Global helpers (accessible from pages) ---
window.__navigate = navigate;
window.__showToast = showToast;
window.__updateApiStatus = updateApiStatus;

// --- Event Listeners ---
function initApp() {
  // Sidebar navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      navigate(item.dataset.page);
    });
  });

  // Handle page links inside content (data-page attribute)
  document.addEventListener('click', (e) => {
    const link = e.target.closest('[data-page]');
    if (link && !link.classList.contains('nav-item')) {
      e.preventDefault();
      navigate(link.dataset.page);
    }
  });

  // Hash-based routing
  const hash = window.location.hash.slice(1);
  const startPage = pages[hash] ? hash : 'dashboard';

  // If no API key configured, redirect to settings on first visit
  if (!freepikAPI.isConfigured() && !hash) {
    navigate('dashboard'); // Show dashboard with onboarding banner
  } else {
    navigate(startPage);
  }

  // Update API status indicator
  updateApiStatus();

  // Handle hash changes
  window.addEventListener('hashchange', () => {
    const newPage = window.location.hash.slice(1);
    if (pages[newPage] && newPage !== currentPage) {
      navigate(newPage);
    }
  });
}

// --- Start ---
document.addEventListener('DOMContentLoaded', initApp);
// Also init immediately if DOM is already ready
if (document.readyState !== 'loading') {
  initApp();
}
