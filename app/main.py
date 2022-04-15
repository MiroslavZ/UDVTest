import logging

import aioredis
import yaml
from aiohttp import web

from app.handlers import Handler
from app.middlewares import error_middleware
from app.routes import setup_routes

logging.basicConfig(level="INFO")


def setup_redis(app: web.Application, conf):
    host = conf["redis"]["host"]
    port = conf["redis"]["port"]
    redis = aioredis.from_url(f"redis://{host}:{port}")

    async def close_redis():
        await redis.close()

    app.on_cleanup.append(close_redis)
    app['redis'] = redis
    return redis


def setup_app(app: web.Application):
    conf = load_config('config/config.yaml')
    redis = setup_redis(app, conf)
    handler = Handler(redis)
    setup_routes(app, handler)


def load_config(fname):
    with open(fname, 'rt') as f:
        data = yaml.safe_load(f)
    return data


if __name__ == "__main__":
    app = web.Application(middlewares=[error_middleware])
    setup_app(app)
    web.run_app(app)
