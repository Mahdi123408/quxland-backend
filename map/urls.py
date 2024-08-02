from django.urls import path

from map import views

urlpatterns = [
    path('city/all', views.AllCityApiView.as_view(), name='city_all'),
    path('city/<int:city_id>', views.CityApiView.as_view(), name='city_and_properties'),
    path('property/<int:property_id>', views.PropertyApiView.as_view(), name='property'),
    path('property', views.CreatPropertyApiView.as_view(), name='creat_property'),
    path('buy-property/<int:property_id>', views.BuyPropertyApiView.as_view(), name='buy_property'),
]
