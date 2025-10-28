from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.utils import timezone
from django.contrib import messages
import random
from django.utils.translation import gettext as _

User = get_user_model()

def phone_view(request):
    """Step 1: Get phone and send OTP"""
    if request.method == "POST":
        phone = request.POST.get("phone")
        otp = str(random.randint(100000, 999999))
        request.session["otp"] = otp
        request.session["phone"] = phone
        request.session["otp_time"] = timezone.now().timestamp()
        print(f"OTP for {phone}: {otp}")  # replace with SMS later
        return redirect("verify_otp")
    return render(request, "core/phone.html")


def verify_otp(request):
    """Step 2: Verify OTP and login/signup"""
    if request.method == "POST":
        otp = request.POST.get("otp")
        session_otp = request.session.get("otp")
        phone = request.session.get("phone")
        otp_time = request.session.get("otp_time")

        if otp_time and timezone.now().timestamp() - otp_time > 300:
            for k in ("otp", "phone", "otp_time"): request.session.pop(k, None)
            messages.error(request, _("OTP has expired. Please request a new one."))
            return redirect("phone_view")

        if otp == session_otp:
            user, created = User.objects.get_or_create(
                phone_number=phone, defaults={"username": phone}
            )
            login(request, user)
            for k in ("otp", "phone", "otp_time"): request.session.pop(k, None)
            messages.success(request, _("Signed up!") if created else _("Signed in!"))
            return redirect("learner-dashboard")

        messages.error(request, _("Invalid OTP"))
    return render(request, "core/verify.html")