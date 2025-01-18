
from rest_framework import generics
from .serializers import CategorySerializer, ProductSerializer, CartItemSerializer
from .models import Category, Product, CartItem
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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