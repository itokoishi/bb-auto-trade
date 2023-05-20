import os
from dotenv import load_dotenv
from aws_cdk import aws_dynamodb as dynamodb

try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk

from chalice.cdk import Chalice


RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir, 'runtime')

load_dotenv(verbose=True)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


class ChaliceApp(cdk.Stack):

    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.dynamodb_table = self._create_ddb_table()
        # chaliceの設定
        self.chalice = Chalice(
            self, 'ChaliceApp', source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                'environment_variables': {
                    'APP_TABLE_NAME': self.dynamodb_table.table_name,
                    'API_KEY': os.environ.get('API_KEY'),
                    'API_SECRET': os.environ.get('API_SECRET'),
                },
                'automatic_layer': True,
                'time_out': '300'
            }
        )

        # -- dynamodbにアクセスするためのロール追加 ---------------------
        self.dynamodb_table.grant_read_write_data(
            self.chalice.get_role('DefaultRole')
        )

        # -- chaliceで設定できないものを追加 ---------------------
        auto_trade_lambda = self.chalice.get_resource('AutoTrade')
        auto_trade_lambda.add_override('Properties', {'FunctionName': 'auto_trade'})
        auto_trade_lambda = self.chalice.get_resource('PutPrice')
        auto_trade_lambda.add_override('Properties', {'FunctionName': 'put_price'})

    def _create_ddb_table(self):
        dynamodb_table = dynamodb.Table(
            self, 'AppTable',
            table_name='auto_trade',
            partition_key=dynamodb.Attribute(name='PK', type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name='SK', type=dynamodb.AttributeType.NUMBER),
            removal_policy=cdk.RemovalPolicy.DESTROY)
        cdk.CfnOutput(self, 'AppTableName', value=dynamodb_table.table_name)

        return dynamodb_table
