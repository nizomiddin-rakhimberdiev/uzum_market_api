from django.urls import path
from .views import SendCodeView, VerifyCodeView, UpdateCustomerAccountView, CustomerAccountView

urlpatterns = [
    path('send-code/', SendCodeView.as_view(), name='send-code'),
    path('verify-login/', VerifyCodeView.as_view(), name='verify-login'),
    path('api/users/update-profile/', UpdateCustomerAccountView.as_view(), name='update-profile'),
    path('customer-account/', CustomerAccountView.as_view(), name='customer-account'),

]
