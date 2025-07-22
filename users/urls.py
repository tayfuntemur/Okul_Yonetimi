from django.contrib import admin
from django.urls import path
from . import views

app_name='users'
urlpatterns = [
    path('register/',views.register_view , name='register_view'), 
    path('login/',views.login_view , name='login_view'), 
    path('update/',views.update_user_view , name='update_user_view'), 
    path('logout/',views.logout_view , name='logout_view'), 
]