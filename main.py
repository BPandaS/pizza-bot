from config import bot_token

from telebot import TeleBot
from telebot import types

from transitions import Machine
from collections import defaultdict


class Matter(object):
    pass


# Initialize all bot's keyboards
def init_keyboard():
    result = dict()

    keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_order = "Сделать заказ"
    keyboard1.add(btn_order)
    result["main"] = keyboard1

    keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_big = "Большую"
    btn_small = "Маленькую"
    btn_cancel = "<< Назад"
    keyboard2.add(btn_big, btn_small)
    keyboard2.add(btn_cancel)
    result["pizza_type"] = keyboard2

    keyboard3 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_money = "Наличкой"
    btn_card = "Картой"
    btn_cancel = "<< Назад"
    keyboard3.add(btn_card, btn_money)
    keyboard3.add(btn_cancel)
    result["pay_type"] = keyboard3

    keyboard4 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_yes = "Да"
    btn_no = "Нет"
    btn_cancel = "<< Назад"
    keyboard4.add(btn_yes, btn_no)
    keyboard4.add(btn_cancel)
    result["yes/no"] = keyboard4

    keyboard5 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_pizza_type = "Размер пиццы"
    btn_pay_type = "Тип оплаты"
    btn_cancel = "<< Назад"
    keyboard5.add(btn_pizza_type, btn_pay_type)
    keyboard5.add(btn_cancel)
    result["change"] = keyboard5

    return result


