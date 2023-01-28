#!/bin/sh

env >> environment

# execute CMD
echo "$@"
exec "$@"
