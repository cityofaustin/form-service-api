import os, sys, inspect, re

# source env file from /src directory
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
import env

# Print which environment variables from 'src/env.py' that your app will use.
# Don't print sensitive env variables ["S3_KEY", "S3_SECRET"]
for m in inspect.getmembers(env):
    name = m[0]
    val = m[1]
    if (
        (isinstance(val, str) or val is None)
        and (not re.match("^__", name))
        and (name not in ["S3_KEY", "S3_SECRET"])
    ):
        print(f"{m[0]}: [{m[1]}]")
