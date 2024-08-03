from django.urls import path

from setting import views

urlpatterns = [
    path('', views.RuleAPIView.as_view(), name='rule'),
]
