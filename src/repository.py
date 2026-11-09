import sqlite3
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class comment:
    #username
    name: str
    
    message: str

    id: Optional[int] = None


class DatabaseRepository:

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
            message TEXT NOT NULL,
        );
        """
        with self._get_connection() as conn:
            conn.execute(query)

    def add(self, comment_id: int, username: str, message: str) -> bool:

        try:
            id = int(comment_id)
        except (ValueError, TypeError):
            raise Exception("Not an int ID")

        if (id < 0):
            raise Exception("Negative ID")

        if (username == None or username.length < 1):
            raise Exception("Empty username")

        if (username == None or username.length < 1):
            raise Exception("Empty username")
        
        query = """
            INSERT INTO comments (
                id, name, message
            ) VALUES (?, ?, ?);
        """
        params = (
            comment_id,
            username,
            message
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
        
    def get_by_id(comment_id: int, username:str, nessage:str) -> Optional[Triangle]:
        query = "SELECT * FROM triangles WHERE side_a = ? AND side_b = ? AND side_c = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (side_a, side_b, side_c))
            row = cursor.fetchone()

            if not row:
                return None

            return Triangle(
                id=row["id"],
                side_a=row["side_a"],
                side_b=row["side_b"],
                side_c=row["side_c"],
                coord_a=(row["coord_a_x"], row["coord_a_y"]),
                coord_b=(row["coord_b_x"], row["coord_b_y"]),
                coord_c=(row["coord_c_x"], row["coord_c_y"]),
                triangle_type=row["triangle_type"],
                error_message=row["error_message"],
            )


    def delete_by_sides(self, side_a: str, side_b: str, side_c: str) -> bool:
        query = """
        DELETE FROM triangles 
        WHERE id = (
            SELECT id FROM triangles 
            WHERE side_a = ? AND side_b = ? AND side_c = ? 
            LIMIT 1
        );
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (side_a, side_b, side_c))
            conn.commit()
            return cursor.rowcount > 0
    
    def fetch_by_sides(
        self, side_a: str, side_b: str, side_c: str
    ) -> Optional[Triangle]:
        query = "SELECT * FROM triangles WHERE side_a = ? AND side_b = ? AND side_c = ?"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (side_a, side_b, side_c))
            row = cursor.fetchone()

            if not row:
                return None

            return Triangle(
                id=row["id"],
                side_a=row["side_a"],
                side_b=row["side_b"],
                side_c=row["side_c"],
                coord_a=(row["coord_a_x"], row["coord_a_y"]),
                coord_b=(row["coord_b_x"], row["coord_b_y"]),
                coord_c=(row["coord_c_x"], row["coord_c_y"]),
                triangle_type=row["triangle_type"],
                error_message=row["error_message"],
            )