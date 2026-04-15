"""
gmail_ops.py — Sistema 180
Gmail API integration: leer emails, clasificar, generar borradores.
OAuth2 flow. GDPR compliant — solo negocios con email público/formulario.
"""

import os
import json
import base64
import logging
from datetime import datetime
from typing import Optional
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

# ─── Optional Google API deps (graceful degradation) ───
GMAIL_AVAILABLE = False
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request as GoogleRequest
    GMAIL_AVAILABLE = True
except ImportError:
    logger.warning(
        "google-auth-oauthlib or google-api-python-client not installed. "
        "Gmail features disabled. Run: pip install google-auth-oauthlib google-api-python-client"
    )

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "gmail_credentials.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "gmail_token.json")

# OAuth redirect URI — must match Google Cloud Console setting
REDIRECT_URI = os.getenv(
    "GMAIL_REDIRECT_URI",
    "https://sistema-180-meta-ads-production.up.railway.app/gmail/callback"
)

# Build credentials file from env vars if not present on disk
def _ensure_credentials_file():
    """Create gmail_credentials.json from env vars if the file doesn't exist."""
    if os.path.exists(CREDENTIALS_FILE):
        return True
    client_id = os.getenv("GMAIL_CLIENT_ID", "")
    client_secret = os.getenv("GMAIL_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        logger.warning("GMAIL_CLIENT_ID/SECRET not set and gmail_credentials.json not found.")
        return False
    creds_data = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    try:
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(creds_data, f)
        logger.info("gmail_credentials.json creado desde env vars.")
        return True
    except Exception as e:
        logger.error(f"Failed to write gmail_credentials.json: {e}")
        return False

# Pending Telegram approval: lead_id -> draft dict
# (Shared with bot.py via module state; in production use Redis/DB)
_pending_send_approvals: dict[int, dict] = {}


# ─────────────────────────────────────────────────────────────────────────────
# GmailClient
# ─────────────────────────────────────────────────────────────────────────────

class GmailClient:
    """
    Gmail OAuth2 client.
    Credentials stored in gmail_token.json.
    Requires gmail_credentials.json (Google Cloud Console → OAuth 2.0 client).
    """

    def __init__(self):
        self._credentials: Optional["Credentials"] = None
        self._service = None
        self._authenticated_email: str = ""

    # ─── OAuth flow ───

    def get_auth_url(self) -> str:
        """Return OAuth URL for user to visit in browser."""
        if not GMAIL_AVAILABLE:
            raise RuntimeError("Gmail packages not installed")
        if not _ensure_credentials_file():
            raise FileNotFoundError(
                "gmail_credentials.json not found and GMAIL_CLIENT_ID/SECRET env vars not set. "
                "Set them in Railway or download credentials from Google Cloud Console."
            )
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        # Store flow state for exchange_code
        self._flow = flow
        return auth_url

    def exchange_code(self, code: str) -> bool:
        """Complete OAuth, save tokens to gmail_token.json."""
        if not GMAIL_AVAILABLE:
            raise RuntimeError("Gmail packages not installed")
        if not hasattr(self, "_flow") or not self._flow:
            # Re-create flow for stateless exchange (e.g. after server restart)
            _ensure_credentials_file()
            flow = Flow.from_client_secrets_file(
                CREDENTIALS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI,
            )
        else:
            flow = self._flow

        flow.fetch_token(code=code)
        creds = flow.credentials
        self._save_token(creds)
        self._credentials = creds
        self._service = None  # Force rebuild
        logger.info("Gmail OAuth completed. Token saved.")
        return True

    def _save_token(self, creds):
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    def _load_credentials(self) -> Optional["Credentials"]:
        if not GMAIL_AVAILABLE:
            return None
        if not os.path.exists(TOKEN_FILE):
            return None
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(GoogleRequest())
                self._save_token(creds)
                logger.info("Gmail token refreshed.")
            return creds
        except Exception as e:
            logger.error(f"Failed to load Gmail credentials: {e}")
            return None

    def is_authenticated(self) -> bool:
        creds = self._credentials or self._load_credentials()
        return bool(creds and creds.valid)

    def _get_service(self):
        if self._service:
            return self._service
        creds = self._credentials or self._load_credentials()
        if not creds or not creds.valid:
            raise RuntimeError("Gmail not authenticated. Call get_auth_url() first.")
        self._credentials = creds
        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def _get_authenticated_email(self) -> str:
        if self._authenticated_email:
            return self._authenticated_email
        try:
            svc = self._get_service()
            profile = svc.users().getProfile(userId="me").execute()
            self._authenticated_email = profile.get("emailAddress", "")
        except Exception:
            self._authenticated_email = ""
        return self._authenticated_email

    # ─── Gmail operations ───

    def fetch_unread(self, limit: int = 20) -> list[dict]:
        """
        Fetch unread emails from inbox.
        Returns list of {id, from_email, from_name, subject, body_text, date}
        """
        svc = self._get_service()
        results = svc.users().messages().list(
            userId="me",
            labelIds=["INBOX", "UNREAD"],
            maxResults=limit,
        ).execute()

        messages = results.get("messages", [])
        emails = []
        for msg in messages:
            try:
                parsed = self._parse_message(svc, msg["id"])
                if parsed:
                    emails.append(parsed)
            except Exception as e:
                logger.warning(f"Failed to parse message {msg['id']}: {e}")
        return emails

    def _parse_message(self, svc, msg_id: str) -> Optional[dict]:
        msg = svc.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
        from_raw = headers.get("from", "")
        subject = headers.get("subject", "(sin asunto)")
        date_str = headers.get("date", "")

        # Parse "From: Name <email>" or just "email"
        from_name, from_email = _parse_from_header(from_raw)

        body_text = _extract_body(msg.get("payload", {}))

        return {
            "id": msg_id,
            "from_email": from_email,
            "from_name": from_name,
            "subject": subject,
            "body_text": body_text[:2000],  # Limit for processing
            "date": date_str,
        }

    def mark_as_read(self, msg_id: str):
        svc = self._get_service()
        svc.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()
        logger.info(f"Gmail: marked {msg_id} as read")

    def send_email(self, to: str, subject: str, body: str) -> dict:
        """Send email via Gmail API."""
        svc = self._get_service()
        from_email = self._get_authenticated_email()
        raw = _build_raw_email(from_email, to, subject, body)
        result = svc.users().messages().send(
            userId="me",
            body={"raw": raw},
        ).execute()
        logger.info(f"Gmail: sent email to {to}, message_id={result.get('id')}")
        return {"ok": True, "message_id": result.get("id")}

    def create_draft(self, to: str, subject: str, body: str) -> dict:
        """Create a draft (safer — needs human approval before sending)."""
        svc = self._get_service()
        from_email = self._get_authenticated_email()
        raw = _build_raw_email(from_email, to, subject, body)
        result = svc.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw}},
        ).execute()
        logger.info(f"Gmail: draft created for {to}, draft_id={result.get('id')}")
        return {"ok": True, "draft_id": result.get("id")}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_from_header(from_raw: str) -> tuple[str, str]:
    """Parse 'Name <email@example.com>' or 'email@example.com'."""
    import re
    match = re.match(r'^"?([^"<]*?)"?\s*<([^>]+)>', from_raw.strip())
    if match:
        return match.group(1).strip(), match.group(2).strip()
    # Just an email
    email = from_raw.strip().strip("<>")
    return "", email


