from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse

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
    P_title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, default="")
    P_Description = models.TextField()
    P_img = models.ImageField(upload_to='image/img',default="")
    P_price = models.DecimalField(max_digits=10, default=Decimal('0.00'), decimal_places=2)
    P_Quality = models.IntegerField(default=1)
    categories = models.ManyToManyField(Category)
    def __str__(self):
        return self.P_name

# models.py (update Order model)
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