from logging import getLogger, Formatter, FileHandler, DEBUG, INFO
import pytest
import time
from chalicelib.put_pice import PutPrice
from chalicelib.auto_trade import AutoTrade
from chalicelib.bringer_band import BringerBand

logger = getLogger(__name__)
logger.setLevel(INFO)


def log_fileout():
    """ ログファイル出力
    Returns: (void)
    """
    logger.setLevel(DEBUG)
    fileout = FileHandler('app.log')
    fileout.setLevel(INFO)
    fmt = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileout.setFormatter(fmt)
    logger.addHandler(fileout)


log_fileout()


@pytest.mark.usefixtures("test_client")
class TestAutoTrade:
    @pytest.fixture(scope='function')
    def init_result(self):
        """ テスト初期化
        Returns:
        """
        self._put_price = PutPrice()
        self._auto_trade = AutoTrade()
        self.bringer_band = BringerBand()

    def test_put_price(self, init_result):
        """
        料金の登録を指定回+1、実行するテスト
        """

        for i in range(self._put_price.DURATION + 1):
            self._put_price.execute()
            time.sleep(5)

        items = self._put_price._get_duration_data()

        # 登録後指定回数分の件数であれば成功
        assert len(items) == self._put_price.DURATION

    def test_auto_trade(self, init_result):
        """
        自動売買のテスト
        """
        self._auto_trade.execute()

    def test_get_trade_type(self, init_result):
        """
        買い、売りの判定テスト
        """

        # -- 買いの判定テスト ---------------------
        self._put_buy_data(self.bringer_band)
        result = self.bringer_band.get_trade_type()
        assert result == 'buy'
        logger.info(result)

        # # -- 売りの判定テスト ---------------------
        self._put_sell_data(self.bringer_band)
        result = self.bringer_band.get_trade_type()
        assert result == 'sell'

    def test_trade_buy(self, init_result):
        """
        買い注文のテスト
        """
        self._put_buy_data(self.bringer_band)
        result = self._auto_trade.trade_buy()
        logger.info(result)

    def test_trade_sell(self, init_result):
        """
        売り注文のテスト
        """
        self._put_sell_data(self.bringer_band)
        result = self._auto_trade.trade_sell()
        logger.info(result)

    @staticmethod
    def _put_buy_data(bringer_band):
        """
        買いの判定がでるデータの登録
        """
        items = bringer_band._get_duration_data()
        for row in items:
            bringer_band.table.delete_item(Key={'PK': 'duration', 'SK': row.get('SK')})

        for i in range(10, 30):
            bringer_band.table.put_item(Item={'PK': 'duration', 'SK': i, 'price': str(i * 100), 'register_time': bringer_band._get_now()})
        bringer_band.table.put_item(Item={'PK': 'duration', 'SK': i, 'price': str(100), 'register_time': bringer_band._get_now()})

    @staticmethod
    def _put_sell_data(bringer_band):
        """
        売りの判定がでるデータの登録
        """
        items = bringer_band._get_duration_data()
        for row in items:
            bringer_band.table.delete_item(Key={'PK': 'duration', 'SK': row.get('SK')})

        for i in range(10, 30):
            bringer_band.table.put_item(Item={'PK': 'duration', 'SK': i, 'price': str(i * 100), 'register_time': bringer_band._get_now()})
        bringer_band.table.put_item(Item={'PK': 'duration', 'SK': i, 'price': str(4000), 'register_time': bringer_band._get_now()})