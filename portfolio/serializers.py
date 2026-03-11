from rest_framework import serializers
from portfolio.models import Asset, PortfolioAlerts, Transaction


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


class PortfolioAlertsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioAlerts
        fields = ['id', 'user', 'symbol', 'target_price', 'alert_type', 'is_active', 'created_at', 'is_triggered']
        read_only_fields = ['user', 'created_at', 'is_triggered']


class PortfolioAlertsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioAlerts
        fields = ['is_active']
