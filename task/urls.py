from django.urls import path

from task import views

urlpatterns = [
    path('', views.TaskAndReferralListAPIView.as_view(), name='task_list'),
    path('/complete/<int:id>', views.CompleteTaskAPIView.as_view(), name='completed_task'),
    path('/daily', views.DailyCompleteTaskAPIView.as_view(), name='daily'),
    # path('/daily/<int:daily_task_id>', views.DailyCompleteTaskAPIView.as_view(), name='daily_task_complet'),
]
