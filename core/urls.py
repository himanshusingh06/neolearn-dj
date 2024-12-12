from django.contrib import admin
from django.urls import path
from core import views
urlpatterns = [
    path('', views.home, name='home'),
    path('contact',views.contact,name='contact'),
    # path('services',views.services,name='services'),
    path('login',views.login,name='login'),
    path('register',views.register,name='register'),
    path('logout',views.logout,name='logout'),
    path('profile',views.profile_view,name='profile'),
    path('course/<int:course_id>/', views.course_detail_view, name='course_detail_view'),

]