from django.urls import path

from . import views

from .views import logout_view

urlpatterns = [

    path('', views.login_view, name='login'),

    path('signup/', views.signup_view, name='signup'),

    path('forgot-password/', views.forgot_password_view, name='forgot_password'),

   

    path('dashboard/', views.dashboard, name='dashboard'),

    path('crop/', views.crop, name='crop'),

    path('weather/', views.weather, name='weather'),

    path('soil/', views.soil, name='soil'),
    path('crop-records/', views.crop_records, name='crop_records'),
    path('crop-records/delete/<int:record_id>/', views.delete_crop_record, name='delete_crop_record'),

   path("logout/", logout_view, name="logout"),

]
