"""Finance Tracker main module."""

import os

import telebot

from db import Database, Password, InsertQuery
from db.query import DeleteQuery, JoinSelectQuery, SimpleSelectQuery, Where

import utils


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


@bot.message_handler(commands=["add"])
def add_expense(message: telebot.types.Message):
    """Handles /add command. Adds new expenses to the database."""
    tokens = message.text.split()

    match tokens:
        case ["/add", amount]:
            query = InsertQuery("expenses", {"amount": amount})
        case ["/add", amount, category]:
            query = InsertQuery(
                "expenses", {"amount": amount, "cat_id": utils.get_category_id(db, category)})
        case ["/add", amount, category, *description]:
            query = InsertQuery("expenses", {"amount": amount, "cat_id": utils.get_category_id(
                db, category), "cat_description": " ".join(description)})
        case _:
            bot.send_message(
                message.chat.id, "Incorrect parameters specified!\nUsage: /add <amount> <categorie> <description>")
            return

    db.execute(query)
    bot.send_message(message.chat.id, f"Added {amount} EUR")


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
        table = utils.generate_table(
            headers=("Amount", "Category"), content=query)
        bot.send_message(message.chat.id, table)


@bot.message_handler(commands=["day", "month", "year"])
def show_interval_expenses(message: telebot.types.Message):
    """
    Handles /day, /month and /year commands.
    Responsible for generating daily, monthly or yearly expense report.
    """
    interval = message.text.lstrip("/")
    query = JoinSelectQuery(
        tables=({"name": "expenses", "alias": "e"}, {"name": "expense_categories", "alias": "ec"}),
        columns=("e.creation_timestamp::date", "e.amount", "ec.cat_name"),
        equation="e.cat_id=ec.id",
        where=Where(f"creation_timestamp > now() - '1 {interval}'::interval"))
    data = db.execute(query)
    table = utils.generate_table(headers=("Date", "Amount (EUR)", "Category"), content=data)
    bot.send_message(message.chat.id, table)


@bot.message_handler(commands=["cat"])
def categories(message: telebot.types.Message):
    """Handles /cat command. Shows all known expense categories."""
    tokens = message.text.split()

    match tokens:
        case ["/cat", "add", name]:
            db.execute(InsertQuery("expense_categories", {"cat_name": name}))
            bot.send_message(message.chat.id, f"Category {name} added")
        case ["/cat", "del", name]:
            db.execute(DeleteQuery("expense_categories",
                       Where(f"cat_name='{name}'")))
            bot.send_message(message.chat.id, f"Category {name} deleted")
        case ["/cat", "list"] | ["/cat"]:
            cats = db.execute(SimpleSelectQuery(
                "expense_categories", ("cat_name",), where=Where("id != 1")))
            table = utils.generate_table(headers=("Categories",), content=cats)
            bot.send_message(message.chat.id, table)
        case ["/cat", "help"] | _:
            bot.send_message(message.chat.id, """
`/cat [[sub-command]] [[arguments]]

Accepted arguments:
/cat help       - Show command help
/cat list       - Show known expense category list
/cat add <name> - Add new expense category
/cat del <name> - Delete expense category`
            """)


bot.polling()
