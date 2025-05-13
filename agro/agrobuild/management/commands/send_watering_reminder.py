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

# Helper: get timedelta for frequency string
def get_timedelta_for_frequency(freq):
    if freq == 'daily':
        return timedelta(days=1)
    elif freq == 'twice':
        return timedelta(hours=12)  # twice a day
    elif freq == 'every_two_days':
        return timedelta(days=2)
    elif freq == 'weekly':
        return timedelta(days=7)
    return timedelta(days=1)

class Command(BaseCommand):
    help = 'Send watering reminders to users based on plant watering frequency and season'

    def handle(self, *args, **options):
        now = timezone.localtime()
        season = get_season()
        for reminder in WateringReminder.objects.filter(is_active=True, allow_gmail=True):
            delivered_orders = Order.objects.filter(
                user=reminder.user, items__product__categories=reminder.category, status='delivered'
            ).distinct()
            if not delivered_orders.exists():
                continue

            # For each plant in this category, check its watering frequency for this season
            notified_products = []
            for order in delivered_orders:
                if order.payment_status != 'paid':
                   continue  # Only process paid orders
                for item in order.items.filter(product__categories=reminder.category):
                    product = item.product
                    # Get frequency for this season
                    if season == 'summer':
                        freq = product.summer_watering
                        times = [reminder.morning_time, reminder.evening_time] if freq == 'twice' else [reminder.morning_time]
                    elif season == 'winter':
                        freq = product.winter_watering
                        times = [reminder.morning_time]
                    else:
                        freq = product.monsoon_watering
                        times = [reminder.morning_time]

                    # Check if it's time to send for this product
                    should_send = False
                    # For "twice" frequency, check both times; for others, just morning_time
                    for t in times:
                        # Only send if last_sent is None or enough time has passed
                        if not reminder.last_sent or (now - reminder.last_sent) >= get_timedelta_for_frequency(freq):
                            # Check if current time is within 5 minutes of the scheduled time
                            if abs((now.time().hour * 60 + now.time().minute) - (t.hour * 60 + t.minute)) < 5:
                                should_send = True
                                break
                    if should_send:
                        notified_products.append(product.P_name)
                        # Send Gmail notification
                        msg_plain = (
                            "Time to refresh your plants. A little water brings them to life.\n"
                            f"🌿 Time to water your {product.P_name} \n"
                        )
                        msg_html = (
                            "<b>Time to refresh your plants. A little water brings them to life.</b><br>"
                            f"🌿 Time to water your {product.P_name} <br>"
                        )
                        send_mail(
                            subject="Watering Reminder",
                            message=msg_plain,
                            from_email=None,
                            recipient_list=[reminder.gmail],
                            html_message=msg_html,
                        )
                        # Also create website notification
                        NotificationHistory.objects.create(
                            user=reminder.user,
                            product=product,
                            message=msg_plain
                        )
                        reminder.last_sent = now
                        reminder.save()