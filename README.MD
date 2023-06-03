# `Crypto Pump bot`

Telegram bot app for participating in pumps conducted by third-party telegram groups. The bot provides the functionality for accelerated purchase of a particular asset for authorized users (subscription system).

*Pump - a scheme of manipulative price increases in the markets of securities, cryptocurrencies or other similar assets, followed by their strong collapse.*

___
## Video [*usage example*]
https://github.com/Segfaul/crypto_pump_bot/assets/101005929/4c1aafc8-a768-4958-a132-1469fa76af13
___

## *Project Status*

***Completed &#10003;***
___
## Functionality
- [The logic of checking messages](https://github.com/Segfaul/crypto_pump_bot/blob/2818c6f68167fddc5b7e30aa185cd8377ae85220/__init__.py#L75-L88) sent to telegram chat and placing orders among [ready clients](https://github.com/Segfaul/crypto_pump_bot/blob/2818c6f68167fddc5b7e30aa185cd8377ae85220/work_db.py#L301-L320)
- [BinanceClient class](https://github.com/Segfaul/crypto_pump_bot/blob/2818c6f68167fddc5b7e30aa185cd8377ae85220/binance_client.py#L6-L34), responsible for checking balance and placing order by market on the exchange
- The PumpDB class for working with the sqlite3 database and implementing the "Singleton" design pattern
- Pyrogram.Client class, responsible for parsing new channel messages
- [TelegramBot class](https://github.com/Segfaul/crypto_pump_bot/blob/2818c6f68167fddc5b7e30aa185cd8377ae85220/tg_bot.py#L27-L35), responsible for implementing client || admin logics

## Technologies and Frameworks
- Python 3.11 
- Aiogram 2.18
- Pyrogram 2.0.1
- Binance API
- SQLite 3
___

## Installation

1. Clone the repository to the local machine

    ```shell
    git clone https://github.com/Segfaul/crypto_pump_bot.git
    ```

2. Go to the repository directory

    ```shell
    cd crypto_pump_bot
    ```

3. Create and activate a virtual environment

    ```shell
    python -m venv env
    source env/bin/activate
    ```

4. Set project dependencies

    ```shell
    pip install -r requirements.txt
    ```

5. Configure the configuration file cfg.json

    ```shell
    nano cfg.json
    ```

6. Add your telegram account id to [admins](https://github.com/Segfaul/crypto_pump_bot/blob/2818c6f68167fddc5b7e30aa185cd8377ae85220/cfg.json#L4)

    ```json
    "admins": [123]
    ```

7. Run the app logic in the background

    ```python
    python __init__.py &
    ```

8. In case of a problem, the program will stop automatically or you can stop execution using

    ```shell
    ps aux | grep ".py"
    kill PID
    ```
___

## Additional Information

Bot provides the functionality of the admin panel to allow access by third-party users (command -> [/addsub](https://github.com/Segfaul/crypto_pump_bot/blob/2818c6f68167fddc5b7e30aa185cd8377ae85220/tg_bot.py#L448-L502)). 

Also, the internal logic of the database and telegram bot is divided into admin || client logic.
___
