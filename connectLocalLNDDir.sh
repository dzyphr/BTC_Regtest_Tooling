#!/bin/bash


# Desired number of arguments
REQUIRED_ARGS=2

# Check the number of arguments
if [ "$#" -ne "$REQUIRED_ARGS" ]; then
    # Display usage message
    echo "Usage: $0 lndDirectoryName targetLndDirectoryName"
    exit 1
fi

python3 main.py connect_localDir_lnd $1 $2
