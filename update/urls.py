from django.urls import path
from .views import UpdateProductsView

urlpatterns = [
    path('update/', UpdateProductsView.as_view(), name='update-products'),
]
