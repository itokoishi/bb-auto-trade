from .common import Common
import pandas as pd


class BringerBand(Common):
    """

    """

    def __init__(self):
        super().__init__()

    def get_trade_type(self):
        """
        ポリンジャーバンドの取得を行い、売り買いどちらかを返す
        Returns: (str): buy or sell
        """

        result = ''
        # dynamoから料金のデータを取得する
        items = self._get_duration_data()

        # 過去取得回数分のデータがある場合に実行
        if len(items) >= self.DURATION:
            df = pd.DataFrame(items)

            df['SMA'] = df['price'].rolling(window=self.DURATION).mean()
            df['std'] = df['price'].rolling(window=self.DURATION).std()

            df['-2σ'] = df['SMA'] - 2 * df['std']
            df['+2σ'] = df['SMA'] + 2 * df['std']

            # もし-2σを割ったら買いを入れる
            if df['price'].iloc[-1] < df['-2σ'].iloc[-1]:
                result = 'buy'

            # もし+2σを超えたら売りを入れる
            if df['+2σ'].iloc[-1] < df['price'].iloc[-1]:
                result = 'sell'

        return result
