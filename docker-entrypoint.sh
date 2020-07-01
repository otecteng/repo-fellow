#! /bin/bash -eu
set -e

if [ $# -gt 0 ] && [[ "$1" =~ \/bin* ]]; then
    exec "$@"
else
    exec python3 -m repofellow "$@"
fi