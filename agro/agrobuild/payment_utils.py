import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount, currency='INR'):
     data = {
         'amount': int(amount * 100),  
         'currency': currency,
         'payment_capture': 1  
     }
     order = client.order.create(data=data)
     return order
