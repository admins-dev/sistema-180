# Sistema 180 — Meta Ads Bot: Quick Start (5 minutos)

## 1️⃣ Instalar Dependencias (2 min)

```bash
cd /home/jose/proyectos/sistema-180/meta-ads-bot
./install.sh
```

## 2️⃣ Activar Entorno Virtual

```bash
source venv/bin/activate
```

## 3️⃣ Iniciar Bot + Servidor (simultaneo)

```bash
./start.sh
```

Verás:
```
🚀 Iniciando Sistema 180 Meta Ads Bot...
✅ Entorno listo
Iniciando servicios en paralelo:
  • Telegram Bot (bot.py)
  • Flask Server (server.py en :5000)

🤖 Bot PID: 12345
🌐 Server PID: 12346
```

## 4️⃣ Verificar Estado

En otra terminal:
```bash
curl http://localhost:5000/api/meta-ads/status
```

Debe retornar:
```json
{"active": true, "lastSync": "...", "totalCampaigns": ...}
```

## 5️⃣ Probar en Dashboard

1. Abre: `http://localhost:3000/`
2. Busca sección **"📢 Meta Ads Bot"** (panel derecho)
3. Click **"🔄 Sync"** → debe mostrar campaña(s)

## 6️⃣ Probar en Telegram

1. Abre Telegram → busca `@Sistema180ADS_bot`
2. Envía: `"Dame los datos de las campañas"`
3. Bot debe responder con metrics

---

## 🎯 Comandos Útiles

| Comando | Uso |
|---------|-----|
| `./install.sh` | Instala dependencias (primera vez) |
| `./start.sh` | Inicia bot + servidor |
| `python3 health-check.py` | Verifica estado del sistema |
| `Ctrl+C` | Detiene bot + servidor |

---

## 🐛 Si Algo Falla

### Error: `ModuleNotFoundError`
```bash
./install.sh  # Reinstalar dependencias
```

### Error: `Connection refused :5000`
```bash
# Verifica que start.sh está ejecutándose
ps aux | grep python3
# Si no, ejecuta: ./start.sh
```

### Error: Telegram bot no responde
1. Verifica TELEGRAM_BOT_TOKEN en `.env` es correcto
2. Verifica bot.py tiene logs correctos: `tail -f ...`

---

## 📚 Documentación Completa

- **SETUP_GUIDE.md** — Guía detallada de instalación
- **../ARCHITECTURE.md** — Diagrama de arquitectura completa

---

*Next: Mantén `./start.sh` ejecutándose en background. Sistema 180 está live. 🚀*
