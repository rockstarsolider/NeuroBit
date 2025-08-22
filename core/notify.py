# core/notify.py
from __future__ import annotations

import logging
import os
import re
from typing import Iterable, List, Optional

import requests
from django.conf import settings
from django.db import models, transaction
from django.template import Context, Template
from django.utils import timezone

try:
    # jdatetime is in requirements; we use it to render Shamsi text like "1404-mordad-13"
    from jdatetime import datetime as jdt
except Exception:  # pragma: no cover
    jdt = None  # graceful fallback if missing; you can plug your own converter

log = logging.getLogger(__name__)

# ------------------------------------------------------------
# Helpers: Jalali formatting & phone normalization
# ------------------------------------------------------------

_PERSIAN_MONTHS_LATIN = [
    "farvardin", "ordibehesht", "khordad", "tir", "mordad", "shahrivar",
    "mehr", "aban", "azar", "dey", "bahman", "esfand",
]

def to_jalali_text(dt) -> str:
    """Return 'YYYY-mordad-DD' (e.g., 1404-mordad-13)."""
    if not dt or not jdt:
        return "-"
    j = jdt.fromgregorian(datetime=dt)
    month = _PERSIAN_MONTHS_LATIN[j.month - 1]
    return f"{j.year}-{month}-{j.day:02d}"

_MSISDN_RE = re.compile(r"[^\d+]")

def normalize_msisdn(raw: str) -> Optional[str]:
    """Normalize a phone to Iranian national format starting with '0', or return None."""
    if not raw:
        return None
    s = _MSISDN_RE.sub("", str(raw))
    # Accept formats: 09xxxxxxxxx, +989xxxxxxxxx, 989xxxxxxxxx, 00989xxxxxxxxx
    if s.startswith("+98"):
        s = "0" + s[3:]
    elif s.startswith("0098"):
        s = "0" + s[4:]
    elif s.startswith("98"):
        s = "0" + s[2:]
    # Ensure it's 11 digits starting with 0 (mobile)
    if len(s) == 11 and s.startswith("0"):
        return s
    # If it's already comma-separated multi-recipients
    if "," in raw:
        nums = [normalize_msisdn(x) for x in raw.split(",")]
        nums = [x for x in nums if x]
        return ",".join(nums) if nums else None
    return None

def coerce_recipients(recipients: Iterable[str]) -> Optional[str]:
    """Join recipients as Kavenegar 'receptor' (comma-separated) after normalization."""
    out: List[str] = []
    for r in recipients:
        n = normalize_msisdn(r)
        if n:
            out.extend(n.split(","))  # handle if 'n' already a comma list
    return ",".join(sorted(set(out))) if out else None

# ------------------------------------------------------------
# Admin-editable Config (singleton)
# ------------------------------------------------------------

