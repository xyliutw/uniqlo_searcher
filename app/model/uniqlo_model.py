from ..database.postgres_manager import PostgresManager


class UniqloModel(PostgresManager):
    def __init__(self):
        super(UniqloModel, self).__init__()

    def add_subscription(self, user_id, product_id):
        """
        :return:
        """
        print(f"Processing: user_id: {user_id}, product_id: {product_id}")
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO subscription (uid, product_id) VALUES ('{user_id}', '{product_id}');"
        )
            
        self.conn.commit()
        cursor.close()
