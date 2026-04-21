// ═══════════════════════════════════════════════
// SISTEMA180 — UGC Avatar Hub — Main Router
// ═══════════════════════════════════════════════
import { renderSidebar, initMobileMenu } from './components/sidebar.js';
import { renderDashboard } from './pages/dashboard.js';
import { renderAvatars } from './pages/avatars.js';
import { renderScripts } from './pages/scripts.js';
import { renderEditor } from './pages/editor.js';
import { renderVideos } from './pages/videos.js';
import { renderAds } from './pages/ads.js';
import { renderSettings } from './pages/settings.js';
import { renderLegal } from './pages/legal.js';
import { renderCrm } from './pages/crm.js';
import { renderClients } from './pages/clients.js';
import { renderFinances } from './pages/finances.js';
import { renderAffiliates } from './pages/affiliates.js';
import { renderMarketplace } from './pages/marketplace.js';
import { renderAgents } from './pages/agents.js';
import { renderDespacho } from './pages/despacho.js';
import './styles/index.css';

const routes = {
    dashboard: renderDashboard,
    avatars: renderAvatars,
    scripts: renderScripts,
    editor: renderEditor,
    videos: renderVideos,
    ads: renderAds,
    settings: renderSettings,
    legal: renderLegal,
    crm: renderCrm,
    clients: renderClients,
    finances: renderFinances,
    affiliates: renderAffiliates,
    marketplace: renderMarketplace,
    agents: renderAgents,
    despacho: renderDespacho,
};

let currentPage = 'dashboard';

export function navigate(page) {
    currentPage = page;
    const content = document.getElementById('content');
    const render = routes[page];
    if (render) {
        content.innerHTML = '';
        content.className = 'fade-in';
        render(content);
    }
    // Update active nav
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.page === page);
    });
    // Reset animation
    void content.offsetWidth;
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    renderSidebar(document.getElementById('sidebar'));
    initMobileMenu();
    navigate('dashboard');
});
