// ═══════════════════════════════════════════════
// Legal & GDPR — Sistema de Cumplimiento
// RGPD / LOPDGDD España — sistema-180.com
// ═══════════════════════════════════════════════

const COMPANY = {
  nombre: 'Sistema 180',
  dominio: 'sistema-180.com',
  email: 'legal@sistema-180.com',
  cif: '',
  direccion: 'Marbella, Málaga, España',
  responsable: 'José María Moreno García',
};

function getCompanyData() {
  const saved = localStorage.getItem('s180_legal_company');
  return saved ? { ...COMPANY, ...JSON.parse(saved) } : COMPANY;
}

function saveCompanyData(data) {
  localStorage.setItem('s180_legal_company', JSON.stringify(data));
  localStorage.setItem('s180_legal_configured', 'true');
}

// ── Generadores de documentos legales ────────────────────────
function genPrivacyPolicy(c) {
  return `POLÍTICA DE PRIVACIDAD

Última actualización: ${new Date().toLocaleDateString('es-ES')}

1. RESPONSABLE DEL TRATAMIENTO
${c.nombre} | ${c.dominio}
Responsable: ${c.responsable}
${c.cif ? 'CIF/NIF: ' + c.cif : ''}
Dirección: ${c.direccion}
Email: ${c.email}

2. DATOS QUE RECOPILAMOS
• Datos de identificación: nombre, email, teléfono
• Datos de navegación: cookies técnicas y analíticas (con consentimiento)
• Datos de facturación: a través de Stripe (procesador externo)

3. FINALIDAD Y BASE LEGAL
• Prestación del servicio contratado (Art. 6.1.b RGPD)
• Envío de comunicaciones comerciales (consentimiento — Art. 6.1.a RGPD)
• Obligaciones legales y fiscales (Art. 6.1.c RGPD)

4. CONSERVACIÓN DE DATOS
Los datos se conservan durante la relación contractual y 5 años posteriores para obligaciones fiscales.

5. DESTINATARIOS
• Stripe Inc. (pagos) — transferencia internacional con garantías RGPD
• Slack Technologies (alertas internas)
• No cedemos datos a terceros sin consentimiento expreso.

6. DERECHOS DEL USUARIO
Puedes ejercer tus derechos de acceso, rectificación, supresión, portabilidad, limitación y oposición enviando email a ${c.email} con asunto "Derechos RGPD" + copia de tu DNI.

También puedes reclamar ante la Agencia Española de Protección de Datos (www.aepd.es).

7. SEGURIDAD
Aplicamos medidas técnicas y organizativas para proteger tus datos conforme al RGPD y la LOPDGDD (Ley Orgánica 3/2018).`;
}

function genCookiePolicy(c) {
  return `POLÍTICA DE COOKIES

Última actualización: ${new Date().toLocaleDateString('es-ES')}
Sitio web: ${c.dominio}

¿QUÉ SON LAS COOKIES?
Las cookies son pequeños archivos de texto que se almacenan en tu dispositivo cuando visitas una web.

COOKIES QUE UTILIZAMOS

1. COOKIES TÉCNICAS (necesarias — no requieren consentimiento)
   • Sesión de usuario: identifica tu sesión activa
   • Preferencias de idioma
   • Consentimiento de cookies (recuerda tu decisión)

2. COOKIES ANALÍTICAS (requieren consentimiento)
   • Google Analytics (si está activo): visitas anónimas, comportamiento
   • Duración: 2 años

3. COOKIES DE TERCEROS (requieren consentimiento)
   • Stripe: procesamiento de pagos seguros
   • Meta Pixel (si está activo): medición campañas publicitarias

CÓMO GESTIONAR LAS COOKIES
Puedes aceptar, rechazar o configurar cookies en nuestro banner al entrar a la web.
También puedes eliminarlas desde la configuración de tu navegador.

CONTACTO
${c.email}`;
}

