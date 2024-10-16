"""
URL configuration for ecommerce_project project.

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
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from product.views import (
    ProductViewSet, CategoryViewSet, UserViewSet, 
    ReviewViewSet, ProductImageViewSet, WishlistViewSet, 
    OrderViewSet, DiscountViewSet
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


router = DefaultRouter()
router.register('product', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')
router.register('users', UserViewSet, basename='user')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'product_image', ProductImageViewSet, basename='product_image')
router.register(r'wish_list', WishlistViewSet, basename='wish_list')
router.register(r'order', OrderViewSet, basename='order')
router.register(r'discounts', DiscountViewSet, basename='discount')

#-----------------------
# swagger schema
#-----------------------
schema_view = get_schema_view(
    openapi.Info(
        title="E-commerce API",
        default_version="v1",
        description="API documentation for the E-commerce project",
        term_of_service="http://google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),


)






urlpatterns = [
    # Main URL patterns
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # JWT authentication paths
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # swagger ui
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-ui'),

    # ReDoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
 ]



