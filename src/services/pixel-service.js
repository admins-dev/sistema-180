// ═══════════════════════════════════════════════════════════
// Pixel Agent — Meta Pixel + Conversions API (CAPI) Service
// Luna · Sistema 180 HQ
// ═══════════════════════════════════════════════════════════
// Based on: facebook/facebook-nodejs-business-sdk
// Server-side: facebookincubator/ConversionsAPI-Tag-for-GoogleTagManager
// Docs: https://developers.facebook.com/docs/marketing-api/conversions-api/
// ═══════════════════════════════════════════════════════════
import { storage } from './storage.js';

// ── META PIXEL CLIENT-SIDE ───────────────────────────────────────────────────

/**
 * Generate the Meta Pixel base code snippet for client injection.
 * This is what gets injected into client landing pages.
 */
function generatePixelSnippet(pixelId) {
  if (!pixelId) return '';
  return `<!-- Meta Pixel Code — Sistema 180 · Luna Agent -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '${pixelId}');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=${pixelId}&ev=PageView&noscript=1"/></noscript>
<!-- End Meta Pixel Code -->`;
}

/**
 * Generate event tracking code for specific conversion events.
 * Events: Lead, Purchase, Schedule, Contact, CompleteRegistration
 */
function generateEventCode(eventName, params = {}) {
  const paramsStr = Object.keys(params).length > 0 ? `, ${JSON.stringify(params)}` : '';
  return `fbq('track', '${eventName}'${paramsStr});`;
}

// ── META CONVERSIONS API (CAPI) SERVER-SIDE ──────────────────────────────────

/**
 * Hash user data for CAPI (SHA-256).
 * Meta requires hashed PII for server events.
 */
async function hashData(value) {
  if (!value) return null;
  const normalized = value.toString().trim().toLowerCase();
  const encoder = new TextEncoder();
  const data = encoder.encode(normalized);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Generate a unique event ID for deduplication between Pixel and CAPI.
 */
function generateEventId() {
  return `s180_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Send a server-side event via Meta Conversions API.
 * Uses n8n webhook as proxy to avoid exposing CAPI token in frontend.
 * 
 * @param {string} eventName - Standard event: PageView, Lead, Purchase, Schedule, etc.
 * @param {object} userData - User data: email, phone, firstName, lastName, city, country
 * @param {object} customData - Custom data: value, currency, content_name, etc.
 * @param {string} eventId - Deduplication ID (same as client-side pixel event)
 */
async function sendServerEvent(eventName, userData = {}, customData = {}, eventId = null) {
  const pixelId = storage.get('meta_pixel_id');
  const capiToken = storage.get('meta_capi');
  const n8nWebhook = storage.get('n8n_webhook_leads');

  if (!pixelId) {
    console.warn('[Luna/Pixel] No Pixel ID configured');
    return { ok: false, error: 'No Pixel ID' };
  }

  const evtId = eventId || generateEventId();

  // Hash user data for privacy
  const hashedUser = {};
  if (userData.email) hashedUser.em = [await hashData(userData.email)];
  if (userData.phone) hashedUser.ph = [await hashData(userData.phone)];
  if (userData.firstName) hashedUser.fn = [await hashData(userData.firstName)];
  if (userData.lastName) hashedUser.ln = [await hashData(userData.lastName)];
  if (userData.city) hashedUser.ct = [await hashData(userData.city)];
  if (userData.country) hashedUser.country = [await hashData(userData.country)];

  // Build CAPI event payload (Meta format)
  const eventPayload = {
    data: [{
      event_name: eventName,
      event_time: Math.floor(Date.now() / 1000),
      event_id: evtId,
      event_source_url: window.location.href,
      action_source: 'website',
      user_data: {
        ...hashedUser,
        client_ip_address: null,  // n8n proxy fills this
        client_user_agent: navigator.userAgent,
        fbc: getCookie('_fbc') || null,
        fbp: getCookie('_fbp') || null,
      },
      custom_data: {
        ...customData,
        currency: customData.currency || 'EUR',
      }
    }]
  };

  // STRATEGY 1: Direct CAPI (if token available — works but exposes token)
  // STRATEGY 2: Via n8n webhook (recommended — token stays server-side)
  
  if (n8nWebhook) {
    // Route through n8n — preferred
    try {
      const res = await fetch(n8nWebhook, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: 'sistema180_pixel_agent',
          type: 'capi_event',
          pixel_id: pixelId,
          ...eventPayload,
        })
      });
      return { ok: res.ok, eventId: evtId, via: 'n8n' };
    } catch (err) {
      console.warn('[Luna/Pixel] n8n webhook failed, trying direct CAPI:', err.message);
    }
  }

  // Fallback: Direct CAPI call (Fix #15: token in header, not URL)
  if (capiToken) {
    try {
      const res = await fetch(
        `https://graph.facebook.com/v21.0/${pixelId}/events`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${capiToken}`,
          },
          body: JSON.stringify(eventPayload)
        }
      );
      const data = await res.json();
      return { ok: res.ok, eventId: evtId, via: 'direct_capi', response: data };
    } catch (err) {
      return { ok: false, error: err.message, via: 'direct_capi' };
    }
  }

  return { ok: false, error: 'No CAPI token or n8n webhook configured' };
}

