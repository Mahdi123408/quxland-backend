from django.urls import path

from transaction import views

urlpatterns = [
    path('/diamond', views.DiamondPackageListAPIView.as_view(), name='diamond-package-list'),
    path('/diamond/buy/<int:diamond_id>', views.BuyDiamondPackageAPIView.as_view(), name='diamond-package-buy'),
]