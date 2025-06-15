from django.shortcuts import render, redirect
from django.views import generic

from .models import Application


class HomeView(generic.TemplateView):
    template_name = 'pages/home.html'


class CoursesView(generic.TemplateView):
    template_name = 'pages/learning_paths.html'


class BackendCoursView(generic.TemplateView):
    template_name = 'pages/learning_path_detail_backend.html'


# def apply_view(request):
#     errors = {}
#     if request.method == 'POST':
#         data = request.POST
#         file = request.FILES.get('sopfile')
#         # basic validation
#         if not data.get('full_name'):
#             errors['full_name'] = 'This field is required.'
#         if not data.get('age'):
#             errors['age'] = 'This field is required.'
#         # you can add more checks here…
#         if not errors:
#             Application.objects.create(
#                 full_name = data['full_name'],
#                 phone     = data.get('phone',''),
#                 location  = data.get('location',''),
#                 age       = int(data['age']),
#                 sopfile   = file
#             )
#             return redirect('home')
#     return render(request, 'joinapp/join.html', {
#         'errors': errors
#     })


# def success_view(request):
#     return render(request, 'joinapp/success.html')
