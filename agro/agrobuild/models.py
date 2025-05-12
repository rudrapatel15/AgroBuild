from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import time, timedelta

class WateringReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    morning_time = models.TimeField(default=time(8, 0))
    evening_time = models.TimeField(default=time(18, 0))
    allow_website = models.BooleanField(default=False)
    allow_gmail = models.BooleanField(default=False)
    gmail = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if not self.product.is_plant():
            from django.core.exceptions import ValidationError
            raise ValidationError("Watering reminders can only be set for plant products.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Enforce the clean() method
        super().save(*args, **kwargs)

class NotificationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def clean(self):
        # Only allow reminders for plant products
        if not self.product.is_plant():
            from django.core.exceptions import ValidationError
            raise ValidationError("Watering reminders can only be set for plant products.")
        
class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('plants', 'Plants'),
        ('seeds', 'Seeds'),
        ('compost', 'Compost'),
        ('fertilizers', 'Fertilizers'),
        ('pesticides', 'Pesticides'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    product_name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.name} about {self.product_name or self.category}"

class Blog(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='blog_images/')
    type = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.name} on {self.blog.title}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user.username} - {self.product.P_name}"
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  

    def total_price(self):
        return self.quantity * self.product.P_price

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    menu = models.CharField(max_length=50, blank=True, null=True)
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def is_main_category(self):
        return self.parent is None
    
    def get_absolute_url(self):
        return reverse('category_products', kwargs={'slug': self.slug})
    
class Product(models.Model):
    P_id = models.AutoField(primary_key=True)
    P_name = models.CharField(max_length=255)
    P_Description = models.TextField()
    P_img = models.ImageField(upload_to='image/img',default="")
    P_price = models.DecimalField(max_digits=10, default=Decimal('0.00'), decimal_places=2)
    categories = models.ManyToManyField(Category)

    summer_watering = models.CharField(
        max_length=50, 
        choices=[
            ('daily', 'Daily'),
            ('twice', 'Twice a day'),
            ('every_two_days', 'Every two days'),
            ('weekly', 'Weekly')
        ], 
        default='daily',
        verbose_name="Summer (Mar-Jun) Watering"
    )
    winter_watering = models.CharField(
        max_length=50, 
        choices=[
            ('daily', 'Daily'),
            ('twice', 'Twice a day'),
            ('every_two_days', 'Every two days'),
            ('weekly', 'Weekly')
        ], 
        default='twice',
        verbose_name="Winter (Nov-Feb) Watering"
    )
    monsoon_watering = models.CharField(
        max_length=50, 
        choices=[
            ('daily', 'Daily'),
            ('twice', 'Twice a day'),
            ('every_two_days', 'Every two days'),
            ('weekly', 'Weekly')
        ], 
        default='every_two_days',
        verbose_name="Monsoon (Jul-Oct) Watering"
    )
    def is_plant(self):
        return self.categories.filter(name__icontains='plant').exists()
    
    def __str__(self):
        return self.P_name
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return self.user.email

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def get_status_class(self):
        if self.status == 'delivered':
            return 'success'
        elif self.status == 'cancelled':
            return 'danger'
        return ''

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.P_name}"
    
class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"