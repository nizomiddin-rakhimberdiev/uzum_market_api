from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import CustomerAccount
from .serializers import SendCodeSerializer, VerifyCodeSerializer, UpdateCustomerAccountSerializer, \
    CustomerAccountSerializer
from .permissions import IsCustomer


class SendCodeView(APIView):
    def post(self, request):
        serializer = SendCodeSerializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)  # Log xatolarni
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        print("Validated Phone Number:", phone_number)  # Tasdiqlangan raqamni ko'rish
        serializer.create_verification_code(phone_number)

        return Response({"detail": "Tasdiqlash kodi yuborildi."}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    """
    Telefon raqam orqali ro‘yxatdan o‘tish yoki tizimga kirish.
    """
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.create_or_login_user(serializer.validated_data)
        return Response(tokens, status=status.HTTP_200_OK)


class UpdateCustomerAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    def get_object(self, user):
        # Get the CustomerAccount associated with the user
        try:
            return CustomerAccount.objects.get(user=user)
        except CustomerAccount.DoesNotExist:
            raise Response({"detail": "Customer account does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        # Retrieve the user's CustomerAccount
        customer_account = self.get_object(request.user)

        # Deserialize and validate the data
        serializer = UpdateCustomerAccountSerializer(customer_account, data=request.data)
        if serializer.is_valid():
            # Update the CustomerAccount with the validated data
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CustomerAccountView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        account = CustomerAccount.objects.filter(user=request.user).first()
        if not account:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerAccountSerializer(account)
        return Response(serializer.data)

    def put(self, request):
        account = CustomerAccount.objects.filter(user=request.user).first()
        if not account:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerAccountSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)