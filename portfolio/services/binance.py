import requests

class BinanceService:
    BASE_URL = "https://api.binance.com/api/v3"
    
    @staticmethod
    def get_price(symbol: str) -> float:
        response = requests.get(
            f"{BinanceService.BASE_URL}/ticker/price",
            params={"symbol": f"{symbol}USDT"}
        )
        response.raise_for_status()
        return float(response.json()["price"])