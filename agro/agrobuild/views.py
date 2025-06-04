# views.py
from django.shortcuts import render, redirect
from .models import Product, Wishlist, CartItem, Order, OrderItem, Category, UserProfile, ContactMessage, Blog, BlogComment, Feedback, WateringReminder, NotificationHistory
from django.contrib.auth.models import User
from math import ceil
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.templatetags.static import static
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.staticfiles import finders
import base64
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import FeedbackForm  
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit   
from decimal import Decimal
from urllib.parse import unquote

@login_required(login_url='/login/')
def view_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user) 
    # Calculate invoice values same as in download_invoice
    subtotal = Decimal('0')
    total_tax = Decimal('0')
    total_amount = Decimal('0')
    processed_items = []

    for item in order.items.all():
        tax_per_unit = item.price * Decimal('0.18')
        price_without_tax = item.price - tax_per_unit
        item_subtotal = price_without_tax * item.quantity
        item_tax = tax_per_unit * item.quantity
        item_total = item.price * item.quantity

        subtotal += item_subtotal
        total_tax += item_tax
        total_amount += item_total

        processed_items.append({
            'product': item.product,
            'quantity': item.quantity,
            'price': round(price_without_tax, 2),
            'subtotal': round(item_subtotal, 2),
            'tax': round(item_tax, 2),
            'total': round(item_total, 2),
        })

    subtotal = round(subtotal, 2)
    total_tax = round(total_tax, 2)
    total_amount = round(total_amount, 2)

    order.subtotal = subtotal
    order.total_tax = total_tax
    order.total_amount = total_amount

    shipping = Decimal('100.00')
    grand_total = total_amount + shipping

    context = {
        'order': order,
        'items': processed_items,
        'user': request.user,
        'shipping': shipping,
        'grand_total': grand_total,
        'show_download': True,
    }
    
    # Add logo and signature same as in download_invoice
    logo_path = finders.find('img/logo/logo.png')
    if logo_path:
        with open(logo_path, "rb") as img_file:
            context['logo_base64'] = base64.b64encode(img_file.read()).decode('utf-8')
    else:
        context['logo_base64'] = ''

    signature_path = finders.find('img/signatures.jpg')
    if signature_path:
        with open(signature_path, "rb") as img_file:
            context['signature_base64'] = base64.b64encode(img_file.read()).decode('utf-8')
    else:
        context['signature_base64'] = ''

    return render(request, 'htmldemo.net/invoice.html', context)

@login_required(login_url='/login/')
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_status.lower() != 'paid':
        return HttpResponse("Invoice not available until payment is verified.", status=403)
    subtotal = Decimal('0')
    total_tax = Decimal('0')
    total_amount = Decimal('0')
    processed_items = []

    for item in order.items.all():
        tax_per_unit = item.price * Decimal('0.18')
        price_without_tax = item.price - tax_per_unit
        item_subtotal = price_without_tax * item.quantity
        item_tax = tax_per_unit * item.quantity
        item_total = item.price * item.quantity

        subtotal += item_subtotal
        total_tax += item_tax
        total_amount += item_total

        processed_items.append({
            'product': item.product,
            'quantity': item.quantity,
            'price': round(price_without_tax, 2),
            'subtotal': round(item_subtotal, 2),
            'tax': round(item_tax, 2),
            'total': round(item_total, 2),
        })

    subtotal = round(subtotal, 2)
    total_tax = round(total_tax, 2)
    total_amount = round(total_amount, 2)

    order.subtotal = subtotal
    order.total_tax = total_tax
    order.total_amount = total_amount

    shipping = Decimal('100.00')
    grand_total = total_amount + shipping

    context = {
        'order': order,
        'items': processed_items,
        'user': request.user,
        'shipping': shipping,
        'grand_total': grand_total,
    }
   
    logo_path = finders.find('img/logo/logo.png')  # Adjust path as needed
    if logo_path:
       with open(logo_path, "rb") as img_file:
        context['logo_base64'] = base64.b64encode(img_file.read()).decode('utf-8')
    else:
        context['logo_base64'] = ''

    signature_path = finders.find('img/signatures.jpg')
    if signature_path:
       with open(signature_path, "rb") as img_file:
        context['signature_base64'] = base64.b64encode(img_file.read()).decode('utf-8')
    else:
       context['signature_base64'] = ''
        
    html = render_to_string('htmldemo.net/invoice.html', context)
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Users\RUDRA PATEL\PycharmProjects\AGRO_BUILD_final 1\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {
        'enable-local-file-access': None,
        'encoding': 'UTF-8',
    }
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{order.id}.pdf'
    return response

