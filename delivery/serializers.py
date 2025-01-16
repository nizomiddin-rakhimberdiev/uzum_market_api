from rest_framework import serializers
from .models import DeliveryPerson

class DeliveryPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPerson
        fields = ['id', 'name', 'phone', 'email', 'status']
