from ..database.postgres_manager import PostgresManager


class UniqloModel(PostgresManager):
    def __init__(self):
        super(UniqloModel, self).__init__()

    def get_stock_id(self, stock_name):
        return super().get_stock_id(stock_name)

    def get_related_stock_id(self, key):
        """
        :return:
        """
        cursor = self.conn.cursor()

        cursor.execute(
            f"SELECT STOCK_ID, STOCK_NAME FROM stock_info WHERE STOCK_NAME LIKE '%{key}%'"
        )
        result = cursor.fetchall()
        self.conn.commit()
        cursor.close()
        return result

    def get_stock_id(self, stock_name):
        """
        :return:
        """
        cursor = self.conn.cursor()

        cursor.execute(
            f"SELECT STOCK_ID, STOCK_NAME FROM stock_info WHERE STOCK_NAME = '{stock_name}'"
        )
        result = cursor.fetchone()
        self.conn.commit()
        cursor.close()
        return result[0]

    def get_stock_name(self, stock_id):
        """
        :return:
        """
        cursor = self.conn.cursor()

        cursor.execute(
            f"SELECT STOCK_NAME FROM stock_info WHERE STOCK_ID = '{stock_id}'"
        )
        result = cursor.fetchone()
        self.conn.commit()
        cursor.close()
        return result[0]

    def insert_stock_info(self, data):
        """
        :return:
        """
        cursor = self.conn.cursor()

        for values in data:
            print(f"Processing: {values}")
            cursor.execute(
                f"INSERT INTO stock_info (stock_id, stock_name) VALUES {values} ON CONFLICT (stock_id) DO NOTHING;"
            )
        self.conn.commit()
        cursor.close()
