"""Database query module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class Sorting(Enum):
    """Sorting order Enum class."""

    ASCE = ""
    DESC = "DESC"


@dataclass
class Order:
    """This class implements query ordering."""

    column: str = None
    sort_order: Sorting = Sorting.ASCE

    def get(self) -> str:
        """Returns SQL ORDER BY statement."""
        if self.column is None:
            return ""
        return f"ORDER BY {self.column} {self.sort_order.value}"


@dataclass
class Where:
    """This class implements SQL WHERE statement."""

    expression: str = None

    def get(self) -> str:
        """Returns SQL WHERE statement."""
        if self.expression is None:
            return ""
        return f"WHERE {self.expression}"


@dataclass
class Limit:
    """This class implements SQL LIMIT statement."""

    limit: int | str = None

    def get(self) -> str:
        """Returns SQL LIMIT statement."""
        if self.limit is None:
            return ""
        return f"LIMIT {self.limit}"


class Query(ABC):
    """Class to store SQL Query data."""

    @abstractmethod
    def get(self) -> str:
        """This method returns a SQL query string."""


@dataclass
class SimpleSelectQuery(Query):
    """This class implemets simple select query."""

    table: str
    columns: tuple[str] = None
    limit: Limit = Limit()
    order: Order = Order()
    where: Where = Where()

    def get(self) -> str:
        return f"SELECT {self.get_columns()} FROM {self.table} {self.where.get()} {self.order.get()} {self.limit.get()}"

    def get_columns(self):
        """Method is used to get columns. Returns '*', if self.columns is None."""
        if self.columns is None:
            return "*"
        return ", ".join(self.columns)


@dataclass
class JoinSelectQuery(Query):
    """
    This class implements select query with join statement.
    If columns variable is None (not specified), the default value ('*') is used instead.
    """

    tables: tuple[dict[str, str]]
    equation: str
    columns: tuple[str] = None
    limit: Limit = Limit()
    order: Order = Order()
    where: Where = Where()

    def get(self) -> str:
        return f"SELECT {self.get_columns()} FROM {self.tables[0]['name']} AS {self.tables[0]['alias']} JOIN {self.tables[1]['name']} AS {self.tables[1]['alias']} ON {self.equation} {self.where.get()} {self.order.get()} {self.limit.get()}"

    def get_columns(self) -> str:
        """
        Is used to construct the SQL query column section.
        Returns '*', if self.columns is None.
        """
        if self.columns is None:
            return "*"
        return ", ".join(self.columns)


@dataclass
class InsertQuery(Query):
    """This class implements insert query."""

    table: str
    column_values: dict

    def __post_init__(self):
        self.columns = ", ".join(self.column_values.keys())
        self.values = list(self.column_values.values())

    def get(self) -> str:
        placeholders = ", ".join("%s" for _ in range(
            len(self.column_values.keys())))
        return f"INSERT INTO {self.table} ({self.columns}) VALUES ({placeholders})"


@dataclass
class DeleteQuery(Query):
    """This class implements delete query."""

    table: str
    where: Where

    def get(self) -> str:
        return f"DELETE FROM {self.table} {self.where.get()}"
