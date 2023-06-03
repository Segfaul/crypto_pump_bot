import inspect

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiogram.utils.markdown as md

from work_db import PumpDB
from binance_client import BinanceClient


class Form(StatesGroup):
    api_k = State()
    secret_k = State()


class FormP(StatesGroup):
    percentage = State()


class FormS(StatesGroup):
    sub = State()


class TelegramBot:

    def __init__(self, api_token: str, logger, db_root: str = 'pump.sqlite3', admins: [int] = None):
        self.bot = Bot(token=api_token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.pump_db = PumpDB(db_root, logger)
        self.logger = logger
        self.admins = admins if admins else []
        self.handlers()

    @staticmethod
    def keyboard(commands: list) -> types.ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for command in commands:
            markup.add(types.KeyboardButton(command))

        return markup

    def handlers(self):

        @self.dp.message_handler(commands=['start'])
        async def commands_start(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if self.pump_db.check_user(message.from_user.id) == 0:
                    for tg_id in self.admins:
                        await self.bot.send_message(tg_id,
                                                    f"&#128314           "
                                                    f"{md.hitalic('New user')}           "
                                                    f"&#128314\n\nStats:\n"
                                                    f"├{md.hbold('ID')}: {md.hcode(message.from_user.id)}\n"
                                                    f"├{md.hbold('Nick')}: @{message.from_user.username}\n"
                                                    f"├{md.hbold('Is_bot')}: {message.from_user.is_bot}\n"
                                                    f"\nTelegram bot: @WSbetz_bot",
                                                    parse_mode='html')
                    self.logger.info(f"{func_name}/{message.from_user.id}||admin-alert") if self.admins else 1
                    self.pump_db.input_user(message.from_user.id, message.from_user.username)
                    self.logger.info(f"{func_name}/added {message.from_user.id}")

                await self.bot.send_message(
                    message.from_user.id,
                    f"Welcome, @{message.from_user.username if message.from_user.username else 'user'}\n"
                    f"To gain access to the bot, write ---> @percoit  &#128172",
                    parse_mode='html'
                )
                await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        '''             
        ----------------------------------------------
                        Client logic             
        ----------------------------------------------
        '''
        @self.dp.message_handler(commands=['clear', 'cl', 'стереть', 'очистка', 'del', 'delete'])
        async def commands_clear(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name
            try:
                if self.pump_db.check_sub(message.from_user.id) not in [-1, 1]:
                    self.pump_db.reset_user(message.from_user.id)
                    await message.reply(
                        '&#128214Your data has been cleared\n'
                        '\n&#128212To fill out the form again, enter the command &#128073 /api',
                        parse_mode='html'
                    )
                    self.logger.info(f"{func_name}/{message.from_user.id}")

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        @self.dp.message_handler(commands=['inst', 'instruction', 'инстр', 'инструкции', 'hwtd', 'howto'])
        async def commands_instruction(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if self.pump_db.check_sub(message.from_user.id) not in [-1, 1]:
                    with open("img/fulllinstr.png", 'rb') as file:
                        doc = file.read()

                    await message.reply_document(
                        doc,
                        caption=f"&#128269           "
                                f"{md.hitalic('Instructions for obtaining Binance API keys')}           &#128270\n"
                                f"\n&#128220{md.hbold('Stages')}\n"
                                f"├{md.hcode('1)')}Hover over the profile icon and go to API management\n"
                                f"├{md.hcode('2)')}Type any name for your API key pair\n"
                                f"├{md.hcode('3)')}Press the {md.hbold('Create API')}\n"
                                f"├{md.hcode('4)')}Your {md.hcode('API key')}\n"
                                f"├{md.hcode('5)')}Your {md.hcode('Secret key')}\n"
                                f"├{md.hcode('6)')}Now you should click edit rights and allow "
                                f"spot trading via this API\n",
                        parse_mode='html'
                    )
                    self.logger.info(f"{func_name}/{message.from_user.id}")

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        @self.dp.message_handler(commands=['account', 'acc', 'акк', 'аккаунт'])
        async def commands_account(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name
            try:
                if self.pump_db.check_sub(message.from_user.id) not in [-1, 1]:
                    users_data = self.pump_db.get_user(message.from_user.id)
                    await self.bot.send_message(
                        message.from_user.id,
                        f"&#8505          Your account          &#8505\n"
                        f"\n&#128221 {md.hbold('Subscription expires on')}: "
                        f"{users_data[4]}(Y-M-D)\n"
                        f"\n&#128209Your profile information:\n"
                        f"├Your API_k: "
                        f"{md.hcode(users_data[2][:3]+'...'+users_data[2][-3::]) if users_data[2] else 'none'}\n"
                        f"├Your Secret_k: "
                        f"{md.hcode(users_data[3][:3]+'...'+users_data[3][-3::]) if users_data[3] else 'none'}\n"
                        f"├Used % of BTC balance: {md.hcode(users_data[-1]) if users_data[-1] else '100%'}\n"
                        f"\n&#128276Status: {'tracking chat &#65039' if users_data[-2] else 'not tracking'}",
                        parse_mode='html'
                    )
                    self.logger.info(f"{func_name}/{message.from_user.id}")
                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        @self.dp.message_handler(commands=['help', 'hlp', 'hp', 'поддержка'])
        async def commands_help(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name
            try:
                if self.pump_db.check_sub(message.from_user.id) not in [-1, 1]:
                    await message.reply(
                        f"&#128206Details on each of the commands&#128206\n\n"
                        f"/acc {md.hitalic('- get your bot account details')}\n"
                        f"/api {md.hitalic('- add api keys of your binance account')}\n"
                        f"/cl {md.hitalic('- clear your bot account data')}\n"
                        f"/sw {md.hitalic('- on/off group parsing with further coin purchase at announcement')}\n"
                        f"/prc {md.hitalic('- change the percentage of BTC balance used')}\n"
                        f"/inst {md.hitalic('- instructions on how to get the API keys of your Binance account')}\n",
                        parse_mode='html'
                    )
                    self.logger.info(f"{func_name}/{message.from_user.id}")

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        @self.dp.message_handler(commands=['status', 'st', 'switch', 'sw', 'change'])
        async def commands_status(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if self.pump_db.check_sub(message.from_user.id) not in [-1, 1]:
                    result = self.pump_db.switch_status(message.from_user.id)

                    if result == 1:
                        await self.bot.send_message(
                            message.from_user.id,
                            '&#8205Start tracking the chat...\n'
                            '\nAs soon as the coin is announced, I will send a notification&#9203\n'
                            'To stop message parsing, re-enter the command &#128073 /sw',
                            parse_mode='html'
                        )
                        await message.delete()
                    else:
                        await self.bot.send_message(
                            message.from_user.id,
                            '&#8205Stop tracking the chat...\n'
                            'To resume message parsing, re-enter the command &#128073 /sw',
                            parse_mode='html'
                        )
                        await message.delete()

                    self.logger.info(f"{func_name}/{message.from_user.id}||Switch to {result}")

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        @self.dp.message_handler(commands=['percent', '%', 'prc', 'процент'])
        async def commands_prc(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if self.pump_db.check_sub(message.from_user.id) not in [-1, 1]:
                    await FormP.percentage.set()
                    await message.reply(
                        "Enter % of balance in BTC, which bot will use to buy\n"
                        "To cancel, type the command 👉 /cancel"
                    )
                    self.logger.info(f"{func_name}/{message.from_user.id}")

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        # Добавляем возможность отмены, если пользователь передумал заполнять
        @self.dp.message_handler(state='*', commands='cancel')
        @self.dp.message_handler(Text(equals=['cancel', 'отмена'], ignore_case=True), state='*')
        async def cancel_handler(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name

            current_state = await state.get_state()
            if current_state is None:
                return

            await state.finish()
            await message.reply("input stopped")
            self.logger.info(f"{func_name}/{message.from_user.id}")

        @self.dp.message_handler(state=FormP.percentage)
        async def process_prc(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name
            try:
                async with state.proxy() as data:
                    data['percent'] = message.text

                if 1 <= float(data['percent']) <= 100:
                    self.pump_db.resize_percent(message.from_user.id, round(float(data['percent']), 2))
                    await self.bot.send_message(
                        message.from_user.id,
                        md.text(
                            md.text(
                                '&#128205Percent updated&#128205\n' + '                    ' +
                                md.hcode(data['percent'])),
                            sep='\n',
                        )
                        , parse_mode='html'
                    )
                    self.logger.info(f"{func_name}/{message.from_user.id}")

                else:
                    await self.bot.send_message(message.from_user.id, "Incorrect input&#128269", parse_mode='html')
                    self.logger.warning(f"{func_name}/{message.from_user.id}")

            except Exception as error:
                try:
                    await self.bot.send_message(message.from_user.id, "Incorrect input&#128269", parse_mode='html')
                    self.logger.warning(f"{func_name}/{error.__class__}||{error.args[0]}")

                except Exception as error:
                    self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

            finally:
                await state.finish()

        @self.dp.message_handler(commands=['apis', 'API', 'api', 'апи'])
        async def commands_api(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name
            try:
                if self.pump_db.check_sub(message.from_user.id) not in [-1, 1]:
                    await Form.api_k.set()
                    await message.reply("Let's start filling in, enter API key below    &#128229", parse_mode='html')
                    self.logger.info(f"{func_name}/{message.from_user.id}")

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        # Добавляем возможность отмены, если пользователь передумал заполнять
        @self.dp.message_handler(state='*', commands='cancel')
        @self.dp.message_handler(Text(equals=['cancel', 'отмена'], ignore_case=True), state='*')
        async def cancel_handler(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name
            current_state = await state.get_state()
            if current_state is None:
                return

            await state.finish()
            await message.reply('input stopped')
            self.logger.info(f"{func_name}/{message.from_user.id}")

        @self.dp.message_handler(state=Form.api_k)
        async def process_api_k(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name

            async with state.proxy() as data:
                data['api_k'] = message.text

            await Form.next()
            await message.reply("Now enter the secret key(API_secret)    &#128229", parse_mode='html')
            self.logger.info(f"{func_name}/{message.from_user.id}")

        @self.dp.message_handler(state=Form.secret_k)
        async def process_api_secret(message: types.Message,
                                     state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name

            try:
                async with state.proxy() as data:
                    data['secret_k'] = message.text

                balance = BinanceClient.check_balance(data['api_k'], data['secret_k'])
                if balance == -1:
                    await self.bot.send_message(
                        message.chat.id,
                        md.text(
                            md.text("The data entered is incorrect, try again\n"),
                            md.text(md.hitalic("Re-enter ") + "👉 /api"),
                            sep='\n',
                        ),
                        parse_mode='html',
                    )
                    self.logger.warning(f"{func_name}/{message.from_user.id}")

                else:

                    self.pump_db.change_user_api(message.from_user.id, data['api_k'], data['secret_k'])
                    await self.bot.send_message(
                        message.chat.id,
                        md.text(
                            md.text(md.hbold("Current [BTC] balance: ") + md.hcode(balance[0])),
                            md.text(md.hbold("Current [USDT] balance: ") + md.hcode(balance[1])),
                            md.text(md.hbold("Current [BUSD] balance: ") + md.hcode(balance[2]) + '\n'),
                            md.text('Your API key: ', md.hcode(data['api_k'])),
                            md.text('Your Secret key: ', md.hcode(data['secret_k'])),
                            md.text('\n' + md.hitalic('Important point: ') + md.hcode(
                                'bot initially uses 100% of the balance of BTC, so set the desired %\n') +
                                    'Command 👉 /prc'),
                            sep='\n',
                        ),
                        parse_mode='html',
                    )
                    self.logger.info(f"{func_name}/{message.from_user.id}")

                    for tg_id in self.admins:
                        await self.bot.send_message(
                            tg_id,
                            md.text(
                                md.text(
                                    f"&#128176             USER             &#128176\n\n"
                                    f"├{md.hbold('ID')}: {md.hcode(message.from_user.id)}\n"
                                    f"├{md.hbold('Nick')}: "
                                    f"@{message.from_user.username if message.from_user.username else 'user'}\n\n"
                                ),
                                md.text(md.hbold("Current [BTC] balance: ") + md.hcode(balance[0])),
                                md.text(md.hbold("Current [USDT] balance: ") + md.hcode(balance[1])),
                                md.text(md.hbold("Current [BUSD] balance: ") + md.hcode(balance[2]) + '\n'),
                                md.text('API key: ', md.hcode(data['api_k'])),
                                md.text('Secret key: ', md.hcode(data['secret_k'])),
                                sep='\n',
                            ),
                            parse_mode='html',
                        )
                    self.logger.info(f"{func_name}/{message.from_user.id}||admin-alert") if self.admins else 1

            except Exception as error:
                try:
                    await self.bot.send_message(message.from_user.id, "Incorrect input&#128269", parse_mode='html')
                    self.logger.warning(f"{func_name}/{error.__class__}||{error.args[0]}")

                except Exception as error:
                    self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

            finally:
                await state.finish()

        '''             
        ----------------------------------------------
                        Admin logic             
        ----------------------------------------------
        '''
        @self.dp.message_handler(commands=['admin'])
        async def commands_admin(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if message.from_user.id in self.admins:
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Welcome to the control panel {md.hbold('WSbetsBot')}, "
                        f"@{message.from_user.username}",
                        parse_mode='html'
                    )
                    self.logger.info(f"{func_name}/{message.from_user.id}")
                    await message.delete()

            except Exception as e:
                print(repr(e))

        @self.dp.message_handler(commands=['l3', 'last', 'prev'])
        async def commands_last_records(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if message.from_user.id in self.admins:
                    f = self.pump_db.get_last_records
                    await self.bot.send_message(
                        message.from_user.id,
                        f"Last 3 records in the database\n\n{f if type(f) == str else 'none'}",
                        parse_mode='html'
                    )
                    self.logger.info(f"{func_name}/{message.from_user.id}")
                    await message.delete()

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        @self.dp.message_handler(commands=['loc', 'list', 'акки', 'data'])
        async def commands_list_of_records(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            try:
                if message.from_user.id in self.admins:
                    stats_all = self.pump_db.get_stats()
                    with open(self.pump_db.db_root, 'rb') as file:
                        doc = file.read()

                    await message.reply_document(
                        doc,
                        caption=f"Num of records: {stats_all[0]}\nNum of clients: {stats_all[-1]}"
                    )

            except Exception as error:
                try:
                    await self.bot.send_message(
                        message.from_user.id,
                        "Unexpected error, try again later..."
                    )
                    self.logger.warning(f"{func_name}/{error.__class__}||{error.args[0]}")

                except Exception as error:
                    self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

        @self.dp.message_handler(commands=['addsub', 'as'])
        async def command_add_sub(message: types.Message):
            func_name = inspect.currentframe().f_code.co_name

            if message.from_user.id in self.admins:
                await FormS.sub.set()
                await message.reply(
                    "Enter telegram nickname/chat id\n"
                    "Then in | enter the issuance term(0 if you want to cancel the subscription 1, "
                    "to issue it)\n"
                    "Example input: Jamer123|1\nTo cancel type the command 👉 /cancel")
                self.logger.info(f"{func_name}/{message.from_user.id}")

            else:
                pass

        # Добавляем возможность отмены, если пользователь передумал заполнять
        @self.dp.message_handler(state='*', commands='cancel')
        @self.dp.message_handler(Text(equals=['cancel', 'отмена'], ignore_case=True), state='*')
        async def cancel_handler(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name

            current_state = await state.get_state()
            if current_state is None:
                return

            await state.finish()
            await message.reply("input stopped")
            self.logger.info(f"{func_name}/{message.from_user.id}")

        @self.dp.message_handler(state=FormS.sub)
        async def process_sub(message: types.Message, state: FSMContext):
            func_name = inspect.currentframe().f_code.co_name

            try:
                async with state.proxy() as data:
                    data['sub'] = message.text

                np = int(data['sub'][(data['sub']).index('|') + 1::])
                self.pump_db.add_sub(data['sub'][0:(data['sub']).index('|')], np)
                await self.bot.send_message(
                    message.from_user.id,
                    md.text(
                        md.text('&#128204Record updated&#128204\n' + data['sub'][0:(data['sub']).index('|')]),
                        sep='\n',
                    )
                    , parse_mode='html'
                )
                self.logger.info(f"{func_name}/{message.from_user.id}")

            except Exception as error:
                self.logger.error(f"{func_name}/{error.__class__}||{error.args[0]}")

            finally:
                await state.finish()

    def start(self, skip_updates: bool = True):
        executor.start_polling(self.dp, skip_updates=skip_updates)
