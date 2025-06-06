from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Product, Wishlist, CartItem, Order, OrderItem, Category, UserProfile, ContactMessage, Blog, BlogComment, Feedback, WateringReminder, NotificationHistory
from django.utils import timezone
from django.utils.html import format_html

@admin.register(WateringReminder)
class WateringReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'morning_time', 'evening_time', 'allow_website', 'allow_gmail', 'is_active')
    list_filter = ('is_active', 'allow_website', 'allow_gmail', 'morning_time', 'evening_time')
    search_fields = ('user__username', 'category__name')

@admin.register(NotificationHistory)
class NotificationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'product__P_name', 'message')

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
    list_display = ('P_id', 'P_name', 'P_price', 'stock', 'display_categories', 'image_preview')
    list_editable = ('P_name', 'P_price', 'stock')
    list_filter = ('categories',)
    search_fields = ('P_name',)
    filter_horizontal = ('categories',)
    readonly_fields = ('image_preview',)
    list_per_page = 20

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Categories'

    def image_preview(self, obj):
        if obj.P_img:
            return format_html('<img src="{}" style="height: 50px; width: 50px; object-fit: cover;" />', obj.P_img.url)
        return "-"
    image_preview.short_description = 'Image'
       
    fieldsets = (
        (None, {
            'fields': ('P_name', 'P_Description', 'P_img', 'image_preview', 'P_price', 'stock', 'categories'),
            'description': "Fill in the basic product details."
        }),
        ('Watering Requirements', {
            'fields': ('summer_watering', 'winter_watering', 'monsoon_watering'),
            'description': 'Set watering schedule for different seasons'
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and not obj.is_plant():
            return (fieldsets[0],)
        return fieldsets

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'full_name', 'email', 'total_amount', 'payment_method',
        'upi_transaction_number', 'payment_status', 'status',
        'tracking_number', 'created_at'
    )
    list_filter = ('status', 'created_at', 'payment_method', 'payment_status')
    search_fields = ('id', 'user__username', 'email', 'tracking_number', 'upi_transaction_number')
    list_editable = ('status', 'tracking_number', 'payment_status')
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