from django.contrib import admin
from django.urls import path, include
from equipment.views import signup, login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('equipment.urls')),
    # Authentication endpoints
    path('api/signup/', signup, name='api_signup'),
    path('api/login/', login, name='api_login'),  # Use custom login, not obtain_auth_token
]