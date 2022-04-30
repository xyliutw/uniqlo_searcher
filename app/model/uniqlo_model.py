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
            f"""INSERT INTO product (product_id, product_code, image_url, origin_price, price, min_price, name, product_name) VALUES ('{info['product_id']}', '{info['product_code']}', '{info['main_pic']}', {info['origin_price']}, {info['price']}, {info['min_price']}, '{info['name']}', '{info['product_name']}') ON CONFLICT (product_id) DO UPDATE SET image_url = '{info['main_pic']}', price = {info['price']}, min_price = {info['min_price']}, name = '{info['name']}', product_name = '{info['product_name']}' """
        ) 
        self.conn.commit()
        cursor.close()
    
    def check_product_exist(self, product_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT * FROM product WHERE product_id = '{product_id}'"
        )
        self.conn.commit()
        result = cursor.fetchone()
        cursor.close()
        return result

    
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

    def update_last_notify_price(self, product_id, price):
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE product SET last_notify_price = {price} WHERE product_id = '{product_id}';"
        )      
        self.conn.commit()
        cursor.close()

    def get_product_list(self):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT * FROM product"
        )
        self.conn.commit()
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def daily_update(self, product_id, price, min_price):
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE product SET price = {price}, min_price = {min_price} WHERE product_id = '{product_id}';"
        )      
        self.conn.commit()
        cursor.close()