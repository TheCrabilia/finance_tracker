"""Finance Tracker main module."""

import os

import telebot

import utils
from db import Database, InsertQuery, Password
from db.query import (DeleteQuery, JoinSelectQuery, Limit, Order,
                      SimpleSelectQuery, Sorting, Where)
from utils import Table

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

    # Try to convert amount (1 element of token list) from string to float number
    try:
        tokens[1] = float(tokens[1])
    except ValueError:
        pass

    match tokens:
        case ["/add", float(amount)]:
            query = InsertQuery("expenses", {"amount": amount})
        case ["/add", float(amount), category]:
            query = InsertQuery(
                "expenses", {"amount": amount, "cat_id": utils.get_category_id(db, category)})
        case ["/add", float(amount), category, *description]:
            query = InsertQuery("expenses", {"amount": amount, "cat_id": utils.get_category_id(
                db, category), "cat_description": " ".join(description)})
        case _:
            bot.send_message(
                message.chat.id, "Incorrect parameters specified!\nUsage: /add <amount> <category> <description>")
            return

    db.execute(query)
    bot.send_message(message.chat.id, f"Added {amount} EUR")


@bot.message_handler(commands=["exp"])
def expenses(message: telebot.types.Message):
    """
    Handles /exp command and all sub-commnads related to it.
    """
    tokens = message.text.split()

    match tokens:
        case ["/exp", "latest", *ulimit]:
            # Set limit variable to user specified variable.
            # If ulimit is not specified, set to default value - 5.
            limit = ulimit[0] if ulimit else 5
            query = JoinSelectQuery(
                tables=(
                    {"name": "expenses", "alias": "e"},
                    {"name": "expense_categories", "alias": "ec"},
                ),
                columns=("e.amount", "ec.cat_name", "e.cat_description",),
                equation="e.cat_id=ec.id",
                order=Order("creation_timestamp", Sorting.DESC),
                limit=Limit(limit)
            )
            data = db.execute(query)
            table = utils.generate_table(
                headers=("Amount (EUR)", "Category", "Description"), content=data)
            bot.send_message(message.chat.id, table)
        case ["/exp", "top"]:
            query = JoinSelectQuery(
                tables=(
                    {"name": "expenses", "alias": "e"},
                    {"name": "expense_categories", "alias": "ec"},
                ),
                columns=("e.amount", "ec.cat_name", "e.cat_description",),
                equation="e.cat_id=ec.id",
                order=Order("amount", Sorting.DESC),
                limit=Limit(10)
            )
            data = db.execute(query)
            # table = utils.generate_table(
            #     headers=("Amount (EUR)", "Category", "Description"), content=data)
            table = Table(headers=("Amount (EUR)", "Category", "Description"), content=data)
            bot.send_message(message.chat.id, table.get_text())
        case ["/exp", "help"] | _:
            bot.send_message(message.chat.id, """
`/exp sub-command [arguments]

Accepted arguments:
/exp help           - Show command help
/exp latest <limit> - List latest expenses
/exp top            - List top 10 of biggest expenses
            `""")


@bot.message_handler(commands=["day", "month", "year"])
def show_interval_expenses(message: telebot.types.Message):
    """
    Handles /day, /month and /year commands.
    Responsible for generating daily, monthly or yearly expense report.
    """
    interval = message.text.lstrip("/").split()[0]
    query = JoinSelectQuery(
        tables=({"name": "expenses", "alias": "e"}, {
                "name": "expense_categories", "alias": "ec"}),
        columns=("e.creation_timestamp::date", "e.amount", "ec.cat_name"),
        equation="e.cat_id=ec.id",
        where=Where(f"creation_timestamp > now() - '1 {interval}'::interval"),
        order=Order("creation_timestamp", Sorting.DESC)
    )
    data = db.execute(query)
    table = utils.generate_table(
        headers=("Date", "Amount (EUR)", "Category"), content=data)
    bot.send_message(message.chat.id, table)


@bot.message_handler(commands=["cat"])
def categories(message: telebot.types.Message):
    """Handles /cat command. Shows all known expense categories."""
    tokens = message.text.split()

    match tokens:
        case ["/cat", "add", name]:
            current_categories: list[tuple] = db.execute(SimpleSelectQuery("expense_categories", ("cat_name",)))
            if utils.has_duplicates(current_categories, name):
                bot.send_message(message.chat.id, f"Category {name} already exists!")
                return
            db.execute(InsertQuery("expense_categories", {"cat_name": name}))
            bot.send_message(message.chat.id, f"Category {name} added")
        case ["/cat", "del", name]:
            db.execute(DeleteQuery("expense_categories",
                       Where(f"UPPER(cat_name)='{name.upper()}'")))
            bot.send_message(message.chat.id, f"Category {name} deleted")
        case ["/cat", "list"] | ["/cat"]:
            cats = db.execute(SimpleSelectQuery(
                "expense_categories", ("cat_name",),
                where=Where("id != 1"),
                order=Order("cat_name")
            ))
            table = utils.generate_table(headers=("Categories",), content=cats)
            bot.send_message(message.chat.id, table)
        case ["/cat", "help"] | _:
            bot.send_message(message.chat.id, """
`/cat [sub-command] [arguments]

Accepted arguments:
/cat help       - Show command help
/cat list       - Show known expense category list
/cat add <name> - Add new expense category
/cat del <name> - Delete expense category`
            """)


bot.polling()
