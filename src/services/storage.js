// ═══════════════════════════════════════════════
// Storage Service — LocalStorage wrapper
// ═══════════════════════════════════════════════

const PREFIX = 's180_';

// Default API keys (pre-injected for SISTEMA180)
const DEFAULTS = {
    gemini_key: 'AIzaSyBI2JBDqXC2GQpVGGiBl4yfO-h8HZkHf0w',
    perplexity_key: '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',
    freepik_key: 'FPSX03c8141aa0eb554cc75376208f194af4',
};

export const storage = {
    get(key) {
        try { return JSON.parse(localStorage.getItem(PREFIX + key)); }
        catch { return null; }
    },
    set(key, val) { localStorage.setItem(PREFIX + key, JSON.stringify(val)); },
    remove(key) { localStorage.removeItem(PREFIX + key); },

    // API Keys
    getFreepikKey() { return this.get('freepik_key') || DEFAULTS.freepik_key; },
    setFreepikKey(k) { this.set('freepik_key', k); },
    getGeminiKey() { return this.get('gemini_key') || DEFAULTS.gemini_key; },
    setGeminiKey(k) { this.set('gemini_key', k); },
    getPerplexityKey() { return this.get('perplexity_key') || DEFAULTS.perplexity_key; },
    setPerplexityKey(k) { this.set('perplexity_key', k); },

    // Avatars library
    getAvatars() { return this.get('avatars') || []; },
    addAvatar(avatar) {
        const list = this.getAvatars();
        list.unshift({ ...avatar, id: Date.now(), createdAt: new Date().toISOString() });
        this.set('avatars', list);
    },

    // Scripts library
    getScripts() { return this.get('scripts') || []; },
    addScript(script) {
        const list = this.getScripts();
        list.unshift({ ...script, id: Date.now(), createdAt: new Date().toISOString() });
        this.set('scripts', list);
    },

    // Stats
    getStats() {
        return {
            avatars: this.getAvatars().length,
            scripts: this.getScripts().length,
            videos: (this.get('videos') || []).length,
            ads: (this.get('ads') || []).length,
        };
    }
};
