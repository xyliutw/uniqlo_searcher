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
    
    def add_product_data(self, info):
        print(f"Processing: product_id: {info['product_id']}")
        cursor = self.conn.cursor()
        print(info)
        cursor.execute(
            f"INSERT INTO product (product_id, product_code, image_url, origin_price, price, min_price) VALUES ('{info['product_id']}', '{info['product_code']}', '{info['main_pic']}', {info['origin_price']}, {info['price']}, {info['min_price']});"
        ) 
        self.conn.commit()
        cursor.close()

    
    def remove_subscription(self, user_id, product_id):
        """
        :return:
        """
        print(f"Processing: user_id: {user_id}, product_id: {product_id}")
        cursor = self.conn.cursor()
        cursor.execute(
            f"DELETE FROM subscription WHERE uid = '{user_id}' AND product_id = '{product_id}';"
        )
            
        self.conn.commit()
        cursor.close()
    
    def get_send_list(self):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT * FROM subscription"
        )
        self.conn.commit()
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_user_subscription_list(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT * FROM subscription WHERE uid = '{user_id}'"
        )
        self.conn.commit()
        result = cursor.fetchall()
        cursor.close()
        return result
