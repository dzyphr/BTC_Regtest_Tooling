#!/bin/bash


# Desired number of arguments
REQUIRED_ARGS=3

# Check the number of arguments
if [ "$#" -ne "$REQUIRED_ARGS" ]; then
    # Display usage message
    echo "Usage: $0 sendFromWalletName targetLndDirectoryName amountToSend"
    exit 1
fi

python3 main.py sendToLNDDir $1 $2 $3
