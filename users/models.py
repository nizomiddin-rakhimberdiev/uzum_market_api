
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Foydalanuvchi uchun telefon raqam talab qilinadi")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser is_staff=True bo‘lishi kerak.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser is_superuser=True bo‘lishi kerak.")

        return self.create_user(phone_number, password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('seller', 'Seller'),
        ('delivery_person', 'Delivery Person'),
        ('delivery_hub', 'Delivery Hub'),
        ('customer', 'Customer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'  # `username` o‘rniga
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number



class CustomerAccount(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    second_name = models.CharField(max_length=50, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(('erkak', 'Erkak'), ('ayol', 'Ayol')), null=True, blank=True)

    def __str__(self):
        return self.user.phone_number


class SellerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='seller_profile')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100,  blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.phone_number

class Store(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='seller-logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='seller-banners/', blank=True, null=True)
    store_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.store_name

class DeliveryPersonProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='delivery_person_profile')
    vehicle_number = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username


class DeliveryHub(models.Model):
    hub_name = models.CharField(max_length=255)
    hub_address = models.TextField()
    latitude = models.CharField(max_length=30)
    longitude = models.CharField(max_length=30)
    manager = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, related_name='hub_manager')

    def __str__(self):
        return self.hub_name