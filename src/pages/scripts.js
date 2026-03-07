// ═══════════════════════════════════════════════
// Scripts Page — Método Heras + UMV + SDD + Formatos
// ═══════════════════════════════════════════════
import { generateScript, getHookTypes, getCtaTypes, getNichos, getSddPillars, getFormatos } from '../services/script-engine.js';
import { storage } from '../services/storage.js';
import { aiCascade } from '../services/ai-cascade.js';

const PREDEFINED_SCRIPTS = [
  {
    id: 's1', title: '1. 3.000€ sin oficina (Dinero)',
    hook: '...facturar 3.000€ al mes sin salir de casa, ¿lo harías? En 6 meses pasé de 0€ a 3.000€/mes con 1 oferta + 1 avatar.',
    story: 'Hace 6 meses: 0 clientes. Hoy: 3.000€/mes. El problema real era que dependía al 100% del boca a boca. Cuando automatizamos la captación, todo cambió.',
    moraleja: 'Clave = 1 oferta simple + 1 hook que repitas + Ads TOFU que te den volumen. Case: cliente X, 4 ventas/semana.',
    cta: 'Sígueme y manda DM "INFO" para mi plantilla de oferta.',
    sddPillar: '💰 Dinero', formatoLabel: '🗣️ Talking Head', hookType: '🤔 Curiosidad', nicho: 'Marca Personal',
    umvNote: 'PROMPT HEYGEN: Avatar mirando a cámara. Overlay "3.000€/mes SIN OFICINA". Triple hook de sonido (whoosh) + zoom in.',
    avatarTip: 'Pose confiada, expresiones marcadas'
  },
  {
    id: 's2', title: '2. ¿Cansado a las 5pm? (Salud)',
    hook: '...a las 5pm te derrumbas? Si llegas hecho polvo después del almuerzo tienes que ver esto.',
    story: 'Micro-escena de trabajo y mal hábito (café, scroll). El problema es que tu ritmo circadiano está destrozado.',
    moraleja: 'Micro-hábito: 12/3 breathing + 10 min movimiento. Te da +30% de energía al día comprobado.',
    cta: 'Sígueme y DM "ENERGÍA" y te paso el protocolo 7 días.',
    sddPillar: '🏥 Salud', formatoLabel: '👁️ POV', hookType: '😰 Dolor', nicho: 'Productividad',
    umvNote: 'PROMPT HEYGEN: Avatar inclinado hacia delante, aspecto empático. Overlay: "¿Cansancio a 5pm?"',
    avatarTip: 'Mirando hacia abajo/pantalla'
  },
  {
    id: 's3', title: '3. Hacks millonarios (Desarrollo)',
    hook: '3 hacks que la gente millonaria usa para concentrarse y tú no.',
    story: 'Hack 1: Pomodoro 52/17. Hack 2: Cue + 2 min reset. Hack 3: Tiempo bloque 90 min sin interrupciones.',
    moraleja: 'No necesitas más motivación, necesitas sistemas a prueba de balas para no depender de la voluntad.',
    cta: 'Guarda este vídeo y DM "PROD" para mi sistema.',
    sddPillar: '🧠 Desarrollo Personal', formatoLabel: '📚 Tutorial Rápido', hookType: '🤔 Curiosidad', nicho: 'Productividad',
    umvNote: 'PROMPT HEYGEN: Usar Green Screen para que el avatar señale un temporizador Pomodoro.',
    avatarTip: 'Señalando con el dedo'
  },
  {
    id: 's4', title: '4. Mi cita acabó mal (Parejas)',
    hook: 'Mi cita terminó porque cometí el PEOR error de comunicación...',
    story: 'Hablar solo de uno mismo es el asesino silencioso de la atracción. Yo lo hice y la cita acabó en 20 minutos.',
    moraleja: '3 pasos para mejorar: 1) Escucha activa 70/30. 2) Haz preguntas abiertas. 3) Valida sus emociones.',
    cta: '¿Te pasó? DM "CITA" y te doy mi plantilla de conversación.',
    sddPillar: '❤️ Sexo/Parejas', formatoLabel: '📖 Storytime', hookType: '🤝 Relatable', nicho: 'Relaciones',
    umvNote: 'PROMPT HEYGEN: Avatar contando la historia con micro, cortes rápidos, música tensa que se relaja al final.',
    avatarTip: 'Hablando con gestos amplios, muy humano'
  },
  {
    id: 's5', title: '5. Seguidores ≠ Ventas (Dinero)',
    hook: 'No necesitas más seguidores para vender más. Los seguidores NO son ventas.',
    story: 'Veo cuentas con 100K seguidores facturando 0€, y cuentas con 2K seguidores facturando 10.000€/mes. La diferencia es el funnel.',
    moraleja: 'Proceso = 1 funnel + 1 oferta clara + Ads retargeting. Deja de buscar likes y busca conversiones.',
    cta: '¿Estancado? DM "VENTAS" si quieres copiar el funnel exacto que yo uso.',
    sddPillar: '💰 Dinero', formatoLabel: '🔄 Antes/Después', hookType: '⚡ Controversia', nicho: 'Marketing',
    umvNote: 'PROMPT HEYGEN: Split screen: Izquierda seguidores, derecha ventas. Tono seguro.',
    avatarTip: 'Brazos cruzados, actitud retadora'
  },
  {
    id: 's6', title: '6. Error nº1 en dietas (Salud)',
    hook: 'Cometes este error en todas las dietas y por eso recuperas el peso.',
    story: 'Omitir comidas o demonizar macronutrientes destruye tu metabolismo. El cerebro entra en modo ahorro de energía.',
    moraleja: '3 cambios sencillos: Prioriza proteína en el desayuno, no elimines carbohidratos (ponlos de noche), camina 8k pasos.',
    cta: 'Sígueme para la rutina de 7 días. Y manda DM "DIETA" GRATIS para el PDF.',
    sddPillar: '🏥 Salud', formatoLabel: '🗣️ Talking Head', hookType: '📚 Educativo', nicho: 'Fitness',
    umvNote: 'PROMPT HEYGEN: Voz didáctica y pausada. Overlay grande: "ERROR MORTAL DIETAS".',
    avatarTip: 'Señalando, explicativo'
  },
  {
    id: 's7', title: '7. +20% tiempo productivo (Desarrollo)',
    hook: 'Así es como gané +20% de tiempo productivo cada día trabajando MENOS.',
    story: 'Antes siempre estaba apagando fuegos. Cambié 3 cosas: (1) Tareas MIT primero. (2) Decir NO por defecto. (3) Descansos estratégicos obligatorios.',
    moraleja: 'El resultado fue liberar 2 horas al día mientras duplicaba resultados. Estar ocupado no es ser productivo.',
    cta: 'Manda DM "TIEMPO" para mi plantilla de Notion de organización.',
    sddPillar: '🧠 Desarrollo Personal', formatoLabel: '📚 Tutorial Rápido', hookType: '📈 Resultados', nicho: 'Productividad',
    umvNote: 'PROMPT HEYGEN: Energía alta, resultados reales en pantalla durante el vídeo.',
    avatarTip: 'Sonriente, motivado'
  },
  {
    id: 's8', title: '8. Rutina = 5 ventas/sem (Dinero)',
    hook: 'Esta rutina de contenidos exactamente igual me da 5 ventas por semana.',
    story: 'Se acabó postear por postear. Plan semanal: 7 posts verticales enganchando niveles TOFU/MOFU, y 1 vídeo largo a YouTube para fidelizar (BOFU).',
    moraleja: 'Todo el tráfico va al perfil gratuito de IG. Los DMs hacen la cualificación y cierre. Es una fábrica.',
    cta: 'Vete a mis Highlights en "OFERTA" para ver cómo lo monto por dentro.',
    sddPillar: '💰 Dinero', formatoLabel: '🟩 Green Screen', hookType: '🤔 Curiosidad', nicho: 'Marca Personal',
    umvNote: 'PROMPT HEYGEN: Avatar en Green Screen sobre un Excel de calendario de contenidos.',
    avatarTip: 'En la esquina señalando los días de la semana'
  },
  {
    id: 's9', title: '9. Avatar vende más (Dinero)',
    hook: 'Por esto un avatar de inteligencia artificial puede vender mucho mejor que tú.',
    story: 'Las 3 razones son matemáticas: (1) Consistencia 24/7 sin cansancio. (2) Multi-idioma instantáneo. (3) Permite A/B testing infinito sin que el ego se interponga.',
    moraleja: 'La gente conecta con el mensaje, no con quién lo emite, si el mensaje duele lo suficiente y aporta valor.',
    cta: '¿Quieres montar el tuyo? Manda DM "AVATAR" y te paso las herramientas.',
    sddPillar: '💰 Dinero', formatoLabel: '📋 Listicle', hookType: '📚 Educativo', nicho: 'Marketing IA',
    umvNote: 'PROMPT HEYGEN: Enumera con los dedos. Tono tecnológico.',
    avatarTip: 'Techy, natural, cortando el aire con la mano'
  },
  {
    id: 's10', title: '10. Challenge 48h Leads (Dinero)',
    hook: '48 horas para transformar tu perfil en una PUTA máquina de captar leads.',
    story: 'Día 1: Optimiza bio y 3 Highlights clave ("Info", "Demo", "Oferta"). Día 2: Pon en marcha el script autoresponder de Instagram.',
    moraleja: 'Tienes que dejar de usar IG como álbum de fotos y empezar a usarlo como Landing Page conversacional.',
    cta: 'Si estás listo manda DM "CHALLENGE" (solo quedan 5 plazas esta semana).',
    sddPillar: '💰 Dinero', formatoLabel: '🏆 Challenge', hookType: '🚨 Urgencia', nicho: 'Producto Digital',
    umvNote: 'PROMPT HEYGEN: Tono urgente, contador regresivo en la pantalla.',
    avatarTip: 'Cerca de cámara, intensidad alta'
  }
];

