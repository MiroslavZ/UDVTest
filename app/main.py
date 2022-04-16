import logging

import aioredis
from aiohttp import web

from handlers import Handler
from middlewares import error_middleware
from routes import setup_routes
from settings import config

logging.basicConfig(level="INFO")


def setup_config(app: web.Application):
    app["config"] = config


def setup_redis(app: web.Application):
    redis_config = config["redis"]
    host = redis_config["host"]
    port = redis_config["port"]
    redis = aioredis.from_url(f"redis://{host}:{port}")

    async def close_redis():
        await redis.close()

    app.on_cleanup.append(close_redis)
    app['redis'] = redis
    return redis


def setup_app(app: web.Application):
    setup_config(app)
    redis = setup_redis(app)
    handler = Handler(redis)
    setup_routes(app, handler)


if __name__ == "__main__":
    app = web.Application(middlewares=[error_middleware])
    setup_app(app)
    web.run_app(app, port=app["config"]["common"]["port"])
