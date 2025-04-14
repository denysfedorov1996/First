import requests
from bs4 import BeautifulSoup
import time
import os
import telegram
from flask import Flask

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Проверка, что токены заданы
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не установлены!")

# Список ключевых слов
KEYWORDS = [
    'fahrrad', 'bike', 'e-bike', 'mountainbike', 'citybike',
    'damenfahrrad', 'herrenfahrrad', 'kinderrad', 'klapprad', 'rennrad',
    'fernseher', 'tv', 'smart-tv', 'flachbildfernseher',
    'computer', 'pc', 'desktop', 'monitor', 'bildschirm',
    'laptop', 'notebook', 'macbook',
    'handy', 'smartphone', 'iphone', 'samsung',
    'tablet', 'ipad', 'android-tablet'
]

# Уже отправленные ссылки
sent_links = set()

# Telegram бот
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Flask приложение
app = Flask(__name__)

@app.route('/')
def index():
    return "Server is running!"

# Функция для проверки сайта Kleinanzeigen
def check_kleinanzeigen():
    url = 'https://www.kleinanzeigen.de/s-63450/zu-verschenken/k0l4285r16'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.select('article.aditem')
    for item in items:
        title_tag = item.select_one('.ellipsis')
        link_tag = item.select_one('a')
        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True).lower()
        link = 'https://www.kleinanzeigen.de' + link_tag['href']

        if link in sent_links:
            continue

        if any(keyword in title for keyword in KEYWORDS):
            message = f"Neue Anzeige gefunden:\n{title}\n{link}"
            try:
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                sent_links.add(link)
            except Exception as e:
                print("Fehler beim Senden an Telegram:", e)

# Пинг функции для Render
@app.route('/ping')
def ping():
    check_kleinanzeigen()  # Проверяем сайт
    return "Ping received"

if __name__ == '__main__':
    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=8080)
