# YouTube pubsubhubbub lambda

This application receives a notification from YouTube via PubSubHubBub and runs AWS Lambda.

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
PuSH_verify_token=[your_push_verify_token]
PuSH_hmac_secret=[your_push_hmac_secret]
```

### 4. Deploy!

```
$ sls deploy
```