// ── COOKIE HELPERS ───────────────────────────────────────────────────────────

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

// ── STANDARD EVENT HELPERS ───────────────────────────────────────────────────

/**
 * Track a Lead event (client + server with deduplication)
 */
async function trackLead(userData = {}, customData = {}) {
  const eventId = generateEventId();
  
  // Client-side Pixel
  if (window.fbq) {
    window.fbq('track', 'Lead', customData, { eventID: eventId });
  }

  // Server-side CAPI
  return sendServerEvent('Lead', userData, customData, eventId);
}

/**
 * Track a Purchase event
 */
async function trackPurchase(userData = {}, value = 0, currency = 'EUR') {
  const eventId = generateEventId();
  const customData = { value, currency };

  if (window.fbq) {
    window.fbq('track', 'Purchase', customData, { eventID: eventId });
  }

  return sendServerEvent('Purchase', userData, customData, eventId);
}

/**
 * Track a Schedule event (appointment/cita booked)
 */
async function trackSchedule(userData = {}, customData = {}) {
  const eventId = generateEventId();

  if (window.fbq) {
    window.fbq('track', 'Schedule', customData, { eventID: eventId });
  }

  return sendServerEvent('Schedule', userData, customData, eventId);
}

/**
 * Track a Contact event (WhatsApp click, phone call)
 */
async function trackContact(userData = {}) {
  const eventId = generateEventId();

  if (window.fbq) {
    window.fbq('track', 'Contact', {}, { eventID: eventId });
  }

  return sendServerEvent('Contact', userData, {}, eventId);
}

// ── LANDING PAGE GENERATOR ───────────────────────────────────────────────────

/**
 * Generate complete tracking code for a client landing page.
 * Includes: Meta Pixel base code + event tracking for Lead/Contact/Schedule
 */
