from django.db import models

from config import settings
from users.models import Store, DeliveryHub
from django.contrib.auth import get_user_model


User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    stock = models.PositiveIntegerField()
    description_uz = models.TextField()
    description_ru = models.TextField()
    short_description_uz = models.TextField(blank=True, null=True)
    short_description_ru = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_uz

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    video = models.FileField(upload_to='products/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name_uz} ({self.quantity})"

    @property
    def total_price(self):
        return self.quantity * self.product.price  # Agar `price` Product modelida bo‘lsa


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    )
    DELIVERY_METHOD_CHOICES = [
        ('home', 'Home Delivery'),
        ('pickup', 'Pickup Point'),
    ]
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card Payment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_price = models.FloatField(null=True, blank=True)
    delivery_method = models.CharField(max_length=50, choices=DELIVERY_METHOD_CHOICES)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES)
    delivery_address = models.TextField(null=True, blank=True)
    delivery_hub = models.ForeignKey(DeliveryHub, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.total_price:
            order_items = OrderItem.objects.filter(order=self)
            self.total_price = sum(item.product.price * item.quantity for item in order_items)
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name_uz} ({self.quantity})"

    @property
    def total_price(self):
        return self.quantity * self.price