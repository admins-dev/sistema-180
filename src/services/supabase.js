// SISTEMA180 — Supabase client
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabaseConfig = { url: SUPABASE_URL, anonKey: SUPABASE_ANON_KEY };
export const isSupabaseConfigured = () => !!(SUPABASE_URL && SUPABASE_ANON_KEY);

/**
 * Simple fetch wrapper for Supabase REST API (sin SDK para mantener bundle pequeño)
 * @param {string} table - Nombre de la tabla
 * @param {Object} options - { method, filter, body, select }
 * @returns {Promise<any>}
 */
export async function supabaseFetch(table, options = {}) {
  if (!isSupabaseConfigured()) throw new Error('Supabase URL not configured. Set VITE_SUPABASE_URL in .env');
  const { method = 'GET', filter, body, select = '*' } = options;
  let url = `${SUPABASE_URL}/rest/v1/${table}?select=${select}`;
  if (filter) url += `&${filter}`;
  const res = await fetch(url, {
    method,
    headers: {
      'apikey': SUPABASE_ANON_KEY,
      'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': method === 'POST' ? 'return=representation' : '',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
