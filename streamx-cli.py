# Copyright 2022 StreamX Developers
# This script is very primitive, because the backend handles most errors

# Modules
import os
import shlex
import requests
from datetime import timedelta, date
try:
    from rich import print

except ImportError:
    pass  # Rich is nice, but not required

# Initialization
__version__ = "1.0.3"
print(f"StreamX Payment CLI v{__version__}\nCopyright (c) 2022 StreamX Developers\n")

# Fetch URL + API key
base_url = input("StreamX Purchase Server URI (quantumpython.xyz): ") or "https://streamxpayment.quantumpython.xyz"
apikeys = [f for f in os.listdir() if ".pem" in f] + (["db/server.pem"] if os.path.isfile("db/server.pem") else [])
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
    ~     activate <userid>       -- Activate/reactivate a user's API status
    ~     info <userid>           -- Shows information on a user
    ~     exit                    -- Exits the CLI
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

    print(make_request("/delete", method = "post", data = {"userid": a[0]}))

def function_info(a: list) -> None:
    if not a:
        return print("[red]\\[streamx]: missing argument <userid>[/]")

    print(make_request(f"/info/{a[0]}"))

def function_activate(a: list) -> None:
    try:
        if not a:
            return print("[red]\\[streamx]: missing argument <userid>[/]")

        opt, username = int(input("Activate (1) or reactivate (2)? ")), ""
        if opt not in [1, 2]:
            return print("[red]\\[streamx]: invalid option[/]")

        elif opt != 2:
            username = input("Roblox Username: ")

        expires = int((date.today() + timedelta(days = int(input("Expires in (days from now): ")))).strftime("%s"))
        print(make_request("/activate", method = "post", data = {
            "userid": a[0], "username": username, "expires": expires
        }))

    except ValueError:
        return print("[red]\\[streamx]: invalid option[/]")

commands = {
    "help": function_help,
    "get-active": function_active,
    "is-active": function_isactive,
    "delete": function_delete,
    "activate": function_activate,
    "info": function_info,
    "exit": lambda *a: exit()
}

# Actual CLI
print("\nWelcome to the StreamX Payment System.")
print("Type 'help' for a list of commands.\n")
while True:
    try:
        data = shlex.split(input("SX >> "))
        if not data:
            continue

        elif data[0] not in commands:
            print("[red]\\[streamx]: invalid command[/]")
            continue

        commands[data[0]](data[1:])

    except KeyboardInterrupt:
        print()

    except Exception as e:
        print(f"[red]\\[streamx]: internal error: {e}[/]")
