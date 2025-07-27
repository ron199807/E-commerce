from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from django.db.models import Q
from rest_framework import permissions, serializers

from .models import Product, Category, CustomUser, Review, Order, Wishlist, ProductImage, Discount
from .serializers import (
    ProductSerializer, 
    ProductCreateSerializer,
    CategorySerializer, 
    UserSerializer, 
    ReviewSerializer, 
    WishlistSerializer, 
    ProductImageSerializer, 
    OrderSerializer, 
    OrderCreateSerializer, 
    DiscountSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .filters import ProductFilter

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    queryset = Product.objects.all().select_related('category').prefetch_related('images')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'rating']
    ordering = ['-created_at']
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateSerializer
        return ProductSerializer

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """
        Get similar products based on category
        """
        product = self.get_object()
        similar_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        serializer = self.get_serializer(similar_products, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'username'

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retrieve the current authenticated user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows reviews to be viewed or edited.
    """
    queryset = Review.objects.all().select_related('user', 'product')
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProductImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows product images to be managed.
    """
    queryset = ProductImage.objects.all().select_related('product')
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

class WishlistViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows wishlist items to be managed.
    """
    queryset = Wishlist.objects.all().select_related('user', 'product')
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orders to be managed.
    """
    queryset = Order.objects.all().select_related('user').prefetch_related('items')
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an order
        """
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'cancelled'
        order.save()
        return Response({'status': 'order cancelled'})

class DiscountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows discounts to be managed.
    """
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(valid_until__gte=now())
        return queryset

    def perform_create(self, serializer):
        if serializer.validated_data['valid_until'] < now():
            raise serializers.ValidationError(
                {"valid_until": "The discount's validity date must be in the future."}
            )
        serializer.save()

    def perform_update(self, serializer):
        if serializer.validated_data.get('valid_until', now()) < now():
            raise serializers.ValidationError(
                {"valid_until": "The discount's validity date must be in the future."}
            )
        serializer.save()