function genLegalNotice(c) {
  return `AVISO LEGAL

En cumplimiento del artículo 10 de la Ley 34/2002, de Servicios de la Sociedad de la Información y Comercio Electrónico (LSSICE):

DATOS IDENTIFICATIVOS
Denominación: ${c.nombre}
${c.cif ? 'CIF/NIF: ' + c.cif : 'CIF/NIF: (pendiente de alta autónomo)'}
Responsable: ${c.responsable}
Domicilio: ${c.direccion}
Email: ${c.email}
Web: https://${c.dominio}

OBJETO
El presente Aviso Legal regula el acceso y uso del sitio web ${c.dominio}.

PROPIEDAD INTELECTUAL
Todos los contenidos de esta web (textos, imágenes, código, diseños) son propiedad de ${c.nombre} o sus licenciantes. Queda prohibida su reproducción sin autorización expresa.

LEGISLACIÓN APLICABLE
Las relaciones entre ${c.nombre} y los usuarios se rigen por la legislación española vigente, siendo competentes los Juzgados y Tribunales de Marbella (Málaga) para cualquier controversia.`;
}

function genTermsOfService(c) {
  return `TÉRMINOS Y CONDICIONES DE SERVICIO

Última actualización: ${new Date().toLocaleDateString('es-ES')}

1. OBJETO
Estos términos regulan la contratación de servicios de ${c.nombre} a través de ${c.dominio}.

2. SERVICIOS
• Web profesional (297€ pago único): incluye diseño, desarrollo y configuración inicial.
• Recepcionista IA 24/7 (300€/mes): bot de atención automática por WhatsApp/teléfono.
• Servicios adicionales: avatares IA, posicionamiento SEO local, consultoría.

3. PROCESO DE CONTRATACIÓN
1) Selección del servicio y pago a través de Stripe
2) Confirmación por email en menos de 24h
3) Inicio del proyecto en un máximo de 48-72h laborables

4. PRECIOS E IVA
Todos los precios se indican sin IVA. Se aplicará el 21% de IVA según normativa española.

5. DERECHO DE DESISTIMIENTO
El cliente dispone de 14 días naturales para desistir del contrato sin penalización, salvo que el servicio haya sido completamente prestado con su consentimiento.

6. RESPONSABILIDADES
${c.nombre} no se responsabiliza de caídas de servicio ajenas (WhatsApp, OpenAI, Stripe) ni de resultados de negocio específicos. Ofrecemos herramientas; los resultados dependen del uso que el cliente haga de ellas.

7. JURISDICCIÓN
Juzgados y Tribunales de Marbella (Málaga). Ley española aplicable.

Contacto: ${c.email}`;
}

