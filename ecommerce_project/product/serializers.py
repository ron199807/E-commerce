from rest_framework import serializers
from .models import Product, Category, CustomUser, Review, ProductImage, Wishlist, Order, Discount


# category serializers
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

# product serializer
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'stock_quantity', 'image_url', 'created_at'
        ]

# creating a product
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock_quantity', 'image_url']

# user serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']


# review serializer
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate(self, data):
        user = self.context['request'].user
        product = data['product']

        #  check if the user has already reviewed the product
        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError('You have already reviewed this product.')
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user

# automatically assign user
        return super().create(validated_data)


# product images serializer
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image_url']


# wish list serializers
class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'added_at']
        read_only_fields = ['id', 'added_at']

# order serializers


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for listing orders."""
    product = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'product', 'quantity', 'user', 'ordered_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an order."""

    class Meta:
        model = Order
        fields = ['product', 'quantity']

    def validate_quantity(self, value):
        """Ensure that the order quantity does not exceed available stock."""
        product = self.initial_data.get('product')
        product_instance = Product.objects.get(id=product)

        if value > product_instance.stock_quantity:
            raise serializers.ValidationError("Insufficient stock for the product.")
        return value

    def create(self, validated_data):
        """Create an order and automatically reduce product stock."""
        product = validated_data['product']
        quantity = validated_data['quantity']

        # Reduce stock quantity
        if product.stock_quantity < quantity:
            raise serializers.ValidationError("Not enough stock available.")
        product.stock_quantity -= quantity
        product.save()

        # Create and return the order
        return Order.objects.create(**validated_data)

# Discount serializer
class DiscountSerializer(serializers.ModelSerializer):
    discounted_price = serializers.ReadOnlyField()

    class Meta:
        model = Discount
        fields = ['id', 'product', 'discount_percentage', 'valid_until', 'discounted_price']

