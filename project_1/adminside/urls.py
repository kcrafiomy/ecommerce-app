from django.urls import path
from . import views
from django.conf import settings  # Import settings module
from django.conf.urls.static import static



urlpatterns = [
     path('',views.SignUpPage,name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('spadmin/',views.adminhome,name='spadmin'),
    path('logout/',views.LogOutPage,name='logout'),
    # path('',views.adminhome,name = 'spadmin'),
    path('dataadd/',views.dataAdd,name = 'dataadd'),
    path('edit/<int:product_id>/', views.edit_data, name='edit_data'),
    path('allproducts/', views.allproducts, name='allproducts'),
    path('delete_product/<int:product_id>/',views.delete_product, name='delete_product'),
    path('add_category/', views.add_category, name='add_category'),
    path('category_list/', views.category_list, name='category_list'),
    path('all_users/', views.all_users, name='all_users'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)