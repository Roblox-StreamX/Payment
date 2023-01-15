# Copyright 2022 StreamX Developers

# Modules
import os
import logging
from aiohttp import web
from rich.logging import RichHandler
from pymongo import MongoClient, errors
from urllib.parse import quote_plus as qp

from .config import config

# Setup logging
logging.basicConfig(
    level = "INFO",
    format = "%(message)s",
    datefmt = "[%X]",
    handlers = [RichHandler()]
)
log = logging.getLogger("rich")
log.info("StreamX Payment Backend is now starting ...")

# Initialization
app = web.Application()

# Connect to MongoDB
log.info("Connecting to MongoDB, please wait ...")
try:
    user, pasw = config["mongo"].get("username", ""), config["mongo"].get("password", "")
    authstr = f"{qp(user)}:{qp(pasw)}@" if (user.strip() and pasw.strip()) else ""
    app.mongo = MongoClient(
        f"mongodb://{authstr}{config['mongo']['address']}",
        serverSelectionTimeoutMS = 1000  # ms
    )
    try:
        app.mongo.server_info()

    except errors.ServerSelectionTimeoutError:
        log.error("FAILED to connect to MongoDB! Check MONGO* env and database status.")
        exit(1)

    app.db = app.mongo["purchases"]  # Reference the "purchases" database

except ValueError:
    log.error("FAILED to read environment variables! Check MONGO_PORT and ensure it's an integer.")
    exit(1)

# Load routes
import src.routes  # noqa
