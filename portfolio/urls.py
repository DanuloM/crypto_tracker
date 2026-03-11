from rest_framework.routers import DefaultRouter, path
from portfolio.views import AssetViewSet, TopMarketCapView, TransactionViewSet, SummaryView


router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = router.urls + [
    path('summary/', SummaryView.as_view()),
    path('top_coins/', TopMarketCapView.as_view()),
]