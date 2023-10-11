import re
import aiosqlite
import logging

# LOG
logging.basicConfig(level=logging.INFO)


class Database:

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.db = None

    async def connect(self):
        self.db = await aiosqlite.connect(self.file_name)
        return self.db

    async def insert_video(self, table: str, title: str, msgid: str, category: str) -> bool:
        try:
            await self.db.execute(f"INSERT INTO {table} (title,msgid,category) VALUES (?,?,?)",
                                  (title, msgid, category,))
            return True
        except aiosqlite.IntegrityError:
            return False

    async def create_table(self, table: str):
        page_table = f"""CREATE TABLE IF NOT EXISTS {table} (
                        id             INTEGER PRIMARY KEY AUTOINCREMENT
                                               UNIQUE
                                               NOT NULL,
                        title       TEXT,
                        msgid       TEXT,
                        UNIQUE(msgid) ON CONFLICT FAIL                                              
                    );"""

        await self.db.execute(page_table)

    async def load_table(self, table: str, id_start: int):
        cursor = await self.db.execute(f"SELECT title,msgid FROM {table} WHERE id>?", (id_start,))
        data = cursor.fetchall

    async def load_last_id(self, table: str) -> int:
        cursor = await self.db.execute(f"SELECT id FROM {table} ORDER BY id DESC LIMIT 1")
        return cursor.fetchone()[0]

    def close(self):
        self.db.close()
