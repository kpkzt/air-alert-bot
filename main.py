import requests
import time
import schedule

# ID міста Київ в API alerts.in.ua
REGION_ID = "8000000000"

# Зберігаємо останній стан тривоги
last_alert_status = None

# Дані для SendPulse
BOT_ID = "6571c6acaa0e5f3a19061706"
TOKEN = "Bearer 6d56f372c6c2c27a6dfd28e05c3e6eec"  # Не забудь вставити свій токен сюди

def check_air_alert():
    global last_alert_status

    try:
        # Отримуємо дані з alerts.in.ua
        response = requests.get("https://api.alerts.in.ua/v1/alerts/active.json")
        data = response.json()

        # Шукаємо статус по Києву
        active_alerts = [alert for alert in data if alert["location"]["id"] == REGION_ID]
        current_status = "alert" if active_alerts else "clear"

        # Якщо статус змінився — надсилаємо повідомлення
        if current_status != last_alert_status:
            last_alert_status = current_status

            if current_status == "alert":
                message = "🚨 Увага! Повітряна тривога у Києві!"
            else:
                message = "✅ Відбій повітряної тривоги у Києві."

            send_message_to_bot(message)

    except Exception as e:
        print("Помилка перевірки тривоги:", e)

def send_message_to_bot(text):
    url = f"https://api.sendpulse.com/chatbots/{BOT_ID}/messages"
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "message": {
            "type": "text",
            "text": text
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Відповідь SendPulse:", response.status_code, response.text)

# Перевіряємо кожні 30 секунд
schedule.every(30).seconds.do(check_air_alert)

print("Скрипт запущено. Слухаємо тривоги кожні 30 секунд...")

while True:
    schedule.run_pending()
    time.sleep(1)
