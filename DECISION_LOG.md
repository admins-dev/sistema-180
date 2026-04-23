# SISTEMA 180 — DECISION LOG

> **Propósito:** Registro de todas las decisiones de limpieza, reorganización y reclasificación del repositorio.  
> **Fecha:** 23 Abril 2026  
> **Ejecutor:** Antigravity (agente IA) con aprobación de José María

---

## Principios aplicados

1. **No borrar visión** — Las 9 patas se preservan íntegramente
2. **Separar presente de historia** — TODO clasificado como CURRENT / LIVE / LEGACY / BACKLOG
3. **No romper producto real** — Cero modificaciones a código funcional, rutas o flujos
4. **Primero auditar, luego proponer, luego ejecutar** — Auditoría completa previa a cualquier cambio
5. **Todo cambio justificado** — Cada movimiento documentado aquí

---

## Decisiones de limpieza

### DEC-001: Eliminar perfiles de navegador del tracking de git
- **Qué era:** 3.999 archivos de Chromium/Edge en `meta-ads-bot/ghost-mouse/profiles/` (~2 GB)
- **Contenido:** GPUCache, GrShaderCache, ShaderCache, BrowserMetrics, DualEngine configs, LOCK files, LevelDB, etc.
- **Por qué estaba mal:** Son artefactos de runtime que Playwright genera automáticamente. No son código, no son producto, no aportan valor en git.
- **Acción:** `git rm -r --cached` + añadir a `.gitignore`
- **Impacto:** Los archivos siguen en disco, los scrapers siguen funcionando. Nuevos clones del repo pasan de ~2 GB a ~15 MB.

### DEC-002: Eliminar screenshots de debug del tracking
- **Qué era:** 65 capturas PNG en `meta-ads-bot/ghost-mouse/screenshots/`
- **Contenido:** Capturas de logins, formularios, resultados de DMs, debugging
- **Por qué estaba mal:** Son artefactos de desarrollo/testing, no documentación ni producto
- **Acción:** `git rm -r --cached` + `.gitignore`

### DEC-003: Eliminar fotos generadas del tracking
- **Qué era:** ~45 imágenes PNG en `generated_photos/`, `generated_photos_v2/`, `phantom_identities/`, `setter_avatars/`
- **Por qué estaba mal:** Son output reproducible de IA, no código fuente
- **Acción:** `git rm -r --cached` + `.gitignore`

