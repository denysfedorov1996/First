import os
import requests
from bs4 import BeautifulSoup
import time
import telegram

# Telegram настройки
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

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

def check_kleinanzeigen():
    url = 'https://www.kleinanzeigen.de/s-63450/zu-verschenken/k0l4285r16'  # ссылка на сайт с фильтром по городу и категории
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

if __name__ == '__main__':
    print("Starte Überwachung...")
    while True:
        try:
            check_kleinanzeigen()
        except Exception as e:
            print("Fehler bei der Überprüfung:", e)
        time.sleep(60)  # интервал 60 секунд
