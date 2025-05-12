from django.core.management.base import BaseCommand
from django.utils import timezone
from agrobuild.models import WateringReminder, Order, NotificationHistory
from django.core.mail import send_mail
from datetime import timedelta, date

print("Watering Reminder Command Loaded")
def get_season():
    today = date.today()
    month = today.month
    if 7 <= month <= 10:
        return 'monsoon'
    elif 3 <= month <= 6:
        return 'summer'
    else:
        return 'winter'

# ...existing imports...
from agrobuild.models import WateringReminder, Order, NotificationHistory
# ...existing code...

class Command(BaseCommand):
    help = 'Send watering reminders to users based on season and user-selected time'

    def handle(self, *args, **options):
        now = timezone.localtime()
        season = get_season()
        for reminder in WateringReminder.objects.filter(is_active=True, allow_gmail=True):
            # Only after order is delivered
            delivered_orders = Order.objects.filter(
                user=reminder.user, items__product__categories=reminder.category, status='delivered'
            ).distinct()
            if not delivered_orders.exists():
                continue

            product_names = set()
            first_product = None
            for order in delivered_orders:
                for item in order.items.filter(product__categories=reminder.category):
                    product_names.add(item.product.P_name)
                    if not first_product:
                        first_product = item.product
            product_list = ', '.join(product_names) if product_names else 'your plant'

            send = False
            msg = (
                f"🌿 Time to water your {reminder.category.name} ({season})\n"
                f"Products: {product_list}"
            )
            # Check if it's time to send (within 5 minutes of selected time)
            if season == 'monsoon':
                if not reminder.last_sent or (now - reminder.last_sent) > timedelta(days=2):
                    if abs((now.time().hour * 60 + now.time().minute) - (reminder.morning_time.hour * 60 + reminder.morning_time.minute)) < 5:
                        send = True
            elif season == 'winter':
                if not reminder.last_sent or (now - reminder.last_sent) > timedelta(days=1):
                    if abs((now.time().hour * 60 + now.time().minute) - (reminder.morning_time.hour * 60 + reminder.morning_time.minute)) < 5:
                        send = True
            elif season == 'summer':
                for t in [reminder.morning_time, reminder.evening_time]:
                    if abs((now.time().hour * 60 + now.time().minute) - (t.hour * 60 + t.minute)) < 5:
                        if not reminder.last_sent or (now - reminder.last_sent) > timedelta(hours=11):
                            send = True
                            break

            if send and reminder.gmail:
                # Send Gmail notification
                send_mail(
                    subject="Watering Reminder",
                    message=msg + "\n\nThis is your scheduled watering reminder from Agro Build.",
                    from_email=None, 
                    recipient_list=[reminder.gmail],
                )
                # Also create website notification
                if first_product:
                    NotificationHistory.objects.create(
                        user=reminder.user,
                        product=first_product,
                        message=msg
                    )
                reminder.last_sent = now
                reminder.save()