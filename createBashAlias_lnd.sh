#!/bin/bash

# Check the number of arguments
if [ "$#" -ne 1 ]; then
    # Display usage message
    echo "Usage: $0  or $0 <lndDirectoryName> "
    exit 1
fi

python3 main.py createBashAlias_lnd $1 

. ./refresh_profile.sh
