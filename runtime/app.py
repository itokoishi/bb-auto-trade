from chalice import Chalice, Rate
from chalicelib.put_pice import PutPrice
from chalicelib.auto_trade import AutoTrade
from chalicelib.common import Common
from boto3.dynamodb.types import TypeDeserializer

app = Chalice(app_name='batch-apps')
ARN = 'arn:aws:dynamodb:ap-northeast-1:422132123004:table/auto_trade/stream/2023-05-07T08:55:23.216'


@app.on_dynamodb_record(stream_arn=ARN)
def auto_trade(event):

    for record in event:
        if record.event_name == 'REMOVE':
            continue

        new_item = record.new_image
        item = deserialize(new_item)

        if item.get('PK') == 'duration':
            auto_trade = AutoTrade()
            auto_trade.execute()


@app.schedule(Rate(Common.PRICE_GET_MINUTES, unit=Rate.MINUTES))
def put_price(event):
    put_price = PutPrice()
    put_price.execute()


deserializer = TypeDeserializer()


def deserialize(image):
    """
    dictに変換する
    """
    d = {}
    for key in image:
        d[key] = deserializer.deserialize(image[key])
    return d