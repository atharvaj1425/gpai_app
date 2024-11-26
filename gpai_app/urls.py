from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('divisional_office_dashboard', views.divisional_office_dashboard, name="divisional_office_dashboard"),
    path('post_office_dashboard', views.post_office_dashboard, name='post_office_dashboard'),
    path('fetch_postoffice', views.fetch_postoffice, name="fetch_postoffice"),
]