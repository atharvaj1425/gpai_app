from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('logout', views.user_logout, name='logout'),
    path('divisional_office_dashboard', views.divisional_office_dashboard, name="divisional_office_dashboard"),
    path('post_office_dashboard', views.post_office_dashboard, name='post_office_dashboard'),
    path('post_office_monitored', views.post_office_monitored, name="post_office_monitored"),
    path('post-office/history/<int:post_office_id>/', views.view_post_office_history, name='view_post_office_history'),
    path('utility_bills/<int:post_office_id>/', views.utility_bills, name='utility_bills'),
    path('fetch_postoffice', views.fetch_postoffice, name="fetch_postoffice"),
    path('image_table', views.image_table, name="image_table")
]