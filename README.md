# Yeastar SMS → Telegram

Проект для автоматической пересылки SMS с GSM-шлюзов Yeastar TG2000/TG400 в Telegram.

---

## Описание

* Приходит SMS на шлюз Yeastar
* Через API/AMI TCP (порт 5038) скрипт получает событие `ReceivedSMS`
* Декодирует текст (URL-декодирование)
* Определяет SIM-карту (порт шлюза)
* Отправляет SMS в Telegram-чат через бота

---

## Быстрый старт

1. **Клонируем проект**

```bash
git clone https://github.com/LynchDeSanto/YeaStar-sms-to-TG.git
cd YeaStar-sms-to-TG
```

2. **Создаем виртуальное окружение и устанавливаем зависимости**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Создаем файл `.env`**  

Пример данных:

```env
YEASTAR_ADDRESS=192.168.88.20
API_USER=apiuser
API_PASSWORD=apipass
TG_TOKEN=123456789:ABC-XYZ
TG_CHAT=-1001234567890
```

4. **Проверяем работу вручную**

```bash
python main.py
```

В консоли должно появиться:

```
[+] Подключено к Yeastar API. Ожидание новых SMS...
```

---

## Автозапуск на Linux (systemd)

1. Создайте сервис:

```bash
sudo nano /etc/systemd/system/yeastar-sms.service
```

```ini
[Unit]
Description=Yeastar SMS to Telegram
After=network.target

[Service]
Type=simple
User=odmen
WorkingDirectory=/opt/Yeastar-sms-to-TG
ExecStart=/opt/Yeastar-sms-to-TG/.venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

2. Перезагружаем systemd и запускаем сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable yeastar-sms
sudo systemctl start yeastar-sms
sudo systemctl status yeastar-sms
```

---

## Просмотр логов

```bash
journalctl -u yeastar-sms -f
```

---

## Команды systemd

| Команда                              | Описание                         |
| ------------------------------------ | -------------------------------- |
| `sudo systemctl restart yeastar-sms` | Перезапуск сервиса               |
| `sudo systemctl stop yeastar-sms`    | Остановить сервис                |
| `sudo systemctl disable yeastar-sms` | Отключить автозапуск             |
| `journalctl -u yeastar-sms -f`       | Смотреть логи в реальном времени |

---
