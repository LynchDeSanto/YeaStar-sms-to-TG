# Yeastar SMS Listener

Проект для прослушки SMS на шлюзах Yeastar через AMI, с отправкой в Telegram.

## Особенности
- Слушает входящие SMS на всех портах
- Декодирует URL-encoded текст (BOM, кириллица, emoji)
- Сопоставляет GsmSpan с номером SIM
- Отправляет в Telegram
- Логирует все SMS в папку `logs/`

## Установка
1. Клонируем репозиторий:
```bash
git clone https://github.com/ТВОЙ_НИК/yeastar-sms-listener.git
cd yeastar-sms-listener
```
2. Создаем виртуальное окружение:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```
3. Создаём .env с настройками:
```
YEASTAR_ADDRESS=IP
API_USER=apiuser
API_PASSWORD=apipass
TG_TOKEN=твой_телеграм_токен
TG_CHAT=твой_chat_id
```
4. Запуск скрипта:
```bash
python main.py
```

Настройка портов
В main.py обновите словарь PORT_SIM_MAP для сопоставления GsmSpan и номеров SIM:
```
PORT_SIM_MAP = {
    "2": "+39110010396",
    "3": "+79110010397",
}
```
