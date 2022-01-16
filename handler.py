import json
import logging
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 検証用のキー
VERIFY_TOKEN = os.getenv("PuSH_verify_token")
HMAC_SECRET = os.getenv("PuSH_hmac_secret")


def challenge(event, context):
    """
    GET /hub
    """
    params: dict = event.get("queryStringParameters")

    if params.get("hub.verify_token", "") != VERIFY_TOKEN:
        logger.info(params)
        return {
            "statusCode": 403,
            "body": ""
        }

    return {
        "statusCode": 200,
        "body": params.get("hub.challenge", "")
    }
