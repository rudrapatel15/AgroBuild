// sw.js
self.addEventListener('push', function(event) {
    let notificationData = {};
    try {
        notificationData = event.data.json();
    } catch (e) {
        notificationData = {
            title: 'Watering Reminder',
            body: 'Time to water your plants!',
            icon: '/static/img/logo.png',
            url: '/notifications/'
        };
    }

    const options = {
        body: notificationData.body,
        icon: notificationData.icon,
        data: {
            url: notificationData.url
        }
    };

    event.waitUntil(
        self.registration.showNotification(notificationData.title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url || '/notifications/')
    );
});