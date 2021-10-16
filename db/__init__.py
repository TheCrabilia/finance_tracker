"""Database main module."""

from dataclasses import dataclass
from base64 import b64encode, b64decode

from psycopg import connect, Connection
from psycopg.cursor import Cursor

from db.query import DeleteQuery, Query, InsertQuery


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


@dataclass
class Database:
    """This class implements the interface to interact with SQL database."""

    host: str
    password: Password
    port: int = 5432
    dbname: str = "postgres"
    user: str = "postgres"

    def __post_init__(self):
        self.connection: Connection = self.connect()
        self.cursor: Cursor = self.connection.cursor()

    def connect(self) -> Connection:
        """This method is used to connect to database. Returns the object of Connection type."""
        return connect(
            f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password.decode()}"
        )

    def disconnect(self) -> None:
        """This method is used to disconnect from database."""
        self.connection.close()

    def execute(self, query: Query) -> list | None:
        """This method can be used to get data from database."""
        match query:
            case InsertQuery():
                self.cursor.execute(query.get(), query.values)
                self.connection.commit()
                return None
            case DeleteQuery():
                self.cursor.execute(query.get())
                self.connection.commit()
                return None
            case _:
                self.cursor.execute(query.get())
                return self.cursor.fetchall()
