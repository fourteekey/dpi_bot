import re
import time

import pymysql.cursors
import telebot

import datetime
import cherrypy
import json

from telebot import apihelper
from telebot import types
from datetime import date, timedelta

import config

paramstyle = "%s"


def connect():
    return pymysql.connect(
        config.db_host,
        config.db_user,
        config.db_password,
        config.db_database,
        use_unicode=True,
        charset=config.db_charset,
        cursorclass=pymysql.cursors.DictCursor)


def execute(sql, *args, commit=False):
    """
     Формат запроса:
     execute('<Запрос>', <передаваемые параметры>, <commit=True>)
    """
    db = connect()
    cur = db.cursor()
    try:
        cur.execute(sql % {"p": paramstyle}, args)
    except pymysql.err.InternalError as e:
        if sql.find('texts') == -1:
            print('Cannot execute mysql request: ' + str(e))
        return
    if commit:
        db.commit()
        db.close()
    else:
        ans = cur.fetchall()
        db.close()
        return ans


def get_user_by_id(id_user):
    return execute('SELECT * FROM users WHERE id=%(p)s', id_user)


def welcome_user(id_user):
    execute('INSERT INTO users(id, status) VALUES(%(p)s, 0)', id_user, commit=True)


def repeat_message(text):
    sql = execute('SELECT * FROM user_message WHERE msg_text=%(p)s', text)
    if sql:
        return sql[0]

def add_message(id_user, id_message, text):
    execute('INSERT INTO user_message(id_user, id_msg, msg_text) VALUES(%(p)s, %(p)s, %(p)s)',
            id_user, id_message, text, commit=True)

def delete_message(id_user, text):
    execute('DELETE * FROM user_message WHERE id_user=%(p)s, msg_text=%(p)s', id_user, text, commit=True)

def get_location(name_build):
    sql = execute('SELECT * FROM bulding_coordinates WHERE name_building=%(p)s', name_build)
    if sql:
        return sql[0]
    else:
        return False

def get_all_facult():
    return execute('SELECT * FROM facultets')

def get_all_special_by_id_facultet(id_facultet):
   return execute('SELECT sp.*, cf.name as cafedra_name, cf.* '
                  'FROM special sp LEFT JOIN cafedra cf ON sp.id_cafedra=cf.id WHERE id_facultet=%(p)s', id_facultet)

def get_special_by_id(id_special):
    sql = execute('SELECT sp.*, cf.name as cafedra_name, cf.*, fc.id as id_facultet, fc.* '
                  'FROM special sp '
                  'LEFT JOIN cafedra cf ON sp.id_cafedra=cf.id '
                  'LEFT JOIN facultets fc ON cf.id_facultet=fc.id '
                  'WHERE sp.id=%(p)s', id_special)
    print(sql)
    if sql:
        return sql[0]
