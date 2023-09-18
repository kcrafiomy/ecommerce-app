from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

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
    profile_image = models.ImageField(upload_to='customer_profile_images/', default='default_image.jpg')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


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

    def checkout(self):
        # Implement your checkout logic here
        pass

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)