@login_required(login_url='/login/')
def get_notifications(request):
    notifications = NotificationHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = [{
        'message': n.message,
        'product_name': n.product.P_name,
        'product_img': n.product.P_img.url if n.product.P_img else '',
        'timestamp': n.created_at.isoformat()
    } for n in notifications]
    return JsonResponse({'notifications': data})

@login_required(login_url='/login/')
def view_all_notifications(request):
    notifications = NotificationHistory.objects.filter(user=request.user).order_by('-created_at')
    # Optionally mark as read:
    notifications.update(is_read=True)
    return render(request, 'htmldemo.net/notifications.html', {'notifications': notifications})

@login_required(login_url='/login/')
def delete_notification(request, id):
    notification = get_object_or_404(NotificationHistory, id=id, user=request.user)
    notification.delete()
    return redirect('view_all_notifications')

@login_required(login_url='/login/')
def clear_notifications(request):
    NotificationHistory.objects.filter(user=request.user).delete()
    return redirect('view_all_notifications')

@login_required(login_url='/login/')
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
                feedback.name = request.user.get_full_name() or request.user.username
                feedback.email = request.user.email
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('feedback')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email
            }
        form = FeedbackForm(initial=initial)
    
    return render(request, 'htmldemo.net/feedback.html', {'form': form})

def search(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    
    if len(query) < 3:
        return render(request, 'htmldemo.net/search.html', {
            'query': query,
            'message': 'Please enter at least 3 characters to search'
        })
    
    products = Product.objects.filter(
        Q(P_name__icontains=query) | 
        Q(P_Description__icontains=query)
    )
    
    # If searching from a category page, filter by that category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(categories=category)
    
    # For AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        results = []
        for product in products[:10]:
            results.append({
                'P_id': product.P_id,
                'P_name': product.P_name,
                'P_img': product.P_img.name if product.P_img else '',
                'P_price': str(product.P_price),
                'category': ', '.join([cat.name for cat in product.categories.all()])
            })
        return JsonResponse({'results': results})
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'htmldemo.net/search.html', {
        'products': page_obj,
        'query': query,
        'category_slug': category_slug
    })

