import sqlite3


class Database:
    def __init__(self, path: str):
        self.path = path

    def create_tables(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS review_results
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact_info VARCHAR(100),
            food_rating INTEGER,
            cleanliness_rating INTEGER,
            extra_comments VARCHAR(300)
            )
            """)
        conn.commit()

    def save_review_results(self, data: dict):
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT INTO review_results
                (name, contact_info,
                food_rating, 
                cleanliness_rating,
                extra_comments) 
                VALUES (?, ?, ?, ?, ?)""",
                (data['name'],
                 data['contact_info'],
                 data['food_rating'],
                 data['cleanliness_rating'],
                 data['extra_comments'])
            )
