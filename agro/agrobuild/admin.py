from django.contrib import admin
from .models import Product, Wishlist,CartItem, Order, OrderItem, Category

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('P_id', 'P_name', 'P_price', 'display_categories')
    filter_horizontal = ('categories',)
    search_fields = ('P_name', 'P_title')
    
    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Categories'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'email', 'total_amount', 'status', 'tracking_number', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'email', 'tracking_number')
    list_editable = ('status', 'tracking_number')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('parent',)

