#!/home/dmitriy/donntu_bot/venv/bin/python
import telebot
import time
import datetime
import cherrypy
import json

from telebot import apihelper
from telebot import types
from datetime import date

import config
import util

import text_config as text_conf
import inline_config as inline_conf
import markups_config as markups_conf

# WEBHOOK_HOST = '195.69.187.63'
# WEBHOOK_PORT = 88  # 443, 80, 88 или 8443 (порт должен быть открыт!)В
# WEBHOOK_LISTEN = '0.0.0.0'

# WEBHOOK_SSL_CERT = './webhook_cert.pem'
# WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

# WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
# WEBHOOK_URL_PATH = "/%s/" % (config.BOT_TOKEN)

HISTORY = {}


bot = telebot.TeleBot(config.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    if not util.get_user_by_id(message.from_user.id):
        bot.send_message(message.from_user.id, text_conf.welcome, parse_mode='HTML',
                         reply_markup=markups_conf.main_menu())
        util.welcome_user(message.from_user.id)
    else:
        bot.send_message(message.from_user.id, '🔃 Бот перезапущен 🔃', reply_markup=markups_conf.main_menu())

@bot.message_handler(commands=['abiturient'])
def abiturient_menu(message):
    # user = util.get_user_by_id(message.from_user.id)
    # if гы
    bot.send_message(message.from_user.id, 'Вы абитуриент', reply_markup=markups_conf.abiturient_menu())

@bot.message_handler(commands=['student'])
def student_menu(message):
    bot.send_message(message.from_user.id, 'Вы студент')


@bot.message_handler(content_types=['text'])
def start_to_do(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    if message.text == '🗺️ Карта зданий':
        bot.send_message(message.from_user.id, 'Куда тебе нужно? ', reply_markup=markups_conf.map_menu())
    elif message.text == '🎓 Факультеты':
        msg = bot.send_message(message.from_user.id, 'Выбери факультет ⤵', reply_markup=markups_conf.facult_menu())
        # bot.register_next_step_handler(msg, facult)
    elif message.text == '🏨 Общежития':
        msg = bot.send_message(message.from_user.id, 'Выбери номер корпуса ⤵',
                               reply_markup=markups_conf.dpi_building())
        bot.register_next_step_handler(msg, get_location)
    elif message.text == '🏢 Учебные копруса':
        msg = bot.send_message(message.from_user.id, 'Выбери номер общежития ⤵',
                               reply_markup=markups_conf.hostel_building())
        bot.register_next_step_handler(msg, get_location)
    elif message.text == '☎ Наши контакты':
        bot.send_message(message.from_user.id, text_conf.contact_me, disable_web_page_preview=True)
    elif message.text == '⁉ Задать вопрос':
        user_markup.row('Отмена')
        msg = bot.send_message(message.from_user.id, "Введите ваш вопрос одним сообщением... ⤵"
                               , reply_markup=user_markup)
        bot.register_next_step_handler(msg, feedback)
    # Обратная связь ответ в чате
    elif str(message.chat.id) == config.chat_feedback_id:
        bot.send_message(config.chat_feedback_id, '{}, 👻 спасибо за помощь'.format(message.from_user.username))
        data_message = util.repeat_message(message.reply_to_message.text)
        if data_message:
            id_user = data_message['id_user']
            text_user = data_message['msg_text']
            bot.send_message(id_user, "Ваше обращение: " + "\"" + text_user + "\"" + "\n\n" + message.text)
            util.delete_message(id_user, text_user)
        else:
            bot.send_message(config.chat_feedback_id, 'Сообщение выбрано неверно')
    elif message.text == '🏠 Назад' or message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Вы вернулись в главное меню.', reply_markup=markups_conf.main_menu())
    elif message.text == '👽 FAQ':
        bot.send_message(message.chat.id, text_conf.faq)
    else:
        bot.send_message(message.chat.id, 'Команда не распознана', reply_markup=markups_conf.main_menu())
    # print(message.chat.id)


def get_location(message):
    if message.text == '🏠 Назад' or message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Вы вернулись в главное меню.', reply_markup=markups_conf.map_menu())
        return
    data = util.get_location(message.text)
    if data:
        bot.send_message(message.chat.id, message.text)
        bot.send_location(message.chat.id, data['x'], data['y'])
        txt = '<code>📮 ' + data['address'] + '</code>\n<a href="http://donntu.org/map-donntu"> Карта всех зданий</a>'
        msg = bot.send_message(message.chat.id, txt, parse_mode='HTML', disable_web_page_preview=True)
        bot.register_next_step_handler(msg, get_location)
    else:
        bot.send_message(message.chat.id, 'Выберите здание из списка', parse_mode='HTML', disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith(inline_conf.facult))
def action_callback(call):
    if call.data[len(inline_conf.facult):] == 'back':
        bot.edit_message_text('Выберите Факультет', call.from_user.id,
                              call.message.message_id, reply_markup=markups_conf.facult_menu())
        return

    id_facult = call.data[len(inline_conf.facult):]
    HISTORY[call.from_user.id] = {}
    HISTORY[call.from_user.id]['id_facult'] = id_facult
    inline_key = telebot.types.InlineKeyboardMarkup()

    bot.edit_message_text('Описание факультета небольшое', call.from_user.id, call.message.message_id,
                          reply_markup=markups_conf.special_menu(id_facult))


@bot.callback_query_handler(func=lambda call: call.data.startswith(inline_conf.special))
def special_call(call):
    if call.data[len(inline_conf.special):] == 'back':
        id_facult = HISTORY[call.from_user.id]['id_facult']
        bot.edit_message_text('Выберите специальность ⤵', call.from_user.id,
                              call.message.message_id, reply_markup=markups_conf.special_menu(id_facult))
        return
    id_special = call.data[len(inline_conf.special):]
    data_special = util.get_special_by_id(id_special)
    # кнопка возврата домой
    inline_key = telebot.types.InlineKeyboardMarkup()
    back_btn = telebot.types.InlineKeyboardButton(text='Назад',
                                                  callback_data=inline_conf.special + 'back')
    inline_key.add(back_btn)
    text = 'Направление: {}\n' \
           '{}'.format(data_special['code'] + ' ' + data_special['name'], data_special['description'])
    bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=inline_key)


def facult(message):
    if message.text == '🏠 Назад':
        bot.send_message(message.chat.id, 'Вы вернулись в главное меню.', reply_markup=markups_conf.main_menu())
    else:
        sql = util.get_all_facult()
        if sql:
            pass
        else:
            bot.send_message(message.from_user.id, 'Факультеты отсутсуют', reply_markup=markups_conf.facult_menu())
        # bot.send_message(message.from_user.id, 'Dыбор факультета', reply_markup=markups_conf.facult_menu())


def feedback(message):
    if message.chat.id != config.chat_feedback_id:
        if message.text == 'Отмена':
            bot.send_message(message.from_user.id, 'Вы вернулись в главное меню.',
                             reply_markup=markups_conf.main_menu())
        else:
            util.add_message(message.from_user.id, message.message_id, message.text, )
            bot.send_message(message.from_user.id, "Спасибо за обращение, мы постараемся ответить как можно скорее. "
                                                   "\nХорошего дня :)", reply_markup=markups_conf.main_menu())
            bot.send_message(config.chat_feedback_id, "!!! Новое обращение !!!")
            bot.forward_message(config.chat_feedback_id, message.from_user.id, message.message_id)


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling()
