from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'userside' 

urlpatterns = [
    
    path('user_profile/', views.user_profile, name='user_profile'),
    path('add_profile_data/', views.add_profile_data, name='add_profile_data'),

    path('product/<int:product_id>/', views.product_detail, name='product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    

    path('cart/', views.view_cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase_quantity/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease_quantity/', views.decrease_quantity, name='decrease_quantity'),

    path('checkout/', views.checkout, name='checkout'),  
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
    path('order_showing/', views.order_showing, name='order_showing'),
    path('order_tracking/<int:order_id>/', views.order_tracking, name='order_tracking'),
    path('all_orders/', views.all_orders, name='all_orders'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    path('search/', views.search_products, name='search_products'),
    path('payment-methods/', views.payment_methods, name='payment_methods'),

    path('',views.SignUpPage,name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('home/',views.homepage,name='home'),
    path('logout/',views.LogOutPage,name='logout'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
