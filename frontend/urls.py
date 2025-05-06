from django.urls import path
from . import views
from .views import admin_panel, add_locker, edit_locker, delete_locker, delete_user, logout_view, admin_panel, courier_view

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('main_page/', views.main_page, name='main_page'),
    path('admin_panel/', admin_panel, name='admin_panel'),
    path('create/', views.create_parcel, name='create_parcel'),
    path('mock-store-parcel/', views.mock_store_parcel, name='mock_store_parcel'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_panel/', admin_panel, name='admin_panel'),
    path('courier/', courier_view, name='courier_view'),
    path('add_locker/', add_locker, name='add_locker'),
    path('edit_locker/<int:locker_id>/', edit_locker, name='edit_locker'),
    path('delete_locker/<int:locker_id>/', delete_locker, name='delete_locker'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),
]
