# Copyright 2022 StreamX Developers

# Modules
import os
import logging
from aiohttp import web
from redis import Redis, exceptions
from rich.logging import RichHandler

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

# Relative path generator
topdir = os.path.dirname(os.path.dirname(__file__))
app.rpath = lambda p: os.path.abspath(os.path.join(topdir, p))  # noqa

# Launch redis
log.info("Connecting to redis, please wait ...")
try:
    app.redis = Redis("127.0.0.1", socket_connect_timeout = 2)
    app.redis.ping()
    log.info("Connected to 127.0.0.1!")

except exceptions.ConnectionError:
    log.error("FAILED to connect to Redis! Is it running?")
    exit(1)

# Load routes
import src.routes  # noqa
