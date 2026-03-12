from decimal import Decimal

from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from portfolio.services.binance import BinanceService
from portfolio.services.coinmarketcap import CoinMarketCapService

from .services.portfolio import PortfolioService
from rest_framework.exceptions import ValidationError
from portfolio.models import Asset, PortfolioAlerts, Transaction
from portfolio.serializers import AssetSerializer, PortfolioAlertsSerializer, PortfolioAlertsUpdateSerializer, TransactionSerializer
    
# Create your views here.
class AssetViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Asset.objects.filter(user=self.request.user)


class TransactionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        try:
            PortfolioService.process_transaction(transaction)
        except ValueError as e:
            transaction.delete()
            raise ValidationError(str(e))

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assets = Asset.objects.filter(user=request.user)
        
        total_invested = Decimal('0')
        total_value = Decimal('0')
        assets_data = []

        for asset in assets:
            try:
                current_price = Decimal(str(BinanceService.get_price(asset.symbol)))
            except ValueError as e:
                return Response(
                    {"error": f"Failed to fetch price for {asset.symbol}: {str(e)}"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            invested = asset.amount * asset.avg_price
            current_value = asset.amount * current_price
            pnl = current_value - invested
            pnl_percent = (pnl / invested * 100) if invested > 0 else Decimal('0')

            total_invested += invested
            total_value += current_value

            assets_data.append({
                "symbol": asset.symbol,
                "amount": asset.amount,
                "avg_price": asset.avg_price,
                "current_price": current_price,
                "current_value": current_value,
                "pnl": pnl,
                "pnl_percent": pnl_percent,
            })

        total_pnl = total_value - total_invested
        total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else Decimal('0')

        return Response({
            "assets": assets_data,
            "total_invested": total_invested,
            "total_value": total_value,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
        })
    

class TopMarketCapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = min(int(request.query_params.get('limit', 10)), 100)
        page = int(request.query_params.get('page', 1))
        
        try:
            coins = CoinMarketCapService.get_top_coins(limit=limit, page=page)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({
            "page": page,
            "limit": limit,
            "results": coins
        })
    

class PortfolioAlertsViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioAlertsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PortfolioAlerts.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return PortfolioAlertsUpdateSerializer
        return PortfolioAlertsSerializer
