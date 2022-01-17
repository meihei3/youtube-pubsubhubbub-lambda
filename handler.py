from dataclasses import dataclass, asdict
import logging
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 検証用のキー
try:
    VERIFY_TOKEN: str = os.environ["PuSH_verify_token"]
    HMAC_SECRET: str = os.environ["PuSH_hmac_secret"]
except KeyError:
    from dotenv import load_dotenv
    load_dotenv()
    VERIFY_TOKEN: str = os.environ["PuSH_verify_token"]
    HMAC_SECRET: str = os.environ["PuSH_hmac_secret"]
except:
    logger.error("environment variable not found")
    exit()


@dataclass(frozen=True)
class RequestChalenge:
    verifyToken: str


@dataclass(frozen=True)
class Response:
    statusCode: int
    body: str


def challenge(req: RequestChalenge) -> Response:
    """
    challengeのロジック部分
    """
    if req.verifyToken != VERIFY_TOKEN:
        return Response(statusCode=404, body='{"message":"Not Found"}')

    return Response(statusCode=200, body=req.verifyToken)


def get_handler(event, context):
    """
    GET /hub
    """
    params: dict = event.get("queryStringParameters")
    req = RequestChalenge(verifyToken=params.get("hub.verify_token", ""))

    res = challenge(req)

    return asdict(res)
