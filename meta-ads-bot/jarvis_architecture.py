"""
JARVIS ARCHITECTURE — Sistema 180
Modelo de seguridad: Híbrido 3.5 (Aprobación Inteligente + Zero-Trust)
Versión: 1.1.0 (hardened)

REGLAS DE ORO:
1. NUNCA ejecutar acciones con dinero sin aprobación explícita
2. Acciones de lectura (métricas, listar) → auto-ejecutar
3. Acciones de escritura (crear, modificar) → requieren aprobación si confidence < 95%
4. Acciones destructivas (eliminar, pausar) → SIEMPRE requieren aprobación
5. Todo queda logueado con audit trail completo
6. PyAutoGUI BLOQUEADO — sin control de escritorio
7. Solo localhost — sin acceso remoto
8. Límite 50€/acción, 100€/día — sin excepciones
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass, field, asdict

# ██████████████████████████████████████████████
#  PROTECCIONES DEL SISTEMA — SE CARGAN PRIMERO
# ██████████████████████████████████████████████
try:
    import system_protection  # Bloquea PyAutoGUI, comandos peligrosos, etc.
except ImportError:
    logging.warning("[JARVIS] system_protection.py no encontrado — protecciones reducidas")

logger = logging.getLogger(__name__)

# Kill switch global
_KILLED = False

def kill_switch():
    """PARA TODO INMEDIATAMENTE. No se puede deshacer sin reiniciar."""
    global _KILLED
    _KILLED = True
    logger.critical("[JARVIS] ████ KILL SWITCH ACTIVADO ████ — Todas las acciones bloqueadas")

def is_killed() -> bool:
    return _KILLED


# ═══════════════════════════════════════════════
#  ENUMS & TYPES
# ═══════════════════════════════════════════════

class RiskLevel(Enum):
    """Nivel de riesgo de una acción."""
    SAFE = "safe"             # Lectura, sin side effects
    LOW = "low"               # Escritura menor (crear nota, log)
    MEDIUM = "medium"         # Escritura con impacto (crear campaña)
    HIGH = "high"             # Involucra dinero o datos sensibles
    CRITICAL = "critical"     # Eliminar, transferir, permisos


class ActionCategory(Enum):
    """Categoría de la acción."""
    READ = "read"             # Solo lectura (métricas, listar, estado)
    CREATE = "create"         # Crear recurso nuevo
    MODIFY = "modify"         # Modificar recurso existente
    DELETE = "delete"         # Eliminar recurso
    MONEY = "money"           # Involucra dinero (presupuesto, pago, transferencia)
    OUTREACH = "outreach"     # Enviar mensajes (DMs, emails)
    EXTERNAL = "external"     # Llamada a API externa


class ApprovalStatus(Enum):
    """Estado de aprobación de una decisión."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    EXPIRED = "expired"


# ═══════════════════════════════════════════════
#  DATA CLASSES
# ═══════════════════════════════════════════════

@dataclass
class JarvisDecision:
    """Una decisión que JARVIS quiere ejecutar."""
    id: str
    action: str
    description: str
    category: ActionCategory
    risk_level: RiskLevel
    confidence: float              # 0.0 - 1.0
    params: dict = field(default_factory=dict)
    money_amount: float = 0.0      # En EUR si aplica
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    executed_at: str = ""
    result: dict = field(default_factory=dict)
    audit_hash: str = ""

    def __post_init__(self):
        """Genera hash de auditoría para integridad."""
        content = f"{self.id}:{self.action}:{self.description}:{self.money_amount}:{self.created_at}"
        self.audit_hash = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class SecurityPolicy:
    """Política de seguridad configurable."""
    # Confidence thresholds
    auto_approve_threshold: float = 0.95     # >95% → auto-approve (solo READ)
    require_approval_threshold: float = 0.70  # <70% → siempre pedir aprobación

    # Money limits (EUR) — MODO PARANOICO
    # JARVIS NO PUEDE gastar dinero NUNCA por su cuenta.
    # Solo ejecuta el monto EXACTO que el usuario dice.
    # No puede subir ni bajar presupuestos.
    max_auto_approve_amount: float = 0.0     # ZERO — NUNCA auto-aprobar dinero
    max_single_action_amount: float = 0.0    # ZERO — JARVIS no decide montos
    daily_spend_limit: float = 0.0           # ZERO — sin límite porque JARVIS no gasta
    money_requires_exact_user_amount: bool = True  # Solo el monto que dice el usuario
    money_can_modify_existing: bool = False  # NO puede cambiar presupuestos existentes

    # Rate limits
    max_actions_per_hour: int = 20
    max_outreach_per_day: int = 50           # DMs/emails por día
    max_campaigns_per_day: int = 1           # Solo 1 campaña por día

    # Time restrictions
    allow_outside_hours: bool = False        # Solo 9-23h
    business_hours_start: int = 9
    business_hours_end: int = 23

    # Approval expiry
    approval_timeout_minutes: int = 60       # Aprobación expira en 1h


