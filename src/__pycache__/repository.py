import sqlite3
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Triangle:
    # Sides
    side_a: float
    side_b: float
    side_c: float
    
    coord_a: Tuple[int, int]
    coord_b: Tuple[int, int]
    coord_c: Tuple[int, int]
    
    triangle_type: str
    error_message: Optional[str] = None

    id: Optional[int] = None


class TriangleRepository:

    def __init__(self, db_path: str = ":database:"):
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        """Creates the triangles table if it does not exist."""
        query = """
        CREATE TABLE IF NOT EXISTS triangles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            side_a REAL NOT NULL,
            side_b REAL NOT NULL,
            side_c REAL NOT NULL,
            coord_a_x INTEGER NOT NULL,
            coord_a_y INTEGER NOT NULL,
            coord_b_x INTEGER NOT NULL,
            coord_b_y INTEGER NOT NULL,
            coord_c_x INTEGER NOT NULL,
            coord_c_y INTEGER NOT NULL,
            triangle_type TEXT NOT NULL,
            error_message TEXT
        );
        """
        with self._get_connection() as conn:
            conn.execute(query)

    def add_triangle(self, triangle: Triangle) -> int:
        query = """
        INSERT INTO triangles (
            side_a, side_b, side_c, 
            coord_a_x, coord_a_y, 
            coord_b_x, coord_b_y, 
            coord_c_x, coord_c_y, 
            triangle_type, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            triangle.side_a,
            triangle.side_b,
            triangle.side_c,
            triangle.coord_a[0],
            triangle.coord_a[1],
            triangle.coord_b[0],
            triangle.coord_b[1],
            triangle.coord_c[0],
            triangle.coord_c[1],
            triangle.triangle_type,
            triangle.error_message,
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            triangle.id = cursor.lastrowid
            return triangle.id

    def delete_by_sides(self, side_a: float, side_b: float, side_c: float) -> bool:
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
        self, side_a: float, side_b: float, side_c: float
    ) -> Optional[Triangle]:
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

