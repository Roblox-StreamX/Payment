# Copyright 2022 StreamX Developers
# This script is very primitive, because the backend handles most errors

# Modules
import os
import json
import shlex
import requests
try:
    from rich import print

except ImportError:
    pass  # Rich is nice, but not required

# Initialization
__version__ = "1.0.5"
print(f"StreamX Payment CLI v{__version__}\nCopyright (c) 2022 StreamX Developers\n")

# Fetch URL + API key
base_url = input("StreamX Purchase Server URI (quantumpython.xyz): ") or "https://streamxpayment.quantumpython.xyz"
streamx_jsonfile = os.path.abspath(os.path.join(os.path.dirname(__file__), ".streamx.json"))
if os.path.isfile(streamx_jsonfile):
    with open(streamx_jsonfile, "r") as fh:
        data = json.loads(fh.read())

    authkey = data["authkey"]

else:
    authkey = input("StreamX Authentication Key: ")
    if (input("Save these credentials (y/N)? ") or "n").lower() == "y":
        with open(streamx_jsonfile, "w+") as fh:
            fh.write(json.dumps({"authkey": authkey}))

def make_request(endpoint: str, method: str = "get", js: bool = True, **kwargs) -> dict:
    d = {
        "get": requests.get,
        "post": requests.post
    }[method](f"{base_url.rstrip('/')}{endpoint}", headers = {
        "X-StreamX-Token": authkey
    }, **kwargs)
    try:
        return d.json() if js else d

    except json.JSONDecodeError as e:
        print(f"[red]\\[streamx]: {d.text()}[/]")
        raise e

# Test connection first
try:
    r = make_request("/", js = False)
    if r.status_code != 200:
        raise Exception

    os.system("cls" if os.name == "nt" else "clear")
    print("-+-+-+-+-+- Connected to StreamX -+-+-+-+-+-")

except Exception:
    exit("Failed to connect to Purchase Server; check API key.")

# Command handlers
def function_help(a: list) -> None:
    msg = "\n".join(x.split("~ ")[1] for x in """
    ~ Commands
    ~     help                    -- Shows this message
    ~     active <key>            -- Checks if an API key is valid
    ~     delete <userid>         -- Removes all stored data about a user
    ~     activate <userid>       -- Activate/reactivate a user's API status
    ~     info <userid>           -- Shows information on a user
    ~     apikeys <userid>        -- Fetch all API keys of a user
    ~     invalidate <userid>     -- Invalidates a user's API key
    ~     whitelist <uid> <gid>   -- Adds a game to a user's whitelist
    ~     dewhitelist <uid> <gid> -- Removes a game from a user's whitelist
    ~     clear                   -- Clears the screen
    ~     exit                    -- Exits the CLI
    """.split("\n") if x.strip())
    return print(msg)

def function_active(a: list) -> None:
    if not a:
        return print("[red]\\[streamx]: missing argument <key>[/]")

    print(make_request(f"/active/{a[0]}"))

def function_delete(a: list) -> None:
    if not a:
        return print("[red]\\[streamx]: missing argument <userid>[/]")

    print(make_request("/delete", method = "post", json = {"userid": a[0]}))

def function_info(a: list) -> None:
    if not a:
        return print("[red]\\[streamx]: missing argument <userid>[/]")

    print(make_request(f"/info/{a[0]}"))

def function_apikeys(a: list) -> None:
    if not a:
        return print("[red]\\[streamx]: missing argument <userid>[/]")

    print(make_request(f"/info/{a[0]}")["apikeys"])

def function_invalidate(a: list) -> None:
    if not a:
        return print("[red]\\[streamx]: missing argument <key>[/]")

    try:
        reason = input("Invalidation reason (abuse/regen): ")
        print(make_request("/invalidate", method = "post", json = {"userid": int(a[0]), "reason": reason}))

    except ValueError:
        return print("[red]\\[streamx]: invalid userid[/]")

def function_activate(a: list) -> None:
    try:
        if not a:
            return print("[red]\\[streamx]: missing argument <userid>[/]")

        opt, username = int(input("Activate (1) or extend quota (2)? ")), ""
        if opt not in [1, 2]:
            return print("[red]\\[streamx]: invalid option[/]")

        elif opt != 2:
            username = input("Roblox Username: ")

        expires = int(input("Quota length (days): "))
        print(make_request("/activate", method = "post", json = {
            "userid": a[0], "username": username, "expires": expires
        }))

    except ValueError:
        return print("[red]\\[streamx]: invalid option[/]")

def function_whitelist(a: list) -> None:
    print(make_request("/whitelist/add", method = "post", json = {"userid": a[0], "gameid": a[1]}))

def function_dewhitelist(a: list) -> None:
    print(make_request("/whitelist/delete", method = "post", json = {"userid": a[0], "gameid": a[1]}))

def function_clear(a: list) -> None:
    os.system("clear" if os.name != "nt" else "cls")

commands = {k.split("_")[1]: v for k, v in globals().items() if k.startswith("function_")} | {
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
