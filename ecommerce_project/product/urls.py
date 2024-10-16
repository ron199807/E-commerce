from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, UserViewSet, ReviewViewSet, ProductImageViewSet, WishlistViewSet, OrderViewSet, DiscountViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi




router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'users', UserViewSet, basename='user')
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

    # main urls
    path('', include(router.urls)),

       # swagger ui
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-ui'),

    # ReDoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]
