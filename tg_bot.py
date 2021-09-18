import telebot

import config
import db_operations


def get_price_months(message, real_bot):
    """
    Function for extracting two numbers from user's message:
    maximal price and month count
    """
    user_id = message.from_user.id

    message_data = message.text.lower().split()
    if len(message_data) != 2:
        real_bot.send_message(
            user_id, "Укажите цену и время"
                     " в месяцах, прошедшее со дня покупки, через пробел"
        )
        return None

    elif not (message_data[0].isdigit() and message_data[1].isdigit()):
        real_bot.send_message(
            user_id, "Макисмальная цена и время в месяцах должны"
                     " быть указаны в виде неотрицательных чисел"
        )
        return None

    return (int(message_data[0]), int(message_data[1]),)


def is_bot_started(message):
    return db_operations.get_user(message.from_user.id) is not None


def get_user_state_checker(required_state):
    def is_required_state(message):
        user = db_operations.get_user(message.from_user.id)
        if user is None:
            return False

        return user['user_state'] == required_state

    return is_required_state


class Bot:
    real_bot = telebot.TeleBot(config.telegram_token)

    @real_bot.message_handler(commands=['help'])
    def help(message):
        Bot.real_bot.send_message(
            message.from_user.id,
            "Перед началом взаимодействия с ботом введите команду /start.\n"
            "У бота доступны следующие команды:\n"
            "- /buy:\n"
            "  Для совершения покупок. Покупать можно"
            " товары 4 типов: pc, tablet, laptop, smartphone.\n"
            "- /sell:\n"
            "  Для продажи товаров. Продавать тоже можно"
            " только товары перечисленных выше типов.\n"
            "- /get_balance:\n"
            "  Для получения текущего баланса.\n"
            "- /help:\n"
            "  Для получения этой инструкции."
        )

    @real_bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.from_user.id

        Bot.real_bot.send_message(user_id,
            "Здравствуйте, это бот онлайн-магазина электронной техники."
            " Для получения инструкции введите команду /help."
        )

        user = db_operations.get_user(user_id)
        if user is None:
            db_operations.create_user(user_id)
        else:
            db_operations.update_user(
                user_id, ('user_state',), ("'select_operation'",)
            )

    @real_bot.message_handler(commands=['buy'], func=is_bot_started)
    def buy(message):
        user_id = message.from_user.id

        db_operations.update_user(
            user_id, ('user_state',), ("'select_buying_type'",)
        )
        Bot.real_bot.send_message(user_id, "Выберите вид техники")

    @real_bot.message_handler(commands=['sell'], func=is_bot_started)
    def sell(message):
        user_id = message.from_user.id

        db_operations.update_user(
            user_id, ('user_state',), ("'select_selling_type'",)
        )
        Bot.real_bot.send_message(user_id, "Выберите вид техники")

    @real_bot.message_handler(commands=['get_balance'], func=is_bot_started)
    def get_balance(message):
        user_id = message.from_user.id

        user = db_operations.get_user(user_id)
        Bot.real_bot.send_message(
            user_id, "Ваш текущий баланс: {}".format(user['money'])
        )

    @real_bot.message_handler(func=lambda message:
          get_user_state_checker('select_operation')(message) or
          not is_bot_started(message)
    )
    def send_help(message):
        user_id = message.from_user.id

        Bot.real_bot.send_message(
            user_id, "Для получения инструкции напишите /help"
        )

    @real_bot.message_handler(
        func=get_user_state_checker('select_buying_type')
    )
    def select_buying_type(message):
        message_text = message.text.lower()
        user_id = message.from_user.id

        if message_text in ['pc', 'tablet', 'laptop', 'smartphone']:
            db_operations.update_user(
                user_id, ('desired_type', 'user_state',),
                ("'{}'".format(message_text), "'select_buying_model'",)
            )
            Bot.real_bot.send_message(user_id, "Выберите модель")
        else:
            Bot.real_bot.send_message(
                user_id, "Такой вид товаров не продается!"
            )

    @real_bot.message_handler(
        func=get_user_state_checker('select_buying_model')
    )
    def select_buying_model(message):
        message_text = message.text.lower()
        user_id = message.from_user.id

        desired_type = db_operations.get_user(user_id)['desired_type']
        device = db_operations.get_device_with_condition(
            "device_type = '{}' AND model = '{}'"
            .format(desired_type, message_text)
        )

        if device is None:
            Bot.real_bot.send_message(user_id, "Таких моделей нет в наличии")
        else:
            db_operations.update_user(
                user_id, ('desired_model', 'user_state',),
                ("'{}'".format(message_text),
                 "'select_buying_max_price_months'",)
            )
            Bot.real_bot.send_message(
                user_id, "Укажите максимально допустимые цену и время"
                         " в месяцах, прошедшее со дня покупки, через пробел"
            )

    @real_bot.message_handler(
        func=get_user_state_checker('select_buying_max_price_months')
    )
    def select_buying_max_price_months(message):
        user_id = message.from_user.id

        price_months = get_price_months(message, Bot.real_bot)
        if price_months is None:
            return
        (price, months) = price_months

        user = db_operations.get_user(user_id)
        buyer_money = user['money']
        if buyer_money < price:
            Bot.real_bot.send_message(user_id,
                "Введите цену, не большую чем ваш баланс."
                " Ваш текущий баланс: {}".format(buyer_money)
            )
            return

        desired_type = user['desired_type']
        desired_model = user['desired_model']

        device = db_operations.get_device_with_condition(
            "device_type = '{}' AND model = '{}' AND"
            " price <= {} AND months <= {}"
            .format(desired_type, desired_model, price, months)
        )

        if device is None:
            Bot.real_bot.send_message(
                user_id, "По вашему запросу ничего не найдено"
            )
        else:
            device_id = device['id']
            seller_id = device['seller_id']
            price = device['price']

            buyer_money -= price
            db_operations.update_user(
                user_id, ('money', 'user_state',),
                (str(buyer_money), "'select_operation'",)
            )

            seller_money = db_operations.get_user(seller_id)['money']
            db_operations.update_user(
                seller_id, ('money',), (str(seller_money + price),)
            )

            db_operations.delete_device(device_id)

            Bot.real_bot.send_message(user_id, "Покупка успешно совершена")
            Bot.real_bot.send_message(
                seller_id,
                "Ваш товар был куплен: {}, {}"
                .format(desired_type, desired_model)
            )

    @real_bot.message_handler(
        func=get_user_state_checker('select_selling_type')
    )
    def select_selling_type(message):
        message_text = message.text.lower()
        user_id = message.from_user.id

        if message_text in ['pc', 'tablet', 'laptop', 'smartphone']:
            db_operations.update_user(
                user_id, ('desired_type', 'user_state',),
                ("'{}'".format(message_text), "'select_selling_model'",)
            )
            Bot.real_bot.send_message(user_id, "Уточните модель")
        else:
            Bot.real_bot.send_message(
                user_id, "Такой вид товаров не продается!"
            )

    @real_bot.message_handler(
        func=get_user_state_checker('select_selling_model')
    )
    def select_selling_model(message):
        message_text = message.text.lower()
        user_id = message.from_user.id

        db_operations.update_user(
            user_id, ('desired_model', 'user_state',),
            ("'{}'".format(message_text), "'select_selling_price_months'",)
        )
        Bot.real_bot.send_message(
            user_id, "Укажите цену и время в месяцах,"
                        " прошедшее со дня покупки"
        )


    @real_bot.message_handler(
        func=get_user_state_checker('select_selling_price_months')
    )
    def select_selling_price_months(message):
        user_id = message.from_user.id

        price_months = get_price_months(message, Bot.real_bot)
        if price_months is None:
            return
        (price, months) = price_months

        user = db_operations.get_user(user_id)
        desired_type = user['desired_type']
        desired_model = user['desired_model']

        db_operations.insert_device(
            (desired_type, desired_model, price, months, user_id,)
        )
        db_operations.update_user(
            user_id, ('user_state',), ("'select_operation'",)
        )
        Bot.real_bot.send_message(
            user_id, "Вы успешно выставили товар на продажу!"
        )

    def execute(self):
        self.real_bot.polling(none_stop=True, timeout=123, interval=0)


def main():
    bot = Bot()
    bot.execute()


if __name__ == '__main__':
    main()
