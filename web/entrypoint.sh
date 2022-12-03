#!/usr/bin/env bash

set -e

npm run css-build

exec "$@"
