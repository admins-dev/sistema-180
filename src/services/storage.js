// ═══════════════════════════════════════════════
// Storage Service — LocalStorage wrapper
// ═══════════════════════════════════════════════

const PREFIX = 's180_';

export const storage = {
    get(key) {
        try { return JSON.parse(localStorage.getItem(PREFIX + key)); }
        catch { return null; }
    },
    set(key, val) { localStorage.setItem(PREFIX + key, JSON.stringify(val)); },
    remove(key) { localStorage.removeItem(PREFIX + key); },

    // API Keys — fallback to env vars (VITE_*), never hardcoded
    getFreepikKey() { return this.get('freepik_key') || ''; },
    setFreepikKey(k) { this.set('freepik_key', k); },
    getGeminiKey() { return this.get('gemini_key') || import.meta.env.VITE_GEMINI_KEY || ''; },
    setGeminiKey(k) { this.set('gemini_key', k); },
    getGeminiKey2() { return this.get('gemini_key_2') || import.meta.env.VITE_GEMINI_KEY_2 || ''; },
    setGeminiKey2(k) { this.set('gemini_key_2', k); },
    getPerplexityKey() { return this.get('perplexity_key') || import.meta.env.VITE_PERPLEXITY_KEY || ''; },
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
