"""
URL configuration for finance_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from django.urls import path, re_path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Finance API",
        default_version='v1',
        description="API documentation for Finance Backend",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    path("", include("frontend.urls")),
    path('admin/', admin.site.urls),
    path('api/token/',TokenObtainPairView.as_view()),
    path('api/token/refresh/',TokenRefreshView.as_view()),
    path('api/',include('users.urls')),
    path('api/',include('records.urls')),
    path('api/dashboard/',include('dashboard.urls')),
 # Swagger endpoints
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),

]
