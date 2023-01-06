from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, CallbackQuery, InputTextMessageContent, InlineQueryResultArticle, InlineQuery
import logging.handlers
import logging
import os
import aiogram
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from parser_ekom_uz import categories, html, get_items
import urllib.request


# Логирование.
logger = logging.getLogger(__name__)

# Записываем в переменную результат логирования
os.makedirs("Logs", exist_ok=True)

# Cоздаёт все промежуточные каталоги, если они не существуют.
logging.basicConfig(  # Чтобы бот работал успешно, создаём конфиг с базовыми данными для бота
    level=logging.INFO,
    format="[%(levelname)-8s %(asctime)s at           %(funcName)s]: %(message)s",
    datefmt="%d.%d.%Y %H:%M:%S",
    handlers=[logging.handlers.RotatingFileHandler("Logs/     TGBot.log", maxBytes=10485760, backupCount=0),
    logging.StreamHandler()])

# Создаём Telegram бота и диспетчер:
Bot = aiogram.Bot("5891681954:AAHnkOkVpyRI3oZjwckgHiGwZnmwF_gfk4M")
DP = aiogram.Dispatcher(Bot, storage=MemoryStorage())


class UserState(StatesGroup):  # Создаём состояния
    item_name = State()  


@DP.message_handler(commands=["start"])      # КОГДА ПОЛЬЗОВАТЕЛЬ ПИШЕТ /start
async def start(msg: Message):

    keyboard = ReplyKeyboardMarkup()
    keyboard.add(*['Выбрать категорию товара', 'Поиск товара по наименованию'])
    await msg.answer("Привет!👋 \n\nЯ Telegram бот, который парсит интернет магазин ekom.uz и помогает тебе быстро выбрать желаемый товар!", reply_markup=keyboard)


@DP.message_handler()
async def ReplyKeyboard_handling(msg: Message):  # Обработка запросов с клавиатуры


    if msg.text == 'Выбрать категорию товара':
        keyboard = InlineKeyboardMarkup()
        for category in categories:
            keyboard.add(aiogram.types.InlineKeyboardButton(
                text=category["category"],
                callback_data=category["link"]
            ))

        await msg.answer("Доступные категории: ", reply_markup=keyboard)

    if msg.text == 'Поиск товара по наименованию':
        keyboard = InlineKeyboardMarkup()
        for category in categories:
            keyboard.add(aiogram.types.InlineKeyboardButton(
                text=category["category"],
                callback_data="search" + category["link"]
            ))

        await msg.answer("Доступные категории: ", reply_markup=keyboard)


@DP.message_handler(state=UserState.item_name)  # Когда появляется состояние с item_name
async def search_by_item_name(msg: Message, state: FSMContext, page=1):
    if page == 1:
        message = await msg.answer("Начинаем парсинг 🔄")
        await state.update_data(msg_id=message.message_id)
        
    data = await state.get_data()
    await Bot.edit_message_text(chat_id=msg.from_user.id, message_id=data["msg_id"], text=f"Парсим страницу {page + 1} 🔄")
    try:
        urllib.request.urlopen(data["url"] + "page-" + str(page))
        items = get_items(html.text, data["url"] + "page-" + str(page))
        for i in items:
            if i["name"] == msg.text:
                await Bot.send_photo(chat_id=msg.from_user.id, caption=f'Название: {i["name"]} \nСсылка: {i["link"]}\nЦена: {i["price"]}\nНаличие: {i["availability"]}', photo=i["photo"])
                break
        else:
            await search_by_item_name(msg, state, page + 1)

    except:
        await msg.answer("По данному запросу не удалось ничего найти.")

    await state.finish()


@DP.callback_query_handler()
async def callback_worker(call: CallbackQuery, state: FSMContext):

    keyboard = InlineKeyboardMarkup()

    if call.data.startswith("search"):
        await state.update_data(url=call.data[6:])
        await call.message.edit_text("Напиши название товара, который хочешь найти")
        await UserState.item_name.set()

    elif call.data in [i["link"] for i in categories]:

        data = await state.get_data()
        await state.update_data(url=call.data)

        for i in range(1, 6):
            try:
                urllib.request.urlopen(call.data + "page-" + str(i))
                keyboard.add(aiogram.types.InlineKeyboardButton(
                    text=i,
                    callback_data=int(i)))
            except:
                pass

        await call.message.edit_text("Выберите страницу, которую хотите получить: ", reply_markup=keyboard)
        
    else:
        call.data = int(call.data)
        data = await state.get_data()
        items = get_items(html.text, data["url"] + "page-" + str(call.data))

        for item in items:
            try:
                await Bot.send_photo(chat_id=call.from_user.id, caption=f'Название: {item["name"]} \nСсылка: {item["link"]}\nЦена: {item["price"]}\nНаличие: {item["availability"]}', photo=item["photo"])
            except:
                break

        for i in range(call.data + 1, call.data + 6):
            try:
                urllib.request.urlopen(data["url"] + "page-" + str(i))
                keyboard.add(aiogram.types.InlineKeyboardButton(
                    text=i,
                    callback_data=i))
            except:
                return

        await Bot.send_message(call.from_user.id, "Выберите страницу, которую хотите получить: ", reply_markup=keyboard)



if __name__ == "__main__":  # Если файл запускается как самостоятельный, а не как модуль
    logger.info("Запускаю бота...")  # В консоле будет отоброжён процесс запуска бота
    executor.start_polling(  # Бот начинает работать
        dispatcher=DP,  # Передаем в функцию диспетчер
        # (диспетчер отвечает за то, чтобы сообщения пользователя доходили до бота)
        on_startup=logger.info("Загрузился успешно!"), skip_updates=True)
    # Если бот успешно загрузился, то в консоль выведется сообщение