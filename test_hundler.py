from datetime import datetime
from dateutil.tz import gettz as dateutil_gettz
from dotenv import load_dotenv
from handler import RequestChalenge, RequestNotify, Response, Entry  # 型の読み込み
import handler  # 関数の読み込み
import os

# dotenvの読み込み
load_dotenv()

# 検証用のキー
HMAC_SECRET: str = os.environ["PuSH_hmac_secret"]


def test_challenge():
    challenge = "challenge"
    expected = Response(200, challenge)
    actual = handler.challenge(RequestChalenge(challenge))
    assert expected == actual


def test_validate_hmac():
    assert handler.validate_hmac("0c94515c15e5095b8a87a50ba0df3bf38ed05fe6", "test", "test")
    assert not handler.validate_hmac("1c94515c15e5095b8a87a50ba0df3bf38ed05fe6", "test", "test")


def test_parse():
    expected = Entry(
        videoId="test_videoId",
        channelId="test_channelId",
        title="test_title",
        link="http://example.com/watch?v=test_videoId",
        authorName="test_author_name",
        authorUri="http://example.com/channel/test_channelId",
        published=datetime(2022, 1, 28, 21, 40, 35, tzinfo=dateutil_gettz('Asia/Tokyo')),
        updated=datetime(2022, 1, 28, 21, 40, 58, 132027, tzinfo=dateutil_gettz('Asia/Tokyo'))
    )
    actual = handler.parse("""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
    <link rel="hub" href="https://pubsubhubbub.appspot.com" />
    <link rel="self" href="https://www.youtube.com/xml/feeds/videos.xml?channel_id=test_channelId" />
    <title>YouTube video feed</title>
    <updated>2022-01-28T12:40:58.132027669+00:00</updated>
    <entry>
        <id>yt:video:test_videoId</id>
        <yt:videoId>test_videoId</yt:videoId>
        <yt:channelId>test_channelId</yt:channelId>
        <title>test_title</title>
        <link rel="alternate" href="http://example.com/watch?v=test_videoId" />
        <author>
            <name>test_author_name</name>
            <uri>http://example.com/channel/test_channelId</uri>
        </author>
        <published>2022-01-28T12:40:35+00:00</published>
        <updated>2022-01-28T12:40:58.132027669+00:00</updated>
    </entry>
</feed>
""")
    assert expected == actual


def test_notify(mocker):
    req = RequestNotify("test_x_hub_signature", "")
    expected = 200
    actual = handler.notify(req)
    assert expected == actual.statusCode

    req = RequestNotify("sha1=0000111122223333444455556666777788889999", "")
    expected = 200
    actual = handler.notify(req)
    assert expected == actual.statusCode

    mocker.patch("handler.validate_hmac", return_value=True)
    mocker.patch("handler.parse", return_value="")
    expected = 200
    req = RequestNotify("sha1=0000111122223333444455556666777788889999", "")
    actual = handler.notify(req)
    assert expected == actual.statusCode

    mocker.patch("handler.action", side_effect=Exception)
    expected = 500
    req = RequestNotify("sha1=0000111122223333444455556666777788889999", "")
    actual = handler.notify(req)
    assert expected == actual.statusCode
