from rest_framework import serializers

from users.models import DeliveryHub
from .models import Category, Product, ProductImage, CartItem, OrderItem, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'slug', 'description')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name_uz', 'price', 'description_uz','short_description_uz', 'created_at', 'images')


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.FloatField(source='product.price', read_only=True)
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'product_name', 'product_price', 'quantity', 'total_price']
        read_only_fields = ['user']  # Foydalanuvchi avtomatik o‘rnatiladi

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Miqdor kamida 1 bo‘lishi kerak.")
        return value


# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ['id', 'product', 'product_name', 'quantity', 'price', 'total_price']


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity']

class DeliveryHubSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryHub
        fields = ['id', 'hub_name', 'hub_address', 'latitude', 'longitude']


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    delivery_method = serializers.ChoiceField(choices=Order.DELIVERY_METHOD_CHOICES)
    payment_type = serializers.ChoiceField(choices=Order.PAYMENT_TYPE_CHOICES)
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    delivery_hub = serializers.PrimaryKeyRelatedField(queryset=DeliveryHub.objects.all(), required=False)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'created_at', 'updated_at', 'status', 'total_price',
            'delivery_method', 'payment_type', 'delivery_address', 'delivery_hub', 'items'
        ]

    def validate(self, attrs):
        delivery_method = attrs.get('delivery_method')
        delivery_address = attrs.get('delivery_address')
        delivery_hub = attrs.get('delivery_hub')

        if delivery_method == 'home' and not delivery_address:
            raise serializers.ValidationError({"delivery_address": "Delivery address is required for home delivery."})
        if delivery_method == 'pickup' and not delivery_hub:
            raise serializers.ValidationError({"delivery_hub": "A delivery hub must be selected for pickup."})
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # `items`ni ajratib olish
        order = Order.objects.create(**validated_data)  # Buyurtmani yaratish

        # `items`ni qayta ishlash va `OrderItem`larni yaratish
        for item in items_data:
            product_id = item.get('product')
            quantity = item.get('quantity')

            # `Product` obyektini olish
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product": f"Product with id {product_id} does not exist."})

            # `price` qiymatini hisoblash va `OrderItem`ni yaratish
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price * quantity  # Mahsulot narxini qo'shish
            )

        # Buyurtmaning umumiy narxini hisoblash
        total_price = sum(item['quantity'] * Product.objects.get(id=item['product']).price for item in items_data)
        order.total_price = total_price
        order.save()

        return order



