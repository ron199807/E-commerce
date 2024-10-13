from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, UserViewSet, ReviewViewSet, ProductImageViewSet, WishlistViewSet, OrderViewSet, DiscountViewSet

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'users', UserViewSet, basename='user')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'product_image', ProductImageViewSet, basename='product_image')
router.register(r'wish_list', WishlistViewSet, basename='wish_list')
router.register(r'order', OrderViewSet, basename='order')
router.register(r'discounts', DiscountViewSet, basename='discount')


urlpatterns = [
    path('', include(router.urls)),
]
