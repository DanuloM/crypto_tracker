from decimal import Decimal

from django.db import models


class Asset(models.Model):
    symbol = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=8, default=Decimal('0'))
    avg_price = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0'))
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='assets')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol
    

class Transaction(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='transactions')
    symbol = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=8)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} {self.symbol} at {self.price}"