// ── Render principal ──────────────────────────────────────────
export function renderLegal(container) {
  const c = getCompanyData();
  const configured = localStorage.getItem('s180_legal_configured') === 'true';

  container.innerHTML = `
    <div class="page-header" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
      <div>
        <h2 style="font-size:24px;font-weight:800;margin-bottom:4px;">⚖️ Legal & GDPR</h2>
        <p style="color:var(--text-muted);font-size:13px;">Cumplimiento RGPD · LOPDGDD · LSSICE — sistema-180.com</p>
      </div>
      <div style="display:flex;gap:10px;align-items:center;">
        ${configured
          ? `<span style="background:rgba(16,185,129,.15);color:var(--green);padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;">✔ Configurado</span>`
          : `<span style="background:rgba(239,68,68,.15);color:var(--red);padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;">⚠ Pendiente de configurar</span>`
        }
      </div>
    </div>

    <!-- Alerta si no está configurado -->
    ${!configured ? `
    <div style="background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:12px;padding:16px;margin-bottom:20px;">
      <div style="font-size:14px;font-weight:700;color:var(--red);margin-bottom:6px;">⚠ Atención: Multas RGPD de hasta 20.000.000€ o el 4% de la facturación anual</div>
      <div style="font-size:13px;color:var(--text-secondary);">Configura los datos de empresa y activa el banner de cookies ANTES de lanzar sistema-180.com. Completa la sección de datos abajo.</div>
    </div>` : ''}

    <!-- Checklist de cumplimiento -->
    <div class="card" style="margin-bottom:20px;">
      <div style="font-size:14px;font-weight:700;margin-bottom:16px;">✅ Checklist de Cumplimiento RGPD</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px;" id="compliance-checklist">
        ${[
          { id:'banner', label:'Banner de cookies activo en la web', done: configured },
          { id:'privacy', label:'Política de privacidad publicada', done: configured },
          { id:'cookies', label:'Política de cookies publicada', done: configured },
          { id:'legal', label:'Aviso legal publicado', done: configured },
          { id:'terms', label:'Términos y condiciones publicados', done: configured },
          { id:'stripe', label:'Stripe con DPA firmado (automático)', done: true },
          { id:'cif', label:'CIF/NIF registrado en documentos', done: !!c.cif },
          { id:'email', label:'Email legal configurado', done: c.email !== COMPANY.email },
        ].map(item => `
          <div style="display:flex;align-items:center;gap:10px;padding:10px;background:var(--bg-glass);border-radius:8px;border:1px solid ${item.done ? 'rgba(16,185,129,.2)' : 'rgba(239,68,68,.2)'};">
            <span style="font-size:18px;">${item.done ? '✅' : '⬜'}</span>
            <span style="font-size:13px;color:${item.done ? 'var(--text-secondary)' : 'var(--text-primary)'};">${item.label}</span>
          </div>
        `).join('')}
      </div>
    </div>

    <!-- Datos de empresa -->
    <div class="card" style="margin-bottom:20px;">
      <div style="font-size:14px;font-weight:700;margin-bottom:16px;">🏢 Datos de la Empresa</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;" id="company-form">
        ${[
          { id:'nombre',      label:'Nombre empresa',      val: c.nombre },
          { id:'dominio',     label:'Dominio web',         val: c.dominio },
          { id:'email',       label:'Email legal',         val: c.email },
          { id:'cif',         label:'CIF / NIF autónomo',  val: c.cif, placeholder:'Cuando des de alta autónomo' },
          { id:'responsable', label:'Responsable tratamiento', val: c.responsable },
          { id:'direccion',   label:'Dirección fiscal',    val: c.direccion },
        ].map(f => `
          <div>
            <label style="font-size:11px;color:var(--text-muted);display:block;margin-bottom:4px;">${f.label}</label>
            <input type="text" id="legal-${f.id}" value="${f.val}" placeholder="${f.placeholder || ''}"
              style="width:100%;background:var(--bg-glass);border:1px solid var(--border);color:var(--text-primary);
                     padding:8px 10px;border-radius:8px;font-size:13px;outline:none;">
          </div>
        `).join('')}
      </div>
      <div style="margin-top:12px;">
        <button id="btn-save-legal-data" style="background:var(--accent);color:#fff;border:none;padding:10px 20px;border-radius:10px;font-weight:700;cursor:pointer;font-size:13px;">
          💾 Guardar datos
        </button>
      </div>
    </div>

    <!-- Documentos generados -->
    <div style="font-size:16px;font-weight:700;margin-bottom:16px;">📄 Documentos Legales — Generados para sistema-180.com</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-bottom:20px;">
      ${[
        { id:'privacy', icon:'🔒', title:'Política de Privacidad', sub:'RGPD + LOPDGDD · Obligatorio', color:'var(--accent)' },
        { id:'cookies', icon:'🍪', title:'Política de Cookies',    sub:'LSSICE · Obligatorio',          color:'var(--orange)' },
        { id:'legal-notice', icon:'📋', title:'Aviso Legal',       sub:'LSSICE Art. 10 · Obligatorio',  color:'var(--green)' },
        { id:'terms',   icon:'📝', title:'Términos y Condiciones', sub:'Contratos de servicio',          color:'var(--cyan)' },
      ].map(doc => `
        <div class="card" style="border-left:3px solid ${doc.color};">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <span style="font-size:24px;">${doc.icon}</span>
            <div>
              <div style="font-size:14px;font-weight:700;">${doc.title}</div>
              <div style="font-size:11px;color:var(--text-muted);">${doc.sub}</div>
            </div>
          </div>
          <div style="display:flex;gap:8px;">
            <button class="btn-preview-doc" data-doc="${doc.id}"
              style="flex:1;background:var(--bg-glass);color:var(--text-secondary);border:1px solid var(--border);
                     padding:8px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;">
              👁 Ver
            </button>
            <button class="btn-copy-doc" data-doc="${doc.id}"
              style="flex:1;background:${doc.color};color:#fff;border:none;
                     padding:8px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;">
              📋 Copiar
            </button>
          </div>
        </div>
      `).join('')}
    </div>

    <!-- Banner de cookies -->
    <div class="card" style="margin-bottom:20px;border:1px solid rgba(6,182,212,.2);">
      <div style="font-size:14px;font-weight:700;margin-bottom:12px;">🍪 Banner de Cookies — Código para tu Web</div>
      <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;">
        Copia este código y pégalo justo antes de <code style="background:var(--bg-glass);padding:2px 6px;border-radius:4px;">&lt;/body&gt;</code> en tu web de Lovable / Vercel.
      </p>
      <div style="background:#0d1117;border-radius:10px;padding:16px;font-family:monospace;font-size:11px;color:#e6edf3;overflow-x:auto;line-height:1.6;" id="cookie-banner-code">
${getCookieBannerCode(c)}
      </div>
      <button id="btn-copy-banner" style="margin-top:12px;background:var(--cyan);color:#0a0a1a;border:none;padding:10px 20px;border-radius:10px;font-weight:700;cursor:pointer;font-size:13px;">
        📋 Copiar código del banner
      </button>
    </div>

    <!-- Modal de preview -->
    <div id="legal-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:1000;overflow-y:auto;padding:40px 20px;">
      <div style="max-width:760px;margin:0 auto;background:var(--bg-secondary);border-radius:16px;border:1px solid var(--border);padding:32px;position:relative;">
        <button id="close-modal" style="position:absolute;top:16px;right:16px;background:var(--bg-glass);border:1px solid var(--border);color:var(--text-primary);padding:6px 12px;border-radius:8px;cursor:pointer;font-size:14px;">✕ Cerrar</button>
        <h3 id="modal-title" style="font-size:18px;font-weight:700;margin-bottom:20px;"></h3>
        <pre id="modal-content" style="white-space:pre-wrap;font-family:inherit;font-size:13px;color:var(--text-secondary);line-height:1.8;"></pre>
        <button id="modal-copy" style="margin-top:20px;background:var(--accent);color:#fff;border:none;padding:10px 20px;border-radius:10px;font-weight:700;cursor:pointer;font-size:13px;">📋 Copiar texto</button>
      </div>
    </div>
  `;

  const currentCompany = getCompanyData();

  // Guardar datos empresa
  container.querySelector('#btn-save-legal-data').addEventListener('click', () => {
    const fields = ['nombre','dominio','email','cif','responsable','direccion'];
    const updated = {};
    fields.forEach(f => {
      const el = container.querySelector(`#legal-${f}`);
      if (el) updated[f] = el.value;
    });
    saveCompanyData(updated);
    // Recargar página
    import('../main.js').then(m => m.navigate('legal'));
  });

  // Preview documentos
  const docs = {
    'privacy':      { title: 'Política de Privacidad',    fn: genPrivacyPolicy },
    'cookies':      { title: 'Política de Cookies',        fn: genCookiePolicy },
    'legal-notice': { title: 'Aviso Legal',                fn: genLegalNotice },
    'terms':        { title: 'Términos y Condiciones',     fn: genTermsOfService },
  };

  container.querySelectorAll('.btn-preview-doc').forEach(btn => {
    btn.addEventListener('click', () => {
      const doc = docs[btn.dataset.doc];
      if (!doc) return;
      const text = doc.fn(currentCompany);
      container.querySelector('#modal-title').textContent = doc.title;
      container.querySelector('#modal-content').textContent = text;
      container.querySelector('#legal-modal').style.display = 'block';
    });
  });

  container.querySelectorAll('.btn-copy-doc').forEach(btn => {
    btn.addEventListener('click', () => {
      const doc = docs[btn.dataset.doc];
      if (!doc) return;
      navigator.clipboard.writeText(doc.fn(currentCompany));
      const orig = btn.textContent;
      btn.textContent = '✅ Copiado';
      setTimeout(() => { btn.textContent = orig; }, 2000);
    });
  });

  container.querySelector('#close-modal').addEventListener('click', () => {
    container.querySelector('#legal-modal').style.display = 'none';
  });

  container.querySelector('#modal-copy').addEventListener('click', () => {
    const text = container.querySelector('#modal-content').textContent;
    navigator.clipboard.writeText(text);
    const btn = container.querySelector('#modal-copy');
    btn.textContent = '✅ Copiado';
    setTimeout(() => { btn.textContent = '📋 Copiar texto'; }, 2000);
  });

  container.querySelector('#btn-copy-banner').addEventListener('click', () => {
    const code = container.querySelector('#cookie-banner-code').textContent;
    navigator.clipboard.writeText(code);
    const btn = container.querySelector('#btn-copy-banner');
    btn.textContent = '✅ Copiado';
    setTimeout(() => { btn.textContent = '📋 Copiar código del banner'; }, 2000);
  });
}

