from django.urls import path, include

from IphoneScrapper import views

urlpatterns = [
    path('', views.home, name='home'),
    path('avg/', views.avg, name='avg'),
    path('scrapp/', views.scrapp, name='scrapp'),
    path('exportcsv/', views.exportcsv, name='exportcsv'),
]
