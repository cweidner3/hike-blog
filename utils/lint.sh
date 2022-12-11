#!/usr/bin/env bash

DEST_DIR="${1:-.}"
OUTFILE="$DEST_DIR/results.txt"

if [[ -f $DEST_DIR ]]; then
    echo "Error: Provided destination is a file" >&2
    exit 1
fi
if [[ ! -d $DEST_DIR ]]; then
    echo "Error: Cannot find destination path '$DEST_DIR'" >&2
    exit 1
fi

cd "$(dirname "$0")/.."

find api \
    -type f \
    -iname '*.py' \
    -exec \
        pylint \
        --output "${OUTFILE}" \
        --exit-zero \
        {} +
echo $?
echo ""
cat results.txt