function getCookieBannerCode(c) {
  return `<!-- SISTEMA 180 — Cookie Banner RGPD/LOPDGDD -->
<style>
#s180-cookie-banner{position:fixed;bottom:0;left:0;right:0;background:#12122a;border-top:1px solid rgba(255,255,255,.1);
  padding:20px 32px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;
  z-index:9999;font-family:Inter,sans-serif;}
#s180-cookie-banner p{margin:0;font-size:13px;color:#94a3b8;max-width:700px;line-height:1.6;}
#s180-cookie-banner a{color:#6366f1;}
.s180-btn{padding:10px 20px;border-radius:10px;font-weight:700;font-size:13px;cursor:pointer;border:none;}
.s180-btn-accept{background:#6366f1;color:#fff;}
.s180-btn-reject{background:transparent;color:#64748b;border:1px solid rgba(255,255,255,.1);}
</style>
<div id="s180-cookie-banner">
  <p>Usamos cookies técnicas (necesarias) y analíticas (opcionales) en ${c.dominio}.
  Puedes aceptar todas o solo las necesarias. <a href="/cookies" target="_blank">Más info</a></p>
  <div style="display:flex;gap:10px;flex-shrink:0;">
    <button class="s180-btn s180-btn-reject" onclick="s180CookieChoice(false)">Solo necesarias</button>
    <button class="s180-btn s180-btn-accept" onclick="s180CookieChoice(true)">Aceptar todas</button>
  </div>
</div>
<script>
(function(){
  if(localStorage.getItem('s180_cookie_consent')) {
    document.addEventListener('DOMContentLoaded',function(){
      var b=document.getElementById('s180-cookie-banner');
      if(b) b.style.display='none';
    });
  }
})();
function s180CookieChoice(all){
  localStorage.setItem('s180_cookie_consent', all ? 'all' : 'necessary');
  localStorage.setItem('s180_cookie_consent_date', new Date().toISOString());
  document.getElementById('s180-cookie-banner').style.display='none';
  if(all){ /* Aquí activar Google Analytics, Meta Pixel, etc. */ }
}
<\/script>`;
}
