from django.utils import timezone
from random import randint
from .models import CustomUser
import logging
import secrets
from django.conf import settings
from django.utils.translation import gettext_lazy as _
try:
    from kavenegar import KavenegarAPI
    _kavenegar = KavenegarAPI(settings.KAVENEGAR_API)
except Exception:  # nosec - best effort
    _kavenegar = None

    
# Optional SMS client (Kavenegar). Falls back silently in dev.
def get_random_otp() -> str:
    """Generate a cryptographically secure 6-digit OTP."""
    return f"{secrets.randbelow(900000) + 100000}"

def send_otp_code(phone_number: str, code: str) -> None:
    if not _kavenegar:
        logging.warning("Kavenegar client not available; SMS not sent (dev mode).")
        return
    params = {
        "sender": '1000100175',
        "receptor": phone_number,
        "message": f"کد ورود شما: {code}",
    }
    try:
        _kavenegar.sms_send(params)
    except Exception as exc:  # nosec
        logging.warning("Failed to send OTP via Kavenegar: %s", exc)


def check_otp_expiration(phone_number):
    try:
        user = CustomUser.objects.get(phone_number=phone_number)
        now = timezone.now()
        otp_time = user.otp_code_created
        diff_time = now - otp_time
        print(f'otptime: {diff_time}')
        if diff_time.seconds > 120:
            return False
        return True

    except CustomUser.DoesNotExist:
        return False