import os
import psycopg2


class PostgresManager:
    def __init__(self):
        self.project_name = os.getenv("PROJECT_NAME")
        self.setPostgresConnection()

    def setPostgresConnection(self):
        """
        :return: 連接 Heroku Postgres SQL 認證用
        """
        self.database_url = os.getenv("CORRECT_DATABASE_URL")
        self.conn = psycopg2.connect(self.database_url)

    def closePostgresConnection(self):
        """
        :return: 關閉資料庫連線使用
        """
        self.conn.close()

    def fetchall(self, sql):
        """
        :return:
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute(sql)
            result = cursor.fetchall()
            self.conn.commit()
            cursor.close()
        except:
            self.conn.rollback()
        return result

    def fetchone(self, sql):
        """
        :return:
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute(sql)
            result = cursor.fetchone()
            self.conn.commit()
            cursor.close()
        except:
            self.conn.rollback()
        return result

    def query_without_fetch(self, sql):
        """
        :return:
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
        except:
            self.conn.rollback()
