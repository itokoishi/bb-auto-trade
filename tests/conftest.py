import os
import sys
import json
import pytest
from chalice.test import Client
from dotenv import load_dotenv

load_dotenv(verbose=True)
dotenv_path = os.path.join(os.path.dirname(__file__), '../infrastructure/stacks/.env')
load_dotenv(dotenv_path)

# -- テスト用に環境変数を設定 ---------------------
os.environ['APP_TABLE_NAME'] = "auto_trade"
os.environ['ENDPOINT_URL'] = "http://trade-dynamodb-local:8000"
os.environ['ENVIRONMENT'] = "dev"
os.environ['API_KEY'] = os.environ.get('API_KEY')
os.environ['API_SECRET'] = os.environ.get('API_SECRET')

@pytest.fixture
def test_client():
    import app
    with Client(app) as client:
        yield client
