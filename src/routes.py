# Copyright 2022 StreamX Developers

# Modules
import logging
from src import app
from aiohttp import web

# Initialization
def mkresp(code: int, data: dict = {}) -> web.Response:
    return web.json_response({"code": code} | data)

log = logging.getLogger("rich")
routes = web.RouteTableDef()

# Routes
@routes.get("/")
async def index(req) -> web.Response:
    return mkresp(200, {"message": "OK"})

@routes.post("/activate")
async def activate(req) -> web.Response:
    return mkresp(200, {"message": "NOT COMPLETE"})

app.add_routes(routes)
