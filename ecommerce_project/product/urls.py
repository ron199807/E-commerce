from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    admin_dashboard, 
    signup_view, 
    login_view, 
    logout_view, 
    admin_users, 
    admin_products, 
    admin_categories,
    admin_orders,
    admin_reviews,
    admin_discounts,
    update_user,
    delete_user,
    create_product,
    update_product,
    delete_product,
    create_category,
    update_category,
    delete_category,
    create_discount,
    update_discount,
    delete_discount,
    admin_reviews,
    delete_review,
    update_order_status,
    admin_orders,
    create_user,
    
    )
from .views import (
    ProductViewSet, 
    CategoryViewSet, 
    UserViewSet,
    ReviewViewSet, 
    ProductImageViewSet, 
    WishlistViewSet,
    OrderViewSet, 
    DiscountViewSet,
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

    # Admin dashboard and related views
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),

    # User URLs
    path('admin-dashboard/users/update/<int:pk>/', update_user, name='update_user'),
    path('admin-dashboard/users/delete/<int:pk>/', delete_user, name='delete_user'),
    path('admin-dashboard/users/', admin_users, name='admin_users'),
    path('admin-dashboard/users/create/', create_user, name='create_user'),

    # Product URLs
    path('admin-dashboard/products/', admin_products, name='admin_products'),
    path('admin-dashboard/products/create/', create_product, name='create_product'),
    path('admin-dashboard/products/update/<int:pk>/', update_product, name='update_product'),
    path('admin-dashboard/products/delete/<int:pk>/', delete_product, name='delete_product'),

    # Category URLs
    path('admin-dashboard/categories/', admin_categories, name='admin_categories'),
    path('admin-dashboard/categories/create/', create_category, name='create_category'),
    path('admin-dashboard/categories/update/<int:pk>/', update_category, name='update_category'),
    path('admin-dashboard/categories/delete/<int:pk>/', delete_category, name='delete_category'),

    # Discount URLs
    path('admin-dashboard/orders/', admin_orders, name='admin_orders'),
    path('admin-dashboard/discounts/create/', create_discount, name='create_discount'),
    path('admin-dashboard/discounts/update/<int:pk>/', update_discount, name='update_discount'),
    path('admin-dashboard/discounts/delete/<int:pk>/', delete_discount, name='delete_discount'),

    # Review URLs
    path('admin-dashboard/reviews/', admin_reviews, name='admin_reviews'),
    path('admin-dashboard/reviews/delete/<int:pk>/', delete_review, name='delete_review'),

    # Discount URLs
    path('admin-dashboard/discounts/', admin_discounts, name='admin_discounts'),
    path('admin-dashboard/discounts/create/', create_discount, name='create_discount'),
    path('admin-dashboard/discounts/update/<int:pk>/', update_discount, name='update_discount'),
    path('admin-dashboard/discounts/delete/<int:pk>/', delete_discount, name='delete_discount'),

    # Order status update
    path('admin-dashboard/orders/update-status/<int:pk>/', update_order_status, name='update_order_status'),

    # Authentication views
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]