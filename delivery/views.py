from rest_framework import viewsets
from .models import DeliveryPerson
from .serializers import DeliveryPersonSerializer

class DeliveryPersonViewSet(viewsets.ModelViewSet):
    queryset = DeliveryPerson.objects.all()
    serializer_class = DeliveryPersonSerializer
