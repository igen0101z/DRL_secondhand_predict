import sqlite3

class DatabaseHandler:
    """
    負責資料庫操作的類別，提供連接、查詢與寫入等功能。
    """
    def __init__(self, db_path=None):
        self.db_path = db_path or 'data.db'
        self.conn = None

    def connect(self):
        """
        連接到資料庫。
        """
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def close(self):
        """
        關閉資料庫連線。
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query, params=None):
        """
        執行查詢語句並回傳結果。
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params or [])
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_non_query(self, query, params=None):
        """
        執行非查詢語句（如 INSERT、UPDATE、DELETE）。
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params or [])
        self.conn.commit()
        cursor.close()