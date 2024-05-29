#!/bin/bash

# Check the number of arguments
if [ "$#" -ne 0 ] && [  "$#" -ne 3 ]; then
    # Display usage message
    echo "Usage: $0  or $0 <altListenPort> <altRpcListenPort> <altRestListenPort> "
    exit 1
fi

python3 main.py createLightningNodeDirAndConf $1 $2 $3
