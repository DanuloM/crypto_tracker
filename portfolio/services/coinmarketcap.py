import requests
import os

class CoinMarketCapService:
    BASE_URL = "https://pro-api.coinmarketcap.com/v1"
    API_KEY = os.getenv("COINMARKETCAP_API_KEY")
    
    @staticmethod
    def get_top_coins(limit=10, page=1):
        start = (page - 1) * limit + 1
        response = requests.get(
            f"{CoinMarketCapService.BASE_URL}/cryptocurrency/listings/latest",
            headers={"X-CMC_PRO_API_KEY": CoinMarketCapService.API_KEY},
            params={
                "limit": limit,
                "start": start,
                "convert": "USD",
                "sort": "market_cap",
            }
        )
        return response.json()["data"]