# Main bot class
class Bot:
    def __init__(self):
        self.bot = TeleBot(token=bot_token)
        self.keyboard = init_keyboard()

        # User order data
        self.data = defaultdict(dict)

        self.states=["Какую вы хотите пиццу?\nБольшую или маленькую?", "Выберете тип оплаты", "Вы хотите ", "Спасибо за заказ"]
        self.transitions = [
            ['большую', self.states[0], self.states[1]],
            ['маленькую', self.states[0], self.states[1]],
            ['наличкой', self.states[1], self.states[2]],
            ['картой', self.states[1], self.states[2]],
        ]
        self.lump = Matter()
        self.machine = None


    def start_bot(self):
        @self.bot.message_handler(commands=["start"])
        def start(message):
            self.machine = None
            self.data = defaultdict(dict)
            self.bot.send_message(chat_id=message.chat.id, text="Здравствуйте, пожалуйста, сделайте заказ.", reply_markup=self.keyboard["main"])
        

        # Choose pizza type function
        @self.bot.message_handler(func=lambda message: self.machine != None and self.lump.state == self.states[0])
        def entering_pizza_size(message):
            if "pizza_type" not in self.data[message.chat.id]:
                if message.text == "<< Назад":
                    self.machine = None
                    self.bot.send_message(chat_id=message.chat.id, text="... Возвращаюсь назад ...", reply_markup=self.keyboard["main"])
                    return
                self.lump.trigger(str.lower(message.text))
                if self.lump.state == self.states[0]:
                    self.bot.send_message(message.chat.id, text="Извините, пиццы данного размера нет.")
                else:
                    self.data[message.from_user.id]["pizza_type"] = message.text
                    self.bot.send_message(message.chat.id, text=self.states[1], reply_markup=self.keyboard["pay_type"])
            else:
                if message.text == "<< Назад":
                    self.machine.set_state(self.states[2])
                    self.bot.send_message(chat_id=message.chat.id, text=self.states[2] + self.data[message.from_user.id]["pizza_type"] + " пиццу, оплата - " + self.data[message.from_user.id]["pay_type"] + "?", reply_markup=self.keyboard["yes/no"])
                    return
                self.data[message.from_user.id]["pizza_type"] = message.text
                self.lump.trigger(str.lower(message.text))
                if self.lump.state == self.states[0]:
                    self.bot.send_message(message.chat.id, text="Извините, пиццы данного размера нет.")
                else:
                    self.machine.set_state(self.states[2])
                    self.bot.send_message(chat_id=message.chat.id, text=self.states[2] + self.data[message.from_user.id]["pizza_type"] + " пиццу, оплата - " + self.data[message.from_user.id]["pay_type"] + "?", reply_markup=self.keyboard["yes/no"])


        # Choose pay type function
        @self.bot.message_handler(func=lambda message: self.machine != None and self.lump.state == self.states[1])
        def entering_pay_type(message):
            if "pay_type" not in self.data[message.chat.id]:
                if message.text == "<< Назад":
                    self.machine.set_state(self.states[0])
                    self.data[message.from_user.id].pop("pizza_type")
                    self.bot.send_message(chat_id=message.chat.id, text=self.states[0], reply_markup=self.keyboard["pizza_type"])
                    return
                self.lump.trigger(str.lower(message.text))
                if self.lump.state == self.states[1]:
                    self.bot.send_message(message.chat.id, text="Извините, данный тип оплаты не поддерживается.")
                else:
                    self.data[message.from_user.id]["pay_type"] = message.text
                    self.machine.set_state(self.states[2])
                    self.bot.send_message(chat_id=message.chat.id, text=self.states[2] + self.data[message.from_user.id]["pizza_type"] + " пиццу, оплата - " + self.data[message.from_user.id]["pay_type"] + "?", reply_markup=self.keyboard["yes/no"])
            else:
                if message.text == "<< Назад":
                    self.machine.set_state(self.states[2])
                    self.bot.send_message(chat_id=message.chat.id, text=self.states[2] + self.data[message.from_user.id]["pizza_type"] + " пиццу, оплата - " + self.data[message.from_user.id]["pay_type"] + "?", reply_markup=self.keyboard["yes/no"])
                    return
                self.lump.trigger(str.lower(message.text))
                if self.lump.state == self.states[1]:
                    self.bot.send_message(message.chat.id, text="Извините, данный тип оплаты не поддерживается.")
                else:
                    self.data[message.from_user.id]["pay_type"] = message.text
                    self.machine.set_state(self.states[2])
                    self.bot.send_message(chat_id=message.chat.id, text=self.states[2] + self.data[message.from_user.id]["pizza_type"] + " пиццу, оплата - " + self.data[message.from_user.id]["pay_type"] + "?", reply_markup=self.keyboard["yes/no"])


        # User check his data
        @self.bot.message_handler(func=lambda message: self.machine != None and self.lump.state == self.states[2])
        def entering_check(message):
            if message.text == "<< Назад":
                self.machine.set_state(self.states[1])
                self.data[message.from_user.id].pop("pay_type")
                self.bot.send_message(chat_id=message.chat.id, text=self.states[1], reply_markup=self.keyboard["pay_type"])
            elif str.lower(message.text) == "да":
                self.bot.send_message(chat_id=message.chat.id, text=self.states[3], reply_markup=self.keyboard["main"])
                self.machine = None
                # Do sth with data (Now I delete all the data)
                self.data[message.from_user.id] = defaultdict(dict)
            elif str.lower(message.text) == "нет":
                self.bot.send_message(chat_id=message.chat.id, text="Что вы хотите поменять?", reply_markup=self.keyboard["change"])
            elif str.lower(message.text) == "размер пиццы":
                self.machine.set_state(self.states[0])
                self.bot.send_message(message.chat.id, text=self.states[0], reply_markup=self.keyboard["pizza_type"])
            elif str.lower(message.text) == "тип оплаты":
                self.machine.set_state(self.states[1])
                self.bot.send_message(message.chat.id, text=self.states[1], reply_markup=self.keyboard["pay_type"])
            else:
                self.bot.send_message(message.chat.id, text="Извините, данного пункта не существует.")


        @self.bot.message_handler(content_types=["text"])
        def message_handle(message):
            if message.text == "<< Назад":
                self.bot.send_message(chat_id=message.chat.id, text="... Возвращаюсь назад ...", reply_markup=self.keyboard["main"])
            elif message.text == "Сделать заказ":
                self.machine = Machine(model=self.lump, states=self.states, transitions=self.transitions, initial=self.states[0], ignore_invalid_triggers=True)
                self.bot.send_message(message.chat.id, text=self.states[0], reply_markup=self.keyboard["pizza_type"])
            else:
                self.bot.send_message(chat_id=message.chat.id, text="Извините, я не знаю такой команды")


        self.bot.polling(non_stop=True)


# Main bot function
class main():
    bot = Bot()
    bot.start_bot()


if __name__ == "__main__":
    main()