function generateLandingTrackingCode(pixelId, options = {}) {
  const {
    trackLeadForm = true,
    trackWhatsAppClick = true,
    trackPhoneClick = true,
    trackSchedule = true,
  } = options;

  let code = generatePixelSnippet(pixelId);

  code += `\n<script>
// === Sistema 180 · Luna Pixel Agent · Auto-tracking ===
(function() {
  var eventCounter = 0;
  function s180EventId() { return 's180_' + Date.now() + '_' + (++eventCounter); }
`;

  if (trackLeadForm) {
    code += `
  // Track Lead on form submit
  document.addEventListener('submit', function(e) {
    var form = e.target;
    if (form.tagName === 'FORM') {
      var eid = s180EventId();
      fbq('track', 'Lead', {content_name: 'landing_form'}, {eventID: eid});
      console.log('[S180] Lead tracked:', eid);
    }
  });
`;
  }

  if (trackWhatsAppClick) {
    code += `
  // Track Contact on WhatsApp click
  document.addEventListener('click', function(e) {
    var link = e.target.closest('a[href*="wa.me"], a[href*="whatsapp"]');
    if (link) {
      var eid = s180EventId();
      fbq('track', 'Contact', {content_name: 'whatsapp_click'}, {eventID: eid});
      console.log('[S180] WhatsApp contact tracked:', eid);
    }
  });
`;
  }

  if (trackPhoneClick) {
    code += `
  // Track Contact on phone click
  document.addEventListener('click', function(e) {
    var link = e.target.closest('a[href^="tel:"]');
    if (link) {
      var eid = s180EventId();
      fbq('track', 'Contact', {content_name: 'phone_click'}, {eventID: eid});
      console.log('[S180] Phone contact tracked:', eid);
    }
  });
`;
  }

  if (trackSchedule) {
    code += `
  // Track Schedule on booking button click
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('[data-s180-event="schedule"], .s180-schedule-btn');
    if (btn) {
      var eid = s180EventId();
      fbq('track', 'Schedule', {content_name: 'appointment_booked'}, {eventID: eid});
      console.log('[S180] Schedule tracked:', eid);
    }
  });
`;
  }

  code += `
  console.log('[S180] Luna Pixel Agent active · Pixel: ${pixelId}');
})();
</script>`;

  return code;
}

// ── PIXEL DIAGNOSTICS ────────────────────────────────────────────────────────

/**
 * Run diagnostics on the current Pixel configuration
 */
function runDiagnostics() {
  const pixelId = storage.get('meta_pixel_id');
  const capiToken = storage.get('meta_capi');
  const adAccount = storage.get('meta_ad_account');
  const n8nWebhook = storage.get('n8n_webhook_leads');

  const checks = [
    { name: 'Pixel ID', ok: !!pixelId, value: pixelId ? `${pixelId.substring(0, 6)}...` : 'No configurado' },
    { name: 'CAPI Token', ok: !!capiToken, value: capiToken ? `${capiToken.substring(0, 8)}...` : 'No configurado' },
    { name: 'Ad Account', ok: !!adAccount, value: adAccount || 'No configurado' },
    { name: 'n8n Webhook', ok: !!n8nWebhook, value: n8nWebhook ? 'Configurado' : 'No configurado' },
    { name: 'Client Pixel (fbq)', ok: typeof window.fbq === 'function', value: typeof window.fbq === 'function' ? 'Cargado' : 'No cargado' },
    { name: 'Cookie _fbp', ok: !!getCookie('_fbp'), value: getCookie('_fbp') || 'No presente' },
    { name: 'Cookie _fbc', ok: !!getCookie('_fbc'), value: getCookie('_fbc') || 'No presente' },
    { name: 'CAPI Route', ok: !!(n8nWebhook || capiToken), value: n8nWebhook ? 'Via n8n (recomendado)' : capiToken ? 'Directo (expone token)' : 'No disponible' },
  ];

  return {
    checks,
    ready: checks.filter(c => c.ok).length,
    total: checks.length,
    score: Math.round((checks.filter(c => c.ok).length / checks.length) * 100),
  };
}

// ── EXPORT ────────────────────────────────────────────────────────────────────

export const pixelService = {
  // Snippets
  generatePixelSnippet,
  generateEventCode,
  generateLandingTrackingCode,

  // CAPI
  sendServerEvent,
  hashData,
  generateEventId,

  // Standard events
  trackLead,
  trackPurchase,
  trackSchedule,
  trackContact,

  // Diagnostics
  runDiagnostics,

  // Status
  isConfigured() {
    return !!storage.get('meta_pixel_id');
  },
  getPixelId() {
    return storage.get('meta_pixel_id') || '';
  },
};
