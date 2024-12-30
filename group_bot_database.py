# # import sqlite3
# #
# #
# # class GroupBotDatabase:
# #     def __init__(self, path: str):
# #         self.path = path
# #         self.create_tables()
# #
# #     def create_tables(self):
#         with sqlite3.connect(self.path) as conn:
#             conn.execute("""
#             CREATE TABLE IF NOT EXISTS bot_database
#             (id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE,
#             warnings INTEGER DEFAULT 0)
#             # """)
#         conn.commit()
# #
# #     def insert_bot_database(self, data: dict):
# #         with sqlite3.connect(self.path) as conn:
# #             conn.execute("""
# #             INSERT INTO bot_database
# #             (username, warnings)
# #             VALUES
# #             (?,0)
# #             ON CONFLICT (username) DO NOTHING
# #             """, (username,))
# #             conn.commit()
# #
# #     def update_warnings(self, username: str):
# #         with sqlite3.connect(self.path) as conn:
# #             conn.execute("""
# #             UPDATE bot_database
# #             SET warnings = warnings + 1
# #             WHERE username = ?""",
# #                          (username,))
# #
# #             conn.commit()
# #
# #     def get_warnings(self, username: str) -> int:
# #         with sqlite3.connect(self.path) as conn:
# #             result = conn.execute("""
# #             SELECT warnings FROM bot_database WHERE username = ?""",
# #                                   (username,)).fetchone()
# #
# #             return result[0] if result else 0
# #
# #     def ban_user(self, username: str):
# #         with sqlite3.connect(self.path) as conn:
# #             conn.execute("""
# #             DELETE FROM bot_database WHERE username = ?""",
# #                          (username,))
# #             conn.commit()
