from dataclasses import dataclass, asdict
from datetime import datetime
from dateutil.parser import parse as dateutil_parse
from dateutil.tz import gettz as dateutil_gettz
import hashlib
import hmac
import logging
import os
import re
import secrets
import xml.etree.ElementTree as ET

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# YouTube から送られてくる HMAC の16進数の値を取り出すための正規表現
X_HUB_SIGNATURE = re.compile(r"sha1=([0-9a-f]{40})")

# YouTube から送られてくるXMLデータの名前空間情報
XML_NAMESPACE = {
    'atom': 'http://www.w3.org/2005/Atom',
    'yt': 'http://www.youtube.com/xml/schemas/2015',
}

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
    challenge: str


@dataclass(frozen=True)
class RequestNotify:
    x_hub_signature: str
    body: str


@dataclass(frozen=True)
class Response:
    statusCode: int
    body: str


@dataclass(frozen=True)
class Entry:
    videoId: str
    channelId: str
    title: str
    link: str
    authorName: str
    authorUri: str
    published: datetime
    updated: datetime


def challenge(req: RequestChalenge) -> Response:
    """
    challengeのロジック部分
    """
    if not secrets.compare_digest(req.verifyToken, VERIFY_TOKEN):
        return Response(statusCode=404, body='{"message":"Not Found"}')

    return Response(statusCode=200, body=req.challenge)


def notify(req: RequestNotify) -> Response:
    """
    notifyのロジック部分
    """
    if not (m := X_HUB_SIGNATURE.match(req.x_hub_signature)):
        return Response(403, '{"message":"Forbidden"}')

    if not validate_hmac(m.groups()[0], req.body, HMAC_SECRET):
        return Response(403, '{"message":"Forbidden"}')

    entry = parse(req.body)

    logger.info(entry)

    return Response(200, "")


def validate_hmac(hub_signature: str, msg: str, key: str) -> bool:
    digits = hmac.new(key.encode(), msg.encode(), hashlib.sha1).hexdigest()

    return hmac.compare_digest(hub_signature, digits)


def parse(text: str) -> Entry:
    root = ET.fromstring(text)
    entry = root.find("atom:entry", XML_NAMESPACE)
    author = entry.find("atom:author", XML_NAMESPACE)

    return Entry(videoId=entry.find("yt:videoId", XML_NAMESPACE).text,
                 channelId=entry.find("yt:channelId", XML_NAMESPACE).text,
                 title=entry.find("atom:title", XML_NAMESPACE).text,
                 link=entry.find("atom:link", XML_NAMESPACE).get("href"),
                 authorName=author.find("atom:name", XML_NAMESPACE).text,
                 authorUri=author.find("atom:uri", XML_NAMESPACE).text,
                 published=dateutil_parse(
                     entry.find("atom:published",
                                XML_NAMESPACE).text).astimezone(
                                    dateutil_gettz('Asia/Tokyo')),
                 updated=dateutil_parse(
                     entry.find("atom:updated",
                                XML_NAMESPACE).text).astimezone(
                                    dateutil_gettz('Asia/Tokyo')))


def get_handler(event, context):
    """
    GET /hub
    """
    logger.info(event)    # for debug
    params: dict = event.get("queryStringParameters", "")
    req = RequestChalenge(verifyToken=params.get("hub.verify_token", ""),
                          challenge=params.get("hub.challenge", ""))

    res = challenge(req)

    return asdict(res)


def post_handler(event, context):
    """
    POST /hub
    """
    logger.info(event)    # for debug
    headers: dict = event.get("headers", {})
    req = RequestNotify(x_hub_signature=headers.get("x-hub-signature", ""),
                        body=event.get("body", ""))

    res = notify(req)

    return asdict(res)
