from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.views.generic import TemplateView
from product.admin import admin_site

# API Documentation Setup
schema_view = get_schema_view(
    openapi.Info(
        title="E-commerce API",
        default_version="v1",
        description="API documentation for E-commerce Platform",
        terms_of_service="https://www.yourcompany.com/terms/",
        contact=openapi.Contact(email="api-support@yourcompany.com"),
        license=openapi.License(name="Commercial License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Main URL Patterns
urlpatterns = [
    # Landing pages
    path('', TemplateView.as_view(template_name='landing/index.html'), name='home'),
    path('features/', TemplateView.as_view(template_name='landing/features.html'), name='features'),
    
    # Admin Interface
    path('admin/', admin_site.urls),
    
    # API Base URL
    path('api/', include([
        path('auth/', include([
            path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        ])),
        path('v1/', include('product.urls')),
    ])),
    
    # Documentation URLs - Only one /docs/ entry point
    path('docs/', include([
        # Your API documentation page
        path('', TemplateView.as_view(template_name='landing/api_docs.html'), name='api_docs'),
        
        # Swagger/Redoc endpoints
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    ])),
]