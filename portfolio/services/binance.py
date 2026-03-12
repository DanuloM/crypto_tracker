import requests
import logging

logger = logging.getLogger(__name__)

class BinanceService:
    BASE_URL = "https://api.binance.com/api/v3"
    
    @staticmethod
    def get_price(symbol: str) -> float:
        try:
            response = requests.get(
                f"{BinanceService.BASE_URL}/ticker/price",
                params={"symbol": f"{symbol}USDT"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return float(data["price"])
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching price for {symbol}")
            raise ValueError(f"Timeout while fetching price for {symbol}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {symbol}: {e}")
            raise ValueError(f"Failed to fetch price for {symbol}: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {symbol}: {e}")
            raise ValueError(f"Network error while fetching price for {symbol}")
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid response data for {symbol}: {e}")
            raise ValueError(f"Invalid price data received for {symbol}")