export function renderScripts(container) {
  const scripts = storage.getScripts();
  const hookTypes = getHookTypes();
  const ctaTypes = getCtaTypes();
  const nichos = getNichos();
  const sddPillars = getSddPillars();
  const formatos = getFormatos();

  container.innerHTML = `
    <div class="page-header">
      <h2>📝 Guiones Virales — Método Heras</h2>
      <p>UMV + SDD + 12 Formatos Virales → Mainstream hook + target story</p>
    </div>

    <div style="display:grid; grid-template-columns:400px 1fr; gap:24px;">
      <!-- Config Panel -->
      <div style="max-height:calc(100vh - 120px); overflow-y:auto; padding-right:8px;">
        <div class="card">
          <h3 style="font-weight:700; margin-bottom:20px;">Plantillas SISTEMA180</h3>
          <div class="input-group" style="background:var(--bg-secondary); padding:12px; border-radius:var(--radius-sm); border-left:3px solid var(--orange)">
            <label style="display:flex; justify-content:space-between; align-items:center;">
              Cargar Guion Probado (2026)
              <span class="tag tag-orange">TOP 10</span>
            </label>
            <select id="predefined-selector" style="font-weight:600;">
              <option value="">-- Seleccionar Plantilla --</option>
              ${PREDEFINED_SCRIPTS.map(s => `<option value="${s.id}">${s.title}</option>`).join('')}
            </select>
          </div>
        </div>

        <div class="card" style="margin-top:24px;">
          <h3 style="font-weight:700; margin-bottom:20px;">Generador Personalizado</h3>

          <!-- SDD Pillar Selector -->
          <div class="input-group">
            <label>🎯 Pilar SDD (motivador universal)</label>
            <div id="sdd-pillars" style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
              ${sddPillars.map((p, i) => `
                <label class="sdd-option" data-color="${p.color}" style="display:flex; align-items:center; gap:8px; padding:10px 12px; background:var(--bg-secondary); border-radius:var(--radius-xs); cursor:pointer; border:2px solid ${i === 1 ? p.color : 'var(--border)'}; font-size:13px; transition:var(--transition);">
                  <input type="radio" name="sddPillar" value="${p.id}" ${i === 1 ? 'checked' : ''} style="width:auto;">
                  <div>
                    <div style="font-weight:600;">${p.label}</div>
                    <div style="font-size:11px; color:var(--text-muted);">${p.desc}</div>
                  </div>
                </label>
              `).join('')}
            </div>
          </div>

          <!-- Formato Viral -->
          <div class="input-group">
            <label>🎬 Formato de Vídeo</label>
            <select id="sc-formato" style="font-size:13px;">
              ${formatos.map((f, i) => `<option value="${f.id}" ${i === 0 ? 'selected' : ''}>${f.label} — ${f.desc}</option>`).join('')}
            </select>
            <div id="formato-tip" style="margin-top:6px; padding:8px 12px; background:var(--bg-secondary); border-radius:var(--radius-xs); font-size:12px; color:var(--text-muted);">
              📹 ${formatos[0].notes}<br>🤖 Avatar: ${formatos[0].avatarTip}
            </div>
          </div>

          <div class="input-group">
            <label>Nicho / Sector</label>
            <select id="sc-nicho">
              ${nichos.map(n => `<option value="${n}">${n.charAt(0).toUpperCase() + n.slice(1)}</option>`).join('')}
            </select>
          </div>

          <div class="input-group">
            <label>Tipo de Gancho</label>
            <div id="hook-types" style="display:flex; flex-wrap:wrap; gap:8px;">
              ${hookTypes.map((h, i) => `
                <label style="display:flex; align-items:center; gap:6px; padding:8px 12px; background:var(--bg-secondary); border-radius:var(--radius-xs); cursor:pointer; border:1px solid var(--border); font-size:13px;">
                  <input type="radio" name="hookType" value="${h.id}" ${i === 0 ? 'checked' : ''} style="width:auto;">
                  ${h.label}
                </label>
              `).join('')}
            </div>
          </div>

          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div class="input-group">
              <label>Duración</label>
              <select id="sc-duracion">
                <option value="30s">30s (Stories)</option>
                <option value="45s">45s (Short)</option>
                <option value="60s" selected>60s (Ideal)</option>
                <option value="90s">1:30 (Largo)</option>
              </select>
            </div>
            <div class="input-group">
              <label>Plataforma</label>
              <select id="sc-plataforma">
                <option value="tiktok">TikTok</option>
                <option value="reels">Reels</option>
                <option value="youtube_shorts">YT Shorts</option>
                <option value="youtube">YouTube</option>
              </select>
            </div>
          </div>

          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div class="input-group">
              <label>CTA</label>
              <select id="sc-cta">
                ${ctaTypes.map(c => `<option value="${c.id}">${c.label}</option>`).join('')}
              </select>
            </div>
            <div class="input-group">
              <label>Ciudad</label>
              <input type="text" id="sc-ciudad" value="Madrid">
            </div>
          </div>

          <div style="display:flex; flex-direction:column; gap:12px; margin-top:24px;">
            <button class="btn btn-primary btn-lg w-full" id="gen-script-btn">
              ⚡ Generar Guion Rápido (Local)
            </button>
            <button class="btn btn-secondary" id="ai-cascade-btn" style="flex:1;">
              🧠 Generador Avanzado IA (Gemini + Perplexity)
            </button>
          </div>
        </div>
      </div>

      <!-- Script Result -->
      <div>
        <div id="script-result">
          ${scripts.length > 0
      ? renderScriptResult(scripts[0])
      : `<div class="card text-center" style="padding:60px;">
                <div style="font-size:48px; margin-bottom:16px;">📝</div>
                <h3 style="margin-bottom:8px;">Genera tu primer guion viral</h3>
                <p style="color:var(--text-muted);">Selecciona SDD + Formato + Gancho y pulsa Generar</p>
              </div>`
    }
        </div>

        ${scripts.length > 0 ? `
          <h3 style="margin-top:24px; margin-bottom:16px; font-weight:700;">📚 Anteriores (${scripts.length})</h3>
          <div style="display:flex; flex-direction:column; gap:12px;">
            ${scripts.slice(0, 5).map((s, i) => `
              <div class="card" style="padding:16px; cursor:pointer;" data-script-idx="${i}">
                <div class="flex items-center justify-between">
                  <div>
                    ${s.sddPillar ? `<span class="tag tag-green">${s.sddPillar}</span>` : ''}
                    <span class="tag tag-purple" style="margin-left:6px;">${s.config?.hookType || ''}</span>
                    <span class="tag tag-cyan" style="margin-left:6px;">${s.config?.nicho || ''}</span>
                    ${s.formato ? `<span class="tag tag-orange" style="margin-left:6px;">${s.formato.label}</span>` : ''}
                  </div>
                  <span style="color:var(--text-muted); font-size:12px;">${new Date(s.timestamp).toLocaleDateString('es-ES')}</span>
                </div>
                <p style="margin-top:8px; font-size:14px; color:var(--text-secondary);">${s.hook?.substring(0, 80)}...</p>
              </div>
            `).join('')}
          </div>
        ` : ''}
      </div>
    </div>
  `;

  // SDD pillar border highlight
  container.querySelectorAll('.sdd-option').forEach(opt => {
    const radio = opt.querySelector('input[type="radio"]');
    radio.addEventListener('change', () => {
      container.querySelectorAll('.sdd-option').forEach(o => o.style.borderColor = 'var(--border)');
      if (radio.checked) opt.style.borderColor = opt.dataset.color;
    });
  });

  // Formato selector tip
  const formatoSelect = container.querySelector('#sc-formato');
  const formatoTip = container.querySelector('#formato-tip');
  formatoSelect.addEventListener('change', () => {
    const f = formatos.find(x => x.id === formatoSelect.value);
    if (f && formatoTip) {
      formatoTip.innerHTML = `📹 ${f.notes}<br>🤖 Avatar: ${f.avatarTip}`;
    }
  });

  // Predefined selector
  container.querySelector('#predefined-selector').addEventListener('change', (e) => {
    const val = e.target.value;
    if (!val) return;
    const pre = PREDEFINED_SCRIPTS.find(x => x.id === val);
    if (!pre) return;

    // Build script object mimicking generator
    const script = {
      hook: pre.hook,
      story: pre.story,
      moraleja: pre.moraleja,
      cta: pre.cta,
      sddPillar: pre.sddPillar,
      formato: { label: pre.formatoLabel, notes: pre.umvNote, avatarTip: pre.avatarTip },
      config: { hookType: pre.hookType, nicho: pre.nicho },
      umvNote: pre.umvNote,
      timestamp: new Date().toISOString()
    };

    storage.addScript(script);
    container.querySelector('#script-result').innerHTML = renderScriptResult(script);
  });

  // Generate button
  container.querySelector('#gen-script-btn').addEventListener('click', () => {
    const hookType = container.querySelector('input[name="hookType"]:checked')?.value || 'curiosidad';
    const sddPillar = container.querySelector('input[name="sddPillar"]:checked')?.value || 'dinero';
    const script = generateScript({
      nicho: container.querySelector('#sc-nicho').value,
      hookType,
      sddPillar,
      formato: formatoSelect.value,
      duracion: container.querySelector('#sc-duracion').value,
      plataforma: container.querySelector('#sc-plataforma').value,
      ctaType: container.querySelector('#sc-cta').value,
      ciudad: container.querySelector('#sc-ciudad').value,
    });

    storage.addScript(script);
    container.querySelector('#script-result').innerHTML = renderScriptResult(script);
  });

  // Advanced AI Cascade Generator button
  container.querySelector('#ai-cascade-btn').addEventListener('click', async () => {
    const aiBtn = container.querySelector('#ai-cascade-btn');
    const resultContainer = container.querySelector('#script-result');

    // Check keys
    if (!storage.getGeminiKey() || !storage.getPerplexityKey()) {
      alert('Error: Faltan claves. Ve a Ajustes y añade tus API Keys de Gemini y Perplexity.');
      return;
    }

    const nicho = container.querySelector('#sc-nicho').value;
    const hookType = container.querySelector('input[name="hookType"]:checked')?.value || 'curiosidad';
    const sddPillar = container.querySelector('input[name="sddPillar"]:checked')?.value || 'dinero';

    const formatoId = formatoSelect.value;
    const formatoObj = getFormatos().find(f => f.id === formatoId);

    // Ask for a topic to research
    const topic = prompt('Dime el tema específico sobre el que quieres que investiguemos y hagamos el guion:', 'Ej: Caída de interacciones en Instagram en 2026');
    if (!topic) return;

    aiBtn.disabled = true;

    try {
      // Loop sequence
      const aiData = await aiCascade.generateViralScriptSequence(
        topic,
        nicho,
        hookType,
        sddPillar,
        (msg) => {
          aiBtn.innerHTML = `<div class="spinner"></div> ${msg}`;
        }
      );

      // Construct final script object
      const script = {
        title: `IA: ${topic.substring(0, 30)}...`,
        hook: aiData.hook,
        story: aiData.story,
        moraleja: aiData.moraleja,
        cta: aiData.cta,
        sddPillar: getSddPillars().find(p => p.id === sddPillar)?.label || 'Dinero',
        formato: { label: formatoObj.label, notes: formatoObj.notes, avatarTip: formatoObj.avatarTip },
        config: { hookType, nicho },
        umvNote: 'Generado automáticamente por IA Cascade Workflow (ChatGPT -> Perplexity -> ChatGPT).',
        timestamp: new Date().toISOString()
      };

      storage.addScript(script);
      resultContainer.innerHTML = renderScriptResult(script);

    } catch (err) {
      console.error(err);
      alert('Error en la cascada IA: ' + err.message);
    } finally {
      aiBtn.disabled = false;
      aiBtn.innerHTML = '🧠 Generador Avanzado IA (ChatGPT + Perplexity)';
      renderScripts(container); // Refresh to show in previous list
    }
  });

  // Click on previous scripts
  container.querySelectorAll('[data-script-idx]').forEach(el => {
    el.addEventListener('click', () => {
      const idx = parseInt(el.dataset.scriptIdx);
      const script = scripts[idx];
      if (script) container.querySelector('#script-result').innerHTML = renderScriptResult(script);
    });
  });
}

