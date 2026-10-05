#!/bin/sh
cd "/home/eamon/Strata"
exec "/home/eamon/Strata/.venv/bin/python" "/home/eamon/Strata/serve/server.py" "--engine" "strata" "--config" "/home/eamon/Strata/strata-iq3_s.json" "--port" "8080" "--open"
