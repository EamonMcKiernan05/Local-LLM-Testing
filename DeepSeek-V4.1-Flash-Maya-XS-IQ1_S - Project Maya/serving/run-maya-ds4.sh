#!/bin/sh
# starts the Project Maya dashboard and API (written by maya.py; ./maya.sh does the same)
cd /home/eamon/project-maya || exit 1
exec /home/eamon/project-maya/.venv/bin/python /home/eamon/project-maya/maya.py --config /home/eamon/project-maya/maya-ds4.json --port 8080 "$@"
