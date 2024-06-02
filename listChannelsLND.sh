#!/bin/bash


# Desired number of arguments
REQUIRED_ARGS=1

# Check the number of arguments
if [ "$#" -ne "$REQUIRED_ARGS" ]; then
    # Display usage message
    echo "Usage: $0 lndDirectoryName"
    exit 1
fi

python3 main.py lndChannels  $1
