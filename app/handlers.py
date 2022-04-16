import json
import logging

from aiohttp import web
from aioredis import Redis
from pydantic import ValidationError

from schemas import ConvertRequest, UpdateExchangeRateRequest

_logger = logging.getLogger(__name__)


class Handler:

    def __init__(self, redis: Redis):
        self.redis = redis

    async def convert_currency(self, request: web.Request) -> web.Response:
        try:
            from_currency = request.query['from']
            to_currency = request.query['to']
            amount = request.query['amount']
            data_validated = ConvertRequest(from_currency=from_currency, to_currency=to_currency, amount=amount)
            pair = from_currency + to_currency
            _logger.info(
                f"from = {from_currency}({type(from_currency)}),to = {to_currency}({type(to_currency)}), "
                f"amount = {amount}({type(amount)})")
            if await self.redis.exists(pair):
                _logger.info(f"Required currency pair {pair} is founded")
                exchange_rate = float((await self.redis.lindex(pair, -1)).decode())
                _logger.info(f"Last saved exchange rate is {exchange_rate}")
                converted = float(amount) * exchange_rate
                response_obj = {'converted': converted}
                return web.Response(text=json.dumps(response_obj), status=200)
            else:
                _logger.warning(f"Required currency pair {pair} not founded")
                response_obj = {'message': f'The exchange of the currency pair {from_currency} '
                                           f'to {to_currency} is not supported'}
                return web.Response(text=json.dumps(response_obj), status=404)
        except KeyError as e:
            raise web.HTTPUnprocessableEntity(reason=f"Field {e} is required")
        except ValidationError as e:
            raise web.HTTPUnprocessableEntity(reason=e.json())
        except ValueError as e:
            raise web.HTTPUnprocessableEntity(reason=str(e))

    async def update_exchange_rate(self, request: web.Request) -> web.Response:
        try:
            merge = int(request.query['merge'])
            body = await request.json()
            pair = body['currency_pair']
            new_rate = body['new_exchange_rate']
            data_validated = UpdateExchangeRateRequest(currency_pair=pair, new_rate=new_rate,
                                                       merge=merge)
            _logger.info(
                f"merge = {merge}({type(merge)}),pair = {pair}({type(pair)}), "
                f"new_rate = {new_rate}({type(new_rate)})")
            if await self.redis.exists(pair):
                _logger.info(f"Required currency pair {pair} is founded")
                if merge == 0:
                    _logger.info(f"Deleting old rates for pair {pair}")
                    await self.redis.delete(pair)
                _logger.info(f"Adding new rate for pair {pair}")
                await self.redis.rpush(pair, new_rate)
            else:
                _logger.info(f"Creating rate for pair {pair}")
                await self.redis.rpush(pair, new_rate)
                response_obj = {'message': f'created new exchange rate {pair} - {new_rate}'}
                return web.Response(text=json.dumps(response_obj), status=200)
            response_obj = {'message': f'exchange rate for pair {pair} updated successfully to {new_rate}'}
            return web.Response(text=json.dumps(response_obj), status=200)
        except KeyError as e:
            raise web.HTTPUnprocessableEntity(reason=f"Field {e} is required")
        except ValidationError as e:
            raise web.HTTPUnprocessableEntity(reason=e.json())
        except ValueError as e:
            raise web.HTTPUnprocessableEntity(reason=str(e))
