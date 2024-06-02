#!/bin/bash


# Desired number of arguments
REQUIRED_ARGS=3

# Check the number of arguments
if [ "$#" -ne "$REQUIRED_ARGS" ]; then
    # Display usage message
    echo "Usage: $0 lndDirectoryName targetLndDirectoryName channelAmount"
    exit 1
fi

python3 main.py openchannel_lnddir $1 $2 $3
