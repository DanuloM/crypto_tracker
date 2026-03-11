from rest_framework import serializers
from portfolio.models import Asset, Transaction


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ['user', 'date_created']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id','user', 'symbol', 'amount', 'price', 'transaction_type', 'created_at']
        read_only_fields = ['user', 'created_at']