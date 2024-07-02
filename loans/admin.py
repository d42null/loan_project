from django.contrib import admin
from .models import Payment,Loan,PaymentAdjustment
# Register your models here.
admin.site.register(Loan)
admin.site.register(Payment)
admin.site.register(PaymentAdjustment)