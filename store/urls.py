from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Shop
    path('shop/', views.shop, name='shop'),
    path('shop/<str:category>/', views.shop_category, name='shop_category'),

    # Product
    path('product/<str:slug>/', views.product_detail, name='product_detail'),

    # Cart & Checkout
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Services page
    path('services/', views.services, name='services'),

    # Info pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact,name='contact'),
    path('faq/', views.faq, name='faq'),
    path('blog/', views.blog, name='blog'),

    # Add these inside urlpatterns in store/urls.py

path('login/', views.login_view, name='login'),
path('register/', views.register_view, name='register'),
path('logout/', views.logout_view, name='logout'),

path('account/', views.account_view, name='account'),
path('account/orders/', views.order_history_view, name='order_history'),
path('account/orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
path('account/wishlist/', views.wishlist_view, name='wishlist'),
path('account/wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),

path('track/', views.track_order_view, name='track_order'),
path('checkout/submit/', views.checkout_submit, name='checkout_submit'),
path('paystack/callback/', views.paystack_callback,name='paystack_callback' )
]
