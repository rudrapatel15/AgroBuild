from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('wishlist/', views.wishlist, name="wishlist"),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('basic/', views.basic, name="basic"),
    path('update-account/', views.update_account, name='update_account'),
    path('my-account/', views.my_account, name='my_account'),
    path('prod_view/', views.prod_view, name='prod_view'),
    path('cart/', views.cart, name='cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart_from_wishlist, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/verify/', views.payment_verification, name='payment_verification'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('home/', views.index, name='home'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('contactus/', views.contactus, name='contactus'),
    path('save-contact/', views.save_contact, name='save_contact'),
    path('logout/', views.logout_view, name='logout'),
    path('faq/', views.faq, name='faq'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('search/', views.search, name='search'),
    path('search/ajax/', views.search_ajax, name='search_ajax'),
    path('feedback/', views.feedback, name='feedback'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)