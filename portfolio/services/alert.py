from .binance import BinanceService
from django.core.mail import send_mail
from django.conf import settings

class AlertService:
    
    @staticmethod
    def get_current_price(symbol):
        return BinanceService.get_price(symbol)
    
    @staticmethod
    def check_alert(alert, current_price):
        if alert.alert_type == 'ABOVE':
            return current_price > alert.target_price
        elif alert.alert_type == 'BELOW':
            return current_price < alert.target_price
        return False
    
    @staticmethod
    def notify_user(alert, current_price):
        subject = f"Price Alert for {alert.symbol}"
        message = f"The price of {alert.symbol} is now {current_price}, which is {'above' if alert.alert_type == 'ABOVE' else 'below'} your target of {alert.target_price}."
        recipient_list = [alert.user.email]
        
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
