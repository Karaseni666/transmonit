import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ваш токен API и Chat ID
API_TOKEN = '7505180874:AAH_QnsJoGcsOGMpfGIr5GXAldN_DSxjDdE'  # Ваш API токен
CHAT_ID = '5659245780'  # Ваш Chat ID

# URL для отправки сообщений в Telegram
url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"

# Функция отправки уведомлений в Telegram
def send_telegram_notification(message):
    params = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, params=params)
    print(response.json())  # Проверим ответ от Telegram

# Настройки Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Функция для проверки данных на сайте
def check_transactions(url):
    driver.get(url)

    # Ожидание до тех пор, пока элемент не станет доступным
    try:
        transaction_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Total')]"))
        )
        transaction_text = transaction_element.text  # Например, "Total 96 activities(s)"
        transaction_count = int(transaction_text.split()[1])  # Извлекаем число
        return transaction_count
    except Exception as e:
        print(f"Ошибка при извлечении данных с сайта: {e}")
        return None

# Сайты для проверки
sites = {
    "https://solscan.io/account/DueiMLGtGtiDAjLLoDZwfmm3raETNUvefv7Ue6mxxMKR#defiactivities": None,
    "https://solscan.io/account/GveV6tgHyETgomYnq186WRuDjzhhus2GjWSS5JU9NWFQ#defiactivities": None,
    "https://solscan.io/account/A3r8K2GEFQ1aiUmKhZd7dvRfJTc2XxmwzkbhEpnioSYq#defiactivities": None,
    "https://solscan.io/account/J4wmg1W6qFMQyfmETKrLtZsoMkv9ibhzVXWHVGQcZdcF#defiactivities": None,
    "https://solscan.io/account/7QWUppre2x1mPhP6kuTSbruCpDmBDRQ5cYR2AXYTKSKY#defiactivities": None,
}

# Проверка начальных данных
for site_url in sites:
    count = check_transactions(site_url)
    if count is not None:
        send_telegram_notification(f"Начальное количество транзакций на сайте {site_url}: {count}")
        sites[site_url] = count
    else:
        send_telegram_notification(f"Ошибка при получении данных с сайта {site_url}.")

while True:
    # Периодическая проверка каждые 10 секунд
    time.sleep(10)

    # Проверяем текущие данные
    for site_url in sites:
        current_count = check_transactions(site_url)

        # Если данные изменились, отправляем уведомление
        if current_count and current_count > sites[site_url]:
            message = f"Количество транзакций на сайте {site_url} изменилось! Теперь их {current_count}."
            send_telegram_notification(message)
            sites[site_url] = current_count  # Обновляем предыдущий счетчик для сайта
