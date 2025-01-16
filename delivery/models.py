from django.db import models

class DeliveryPerson(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=50, default='active')

    def __str__(self):
        return self.name