def search_ajax(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    
    if len(query) < 3:
        return JsonResponse({'results': []})
    
    products = Product.objects.filter(
        Q(P_name__icontains=query) | 
        Q(P_Description__icontains=query)
    )
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(categories=category)
    
    results = []
    for product in products[:10]:
        results.append({
            'P_id': product.P_id,
            'P_name': product.P_name,
            'P_img': product.P_img.name if product.P_img else '',
            'P_price': str(product.P_price),
            'category': ', '.join([cat.name for cat in product.categories.all()])
        })
    
    return JsonResponse({'results': results})

def blog_list(request):
    blogs = Blog.objects.all().order_by('-date')
    return render(request, 'htmldemo.net/blog.html', {'blogs': blogs})
    
def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    comments = blog.comments.all().order_by('-created_at')
    related_blogs = Blog.objects.filter(type=blog.type).exclude(id=id)[:3]
    recent_posts = Blog.objects.all().order_by('-date')[:4]
    recent_comments = BlogComment.objects.all().order_by('-created_at')[:4]

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        if name and email and message:
            BlogComment.objects.create(blog=blog, name=name, email=email, message=message)
            return redirect('blog_detail', id=blog.id)

    return render(request, 'htmldemo.net/blog-details.html', {
        'blog': blog,
        'comments': comments,
        'related_blogs': related_blogs,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
    })

@login_required(login_url='/login/')
def save_contact(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
            created_at=timezone.now()
        )
        messages.success(request, "Thank you for contacting us! We'll get back to you soon.")
        return redirect('contactus') 
    
    return redirect('contactus')

@require_POST
@login_required(login_url='/login/')
def update_cart(request):
    for item_id, quantity in request.POST.items():
        if item_id.startswith('quantity_'):
            item_pk = int(item_id.split('_')[1])
            try:
                cart_item = CartItem.objects.get(id=item_pk, user=request.user)
                cart_item.quantity = max(1, int(quantity))  
                cart_item.save()
            except CartItem.DoesNotExist:
                continue
    return redirect('cart')

@login_required(login_url='/login/')
def my_account(request, order_id=None):
    # Fetch user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Fetch all user orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginate orders
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    order = None
    subtotal = Decimal('0.00')
    shipping = Decimal('0.00')
    total = Decimal('0.00')

    if order_id:
        # Fetch specific order
        order = get_object_or_404(Order, id=order_id, user=request.user)
        # Calculate subtotal from order items
        subtotal = sum(Decimal(str(item.price)) * Decimal(item.quantity) for item in order.items.all())
        shipping = Decimal('100.00')
        total = subtotal + shipping

        # Validate and fix total_amount if incorrect
        if order.total_amount != total:
            print(f"Warning: Order {order.id} total_amount mismatch. Expected: {total}, Stored: {order.total_amount}")
            order.total_amount = total
            order.save()

        # Debug values
        print(f"My Account Order Debug: order_id={order_id}, subtotal={subtotal}, shipping={shipping}, total={total}, items={[(item.product.P_name, item.quantity, item.price) for item in order.items.all()]}")

    return render(request, 'htmldemo.net/my-account.html', {
        'user': request.user,
        'profile': profile,
        'orders': page_obj,  # Paginated orders
        'order': order,
        'subtotal': float(subtotal),
        'shipping': float(shipping),
        'total': float(total),
    })

@login_required(login_url='/login/')
def update_account(request):
    if request.method == 'POST':
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
       
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        profile.phone = request.POST.get('phone')
        profile.dob = request.POST.get('dob')
        profile.gender = request.POST.get('gender')
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']
        profile.save()
        messages.success(request, 'Account details updated successfully!')
    return redirect('my_account')

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url='/login/')
def add_to_cart_from_wishlist(request, product_id):
    product = get_object_or_404(Product, P_id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@require_POST
@login_required(login_url='/login/')
def remove_from_cart(request):
    item_id = request.POST.get('item_id')
    CartItem.objects.filter(id=item_id, user=request.user).delete()
    return redirect('cart')

def index(request):
    if request.user.is_authenticated:
        wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('product__P_id', flat=True))
        cart_ids = set(CartItem.objects.filter(user=request.user).values_list('product__P_id', flat=True))
    else:
        wishlist_ids = set()
        cart_ids = set()
    
    allProds = []
    categories_to_show = ['indoor plants', 'Fruit Seeds', 'Garden Tools']
    
    for category_name in categories_to_show:
        category = Category.objects.filter(name__iexact=category_name).first()
        if category:
            prod = Product.objects.filter(categories=category)
            n = len(prod)
            if n > 0:
                nSlides = n // 4 + ceil((n / 4) - (n // 4))
                allProds.append([prod, range(1, nSlides), nSlides, category_name])
    
    cart_message = request.session.pop('cart_message', None)
    return render(request, 'htmldemo.net/index.html', {'allProds': allProds, 'wishlist_ids': wishlist_ids, 'cart_ids': cart_ids, 'cart_message': cart_message})

def account(request): return render(request, 'htmldemo.net/my-account.html')

@login_required(login_url='/login/')
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'htmldemo.net/wishlist.html', {'wishlist_items': wishlist_items})

@login_required(login_url='/login/')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, P_id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
        status = 'removed'
    else:
        status = 'added'
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': status})
    return redirect('wishlist')

@login_required(login_url='/login/')
def remove_from_wishlist(request, product_id):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product__P_id=product_id)
    wishlist_item.delete()
    return redirect('wishlist') 

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, P_id=product_id)
    cart_item = CartItem.objects.filter(user=request.user, product=product).first()

    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if cart_item:
                cart_item.delete()
                return JsonResponse({'status': 'removed', 'message': f"{product.P_name} removed from cart"})
            else:
                CartItem.objects.create(user=request.user, product=product, quantity=1)
                return JsonResponse({'status': 'added', 'message': f"{product.P_name} added to cart"})
        # fallback for normal POST (not AJAX)
        if cart_item:
            cart_item.delete()
            messages.success(request, f"{product.P_name} removed from cart")
        else:
            CartItem.objects.create(user=request.user, product=product, quantity=1)
            messages.success(request, f"{product.P_name} added to cart")
        return redirect(request.POST.get('return_url', 'index'))

    return redirect('index')

def basic(request): return render(request, 'htmldemo.net/basic.html')

@login_required(login_url='/login/')
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    subtotal = sum(item.product.P_price * item.quantity for item in cart_items)
    shipping = 100
    total = subtotal + shipping
    return render(request, 'htmldemo.net/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total
    })