def _extract_body(payload: dict) -> str:
    """Recursively extract plain text body from Gmail message payload."""
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data", "")

    if mime_type == "text/plain" and body_data:
        return base64.urlsafe_b64decode(body_data + "==").decode("utf-8", errors="replace")

    # Multipart: recurse into parts
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text:
            return text

    return ""


def _build_raw_email(from_email: str, to: str, subject: str, body: str) -> str:
    """Build base64url-encoded RFC 2822 email."""
    import email.mime.text
    msg = email.mime.text.MIMEText(body, "plain", "utf-8")
    msg["From"] = from_email
    msg["To"] = to
    msg["Subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return raw


# ─────────────────────────────────────────────────────────────────────────────
# Flask Blueprint
# ─────────────────────────────────────────────────────────────────────────────

gmail_bp = Blueprint("gmail", __name__, url_prefix="/gmail")

# Module-level client instance (shared across requests)
_gmail_client = GmailClient()


def _get_revenue_ops():
    """Lazy import to avoid circular deps."""
    from revenue_ops import get_revenue_ops
    return get_revenue_ops()


@gmail_bp.route("/auth", methods=["GET"])
def gmail_auth():
    """GET /gmail/auth — returns {url: auth_url}"""
    if not GMAIL_AVAILABLE:
        return jsonify({"error": "Gmail packages not installed. Run: pip install google-auth-oauthlib google-api-python-client"}), 503
    try:
        url = _gmail_client.get_auth_url()
        return jsonify({"url": url})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Gmail auth error: {e}")
        return jsonify({"error": "Internal error"}), 500


@gmail_bp.route("/callback", methods=["GET"])
def gmail_callback():
    """GET /gmail/callback?code=X — exchanges OAuth code"""
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing code parameter"}), 400
    try:
        _gmail_client.exchange_code(code)
        return jsonify({"ok": True, "message": "Gmail autenticado correctamente."})
    except Exception as e:
        logger.error(f"Gmail callback error: {e}")
        return jsonify({"error": str(e)}), 400


@gmail_bp.route("/status", methods=["GET"])
def gmail_status():
    """GET /gmail/status — {authenticated: bool, email: str}"""
    authenticated = _gmail_client.is_authenticated()
    email = _gmail_client._get_authenticated_email() if authenticated else ""
    return jsonify({"authenticated": authenticated, "email": email})


@gmail_bp.route("/inbox", methods=["GET"])
def gmail_inbox():
    """GET /gmail/inbox — fetches + classifies unread emails"""
    if not GMAIL_AVAILABLE:
        return jsonify({"error": "Gmail not available"}), 503
    if not _gmail_client.is_authenticated():
        return jsonify({"error": "Gmail not authenticated. Call /gmail/auth first."}), 401

    try:
        db, classifier, copywriter, followup, reporter, gmail_ops = _get_revenue_ops()
        emails = _gmail_client.fetch_unread(limit=20)

        processed = []
        for email_data in emails:
            from_email = email_data["from_email"]

            # GDPR: skip do-not-contact
            if db.is_do_not_contact(from_email):
                continue

            result = gmail_ops.add_email_lead(
                from_email=from_email,
                from_name=email_data["from_name"],
                subject=email_data["subject"],
                body=email_data["body_text"],
            )

            if result.get("lead_id"):
                _gmail_client.mark_as_read(email_data["id"])

            processed.append({
                **email_data,
                "lead_id": result.get("lead_id"),
                "classification": result.get("classification"),
                "skipped": result.get("skipped"),
            })

        return jsonify({"emails": processed, "count": len(processed)})
    except Exception as e:
        logger.error(f"Gmail inbox error: {e}", exc_info=True)
        return jsonify({"error": "Internal error"}), 500


@gmail_bp.route("/draft", methods=["POST"])
def gmail_draft():
    """POST /gmail/draft body={lead_id} — generate AI draft"""
    data = request.get_json() or {}
    lead_id = data.get("lead_id")
    if not lead_id:
        return jsonify({"error": "lead_id required"}), 400

    try:
        db, classifier, copywriter, followup, reporter, gmail_ops = _get_revenue_ops()
        draft = gmail_ops.draft_reply(int(lead_id))
        if not draft:
            return jsonify({"error": f"Lead {lead_id} not found"}), 404

        # Store for approval (in-memory; bot.py reads this)
        _pending_send_approvals[int(lead_id)] = draft
        return jsonify({"draft": draft, "lead_id": lead_id})
    except Exception as e:
        logger.error(f"Gmail draft error: {e}", exc_info=True)
        return jsonify({"error": "Internal error"}), 500


@gmail_bp.route("/send", methods=["POST"])
def gmail_send():
    """
    POST /gmail/send body={lead_id, subject, body}
    REQUIRES prior /gmail/draft call for this lead_id (approval gate).
    Logs all sends. GDPR compliant.
    """
    if not GMAIL_AVAILABLE:
        return jsonify({"error": "Gmail not available"}), 503
    if not _gmail_client.is_authenticated():
        return jsonify({"error": "Gmail not authenticated"}), 401

    data = request.get_json() or {}
    lead_id = data.get("lead_id")
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()

    if not lead_id or not subject or not body:
        return jsonify({"error": "lead_id, subject, body required"}), 400

    lead_id = int(lead_id)

    # Approval gate: draft must have been generated first
    if lead_id not in _pending_send_approvals:
        return jsonify({
            "error": "Draft not found. Call /gmail/draft first, then approve via Telegram /send_email."
        }), 403

    try:
        db, *_ = _get_revenue_ops()
        lead = db.get_lead(lead_id)
        if not lead:
            return jsonify({"error": "Lead not found"}), 404

        to_email = lead.get("email")
        if not to_email:
            return jsonify({"error": "Lead has no email"}), 400

        # GDPR: final check
        if db.is_do_not_contact(to_email):
            return jsonify({"error": "Lead is on do-not-contact list"}), 403

        result = _gmail_client.send_email(to_email, subject, body)

        # Update lead status
        db.update_lead(
            lead_id,
            last_contact=datetime.utcnow().isoformat(),
            status="followup",
        )

        # Clear approval
        _pending_send_approvals.pop(lead_id, None)

        logger.info(f"Email sent to lead {lead_id} ({to_email}): {subject}")
        return jsonify({"ok": True, "to": to_email, "message_id": result.get("message_id")})

    except Exception as e:
        logger.error(f"Gmail send error: {e}", exc_info=True)
        return jsonify({"error": "Internal error"}), 500


def get_pending_approvals() -> dict:
    """Expose pending approvals for bot.py to read."""
    return _pending_send_approvals


def get_gmail_client() -> GmailClient:
    return _gmail_client
