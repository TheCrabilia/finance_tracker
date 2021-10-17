"""Utilities module. Contains useful classes and functions."""

import random as rand
import string
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from db import Database
from db.query import SimpleSelectQuery


@dataclass
class Table:
    """This class implements Table object."""

    headers: tuple
    content: list

    def get_file(self, path: Path = Path("./tmp")) -> BinaryIO:
        """This method can be used to get table as a file.

        Args:
            path (Path, optional): Directory path, where to save table file. Defaults to "./tmp".

        Returns:
            BinaryIO: Open file object in rb mode.
        """
        table = "`" + self.__gen_table() + "`"
        fname = self.__gen_name()

        # Create directory, ignore error, if it already exists
        path.mkdir(exist_ok=True)
        with open(Path(path, fname), "w", encoding="utf-8") as tfile:
            tfile.write(table)
        return open(Path(path, fname), "rb")

    def get_text(self) -> str:
        """This method can be used to get table text representation.

        Returns:
            str: Table as a single string with \\n characters for the new line.
        """
        table = "`" + self.__gen_table() + "`"
        return table

    def __gen_table(self) -> str:
        data = convert_to_strings([self.headers] + self.content)
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
        return table

    @staticmethod
    def __gen_name() -> str:
        return (
            "".join([rand.choice(string.ascii_lowercase) for _ in range(20)]) + ".md"
        )


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


def has_duplicates(current: list[tuple[str]], to_find: str):
    for i in current:
        if to_find == i[0]:
            return True
    return False
    