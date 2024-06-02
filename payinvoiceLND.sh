#!/bin/bash


# Desired number of arguments
REQUIRED_ARGS=2

# Check the number of arguments
if [ "$#" -ne "$REQUIRED_ARGS" ]; then
    # Display usage message
    echo "Usage: $0 lndDirectoryName pay_req"
    exit 1
fi

python3 main.py payinvoiceLND $1 $2