@login_required(login_url='/login/')
def checkout(request):
    # Initialize variables
    items = []
    subtotal = Decimal('0.00')
    has_plants = False
    is_buy_now = False
    buy_now_product = None
    buy_now_quantity = 1

    # Handle GET request (initial page load)
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        quantity = request.GET.get('quantity')

        if product_id and quantity:  # Buy Now flow
            try:
                is_buy_now = True
                buy_now_product = Product.objects.get(P_id=product_id)
                buy_now_quantity = int(quantity)
                if buy_now_quantity < 1:
                    raise ValueError("Quantity must be at least 1")
                # Validate product price
                if buy_now_product.P_price is None or buy_now_product.P_price <= 0:
                    raise ValueError(f"Invalid price for product {buy_now_product.P_name}")
                subtotal = Decimal(str(buy_now_product.P_price)) * Decimal(buy_now_quantity)
                items = [{
                    'product': buy_now_product,
                    'quantity': buy_now_quantity,
                    'subtotal': subtotal,
                }]
                has_plants = hasattr(buy_now_product, 'is_plant') and buy_now_product.is_plant()
            except Product.DoesNotExist:
                messages.error(request, "Product not found.")
                return redirect('home')
            except ValueError as e:
                messages.error(request, f"Invalid quantity or price: {str(e)}")
                return redirect('home')
        else:  # Cart Buy flow
            cart_items = CartItem.objects.filter(user=request.user).select_related('product')
            if not cart_items.exists():
                messages.error(request, "Your cart is empty.")
                return redirect('cart')
            for item in cart_items:
                # Validate product price
                if item.product.P_price is None or item.product.P_price <= 0:
                    messages.error(request, f"Invalid price for product {item.product.P_name}")
                item_subtotal = Decimal(str(item.product.P_price)) * Decimal(item.quantity)
                items.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'subtotal': item_subtotal,
                })
                subtotal += item_subtotal
            has_plants = any(hasattr(item.product, 'is_plant') and item.product.is_plant() for item in cart_items)

    # Calculate total
    shipping = Decimal('100.00')
    total = subtotal + shipping

    # Debug values
    print(f"Checkout Debug: subtotal={subtotal}, shipping={shipping}, total={total}, items={[(item['product'].P_name, item['quantity'], item['subtotal']) for item in items]}")

    # Handle POST request (form submission)
    if request.method == 'POST':
        try:
            payment_method = request.POST.get('payment_method')
            upi_txn = request.POST.get('upi_txn', '').strip()
            is_buy_now = request.POST.get('is_buy_now') == 'true'

            # Validate UPI payment
            if payment_method == 'upi' and not upi_txn:
                messages.error(request, "Please provide UPI transaction ID for UPI payments")
                return redirect('checkout')

            # Create Order
            order = Order.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                zip_code=request.POST.get('zip_code'),
                mobile_number=request.POST.get('mobile_number'),
                total_amount=total,
                payment_method=payment_method,
                upi_transaction_number=upi_txn if payment_method == 'upi' else None,
                payment_status='Paid' if payment_method == 'upi' else 'Pending',
            )

            # Handle Buy Now order
            if is_buy_now:
                product_id = request.POST.get('buy_now_product_id')
                quantity = request.POST.get('buy_now_quantity')
                try:
                    product = Product.objects.get(P_id=product_id)
                    quantity = int(quantity)
                    if quantity < 1:
                        raise ValueError("Quantity must be at least 1")
                    if product.P_price is None or product.P_price <= 0:
                        raise ValueError(f"Invalid price for product {product.P_name}")
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=product.P_price,
                        quantity=quantity
                    )
                    # Watering Reminder for Buy Now
                    if hasattr(product, 'is_plant') and product.is_plant() and request.POST.get('enable_notifications') == 'true':
                        allow_website = request.POST.get('allow_website') == 'true'
                        allow_gmail = request.POST.get('allow_gmail') == 'true'
                        gmail = request.POST.get('gmail')
                        morning_time = request.POST.get('morning_time', '08:00')
                        evening_time = request.POST.get('evening_time', '18:00')
                        for cat in product.categories.filter(name__icontains='plant'):
                            WateringReminder.objects.update_or_create(
                                user=request.user,
                                product=product,
                                category=cat,
                                defaults={
                                    'morning_time': morning_time,
                                    'evening_time': evening_time,
                                    'allow_website': allow_website,
                                    'allow_gmail': allow_gmail,
                                    'gmail': gmail,
                                    'is_active': True,
                                }
                            )
                except Product.DoesNotExist:
                    messages.error(request, "Selected product not found.")
                    return redirect('checkout')
                except ValueError as e:
                    messages.error(request, f"Invalid quantity or price: {str(e)}")
                    return redirect('checkout')
            else:
                # Handle Cart Buy order
                cart_items = CartItem.objects.filter(user=request.user).select_related('product')
                if not cart_items.exists():
                    messages.error(request, "Your cart is empty.")
                    return redirect('cart')
                for item in cart_items:
                    if item.product.P_price is None or item.product.P_price <= 0:
                        messages.error(request, f"Invalid price for product {item.product.P_name}")
                        return redirect('cart')
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.product.P_price,
                        quantity=item.quantity
                    )
                    # Watering Reminder for Cart Items
                    if hasattr(item.product, 'is_plant') and item.product.is_plant() and request.POST.get('enable_notifications') == 'true':
                        allow_website = request.POST.get('allow_website') == 'true'
                        allow_gmail = request.POST.get('allow_gmail') == 'true'
                        gmail = request.POST.get('gmail')
                        morning_time = request.POST.get('morning_time', '08:00')
                        evening_time = request.POST.get('evening_time', '18:00')
                        for cat in item.product.categories.filter(name__icontains='plant'):
                            WateringReminder.objects.update_or_create(
                                user=request.user,
                                product=item.product,
                                category=cat,
                                defaults={
                                    'morning_time': morning_time,
                                    'evening_time': evening_time,
                                    'allow_website': allow_website,
                                    'allow_gmail': allow_gmail,
                                    'gmail': gmail,
                                    'is_active': True,
                                }
                            )
                cart_items.delete()  # Clear cart only for Cart Buy

            return redirect('order_confirmation', order_id=order.id)

        except Exception as e:
            messages.error(request, f"Error processing your order: {str(e)}")
            return redirect('checkout')

    return render(request, 'htmldemo.net/checkout.html', {
        'items': items,
        'subtotal': float(subtotal),
        'shipping': float(shipping),
        'total': float(total),
        'has_plants': has_plants,
        'is_buy_now': is_buy_now,
    })

