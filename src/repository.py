import sqlite3
from typing import Optional
from src.logger import logger
import textwrap
from src.comment import Comment
from abc import ABC, abstractmethod

class DBRInterface(ABC):
    @abstractmethod
    def add(comment_id: int, username: str, message: str) -> bool:
        pass

    @abstractmethod
    def get_by_id(comment_id: int) -> Optional[Comment]:
        pass

    @abstractmethod
    def get_by_name(username: str) -> Optional[Comment]:
        pass

    @abstractmethod
    def update(self, comment_id: int, new_message: str) -> bool:
        pass

class DatabaseRepository(DBRInterface):

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _get_connection(self):
        return self._conn

    def _create_table(self):
        """Creates the comments table if it does not exist."""
        query = """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            message TEXT NOT NULL
        );
        """
        logger.info("db set up, comments table created")
        with self._get_connection() as conn:
            conn.execute(query)

    def add(self, comment_id: int, username: str, message: str) -> bool:

        try:
            id = int(comment_id)
        except (ValueError, TypeError):
            raise Exception("Not an int ID")

        if (id < 0):
            raise Exception("Negative ID")

        if (username == None or len(username.strip()) < 1):
            raise Exception("Empty username")

        if (message == None or len(message.strip()) < 1):
            raise Exception("Empty message")
        
        query = """
            INSERT INTO comments (
                id, name, message
            ) VALUES (?, ?, ?);
        """
        params = (
            comment_id,
            username.strip(),
            message.strip()
        )
        logger.info(f"adding comment {id} by {username.strip()}: {textwrap.shorten(message.strip(), width=20, placeholder="...")}")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
        
    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        try:
            id = int(comment_id)
        except (ValueError, TypeError):
            logger.exception(f"db error on lookup id {comment_id} is not an int")
            raise Exception("Not an int ID")
        query = "SELECT * FROM comments WHERE id = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id,))
            row = cursor.fetchone()

            if not row:
                logger.info(f"db could not find id {id}")
                return None

            return Comment(
                id=row["id"],
                name=row["name"],
                message=row["message"],
            )

    def get_by_name(self, username: str) -> Optional[Comment]:
        query = "SELECT * FROM comments WHERE name = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, username)
            row = cursor.fetchone()

            if not row:
                logger.info(f"db could not find name {username}")
                return None

            return Comment(
                id=row["id"],
                name=row["name"],
                message=row["message"],
            )

    def update(self, comment_id: int, new_message: str) -> bool:

        try:
            id = int(comment_id)
        except (ValueError, TypeError):
            logger.exception(f"db error on updating id={id}, new_message={new_message}")
            raise Exception("Not an int ID")

        if (id < 0):
            raise Exception("Negative ID")

        if (new_message == None or len(new_message.strip()) < 1):
            raise Exception("Empty message")
        
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE comments SET message = ? WHERE id = ?",
                (new_message.strip(), comment_id),
            )
        conn.commit()
        logger.info(f"db commit, updating id={id}, new_message={new_message}")

        return cursor.rowcount > 0