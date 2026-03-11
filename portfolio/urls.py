from rest_framework.routers import DefaultRouter, path
from portfolio.views import AssetViewSet, PortfolioAlertsViewSet, TopMarketCapView, TransactionViewSet, SummaryView


router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'alerts', PortfolioAlertsViewSet, basename='alerts')

urlpatterns = router.urls + [
    path('summary/', SummaryView.as_view()),
    path('top_coins/', TopMarketCapView.as_view()),
]