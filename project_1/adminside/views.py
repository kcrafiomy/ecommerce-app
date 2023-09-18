from django.shortcuts import render, redirect,HttpResponse
# Import the  model on userside app
from userside.models import Product ,Category,CustomUser,Supplier,Stock  
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control, never_cache
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#----------------------------------------------------------------------------
def SignUpPage(request):
    if 'username' in request.session:
        return redirect('spadmin')

    elif request.method == 'POST' :
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        
        if not (username and email and pass1 and pass2):
            messages.info(request,"Please fill required field")
            return redirect('signup')
    
        elif pass1 != pass2:
            messages.info(request,"Password mismatch")
            return redirect('signup')
       
        else:
            if CustomUser.objects.filter(username = username).exists():
                messages.info(request,"Username Already Taken")
                return redirect('signup')
           
            elif CustomUser.objects.filter(email = email).exists():
                 messages.info(request,"Email Already Taken")
                 return redirect('signup')
            else:
                my_user = CustomUser.objects.create_user(username=username, email=email, password=pass1)
                my_user.save()
            
        return redirect('login')
    return render(request,'signup.html')
 
@never_cache
def LoginPage(request):
    if 'username' in request.session:
        return redirect('spadmin')
    
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,email=username,password = password)

        if user is not None:
            request.session['username'] = username
            login(request,user)
            return redirect('spadmin')
        else:
            return HttpResponse("Username or Password is Incorrect!!!")
  
    return render(request,'login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache    
def LogOutPage(request):
    if 'username' in request.session:
        logout(request)
        return redirect('spadmin')
    
#-------------------------------------------------------------------

from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
def adminhome(request):
    if request.user.is_staff:
        return render(request, 'adminhome.html')
    else:
        return HttpResponse("You are not authorized to access this page.")


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
            return redirect('spadmin')  # Redirect to a product list page
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

            # Update the existing stock count
            stock.stock_count = stock_count
            stock.save()

            return redirect('spadmin')  # Redirect to a product list page
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
        return redirect('spadmin') # Redirect to admin page after deletion
    context = {'product': product}
    return render(request, 'delete_product.html', context)

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