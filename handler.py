from dataclasses import dataclass, asdict
import hashlib
import hmac
import logging
import os
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

X_HUB_SIGNATURE = re.compile(r"sha1=([0-9a-f]{40})")

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
class RequestNotify:
    x_hub_signature: str
    body: str


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


def notify(req: RequestNotify) -> Response:
    """
    notifyのロジック部分
    """
    if not (m := X_HUB_SIGNATURE.match(req.x_hub_signature)):
        return Response(403, '{"message":"Forbidden"}')

    if not validate_hmac(m.groups()[0], req.body, HMAC_SECRET):
        return Response(403, '{"message":"Forbidden"}')

    return Response(200, "")


def validate_hmac(hub_signature: str, msg: str, key: str) -> bool:
    digits = hmac.new(key.encode(), msg.encode(), hashlib.sha1).hexdigest()

    return hmac.compare_digest(hub_signature, digits)


def get_handler(event, context):
    """
    GET /hub
    """
    params: dict = event.get("queryStringParameters")
    req = RequestChalenge(verifyToken=params.get("hub.verify_token", ""))

    res = challenge(req)

    return asdict(res)


def post_handler(event, context):
    """
    POST /hub
    """
    headers: dict = event.get("headers", {})
    req = RequestNotify(signature=headers.get("x-hub-signature", ""),
                        body=event.get("body", ""))

    res = notify(req)

    return asdict(res)