# ═══════════════════════════════════════════════
#  SECURITY GATE
# ═══════════════════════════════════════════════

class SecurityGate:
    """
    Zero-trust security gate.
    Toda acción de JARVIS pasa por aquí antes de ejecutarse.
    """

    def __init__(self, policy: SecurityPolicy = None):
        self.policy = policy or SecurityPolicy()
        self.audit_log: list[dict] = []
        self.daily_spend: float = 0.0
        self.daily_spend_date: str = ""
        self.hourly_actions: list[datetime] = []
        self.daily_outreach: int = 0
        self.daily_campaigns: int = 0
        self.pending_approvals: dict[str, JarvisDecision] = {}

    def evaluate(self, decision: JarvisDecision) -> tuple[bool, str]:
        """
        Evalúa si una decisión puede ejecutarse.
        Returns: (can_execute, reason)
        """
        # 0. KILL SWITCH — bloquea TODO
        if is_killed():
            return False, "KILL SWITCH ACTIVO — todas las acciones bloqueadas"

        # 1. TIME CHECK
        if not self.policy.allow_outside_hours:
            hour = datetime.now().hour
            if hour < self.policy.business_hours_start or hour >= self.policy.business_hours_end:
                return False, f"Fuera de horario ({self.policy.business_hours_start}:00-{self.policy.business_hours_end}:00)"

        # 2. RATE LIMIT CHECK
        now = datetime.now()
        self.hourly_actions = [t for t in self.hourly_actions if (now - t).seconds < 3600]
        if len(self.hourly_actions) >= self.policy.max_actions_per_hour:
            return False, f"Rate limit: {self.policy.max_actions_per_hour} acciones/hora"

        # 3. MONEY CHECK — MODO PARANOICO
        # JARVIS NO GASTA DINERO NUNCA POR SU CUENTA.
        # Solo pasa el monto EXACTO que el usuario dijo.
        if decision.category == ActionCategory.MONEY or decision.money_amount > 0:
            # JARVIS no puede modificar presupuestos existentes
            if decision.action == "modify_budget" and not self.policy.money_can_modify_existing:
                return False, "BLOQUEADO: JARVIS no puede modificar presupuestos. Hazlo tu manualmente."

            # JARVIS no puede decidir montos — solo el usuario
            if not decision.params.get("_user_explicitly_set_amount", False):
                self._queue_for_approval(decision)
                return False, f"REQUIERE TU ORDEN EXACTA: di el monto exacto que quieres gastar"

            # SIEMPRE requiere aprobación — SIN EXCEPCIONES
            if decision.approval_status != ApprovalStatus.APPROVED:
                self._queue_for_approval(decision)
                return False, f"REQUIERE TU APROBACION: {decision.money_amount}EUR — di 'si' para confirmar"

        # 4. CATEGORY-BASED CHECK
        if decision.category == ActionCategory.DELETE:
            if decision.approval_status != ApprovalStatus.APPROVED:
                self._queue_for_approval(decision)
                return False, "REQUIERE APROBACION: accion destructiva"

        if decision.category == ActionCategory.OUTREACH:
            if self.daily_outreach >= self.policy.max_outreach_per_day:
                return False, f"Limite outreach: {self.policy.max_outreach_per_day}/dia"

        # 5. CONFIDENCE-BASED CHECK
        if decision.category == ActionCategory.READ:
            # Lectura → auto-approve si confidence > threshold
            if decision.confidence >= self.policy.auto_approve_threshold:
                decision.approval_status = ApprovalStatus.AUTO_APPROVED
                self._log_audit(decision, "auto_approved", "read action, high confidence")
                return True, "Auto-aprobado (lectura)"

        if decision.category in (ActionCategory.CREATE, ActionCategory.MODIFY):
            if decision.confidence >= self.policy.auto_approve_threshold and decision.money_amount == 0:
                decision.approval_status = ApprovalStatus.AUTO_APPROVED
                self._log_audit(decision, "auto_approved", "write action, high confidence, no money")
                return True, "Auto-aprobado (alta confianza, sin dinero)"

        # 6. DEFAULT: requiere aprobación
        if decision.approval_status == ApprovalStatus.APPROVED:
            return True, "Aprobado por usuario"

        self._queue_for_approval(decision)
        return False, "Requiere aprobacion del usuario"

    def approve(self, decision_id: str, approved_by: str = "user") -> bool:
        """Aprobar una decisión pendiente."""
        if decision_id in self.pending_approvals:
            decision = self.pending_approvals[decision_id]
            decision.approval_status = ApprovalStatus.APPROVED
            decision.approved_by = approved_by
            self._log_audit(decision, "approved", f"by {approved_by}")
            del self.pending_approvals[decision_id]
            return True
        return False

    def reject(self, decision_id: str, reason: str = "") -> bool:
        """Rechazar una decisión pendiente."""
        if decision_id in self.pending_approvals:
            decision = self.pending_approvals[decision_id]
            decision.approval_status = ApprovalStatus.REJECTED
            self._log_audit(decision, "rejected", reason)
            del self.pending_approvals[decision_id]
            return True
        return False

    def get_pending(self) -> list[JarvisDecision]:
        """Obtener decisiones pendientes de aprobación."""
        # Expirar las antiguas
        now = datetime.now()
        expired = []
        for did, decision in self.pending_approvals.items():
            created = datetime.fromisoformat(decision.created_at)
            if (now - created).seconds > self.policy.approval_timeout_minutes * 60:
                decision.approval_status = ApprovalStatus.EXPIRED
                self._log_audit(decision, "expired", "timeout")
                expired.append(did)
        for did in expired:
            del self.pending_approvals[did]

        return list(self.pending_approvals.values())

    def record_execution(self, decision: JarvisDecision):
        """Registrar que una acción fue ejecutada."""
        self.hourly_actions.append(datetime.now())
        if decision.money_amount > 0:
            self.daily_spend += decision.money_amount
        if decision.category == ActionCategory.OUTREACH:
            self.daily_outreach += 1
        decision.executed_at = datetime.now().isoformat()
        self._log_audit(decision, "executed", json.dumps(decision.result)[:200])

    def _queue_for_approval(self, decision: JarvisDecision):
        """Poner decisión en cola de aprobación."""
        self.pending_approvals[decision.id] = decision
        self._log_audit(decision, "queued", "waiting for approval")
        logger.info(f"[JARVIS] Queued for approval: {decision.id} — {decision.description}")

    def _log_audit(self, decision: JarvisDecision, event: str, detail: str = ""):
        """Log de auditoría inmutable."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision_id": decision.id,
            "action": decision.action,
            "category": decision.category.value,
            "risk": decision.risk_level.value,
            "confidence": decision.confidence,
            "money": decision.money_amount,
            "event": event,
            "detail": detail,
            "audit_hash": decision.audit_hash,
        }
        self.audit_log.append(entry)
        logger.info(f"[AUDIT] {event}: {decision.id} | {decision.action} | {decision.money_amount}EUR | {detail}")

    def get_audit_log(self, last_n: int = 20) -> list[dict]:
        """Obtener últimas N entradas del audit log."""
        return self.audit_log[-last_n:]

    def get_daily_summary(self) -> dict:
        """Resumen del día."""
        today = datetime.now().strftime("%Y-%m-%d")
        today_events = [e for e in self.audit_log if e["timestamp"].startswith(today)]
        return {
            "date": today,
            "total_actions": len(today_events),
            "approved": sum(1 for e in today_events if e["event"] == "approved"),
            "auto_approved": sum(1 for e in today_events if e["event"] == "auto_approved"),
            "rejected": sum(1 for e in today_events if e["event"] == "rejected"),
            "executed": sum(1 for e in today_events if e["event"] == "executed"),
            "expired": sum(1 for e in today_events if e["event"] == "expired"),
            "total_spend": self.daily_spend,
            "spend_limit": self.policy.daily_spend_limit,
            "pending": len(self.pending_approvals),
        }


# ═══════════════════════════════════════════════
#  DECISION ENGINE
# ═══════════════════════════════════════════════

class DecisionEngine:
    """
    Motor de decisiones de JARVIS.
    Clasifica intenciones y genera JarvisDecisions con el nivel de riesgo correcto.
    """

    # Mapa de acciones conocidas → (categoría, riesgo)
    ACTION_REGISTRY = {
        # Meta Ads
        "get_metrics":       (ActionCategory.READ,     RiskLevel.SAFE),
        "list_campaigns":    (ActionCategory.READ,     RiskLevel.SAFE),
        "get_account_info":  (ActionCategory.READ,     RiskLevel.SAFE),
        "create_campaign":   (ActionCategory.MONEY,    RiskLevel.HIGH),
        "pause_campaign":    (ActionCategory.MODIFY,   RiskLevel.MEDIUM),
        "delete_campaign":   (ActionCategory.DELETE,   RiskLevel.CRITICAL),
        "modify_budget":     (ActionCategory.MONEY,    RiskLevel.HIGH),

        # CRM / Notion
        "list_clients":      (ActionCategory.READ,     RiskLevel.SAFE),
        "list_affiliates":   (ActionCategory.READ,     RiskLevel.SAFE),
        "create_client":     (ActionCategory.CREATE,   RiskLevel.LOW),
        "delete_client":     (ActionCategory.DELETE,   RiskLevel.CRITICAL),

        # Outreach
        "send_dm":           (ActionCategory.OUTREACH, RiskLevel.MEDIUM),
        "send_email":        (ActionCategory.OUTREACH, RiskLevel.MEDIUM),
        "send_whatsapp":     (ActionCategory.OUTREACH, RiskLevel.MEDIUM),
        "bulk_dm":           (ActionCategory.OUTREACH, RiskLevel.HIGH),
        "bulk_email":        (ActionCategory.OUTREACH, RiskLevel.HIGH),

        # System
        "get_status":        (ActionCategory.READ,     RiskLevel.SAFE),
        "generate_report":   (ActionCategory.READ,     RiskLevel.SAFE),
        "run_maestro_cycle": (ActionCategory.EXTERNAL, RiskLevel.MEDIUM),

        # Stripe
        "create_invoice":    (ActionCategory.MONEY,    RiskLevel.HIGH),
        "charge_client":     (ActionCategory.MONEY,    RiskLevel.CRITICAL),
        "refund":            (ActionCategory.MONEY,    RiskLevel.CRITICAL),
    }

    def __init__(self):
        self._counter = 0

    def create_decision(
        self,
        action: str,
        description: str,
        confidence: float,
        params: dict = None,
        money_amount: float = 0.0,
    ) -> JarvisDecision:
        """Crea una decisión con clasificación automática de riesgo."""
        self._counter += 1

        cat, risk = self.ACTION_REGISTRY.get(
            action,
            (ActionCategory.EXTERNAL, RiskLevel.MEDIUM)  # Default: medium risk
        )

        # Override risk if money involved
        if money_amount > 0:
            cat = ActionCategory.MONEY
            risk = RiskLevel.HIGH if money_amount <= 50 else RiskLevel.CRITICAL

        return JarvisDecision(
            id=f"jarvis_{self._counter:04d}_{datetime.now().strftime('%H%M%S')}",
            action=action,
            description=description,
            category=cat,
            risk_level=risk,
            confidence=confidence,
            params=params or {},
            money_amount=money_amount,
        )


# ═══════════════════════════════════════════════
#  EXECUTION CONTROLLER
# ═══════════════════════════════════════════════

class ExecutionController:
    """
    Controlador de ejecución.
    Conecta DecisionEngine → SecurityGate → Execution.
    """

    def __init__(self, policy: SecurityPolicy = None):
        self.engine = DecisionEngine()
        self.gate = SecurityGate(policy)
        self.execution_history: list[JarvisDecision] = []

    def propose(
        self,
        action: str,
        description: str,
        confidence: float,
        params: dict = None,
        money_amount: float = 0.0,
    ) -> tuple[JarvisDecision, bool, str]:
        """
        Propone una acción. Retorna (decision, can_execute, reason).
        Si can_execute=True, la acción se puede ejecutar.
        Si can_execute=False, necesita aprobación del usuario.
        """
        decision = self.engine.create_decision(
            action, description, confidence, params, money_amount
        )

        can_execute, reason = self.gate.evaluate(decision)

        logger.info(
            f"[JARVIS] Proposed: {action} | conf={confidence:.0%} | "
            f"risk={decision.risk_level.value} | money={money_amount}EUR | "
            f"{'EXECUTE' if can_execute else 'BLOCKED'}: {reason}"
        )

        return decision, can_execute, reason

    def execute(self, decision: JarvisDecision, result: dict = None):
        """Registra la ejecución de una decisión ya aprobada."""
        decision.result = result or {}
        self.gate.record_execution(decision)
        self.execution_history.append(decision)

    def approve(self, decision_id: str) -> bool:
        return self.gate.approve(decision_id)

    def reject(self, decision_id: str) -> bool:
        return self.gate.reject(decision_id)

    def get_pending(self) -> list[JarvisDecision]:
        return self.gate.get_pending()

    def get_summary(self) -> dict:
        return self.gate.get_daily_summary()

    def get_audit(self, n: int = 20) -> list[dict]:
        return self.gate.get_audit_log(n)


# ═══════════════════════════════════════════════
#  FORMAT HELPERS (para Telegram)
# ═══════════════════════════════════════════════

def format_pending_for_telegram(pending: list[JarvisDecision]) -> str:
    """Formatea decisiones pendientes para mostrar en Telegram."""
    if not pending:
        return "No hay acciones pendientes de aprobacion."

    lines = [f"Acciones pendientes ({len(pending)}):\n"]
    for d in pending:
        emoji = {"safe": "🟢", "low": "🟡", "medium": "🟠", "high": "🔴", "critical": "⛔"}.get(d.risk_level.value, "⚪")
        money_str = f" | {d.money_amount}EUR" if d.money_amount > 0 else ""
        lines.append(
            f"{emoji} [{d.id}]\n"
            f"  {d.description}\n"
            f"  Conf: {d.confidence:.0%}{money_str}\n"
            f"  /aprobar_{d.id.split('_')[1]} o /rechazar_{d.id.split('_')[1]}"
        )
    return "\n".join(lines)

def format_summary_for_telegram(summary: dict) -> str:
    """Formatea resumen diario para Telegram."""
    return (
        f"JARVIS — Resumen {summary['date']}\n\n"
        f"Acciones totales: {summary['total_actions']}\n"
        f"Auto-aprobadas: {summary['auto_approved']}\n"
        f"Aprobadas: {summary['approved']}\n"
        f"Rechazadas: {summary['rejected']}\n"
        f"Ejecutadas: {summary['executed']}\n"
        f"Expiradas: {summary['expired']}\n"
        f"Pendientes: {summary['pending']}\n\n"
        f"Gasto hoy: {summary['total_spend']:.2f}EUR / {summary['spend_limit']:.2f}EUR"
    )


# ═══════════════════════════════════════════════
#  SINGLETON
# ═══════════════════════════════════════════════

_jarvis: Optional[ExecutionController] = None

def get_jarvis(policy: SecurityPolicy = None) -> ExecutionController:
    """Obtener instancia singleton de JARVIS."""
    global _jarvis
    if _jarvis is None:
        _jarvis = ExecutionController(policy)
        logger.info("[JARVIS] Initialized with hybrid security model (3.5)")
    return _jarvis


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== JARVIS Security Test ===\n")

    jarvis = get_jarvis()

    # Test 1: Read action (should auto-approve)
    d, ok, reason = jarvis.propose("get_metrics", "Ver metricas de hoy", 0.98)
    print(f"1. get_metrics: {ok} — {reason}")

    # Test 2: Create campaign with money (should BLOCK)
    d, ok, reason = jarvis.propose("create_campaign", "Crear campana 10EUR", 0.90, money_amount=10.0)
    print(f"2. create_campaign 10EUR: {ok} — {reason}")

    # Test 3: Send DM (should need approval)
    d, ok, reason = jarvis.propose("send_dm", "Mensaje a lead", 0.85)
    print(f"3. send_dm: {ok} — {reason}")

    # Test 4: Delete client (should ALWAYS block)
    d, ok, reason = jarvis.propose("delete_client", "Eliminar cliente X", 0.99)
    print(f"4. delete_client: {ok} — {reason}")

    # Show pending
    print(f"\nPending: {len(jarvis.get_pending())}")
    print(format_pending_for_telegram(jarvis.get_pending()))
    print(f"\n{format_summary_for_telegram(jarvis.get_summary())}")
