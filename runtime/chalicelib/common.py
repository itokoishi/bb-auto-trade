import os
import boto3
import pybitflyer
import datetime


class Common:

    # １回の取引で購入する数量
    SIZE = 70
    # 何分ごとに価格を取得するか
    PRICE_GET_MINUTES = 30
    # 過去何回分の平均値を取得するか
    DURATION = 20
    # API情報
    API_KEY = os.environ.get('API_KEY', '')
    API_SECRET = os.environ.get('API_SECRET', '')
    # テーブル名
    APP_TABLE_NAME = os.environ.get('APP_TABLE_NAME', '')
    # 環境情報
    ENVIRONMENT = os.environ.get('ENVIRONMENT', '')
    # dynamoDBのエンドポイント
    ENDPOINT_URL = os.environ.get('ENDPOINT_URL', '')
    # 銘柄指定
    PRODUCT_CODE = 'XRP_JPY'
    CURRENCY_CODE = 'XRP'

    def __init__(self):
        # ローカル（dev）の場合はエンドポイントを指定
        if self.ENVIRONMENT == 'dev':
            dynamodb = boto3.resource('dynamodb', endpoint_url=self.ENDPOINT_URL)
        else:
            dynamodb = boto3.resource('dynamodb')

        self.table = dynamodb.Table(self.APP_TABLE_NAME)
        self.bitflyer_api = pybitflyer.API(api_key=self.API_KEY, api_secret=self.API_SECRET)

    def _get_duration_data(self):
        """ 料金のデータを取得する(ソートキーを昇順に並べる)
        Args:
        Returns: (dict): 料金データ
        """

        query = self._get_all_price_query()

        response = self.table.query(**query)
        response_items = response.get('Items', [])
        items = []
        for row in response_items:
            items.append({key: float(val) if key == 'price' else val for key, val in row.items()})

        return items

    def _get_first_sk(self):
        """ 最初のデータを取得する
        Returns:　(dict): 最初のデータ
        """

        query = self._get_all_price_query()
        query.update({'Limit': 1})
        response = self.table.query(**query)
        items = response.get('Items', [])

        return items[0].get('SK')

    def _get_latest_sk(self):
        """ 最新のデータを取得する
        Args:
        Returns:　(dict): 最新のデータ
        """

        query = self._get_all_price_query()
        query.update({
            'ScanIndexForward': False,
            'Limit': 1
        })

        response = self.table.query(**query)
        items = response.get('Items', [])

        return items[0].get('SK')

    @staticmethod
    def _get_all_price_query():
        """
        全料金の情報を返す
        Returns: (dict): 全料金の情報
        """

        return {
            'TableName': 'auto_trade',
            'KeyConditionExpression': 'PK=:PK',
            'ScanIndexForward': True,
            'ExpressionAttributeValues': {':PK': 'duration'}
        }

    @staticmethod
    def _get_now():
        """
        JSTの現在時間を返す
        Returns: (str): 現在時間
        """

        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        date = datetime.datetime.now(JST)
        now_time = date.strftime('%Y%m%d%H%M%S')

        return now_time