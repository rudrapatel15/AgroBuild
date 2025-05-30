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

def get_timedelta_for_frequency(freq):
    if freq == 'daily':
        return timedelta(days=1)
    elif freq == 'twice':
        return timedelta(hours=12)
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

            for order in delivered_orders:
                if order.payment_status != 'paid':
                    continue
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

                    for t in times:
                        # Only send if last_sent is None or enough time has passed
                        if not reminder.last_sent or (now - reminder.last_sent) >= get_timedelta_for_frequency(freq):
                            # Check if current time is within 5 minutes of the scheduled time
                            if abs((now.time().hour * 60 + now.time().minute) - (t.hour * 60 + t.minute)) < 5:
                                is_morning = (t.hour < 15)
                                customer_name = reminder.user.first_name or reminder.user.username
                                plant_name = product.P_name
                                subject = ""
                                msg_plain = ""
                                msg_html = ""
                                if is_morning:
                                    subject = f"🌱 Time to Hydrate Your {plant_name}!"
                                    msg_plain = (
                                        f"Dear {customer_name},\n\n"
                                        f"Good morning! Just a gentle reminder that it's time to water your {plant_name}.\n\n"
                                    )
                                    msg_html = (
                                       f"<b>Dear {customer_name},</b><br><br>"
                                       f"Time to refresh your plants. A little water brings them to life.<br>"
                                        f"Good morning! Just a gentle reminder that it's time to water your <b>{plant_name}</b>.<br><br>"
                                        "<b>💧 Watering Tip:</b><ul>"
                                        "<li>Use the recommended amount of water for your plant</li>"
                                        "<li>Ensure proper drainage to avoid overwatering</li>"
                                        "<li>Check soil moisture by touching the top 1-2 inches</li>"
                                        "</ul>"
                                        "Your plant will thrive with this morning hydration!<br><br>"
                                        "<b>With green regards,<br>"
                                        "The AGRO BUILD Team</b><br><br>"
                                        "Contact Info <br>"
                                        "B-42 AKRITIGARDEN, NEHRUNAGAR<br>"
                                        "AHMEDABAD, 380015<br>"
                                        "📞 8128383925<br>"
                                        "✉️ shopmulti9859@gmail.com<br>"
                                    )
                                else:
                                    subject = f"🌿 Evening Care for Your {plant_name}"
                                    msg_plain = (
                                        f"Hello {customer_name},\n\n"
                                        f"Don't forget to give your 🌿{plant_name} some evening love!\n\n"
                                    )
                                    msg_html = (
                                        f"<b>Hello {customer_name},</b><br><br>"
                                        f"Time to refresh your plants. A little water brings them to life.<br>"
                                        f"Don't forget to give your <b>{plant_name}</b> some evening love!<br><br>"
                                        "<b>🌻 Best Practices:</b><ul>"
                                        "<li>Water at the base to keep leaves dry</li>"
                                        "<li>Use room-temperature water</li>"
                                        "<li>Adjust quantity based on seasonal needs</li>"
                                        "</ul>"
                                        "Thank you for nurturing your green companion!<br><br>"
                                        "<b>Warmly,<br>AGRO BUILD</b><br><br>"
                                        "Contact Info <br>"
                                        "B-42 AKRITIGARDEN, NEHRUNAGAR<br>"
                                        "AHMEDABAD, 380015<br>"
                                        "📞 8128383925<br>"
                                        "✉️ shopmulti9859@gmail.com<br>"   
                                    )
                                # Send the email
                                send_mail(
                                    subject=subject,
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
                                break