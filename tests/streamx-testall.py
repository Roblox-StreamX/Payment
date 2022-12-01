# Copyright 2022 iiPython

# Modules
import os
import json
from requests import post, get
try:
    from rich import print

except ImportError:
    pass

# Initialization
root_url = "http://localhost:8080"
if os.path.isfile("../.streamx.json"):
    with open("../.streamx.json", "r") as fh:
        data = json.loads(fh.read())

    authkey = data["authkey"]

else:
    authkey = input("StreamX Authentication Key: ")

# Handlers
def tasklog(task: int, text: str) -> None:
    return print(f"[Task {task}]:", text)

def do_assert(tid: str, task: str, meth: str, ep: str, expect_code: int, **kwargs) -> None:
    tasklog(tid, task)
    req = {"get": get, "post": post}[meth](root_url + ep, headers = {"X-StreamX-Token": authkey}, **kwargs)
    try:
        tasklog(tid, req.json())

    except json.JSONDecodeError:
        tasklog(tid, req.text)

    tasklog(tid, "[green]** Passed test! **[/]" if req.status_code == expect_code else "[red]** Failed test! **[/]")

# Launch tests
do_assert(
    1,
    "Creating new StreamX account (expires 31 days, userid 2, username 'STX Testing') ...",
    "post",
    "/activate",
    200,
    json = {"userid": 2, "username": "STX Testing", "expires": 31}
)
do_assert(
    2,
    "Renewing account for another 31 days ...",
    "post",
    "/activate",
    200,
    json = {"userid": 2, "username": "STX Testing", "expires": 31}
)
do_assert(3, "Fetching account info ...", "get", "/info/2", 200)
do_assert(4, "Invalidating API key for abuse ...", "post", "/invalidate", 200, json = {
    "userid": 2,
    "reason": "abuse"
})
do_assert(5, "Fetching account info ...", "get", "/info/2", 200)
do_assert(6, "Invalidating API key for regen ...", "post", "/invalidate", 200, json = {
    "userid": 2,
    "reason": "regen"
})
do_assert(7, "Fetching account info ...", "get", "/info/2", 200)
do_assert(8, "Deleting StreamX account ...", "post", "/delete", 200, json = {"userid": 2})
