import telebot
import sqlite3


def get_query_results(query):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    connection.close()
    return results


def execute_query(query):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.executescript(query)
    connection.close()


def get_state(user_id):
    user_state = get_query_results("SELECT user_state FROM users WHERE user_id = {}".format(user_id))
    if len(user_state) != 0:
        return user_state[0][0]
    else:
        return user_state


def set_state(user_id, state):
    execute_query("UPDATE users SET user_state = '{}' WHERE user_id = {}".format(state, user_id))


def set_desired_model(user_id, model):
    execute_query("UPDATE users SET desired_model = '{}' WHERE user_id = {}".format(model, user_id))


class Bot:
    real_bot = telebot.TeleBot('775986826:AAGHPEOdNI9_bfcIDNG4TQE3tBMDhoIs-FU')

    @real_bot.message_handler(commands=['start'])
    def start(message):
        Bot.real_bot.send_message(message.from_user.id, "Здравствуйте, это бот онлайн-магазина электронной техники")
        user_count = get_query_results("SELECT COUNT(user_id) FROM users WHERE user_id = {}"
                                       .format(message.from_user.id))[0][0]
        if user_count == 0:
            execute_query("INSERT INTO users values({}, 'operation', 'type', 'model', 1000)"
                          .format(message.from_user.id))
        else:
            set_state(message.from_user.id, 'operation')

    @real_bot.message_handler(commands=['reset'])
    def reset(message):
        set_state(message.from_user.id, 'operation')

    @real_bot.message_handler(func=lambda message: get_state(message.from_user.id) == 'operation')
    def operation(message):
        if "купить" in message.text.lower() or "куплю" in message.text.lower():
            Bot.real_bot.send_message(message.from_user.id, "Хорошо, выберите вид техники")
            set_state(message.from_user.id, 'buying_select_type')
        elif "продать" in message.text.lower() or "продам" in message.text.lower():
            Bot.real_bot.send_message(message.from_user.id, "Хоршошо, выберите вид техники")
            set_state(message.from_user.id, 'selling_select_type')
        elif message.text == "/help":
            Bot.real_bot.send_message(message.from_user.id, "напишите 'купить' или 'продать'")
        else:
            Bot.real_bot.send_message(message.from_user.id,
                             "Пожалуйста, уточните, что вы хотите. Воспользуйтесь командой /help, чтобы узнать команды")

    @real_bot.message_handler(func=lambda message: get_state(message.from_user.id) == 'buying_select_type')
    def buying_select_type(message):
        if message.text.lower() in ['pc', 'tablet', 'laptop', 'smartphone']:
            Bot.real_bot.send_message(message.from_user.id, "Выберите модель")
            execute_query(
                "UPDATE users SET desired_type = '{}' WHERE user_id = {}".format(message.text, message.from_user.id))
            set_state(message.from_user.id, 'buying_select_model')
        else:
            Bot.real_bot.send_message(message.from_user.id, "Такой вид товаров не продается!")
            set_state(message.from_user.id, 'operation')

    @real_bot.message_handler(func=lambda message: get_state(message.from_user.id) == "buying_select_model")
    def buying_select_model(message):
        type = get_query_results("SELECT desired_type FROM users WHERE user_id = {}".format(message.from_user.id))[0][0]
        model_count = get_query_results("SELECT COUNT(model) FROM {} WHERE model = '{}'"
                                        .format(type, message.text))[0][0]
        if model_count == 0:
            Bot.real_bot.send_message(message.from_user.id, "Таких моделей не осталось")
        else:
            Bot.real_bot.send_message(
                message.from_user.id,
                "Уточните макс. цену и макс. время в месяцах, прошедшее со дня покупки, через пробел")
            execute_query(
                "UPDATE users SET desired_model = '{}' WHERE user_id = {}".format(message.text, message.from_user.id))
            set_state(message.from_user.id, 'buying_max_price_months')

    @real_bot.message_handler(func=lambda message: get_state(message.from_user.id) == 'buying_max_price_months')
    def buying_max_price_months(message):
        if len(message.text.split()) == 2:
            price = message.text.split()[0]
            months = message.text.split()[1]
        else:
            Bot.real_bot.send_message(message.from_user.id, "Введите корректную информацию")
            return
        type = get_query_results("SELECT desired_type FROM users WHERE user_id = {}".format(message.from_user.id))[0][0]
        model = get_query_results("SELECT desired_model FROM users WHERE user_id = {}"
                                  .format(message.from_user.id))[0][0]
        model_count = get_query_results(
            "SELECT COUNT(model) FROM {} WHERE model = '{}' AND price <= {} AND months <= {}"
                                   .format(type, model, int(price), int(months)))[0][0]

        if model_count == 0:
            Bot.real_bot.send_message(message.from_user.id, "По вашему запросу ничего не найдено")
        else:
            money = int(get_query_results("SELECT money FROM users WHERE user_id = {}"
                                          .format(message.from_user.id))[0][0])
            product = get_query_results(
                "SELECT id, seller_id, price FROM {} WHERE model = '{}' AND price <= {} AND months <= {}".format(type,
                                                                                                        model,
                                                                                                        int(price),
                                                                                                        int(months)))
            id = product[0][0]
            seller_id = product[0][1]
            price = product[0][2]
            money -= price
            if money < 0:
                Bot.real_bot.send_message(message.from_user.id, "У вас недостаточно средств")
            else:
                Bot.real_bot.send_message(message.from_user.id, "Покупка успешно совершена")
                execute_query("UPDATE users SET money = {} WHERE user_id = {}".format(money, message.from_user.id))
                money = int(get_query_results("SELECT money FROM users WHERE user_id = {}".format(seller_id))[0][0])
                money += price
                execute_query("UPDATE users SET money = {} WHERE user_id = {}".format(money, seller_id))
                execute_query("DELETE FROM {} WHERE id = {}".format(type, id))
                set_state(message.from_user.id, 'operation')

    @real_bot.message_handler(func=lambda message: get_state(message.from_user.id) == 'selling_select_type')
    def selling_select_type(message):
        if message.text.lower() in ['pc', 'tablet', 'laptop', 'smartphone']:
            Bot.real_bot.send_message(message.from_user.id, "Уточните модель")
            execute_query(
                "UPDATE users SET desired_type = '{}' WHERE user_id = {}".format(message.text, message.from_user.id))
            set_state(message.from_user.id, 'selling_select_model')
        else:
            Bot.real_bot.send_message(message.from_user.id, "Такой вид товаров не продается!")
            set_state(message.from_user.id, 'operation')

    @real_bot.message_handler(func=lambda message: get_state(message.from_user.id) == 'selling_select_model')
    def selling_select_model(message):
        execute_query("UPDATE users SET desired_model = '{}'".format(message.text))
        Bot.real_bot.send_message(message.from_user.id, "Укажите цену и время в месяцах, прошедшее со дня покупки")
        set_state(message.from_user.id, 'selling_set_price_months')

    @real_bot.message_handler(func=lambda message: get_state(message.from_user.id) == 'selling_set_price_months')
    def selling_set_price_months(message):
        if len(message.text.split()) == 2:
            price = message.text.split()[0]
            months = message.text.split()[1]
        else:
            Bot.real_bot.send_message(message.from_user.id, "Введите корректную информацию!")
            return
        type = get_query_results("SELECT desired_type FROM users WHERE user_id = {}".format(message.from_user.id))[0][0]
        model = get_query_results("SELECT desired_model FROM users WHERE user_id = {}"
                                  .format(message.from_user.id))[0][0]
        id = get_query_results("SELECT COUNT(id) FROM {}".format(type))[0][0]
        execute_query(
            "INSERT INTO {} values ({}, '{}', {}, {}, {})".format(type, id + 1, model, int(price),
                                                                  int(months),
                                                                  message.from_user.id))
        Bot.real_bot.send_message(message.from_user.id, "Вы успешно продали продукт!")
        set_state(message.from_user.id, 'operation')

    def execute(self):
        self.real_bot.polling(none_stop=True, timeout=123, interval=0)


def main():
    bot = Bot()
    bot.execute()


if __name__ == '__main__':
    main()