from .models import CartItem  # Replace 'your_app' with the actual app name where CartItem is defined

def cart_data(request):
    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user)
        subtotal = sum(item.total_price() for item in items)
        return {
            'mini_cart_items': items,
            'mini_cart_total': subtotal
        }
    return {
        'mini_cart_items': [],
        'mini_cart_total': 0
    }

def cart_items_processor(request):
    cart_items = []
    cart_total = 0
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_total = sum(item.product.P_price * item.quantity for item in cart_items)
    return {'cart_items': cart_items, 'cart_total': cart_total}