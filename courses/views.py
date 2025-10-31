from django.shortcuts import render
from django.views.generic import View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

# Learner side Views
class LearnerDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/learner_dash.html')
    
class StepListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/step_list.html')
    
class TaskListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/task_list.html')
    
class TaskSubmissionView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/task_submission.html')
    
class ProfileOverviewView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/profile_overview.html')
    
class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/edit_profile.html')
    
class LearningPathView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/learning_path.html')
    
class SubscriptionPlansView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/subscription/plans.html')

class StepPromiseView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/step_promise.html')
    
class TaskFeedbackView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/task_feedback.html')
    
# Mentor side Views
class MnetorFeedbackListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/mentor_feedback_list.html')
    
class MnetorFeedbackView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/mentor/mentor_feedback.html')
    
class AttendaceHubView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/mentor/attendance_hub.html')
    
class LearnersListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/learners_list.html')
    
class SessionListView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/session_list.html')
    
class GroupSessionAttendanceView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/group_session_attendance.html')
    
class PrivateSessionAttendanceView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/private_session_attendance.html')
    
class PrivateSessionManageView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'courses/mentor/private_session_manage.html')

class LearnerAttendanceHistoryView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/learner_attendance_history.html')
    
class GroupAttendanceHistoryView(LoginRequiredMixin, ListView):
    def get(self, request):
        return render(request, 'courses/mentor/group_attend_history.html')