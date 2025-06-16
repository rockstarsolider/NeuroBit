import re
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic

from .models import Application

IR_PHONE_REGEX = r'^(?:\+98|0)?9\d{9}$'
ALLOWED_SOP_EXTENSIONS = ['pdf', 'docx']


class HomeView(generic.TemplateView):
    template_name = 'pages/home.html'


class CoursesView(generic.TemplateView):
    template_name = 'pages/learning_paths.html'


class BackendCoursView(generic.TemplateView):
    template_name = 'pages/learning_path_detail_backend.html'


class FrontendCourseView(generic.TemplateView):
    template_name = 'pages/learning_path_detail_frontend.html'


class AICourseView(generic.TemplateView):
    template_name = 'pages/learning_path_detail_AI.html'


class UIUXCourseView(generic.TemplateView):
    template_name = 'pages/learning_path_detail_UIUX.html'


class GameDevCourseView(generic.TemplateView):
    template_name = 'pages/learning_path_detail_GameDevelopment.html'


class JoinView(generic.View):
    template_name = 'pages/join.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        data = request.POST
        file = request.FILES.get('sopfile')
        errors = {}
        context = {'data': data}

        # Full name
        if not data.get('fullName'):
            errors['fullName'] = 'This field is required.'

        # Phone validation
        phone = data.get('phone', '').strip()
        if not phone:
            errors['phone'] = 'شماره تماس را وارد کنید!'
        elif not re.match(IR_PHONE_REGEX, phone):
            errors['phone'] = 'شماره تماس وارد شده معتبر نمی باشد!'
        elif Application.objects.filter(phone=phone).exists():
            errors['phone'] = 'این شماره قبلا ثبت شده است!'
            context['already_submitted'] = True

        # Age validation
        age = data.get('age')
        age_int = None
        if not age:
            errors['age'] = 'سن را وارد کنید!'
        else:
            try:
                age_int = int(age)
                if age_int < 15:
                    errors['age'] = 'Only students aged 15 and above can apply.'
            except ValueError:
                errors['age'] = 'Enter a valid age.'

        # SOP file validation
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ALLOWED_SOP_EXTENSIONS:
                errors['sopfile'] = "فقط فایل های pdf و docx پذیرفته می شودند."
        # If errors, re-render form with errors and previous data
        if errors:
            context['errors'] = errors
            return render(request, self.template_name, context)

        # Save application
        Application.objects.create(
            full_name=data['fullName'],
            phone=phone,
            location=data.get('location', ''),
            age=age_int,
            sopfile=file
        )

        # Redirect to home page after successful submission
        return redirect(reverse('home'))
