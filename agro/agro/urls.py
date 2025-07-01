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
    path('resend-otp-ajax/', views.resend_otp_ajax_view, name='resend_otp_ajax'), 
    # Chatbot API endpoint
    path('api/chatbot/', views.chatbot_response, name='chatbot_response'),
    
    # Chat history endpoint
    path('api/chat-history/', views.get_chat_history, name='get_chat_history'),
    
    # Clear chat history endpoint
    path('api/clear-chat-history/', views.clear_chat_history, name='clear_chat_history'),
    
    # Chatbot test page
    path('chatbot-test/', views.chatbot_test_page, name='chatbot_test'),
] 

if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
