"""
resilience.py — Sistema 180
Retry logic, circuit breaker, metrics collection, and auto-alerting.
Designed for 50/50 production-grade reliability.
"""
import time, threading, logging, os
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# RETRY WITH EXPONENTIAL BACKOFF
# ══════════════════════════════════════════════════════════════════════════════

def retry(max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 30.0,
          exceptions: tuple = (Exception,)):
    """Decorator: retries function with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts:
                        logger.error(f"[Retry] {func.__name__} failed after {max_attempts} attempts: {e}")
                        metrics.record_error(func.__name__, str(e))
                        raise
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(f"[Retry] {func.__name__} attempt {attempt}/{max_attempts} failed: {e}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


# ══════════════════════════════════════════════════════════════════════════════
# CIRCUIT BREAKER
# ══════════════════════════════════════════════════════════════════════════════

class CircuitBreaker:
    """Prevents cascading failures by temporarily disabling failing services."""

    CLOSED = "closed"      # normal operation
    OPEN = "open"          # service down, skip calls
    HALF_OPEN = "half_open"  # testing if service recovered

    def __init__(self, name: str, failure_threshold: int = 5,
                 recovery_timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.CLOSED
        self.failures = 0
        self.last_failure_time = 0
        self._lock = threading.Lock()

    def can_execute(self) -> bool:
        with self._lock:
            if self.state == self.CLOSED:
                return True
            if self.state == self.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = self.HALF_OPEN
                    logger.info(f"[CircuitBreaker] {self.name}: OPEN -> HALF_OPEN")
                    return True
                return False
            return True  # HALF_OPEN: allow one test

    def record_success(self):
        with self._lock:
            if self.state == self.HALF_OPEN:
                self.state = self.CLOSED
                self.failures = 0
                logger.info(f"[CircuitBreaker] {self.name}: HALF_OPEN -> CLOSED (recovered)")

    def record_failure(self):
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = self.OPEN
                logger.warning(f"[CircuitBreaker] {self.name}: OPEN (failures={self.failures})")
                metrics.record_error("circuit_breaker", f"{self.name} OPEN")

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state,
            "failures": self.failures,
        }


# Global circuit breakers for external services
cb_notion = CircuitBreaker("notion", failure_threshold=5, recovery_timeout=60)
cb_slack = CircuitBreaker("slack", failure_threshold=5, recovery_timeout=60)
cb_claude = CircuitBreaker("claude", failure_threshold=3, recovery_timeout=120)
cb_instagram = CircuitBreaker("instagram", failure_threshold=3, recovery_timeout=300)


# ══════════════════════════════════════════════════════════════════════════════
# METRICS COLLECTOR
# ══════════════════════════════════════════════════════════════════════════════

class MetricsCollector:
    """Collects operational metrics for monitoring."""

    def __init__(self):
        self._lock = threading.Lock()
        self._api_calls: dict[str, int] = defaultdict(int)
        self._api_errors: dict[str, int] = defaultdict(int)
        self._api_latency: dict[str, list[float]] = defaultdict(list)
        self._commands: dict[str, int] = defaultdict(int)
        self._errors: list[dict] = []
        self._start_time = time.time()

    def record_api_call(self, service: str, latency_ms: float = 0, success: bool = True):
        with self._lock:
            self._api_calls[service] += 1
            if latency_ms > 0:
                self._api_latency[service].append(latency_ms)
                # Keep only last 100
                if len(self._api_latency[service]) > 100:
                    self._api_latency[service] = self._api_latency[service][-100:]
            if not success:
                self._api_errors[service] += 1

    def record_command(self, command: str):
        with self._lock:
            self._commands[command] += 1

    def record_error(self, source: str, error: str):
        with self._lock:
            self._errors.append({
                "ts": datetime.utcnow().isoformat(),
                "source": source,
                "error": error[:200],
            })
            # Keep only last 50 errors
            if len(self._errors) > 50:
                self._errors = self._errors[-50:]

    def get_metrics(self) -> dict:
        with self._lock:
            uptime = int(time.time() - self._start_time)
            
            # Calculate avg latencies
            avg_latencies = {}
            for svc, lats in self._api_latency.items():
                if lats:
                    avg_latencies[svc] = round(sum(lats) / len(lats), 1)

            # Error rates
            error_rates = {}
            for svc, calls in self._api_calls.items():
                errors = self._api_errors.get(svc, 0)
                rate = (errors / max(calls, 1)) * 100
                error_rates[svc] = f"{rate:.1f}%"

            return {
                "uptime_seconds": uptime,
                "api_calls": dict(self._api_calls),
                "api_errors": dict(self._api_errors),
                "avg_latency_ms": avg_latencies,
                "error_rates": error_rates,
                "commands_used": dict(self._commands),
                "recent_errors": self._errors[-5:],
                "circuit_breakers": {
                    "notion": cb_notion.get_status(),
                    "slack": cb_slack.get_status(),
                    "claude": cb_claude.get_status(),
                    "instagram": cb_instagram.get_status(),
                },
            }

    def get_health_summary(self) -> str:
        """Human-readable health summary for Telegram."""
        m = self.get_metrics()
        lines = [
            "📊 *Sistema 180 — Métricas*\n",
            f"⏱ Uptime: {m['uptime_seconds'] // 3600}h {(m['uptime_seconds'] % 3600) // 60}m",
            "\n📡 *API Calls:*",
        ]
        for svc, count in m["api_calls"].items():
            err = m["api_errors"].get(svc, 0)
            lat = m["avg_latency_ms"].get(svc, "?")
            emoji = "✅" if err == 0 else "⚠️"
            lines.append(f"  {emoji} {svc}: {count} calls | {err} errors | avg {lat}ms")

        lines.append("\n🔌 *Circuit Breakers:*")
        for name, cb in m["circuit_breakers"].items():
            state_emoji = {"closed": "🟢", "open": "🔴", "half_open": "🟡"}.get(cb["state"], "⚪")
            lines.append(f"  {state_emoji} {name}: {cb['state']} ({cb['failures']} failures)")

        if m["recent_errors"]:
            lines.append("\n❌ *Últimos errores:*")
            for e in m["recent_errors"][-3:]:
                lines.append(f"  • {e['source']}: {e['error'][:60]}")

        return "\n".join(lines)


# Global singleton
metrics = MetricsCollector()


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-ALERTING
# ══════════════════════════════════════════════════════════════════════════════

class AutoAlerter:
    """Sends Slack alerts when error thresholds are exceeded."""

    def __init__(self, error_threshold: int = 10, check_interval: int = 300):
        self.error_threshold = error_threshold
        self.check_interval = check_interval
        self._last_alert_time = 0
        self._alert_cooldown = 600  # 10 min between alerts

    def start(self):
        """Start background alerting thread."""
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()
        logger.info("[Alerter] Auto-alerting started")

    def _loop(self):
        while True:
            time.sleep(self.check_interval)
            try:
                self._check()
            except Exception as e:
                logger.error(f"[Alerter] Error: {e}")

    def _check(self):
        m = metrics.get_metrics()
        total_errors = sum(m["api_errors"].values())
        
        # Check circuit breakers
        open_cbs = [name for name, cb in m["circuit_breakers"].items() if cb["state"] == "open"]
        
        should_alert = (
            total_errors > self.error_threshold or
            len(open_cbs) > 0
        )

        if should_alert and time.time() - self._last_alert_time > self._alert_cooldown:
            self._send_alert(total_errors, open_cbs)
            self._last_alert_time = time.time()

    def _send_alert(self, total_errors: int, open_cbs: list):
        """Send alert to Slack."""
        try:
            import requests
            slack_token = os.getenv("SLACK_BOT_TOKEN", "")
            slack_channel = os.getenv("SLACK_CHANNEL_ID", "")
            if not slack_token or not slack_channel:
                return
            
            msg = (
                "🚨 *ALERTA SISTEMA 180*\n\n"
                f"Errores totales: {total_errors}\n"
            )
            if open_cbs:
                msg += f"Circuit breakers ABIERTOS: {', '.join(open_cbs)}\n"
            msg += f"\nTimestamp: {datetime.utcnow().isoformat()}"

            requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {slack_token}"},
                json={"channel": slack_channel, "text": msg},
                timeout=5
            )
            logger.warning(f"[Alerter] Alert sent: {total_errors} errors, open CBs: {open_cbs}")
        except Exception as e:
            logger.error(f"[Alerter] Failed to send alert: {e}")


# Global alerter
alerter = AutoAlerter()
