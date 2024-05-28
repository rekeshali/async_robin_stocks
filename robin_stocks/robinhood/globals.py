"""Holds the session header and other global variables."""
import sys
import os
import aiohttp

# Keeps track on if the user is logged in or not.
LOGGED_IN = False

# Headers for the session
HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br",
    "Accept-Language": "en-US,en;q=1",
    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    "X-Robinhood-API-Version": "1.431.4",
    "Connection": "keep-alive",
    "User-Agent": "*"
}

# The session object for making get and post requests.
SESSION = aiohttp.ClientSession()

# All print() statement direct their output to this stream
# by default, we use stdout which is the existing behavior
# but a client can change to any normal Python stream that
# print() accepts.  Common options are
# sys.stderr for standard error
# open(os.devnull,"w") for dev null
# io.StringIO() to go to a string for the client to inspect
OUTPUT = sys.stdout