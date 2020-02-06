from telebot import types

import util
import inline_config as inline_conf

def main_menu():
    main_key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_key.row('🗺️ Карта зданий', '🎓 Факультеты')
    main_key.row('⁉ Задать вопрос', '☎ Наши контакты')
    main_key.row('👽 FAQ')

    return main_key


def map_menu():
    map_key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    map_key.row('🏨 Общежития', '🏢 Учебные копруса')
    map_key.row('🏠 Назад')

    return map_key


def dpi_building():
    map_dpi_key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    map_dpi_key.row('Общежитие 1', 'Общежитие 2', 'Общежитие 3')
    map_dpi_key.row('Общежитие 4', 'Общежитие 5', 'Общежитие 6')
    map_dpi_key.row('Общежитие 7', 'Общежитие 8', 'Общежитие 9')
    map_dpi_key.row('🏠 Назад')

    return map_dpi_key


def hostel_building():
    map_hostel_key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    map_hostel_key.row('Корпус 1', 'Корпус 2', 'Корпус 3', 'Корпус 4')
    map_hostel_key.row('Корпус 5', 'Корпус 6', 'Корпус 7', 'Корпус 8')
    map_hostel_key.row('Корпус 9', 'Корпус 10', 'Корпус 11')
    map_hostel_key.row('🏠 Назад')

    return map_hostel_key

# Меню для абитуриента
def abiturient_menu():
    pass


def facult_menu():
    inline_key = types.InlineKeyboardMarkup()
    facultets = util.get_all_facult()
    # print(facultets)
    for facult in facultets:
        inline_btn = types.InlineKeyboardButton(text=facult['short_name'] + ' - ' + facult['discription'],
                                                callback_data=inline_conf.facult + str(facult['id']))
        inline_key.add(inline_btn)

    return inline_key


def special_menu(id_facultet):
    inline_key = types.InlineKeyboardMarkup()
    specials = util.get_all_special_by_id_facultet(id_facultet)
    print('Specials: ', specials)
    for special in specials:
        inline_btn = types.InlineKeyboardButton(text=special['code'] + ' - ' + special['name'],
                                                callback_data=inline_conf.special + str(special['id']))
        inline_key.add(inline_btn)
    # кнопка возвращает назад на выбор факультетов
    back_btn = types.InlineKeyboardButton(text='Назад', callback_data=inline_conf.facult + 'back')
    inline_key.add(back_btn)

    return inline_key

def back():
    inline_key = types.InlineKeyboardMarkup()
    inline_btn = types.InlineKeyboardButton(text='Назад', callback_data='Назад')
    inline_key.add(inline_btn)

    return inline_key