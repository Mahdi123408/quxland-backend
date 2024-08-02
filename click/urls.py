from django.urls import path

from click import views

urlpatterns = [
    path('', views.UserDataAPIView.as_view(), name='click_user_data'),
    path('/add', views.AddClickAPIView.as_view(), name='add_point'),
]
