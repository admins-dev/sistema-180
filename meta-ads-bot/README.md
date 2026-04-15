# Meta Ads Bot — Gestión de campañas desde Telegram

Bot minimalista para gestionar campañas Meta Ads desde Telegram. Integrado con Meta Marketing API.

## Setup Rápido

### 1. Dependencias
```bash
pip install python-telegram-bot>=20.0 requests python-dotenv
```

### 2. Credenciales
- Copia `.env.example` a `.env`
- **Telegram**: Crea bot en [@BotFather](https://t.me/BotFather), obtén `TELEGRAM_BOT_TOKEN`
- **Meta**: En Meta Business Manager → Herramientas → API & Herramientas
  - Genera token con permisos: `ads_management`, `campaigns_read`, `campaigns_write`
  - Copia `META_ACCESS_TOKEN` y `META_AD_ACCOUNT_ID`

### 3. Lanzar bot
```bash
python bot.py
```

El bot debería iniciar y esperar comandos en Telegram.

## Comandos

| Comando | Uso | Ejemplo |
|---------|-----|---------|
| `/nueva_campaña` | Crear campaña | `/nueva_campaña 15 WEB800_Málaga` |
| `/pausar` | Pausar campaña | `/pausar camp_001` |
| `/métricas` | Ver métricas | `/métricas camp_001` |
| `/reporte_diario` | Resumen diario | `/reporte_diario` |

## Estructura

- **bot.py** (172 líneas): Handlers Telegram + validaciones
- **meta_client.py** (130 líneas): Cliente Meta API + CRUD
- **sync.py** (~110 líneas): Puente bot ↔ Meta API
- **.env**: Variables secretas

## Flujo

```
Usuario en Telegram
    ↓
bot.py (handler)
    ↓
sync.py (procesamiento)
    ↓
meta_client.py (API)
    ↓
Meta Marketing API
```

## Limitaciones (seguridad anti-baneo)

- Presupuesto máximo: 50€/campaña
- Nombre máximo: 50 caracteres
- Sin palabras prohibidas (validadas en bot.py)

## Próximos pasos

- [ ] Integración con Database (SQLite) en lugar de memoria
- [ ] Webhook para notificaciones en tiempo real
- [ ] Dashboard en Sistema 180 UI
- [ ] Auto-optimización de campañas (pausar bajos CPA, escalar ganadores)
