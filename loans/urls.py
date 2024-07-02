from django.urls import path
from .views import CreateLoan, UpdatePayment

urlpatterns = [
    path('create-loan/', CreateLoan.as_view(), name='create-loan'),
    path('update-payment/<int:payment_id>/', UpdatePayment.as_view(), name='update-payment'),
]
