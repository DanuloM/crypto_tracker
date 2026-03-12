import requests
import os
import logging

logger = logging.getLogger(__name__)

class CoinMarketCapService:
    BASE_URL = "https://pro-api.coinmarketcap.com/v1"
    API_KEY = os.getenv("COINMARKETCAP_API_KEY")
    
    @staticmethod
    def get_top_coins(limit=10, page=1):
        if not CoinMarketCapService.API_KEY:
            logger.error("CoinMarketCap API key is not configured")
            raise ValueError("CoinMarketCap API key is missing")
        
        start = (page - 1) * limit + 1
        
        try:
            response = requests.get(
                f"{CoinMarketCapService.BASE_URL}/cryptocurrency/listings/latest",
                headers={"X-CMC_PRO_API_KEY": CoinMarketCapService.API_KEY},
                params={
                    "limit": limit,
                    "start": start,
                    "convert": "USD",
                    "sort": "market_cap",
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data["data"]
        except requests.exceptions.Timeout:
            logger.error("Timeout while fetching top coins from CoinMarketCap")
            raise ValueError("CoinMarketCap API timeout")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from CoinMarketCap: {e}")
            raise ValueError(f"CoinMarketCap API error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error from CoinMarketCap: {e}")
            raise ValueError("Network error while fetching data from CoinMarketCap")
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid response from CoinMarketCap: {e}")
            raise ValueError("Invalid data received from CoinMarketCap")