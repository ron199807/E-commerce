from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User 
from .models import CustomUser, Category, Product, Order, Wishlist, ProductImage, Review, Discount
from django.utils.translation import gettext_lazy as _

class EcommerceAdminSite(AdminSite):
    site_header = _('E-Commerce Administration')
    site_title = _('E-Commerce Admin')
    index_title = _('Dashboard')

admin_site = EcommerceAdminSite(name='ecommerce_admin')

admin_site.register(User)
admin_site.register(CustomUser)
admin_site.register(Category)
admin_site.register(Product)
admin_site.register(Order)
admin_site.register(Wishlist)
admin_site.register(ProductImage)
admin_site.register(Review)
admin_site.register(Discount)
