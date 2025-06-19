from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', include('agrobuild.urls')),
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('registration/', views.register_view, name="registration"),
    path('otp-verify/', views.otp_verify_view, name='otp_verify'),
    # NEW LINE ADDED: This maps the AJAX request for resending OTP to its view
    path('resend-otp-ajax/', views.resend_otp_ajax_view, name='resend_otp_ajax'),
    
] 
if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
