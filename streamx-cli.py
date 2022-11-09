# Copyright 2022 StreamX Developers
# This script is very primitive, because the backend handles most errors

# Modules
import os
import shlex
import requests
try:
    from rich import print

except ImportError:
    pass  # Rich is nice, but not required

# Initialization
__version__ = "1.0.2"
print(f"StreamX Payment CLI v{__version__}\nCopyright (c) 2022 StreamX Developers\n")

# Fetch URL + API key
base_url = input("StreamX Purchase Server URI (quantumpython.xyz): ") or "https://streamxpayment.quantumpython.xyz"
apikeys = [f for f in os.listdir() if ".pem" in f]
if not apikeys:
    api_key = input("StreamX API Key: ")

else:
    with open(apikeys[0], "r") as fh:
        api_key = fh.read().strip("\n")

def make_request(endpoint: str, method: str = "get", js: bool = True, **kwargs) -> dict:
    d = {
        "get": requests.get,
        "post": requests.post
    }[method](f"{base_url.rstrip('/')}{endpoint}", headers = {
        "X-StreamX-Token": api_key
    }, **kwargs)
    return d.json() if js else d

# Test connection first
try:
    r = make_request("/", js = False)
    if r.status_code != 200:
        raise Exception

    os.system("cls" if os.name == "nt" else "clear")
    print("... Connected to StreamX ...")

except Exception:
    exit("Failed to connect to Purchase Server; check API key.")

# Command handlers
def function_help(a: list) -> None:
    msg = "\n".join(x.split("~ ")[1] for x in """
    ~ Commands
    ~     help                    -- Shows this message
    ~     get-active              -- Lists all active API keys
    ~     is-active <key>         -- Checks if an API key is valid
    ~     delete <userid>         -- Removes a user and their API key
    ~     info <userid>           -- Shows information on a user
    """.split("\n") if x.strip())
    return print(msg)

def function_active(a: list) -> None:
    print(make_request("/active"))

def function_isactive(a: list) -> None:
    if not a:
        return print("[red]\\[streamx]: missing argument <key>[/]")

    print(make_request(f"/active/{a[0]}"))

def function_delete(a: list) -> None:
    if not a:
        return print("[red]\\[streamx]: missing argument <userid>[/]")

    make_request("/delete", method = "post", data = {"userid": a[0]})

def function_info(a: list) -> None:
    if not a:
        return print("[red]\\[streamx]: missing argument <userid>[/]")

    print(make_request(f"/info/{a[0]}"))

commands = {
    "help": function_help,
    "get-active": function_active,
    "is-active": function_isactive,
    "delete": function_delete,
    "info": function_info
}

# Actual CLI
print("\nWelcome to the StreamX Payment System.")
print("Type 'help' for a list of commands.\n")
while True:
    try:
        data = shlex.split(input("SX >> "))
        if data[0] not in commands:
            print("[red]\\[streamx]: invalid command[/]")
            continue

        commands[data[0]](data[1:])

    except KeyboardInterrupt:
        break
