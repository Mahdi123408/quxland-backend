from django.urls import path

from files import views

urlpatterns = [
    path('/upload', views.UploadAPIView.as_view(), name='upload-file'),
    path('/all', views.GetFilesAPIView.as_view(), name='get-all-files'),
]