### DEC-004: Eliminar datos operativos del tracking
- **Qué era:** leads.json, emails_leads*.json, sessions/*.json, dossiers/*.json, *.db, pending-insights.jsonl, _response.*, _tmp.py, profile_update_results.json
- **Por qué estaba mal:** Son datos runtime que cambian constantemente, no deberían estar versionados
- **Acción:** `git rm --cached` + `.gitignore`

### DEC-005: Eliminar archivos temporales de la raíz
- **Qué era:** temp-css.css, temp-key.js, css-diff.txt, result.json
- **Por qué estaba mal:** Residuos de desarrollo con "temp" en el nombre, sin función actual
- **Acción:** `git rm --cached` + `.gitignore`

### DEC-006: Eliminar PROMPT_CLAUDE_CODE.md del tracking
- **Qué era:** Documento de 32 KB con instrucciones completas + TODAS las API keys en texto plano
- **Por qué estaba mal:** Exposición de credenciales en el historial de git (Stripe live keys, Anthropic, Gemini, Groq, Meta, Gmail password, 5 contraseñas de Instagram, proxies)
- **Acción:** `git rm --cached` + `.gitignore`. Información útil (arquitectura, bugs) preservada en otros documentos.
- **Recomendación pendiente:** Regenerar todas las keys expuestas

---

## Decisiones de reorganización

### DEC-007: Mover scripts ComfyUI de la raíz a `scripts/comfyui/`
- **Qué era:** 10 archivos .mjs sueltos en la raíz (faceswap.mjs, generate_profile_*.mjs, clone.js, etc.)
- **Por qué estaba mal ubicado:** Son scripts experimentales de ComfyUI API, no parte del core del producto
- **Dónde va:** `scripts/comfyui/`
- **Clasificación:** LEGACY

### DEC-008: Mover landing pages a `landings/`
- **Qué era:** landing.html, landing-it.html, informe-ahorro.html en la raíz
- **Por qué estaba mal ubicado:** Mezclados con config files y código fuente
- **Dónde va:** `landings/`
- **Clasificación:** LIVE

### DEC-009: Mover miro/ y PDF a `legacy/`
- **Qué era:** Carpeta miro/ con exports de tablero + PDF de informe de ahorro
- **Por qué estaba mal ubicado:** Materiales de planificación/venta de fase anterior mezclados con código activo
- **Dónde va:** `legacy/miro/`, `legacy/Informe_Ahorro_*.pdf`
- **Clasificación:** LEGACY

### DEC-010: Reorganizar docs/ en subdirectorios por estado
- **Qué era:** 11 documentos + emails todos en docs/ sin clasificación
- **Por qué estaba mal:** Mezcla de documentación actual con estrategias expiradas y casos de clientes individuales
- **Acción:** Crear `docs/current/`, `docs/legacy/`, `docs/backlog/`
- **A current/:** ARQUITECTURA.md, APIS.md, README_SISTEMA180.md, DEPLOY_VERCEL.md
- **A legacy/:** ESTRATEGIA_VENTAS_MARZO.md, ESTRATEGIA_INFLUENCERS_4M.md, CLIENTE_ESTEFANIA_ROMERO.md, METODOLOGIA_HERAS.md, MAPA_COMPLETO_SISTEMA180.md, clon_influencer_perfecto.png

---

## Decisiones de documentación

### DEC-011: Crear CURRENT_STATE.md como source of truth
- **Motivo:** 5 documentos contradictorios (6/7/8/9 patas, pricing diferente, niveles de afiliación inconsistentes)
- **Solución:** Un documento canónico que manda sobre todos los demás
- **Contenido:** 3 líneas activas, 9 patas con estado, pricing actual, stack actual, módulos estratégicos

### DEC-012: Crear BACKLOG_MAP.md para preservar la visión
- **Motivo:** La visión de 9 patas no debe perderse ni mezclarse con la operativa actual
- **Contenido:** Las 9 patas completas con estado, módulos futuros, expansiones geográficas, ideas estratégicas

### DEC-013: Crear REPO_MAP.md para navegabilidad
- **Motivo:** Sin un mapa, el repo es innavegable para cualquier agente o persona nueva
- **Contenido:** Estructura completa con clasificación y función de cada carpeta

### DEC-014: Arreglar .gitignore corrupto
- **Qué era:** Línea 56 contenía caracteres nulos UTF-16 mezclados con UTF-8
- **Acción:** Reescritura completa del archivo con encoding limpio

---

## Cosas dejadas intactas (decisiones de NO tocar)

| Componente | Motivo |
|------------|--------|
| `meta-ads-bot/` estructura interna | 140+ archivos Python con imports relativos — alto riesgo de romper |
| `meta-ads-bot/ghost-mouse/` estructura interna | Misma razón |
| `src/` | Deploy Vercel activo |
| `backend/` | Tests 27/27, estructura profesional |
| `video-editor/` | Módulo funcional autocontenido |
| `PLAN_MAESTRO.md` | Documento de visión — se mantiene en raíz |
| Todos los archivos .py funcionales | Principio #3: no romper producto real |
| Tests ad-hoc (test_*.py) | Pueden ser útiles para debugging futuro de scrapers |
| `PROMPT_MAESTRO.md` | Se mantiene como referencia histórica de instrucciones |

---

## Riesgos que siguen vivos

| Riesgo | Severidad | Mitigación pendiente |
|--------|-----------|---------------------|
| Credenciales en historial de git | 🔴 Alta | Regenerar todas las API keys expuestas |
| Tamaño histórico del repo | 🟡 Media | BFG Repo Cleaner si se necesita reducir el .git/ |
| meta-ads-bot/ sin estructura interna | 🟡 Media | Fase separada de reorganización con testing |
| Documentación aún con contradicciones menores | 🟢 Baja | CURRENT_STATE.md manda; otros docs marcados como legacy |
