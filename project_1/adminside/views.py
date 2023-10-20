# Import the  model on userside app
from userside.models import Product ,Category,CustomUser,Supplier,Stock,Order,OrderItem ,DiscountCoupon 
from django.views.decorators.cache import cache_control, never_cache
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Sum

# home page =============================================================================

@login_required
def adminhome(request):
    if request.user.is_staff:
        total_sale_amount = calculate_total_sale_amount() 
        total_users = get_total_users_count() 
        total_products = get_total_products_count()  
        total_delivered_orders = get_total_delivered_orders_count()  

        context = {
            'total_sale_amount': total_sale_amount,
            'total_users': total_users,
            'total_products': total_products,
            'total_delivered_orders': total_delivered_orders
        }

        return render(request, 'adminhome.html', context)
    else:
        return HttpResponse("You are not authorized to access this page.")

def calculate_total_sale_amount():
    return Order.objects.aggregate(total_sale=Sum('total_price'))['total_sale']

def get_total_users_count():
    return CustomUser.objects.count()

def get_total_products_count():
    return Product.objects.count()

def get_total_delivered_orders_count():
    return Order.objects.filter(order_status='delivered').count()

# Category Section =================================================

def category_list(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'category_list.html', context)

def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        if name:
            Category.objects.create(name=name)
            return redirect('category_list')  
    return render(request, 'addcategory.html')

# All Products ======================================================
def allproducts(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'allproducts.html', context)

def dataAdd(request):  
    if request.method == 'POST':
        modelname = request.POST.get('modelname', '')
        color = request.POST.get('color', '')
        brand = request.POST.get('brand', '')
        description = request.POST.get('description', '')
        price = request.POST.get('price', '')
        storage = request.POST.get('storage', '')
        image1 = request.FILES.get('image1', None)
        image2 = request.FILES.get('image2', None)
        image3 = request.FILES.get('image3', None)
        category_id = request.POST.get('category', None)
        stock_count = request.POST.get('stock_count', '')

        if modelname and color and brand and price and category_id:
            category = Category.objects.get(id=category_id)
            product = Product.objects.create(
                modelname=modelname,
                color=color,
                brand=brand,
                description=description,
                price=price,
                storage=storage,
                image1=image1,
                image2=image2,
                image3=image3,
                category=category,
            )
            stock = Stock.objects.create(
                product=product,
                stock_count=stock_count
            )
            return redirect('spadmin')  
        else:
            error_message = "Please fill in all required fields."
            categories = Category.objects.all()
            context = {
                'categories': categories,
                'error_message': error_message,
            }
            return render(request, 'addproducts.html', context)
    
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'addproducts.html', context)



