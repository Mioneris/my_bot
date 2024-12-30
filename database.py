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
            extra_comments VARCHAR(300),
            date Date,
            user_id INTEGER
            )
            """)
            conn.commit()

            conn.execute("""
                        CREATE TABLE IF NOT EXISTS dish_info
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        price FLOAT,
                        description VARCHAR(150),
                        category TEXT,
                        dish_picture TEXT,
                        FOREIGN KEY (category) REFERENCES dish_category(category_name)                     
                        )
                        """)
            conn.commit()

            conn.execute("""
                        CREATE TABLE IF NOT EXISTS dish_category
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category_name TEXT UNIQUE NOT NULL)""")
            conn.commit()

            conn.execute("""
                CREATE TABLE IF NOT EXISTS bot_database
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE ,
                warnings INTEGER DEFAULT 0)
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
                extra_comments,
                date,
                user_id
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data['name'],
                 data['contact_info'],
                 data['food_rating'],
                 data['cleanliness_rating'],
                 data['extra_comments'],
                 data['review_date'],
                 data['user_id'])
            )

    def insert_categories(self):
        default_categories = ["Супы",
                              "Вторые блюда",
                              "Горячие напитки",
                              "Холодные напитки"]
        with sqlite3.connect(self.path) as conn:
            for category in default_categories:
                try:
                    conn.execute('INSERT INTO dish_category (category_name) VALUES (?)', (category,))
                except sqlite3.IntegrityError:
                    continue
            conn.commit()

    def get_categories_dish_edit(self):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.execute('SELECT category_name FROM dish_category')
            return [row[0] for row in cursor.fetchall()]

    def get_categories_with_dishes(self):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.execute("""
            SELECT DISTINCT dc.category_name
            FROM dish_category dc
            JOIN dish_info di ON dc.category_name = di.category"""
                                  )
            return [row[0] for row in cursor.fetchall()]

    def save_dish_info(self, data: dict):
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
            insert into dish_info 
            (name, 
            price,
            description,
            category,
            dish_picture)
            VALUES (?,?,?,?,?)""",
                         (data['name'],
                          data['price'],
                          data['description'],
                          data['category'],
                          data['dish_picture']))
            conn.commit()

    def get_menu(self):
        with sqlite3.connect(self.path) as conn:
            result = conn.execute("SELECT * FROM dish_info")
            result.row_factory = sqlite3.Row
            data = result.fetchall()
            return [dict(row) for row in data]

    def check_user_id(self, user_id):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM review_results WHERE user_id = ?",
                           (user_id,))
            user = cursor.fetchall()
            return user

    def insert_or_update_user(self, user_id):
        with sqlite3.connect(self.path) as connection:
            connection.execute("""
            INSERT INTO bot_database (user_id, warnings)
            VALUES (?,0)
            ON CONFLICT(user_id) DO NOTHING """,
                               (user_id,))
            connection.commit()

    def update_warnings(self, user_id: int):
        with sqlite3.connect(self.path) as connection:
            connection.execute("""
            UPDATE bot_database 
            SET warnings = warnings + 1
            WHERE user_id = ?""", (user_id,))
            connection.commit()

            result = connection.execute("""
                        SELECT warnings FROM bot_database WHERE user_id = ?""",
                                        (user_id,)).fetchone()
            return result[0] if result else 0

    def get_warnings(self,user_id: int):
        with sqlite3.connect(self.path) as connection:
            result = connection.execute("""
                                    SELECT warnings FROM bot_database WHERE user_id = ?""",
                                        (user_id,)).fetchone()
            return result[0] if result else 0


    def ban_user(self, user_id: int):
        with sqlite3.connect(self.path) as connection:
            connection.execute("DELETE FROM bot_database WHERE user_id = ?",
                               (user_id,))
            connection.commit()
