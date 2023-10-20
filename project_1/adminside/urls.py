from django.urls import path
from . import views
from django.conf import settings  # Import settings module
from django.conf.urls.static import static



urlpatterns = [
    path('',views.adminhome,name='spadmin'),

    path('dataadd/',views.dataAdd,name = 'dataadd'),
    path('edit/<int:product_id>/', views.edit_data, name='edit_data'),

    path('allproducts/', views.allproducts, name='allproducts'),
    path('delete_product/<int:product_id>/',views.delete_product, name='delete_product'),
    \
    path('add_category/', views.add_category, name='add_category'),
    path('category_list/', views.category_list, name='category_list'),

    path('all_users/', views.all_users, name='all_users'),

    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),

    path('delivery_sec/',views.delivery_sec , name = 'delivery'),
    path('update_delivery_status/<int:order_id>/', views.update_delivery_status, name='update_delivery_status'),

    path('sales_report/', views.generate_sales_report, name='sales_report'),

    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('make_superuser/<int:user_id>/', views.make_superuser, name='make_superuser'),
    path('remove_superuser/<int:user_id>/', views.remove_superuser, name='remove_superuser'),

    path('discount-coupon/', views.discount_coupon, name='discount_coupon'),
    path('add_coupon/', views.add_coupon, name='add_coupon'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)