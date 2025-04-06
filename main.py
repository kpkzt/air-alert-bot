import os
import time
import requests
import schedule

# ID регіону Київ
REGION_ID = "8000000000"

# Змінні середовища
CLIENT_ID = os.getenv("SENDPULSE_CLIENT_ID")
CLIENT_SECRET = os.getenv("SENDPULSE_CLIENT_SECRET")
BOT_ID = os.getenv("BOT_ID")

# Зберігаємо токен в пам'яті
access_token = None
token_expiry = 0  # в секундах UNIX time

def get_sendpulse_token():
    global access_token, token_expiry
    print("🔐 Отримуємо новий токен доступу SendPulse...")

    url = "https://oauth.sendpulse.com/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if response.status_code == 200 and "access_token" in data:
        access_token = data["access_token"]
        token_expiry = int(time.time()) + data["expires_in"]
        print("✅ Токен отримано")
    else:
        print("❌ Помилка отримання токена:", data)
        access_token = None

def is_token_expired():
    return access_token is None or time.time() > token_expiry - 60  # оновлюємо трохи заздалегідь

def check_air_alert():
    global access_token
    if is_token_expired():
        get_sendpulse_token()

    if not access_token:
        print("⚠️ Немає токена — пропускаємо перевірку.")
        return

    try:
        response = requests.get("https://api.alerts.in.ua/v1/alerts/active.json")
        data = response.json()

        active_alerts = [alert for alert in data if alert["location"]["id"] == REGION_ID]
        current_status = "alert" if active_alerts else "clear"

        # Зберігаємо останній статус в атрибуті функції
        if not hasattr(check_air_alert, "last_status"):
            check_air_alert.last_status = None

        if current_status != check_air_alert.last_status:
            check_air_alert.last_status = current_status
            message = "🚨 Увага! Повітряна тривога у Києві!" if current_status == "alert" else "✅ Відбій повітряної тривоги у Києві."
            send_message_to_bot(message)

    except Exception as e:
        print("❌ Помилка перевірки тривоги:", e)

def send_message_to_bot(text):
    url = f"https://api.sendpulse.com/chatbots/{BOT_ID}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": {
            "type": "text",
            "text": text
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📤 Відправка повідомлення:", response.status_code, response.text)

# Перевіряємо кожні 30 секунд
schedule.every(30).seconds.do(check_air_alert)

print("🚀 Бот запущено. Слухаємо тривоги кожні 30 секунд...")

while True:
    schedule.run_pending()
    time.sleep(1)
