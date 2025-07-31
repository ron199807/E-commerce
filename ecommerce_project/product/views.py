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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .form import CustomUserCreationForm, CategoryForm, ProductForm, DiscountForm  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from .form import CustomUserAdminForm


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

# custom admin dashboard

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Get counts for dashboard stats
    products_count = Product.objects.count()
    orders_count = Order.objects.count()
    users_count = CustomUser.objects.count()
    
    # Calculate total revenue (simplified example)
    orders = Order.objects.select_related('product')
    total_revenue = sum(order.quantity * order.product.price for order in orders)
    
    # Get recent orders and reviews
    recent_orders = Order.objects.select_related('product', 'user').order_by('-ordered_at')[:5]
    recent_reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:5]
    
    context = {
        'products_count': products_count,
        'orders_count': orders_count,
        'users_count': users_count,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
    }
    
    return render(request, 'landing/admin_dashboard.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('home')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_users(request):
    user_list = CustomUser.objects.all().order_by('-date_joined')
    paginator = Paginator(user_list, 10)  # Show 10 users per page
    page = request.GET.get('page')
    
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results
        users = paginator.page(paginator.num_pages)
    
    context = {
        'users': users,
    }
    return render(request, 'landing/admin_users.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_products(request):
    product_list = Product.objects.all().select_related('category').prefetch_related('images').order_by('-created_at')
    categories = Category.objects.all()
    paginator = Paginator(product_list, 10)  # Show 10 products per page
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'landing/admin_products.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_categories(request):
    category_list = Category.objects.all().annotate(product_count=Count('products')).order_by('name')
    paginator = Paginator(category_list, 10)  # Show 10 categories per page
    page = request.GET.get('page')
    
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    
    context = {
        'categories': categories,
    }
    return render(request, 'landing/admin_categories.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_orders(request):
    order_list = Order.objects.all().select_related('user', 'product').order_by('-ordered_at')
    paginator = Paginator(order_list, 10)  # Show 10 orders per page
    page = request.GET.get('page')
    
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    
    context = {
        'orders': orders,
    }
    return render(request, 'landing/admin_orders.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_reviews(request):
    review_list = Review.objects.all().select_related('user', 'product').order_by('-created_at')
    paginator = Paginator(review_list, 10)  # Show 10 reviews per page
    page = request.GET.get('page')
    
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
    
    context = {
        'reviews': reviews,
    }
    return render(request, 'landing/admin_reviews.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_discounts(request):
    discount_list = Discount.objects.all().select_related('product').order_by('-valid_until')
    paginator = Paginator(discount_list, 10)  # Show 10 discounts per page
    page = request.GET.get('page')
    
    try:
        discounts = paginator.page(page)
    except PageNotAnInteger:
        discounts = paginator.page(1)
    except EmptyPage:
        discounts = paginator.page(paginator.num_pages)
    
    context = {
        'discounts': discounts,
    }
    return render(request, 'landing/admin_discounts.html', context)


# ======================
# CATEGORY CRUD VIEWS
# ======================

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'landing/category_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'landing/category_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('admin_categories')
    return render(request, 'landing/category_confirm_delete.html', {'category': category})

# ======================
# PRODUCT CRUD VIEWS
# ======================

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.added_by = request.user
            product.save()
            messages.success(request, 'Product created successfully!')
            return redirect('admin_products')
    else:
        form = ProductForm()
    return render(request, 'landing/product_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'landing/product_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('admin_products')
    return render(request, 'landing/product_confirm_delete.html', {'product': product})

# ======================
# DISCOUNT CRUD VIEWS
# ======================

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_discount(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount created successfully!')
            return redirect('admin_discounts')
    else:
        form = DiscountForm()
    return render(request, 'landing/discount_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_discount(request, pk):
    discount = get_object_or_404(Discount, pk=pk)
    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount updated successfully!')
            return redirect('admin_discounts')
    else:
        form = DiscountForm(instance=discount)
    return render(request, 'landing/discount_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_discount(request, pk):
    discount = get_object_or_404(Discount, pk=pk)
    if request.method == 'POST':
        discount.delete()
        messages.success(request, 'Discount deleted successfully!')
        return redirect('admin_discounts')
    return render(request, 'landing/discount_confirm_delete.html', {'discount': discount})

# ======================
# ORDER CRUD VIEWS
# ======================

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'completed', 'cancelled']:
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {new_status}!')
        return redirect('admin_orders')
    return render(request, 'landing/order_status_form.html', {'order': order})

# ======================
# REVIEW CRUD VIEWS
# ======================

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('admin_reviews')
    return render(request, 'landing/review_confirm_delete.html', {'review': review})

# ======================
# USER CRUD VIEWS
# ======================
from .form import CustomUserCreationAdminForm, CustomUserAdminForm

@login_required
@user_passes_test(lambda u: u.is_staff)
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationAdminForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, 'User created successfully!')
            return redirect('admin_users')
    else:
        form = CustomUserCreationAdminForm()
    return render(request, 'landing/user_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def update_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        
        form = CustomUserAdminForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('admin_users')
    else:
        form = CustomUserAdminForm(instance=user)
    return render(request, 'landing/user_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('admin_users')
    return render(request, 'landing/user_confirm_delete.html', {'user': user})