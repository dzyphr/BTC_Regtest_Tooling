#!/bin/bash

# Desired number of arguments
REQUIRED_ARGS=1

# Check the number of arguments
if [ "$#" -eq "$REQUIRED_ARGS" ]; then
        continue
else
    # Display usage message
    echo "Usage: $0 yourWalletNameHere"
    exit 1
fi


export REGTEST_DIR=$(pwd)
walletname=$1
loadWallet(){
	export clipath="$REGTEST_DIR/bitcoin/src/bitcoin-cli"
	$clipath -datadir="$REGTEST_DIR" loadwallet $walletname
}

loadWallet
