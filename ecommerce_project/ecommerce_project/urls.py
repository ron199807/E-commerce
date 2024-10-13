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



router = DefaultRouter()
router.register('product', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')
router.register('users', UserViewSet, basename='user')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'product_image', ProductImageViewSet, basename='product_image')
router.register(r'wish_list', WishlistViewSet, basename='wish_list')
router.register(r'order', OrderViewSet, basename='order')
router.register(r'discounts', DiscountViewSet, basename='discount')

urlpatterns = [
    # Main URL patterns
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # JWT authentication paths
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]



