import requests
from bs4 import BeautifulSoup
import time
import os
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading
import asyncio

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не установлены!")

# Ключевые слова
KEYWORDS = [
    'fahrrad', 'bike', 'e-bike', 'mountainbike', 'citybike',
    'damenfahrrad', 'herrenfahrrad', 'kinderrad', 'klapprad', 'rennrad',
    'fernseher', 'tv', 'smart-tv', 'flachbildfernseher',
    'computer', 'pc', 'desktop', 'monitor', 'bildschirm',
    'laptop', 'notebook', 'macbook',
    'handy', 'smartphone', 'iphone', 'samsung',
    'tablet', 'ipad', 'android-tablet'
]

sent_links = set()
bot = Bot(token=TELEGRAM_TOKEN)

# Функция для отправки сообщений в Telegram
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply("Привет! Это тестовое сообщение от Kleinanzeigen-бота.")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

# Функция проверки сайта
async def check_kleinanzeigen():
    print("Проверка новых объявлений...")  # Отладка
    url = 'https://www.kleinanzeigen.de/s-63450/zu-verschenken/k0l4285r16'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Отправляем запрос и проверяем статус
    response = requests.get(url, headers=headers)
    print(f"Статус ответа: {response.status_code}")  # Отладка

    # Если статус не 200, прерываем выполнение
    if response.status_code != 200:
        print("Ошибка: не удалось загрузить страницу.")
        return

    # Парсим страницу
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все объявления
    items = soup.select('article.aditem')
    print(f"Найдено объявлений: {len(items)}")  # Отладка

    for item in items:
        title_tag = item.select_one('.ellipsis')
        link_tag = item.select_one('a')

        # Если нет заголовка или ссылки, пропускаем
        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True).lower()
        link = 'https://www.kleinanzeigen.de' + link_tag['href']

        print(f"Обрабатываем объявление: {title} ({link})")  # Отладка

        # Пропускаем уже отправленные ссылки
        if link in sent_links:
            print(f"Пропускаем уже отправленную ссылку: {link}")  # Отладка
            continue

        # Проверяем на ключевые слова
        if any(keyword in title for keyword in KEYWORDS):
            message = f"Neue Anzeige gefunden:\n{title}\n{link}"
            try:
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                sent_links.add(link)
                print(f"Отправлено сообщение: {message}")  # Отладка
            except Exception as e:
                print("Ошибка при отправке в Telegram:", e)

# Поток проверки каждые 60 секунд
async def run_checker():
    print("Запуск проверки каждые 60 секунд...")  # Отладка
    while True:
        try:
            await check_kleinanzeigen()
        except Exception as e:
            print(f"Ошибка в функции проверки: {e}")
        await asyncio.sleep(60)

# Основная асинхронная функция для запуска бота и проверки
async def main():
    # Настроим бота с использованием новой версии библиотеки
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчик для команды /test
    application.add_handler(CommandHandler("test", send_message))

    # Запуск фоновой проверки
    asyncio.create_task(run_checker())

    # Запуск бота
    await application.run_polling()

if __name__ == '__main__':
    # Запуск асинхронного приложения
    asyncio.run(main())
