from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, 
    CategoryViewSet, 
    UserViewSet,
    ReviewViewSet, 
    ProductImageViewSet, 
    WishlistViewSet,
    OrderViewSet, 
    DiscountViewSet
)

# Initialize DefaultRouter
router = DefaultRouter()

# Register API endpoints with appropriate base names
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'users', UserViewSet, basename='user')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'product-images', ProductImageViewSet, basename='product-image')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'discounts', DiscountViewSet, basename='discount')

# App-specific URL patterns
urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
]