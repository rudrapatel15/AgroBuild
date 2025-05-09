from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Product, Wishlist, CartItem, Order, OrderItem, Category, UserProfile, ContactMessage, Blog, BlogComment, Feedback, PlantNotification
from django.utils import timezone

@admin.register(PlantNotification)
class PlantNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'product__P_name')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(product__categories__name__icontains='plant')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(categories__name__icontains='plant')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'product_name', 'category', 'created_at')
    search_fields = ('name', 'email', 'product_name', 'review')
    list_filter = ('category', 'created_at')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'date')
    search_fields = ('title', 'type')
    list_filter = ('type', 'date')

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'blog', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'formatted_date', 'user')
    
    def formatted_date(self, obj):
        return timezone.localtime(obj.created_at).strftime('%Y-%m-%d %H:%M:%S')
    formatted_date.short_description = 'Created At'
    formatted_date.admin_order_field = 'created_at'

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'dob', 'gender']
    search_fields = ['user__email', 'phone']
admin.site.register(UserProfile, UserProfileAdmin)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    list_filter = ('user',)
    search_fields = ('user__username', 'product__P_name')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    list_filter = ('user',)
    search_fields = ('user__username', 'product__P_name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('P_id', 'P_name', 'P_price', 'display_categories')
    filter_horizontal = ('categories',)
    search_fields = ('P_name',)
    
    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Categories'
    
    fieldsets = (
        (None, {
            'fields': ('P_name', 'P_Description', 'P_img', 'P_price', 'categories')
        }),
        ('Watering Requirements', {
            'fields': ('summer_watering', 'winter_watering', 'monsoon_watering'),
            'description': 'Set watering schedule for different seasons'
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and not obj.is_plant():
            # Remove watering fields for non-plant products
            return (fieldsets[0],)
        return fieldsets

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'email', 'total_amount', 'status', 'tracking_number', 'created_at', 'is_paid')
    list_filter = ('status', 'created_at', 'is_paid')
    search_fields = ('id', 'user__username', 'email', 'tracking_number')
    list_editable = ('status', 'tracking_number')
    readonly_fields = ('created_at', 'total_amount')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity')
    list_filter = ('order',)
    search_fields = ('order__id', 'product__P_name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('parent',)