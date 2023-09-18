from .models import CustomUser,CustomerPaymentMethod,Product,Stock
from .models import Cart, CartItem, Product
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control, never_cache
from django.contrib import messages
from django.core.files.uploadedfile import InMemoryUploadedFile

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

#home page----------------------------------------------------------------------
@login_required(login_url='userside:login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def homepage(request):
    product = Product.objects.all() 
    context = {'product': product}
    return render(request, 'home.html', context)


# product related --------------------------------------------------------------
def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)
    stock = Stock.objects.get(product = product_id)
    context = {'product': product,'stock': stock}
    return render(request, 'products_detail.html', context)

# user profile -----------------------------------------------------------------
@login_required
def user_profile(request):
    customer = CustomUser.objects.get(email=request.user.email)
    return render(request, 'user_profile.html', {'customer': customer})

@login_required  
def add_profile_data(request):
    if request.method == 'POST':
        # Retrieve the current user
        user = request.user
        # Retrieve form data from POST request
        username = request.POST.get('username')
        email = request.POST.get('email')
        image = request.FILES.get('image', None)
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        password = request.POST.get('password')
        payment_method = request.POST.get('payment_method')
        upi_id = request.POST.get('upi_id')
        
        # Update the user's fields
        user.username = username
        user.email = email
        user.profile_image = image if image else CustomUser.profile_image
        user.address1 = address1
        user.address2 = address2
        if image:
            # Ensure it's an InMemoryUploadedFile to prevent the _committed error
            if not isinstance(image, InMemoryUploadedFile):
                image = InMemoryUploadedFile(image, None, image.name, image.content_type, image.tell, None)
            user.profile_image = image
        # Save the updated user data
        user.save()
        
        # Check if a payment method object exists, and if not, create it
        payment_method_obj, created = CustomerPaymentMethod.objects.get_or_create(
            customer=user,
            defaults={'payment_method': payment_method, 'upi_id': upi_id}
        )
        
        # If it's not created, update its fields
        if not created:
            payment_method_obj.payment_method = payment_method
            payment_method_obj.upi_id = upi_id
            payment_method_obj.save()
        
        return redirect('userside:home')  
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
    product = Product.objects.get(pk=product_id)
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(customer=request.user)
        user_cart.add_to_cart(product)
        return redirect('userside:cart')
    else:
        return redirect('userside:login')

def remove_from_cart(request, product_id):
    cart = Cart.objects.get(customer=request.user)
    product = Product.objects.get(pk=product_id)
    cart.remove_from_cart(product)
    return redirect('userside:cart')

#------------------------------------------------------------------------------------------