from itertools import product
from statistics import quantiles

from rest_framework import generics

from .permissions import IsSeller
from .serializers import CategorySerializer, ProductSerializer, CartItemSerializer, OrderSerializer
from .models import Category, Product, CartItem, OrderItem, Order
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import status

# Create your views here.
def teacher_view(request):
    pass

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Foydalanuvchining savatini ko‘rish"""
        cart_items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Mahsulotni savatga qo‘shish yoki yangilash"""
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = CartItemSerializer(data=data)

        if serializer.is_valid():
            # Agar savatda mahsulot bo‘lsa, miqdorini oshirish
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product_id=serializer.validated_data['product'].id,
                defaults={'quantity': serializer.validated_data['quantity']}
            )
            if not created:
                cart_item.quantity += serializer.validated_data['quantity']
                cart_item.save()

            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Savatdagi mahsulotni o‘chirish"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
            cart_item.delete()
            return Response({"message": "Mahsulot savatdan o‘chirildi."}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Bunday mahsulot savatda topilmadi."}, status=status.HTTP_404_NOT_FOUND)


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Total price calculation
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # Add user and total price to the request data
        data = request.data.copy()
        data['user'] = user.id
        data['total_price'] = total_price

        # Validate and save the order
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save()  # Save the order

            # Create OrderItem for each cart item
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price * cart_item.quantity  # Set the price
                )

            cart_items.delete()  # Clear the cart
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdersListForSellerView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsSeller]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role != 'seller':
            raise PermissionDenied("You do not have permission to view these orders.")
        # Faqat sellerga tegishli buyurtmalarni filterlash
        return Order.objects.filter(
            items__product__store__seller__user=user
        ).distinct()
