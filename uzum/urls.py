from django.urls import path
from .views import CategoryListCreateView, ProductListCreateView, CartAPIView, CreateOrderAPIView, \
    OrdersListForSellerView

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('orders/create/', CreateOrderAPIView.as_view(), name='create-order'),
    path('orders/seller/', OrdersListForSellerView.as_view(), name='orders-for-seller'),
]
