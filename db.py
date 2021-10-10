from typing import Any
import psycopg

DB_CREDS = "host=k3s-node-01.home.lab port=30001 dbname=postgres user=postgres password=123"

conn = psycopg.connect(DB_CREDS)
cursor = conn.cursor()


def insert(table: str, column_values: dict) -> None:
    columns = ", ".join(column_values.keys())
    values = list(column_values.values())
    placeholders = ", ".join("%s" for _ in range(len(column_values.keys())))
    cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
    conn.commit()


def delete(table: str, filter: str) -> None:
    cursor.execute(f"DELETE FROM {table} WHERE {filter}")
    

def get_latest(table: str, limit: int) -> list[tuple[Any]]:
    cursor.execute(f"SELECT t.amount, jt.cat_name FROM {table} AS t JOIN expense_categories as jt ON t.cat_id=jt.id ORDER BY creation_timestamp DESC LIMIT {limit}")
    return cursor.fetchall()


def get_top(table: str) -> list[tuple[Any]]:
    ...


def fetchall(table: str, columns: str = "*", _filter: str = "id>0") -> list[tuple[Any]]:
    cursor.execute(f"SELECT {columns} FROM {table} WHERE {_filter}")
    return cursor.fetchall()


def get_inverval(table: str, interval: str, columns: str = "*"):
    cursor.execute(f"SELECT {columns} FROM {table} JOIN expense_categories jt ON t.cat_id=jt.id WHERE creation_timestamp > now() - '1 {interval}'::interval")
    return cursor.fetchall()
