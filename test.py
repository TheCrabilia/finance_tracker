"""Database module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from base64 import b64encode, b64decode

from psycopg import connect, Connection


@dataclass
class Password:
    """This class is used to store password."""

    password: str

    def __post_init__(self) -> None:
        self.password = self.encode()

    def __str__(self) -> str:
        return self.password

    def encode(self) -> str:
        """Encodes password."""
        b64encoded = b64encode(self.password.encode("utf-8"))
        return b64encoded.decode("utf-8")

    def decode(self) -> str:
        """Decodes password."""
        b64decoded = b64decode(self.password.encode("utf-8"))
        return b64decoded.decode("utf-8")


class Query(ABC):
    """Class to store SQL Query data."""

    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass
class SimpleSelectQuery(Query):
    """This class implemets simple select query."""

    table: str
    columns: list = None

    def __post_init__(self) -> None:
        self.query = f"SELECT {self.get_columns()} FROM {self.table}"

    def __str__(self) -> str:
        return self.query

    def get_columns(self):
        """Method is used to get columns. Returns '*', if self.columns is None."""
        if self.columns is None:
            return "*"
        return ", ".join(self.columns)


@dataclass
class JoinSelectQuery(Query):
    """This class implements select query with join statement."""

    table: str
    columns: list = None

    def __post_init__(self):
        self.query = f"SELECT * FROM tables "  # TODO end with join select query


@dataclass
class Database:
    """This class implements the interface to interact with SQL database."""

    host: str
    password: Password
    port: int = 5432
    dbname: str = "postgres"
    user: str = "postgres"

    def __post_init__(self):
        self.connection = self.connect()
        self.cursor = self.connection.cursor()

    def connect(self) -> Connection:
        """This method is used to connect to database. Returns the object of Connection type."""
        return connect(
            f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password.decode()}"
        )

    def disconnect(self) -> None:
        """This method is used to disconnect from database."""
        self.connection.close()

    def execute(self, query: Query) -> list:
        """This method executes the SQL query."""
        self.cursor.execute(query.__str__())
        return self.cursor.fetchall()


database = Database(
    host="k3s-node-01.home.lab",
    port=30001,
    password=Password("123"),
)

q = SimpleSelectQuery("expense_categories", ["id", "cat_name"])
print(q)
print(database.execute(q))
