from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.intra import Node
    from ..enums import DB_NAME
    from mssql_python import Cursor
    from ..cli import CLI

from mssql_python import connect, Error as SQLERROR, OperationalError
import sqlite3
from ..errors.db import DBConnectionError


class SQLConnectionManager:
    def __init__(self, cli: CLI):
        self._cli = cli
        self.connection = None

    def connect(self, node: Node, db_name: DB_NAME):
        db_name = getattr(node, db_name)
        if db_name is None or not db_name:
            raise ValueError(f"{node.name} is missing the db name for {db_name}.")
        SQL_CONNECTION_STRING = f"Server={node.db_server};Database={db_name};UID={node.db_user_name};PWD={node.db_password};Encrypt=yes;TrustServerCertificate=yes"

        try:
            if self.connection is not None:
                msg = f"{self.__class__.__name__} is already connected."
                raise RuntimeError(msg)
            self.connection = connect(SQL_CONNECTION_STRING)
        except OperationalError as e:
            if "Client unable to establish connection" in str(e):
                message = f"Could not connect to SQL Server for {node.name}. If you're off-network, check your VPN connection."
                self._cli.print_error(message)
                raise DBConnectionError(message) from e

            else:
                self._cli.print_error(
                    f"{self.__class__.__name__}: Operational Error - {e}"
                )
                raise
        except Exception as e:
            print(e)
            raise

    def execute_query(self, query, params=None) -> Cursor:
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
        except Exception as e:
            self._cli.print_error(f"{self.__class__.__name__}: Error {e}")
            self.clean_up_cursor(cursor)
            raise
        return cursor

    def clean_up_cursor(self, cursor: Cursor) -> None:
        if cursor:
            cursor.close()

    def disconnect(self):
        """
        Close the connection to the SQLite database.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def fetch_all(self, query, params=None):
        """
        Execute a query and return all results.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters to use in the query.
        :return: A list of rows from the result set.
        """
        # print("fetch_all", query, params)
        cursor = self.execute_query(query, params)
        try:

            return cursor.fetchall() if cursor else []
        finally:
            self.clean_up_cursor(cursor)

    def fetch_one(self, query, params=None):
        """
        Execute a query and return a single result.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters to use in the query.
        :return: A single row from the result set.
        """
        cursor = self.execute_query(query, params)
        try:
            return cursor.fetchone() if cursor else None
        finally:
            self.clean_up_cursor(cursor)
