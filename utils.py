from db import Database
from db.query import SimpleSelectQuery


def generate_table(headers: tuple, content: list) -> str:
    data = convert_to_strings([headers] + content)
    longest = get_longest_lenght(data)
    table = ""
    for i, _ in enumerate(data):
        for j, column in enumerate(data[i]):
            table += "| " + column + " " * (longest[j] - len(column) + 1)
        table += "|\n"
        if i == 0:
            for j, column in enumerate(data[i]):
                table += "|" + "-" * (longest[j] + 2)
            table += "|\n"
    table = "`" + table + "`"
    return table


def get_longest_lenght(content: list) -> list:
    maxes = []
    for i in zip(*content):
        maxes.append(max(i, key=len))
    return list(map(len, maxes))

    
def convert_to_strings(data: list) -> list:
    new_data = []
    for i in data:
        new_data += [tuple(map(str, i))]
    return new_data


def get_category_id(db: Database, category: str) -> str:
    all_categories = db.execute(SimpleSelectQuery("expense_categories"))
    for cat in all_categories:
        if category.upper() in cat[1].upper():
            return str(cat[0])
    return str(1)
