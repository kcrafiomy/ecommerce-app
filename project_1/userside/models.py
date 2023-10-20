from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import transaction
#---------------------------------------------------------------------------------------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255)
    address1 = models.TextField(blank=True)
    address2 = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='customer_images/', default='default_image.jpg')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
#==============================================================================================================

class Category(models.Model):
    name = models.CharField(max_length=255)

class Product(models.Model):
    modelname = models.CharField(max_length=255)
    color = models.CharField(max_length=100)
    brand = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    storage = models.CharField(max_length=100,blank=True)
    image1 = models.ImageField(upload_to='product_images/', default='default_image.jpg')
    image2 = models.ImageField(upload_to='product_images/', default='default_image.jpg')
    image3 = models.ImageField(upload_to='product_images/', default='default_image.jpg')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_count = models.IntegerField()

#---------------------------------------------------------------------------------------------------------------
class CustomerPaymentMethod(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Net Bank', 'Net Bank'),
        ('UPI', 'UPI'),
        ('Cash on Delivery', 'Cash on Delivery'),
        ('EMI', 'EMI'),
    ]
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    upi_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.customer.username} - {self.payment_method}"

class Supplier(models.Model):
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    mail = models.EmailField()  
    name = models.CharField(max_length=100) 
    def __str__(self):
        return self.namef
#==============================================================================================================
class Cart(models.Model):
    customer = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='CartItem')

    def add_to_cart(self, product, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(cart=self, product=product)
        cart_item.quantity += quantity
        cart_item.save()

    def remove_from_cart(self, product):
        cart_item = CartItem.objects.filter(cart=self, product=product).first()
        if cart_item:
            cart_item.delete()
    
    @transaction.atomic
    def checkout(self):
    # Start a database transaction to ensure consistency
        with transaction.atomic():
        # Create an Order object
            order = Order.objects.create(
                customer=self.customer,
                total_price=self.calculate_total_price(),
                shipping_address=self.customer.address1,
            )

            for cart_item in self.cartitem_set.all():
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )

            self.cartitem_set.update(is_completed=True)

            order.order_status = 'confirmed'
            order.save()

    def calculate_total_price(self):
        # Calculate the total price of items in the cart
        total_price = 0
        for cart_item in self.cartitem_set.all():
            total_price += cart_item.product.price * cart_item.quantity
        return total_price

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

User = get_user_model()

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    shipping_address = models.TextField()
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='confirmed') 
    is_completed = models.BooleanField(default=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.customer.username} ({self.get_order_status_display()})"

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_item_total(self):
        return self.price * self.quantity

class ProductComment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class DiscountCoupon(models.Model):
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_till = models.DateField()
    category_id = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)

