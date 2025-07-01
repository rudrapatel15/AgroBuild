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

    # Agriculture news pages
    path('agriculture-news/', views.agriculture_news_page, name='agriculture_news'),
    
    # API endpoints for fetching news
    path('api/news/', views.fetch_agriculture_news, name='fetch_agriculture_news'),
    path('api/news/<str:category>/', views.fetch_category_news, name='fetch_category_news'),
    
    # API endpoints for fetching news
    path('api/news/', views.fetch_agriculture_news, name='fetch_agriculture_news'),
    path('api/news/<str:category>/', views.fetch_category_news, name='fetch_category_news'),
    
    # Chatbot API endpoint
    path('api/chatbot/', views.chatbot_response, name='chatbot_response'),
    
    # Chat history endpoint
    path('api/chat-history/', views.get_chat_history, name='get_chat_history'),
    
    # Clear chat history endpoint
    path('api/clear-chat-history/', views.clear_chat_history, name='clear_chat_history'),
    
    # Chatbot test page
    path('chatbot-test/', views.chatbot_test_page, name='chatbot_test'),
    
    # Test chatbot endpoint
    path('test-chatbot/', views.test_chatbot, name='test_chatbot'),
    
    # Debug weather endpoint
    path('debug-weather/', views.debug_weather, name='debug_weather'),
      
] 

if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
