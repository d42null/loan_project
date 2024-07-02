from django.db import models
class Loan(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_start_date = models.DateField()
    number_of_payments = models.IntegerField()
    periodicity = models.CharField(max_length=10)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)

class Payment(models.Model):
    loan = models.ForeignKey(Loan, related_name='payments', on_delete=models.CASCADE)
    date = models.DateField()
    principal = models.DecimalField(max_digits=10, decimal_places=2)
    interest = models.DecimalField(max_digits=10, decimal_places=2)

class PaymentAdjustment(models.Model):
    payment = models.ForeignKey(Payment, related_name='adjustments', on_delete=models.CASCADE)
    reduction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    adjustment_date = models.DateField(auto_now_add=True)