from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Loan, Payment
from decimal import Decimal

class LoanScheduleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.loan_data = {
            "amount": 1000,
            "loan_start_date": "2024-01-10",
            "number_of_payments": 4,
            "periodicity": "1m",
            "interest_rate": 0.1
        }

    def test_create_loan_schedule(self):
        response = self.client.post('/loans/create-loan/', self.loan_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 4)  # Перевірка кількості платежів
        self.assertTrue(all('principal' in payment and 'interest' in payment for payment in response.data))

class PaymentAdjustmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.loan = Loan.objects.create(amount=1000, loan_start_date="2024-01-10", number_of_payments=4, periodicity="1m", interest_rate=0.1)
        self.payment1 = Payment.objects.create(loan=self.loan, date="2024-02-10", principal=Decimal('200.00'), interest=Decimal('10.00'))
        self.payment2 = Payment.objects.create(loan=self.loan, date="2024-03-10", principal=Decimal('200.00'), interest=Decimal('8.00'))

    def test_reduce_payment_principal(self):
        response = self.client.post(f'/loans/update-payment/{self.payment1.id}/', {'reduction_amount': '50.00'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.payment1.refresh_from_db()
        self.assertEqual(self.payment1.principal, Decimal('150.00'))  # Перевірка нової суми тіла платежу

        # Перевірка оновлених сум наступних платежів
        self.payment2.refresh_from_db()
        self.assertNotEqual(self.payment2.interest, Decimal('8.00'))  # Перевірка, що сума відсотків змінилася
