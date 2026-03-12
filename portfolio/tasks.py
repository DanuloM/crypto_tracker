from celery import shared_task
from .services.alert import AlertService
from portfolio.models import PortfolioAlerts

@shared_task
def check_price_alerts():
    alerts = PortfolioAlerts.objects.filter(is_active=True, is_triggered=False)
    for alert in alerts:
        current_price = AlertService.get_current_price(alert.symbol)
        if AlertService.check_alert(alert, current_price):
            AlertService.notify_user(alert, current_price)
            alert.is_triggered = True
            alert.is_active = False
            alert.save()