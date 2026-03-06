/** Storage service — manages local data for projects, avatars, scripts */

const KEYS = {
    AVATARS: 'ugc_hub_avatars',
    SCRIPTS: 'ugc_hub_scripts',
    VIDEOS: 'ugc_hub_videos',
    PROJECTS: 'ugc_hub_projects',
    SETTINGS: 'ugc_hub_settings',
};

function load(key) {
    try {
        return JSON.parse(localStorage.getItem(key)) || [];
    } catch {
        return [];
    }
}

function save(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

// --- Avatars ---
export function getAvatars() {
    return load(KEYS.AVATARS);
}

export function saveAvatar(avatar) {
    const avatars = load(KEYS.AVATARS);
    avatar.id = avatar.id || generateId();
    avatar.createdAt = avatar.createdAt || new Date().toISOString();
    avatars.unshift(avatar);
    save(KEYS.AVATARS, avatars);
    return avatar;
}

export function deleteAvatar(id) {
    const avatars = load(KEYS.AVATARS).filter(a => a.id !== id);
    save(KEYS.AVATARS, avatars);
}

// --- Scripts ---
export function getScripts() {
    return load(KEYS.SCRIPTS);
}

export function saveScript(script) {
    const scripts = load(KEYS.SCRIPTS);
    script.id = script.id || generateId();
    script.createdAt = script.createdAt || new Date().toISOString();
    scripts.unshift(script);
    save(KEYS.SCRIPTS, scripts);
    return script;
}

export function deleteScript(id) {
    const scripts = load(KEYS.SCRIPTS).filter(s => s.id !== id);
    save(KEYS.SCRIPTS, scripts);
}

// --- Videos ---
export function getVideos() {
    return load(KEYS.VIDEOS);
}

export function saveVideo(video) {
    const videos = load(KEYS.VIDEOS);
    video.id = video.id || generateId();
    video.createdAt = video.createdAt || new Date().toISOString();
    videos.unshift(video);
    save(KEYS.VIDEOS, videos);
    return video;
}

export function deleteVideo(id) {
    const videos = load(KEYS.VIDEOS).filter(v => v.id !== id);
    save(KEYS.VIDEOS, videos);
}

// --- Settings ---
export function getSettings() {
    try {
        return JSON.parse(localStorage.getItem(KEYS.SETTINGS)) || {};
    } catch {
        return {};
    }
}

export function saveSettings(settings) {
    const current = getSettings();
    const merged = { ...current, ...settings };
    localStorage.setItem(KEYS.SETTINGS, JSON.stringify(merged));
    return merged;
}

// --- Stats ---
export function getStats() {
    return {
        totalAvatars: getAvatars().length,
        totalScripts: getScripts().length,
        totalVideos: getVideos().length,
    };
}
