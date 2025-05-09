# check_watering.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from agrobuild.models import PlantNotification
from agrobuild.notifications import send_browser_notification
from datetime import datetime, time

class Command(BaseCommand):
    help = 'Check and send watering notifications'

    def handle(self, *args, **options):
        now = timezone.now()
        current_time = now.time()
        current_hour = now.hour
        
        # Check if it's morning or evening notification time
        is_morning_time = 6 <= current_hour <= 9
        is_evening_time = 17 <= current_hour <= 19
        
        if is_morning_time or is_evening_time:
            notifications = PlantNotification.objects.filter(
                is_active=True,
                allow_push=True
            )
            
            for notification in notifications:
                # Check if it's time to send notification based on user's settings
                if (is_morning_time and notification.morning_time.hour == current_hour) or \
                   (is_evening_time and notification.evening_time.hour == current_hour):
                    
                    title = "🌿 Watering Reminder"
                    body = f"Time to water your {notification.product.P_name}"
                    
                    # Send browser notification
                    send_browser_notification(
                        notification.user,
                        title,
                        body,
                        notification.product.P_img.url if notification.product.P_img else None
                    )
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'Sent watering notification to {notification.user.username}'
                    ))