class SubscriptionNotificationConfig(models.Model):
    """
    Singleton config to control SMS notifications (editable in Admin).
    """
    enable_user_sms = models.BooleanField(default=True)
    enable_manager_sms = models.BooleanField(default=True)

    # List of manager phone numbers; editable in Admin
    manager_phones = models.JSONField(default=list, blank=True,
                                      help_text="List of manager phone numbers (e.g., 09xxxxxxxxx).")

    # Templates are editable; we also support environment defaults on first bootstrap.
    user_sms_template = models.TextField(
        default="اشتراک شما تا {{ end_jalali }} بوده و اکنون منقضی شده است. برای تمدید اقدام کنید."
    )
    manager_sms_template = models.TextField(
        default="اشتراک کاربر {{ user.get_full_name }} (تا {{ end_jalali }}) منقضی شد."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscription Notifications"
        verbose_name_plural = "Subscription Notifications"

    def __str__(self) -> str:  # pragma: no cover
        return "Subscription Notifications"

    # ---- Singleton accessors ----
    @classmethod
    def load(cls) -> "SubscriptionNotificationConfig":
        """
        Get or create the singleton row.
        On first creation, bootstrap values from environment:
          - KAVENEGAR_MANAGERS -> manager_phones
          - SMS_TEMPLATE_USER_EXPIRED -> user_sms_template
          - SMS_TEMPLATE_MANAGER_EXPIRED -> manager_sms_template
        """
        with transaction.atomic():
            obj = cls.objects.first()
            if obj:
                return obj

            managers_env = os.getenv("KAVENEGAR_MANAGERS", "")
            managers = [m.strip() for m in managers_env.split(",") if m.strip()]
            normalized = coerce_recipients(managers)
            manager_list = normalized.split(",") if normalized else []

            user_tpl_env = os.getenv(
                "SMS_TEMPLATE_USER_EXPIRED",
                "اشتراک شما تا {{ end_jalali }} بوده و اکنون منقضی شده است. برای تمدید اقدام کنید.",
            )
            mgr_tpl_env = os.getenv(
                "SMS_TEMPLATE_MANAGER_EXPIRED",
                "اشتراک کاربر {{ user.get_full_name }} (تا {{ end_jalali }}) منقضی شد.",
            )
            obj = cls.objects.create(
                manager_phones=manager_list,
                user_sms_template=user_tpl_env,
                manager_sms_template=mgr_tpl_env,
            )
            return obj

# ------------------------------------------------------------
# Kavenegar client (safe, logged, timeouts)
# ------------------------------------------------------------

def _get_api_key() -> Optional[str]:
    return getattr(settings, "KAVENEGAR_API_KEY", None) or os.getenv("KAVENEGAR_API_KEY")

def _get_sender() -> Optional[str]:
    return getattr(settings, "KAVENEGAR_SENDER", None) or os.getenv("KAVENEGAR_SENDER") or "1000100175"

def kavenegar_send_sms(to_receptors: Iterable[str] | str, message: str) -> bool:
    """
    Send SMS via Kavenegar.
    - to_receptors: iterable of numbers or a single comma-separated string.
    - returns True if the HTTP call was attempted and succeeded (HTTP 200).
    """
    api_key = _get_api_key()
    sender = _get_sender()
    if not api_key or not sender:
        log.warning("SMS disabled: missing KAVENEGAR_API_KEY or KAVENEGAR_SENDER.")
        return False

    if isinstance(to_receptors, str):
        receptor = coerce_recipients([to_receptors])
    else:
        receptor = coerce_recipients(to_receptors)

    if not receptor:
        log.info("SMS skipped: no valid recipients after normalization.")
        return False

    url = f"https://api.kavenegar.com/v1/{api_key}/sms/send.json"
    try:
        resp = requests.post(
            url,
            data={"receptor": receptor, "sender": sender, "message": message},
            timeout=10,
        )
        ok = resp.status_code == 200
        if not ok:
            log.error("Kavenegar non-200: %s %s", resp.status_code, resp.text[:300])
        return ok
    except Exception as e:  # pragma: no cover
        log.exception("Kavenegar error: %s", e)
        return False

# ------------------------------------------------------------
# Public API used by models/views: send_subscription_expired_sms
# ------------------------------------------------------------

def _render_template(tpl: str, ctx: dict) -> str:
    try:
        return Template(tpl).render(Context(ctx))
    except Exception as e:  # pragma: no cover
        log.exception("Template render error: %s", e)
        return tpl  # best-effort fallback

def _extract_user_and_phone(subscription) -> tuple[Optional[object], Optional[str]]:
    """
    Try to find the learner's user and a phone-like field.
    Adjust paths here if your user/learner schema differs.
    """
    user = None
    phone = None
    enrol = getattr(subscription, "learner_enrolment", None)
    learner = getattr(enrol, "learner", None)
    if learner and hasattr(learner, "user"):
        user = learner.user

    # probe common phone attributes on learner first, then user
    for obj in (learner, user):
        for attr in ("phone_number", "mobile", "phone", "msisdn"):
            if obj and hasattr(obj, attr):
                phone = getattr(obj, attr)
                if phone:
                    break
        if phone:
            break

    # fallback: username if it's a phone-like number
    if not phone and user and getattr(user, "username", "") and user.username.isdigit():
        phone = user.username

    return user, normalize_msisdn(phone) if phone else None

def send_subscription_expired_sms(subscription) -> None:
    """
    Main entrypoint. Call this when a subscription transitions to EXPIRED.
    - Auto-bootstraps admin config on first use (populates manager list/templates from env).
    - Renders templates with a simple Django Template context.
    - Sends to user (if enabled + phone exists) and to managers (if enabled + numbers exist).
    Context variables you can use in templates:
      user, plan, subscription, enrolment, end, end_jalali, now
    """
    cfg = SubscriptionNotificationConfig.load()  # auto-create + env bootstrap
    user, user_phone = _extract_user_and_phone(subscription)

    plan = getattr(subscription, "subscription_plan", None)
    end_dt = getattr(subscription, "end_datetime", None)
    enrolment = getattr(subscription, "learner_enrolment", None)

    ctx = {
        "user": user,
        "plan": plan,
        "subscription": subscription,
        "enrolment": enrolment,
        "end": end_dt,
        "end_jalali": to_jalali_text(end_dt),
        "now": timezone.now(),
    }

    # User SMS
    if cfg.enable_user_sms and user_phone:
        msg = _render_template(cfg.user_sms_template, ctx)
        kavenegar_send_sms([user_phone], msg)

    # Managers SMS
    if cfg.enable_manager_sms:
        # If admin list is empty but env has managers, we backfill once (auto-set requirement)
        if not cfg.manager_phones:
            env_nums = os.getenv("KAVENEGAR_MANAGERS", "")
            mgrs = [m.strip() for m in env_nums.split(",") if m.strip()]
            normalized = coerce_recipients(mgrs)
            if normalized:
                cfg.manager_phones = normalized.split(",")
                cfg.save(update_fields=["manager_phones"])

        if cfg.manager_phones:
            msg_mgr = _render_template(cfg.manager_sms_template, ctx)
            kavenegar_send_sms(cfg.manager_phones, msg_mgr)

# Alias for the earlier typo so both names work
def send_subscription_expired_sm(subscription) -> None:
    return send_subscription_expired_sms(subscription)

# ------------------------------------------------------------
# Optional: register Admin here so it shows up even if core/admin.py forgets it
# (Feel free to move this to core/admin.py if you prefer.)
# ------------------------------------------------------------
try:  # pragma: no cover
    from django.contrib import admin
    try:
        from unfold.admin import ModelAdmin as _BaseAdmin
    except Exception:
        from django.contrib.admin import ModelAdmin as _BaseAdmin

    @admin.register(SubscriptionNotificationConfig)
    class SubscriptionNotificationConfigAdmin(_BaseAdmin):
        list_display = ("enable_user_sms", "enable_manager_sms", "managers_count", "updated_at")
        search_fields = ()
        list_filter = ()
        fieldsets = (
            ("Toggles", {"fields": ("enable_user_sms", "enable_manager_sms")}),
            ("Recipients", {"fields": ("manager_phones",)}),
            ("Templates", {"fields": ("user_sms_template", "manager_sms_template")}),
        )

        def has_add_permission(self, request):
            # singleton: allow add only if not exists
            return not SubscriptionNotificationConfig.objects.exists()

        def managers_count(self, obj):
            return len(obj.manager_phones or [])
        managers_count.short_description = "Managers"

except Exception as e:  # pragma: no cover
    # Admin registration is optional; we don't want to break imports if admin isn't ready.
    log.debug("Admin registration for SubscriptionNotificationConfig skipped: %s", e)
