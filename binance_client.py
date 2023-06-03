import inspect

from binance import Client


class BinanceClient:

    @staticmethod
    def check_balance(api_k: str, api_s: str, logger=None) -> [float] or int:
        func_name = inspect.currentframe().f_code.co_name

        try:
            client = Client(api_k, api_s)
            client.close_connection()
            return [float(client.get_asset_balance(value).get("free")) for value in ["BTC", "USDT", "BUSD"]]

        except Exception as error:
            logger.error(f"{func_name}/{api_k}||{error.__class__},{error.args[0]}") if logger else 1
            return -1

    @staticmethod
    def buy_order(api_k: str, api_s: str, token: str, percent: str = None, logger=None) -> int:
        func_name = inspect.currentframe().f_code.co_name
        try:
            client = Client(api_k, api_s)
            balance = float(client.get_asset_balance("BTC").get("free"))
            client.create_order(symbol=(token + "BTC"), side='BUY', type='MARKET', quoteOrderQty=balance)
            client.close_connection()
            logger.info(f"{func_name}/{api_k}") if logger else 1
            return 0

        except Exception as error:
            logger.error(f"{func_name}/{api_k}||{error.__class__},{error.args[0]}") if logger else 1
            return -1
