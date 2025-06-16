from django.shortcuts import render, redirect
from django.views import generic
from django.http import JsonResponse

from .models import Application


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
        # Render the form as usual
        return render(request, self.template_name)

    def post(self, request):
        # Expecting AJAX POST with form data
        data = request.POST
        file = request.FILES.get('sopfile')
        errors = {}

        # Validate fields
        if not data.get('fullName'):
            errors['fullName'] = 'This field is required.'
        if not data.get('age'):
            errors['age'] = 'This field is required.'
        # Add more validation as needed

        if errors:
            # Return errors as JSON for AJAX
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # Save application
        Application.objects.create(
            full_name=data['fullName'],
            phone=data.get('phone', ''),
            location=data.get('location', ''),
            age=int(data['age']),
            sopfile=file
        )
        return JsonResponse({'success': True})