def edit_data(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    stock = get_object_or_404(Stock, product=product_id)

    if request.method == 'POST':
        modelname = request.POST.get('modelname', '')
        color = request.POST.get('color', '')
        brand = request.POST.get('brand', '')
        description = request.POST.get('description', '')
        price = request.POST.get('price', '')
        storage = request.POST.get('storage', '')
        image1 = request.FILES.get('image1', None)
        image2 = request.FILES.get('image2', None)
        image3 = request.FILES.get('image3', None)
        category_id = request.POST.get('category', None)
        stock_count = request.POST.get('stock_count', '')

        if modelname and color and brand and price and category_id:
            category = get_object_or_404(Category, id=category_id)

            # Update the existing product
            product.modelname = modelname
            product.color = color
            product.brand = brand
            product.description = description
            product.price = price
            product.storage = storage
            product.image1 = image1 if image1 else product.image1
            product.image2 = image2 if image2 else product.image2
            product.image3 = image3 if image3 else product.image3
            product.category = category
            product.save()

            stock.stock_count = stock_count
            stock.save()

            return redirect('spadmin')
        else:
            error_message = "Please fill in all required fields."
            categories = Category.objects.all()
            context = {
                'categories': categories,
                'error_message': error_message,
            }
            return render(request, 'edit_data.html', context)

    categories = Category.objects.all()
    context = {'product': product, 'category': categories, 'stock': stock}
    return render(request, 'edit_data.html', context)


def delete_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('spadmin') 
    context = {'product': product}
    return render(request, 'delete_product.html', context)

# add supplier ============================================================

def add_supplier(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        address = request.POST['address']
        mail = request.POST['mail']
        name = request.POST['name']
       
        new_supplier = Supplier.objects.create(
            phone_number=phone_number,
            address=address,
            mail=mail,
            name=name,
        )
        return redirect('supplier_list')
    return render(request, 'add_supplier.html')

def supplier_list(request):
    suppliers = Supplier.objects.all()
    context =  {'suppliers': suppliers}
    return render(request, 'supplier_list.html',context)

def edit_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        # Update the supplier's fields based on POST data
        supplier.phone_number = request.POST['phone_number']
        supplier.address = request.POST['address']
        supplier.mail = request.POST['mail']
        supplier.name = request.POST['name']
        supplier.save()
        return redirect('supplier_list')
    return render(request, 'edit_supplier.html', {'supplier': supplier})

def all_users(request):
    users = CustomUser.objects.all()
    context = {'users': users}
    return render(request, 'all_users.html', context)



def delivery_sec(request):
    orders = Order.objects.all()
    context = { 'orders' : orders }
    return render(request, 'delivery_sec.html', context)


def update_delivery_status(request, order_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        try :
            order = Order.objects.get(pk=order_id)
            order.order_status = status
            order.save()
            messages.success(request, 'Order has been successfully cancelled.')
        

        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
        return redirect('delivery')
    return redirect('delivery')




def generate_sales_report(request):
    total_sales, last_month_sales, recent_orders = get_sales_data()

    context = {
        'total_sales': total_sales,
        'last_month_sales': last_month_sales,
        'recent_orders': recent_orders
    }
    return render(request, 'sales_report.html', context)

# sales section ===========================================================================
def get_sales_data():
    # Retrieve all orders and calculate the total sales amount
    total_sales = Order.objects.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0

    # Retrieve all orders in the last month and calculate the total sales amount
    last_month = datetime.now() - timedelta(days=30)
    last_month_sales = Order.objects.filter(order_date__gte=last_month).aggregate(last_month_sales=Sum('total_price'))['last_month_sales'] or 0

    # Retrieve orders from the last 5 days
    last_5_days = datetime.now() - timedelta(days=5)
    recent_orders = Order.objects.filter(order_date__gte=last_5_days)

    return total_sales, last_month_sales, recent_orders

# Each user defs ============================================================================= 
User = get_user_model()
def block_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = False
    user.save()
    return redirect('all_users')  

def unblock_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    return redirect('all_users') 

def make_superuser(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_staff = True
    user.save()
    return redirect('all_users') 

def remove_superuser(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_staff = False
    user.save()
    return redirect('all_users') 


# discont section ============================================================

def discount_coupon(request):
    coupons = DiscountCoupon.objects.all()
    return render(request, 'discount_coupon.html', {'coupons': coupons})

def add_coupon(request):
    if request.method == 'POST':
        discount_amount = request.POST.get('discount_amount')
        valid_till = request.POST.get('valid_till')
        category_id = request.POST.get('category_id', None)
        product_id = request.POST.get('product_id', None)

        category = Category.objects.get(pk=category_id) if category_id else None
        product = Product.objects.get(pk=product_id) if product_id else None

        coupon = DiscountCoupon(
            discount_amount=discount_amount,
            valid_till=valid_till,
            category_id=category,
            product_id=product
        )
        coupon.save()
        return redirect('discount_coupon') 

    coupons = DiscountCoupon.objects.all()
    return render(request, 'discount_coupon.html', {'coupons': coupons})

# ==================================================================================


