from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'userside' 

urlpatterns = [
    
    path('user_profile/', views.user_profile, name='user_profile'),
    path('add_profile_data/', views.add_profile_data, name='add_profile_data'),

    path('product/<int:product_id>/', views.product_detail, name='product'),

    path('cart/', views.view_cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('',views.SignUpPage,name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('home/',views.homepage,name='home'),
    path('logout/',views.LogOutPage,name='logout')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
