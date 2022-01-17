from dotenv import load_dotenv
from handler import RequestChalenge, Response  # 型の読み込み
import handler  # 関数の読み込み
import os

# dotenvの読み込み
load_dotenv()

# 検証用のキー
VERIFY_TOKEN: str = os.environ["PuSH_verify_token"]
HMAC_SECRET: str = os.environ["PuSH_hmac_secret"]


def test_challenge():
    expected = Response(200, VERIFY_TOKEN)
    actual = handler.challenge(RequestChalenge(VERIFY_TOKEN))
    assert expected == actual

    expected = 404
    actual = handler.challenge(RequestChalenge("hoge"))
    assert expected == actual.statusCode

    expected = 404
    actual = handler.challenge(RequestChalenge(""))
    assert expected == actual.statusCode

