from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("register/",views.register,name='register'),
    path('login/', views.login,name='login'),
    path('password-reset/', views.password_reset, name='password_reset'), 
    path('password/reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]