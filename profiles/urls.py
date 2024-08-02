from django.urls import path

from profiles import views

urlpatterns = [
    path('', views.ProfileAPIView.as_view(), name='profile-change'),
    path('/history', views.GetHistoryAPIView.as_view(), name='profile-history'),
    path('/news', views.GetNewsAPIView.as_view(), name='profile-news'),
]
