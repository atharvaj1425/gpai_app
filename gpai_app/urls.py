from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path('login', views.login, name="login"),
    path('logout', views.user_logout, name='logout'),
    path('divisional_office_dashboard', views.divisional_office_dashboard, name="divisional_office_dashboard"),
    path('post_office_dashboard', views.post_office_dashboard, name='post_office_dashboard'),
    path('post_office_monitored', views.post_office_monitored, name="post_office_monitored"),
    path('post-office/history/<int:post_office_id>/', views.view_post_office_history, name='view_post_office_history'),
    path('utility_bills/<int:post_office_id>/', views.utility_bills, name='utility_bills'),
    path('campaigns/<int:post_office_id>/', views.drive_campaigns, name='drive_campaigns'),
    path('life_practices/<int:post_office_id>/', views.life_practices, name='life_practices'),
    path('post-office/view_campaign_history/<int:post_office_id>/', views.view_campaign_history, name='view_campaign_history'),
    path('fetch_postoffice', views.fetch_postoffice, name="fetch_postoffice"),
    path('image_table', views.image_table, name="image_table"),
    path('get-post-offices/', views.get_post_offices, name='get_post_offices'),
    path('submit-recycling-request/', views.submit_recycling_request, name='submit_recycling_request'),
    path('citizen_dashboard', views.citizen_dashboard, name='citizen_dashboard'),
    path('register/<int:user_id>/<int:campaign_drive_id>/', views.register_campaign, name='register_campaign'),
]