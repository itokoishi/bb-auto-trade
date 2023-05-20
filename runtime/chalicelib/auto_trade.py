from .common import Common
from .bringer_band import BringerBand
import math


class AutoTrade(Common):
    """
    自動売買処理
    """

    def __init__(self):
        super().__init__()

    def execute(self):
        """自動売買処理の実行
        Returns: (None)
        """

        bringer_band = BringerBand()
        trade_type = bringer_band.get_trade_type()

        if trade_type == 'buy':
            if not self.is_exists_buy(): self.trade_buy()
        if trade_type == 'sell':
            if self.is_exists_buy(): self.trade_sell()
        else:
            return {}

    def trade_buy(self):
        """
        買い注文APIを走らせる
        """

        result = []
        # if self.ENVIRONMENT != 'dev':
        result = self.bitflyer_api.sendchildorder(
            product_code=self.PRODUCT_CODE,
            child_order_type='MARKET',
            side='BUY',
            size=self.SIZE
        )

        if 'error_message' not in result:
            self.change_progress('BUY')

        return result

    def trade_sell(self):
        """
        売り注文処理を走らせる
        """

        # 現在の残高取得
        result = []
        balance = self.bitflyer_api.getbalance()
        currency_balance = [row for row in balance if row.get('currency_code') == self.CURRENCY_CODE][0]
        amount = currency_balance.get('amount')

        # 手数料を差し引いた金額
        trading_commission = self.bitflyer_api.gettradingcommission(product_code=self.PRODUCT_CODE)
        size = amount - (trading_commission['commission_rate'] * currency_balance.get('amount'))

        # 最低取引価格で切り捨て
        size = math.floor(size * 10 ** 6) / (10 ** 6)

        # if self.ENVIRONMENT != 'dev':
        result = self.bitflyer_api.sendchildorder(
            product_code=self.PRODUCT_CODE,
            child_order_type='MARKET',
            side='SELL',
            size=size
        )

        if 'error_message' not in result:
            self.change_progress('SELL')

        return result

    def change_progress(self, progress):
        """買い注文、売り注文の進捗を変更する
        Args:
            progress (str): 買い(BUY) or 売り(SELL)
        """

        param = {
            'PK': 'trade',
            'SK': 0,
            'progress': progress,
            'register_time': self._get_now()
        }
        self.table.put_item(Item=param)

    def is_exists_buy(self):
        """買い注文中か否かを返す
        Returns: (bool): 買い注文中か否か
        """

        query = {
            'TableName': 'auto_trade',
            'KeyConditionExpression': 'PK=:PK',
            'ExpressionAttributeValues': {':PK': 'trade'}
        }
        response = self.table.query(**query)
        items = response.get('Items', [])

        return items[0].get('progress') == 'BUY'
