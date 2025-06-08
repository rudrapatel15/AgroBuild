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
    
] 
if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
