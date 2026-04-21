export function renderEditor(container) {
    container.innerHTML = `
    <!-- TAB: VIDEO EDITOR (CAPCUT/PREMIERE CLONE) -->
    <div style="padding:0">
        <div class="page-header" style="margin-bottom: 16px;">
            <h2 style="font-size: 28px; font-weight: 800; display:flex; align-items:center; gap:8px;">
                <span style="font-size:24px;">✂️</span> Editor IA <span style="background:linear-gradient(135deg, #8b5cf6, #ec4899); -webkit-background-clip: text; color: transparent;">Pro</span>
            </h2>
            <p style="color:var(--text-secondary);">Motor de Edición Automático — Caput Pro Killer + After Effects Preset</p>
        </div>

        <div class="editor-layout" style="display:flex; height:calc(100vh - 180px); gap:16px; flex-direction:column;">
            
            <div style="display:flex; flex:1; gap:16px; min-height:0;">
                <!-- Left Panel: After Effects / Tools -->
                <div class="panel editor-sidebar" style="width:300px; background:var(--bg-card); overflow-y:auto; border:1px solid var(--border); padding:16px; border-radius:var(--radius-sm);">
                    <h3 style="font-size:14px; margin-bottom:12px; color:var(--text-secondary);">✨ Efectos (After Effects)</h3>
                    <div class="vfx-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                        <button class="vfx-btn active" style="background:rgba(139,92,246,.2);border:1px solid var(--accent);border-radius:6px;padding:12px 8px;cursor:pointer;"><div style="font-size:20px;">✂️</div><div style="font-size:11px;font-weight:700;color:#fff;">Corte IA Mágico</div></button>
                        <button class="vfx-btn" style="background:var(--bg-card);border:1px solid var(--border);border-radius:6px;padding:12px 8px;cursor:pointer;"><div style="font-size:20px;">🔍</div><div style="font-size:11px;font-weight:700;color:var(--text-secondary);">Smart Zoom</div></button>
                        <button class="vfx-btn" style="background:var(--bg-card);border:1px solid var(--border);border-radius:6px;padding:12px 8px;cursor:pointer;"><div style="font-size:20px;">📹</div><div style="font-size:11px;font-weight:700;color:var(--text-secondary);">Estabilizar</div></button>
                        <button class="vfx-btn" style="background:var(--bg-card);border:1px solid var(--border);border-radius:6px;padding:12px 8px;cursor:pointer;"><div style="font-size:20px;">🎨</div><div style="font-size:11px;font-weight:700;color:var(--text-secondary);">Color Grade Pro</div></button>
                    </div>
                    
                    <h3 style="margin-top:24px; font-size:14px; margin-bottom:12px; color:var(--text-secondary);">💬 Subtítulos (Estilos)</h3>
                    <div class="subs-grid" style="display:flex; flex-direction:column; gap:8px;">
                        <button class="sub-btn active" style="background:rgba(245,158,11,.1);border:1px solid var(--orange);border-radius:6px;padding:12px;cursor:pointer;text-align:center;"><span style="font-weight:900; color:#f59e0b; text-transform:uppercase; text-shadow:2px 2px 0px black;">Hormozi (XL)</span></button>
                        <button class="sub-btn" style="background:var(--bg-card);border:1px solid var(--border);border-radius:6px;padding:12px;cursor:pointer;text-align:center;"><span style="font-weight:800; color:#3b82f6; border-bottom:3px solid cyan;">MrBeast (Pops)</span></button>
                        <button class="sub-btn" style="background:var(--bg-card);border:1px solid var(--border);border-radius:6px;padding:12px;cursor:pointer;text-align:center;"><span style="font-family:serif; font-style:italic; border-left:2px solid gray; padding-left:4px;color:var(--text-primary);">Cinematic (Clean)</span></button>
                    </div>
                </div>

                <!-- Middle: Player -->
                <div class="editor-main" style="flex-grow:1; display:flex; flex-direction:column; background:#000; border-radius:var(--radius-sm); border:1px solid var(--border); overflow:hidden; position:relative;">
                    <div class="editor-header" style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:rgba(255,255,255,0.05);border-bottom:1px solid rgba(255,255,255,0.1);">
                        <div class="editor-actions" style="display:flex;gap:8px;">
                            <button id="editor-btn-upload" class="btn btn-secondary">📁 Subir Bruto</button>
                            <input type="file" id="video-upload" hidden accept="video/mp4,video/mov">
                            <button id="editor-btn-jarvis" class="btn" style="background:linear-gradient(135deg, #10b981, #059669);color:#fff;">🤖 MODO JARVIS (Auto-Pilot)</button>
                        </div>
                        <button class="btn btn-primary" onclick="alert('Exportando a 4K 60fps...')">🎬 Exportar 4K</button>
                    </div>
                    <div class="player-container" style="flex-grow:1;position:relative;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle, #2a2a2a 0%, #000 100%);">
                        <video id="editor-video" muted controls poster="https://i.imgur.com/8Q5c64k.png" style="max-height:100%;max-width:100%;object-fit:contain;"></video>
                        <div class="player-subs" id="player-subs" style="display:none; position:absolute; bottom:20%; text-align:center; width:100%; font-size:32px; font-weight:900; color:#f59e0b; text-shadow:2px 2px 0px #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; text-transform:uppercase; z-index:5; pointer-events:none;">ESCRIBE UN TEXTO...</div>
                        
                        <div class="player-controls-overlay" id="jarvis-editing-overlay" style="display:none;position:absolute;inset:0;background:rgba(0,0,0,0.8);backdrop-filter:blur(4px);flex-direction:column;align-items:center;justify-content:center;z-index:10;">
                            <div class="jarvis-eye" style="width:60px;height:60px;border-radius:50%;background:radial-gradient(circle, #f59e0b 0%, transparent 70%);box-shadow:0 0 30px #f59e0b, inset 0 0 20px #ef4444;margin-bottom:16px;"></div>
                            <span style="font-weight:800;color:#fff;">JARVIS ANALIZANDO CORTES...</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bottom: Premiere Timeline -->
            <div class="timeline-panel" style="height:220px; background:#111; border:1px solid var(--border); border-radius:var(--radius-sm); display:flex; flex-direction:column;flex-shrink:0;">
                <div class="timeline-header" style="padding:8px 16px; background:#222; border-bottom:1px solid #333; display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="font-size:12px;color:var(--text-secondary);">⏱️ Línea de Tiempo (Premiere Pro Mode)</h3>
                    <div style="font-family:monospace;font-size:12px;color:var(--text-muted);">Espacio de Trabajo: VideoForge <span style="color:var(--accent);font-weight:700;margin-left:12px;">00:00:00:00</span></div>
                </div>
                <div class="tracks-container" style="flex-grow:1; overflow-y:auto; overflow-x:hidden; position:relative; background:#181818; padding-top:20px;">
                    <div class="track-playhead" id="playhead" style="position:absolute;top:0;bottom:0;width:2px;background:#ef4444;z-index:10;left:5%;"></div>
                    <style>
                        .track { display:flex; height:40px; border-bottom:1px solid #2a2a2a; }
                        .track-label { width:90px; background:#222; border-right:1px solid #333; display:flex; align-items:center; font-size:10px; padding-left:8px; color:var(--text-muted); flex-shrink:0;}
                        .track-content { flex-grow:1; position:relative; background:repeating-linear-gradient(90deg, transparent, transparent 49px, #2a2a2a 50px); }
                        .clip { position:absolute; height:32px; top:4px; border-radius:4px; border:1px solid rgba(255,255,255,.2); display:flex; align-items:center; padding:0 8px; font-size:10px; font-family:monospace; color:white; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; box-shadow:inset 0 0 10px rgba(0,0,0,.5); cursor:pointer;}
                        .clip.cut { border-left: 2px solid #ef4444 !important; border-radius:0; }
                    </style>
                    <div class="track">
                        <div class="track-label">V2 (FX/TXT)</div>
                        <div class="track-content">
                            <div class="clip" style="left:10%; width:20%; background:#8b5cf6;">Smart Zoom</div>
                            <div class="clip" style="left:5%; width:30%; background:#b45309;">Hormozi Subs</div>
                        </div>
                    </div>
                    <div class="track">
                        <div class="track-label">V1 (Vídeo)</div>
                        <div class="track-content" id="v1-track">
                            <div class="clip vid-clip" style="left:0%; width:35%; background:#1e3a8a;">Bruto_camara_1.mp4</div>
                            <div class="clip vid-clip" style="left:36%; width:40%; background:#1e3a8a;">Bruto_camara_1.mp4</div>
                            <div class="clip cut" style="left:35%; width:1%; background:#1e3a8a;">✂️</div>
                        </div>
                    </div>
                    <div class="track">
                        <div class="track-label">A1 (Audio)</div>
                        <div class="track-content">
                            <div class="clip" style="left:0%; width:35%; background:#065f46;">[Onda vocal]</div>
                            <div class="clip" style="left:36%; width:40%; background:#065f46;">[Onda vocal]</div>
                        </div>
                    </div>
                    <div class="track">
                        <div class="track-label">A2 (Música)</div>
                        <div class="track-content">
                            <div class="clip" style="left:0%; width:80%; background:#047857; opacity:0.8;">Phonk_BassBoosted.mp3</div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
    `;

    // Interaction Setup
    const btnUpload = container.querySelector('#editor-btn-upload');
    const btnJarvis = container.querySelector('#editor-btn-jarvis');
    const fileInput = container.querySelector('#video-upload');
    const overlay = container.querySelector('#jarvis-editing-overlay');
    const subs = container.querySelector('#player-subs');
    const playhead = container.querySelector('#playhead');

    btnUpload.addEventListener('click', () => fileInput.click());

    btnJarvis.addEventListener('click', () => {
        if (!overlay || !subs || !playhead) return;
        overlay.style.display = 'flex';
        
        let p = 5;
        const iv = setInterval(() => {
            p += 2;
            playhead.style.left = `${p}%`;
            if (p > 90) {
                clearInterval(iv);
                overlay.style.display = 'none';
                
                subs.style.display = 'block';
                const phrases = ["ESTA ES LA ÚNICA", "ESTRATEGIA", "QUE NECESITAS", "PARA FACTURAR", "10K AL MES"];
                let i = 0;
                const subsIv = setInterval(() => {
                    if(!container.isConnected) { clearInterval(subsIv); return; } // cleanup
                    subs.textContent = phrases[i];
                    i = (i + 1) % phrases.length;
                }, 800);
                
                container.querySelectorAll('.vid-clip').forEach(v => v.style.borderColor = '#10b981');
            }
        }, 100);
    });
}
