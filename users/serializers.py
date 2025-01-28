import requests
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.cache import cache
import re
import random

from users.models import CustomerAccount, SellerProfile

User = get_user_model()



class CustomerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAccount
        fields = ('phone_number', 'first_name', 'last_name','second_name', 'birthdate', 'email', 'gender')


class UpdateCustomerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAccount
        fields = ['first_name', 'last_name', 'second_name', 'birthdate', 'email', 'gender']

    def validate_phone_number(self, value):
        # This method is not necessary anymore since phone_number is not being updated directly
        return value


class SendCodeSerializer(serializers.Serializer):
    class Meta:
        schema = 'SendCodeSerializer'
        fields = ['phone_number']

    phone_number = serializers.CharField(max_length=15, required=True)

    def validate_phone_number(self, value):
        """
        Telefon raqamni validatsiya qiladi:
        +998XXXXXXXXX yoki XXXXXXXXX (faqat 9 xonali raqam) formatlarini qabul qiladi.
        """
        pattern = r"^\+998\d{9}$|^\d{9}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Telefon raqam noto‘g‘ri formatda. +998XXXXXXXXX yoki XXXXXXXXX (faqat 9 ta raqam) formatida bo‘lishi kerak."
            )
        # Raqamni `+998` formatiga o‘tkazish
        if len(value) == 9:  # Faqat 9 xonali raqam
            value = f"+998{value}"
            return value
        elif value.startswith("+998") and len(value) == 13:
            return value
        else:
            raise serializers.ValidationError("Telefon raqam noto‘g‘ri formatda. +998XXXXXXXXX yoki XXXXXXXXX (faqat 9 ta raqam) formatida bo‘lishi kerak.")


    def create_verification_code(self, phone_number):
        import random
        from django.core.cache import cache

        try:
            # Tasdiqlash kodini yaratish
            code = random.randint(10000, 99999)
            cache.set(f'verify_code_{phone_number}', code, timeout=10000)

            # SMS yuborish
            # send_verification_code(phone_number, code)
            print(f"Code {code} successfully sent to {phone_number}")
            return code
        except Exception as e:
            print("Error sending verification code:", str(e))
            raise serializers.ValidationError("SMS yuborishda xatolik yuz berdi.")





class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    verification_code = serializers.CharField(max_length=6)

    def validate(self, data):
        """
        Telefon raqam va tasdiqlash kodini tekshiradi.
        """
        phone_number = data['phone_number']
        code = data['verification_code']

        # Telefon raqamni to‘g‘ri formatga o‘tkazish
        if len(phone_number) == 9:
            phone_number = f"+998{phone_number}"

        # Keshdagi kodni olish
        cached_code = cache.get(f'verify_code_{phone_number}')
        if not cached_code or str(cached_code) != str(code):
            raise serializers.ValidationError("Tasdiqlash kodi noto‘g‘ri yoki muddati tugagan.")

        # Keshdan kodni o‘chirish
        cache.delete(f'verify_code_{phone_number}')
        return {'phone_number': phone_number}

    def create_or_login_user(self, validated_data):
        """
        Agar foydalanuvchi mavjud bo‘lmasa, uni yaratadi.
        Foydalanuvchi mavjud bo‘lsa, login qiladi va token qaytaradi.
        """
        phone_number = validated_data['phone_number']
        user, created = User.objects.get_or_create(phone_number=phone_number)

        if created:
            CustomerAccount.objects.create(user=user, first_name='', last_name='')
            SellerProfile.objects.create(user=user, first_name='', last_name='')

        # JWT tokenlar yaratish
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'is_new_user': created
        }

