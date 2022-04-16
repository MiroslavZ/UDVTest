from aiohttp import web

from handlers import Handler


def setup_routes(app: web.Application, handler: Handler):
    app.router.add_get('/convert', handler.convert_currency)
    app.router.add_post('/database', handler.update_exchange_rate)
