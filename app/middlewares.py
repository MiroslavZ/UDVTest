from aiohttp import web


@web.middleware
async def error_middleware(request: web.Request, handler):
    try:
        response = await handler(request)
        if response.status == 200:
            return response
        message = response.message
        status = 200
    except web.HTTPException as ex:
        message = ex.reason
        status = ex.status
    return web.Response(text=message, status=status)

