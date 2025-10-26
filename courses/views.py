from django.shortcuts import render
from django.views.generic import View, ListView

# Create your views here.
class LearnerDashboardView(View):
    def get(self, request):
        return render(request, 'courses/learner_dash.html')
    
class StepListView(ListView):
    def get(self, request):
        return render(request, 'courses/step_list.html')
    
class MnetorFeedbackListView(ListView):
    def get(self, request):
        return render(request, 'courses/mentor_feedback_list.html')