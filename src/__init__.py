# Copyright 2022 StreamX Developers

# Modules
import logging
from aiohttp import web
from rich.logging import RichHandler

# Setup logging=
logging.basicConfig(
    level = "INFO",
    format = "%(message)s",
    datefmt = "[%X]",
    handlers = [RichHandler()]
)

# Initialization
app = web.Application()

# Load routes
import src.routes  # noqa
