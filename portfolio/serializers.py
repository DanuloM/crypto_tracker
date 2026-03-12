from decimal import Decimal
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
    
    def validate_amount(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Amount must be greater than zero")
        return value
    
    def validate_price(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Price must be greater than zero")
        return value
    
    def validate_symbol(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Symbol cannot be empty")
        return value.upper()


class PortfolioAlertsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioAlerts
        fields = ['id', 'user', 'symbol', 'target_price', 'alert_type', 'is_active', 'created_at', 'is_triggered']
        read_only_fields = ['user', 'created_at', 'is_triggered']
    
    def validate_target_price(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Target price must be greater than zero")
        return value
    
    def validate_symbol(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Symbol cannot be empty")
        return value.upper()


class PortfolioAlertsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioAlerts
        fields = ['is_active']
