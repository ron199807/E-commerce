from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Product, Category, CustomUser, Review, Order, Wishlist, ProductImage, Discount
from .serializers import (
    ProductSerializer, ProductCreateSerializer, 
    CategorySerializer, UserSerializer, ReviewSerializer, WishlistSerializer, ProductImageSerializer, OrderSerializer, OrderCreateSerializer, DiscountSerializer
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework import status



# product viewset and pagination
class ProductPagination(PageNumberPagination):
    page_size = 10

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    pagination_class = ProductPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'category__name']
    filterset_fields = ['category', 'price', 'stock_quantity']

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return ProductCreateSerializer
        return ProductSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# category viewset
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# user viewset
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]



# Review views
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# product image view set
class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

# wish list view set
class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# order view set


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Assign the current user to the order."""
        serializer.save(user=self.request.user)



# discount view set
class DiscountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product discounts.
    Allows creating, updating, deleting, and retrieving discounts.
    """
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Validate that the discount is still valid upon creation."""
        if serializer.validated_data['valid_until'] < now():
            return Response(
                {"error": "The discount's validity date must be in the future."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()

    def perform_update(self, serializer):
        """Ensure the discount remains valid upon update."""
        if serializer.validated_data.get('valid_until', now()) < now():
            return Response(
                {"error": "The discount's validity date must be in the future."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()

