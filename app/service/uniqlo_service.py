from ..module.uniqlo_module import UniqloModule


class UniqloService:
    def __init__(self, user_id=None, message=None):
        self.user_id = user_id
        self.message = message
        self.module = UniqloModule(self.user_id, self.message)

    def get_current_price(self):
        flex_message = self.module.get_current_price()
        return flex_message

    def subscribe(self, data):
        result = self.module.subscribe(data)
        return result

    def unsubscribe(self, data):
        result = self.module.unsubscribe(data)
        return result

    def send_notification(self):
        result = self.module.send_notification(self.user_id)
        return result
    
    def get_subscription_list(self):
        result = self.module.get_subscription_list()
        return result