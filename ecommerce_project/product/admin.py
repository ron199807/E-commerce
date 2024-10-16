from django.contrib import admin
from django.contrib.auth.models import User 
from .models import CustomUser, Category, Product, Order, Wishlist, ProductImage, Review, Discount

admin.site.register(User)
admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Wishlist)
admin.site.register(ProductImage)
admin.site.register(Review)
admin.site.register(Discount)
