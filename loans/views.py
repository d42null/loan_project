from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoanSerializer, PaymentSerializer, PaymentAdjustmentSerializer
from .models import Payment, PaymentAdjustment
from datetime import timedelta
from decimal import Decimal
from math import pow
class CreateLoan(APIView):
    def post(self, request, format=None):
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.save()
            amount = loan.amount
            loan_start_date = loan.loan_start_date
            number_of_payments = loan.number_of_payments
            periodicity = loan.periodicity
            interest_rate = loan.interest_rate

            cache_key = f"{amount}_{loan_start_date}_{number_of_payments}_{periodicity}_{interest_rate}"
            cached_schedule = cache.get(cache_key)

            if cached_schedule:
                return Response(cached_schedule, status=status.HTTP_200_OK)

            period_length_map = {
                'd': 1/365,
                'w': 1/52,
                'm': 1/12
            }

            period_unit = periodicity[-1]
            period_count = int(periodicity[:-1])
            period_length = period_length_map[period_unit] * period_count
            i = interest_rate * Decimal(period_length)
            n = number_of_payments
            P = amount

            # EMI calculation
            EMI = i * P / (1 - Decimal(pow(1 + i, -n)))

            payments = []
            remaining_principal = P

            for payment_number in range(1, n + 1):
                interest = remaining_principal * i
                principal = EMI - interest

                if period_unit == 'd':
                    payment_date = loan_start_date + timedelta(days=period_count * payment_number)
                elif period_unit == 'w':
                    payment_date = loan_start_date + timedelta(weeks=period_count * payment_number)
                elif period_unit == 'm':
                    payment_date = loan_start_date + timedelta(days=30 * period_count * payment_number)

                payment = {                    
                    'loan': loan,
                    'date': payment_date,
                    'principal': round(principal, 2),
                    'interest': round(interest, 2)
                }
                payments.append(payment)

                remaining_principal -= principal

            payment_objects = [Payment(**payment) for payment in payments]
            Payment.objects.bulk_create(payment_objects)

            payment_serializer = PaymentSerializer(payment_objects, many=True)
            cache.set(cache_key, payment_serializer.data, timeout=60*15)  # Cache for 15 minutes

            return Response(payment_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdatePayment(APIView):
    def post(self, request, payment_id, format=None):
        reduction_amount = request.data.get('reduction_amount')

        # Get the payment to be adjusted
        payment = get_object_or_404(Payment, id=payment_id)

        # Save the adjustment
        adjustment = PaymentAdjustment(payment=payment, reduction_amount=reduction_amount)
        adjustment.save()

        # Update the principal of the payment
        payment.principal -= Decimal(reduction_amount)
        payment.save()

        # Recalculate interests and principals for the subsequent payments
        subsequent_payments = Payment.objects.filter(loan=payment.loan, date__gt=payment.date).order_by('date')

        remaining_principal = payment.principal
        interest_rate = payment.loan.interest_rate
        periodicity = payment.loan.periodicity
        period_unit = periodicity[-1]
        period_count = int(periodicity[:-1])
        period_length_map = {
            'd': 1/365,
            'w': 1/52,
            'm': 1/12
        }
        period_length = period_length_map[period_unit] * period_count
        i = interest_rate * Decimal(period_length)

        for subsequent_payment in subsequent_payments:
            interest = remaining_principal * i
            principal = subsequent_payment.principal
            subsequent_payment.interest = round(interest, 2)
            subsequent_payment.principal = round(principal, 2)
            subsequent_payment.save()

            remaining_principal -= principal

        return Response({"detail": "Payment updated successfully"}, status=status.HTTP_200_OK)