function renderScriptResult(script) {
  const formato = script.formato;
  return `
    <div class="card" style="padding:28px;">
      <div class="flex items-center justify-between mb-16" style="flex-wrap:wrap; gap:8px;">
        <h3 style="font-weight:700;">🎬 Guion Generado</h3>
        <div>
          ${script.sddPillar ? `<span class="tag tag-green">${script.sddPillar}</span>` : ''}
          ${formato ? `<span class="tag tag-orange" style="margin-left:6px;">${formato.label}</span>` : ''}
          <span class="tag tag-purple" style="margin-left:6px;">${script.config?.hookType || ''}</span>
          <span class="tag tag-cyan" style="margin-left:6px;">${script.config?.nicho || ''}</span>
        </div>
      </div>

      <!-- UMV + SDD + Format Note -->
      <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2); border-radius:var(--radius-sm); padding:12px 16px; margin-bottom:20px;">
        <p style="font-size:13px; color:var(--accent);">💡 ${script.umvNote || 'UMV + SDD'}</p>
      </div>

      ${formato ? `
      <!-- Format Production Card -->
      <div style="background:rgba(245,158,11,0.06); border:1px solid rgba(245,158,11,0.2); border-radius:var(--radius-sm); padding:12px 16px; margin-bottom:20px;">
        <div style="font-size:12px; font-weight:700; color:var(--orange); margin-bottom:4px;">🎬 PRODUCCIÓN — ${formato.label}</div>
        <p style="font-size:13px; color:var(--text-secondary);">📹 ${formato.notes}</p>
        <p style="font-size:13px; color:var(--text-secondary); margin-top:4px;">🤖 ${formato.avatarTip}</p>
        <p style="font-size:12px; color:var(--text-muted); margin-top:4px;">💡 Ejemplo: "${formato.ejemplo}"</p>
      </div>` : ''}

      <div class="script-phase hook">
        <div class="phase-tag">🪝 GANCHO — 0.6 segundos (Mainstream SDD)</div>
        <p>${script.hook}</p>
      </div>

      <div class="script-phase story">
        <div class="phase-tag">📖 DESARROLLO — Historia + Valor (→ Target)</div>
        <p>${script.story}</p>
      </div>

      <div class="script-phase moral">
        <div class="phase-tag">🎓 MORALEJA — Posicionamiento Experto</div>
        <p>${script.moraleja}</p>
      </div>

      <div class="script-phase cta">
        <div class="phase-tag">📢 CTA — Llamada a la Acción</div>
        <p>${script.cta}</p>
      </div>

      <div class="flex gap-8 mt-24">
        <button class="btn btn-primary">🎬 Usar en Vídeo</button>
        <button class="btn btn-secondary" onclick="navigator.clipboard.writeText(document.querySelector('.script-phase.hook p').textContent + '\\n\\n' + document.querySelector('.script-phase.story p').textContent + '\\n\\n' + document.querySelector('.script-phase.moral p').textContent + '\\n\\n' + document.querySelector('.script-phase.cta p').textContent)">📋 Copiar</button>
      </div>
    </div>
  `;
}
