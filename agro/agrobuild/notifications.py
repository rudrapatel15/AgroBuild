# notifications.py
from pywebpush import webpush, WebPushException
from django.conf import settings
import json

def send_browser_notification(user, title, body, icon=None):
    """
    Send browser push notification using Web Push API
    """
    try:
        # Get all active subscriptions for the user
        subscriptions = user.pushsubscription_set.filter(is_active=True)
        
        if not subscriptions.exists():
            return False
            
        icon_url = icon or f"{settings.STATIC_URL}img/logo.png"
        
        payload = {
            "title": title,
            "body": body,
            "icon": icon_url,
            "url": "/notifications/"  # URL to open when clicked
        }
        
        # Send to each subscription
        for subscription in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.keys["p256dh"],
                            "auth": subscription.keys["auth"]
                        }
                    },
                    data=json.dumps(payload),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims=settings.VAPID_CLAIMS
                )
            except WebPushException as e:
                print(f"WebPushException for user {user.username}: {e}")
                # Mark subscription as inactive if it fails
                subscription.is_active = False
                subscription.save()
        
        return True
    except Exception as e:
        print(f"Error sending notification: {e}")
    return False