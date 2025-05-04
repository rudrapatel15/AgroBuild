# views.py
from django.shortcuts import render, redirect
from .models import Product, Wishlist, CartItem, Order, OrderItem, Category
from math import ceil
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .payment_utils import create_razorpay_order
from django.conf import settings
import razorpay
from django.urls import reverse

@require_POST
@login_required
def update_cart(request):
    for item_id, quantity in request.POST.items():
        if item_id.startswith('quantity_'):
            item_pk = int(item_id.split('_')[1])
            try:
                cart_item = CartItem.objects.get(id=item_pk, user=request.user)
                cart_item.quantity = max(1, int(quantity))  # avoid zero or negative
                cart_item.save()
            except CartItem.DoesNotExist:
                continue
    return redirect('cart')

@login_required
def add_to_cart_from_wishlist(request, product_id):
    product = get_object_or_404(Product, P_id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@require_POST
@login_required
def remove_from_cart(request):
    item_id = request.POST.get('item_id')
    CartItem.objects.filter(id=item_id, user=request.user).delete()
    return redirect('cart')

def index(request):
    allProds = []
   
    categories_to_show = ['indoor plants', 'Fruit Seeds', 'Garden Tools']
    
    for category_name in categories_to_show:
        prod = Product.objects.filter(category__iexact=category_name)
        n = len(prod)
        if n > 0:
            nSlides = n // 4 + ceil((n / 4) - (n // 4))
            allProds.append([prod, range(1, nSlides), nSlides, category_name])
    
    return render(request, 'htmldemo.net/index.html', {'allProds': allProds})

def account(request): return render(request, 'htmldemo.net/my-account.html')

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'htmldemo.net/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = Product.objects.get(P_id=product_id)
    product = get_object_or_404(Product, pk=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist') 

@login_required
def remove_from_wishlist(request, product_id):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product__P_id=product_id)
    wishlist_item.delete()
    return redirect('wishlist') 

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(P_id=product_id)
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product, defaults={'quantity': quantity})
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    return redirect('cart') 

def basic(request): return render(request, 'htmldemo.net/basic.html')

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    subtotal = sum(item.product.P_price * item.quantity for item in cart_items)
    shipping = 60
    total = subtotal + shipping
    return render(request, 'htmldemo.net/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total
    })

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    subtotal = sum(item.product.P_price * item.quantity for item in cart_items)
    shipping = 100
    total = subtotal + shipping

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'online':
           
            razorpay_order = create_razorpay_order(total)
            
            order = Order.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name'),
                total_amount=total,
                payment_method='Online Payment',
                razorpay_order_id=razorpay_order['id'],
                is_paid=False
            )
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.P_price,
                    quantity=item.quantity
                )
            
            context = {
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_amount': razorpay_order['amount'],
                'currency': 'INR',
                'key_id': settings.RAZORPAY_KEY_ID,
                'order': order,
                'user': request.user
            }
            return render(request, 'htmldemo.net/payment.html', context)
          
    return render(request, 'htmldemo.net/checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total
    })
def payment_verification(request):
   
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
def payment_verification(request):
    if request.method == 'POST':
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.is_paid = True
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.status = 'processing'
            order.save()
            
            CartItem.objects.filter(user=request.user).delete()
            
            return redirect('order_confirmation', order_id=order.id)
        except:
           
            return render(request, 'htmldemo.net/payment_failed.html')

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'htmldemo.net/order_confirmation.html', {
        'order': order,
        'order_items': order.items.all()
    })
def blog(request): return render(request, 'htmldemo.net/blog-details.html')
def aboutus(request): return render(request, 'htmldemo.net/about.html')
def contactus(request): return render(request, 'htmldemo.net/contact.html')
def faq(request): return render(request, 'htmldemo.net/faq.html')

def prod_view(request):
    prod_id = request.GET.get('myid')
    product = Product.objects.filter(P_id=prod_id).first()
    return render(request, 'htmldemo.net/prod_View.html', {'product': product})

@login_required
def account(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'htmldemo.net/my-account.html', {'orders': orders})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(categories=category)
    subcategories = category.children.all()
    
    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
        'is_main_category': category.parent is None
    }
    return render(request, 'htmldemo.net/category_products.html', context)