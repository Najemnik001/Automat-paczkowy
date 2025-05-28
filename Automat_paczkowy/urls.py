from django.urls import path, include

urlpatterns = [

    path('api/users/', include('users.urls')),
    path('', include('frontend.urls')),
    path('webpush/', include('webpush.urls')),
]