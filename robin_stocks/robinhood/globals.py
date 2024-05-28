"""Holds the global variables."""
import sys
import os
import aiohttp

# All print() statement direct their output to this stream
# by default, we use stdout which is the existing behavior
# but a client can change to any normal Python stream that
# print() accepts.  Common options are
# sys.stderr for standard error
# open(os.devnull,"w") for dev null
# io.StringIO() to go to a string for the client to inspect
OUTPUT = sys.stdout