import sqlite3

# DISH DATABASE

class Dish_db:
    def __init__(self, path: str):
        self.path = path

    def create_tables(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS dish_info
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price FLOAT,
            description VARCHAR(150),
            category TEXT 
            )""")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS dish_category
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL)""")
            conn.commit()

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


    def get_categories(self):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.execute('SELECT category_name FROM dish_category')
            return [row[0] for row in cursor.fetchall()]

    def save_dish_info(self, data: dict):
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
            insert into dish_info 
            (name, 
            price,
            description,
            category)
            VALUES (?,?,?,?)""",
                         (data['name'],
                          data['price'],
                          data['description'],
                          data['category']))
            conn.commit()


    def get_menu(self):
        with sqlite3.connect(self.path) as conn:
            result = conn.execute("SELECT * FROM dish_info")
            return result.fetchall()

