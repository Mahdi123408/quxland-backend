from django.urls import path

from weblog import views

urlpatterns = [
    path('', views.WeblogReadAndCreateAPIView.as_view(), name='weblog-api-read-create'),
    path('/<int:article_id>', views.EditAndDeleteArticleAPIView.as_view(), name='weblog-api-delete-edit'),

]
