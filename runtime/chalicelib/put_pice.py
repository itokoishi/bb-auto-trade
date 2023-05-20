from .common import Common


class PutPrice(Common):
    """
    料金情報をDynamoDBに登録
    """

    def __init__(self):
        super().__init__()

    def execute(self):
        """ 料金データの登録実行
        Returns: void
        """

        latest_sk = self._get_latest_sk()
        ticker = self.bitflyer_api.ticker(product_code=self.PRODUCT_CODE)
        param = {
            'PK': 'duration',
            'SK': latest_sk + 1,
            'price': str(ticker['ltp']),
            'register_time': self._get_now()
        }
        self.table.put_item(Item=param)

        # 取得回数以上のデータがある場合は最初のデータを削除
        after_items = self._get_duration_data()
        if len(after_items) > self.DURATION:
            first_sk = self._get_first_sk()
            self.table.delete_item(Key={'PK': 'duration', 'SK': first_sk})


