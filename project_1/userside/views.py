from .models import CustomUser,CustomerPaymentMethod,Product,Stock,DiscountCoupon
from .models import Cart, CartItem, Product,Order,OrderItem,ProductComment
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.views.decorators.cache import cache_control, never_cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.http import Http404

# user login logout signup def ------------------------------------------
def SignUpPage(request):
    if 'username' in request.session:
        return redirect('userside:home')

    elif request.method == 'POST' :
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        
        if not (username and email and pass1 and pass2):
            messages.info(request,"Please fill required field")
            return redirect('userside:signup')
    
        elif pass1 != pass2:
            messages.info(request,"Password mismatch")
            return redirect('userside:signup')
       
        else:
            if CustomUser.objects.filter(username = username).exists():
                messages.info(request,"Username Already Taken")
                return redirect('userside:signup')
           
            elif CustomUser.objects.filter(email = email).exists():
                 messages.info(request,"Email Already Taken")
                 return redirect('userside:signup')
            else:
                my_user = CustomUser.objects.create_user(username=username, email=email, password=pass1)
                my_user.save()
            
        return redirect('userside:login')
    return render(request,'signup.html')
 
@never_cache
def LoginPage(request):
    if 'username' in request.session:
        return redirect('userside:home')
    
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,email=username,password = password)

        if user is not None:
            request.session['username'] = username
            login(request,user)
            return redirect('userside:home')
        else:
            return HttpResponse("Username or Password is Incorrect!!!")
  
    return render(request,'login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache    
def LogOutPage(request):
    if 'username' in request.session:
        logout(request)
        return redirect('userside:home')



# find each product discont 
def get_discount_for_product(product):
    product_discount = 0
    if DiscountCoupon.objects.filter(product_id=product.id, valid_till__gte=timezone.now()).exists():
        product_discount = DiscountCoupon.objects.get(product_id=product.id).discount_amount

    category_discount = 0
    if DiscountCoupon.objects.filter(category_id=product.category_id, valid_till__gte=timezone.now()).exists():
        category_discount = DiscountCoupon.objects.get(category_id=product.category_id).discount_amount

    return max(product_discount, category_discount)

#home page----------------------------------------------------------------------
@login_required(login_url='userside:login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def homepage(request):
    products = Product.objects.all()
    discounted_products = []
    for product in products:
        discount = get_discount_for_product(product)
        discounted_price = product.price - discount
        discounted_products.append({
            'product': product,
            'original_price': product.price,
            'discounted_price': discounted_price
        })
    context = {'products': discounted_products}
    return render(request, 'home.html', context)

# product related --------------------------------------------------------------
def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)
    stock = Stock.objects.get(product=product_id)
    comments = ProductComment.objects.filter(product=product)
    context = {'product': product, 'stock': stock, 'comments': comments}

    if request.method == 'POST':
        user = request.user
        comment_text = request.POST.get('comment')
        ProductComment.objects.create(product=product, user=user, comment=comment_text)

    return render(request, 'products_detail.html', context)

# user profile -----------------------------------------------------------------
@login_required
def user_profile(request):
    customer = CustomUser.objects.get(email=request.user.email)
    return render(request, 'user_profile.html', {'customer': customer})

def add_profile_data(request):
    if request.method == 'POST':
        user = CustomUser.objects.get(email=request.user.email)
        username = request.POST.get('username')
        email = request.POST.get('email')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        payment_method = request.POST.get('payment_method')
        upi_id = request.POST.get('upi_id')
        
        user.username = username
        user.email = email
        user.address1 = address1
        user.address2 = address2
        user.save()
        
        payment_method_obj, created = CustomerPaymentMethod.objects.get_or_create(
            customer=user,
            defaults={'payment_method': payment_method, 'upi_id': upi_id}
        )
        
        if not created:
            payment_method_obj.payment_method = payment_method
            payment_method_obj.upi_id = upi_id
            payment_method_obj.save()
        
        customer = CustomUser.objects.get(email=request.user.email)
        return render(request, 'user_profile.html', {'customer': customer})
    return render(request, 'profile_data_edit.html')

# cart related- --------------------------------------------------------------------
def view_cart(request):
    cart = Cart.objects.get(customer=request.user)
    cart_items = cart.cartitem_set.all()
    # Calculate the total price for each cart item and add it to the cart item object
    for cart_item in cart_items:
        cart_item.total_price = cart_item.product.price * cart_item.quantity

    context = {
        'cart_items': cart_items,  
    }
    return render(request, 'cart.html', context)

def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(pk=product_id)
        user_cart, created = Cart.objects.get_or_create(customer=request.user)
        cart_items = CartItem.objects.filter(cart=user_cart, product=product)
        if cart_items.exists():
            # If CartItem already exists, update the quantity or any other necessary actions
            # For example, you can increase the quantity of the existing CartItem
            cart_item = cart_items.first()
            cart_item.quantity += 1
            cart_item.save()
        else:
            # If the CartItem does not exist, create a new one
            user_cart.add_to_cart(product)
        response_data = {'message': 'Product added to cart successfully'}
        return JsonResponse(response_data)
    else:
        response_data = {'message': 'User is not authenticated'}
        return JsonResponse(response_data)


def remove_from_cart(request, product_id):
    cart = Cart.objects.get(customer=request.user)
    product = Product.objects.get(pk=product_id)
    cart.remove_from_cart(product)
    return redirect('userside:cart')
# stock conting ajax ==================================================================
def increase_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart_item = CartItem.objects.get(product_id=product_id)
        cart_item.quantity += 1
        cart_item.save()
        new_quantity = cart_item.quantity
        return JsonResponse({'quantity': new_quantity})

def decrease_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart_item = CartItem.objects.get(product_id = product_id)
        cart_item.quantity -= 1
        cart_item.save()
        new_quantity =  cart_item.quantity
        return JsonResponse({'quantity': new_quantity})
# order def start ===================================================================
def checkout(request):
    if request.method == 'POST':
        cart = Cart.objects.get(customer=request.user)
        cart.checkout()
        cart.cartitem_set.all().delete()
        return redirect('userside:order_confirmation')
    return redirect('userside:order_showing')



def order_confirmation(request):
    order = Order.objects.filter(customer=request.user).latest('order_date')
    order_items = OrderItem.objects.filter(order=order)

    # Calculate the total price for each item
    for item in order_items:
        item.total_price = ExpressionWrapper(F('product__price') * F('quantity'), output_field=DecimalField())

    context = {'order': order, 'order_items': order_items}
    return render(request, 'order_status.html', context)



def order_showing(request):
    cart = Cart.objects.get(customer=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    # Calculate the total price using aggregate function
    total_price = cart_items.aggregate(total_price=Sum(F('product__price') * F('quantity')))['total_price'] or 0

    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'order_confirmation.html', context)

# order related ==========================================================================

def all_orders(request) :
    oeders = Order.objects.filter(customer = request.user)
    context = { 'orders' : oeders}
    return render(request , 'all_orders.html',context)

def order_tracking(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        raise Http404("Order does not exist")

    context = {'order': order} 

    return render(request, 'order_tracking.html', context)


def cancel_order(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        if order.customer == request.user:
            if order.order_status == 'confirmed':
                order.order_status = 'cancelled'
                order.save()
                messages.success(request, 'Order has been successfully cancelled.')
            else:
                messages.error(request, 'This order cannot be cancelled.')
        else:
            messages.error(request, 'You do not have permission to cancel this order.')

    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
    return redirect('userside:all_orders')
#------------------------------------------------------------------------------------------ 
# search products
@csrf_exempt
def search_products(request):
    if request.method == 'GET' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        query = request.GET.get('query', None)
        if query:
            products = Product.objects.filter(modelname__icontains=query)
            serialized_products = list(products.values('id', 'modelname', 'color', 'brand'))
            return JsonResponse({'products': serialized_products})
    return JsonResponse({'error': 'Invalid request'}, status=400)



def payment_methods(request):
    return render(request, 'payment_method.html')



