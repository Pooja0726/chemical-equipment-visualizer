from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token # New import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('equipment.urls')),
    # This creates the /api/login/ endpoint for your frontends
    path('api/login/', obtain_auth_token, name='api_token_auth'), 
]