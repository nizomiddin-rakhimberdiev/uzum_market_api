from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Product
import requests

class UpdateProductsView(APIView):
    def post(self, request):
        # Simulate fetching updated products from an external API
        external_api_url = "https://mockapi.com/products"  # Replace with the real API URL
        try:
            response = requests.get(external_api_url)
            products_data = response.json()

            for product_data in products_data:
                Product.objects.update_or_create(
                    id=product_data.get('id'),
                    defaults={
                        'name': product_data.get('name'),
                        'description': product_data.get('description'),
                        'price': product_data.get('price'),
                        'quantity': product_data.get('quantity'),
                    }
                )

            return Response({"message": "Products updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
