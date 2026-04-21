"""
jarvis_calendar.py — Sistema 180
Google Calendar integration via API.
Crea, consulta y gestiona eventos desde Telegram.
"""
import os, json, logging, requests
from datetime import datetime, timedelta, date
from pathlib import Path

logger = logging.getLogger(__name__)

GOOGLE_CALENDAR_API_KEY = os.getenv("GOOGLE_CALENDAR_API_KEY", "")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

# Local storage for events (works without Google API key)
EVENTS_FILE = Path(__file__).parent / "calendar_events.json"


def _load_events() -> list[dict]:
    if EVENTS_FILE.exists():
        try:
            return json.loads(EVENTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save_events(events: list[dict]):
    EVENTS_FILE.write_text(json.dumps(events, indent=2, ensure_ascii=False))


def _parse_date(date_str: str) -> str:
    """Parse natural date references to ISO format."""
    today = date.today()
    date_lower = date_str.lower().strip()

    if not date_str:
        return today.isoformat()
    if "hoy" in date_lower:
        return today.isoformat()
    if "mañana" in date_lower or "manana" in date_lower:
        return (today + timedelta(days=1)).isoformat()
    if "pasado" in date_lower:
        return (today + timedelta(days=2)).isoformat()

    # Day of week
    days_map = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }
    for day_name, day_num in days_map.items():
        if day_name in date_lower:
            days_ahead = day_num - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).isoformat()

    # Try direct parse
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m"):
        try:
            parsed = datetime.strptime(date_str.strip(), fmt)
            if parsed.year == 1900:  # no year given
                parsed = parsed.replace(year=today.year)
            return parsed.date().isoformat()
        except ValueError:
            continue

    return today.isoformat()


def _parse_time(time_str: str) -> str:
    """Parse time string to HH:MM."""
    if not time_str:
        return "09:00"
    # Remove common words
    time_str = time_str.lower().replace("de la mañana", "").replace("de la tarde", "")
    time_str = time_str.replace("am", "").replace("pm", "").strip()

    # Try HH:MM
    import re
    m = re.search(r'(\d{1,2}):(\d{2})', time_str)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"

    # Try just hour
    m = re.search(r'(\d{1,2})', time_str)
    if m:
        h = int(m.group(1))
        if "tarde" in time_str and h < 12:
            h += 12
        return f"{h:02d}:00"

    return "09:00"


def create_event(title: str, event_date: str = "", event_time: str = "",
                 description: str = "") -> dict:
    """Crea un evento en el calendario."""
    parsed_date = _parse_date(event_date)
    parsed_time = _parse_time(event_time)

    event = {
        "id": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "title": title,
        "date": parsed_date,
        "time": parsed_time,
        "description": description,
        "created_at": datetime.utcnow().isoformat(),
        "status": "confirmed",
    }

    # Try Google Calendar API first
    if GOOGLE_CALENDAR_API_KEY:
        try:
            start_dt = f"{parsed_date}T{parsed_time}:00"
            end_dt_obj = datetime.fromisoformat(f"{parsed_date}T{parsed_time}:00") + timedelta(hours=1)
            end_dt = end_dt_obj.isoformat()

            r = requests.post(
                f"https://www.googleapis.com/calendar/v3/calendars/{GOOGLE_CALENDAR_ID}/events",
                params={"key": GOOGLE_CALENDAR_API_KEY},
                json={
                    "summary": title,
                    "description": description,
                    "start": {"dateTime": start_dt, "timeZone": "Europe/Madrid"},
                    "end": {"dateTime": end_dt, "timeZone": "Europe/Madrid"},
                },
                timeout=10,
            )
            if r.ok:
                event["google_id"] = r.json().get("id", "")
                logger.info(f"[Calendar] Google event created: {title}")
        except Exception as e:
            logger.warning(f"[Calendar] Google API error: {e}")

    # Always save locally
    events = _load_events()
    events.append(event)
    _save_events(events)

    logger.info(f"[Calendar] Event created: {title} on {parsed_date} at {parsed_time}")
    return {"ok": True, "event": event}


def get_upcoming_events(days_ahead: int = 7) -> list[dict]:
    """Devuelve eventos de los próximos X días."""
    events = _load_events()
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)

    upcoming = []
    for e in events:
        try:
            event_date = date.fromisoformat(e["date"])
            if today <= event_date <= cutoff and e.get("status") != "cancelled":
                upcoming.append(e)
        except (ValueError, KeyError):
            continue

    # Sort by date and time
    upcoming.sort(key=lambda x: (x.get("date", ""), x.get("time", "")))
    return upcoming


def delete_event(event_id: str) -> bool:
    """Cancela un evento."""
    events = _load_events()
    for e in events:
        if e["id"] == event_id:
            e["status"] = "cancelled"
            _save_events(events)
            return True
    return False


def get_today_events() -> list[dict]:
    """Eventos de hoy."""
    events = _load_events()
    today = date.today().isoformat()
    return [e for e in events if e.get("date") == today and e.get("status") != "cancelled"]
