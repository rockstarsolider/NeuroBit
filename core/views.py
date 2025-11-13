from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import login

from . models import CustomUser
from .forms import LoginForm
from . import helper
from django.utils.translation import gettext as _


class LoginView(View):

    template_name = 'core/login.html'
    form_class = LoginForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request):

        form = self.form_class(request.POST)
        otp = helper.get_random_otp()
        print(otp)

        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']

            try:
                user = CustomUser.objects.get(phone_number=phone_number)
                helper.send_otp_code(phone_number, otp)
                user.otp_code = otp
                user.save()
                request.session['phone_number'] = phone_number
                return redirect('verify')

            except CustomUser.DoesNotExist:
                user = CustomUser(phone_number=phone_number)
                helper.send_otp_code(phone_number, otp)
                user.otp_code = otp
                user.is_active = False
                user.save()
                request.session['phone_number'] = phone_number
                return redirect('verify')

        return render(request, 'core/login.html', {'form': form})


# TODO: after login delete the session
def verify_otp_view(request):
    try:
        phone_number = request.session.get('phone_number')
        user = CustomUser.objects.get(phone_number=phone_number)
        if request.method == "POST":
            # check otp expiration
            if not helper.check_otp_expiration(phone_number):
                messages.error(request, _('OTP code is expired!, please try again.'))
                return redirect('verify')

            if user.otp_code != int(request.POST.get('otp')):
                messages.error(request, _('OTP code is incorrect!, please try again.'))
                return redirect('verify')
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, _("Signed in!"))
            return redirect('learner-dashboard')
        return render(request, 'core/verify.html', {'phone_number': phone_number})
    except CustomUser.DoesNotExist:
        messages.error(request, 'Error accorded!, please try again.')
        return redirect('login')