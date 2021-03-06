# YouTube pubsubhubbub lambda
[![Python lint and test](https://github.com/meihei3/youtube-pubsubhubbub-lambda/actions/workflows/python-lint-and-test.yml/badge.svg)](https://github.com/meihei3/youtube-pubsubhubbub-lambda/actions/workflows/python-lint-and-test.yml)

This application receives notifications from YouTube via PubSubHubBub and runs AWS Lambda.

For more information on how to use PubSubHubBub(PuSH) and how to receive notifications from YouTube, please refer to [here](https://developers.google.com/youtube/v3/guides/push_notifications).

## Require
- pipenv
- serverless framework

## Setup & Deploy

### 1. Set up pipenv

```
$ pipenv sync
```

### 2. Set up npm packages

```
$ npm install
```

### 3. Wrtie .env

```
PuSH_hmac_secret=[your_push_hmac_secret]
```

### 4. Deploy!

```
$ sls deploy
```

## Usage

### Implement the your process

By rewriting the `action()` function, you can implement the original process.
