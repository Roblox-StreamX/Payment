# Copyright 2022 StreamX Developers

# Modules
import os
import time
import logging
import secrets
from src import app
from typing import Any
from aiohttp import web

# Initialization
def mkresp(code: int, data: dict = {}) -> web.Response:
    return web.json_response({"code": code} | data, status = code)

log, routes = logging.getLogger("rich"), web.RouteTableDef()

# Load server.pem
serverpem = app.rpath("db/server.pem")
if not os.path.isfile(serverpem):
    with open(serverpem, "w+") as fh:
        fh.write(secrets.token_urlsafe(256))

with open(serverpem, "r") as fh:
    streamx_token = fh.read()

log.info(f"StreamX API key is {streamx_token}")

# Helpers
def sanitize_userid(text: str) -> str:
    d = int(text)
    if d > (10 ** 10) or d < 1:
        raise ValueError

    return f"user:{text}"

def generate_apikey() -> str:
    return secrets.token_urlsafe(64)

# Authentication
@web.middleware
async def authentication_handler(req: web.Request, handler: Any) -> web.Response:
    token = req.headers.get("X-StreamX-Token")
    if token != streamx_token:
        return mkresp(401, {"message": "Unauthorized"})

    return await handler(req)

app.middlewares.append(authentication_handler)

# Routes
@routes.get("/")
async def index(req) -> web.Response:
    return mkresp(200, {"message": "OK"})

@routes.get("/info/{userid}")
async def get_customer_info(req) -> web.Response:
    try:
        data = app.redis.hgetall(sanitize_userid(req.match_info["userid"]))
        if not data:
            return mkresp(404, {"message": "No information available."})

        return mkresp(200, data)

    except ValueError:
        return mkresp(400, {"message": "Invalid Roblox user ID provided."})

@routes.get("/active")
async def get_active_keys(req) -> web.Response:
    return mkresp(200, {"keys": list(app.redis.smembers("apikeys"))})

@routes.get("/active/{key}")
async def check_active_key(req) -> web.Response:
    try:
        k = f"apikey:{req.match_info['key']}"
        if not app.redis.exists(k):
            return mkresp(200, {"active": False})

        expires = app.redis.hget(app.redis.get(k), "expires")
        return mkresp(200, {"active": float(expires) < time.time()})

    except KeyError:
        return mkresp(400, {"message": "Missing API key."})

@routes.post("/delete")
async def delete_api_key(req) -> web.Response:
    try:
        userid = sanitize_userid((await req.post())["userid"])
        if not app.redis.exists(userid):
            return mkresp(404, {"message": "Unknown user ID."})

        # Fetch API key
        apikey = app.redis.hget(userid, "apikey")

        # Handle deletion
        app.redis.delete(userid)
        app.redis.delete(f"apikey:{apikey}")
        app.redis.srem("apikeys", apikey)
        return mkresp(200, {"message": "OK"})

    except ValueError:
        return mkresp(400, {"message": "Invalid Roblox user ID provided."})

@routes.post("/activate")
async def activate(req) -> web.Response:
    try:
        d = await req.post()
        if not d:
            d = await req.json()

        userid, username, expires = sanitize_userid(d["userid"]), d["username"], d["expires"]

        # Renew existing subscription
        user_expired = app.redis.hget(userid, "expires")
        if user_expired is not None:
            app.redis.hset(userid, "expires", expires)
            return mkresp(200, {"message": "Subscription renewed.", "expires": expires})

        # Create new subscription
        apikey = generate_apikey()
        app.redis.set(f"apikey:{apikey}", userid)
        app.redis.sadd("apikeys", apikey)
        app.redis.hset(userid, mapping = {"username": username, "expires": expires, "apikey": apikey})
        return mkresp(200, {"message": "OK", "apikey": apikey})

    except KeyError:
        return mkresp(400, {"message": "Required fields: userid, username, expires."})

    except ValueError:
        return mkresp(400, {"message": "Invalid Roblox user ID provided."})

app.add_routes(routes)
