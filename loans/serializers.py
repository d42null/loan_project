from rest_framework import serializers
from .models import Loan, Payment, PaymentAdjustment

class LoanSerializer(serializers.ModelSerializer):
    loan_start_date = serializers.DateField(input_formats=['%Y-%m-%d', '%d-%m-%Y'])
    
    class Meta:
        model = Loan
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields=['id','date','principal','interest']
        
        

class PaymentAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAdjustment
        fields = '__all__'
