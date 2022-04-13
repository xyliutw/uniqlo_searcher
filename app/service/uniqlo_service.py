from ..module.uniqlo_module import UniqloModule


class UniqloService:
    def __init__(self, user_id=None, message=None):
        self.user_id = user_id
        self.message = message
        self.module = UniqloModule(self.user_id, self.message)

    def get_current_price(self):
        stock_ids = self.module.get_current_price()
        return stock_ids
