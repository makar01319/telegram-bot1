#import telebot
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import BufferedInputFile

import math
from geopy.distance import geodesic
from PIL import Image
import requests
from io import BytesIO
from bs4 import BeautifulSoup
import re
import os
import emoji

bot = Bot(token=os.environ["TOKEN"])
dp = Dispatcher()
#ALLOWED_USERS = [6786356810, 7151289924, 1363237952, 1003452396, 1911144024, 5150929048, 1578662299, 7534631220, 705241092, 2127881707, 1661767451]
BASE_LOCATIONS = {"Харків": (50.00, 36.25), "Маріуполь": (47.10, 37.55), "Суми": (50.91, 34.80)}

MAPS = [
        {
            "url": "https://i.ibb.co/b5j2XrRD/2025-03-01-14-17-37.png",
            "lat_min": 49.972, "lat_max": 53.527,
            "lon_min": 29.399, "lon_max": 43.923
        },
        {
            "url": "https://i.ibb.co/S7D5MZfp/2025-03-01-12-26-19.png",
            "lat_min": 39.84, "lat_max": 48.08,
            "lon_min": 27.49, "lon_max": 56.65
        },
        {
            "url": "https://i.ibb.co/cGBhScb/image-2025-02-20-22-18-21.png",
            "lat_min": 51.43, "lat_max": 58.25,
            "lon_min": 26.89, "lon_max": 56.23
        },
        {
            "url": "https://i.ibb.co/JFKnYNfh/2025-02-20-20-56-32.png",
            "lat_min": 44.20, "lat_max": 51.82,
            "lon_min": 29.07, "lon_max": 57.44
        },
        {
            "url": "https://i.ibb.co/XZnRB6dq/2025-02-20-21-12-10.png",
            "lat_min": 60.93, "lat_max": 70.24,
            "lon_min": 17.01, "lon_max": 78.22
        },
        {
            "url": "https://i.ibb.co/TMc341G2/2025-02-20-21-10-31.png",
            "lat_min": 50.18, "lat_max": 62.65,
            "lon_min": 26.32, "lon_max": 87.63
        },
        {
            "url": "https://i.ibb.co/nsSyv88P/2025-02-21-16-23-47.png",
            "lat_min": 54.14, "lat_max": 65.51,
            "lon_min": 38.98, "lon_max": 96.28
        },
        {
            "url": "https://i.ibb.co/hRvtjktV/8343284.png",
            "lat_min": 53.1774,
            "lat_max": 65.7855,
            "lon_min": -12.1248,
            "lon_max": 33.0397
        },
    ]

DIRECTION_MAP = {
    "пн": 0,
    "пн-сх": 45,
    "сх": 90,
    "пд-сх": 135,
    "пд": 180,
    "пд-зх": 225,
    "зх": 270,
    "пн-зх": 315
}
# Міста та їх координати
cities = {
    "Херсонська область": [
        ("Херсон", (46.6356, 32.6169)),
        ("Новоолексіївка", (46.0929, 32.5503)),
        ("Каховка", (46.7269, 33.4676)),
        ("Генічеськ", (46.4216, 34.7801)),
        ("Скадовськ", (46.3928, 33.5739)),
        ("Олешки", (46.1448, 32.8914)),
        ("Берислав", (46.6425, 33.3953)),
    ],
    "Запорізька область": [
        ("Запоріжжя", (47.8388, 35.1396)),
        ("Мелітополь", (46.0661, 35.3656)),
        ("Бердянськ", (46.7661, 36.8119)),
        ("Енергодар", (47.5096, 34.5858)),
        ("Токмак", (47.5313, 35.6778)),
        ("Василівка", (47.4817, 35.2250)),
        ("Оріхів", (47.4194, 35.6636)),
    ],
    "Донецька область": [
        ("Донецьк", (48.0159, 37.8029)),
        ("Маріуполь", (47.0974, 37.5407)),
        ("Краматорськ", (48.7197, 37.5613)),
        ("Покровськ", (48.2597, 37.2206)),
        ("Бахмут", (48.5747, 38.0295)),
        ("Слов'янськ", (48.8722, 37.6210)),
        ("Дружківка", (48.2925, 37.6162)),
    ],
    "Луганська область": [
        ("Луганськ", (48.5747, 39.3147)),
        ("Сєвєродонецьк", (48.9253, 38.5011)),
        ("Лисичанськ", (48.9221, 38.4525)),
        ("Алчевськ", (48.5784, 38.7417)),
        ("Стаханов", (48.6863, 38.5364)),
        ("Кремінна", (48.7462, 38.3832)),
        ("Попасна", (48.6262, 38.4779)),
    ],
    "Ростовська область": [
        ("Ростов-на-Дону", (47.2357, 39.7015)),
        ("Таганрог", (47.2307, 38.9020)),
        ("Шахти", (48.0395, 40.2232)),
        ("Новочеркаськ", (47.4095, 40.0997)),
        ("Азов", (47.1100, 38.8806)),
        ("Батайськ", (47.2295, 39.7301)),
        ("Волгодонськ", (48.0403, 42.1431)),
    ],
    "Воронезька область": [
        ("Воронеж", (51.6758, 39.2082)),
        ("Россош", (50.8257, 39.4897)),
        ("Лискин", (50.3403, 39.5063)),
        ("Борисоглібськ", (51.2947, 39.6106)),
        ("Павловськ", (50.6290, 39.5082)),
        ("Богучар", (50.6539, 39.2416)),
        ("Острогожськ", (50.8761, 39.3130)),
    ],
    "Бєлгородська область": [
        ("Бєлгород", (50.5937, 36.5858)),
        ("Старий Оскол", (51.2916, 37.8549)),
        ("Грайворон", (50.5446, 36.5654)),
        ("Шебекіно", (50.6144, 36.7190)),
        ("Короча", (50.4981, 36.4954)),
        ("Валуйки", (50.4116, 37.4558)),
        ("Чернянка", (50.3756, 37.2297)),
    ],
    "Курська область": [
        ("Курськ", (51.7373, 36.1876)),
        ("Рильськ", (51.0295, 35.7665)),
        ("Щигри", (51.0405, 36.1763)),
        ("Льгов", (51.3771, 35.6593)),
        ("Суджа", (51.1281, 34.9554)),
        ("Обоянь", (50.7255, 36.1358)),
        ("Фатеж", (51.2766, 36.4244)),
    ],
    "Брянська область": [
        ("Брянськ", (53.2415, 34.3705)),
        ("Клинці", (52.6646, 32.0295)),
        ("Севськ", (52.0995, 33.4299)),
        ("Новозибков", (52.9496, 31.1169)),
        ("Почеп", (53.2490, 33.3876)),
        ("Фокино", (53.0569, 34.3486)),
        ("Жуковка", (53.0255, 33.1424)),
    ]
}

