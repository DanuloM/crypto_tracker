from ..models import Asset
from django.db import transaction as db_transaction

class PortfolioService:
    
    @staticmethod
    def process_transaction(transaction):
        if transaction.transaction_type == 'BUY':
            PortfolioService.process_buy(transaction)
        elif transaction.transaction_type == 'SELL':
            PortfolioService.process_sell(transaction)
    
    @staticmethod
    def process_buy(transaction):
        with db_transaction.atomic():
            asset, created = Asset.objects.get_or_create(
                user=transaction.user,
                symbol=transaction.symbol,
                defaults={'amount': 0, 'avg_price': 0}
            )
            if created:
                asset.amount = transaction.amount
                asset.avg_price = transaction.price
            else:
                old_amount = asset.amount
                old_value = old_amount * asset.avg_price
                new_value = transaction.amount * transaction.price
                asset.amount = old_amount + transaction.amount
                asset.avg_price = (old_value + new_value) / asset.amount
            
            asset.save()

    @staticmethod
    def process_sell(transaction):
        try:
            asset = Asset.objects.get(
                user=transaction.user,
                symbol=transaction.symbol,
            )
        except Asset.DoesNotExist:
            raise ValueError("Cannot sell an asset that does not exist")

        with db_transaction.atomic():
            if transaction.amount > asset.amount:
                raise ValueError("Cannot sell more than the amount owned")

            asset.amount -= transaction.amount

            if asset.amount == 0:
                asset.delete()
            else:
                asset.save()