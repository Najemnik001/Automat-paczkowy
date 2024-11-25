from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('main/', views.main_page, name='main_page'),
    path('create/', views.create_parcel, name='create_parcel'),
    path('logout/', views.logout_view, name='logout'),
]
