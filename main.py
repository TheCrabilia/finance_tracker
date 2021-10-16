"""Finance Tracker main module."""

import os

import telebot

from db import Database, Password, InsertQuery
from db.query import SimpleSelectQuery

import utils
import exceptions


TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

bot = telebot.TeleBot(TOKEN, parse_mode="markdown")
db = Database(
    host="k3s-node-01.home.lab",
    port=30001,
    dbname="postgres",
    user="postgres",
    password=Password(os.getenv("DB_PASS")),
)


@bot.message_handler(commands=["start"])
def send_welcome(message: telebot.types.Message):
    bot.send_message(
        message.chat.id,
        f"Welcome to Finance Tracking Telegram bot!\nYour chat id = {message.chat.id}",
    )


# @bot.message_handler(commands=["add"])
# def add_expense(message):
#     try:
#         tokens = message.text.split()
#         if len(tokens) < 2:
#             raise exceptions.IncorrectArgumentCount
#         payload = {"cat_id": 1, "cat_description": ""}
#         for index, token in enumerate(tokens):
#             if index == 0:
#                 continue
#             elif index == 1:
#                 payload["amount"] = float(token)
#             elif index == 2:
#                 known_categories = db.fetchall("expense_categories")
#                 for known_category in known_categories:
#                     if token.upper() == known_category[1].upper():
#                         payload["cat_id"] = known_category[0]
#                         break
#             else:
#                 payload["cat_description"] = " ".join(tokens[index:])
#                 break
#     except Exception:
#         bot.send_message(
#             message.chat.id,
#             "Incorrect parameters specified!\nUsage: /add <amount> <categorie> <description>",
#         )
#     else:
#         db.insert("expenses", payload)
#         bot.send_message(message.chat.id, f"Added {payload['amount']} EUR")

@bot.message_handler(commands=["add"])
def add_expense(message: telebot.types.Message):
    tokens = message.text.split()

    for record in db.execute(SimpleSelectQuery("expense_categories")):
        cat_id = 1
        if tokens[2] in record[1]:
            cat_id = record[0]
            break

    query = InsertQuery("expenses", {"amount": tokens[1], "cat_id": cat_id, "cat_description": " ".join(tokens[3:])})
    db.execute(query)


@bot.message_handler(commands=["add-cat"])
def add_expense_category(message: telebot.types.Message):
    ...


@bot.message_handler(commands=["top"])
def show_top_expenses(message: telebot.types.Message):
    ...


@bot.message_handler(commands=["latest"])
def show_latest_expenses(message: telebot.types.Message):
    try:
        limit = int(message.text.split()[1])
    except:
        limit = 5
    finally:
        query = db.get_latest("expenses", limit)
        table = utils.generate_table(headers=("Amount", "Category"), content=query)
        bot.send_message(message.chat.id, table)


@bot.message_handler(commands=["day", "month", "year"])
def show_interval_expenses(message: telebot.types.Message):
    interval = message.text.lstrip("/")
    query = db.get_inverval(
        "expenses as t", interval, "t.creation_timestamp::date, t.amount, jt.cat_name"
    )
    table = utils.generate_table(headers=("Date", "Amount", "Category"), content=query)
    bot.send_message(message.chat.id, table)


@bot.message_handler(commands=["cat"])
def show_categories(message: telebot.types.Message):
    query = db.fetchall("expense_categories", "cat_name")
    table = utils.generate_table(headers=("Categories",), content=query)
    bot.send_message(message.chat.id, table)


bot.polling()