@login_required(login_url='/login/')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Calculate subtotal from order items
    subtotal = sum(Decimal(str(item.price)) * Decimal(item.quantity) for item in order.items.all())
    shipping = Decimal('100.00')
    total = subtotal + shipping

    # Validate total_amount
    if order.total_amount != total:
        print(f"Warning: Order {order.id} total_amount mismatch. Expected: {total}, Stored: {order.total_amount}")
        order.total_amount = total
        order.save()

    # Debug values
    print(f"Order Confirmation Debug: order_id={order_id}, subtotal={subtotal}, shipping={shipping}, total={total}, items={[(item.product.P_name, item.quantity, item.price) for item in order.items.all()]}")

    return render(request, 'htmldemo.net/order_confirmation.html', {
        'order': order,
        'subtotal': float(subtotal),
        'shipping': float(shipping),
        'total': float(total),
        'order_items': order.items.all()
    })

def blog(request): return render(request, 'htmldemo.net/blog-details.html')
def aboutus(request): return render(request, 'htmldemo.net/about.html')
def contactus(request): return render(request, 'htmldemo.net/contact.html')
def faq(request): return render(request, 'htmldemo.net/faq.html')

def prod_view(request):
    prod_id = request.GET.get('myid')
    product = get_object_or_404(Product, P_id=prod_id)
    cart_ids = set(CartItem.objects.filter(user=request.user).values_list('product__P_id', flat=True)) if request.user.is_authenticated else set()
    wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('product__P_id', flat=True)) if request.user.is_authenticated else set()
    return render(request, 'htmldemo.net/prod_view.html', {'product': product, 'cart_ids': cart_ids, 'wishlist_ids': wishlist_ids})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(categories=category)
    subcategories = category.children.all()
    if request.user.is_authenticated:
        wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('product__P_id', flat=True))
        cart_ids = set(CartItem.objects.filter(user=request.user).values_list('product__P_id', flat=True))
    else:
        wishlist_ids = set()
        cart_ids = set()
    
    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
        'is_main_category': category.parent is None,
        'wishlist_ids': wishlist_ids,
        'cart_ids': cart_ids,
    }
    return render(request, 'htmldemo.net/category_products.html', context)