from django.shortcuts import render
from rest_framework import generics
from .serializers import CategorySerializer, ProductSerializer
from .models import Category, Product

# Create your views here.
def teacher_view(request):
    pass

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