BASE_LOCATIONS = {
    "Харків": (50.00, 36.25),
    "Маріуполь": (47.10, 37.55),
    "Суми": (50.91, 34.80)
}

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
import asyncio
PROVIDER_TOKEN = ""

# Функція для створення клавіатури оплати
def payment_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Оплатити 1 XTR", pay=True)]]
    )
import re
from datetime import datetime
from io import BytesIO

import pytz
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, BufferedInputFile
from aiogram.enums import ContentType, ParseMode
from aiogram.types import Document
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import InputFile
import asyncio

# 🧠 Стан машини
class Form(StatesGroup):
    airfield = State()
    price = State()
    wait_text = State()
    wait_photo = State()

user_data = {}

# /start
@dp.message(Command("airf"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привіт! Введи назву аеродрому:")
    await state.set_state(Form.airfield)


@dp.message(Form.airfield)
async def process_airfield(message: Message, state: FSMContext):
    await state.update_data(airfield=message.text)
    await message.answer("Введи ціну (наприклад 2100 грн):")
    await state.set_state(Form.price)


@dp.message(Form.price)
async def process_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Очікую текстову інформацію про знімок. Потім надішли фото окремо.")
    await state.set_state(Form.wait_text)


@dp.message(Form.wait_text, F.content_type == ContentType.TEXT)
async def handle_text_data(message: Message, state: FSMContext):
    parsed = parse_image_info(message.text)
    if not parsed:
        await message.answer("Не вдалося розпізнати формат. Перевір правильність.")
        return

    await state.update_data(parsed=parsed)
    await message.answer("Добре! Тепер надішли preview-зображення (документом або фото).")
    await state.set_state(Form.wait_photo)


@dp.message(Form.wait_photo, F.document)
async def handle_document(message: Message, state: FSMContext):
    document: Document = message.document

    '''if document.file_name != "image1.png":
        await message.answer("Очікую файл з назвою image1.png.")
        return'''

    file = await bot.download(document.file_id)
    photo_bytes = file.read()
    file.close()

    await send_final_photo(message, state, photo_bytes)


@dp.message(Form.wait_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await bot.download(photo.file_id)
    photo_bytes = file.read()
    file.close()

    await send_final_photo(message, state, photo_bytes)


async def send_final_photo(message: Message, state: FSMContext, photo_bytes: bytes):
    data = await state.get_data()
    airfield = data['airfield']
    price = data['price']
    parsed = data['parsed']

    resolution_label = resolution_to_label(parsed['resolution'])

    caption = f"""<b>➕ Новий знімок знайдено:</b>
авб. {airfield}.

<b>Джерело:</b> {parsed['source']};
<b>Роздільна здатність:</b> {parsed['resolution']} ({resolution_label});
<b>Ціна:</b> {price} грн;
<b>Хмарність:</b> {parsed['cloud']}%;
<b>Дата та час знімку:</b> {parsed['date_kyiv']}."""

    photo_input = BufferedInputFile(photo_bytes, filename="preview.jpg")
    await bot.send_photo(chat_id=message.chat.id, photo=photo_input, caption=caption, parse_mode="HTML")
    await bot.send_photo(chat_id=-1002547942054, photo=photo_input, caption=caption, parse_mode="HTML")
    '''await bot.send_photo(
        chat_id=-1002321030142,
        photo=photo_input,
        caption=caption,
        parse_mode="HTML",
        message_thread_id=30278  # ID гілки (thread)
    )'''
    await bot.send_photo(
        chat_id=-1003092949848,
        photo=photo_input,
        caption=caption,
        parse_mode="HTML",
        message_thread_id=28  # ID гілки (thread)
    )


    #await message.answer("✅ Дані надіслано.", reply_markup=ReplyKeyboardRemove())
    await state.clear()


# 📦 Парсер
def parse_image_info(text):
    try:
        product = re.search(r'Product\s+(.+)', text).group(1).strip()
        resolution = re.search(r'Resolution\s+(.+)', text).group(1).strip()
        cloud = re.search(r'Est Cloud Coverage\s+([0-9.]+)%', text).group(1).strip()
        source = re.search(r'Source\s+(.+)', text).group(1).strip()
        date_utc_str = re.search(r'Date taken\s+(.+ GMT)', text).group(1).strip()

        utc_dt = datetime.strptime(date_utc_str, "%b %d,%Y %H:%M:%S GMT")
        kyiv_dt = pytz.utc.localize(utc_dt).astimezone(pytz.timezone("Europe/Kyiv"))
        formatted_date = kyiv_dt.strftime("%d %B %Y, %H:%M")

        return {
            'product': product,
            'resolution': resolution,
            'cloud': cloud,
            'source': source,
            'date_kyiv': formatted_date
        }
    except Exception as e:
        print("❌ Parser error:", e)
        return None


def resolution_to_label(res):
    try:
        num = float(res.replace("cm", "").strip())
        if num <= 50:
            return "висока"
        elif num <= 150:
            return "середньо-висока"
        else:
            return "низька"
    except:
        return "невідома"

# Обробник команди /donate
@dp.message(Command("donate"))
async def send_invoice_handler(message: Message):
    prices = [LabeledPrice(label="Підтримка", amount=1)]  # 100 XTR = 10000 (бо сума в копійках)
    
    await message.answer_invoice(
        title="Донат власнику бота",
        description="Підтримати власника бота",
        provider_token=PROVIDER_TOKEN,
        currency="XTR",
        prices=prices,
        payload="channel_support",
        reply_markup=payment_keyboard(),
    )

# Обробник передоплатної перевірки
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

# Обробник успішної оплати
@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    await message.answer(
        f"✅ Оплата успішна! ID транзакції: {message.successful_payment.telegram_payment_charge_id}"
    )

@dp.message(Command('refund'))
async def refund_handler(message: Message, bot: Bot, command: CommandObject) -> None:
    transaction_id = command.args
    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id
        )
        await message.answer("Refund initiated successfully.")
    except Exception as e:
        print(e)
        await message.answer("An error occurred while processing the refund.")

# Ваші глобальні змінні
ALLOWED_USERS = ['6307765045', '5846625636', '3113369', '5355006713', '6549051790', '334092624', '1009518020', '6786356810', '1446354057', '5571905790', '7151289924', '1363237952', '1003452396', '1911144024', '5150929048', '1578662299', '7534631220', '705241092', '2127881707', '1661767451']
CHANNEL_ID2 = -1002543043073
TARGET_MESSAGE_ID = 2 
AUTHORIZED_USER_IDS = [1911144024, 6786356810]
forwarding_enabled = None
def get_forwarding_status_from_url():
    global forwarding_enabled
    url = 'https://t.me/ofdsnfajsdnfajdsnf344/2'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_tag = soup.find('meta', property='og:description')
        if meta_tag and 'content' in meta_tag.attrs:
            content = meta_tag['content'].strip().lower()
            forwarding_enabled = content == "on"
        else:
            forwarding_enabled = True
    else:
        forwarding_enabled = True 
        
from aiogram.enums.parse_mode import ParseMode

import asyncio
import emoji
from aiogram import Bot, Dispatcher, F
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION

CHANNEL_ID11 = -1002133315828
ADMIN_IDS11 = [1911144024,6786356810]  # Замініть на свій Telegram ID

# 🔍 Перевірка ключових слів
def contains_target_words(name: str) -> bool:
    name = name.lower()
    keywords = [
        "мірослава", "ангеліна", "повст", "мирослава", "юличка", "юлічка",
        "смотри", "профил", "интим", "t.me", "🥵", "💗", "kira", "ангелинка",
        "ангел", "пусси", "юля", "твоя", "зайка", "🔥", "пуси"
    ]
    return any(word in name for word in keywords)

# 🔍 Перевірка на емодзі (опційно)
def contains_emoji(text: str) -> bool:
    return any(char in emoji.EMOJI_DATA for char in text)

# 🔔 Повідомлення для адміна
async def send_alert(bot: Bot, user, reason: str):
    message = (
        f"🛑 УВАГА! {reason}!\n"
        f"ID: {user.id}\n"
        f"Firstname: {user.first_name or '-'}\n"
        f"Lastname: {user.last_name or '-'}\n"
        f"Username: @{user.username if user.username else '-'}"
    )
    try:
        await bot.send_message(chat_id=-1002775403549, text=message)
    except Exception as e:
        print(f"❌ Помилка надсилання адміну: {e}")

# 🧩 Основна логіка перевірки
async def join_member_channel(event: ChatMemberUpdated, bot: Bot):
    user = event.from_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    try:
        profile = await bot.get_chat(user.id)
        bio = profile.bio or ""
    except Exception as e:
        print(f"⚠️ Не вдалося отримати біо: {e}")
        bio = ""

    # Перевірка одразу після приєднання
    if contains_target_words(full_name) or "t.me" in bio.lower():
        await send_alert(bot, user, reason="Підозрілий підписник при приєднанні")
        return  # Не чекаємо 2 хв — вже підозрілий

    # Якщо все виглядає нормально — спостерігаємо 2 хвилини
    await asyncio.sleep(120)

    try:
        updated_profile = await bot.get_chat(user.id)
        updated_full_name = f"{updated_profile.first_name or ''} {updated_profile.last_name or ''}".strip()
        updated_bio = updated_profile.bio or ""

        # Перевірка на зміну профілю
        if updated_full_name != full_name or updated_bio != bio:
            await send_alert(bot, user, reason="Зміна профілю протягом 2 хвилин після приєднання")
    except Exception as e:
        print(f"⚠️ Не вдалося отримати оновлений профіль: {e}")
dp.chat_member.register(
    join_member_channel,
    ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION),
    F.chat.id == CHANNEL_ID11
)
'''# 🔍 Перевірка ключових слів
def contains_target_words(name: str) -> bool:
    name = name.lower()
    keywords = ["мірослава", "ангеліна", "повст", "мирослава", "юличка", "юлічка", "смотри", "профил", "интим", "t.me", "🥵", "💗", "kira", "ангелинка", "ангел", "пусси", "юля", "твоя", "зайка", "🔥", "пуси"]
    return any(word in name for word in keywords)
def contains_emoji(text: str) -> bool:
    return any(char in emoji.EMOJI_DATA for char in text)
async def join_member_channel(event: ChatMemberUpdated, bot: Bot):
    user = event.from_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    if contains_target_words(full_name):
        message = (
            f"🛑 УВАГА! Новий ПІДОЗРІЛИЙ підписник на каналі!\n"
            f"ID: {user.id}\n"
            f"Firstname: {user.first_name or '-'}\n"
            f"Lastname: {user.last_name or '-'}\n"
            f"Username: @{user.username if user.username else '-'}"
        )
        try:
            await bot.send_message(chat_id=-1002775403549, text=message)
        except Exception as e:
            print(f"❌ Помилка надсилання адміну: {e}")
    else:
        pass

dp.chat_member.register(
    join_member_channel,
    ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION),
    F.chat.id == CHANNEL_ID11
)
'''
@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    # Перевіряємо, чи є у користувача доступ до налаштувань
    if message.from_user.id not in AUTHORIZED_USER_IDS:
        await message.answer("У вас немає доступу до налаштувань.")
        return
    get_forwarding_status_from_url()
    if forwarding_enabled:
        greeting_text = (
            'ℹ️ Зараз пересилка з каналу "<i><b>Повітряні сили ЗСУ</b></i>" — <b>увімкнена.</b>\n\n'
            'Щоб вимкнути пересилку <b>натисни "❌ Вимкнути пересилку"</b> нижче.'
        )
        button_text = "❌ Вимкнути пересилку"
    else:
        greeting_text = (
            'ℹ️ Зараз пересилка з каналу "<i><b>Повітряні сили ЗСУ</b></i>" — <b>вимкнена.</b>\n\n'
            'Щоб увімкнити пересилку <b>натисни "✅ Увімкнути пересилку"</b> нижче.'
        )
        button_text = "✅ Увімкнути пересилку"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=button_text, callback_data="toggle_forwarding")]]
    )
    await message.answer(greeting_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# Функція для обробки натискання на кнопку
@dp.callback_query(F.data == "toggle_forwarding")
async def toggle_forwarding(callback: types.CallbackQuery):
    global forwarding_enabled
    forwarding_enabled = not forwarding_enabled
    if forwarding_enabled:
        button_text = "❌ Вимкнути пересилку"
        greeting_text = (
            'ℹ️ Зараз пересилка з каналу "<i><b>Повітряні сили ЗСУ</b></i>" — <b>увімкнена.</b>\n\n'
            'Щоб вимкнути пересилку <b>натисни "❌ Вимкнути пересилку"</b> нижче.'
        )
    else:
        button_text = "✅ Увімкнути пересилку"
        greeting_text = (
            'ℹ️ Зараз пересилка з каналу "<i><b>Повітряні сили ЗСУ</b></i>" — <b>вимкнена.</b>\n\n'
            'Щоб увімкнити пересилку <b>натисни "✅ Увімкнути пересилку"</b> нижче.'
        )
    try:
        await bot.edit_message_text(
            text = 'on' if forwarding_enabled else 'off',
            chat_id=CHANNEL_ID2,
            message_id=TARGET_MESSAGE_ID,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(f"Error editing message: {e}")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=button_text, callback_data="toggle_forwarding")]]
    )
    await callback.message.edit_text(greeting_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await callback.answer()

from geopy.distance import geodesic
import math

# Функція для обрахунку азимута
def calculate_bearing(start_lat, start_lon, end_lat, end_lon):
    start_lat, start_lon = math.radians(start_lat), math.radians(start_lon)
    end_lat, end_lon = math.radians(end_lat), math.radians(end_lon)

    d_lon = end_lon - start_lon
    x = math.sin(d_lon) * math.cos(end_lat)
    y = math.cos(start_lat) * math.sin(end_lat) - \
        math.sin(start_lat) * math.cos(end_lat) * math.cos(d_lon)
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    return (bearing + 360) % 360

# Обробник команди /h
@dp.message(Command("h"))
async def handle_h_command(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer("❗ Формат: /h <широта> <довгота>\nНаприклад: /h 49.9935 36.2304")
            return
        
        lat, lon = float(parts[1]), float(parts[2])
        kharkiv_coords = (50.00, 36.25)

        distance_km = geodesic(kharkiv_coords, (lat, lon)).kilometers
        bearing_deg = calculate_bearing(kharkiv_coords[0], kharkiv_coords[1], lat, lon)

        await message.answer(
            f"📍 Відстань від Харкова: <b>{round(distance_km)} км</b>\n"
            f"🧭 Азимут: <b>{round(bearing_deg)}°</b>\n\n"
            f"<b>Кінцевий вивід:</b> від ХАРКОВА {round(bearing_deg)}/{round(distance_km)}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.answer("❌ Помилка: перевір формат (потрібне введення широти та довготи в один рядок не розділяючи їх комою). \n\nПриклад: /h 49.99 36.23")
        print(f"Помилка в /h: {e}")
            
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    if str(message.from_user.id) not in ALLOWED_USERS:
        await message.answer("🚫 Вам заборонено користуватися ботом.")
        return

    welcome_text = (
        "<b>Бот допоможе</b> вирахувати локацію за азимутом та віддаленням.\n" 
        "<b>Ввід у форматі:</b>\n\n"
        "1 — місто (Харків/Маріуполь)\n"
        "2 — азимут\n"
        "3 — віддалення\n"
        "4 — курс (необовʼязковий)\n\n"
        "<b>Приклади введення:</b>\n"
        "— Харків 10 555 85\n"
        "— Маріуполь 85 1000 195\n\n"
        "🆕 /get_approx_time — розрахунок <b>приблизного часу </b>прильоту<b> ударних БпЛА до ДКУ.</b>"
    )

    await message.answer(welcome_text, parse_mode=ParseMode.HTML)

locations2 = {
    "1": "Брянськ",
    "2": "Смоленськ",
    "3": "Орел",
    "4": "Курськ",
    "5": "Міллерово",
    "6": "Приморськ-Ахтарськ",
    "7": "Бердянськ",
    "8": "Єйськ",
    "9": "Мис Чауда",
    "10": "Гвардійське",
}

flight_times2 = {
    "1": {
        "ДКУ Шостка": 45,
        "Шостка": 70,
        "ДКУ Суми": 90,
        "Суми": 105,
        "ДКУ Харків": 120,
        "Харків": 140
    },
    "2": {
        "ДКУ Шостка": 90,
        "Шостка": 105,
        "ДКУ Суми": 150,
        "Суми": 170,
        "ДКУ Харків": 190,
        "Харків": 210
    },
    "3": {
        "ДКУ Шостка": 70,
        "Шостка": 90,
        "ДКУ Суми": 90,
        "Суми": 105,
        "ДКУ Харків": 110,
        "Харків": 125
    },
    "4": {
        "ДКУ Шостка": 55,
        "Шостка": 75,
        "ДКУ Суми": 40,
        "Суми": 55,
        "ДКУ Харків": 65,
        "Харків": 80
    },
    "5": {
        "ЛБЗ Сіверськ": 50,
        "ЛБЗ на Купʼянськ": 60,
        "Купʼянськ": 70
    },
    "6": {
        "Дудчани": 120,
        "Херсон": 140,
        "Кінбурнська коса": 160,
        "Одеса": 180
    },
    "7": {
        "Запоріжжя": 55,
        "Берислав": 80,
        "Очаків": 110,
        "Одеса": 150
    },
    "8": {
        "Херсон": 130,
        "Очаків": 165,
        "Одеса": 180
    },
    "9": {
        "Дудчани": 90,
        "Херсон": 100,
        "Кінбурнська коса": 125,
        "Одеса": 140,
        "Вздовж південного узбережжя АР Крим:\nЗміїний": 170,
        "Кінбурнська косa": 170,
        "Одесa": 180
    },
    "10": {
        "Дудчани": 70,
        "Херсон": 75,
        "Кінбурська коса": 85,
        "Одеса": 105
    }
}
user_selection2 = {}
user_time_selection2 = {}
id_on = []

# Перевірка введеного часу
def validate_time_format2(time_input: str) -> str:
    time_input = time_input.strip().replace(":", ".").replace(" ", "")  # Заміняємо пробіли, двокрапки на крапки
    if len(time_input) == 4 and time_input.isdigit():
        return time_input[:2] + ":" + time_input[2:]  # Форматуємо як 00:00
    elif re.match(r"^\d{2}[:.]\d{2}$", time_input):  # Перевіряємо на формат 00:00 або 00.00
        return time_input
    return None

# Перевірка на правильність часу (години до 24, хвилини до 60)
def is_valid_time2(time_input: str) -> bool:
    time_parts = time_input.split(":")
    if len(time_parts) != 2:
        return False
    hours, minutes = time_parts
    try:
        hours = int(hours)
        minutes = int(minutes)
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return True
    except ValueError:
        return False
    return False

# Клавіатура для введення часу
async def get_time_input_keyboard2():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Скасувати ❌", callback_data="cancel")]
    ])

# Клавіатура для вибору локації
def get_location_keyboard2(user_id, page=1):
    pages = [
        [("1️⃣ Брянськ", "1"), ("2️⃣ Смоленськ", "2")], [("3️⃣ Орел", "3"), ("4️⃣ Курськ", "4")],
        [("5️⃣ Міллерово", "5"), ("6️⃣ Приморськ-Ахтарськ", "6")], [("7️⃣ Бердянськ", "7"), ("8️⃣ Єйськ", "8")],
        [("9️⃣ Мис Чауда", "9"), ("🔟 Гвардійське", "10")],
    ]
    
    buttons = [
        [InlineKeyboardButton(
            text=f"✅ {locations2[btn_id]}" if user_selection2.get(user_id) == btn_id else text,
            callback_data=btn_id
        ) for text, btn_id in pages[i]] for i in range((page - 1) * 2, min(page * 2, len(pages)))
    ]
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page - 1}"))
    if page < 3:
        nav_buttons.append(InlineKeyboardButton(text="Далі ➡️", callback_data=f"page_{page + 1}"))
    else:
        nav_buttons.append(InlineKeyboardButton(text="Далі ➡️", callback_data="page_1"))
    if page == 1:
        nav_buttons.insert(0, InlineKeyboardButton(text="⬅️ Назад", callback_data="page_3"))
    
    buttons.append(nav_buttons)
    
    if user_id in user_selection2:
        buttons.append([InlineKeyboardButton(text="Підтвердити локацію ✅", callback_data="confirm_location")])
    
    buttons.append([InlineKeyboardButton(text="Скасувати ❌", callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("get_approx_time"))
async def start(message: types.Message):
    await message.answer(
        "<b>Обери пускову локацію</b> серед запропонованих нижче:\n\n— <b>Північний:</b> Брянськ — 1️⃣, Смоленськ — 2️⃣\n— <b>Північний-схід:</b> Орел — 3️⃣, Курськ — 4️⃣\n— <b>Схід:</b> Міллерово — 5️⃣\n— <b>Південний-схід:</b> Приморськ-Ахтарськ — 6️⃣, Бердянськ — 7️⃣, Єйськ — 8️⃣\n— <b>Південь:</b> Мис Чауда — 9️⃣, Гвардійське — 🔟",
        parse_mode=ParseMode.HTML, reply_markup=get_location_keyboard2(message.from_user.id, 1)
    )

# Обробка натискання кнопок локацій
@dp.callback_query(F.data.in_(locations2.keys()))
async def select_location(callback: CallbackQuery):
    user_selection2[callback.from_user.id] = callback.data
    id_on.append(callback.from_user.id)  # Додаємо користувача в список id_on
    await callback.message.edit_text(
        "ℹ️ Тепер введи час у форматі 0000, <b>не розділяючи цифри нічим</b>. Наприклад, якщо ти хочеш ввести <b>12 годину 10 хвилин напиши 1210</b>.",
        parse_mode=ParseMode.HTML, reply_markup=await get_time_input_keyboard2()
    )
    await callback.answer()

# Обробка натискання кнопок пагінації
@dp.callback_query(F.data.startswith("page_"))
async def navigate_pages(callback: CallbackQuery):
    page = int(callback.data.split("_")[1])  # Отримуємо номер сторінки
    user_id = callback.from_user.id
    await callback.message.edit_text(
        "Обери пускову локацію серед запропонованих нижче:",
        reply_markup=get_location_keyboard2(user_id, page)
    )
    await callback.answer()

@dp.callback_query(F.data == "cancel")
async def cancel_selection(callback: CallbackQuery):
    user_selection2.pop(callback.from_user.id, None)
    id_on.remove(callback.from_user.id)
    await callback.message.edit_text("❌ Розрахунок часу успішно скасовано.")
    await callback.answer()

locations = {
    "курс": "Курськ",
    "чауд": "мис Чауда",
    "ахт": "Приморськ-Ахтарськ",
    "орла": "Орел",
    "орел": "Орел",
    "орлов": "Орел",
    "брянс": "Брянська",
    "навл": "Брянська",
    "єйсь": "Єйськ",
    "шат": "Смоленськ",
    "міл": "Міллерово (Ростовська обл.)"
}

'''
def remove_emojis(text: str) -> str:
    text_no_spaces_after_emojis = re.sub(r'([\U00010000-\U0010ffff])\s+', r'\1', text)
    text_cleaned = emoji.replace_emoji(text_no_spaces_after_emojis, replace='')
    text_no_extra_spaces = re.sub(r'\s+', ' ', text_cleaned).strip()
    return text_no_extra_spaces
'''
@dp.message(Command("send_msg"))
async def send_message_to_group(message: types.Message):
    # Перевірка дозволених користувачів
    if str(message.from_user.id) not in ALLOWED_USERS:
        await message.answer("У вас немає прав для надсилання повідомлень через цю команду.")
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("❌ Невірний формат. Використовуйте:\n`/send_msg <chat_id> <текст повідомлення>`", parse_mode=ParseMode.MARKDOWN)
        return

    try:
        chat_id = int(parts[1])
        text_to_send = parts[2]
        await bot.send_message(chat_id=chat_id, text=text_to_send)
        await message.answer("✅ Повідомлення успішно надіслано.")
    except Exception as e:
        await message.answer(f"❌ Помилка при надсиланні повідомлення:\n<code>{e}</code>", parse_mode=ParseMode.HTML)

from datetime import datetime, timedelta
def remove_emojis(text: str) -> str:
    emojis = [
        "🚀 ", "🚀", "🛫 ", "🛫", "🛬 ", "🛬", "✈ ", "✈", "🛸 ", "🛸", "🛵 ", "🛵",
        "☄ ", "☄", "💥 ", "💥", "🚁 ", "🚁", "⚠ ", "⚠", "⚠️ ", "⚠️", "📢 ", "📢",
        "⚡ ", "⚡", "🗺 ", "🗺", "🔱 ", "🔱", "🛩️ ", "🛩️", "✈️ ", "✈️", "⚡️ ", "⚡️", "🚨", "🚨 ", "➡️", "➡️ "
    ]
    emoji_pattern = '|'.join(map(re.escape, emojis))
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.replace("!", ".")  # Заміна всіх "!" на "."
        line = re.sub(emoji_pattern, '', line)  # Видаляємо емодзі
        line = re.sub(r'\s+', ' ', line).strip()  # Видаляємо зайві пробіли

        if 'загроза застосування авіа' in line.lower():
            continue  # Прибираємо весь рядок, що містить це

        line = re.sub(r'\bворо\S*', '', line, flags=re.IGNORECASE)  # Прибираємо слова, що починаються на "воро"

        # Видаляємо слово "увага" + опціональний "!" після нього
        line = re.sub(r'\bувага\b[.!]?', '', line, flags=re.IGNORECASE).strip()

        if not line:
            continue

        if 'відбій' in line.lower():
            line = "🟢 " + line

        cleaned_lines.append(line)
    cleaned_text = '\n'.join(cleaned_lines)
    if 'бпла' in cleaned_text.lower() and 'розв' not in cleaned_text.lower() and 'загр' not in cleaned_text.lower():
        kyiv_time = datetime.utcnow() + timedelta(hours=3)
        time_str = kyiv_time.strftime('%H:%M')
        cleaned_text = f"{time_str}\n\n" + '\n\n'.join(cleaned_text.split('\n'))
    return cleaned_text

@dp.message()
async def handle_message(message: types.Message):
    global forwarding_enabled
    user_id = int(message.from_user.id)
    get_forwarding_status_from_url()
    if forwarding_enabled:
        if message.chat.id == -1002419856421:
            if message.text:
                cleaned_text = remove_emojis(message.text)
                if '@' not in cleaned_text and 't.me' not in cleaned_text and 'Auto_Forward_Messages_Bot' not in cleaned_text:
                    await bot.send_message(chat_id=-1002133315828, text=cleaned_text)
                else:
                    pass
    if str(user_id) not in ALLOWED_USERS:
        await message.reply(f"🚫 Вам заборонено користуватися ботом, {user_id}.")
        return
    if message.from_user.id in id_on:
        time_input = message.text.strip()
        validated_time = validate_time_format2(time_input)
        
        if validated_time and is_valid_time2(validated_time):
            location_id = user_selection2.get(message.from_user.id, "")
            flight_time_data = flight_times2.get(location_id, {})
            
            hours, minutes = map(int, validated_time.split(":"))
            message_text = f"ℹ️ <b> Підліт БпЛА з {locations2[location_id]} </b> (пуск о <b>{validated_time}</b>).\n\n"
            
            # Рахуємо час підльоту для кожного пункту
            for point, flight_time in flight_time_data.items():
                flight_hours = (minutes + flight_time) // 60
                flight_minutes = (minutes + flight_time) % 60
                target_time = f"{hours + flight_hours:02}:{flight_minutes:02}"
                message_text += f"{point} — <b>{target_time}</b>;\n"
            
            await message.answer(message_text, parse_mode=ParseMode.HTML)
            id_on.remove(message.from_user.id)
            # Скидаємо дані про вибір
            user_selection2.pop(message.from_user.id, None)
        else:
            await message.answer("Будь ласка, введіть час у правильному форматі без пробілів.")
            id_on.remove(message.from_user.id)
    if message.text and ('‼️' in message.text or '🛑' in message.text or 'Харків' in message.text or 'Маріуполь' in message.text or "Суми" in message.text or 'Балістика' in message.text):
        #await bot.send_message(1911144024, 'повідомлення отримане')
        if re.match(r"(‼️|🛑) \d{1,2}:\d{2} (пуск|відмічено пуск|запуск)", message.text.lower()):
            text = message.text.lower()
            detected_locations = set()
            for key, value in locations.items():
                if key in text:
                    detected_locations.add(value)
            if detected_locations:
                if message.from_user.id == 6786356810:
                    formatted_locations = ", ".join(sorted(detected_locations))
                    response = f"Відмічено пуски шахедів з району {formatted_locations}."
                    await bot.send_message(-1002133315828, response)
                    return
                elif message.from_user.id == 1911144024:
                    formatted_locations = " та ".join(sorted(detected_locations))
                    response = f"Відмічено пуски шахедів з району {formatted_locations}."
                    await bot.send_message(-1002339688858, response)
                    return
        if "Харків" in message.text or "Маріуполь" in message.text or "Суми" in message.text:
            print('1')
            ARROW_URL = "https://i.ibb.co/bjPrgtgV/1-1.png"
            #ARROW_URL = "https://i.ibb.co/MDYsw1s9/1.png"
            CIRCLE_URL = "https://i.ibb.co/xqxGGJ0n/24.png"
            try:
                parts = message.text.split()
                if len(parts) < 3 or len(parts) > 4:
                    #raise ValueError("Неправильний формат. Використовуйте: 'Харків 45 100 [90 або сх]'")
                    pass
                    #raise ValueError('')
        
                city, azimuth, distance = parts[:3]
                course = parts[3] if len(parts) == 4 else None
                azimuth, distance = map(float, [azimuth, distance])
        
                if city not in BASE_LOCATIONS:
                    raise ValueError("Місто має бути або 'Харків', або 'Маріуполь'.")
        
                if course is not None:
                    if course.lower() in DIRECTION_MAP:
                        course = DIRECTION_MAP[course.lower()]
                    else:
                        course = float(course)
        
                lat0, lon0 = BASE_LOCATIONS[city]
                R = 6371
                d_rad = distance / R
                azimuth_rad = math.radians(azimuth)
        
                lat1 = math.asin(math.sin(math.radians(lat0)) * math.cos(d_rad) +
                                math.cos(math.radians(lat0)) * math.sin(d_rad) * math.cos(azimuth_rad))
                lon1 = math.radians(lon0) + math.atan2(math.sin(azimuth_rad) * math.sin(d_rad) * math.cos(math.radians(lat0)),
                                                        math.cos(d_rad) - math.sin(math.radians(lat0)) * math.sin(lat1))
                lat1, lon1 = math.degrees(lat1), math.degrees(lon1)
        
                selected_map = next((m for m in MAPS if m["lat_min"] <= lat1 <= m["lat_max"] and m["lon_min"] <= lon1 <= m["lon_max"]), None)
                if not selected_map:
                    await message.reply("Координати поза мапою.")
                    return
        
                response = requests.get(selected_map["url"])
                img = Image.open(BytesIO(response.content))
                MAP_WIDTH, MAP_HEIGHT = img.size
                x = int((lon1 - selected_map["lon_min"]) / (selected_map["lon_max"] - selected_map["lon_min"]) * MAP_WIDTH)
                y = int((selected_map["lat_max"] - lat1) / (selected_map["lat_max"] - selected_map["lat_min"]) * MAP_HEIGHT)
        
                img_obj_url = ARROW_URL if course is not None else CIRCLE_URL
                response_obj = requests.get(img_obj_url)
                obj_img = Image.open(BytesIO(response_obj.content)).convert("RGBA")
                obj_size = int(MAP_WIDTH * (0.05 if course is not None else 0.03))
                obj_img = obj_img.resize((obj_size, obj_size), Image.LANCZOS)
                if course is not None:
                    obj_img = obj_img.rotate(360 - course, expand=True)
                img.paste(obj_img, (x - obj_size // 2, y - obj_size // 2), obj_img)
        
                description = f'<b>Проліт</b> за <b>координатами</b>:<code> {lat1:.4f}, {lon1:.4f}</code>'
                if course is not None:
                    description += f'\n<b>Курс</b>: <code>{get_course_description(course)}</code>'
        
                # Save the image into a BytesIO object
                output = BytesIO()
                img.save(output, format="PNG")
                output.seek(0)
                photo = BufferedInputFile(output.getvalue(), filename="image.png")
                await bot.send_photo(message.chat.id, photo, caption=description, parse_mode="HTML")
                
            except Exception as e:
                # Log error and ensure a valid message is returned
                if message.chat.type == 'private':
                    await bot.send_message(message.chat.id, f"Error: {str(e)}")
                else:
                    print(f'Error: {str(e)}')

def convert_to_decimal(degrees, minutes, seconds, direction):
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal
def find_nearest_city(user_coordinates):
    nearest_city = None
    nearest_region = None
    nearest_distance = float('inf')
    
    for region, cities_list in cities.items():
        for city_name, city_coords in cities_list:
            distance = geodesic(user_coordinates, city_coords).kilometers
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_city = city_name
                nearest_region = region
    
    return nearest_city, nearest_region, nearest_distance
def parse_coordinates(coord_str):
    lat_str, lon_str = coord_str.split(", ")
    
    # Розбір широти
    lat_deg, lat_min, lat_sec, lat_dir = lat_str.replace('°', '').replace("'", '').replace('"', '').split()
    
    # Розбір довготи
    lon_deg, lon_min, lon_sec, lon_dir = lon_str.replace('°', '').replace("'", '').replace('"', '').split()
    
    return (lat_deg, lat_min, lat_sec, lat_dir), (lon_deg, lon_min, lon_sec, lon_dir)

# Функція для конвертації в десяткові координати
def convert_to_decimal(degrees, minutes, seconds, direction):
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal
# Функція для визначення курсу
def get_course_description(course):
    course = course % 360  # Коригуємо курс в діапазоні [0, 360)
    
    if 345 <= course <= 360 or 0 <= course < 15:
        return "північний"
    elif 15 <= course < 75:
        return "північно-східний"
    elif 75 <= course < 105:
        return "східний"
    elif 105 <= course < 165:
        return "південно-східний"
    elif 165 <= course < 195:
        return "південний"
    elif 195 <= course < 255:
        return "південно-західний"
    elif 255 <= course < 285:
        return "західний"
    elif 285 <= course < 345:
        return "північно-західний"
    else:
        return "невизначений"
    
def mark_on_map(lat1, lon1, course=None):
    # Мапи для вибору
    MAPS = [
        {
            "url": "https://i.ibb.co/b5j2XrRD/2025-03-01-14-17-37.png",
            "lat_min": 49.972, "lat_max": 53.527,
            "lon_min": 29.399, "lon_max": 43.923
        },
        {
            "url": "https://i.ibb.co/S7D5MZfp/2025-03-01-12-26-19.png",
            "lat_min": 27.49, "lat_max": 56.65,
            "lon_min": 39.84, "lon_max": 48.08
        },
        {
            "url": "https://i.ibb.co/cGBhScb/image-2025-02-20-22-18-21.png",
            "lat_min": 51.43, "lat_max": 58.25,
            "lon_min": 26.89, "lon_max": 56.23
        },
        {
            "url": "https://i.ibb.co/JFKnYNfh/2025-02-20-20-56-32.png",
            "lat_min": 44.20, "lat_max": 51.82,
            "lon_min": 29.07, "lon_max": 57.44
        },
        {
            "url": "https://i.ibb.co/XZnRB6dq/2025-02-20-21-12-10.png",
            "lat_min": 60.93, "lat_max": 70.24,
            "lon_min": 17.01, "lon_max": 78.22
        },
        {
            "url": "https://i.ibb.co/TMc341G2/2025-02-20-21-10-31.png",
            "lat_min": 50.18, "lat_max": 62.65,
            "lon_min": 26.32, "lon_max": 87.63
        },
        {
            "url": "https://i.ibb.co/nsSyv88P/2025-02-21-16-23-47.png",
            "lat_min": 54.14, "lat_max": 65.51,
            "lon_min": 38.98, "lon_max": 96.28
        }
    ]

    selected_map = next((m for m in MAPS if m["lat_min"] <= lat1 <= m["lat_max"] and m["lon_min"] <= lon1 <= m["lon_max"]), None)
    if not selected_map:
        return None
    response = requests.get(selected_map["url"])
    img = Image.open(BytesIO(response.content))
    MAP_WIDTH, MAP_HEIGHT = img.size

    # Обчислення координат x, y на карті
    x = int((lon1 - selected_map["lon_min"]) / (selected_map["lon_max"] - selected_map["lon_min"]) * MAP_WIDTH)
    y = int((selected_map["lat_max"] - lat1) / (selected_map["lat_max"] - selected_map["lat_min"]) * MAP_HEIGHT)

    # Вибір маркера (стрілка або коло) та його зображення
    ARROW_URL = "https://i.ibb.co/bjPrgtgV/1-1.png"
    #ARROW_URL = "https://i.ibb.co/MDYsw1s9/1.png"
    CIRCLE_URL = "https://i.ibb.co/xqxGGJ0n/24.png"
    img_obj_url = ARROW_URL if course is not None else CIRCLE_URL
    response_obj = requests.get(img_obj_url)
    obj_img = Image.open(BytesIO(response_obj.content)).convert("RGBA")
    obj_size = int(MAP_WIDTH * (0.05 if course is not None else 0.03))
    obj_img = obj_img.resize((obj_size, obj_size), Image.LANCZOS)
    if course is not None:
        obj_img = obj_img.rotate(360 - course, expand=True)
    img.paste(obj_img, (x - obj_size // 2, y - obj_size // 2), obj_img)
    return img
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

'''
            if re.match(r"^Балістика\n(\d{1,2}° \d{1,2}' \d{1,2}\" [NS]), (\d{1,3}° \d{1,2}' \d{1,2}\" [EW])\nКурс (\d+)$", message.text):
                try:
                    await bot.send_message(1911144024, 'етап0')
                    parts = message.text.splitlines()
                    await bot.send_message(1911144024, 'етап0.5')
                    if len(parts) != 3:
                        await message.reply('ℹ️ Помилка:\nПереконайтеся, <b>що повідомлення має вигляд:</b>\n\n— Балістика\n51° 46\' 5" N, 36° 19\' 42" E" E\nКурс 210\n— Харків 100 100 100\n— Маріуполь 0 100 100\n\n<b>Або</b> без додаткового параметра:\n— Харків 100 100\n— Маріуполь 0 100', parse_mode=ParseMode.HTML)
                        raise ValueError('ℹ️ Помилка 1')
                    if parts[0] != "Балістика":
                        await message.reply('ℹ️ Помилка:\nПереконайтеся, <b>що повідомлення має вигляд:</b>\n\n— Балістика\n51° 46\' 5" N, 36° 19\' 42" E" E\nКурс 210\n— Харків 100 100 100\n— Маріуполь 0 100 100\n\n<b>Або</b> без додаткового параметра:\n— Харків 100 100\n— Маріуполь 0 100', parse_mode=ParseMode.HTML)
                        raise ValueError('ℹ️ Помилка 2')
                    await bot.send_message(1911144024, 'етап1')
                    coord_str = parts[1]
                    (lat_deg, lat_min, lat_sec, lat_dir), (lon_deg, lon_min, lon_sec, lon_dir) = parse_coordinates(coord_str)
                    lat1 = convert_to_decimal(lat_deg, lat_min, lat_sec, lat_dir)
                    lon1 = convert_to_decimal(lon_deg, lon_min, lon_sec, lon_dir)
                    nearest_city, nearest_region = find_nearest_city((lat1, lon1))
                    course = float(parts[2].split()[1])
                    course_description = get_course_description(course)
                    img = mark_on_map(lat1, lon1, course)
                    if img is None:
                        await message.reply("🚫 Помилка: не вдалося створити зображення.")
                    else:
                        await bot.send_message(1911144024, 'е2')
                        img.save("output_map.png")
                        with open("output_map.png", "rb") as f:
                            await bot.send_photo(
                                message.chat.id, 
                                f, 
                                caption=f"<b>Найближче місто</b>: <code>{nearest_city}</code>, <code>{nearest_region}</code>.\n"
                                        f"<b>Курс</b>: <code>{course_description}</code>",
                                parse_mode=ParseMode.HTML
                            )
                except ValueError as e:
                    await bot.send_message(1911144024, f"Error: {str(e)}")
'''
