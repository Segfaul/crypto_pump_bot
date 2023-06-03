import asyncio
import inspect
import logging
from json import load
from concurrent.futures import ThreadPoolExecutor

import aiogram.utils.markdown as md
from pyrogram import Client, filters
from telebot import TeleBot

from binance_client import BinanceClient
from tg_bot import TelegramBot
from work_db import PumpDB


async def main() -> None:
    func_name = inspect.currentframe().f_code.co_name
    try:
        cfg = load(open("cfg.json", "r"))

        logger = logging.getLogger("pump")
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler('pump.log')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        pump_db_conn = PumpDB(cfg['database']['root'], logger)

        tg_app = Client(
            "pump_s",
            api_id=cfg['telegram']['client_app']['id'],
            api_hash=cfg['telegram']['client_app']['hash']
        )

        aio_bot = TelegramBot(cfg['telegram']['bot']['api_token'], logger,
                              cfg['database']['root'], cfg['telegram']['admins'])
        await aio_bot.dp.skip_updates()

        tele_bot = TeleBot(cfg['telegram']['bot']['api_token'])

        tasks = [
            asyncio.create_task(aio_bot.dp.start_polling()),
            asyncio.create_task(void_logic(tg_app, cfg['telegram']['chat']['example']['link'], tele_bot,
                                           pump_db_conn, logger))
        ]

        await asyncio.gather(*tasks)

    except Exception as error:
        logging.error(f"{func_name}/{error.__class__}||{error.args[0]}")
        quit()


def user_logic(record: tuple, token: str, bot: TeleBot, logger=None):
    func_name = inspect.currentframe().f_code.co_name

    try:
        BinanceClient.buy_order(record[2], record[3], token, record[-1], logger)
        bot.send_message(
            record[0],
            f"&#9725 Trading Pair: {md.hitalic(f'{token}/BTC')} &#9725\n"
            f"\n{md.hbold('Order successfully placed')}&#9989\n"
            f"\nSpent {md.hcode(record[-1] if record[-1] else '100')}% of {md.hcode('BTC')} balance\n"
            f"\nLink to spot Binance: https://www.binance.com/en/trade/{token}_BTC?layout=basic",
            parse_mode='html'
        )
        logger.info(f"{func_name}/{record[-1]}")

    except Exception as error:
        logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")


async def void_logic(app: Client, chat_link: str, bot: TeleBot, pump_db: PumpDB, logger=None):
    @app.on_message(filters.chat(chat_link.split('/')[-1]))
    def handle_message(client, message):
        if '#' in message.text:
            f = message.text.index('#')
            while message.text[f + 1] not in '! " # $ % & ’ ( ) * + , - . / : ; < = > ? @ [  ] ^ _ ` { | } ~.\n':
                f += 1
            # print(message.text[message.text.index('#') + 1:f + 1].upper())
            token = message.text[message.text.index('#') + 1:f + 1].upper()
            with ThreadPoolExecutor(max_workers=5) as executor:
                for record in pump_db.get_all_ready:
                    executor.submit(user_logic, record, token, bot, logger)

    app.run()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())

    finally:
        loop.close()
