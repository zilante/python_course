# Telegram bot

#### Описание
Это репозиторий телеграм бота @blue_sales_bot, который позволяет продавать и покупать технику в вымышленном магазине.
При создании была использована `Python` библиотека `telebot`.

#### Инструкция по установке и запуску на локальной машине
* установите `Python`, `pip`
* создайте виртуальное окружение
```bash
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```
Когда захотите выйти из этого окружения, используйте команду
`deactivate`
* создайте базу данных
```bash
python3 setup.py
```
* создайте файл `config.py` и поместите туда строку `telegram_token='<your_telegram_token>'`,
где нужно указать API токен, полученный от @BotFather
* запустите бота
```bash
python3 tg_bot.py
```