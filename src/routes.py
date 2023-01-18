# Copyright 2022 StreamX Developers

# Modules
import logging
import secrets
from src import app
from typing import Any
from aiohttp import web

# Initialization
def mkresp(code: int, data: dict = {}) -> web.Response:
    return web.json_response({"code": code} | data, status = code)

log, routes = logging.getLogger("rich"), web.RouteTableDef()

# Fetch server API key
streamx_token = app.db["authkey"].find_one()
if streamx_token is None:
    streamx_token = secrets.token_urlsafe(64)
    app.db["authkey"].insert_one({"key": streamx_token})

else:
    streamx_token = streamx_token["key"]

log.info(f"StreamX Authentication key is:\n{streamx_token}")

# Authentication
@web.middleware
async def authentication_handler(req: web.Request, handler: Any) -> web.Response:
    token = req.headers.get("X-StreamX-Token")
    if (token != streamx_token) and req.path != "/":
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
        data = app.db["data"].find_one({"userid": int(req.match_info["userid"])})
        if not data:
            return mkresp(404, {"message": "No information available."})

        data = dict(data)
        del data["_id"]  # Stop ObjectId class from hitting the JSON serializer
        return mkresp(200, data)

    except ValueError:
        return mkresp(400, {"message": "Invalid Roblox user ID provided."})

@routes.get("/active/{key}")
async def check_active_key(req) -> web.Response:
    try:
        user = app.db["data"].find_one({"apikeys": {"key": req.match_info["key"], "reason": None}})
        if user is None:
            return mkresp(200, {"active": False})

        return mkresp(200, {"active": user["quota"] > 0})

    except KeyError:
        return mkresp(400, {"message": "Missing API key."})

@routes.post("/delete")
async def delete_api_key(req) -> web.Response:
    try:
        d = await req.json()
        success = app.db["data"].delete_one({"userid": int(d["userid"])})
        if success:
            return mkresp(200, {"message": "OK"})

        return mkresp(404, {"message": f"No records exist for user {d['userid']}."})

    except KeyError:
        return mkresp(400, {"message": "Missing user ID."})

    except ValueError:
        return mkresp(400, {"message": "Invalid Roblox user ID provided."})

@routes.post("/invalidate")
async def invalidate(req) -> web.Response:
    try:
        d = await req.json()
        userid, reason = int(d["userid"]), d["reason"]

        # Invalidate current API key
        user_data = app.db["data"].find_one({"userid": userid})
        if user_data is None:
            return mkresp(400, {"message": f"No records exist for user {d['userid']}."})

        for k in user_data["apikeys"]:
            if k["reason"] is None:
                app.db["data"].update_one({"apikeys.key": k["key"]}, {"$set": {"apikeys.$.reason": reason}})

        # Generate a new API key
        apikey = secrets.token_urlsafe(64)
        app.db["data"].update_one(
            {"userid": user_data["userid"]},
            {"$push": {"apikeys": {"key": apikey, "reason": None}}}
        )
        return mkresp(200, {"message": "OK", "apikey": apikey})

    except KeyError:
        return mkresp(400, {"message": "Missing one (or multiple) of required fields: userid, reason."})

    except ValueError:
        return mkresp(400, {"message": "Invalid Roblox user ID provided."})

@routes.post("/whitelist/add")
async def whitelist_add(req) -> web.Response:
    try:
        d = await req.json()
        userid, gameid = int(d["userid"]), int(d["gameid"])
        user_data = app.db["data"].find_one({"userid": userid})
        if user_data is None:
            return mkresp(400, {"message": f"No records exist for user {d['userid']}."})

        app.db["data"].update_one({"userid": userid}, {"$push": {"whitelist": gameid}})
        return mkresp(200, {"message": "OK"})

    except KeyError:
        return mkresp(400, {"message": "Missing one (or multiple) of required fields: userid, gameid."})

    except ValueError:
        return mkresp(400, {"message": "Invalid Roblox User ID or Game ID provided."})

@routes.post("/whitelist/delete")
async def whitelist_delete(req) -> web.Response:
    try:
        d = await req.json()
        userid, gameid = int(d["userid"]), int(d["gameid"])
        user_data = app.db["data"].find_one({"userid": userid})
        if user_data is None:
            return mkresp(400, {"message": f"No records exist for user {d['userid']}."})

        app.db["data"].update_one({"userid": userid}, {"$pull": {"whitelist": gameid}})
        return mkresp(200, {"message": "OK"})

    except KeyError:
        return mkresp(400, {"message": "Missing one (or multiple) of required fields: userid, gameid."})

    except ValueError:
        return mkresp(400, {"message": "Invalid Roblox User ID or Game ID provided."})

@routes.post("/activate")
async def activate(req) -> web.Response:
    try:
        d = await req.json()
        userid, username, expires = int(d["userid"]), d["username"], int(d["expires"])

        # Renew existing subscription
        user_data = app.db["data"].find_one({"userid": userid})
        if user_data is not None:
            quota = user_data["quota"]
            app.db["data"].update_one({"userid": userid}, {"$set": {"quota": quota + expires}})
            return mkresp(200, {"message": "Successfully extended quota", "old": quota, "new": quota + expires})

        # Create new subscription
        apikey = secrets.token_urlsafe(64)
        app.db["data"].insert_one({
            "userid": userid, "username": username, "quota": expires,
            "apikeys": [{"key": apikey, "reason": None}],
            "whitelist": [],
            "lastusage": None
        })
        return mkresp(200, {"message": "OK", "apikey": apikey, "quota": expires})

    except KeyError:
        return mkresp(400, {"message": "Missing one (or multiple) of required fields: userid, username, expires."})

    except ValueError:
        return mkresp(400, {"message": "Invalid Roblox user ID or quota value provided."})

app.add_routes(routes)
