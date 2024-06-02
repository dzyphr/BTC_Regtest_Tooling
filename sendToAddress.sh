#!/bin/bash


# Desired number of arguments
REQUIRED_ARGS=3

# Check the number of arguments
if [ "$#" -ne "$REQUIRED_ARGS" ]; then
    # Display usage message
    echo "Usage: $0 rpcwallet targetAddress numberOfCoinsToSend"
    exit 1
fi


#-rpcwallet=$walletname

export REGTEST_DIR=$(pwd)
rpcwallet=$1
targetAddress=$2
numberOfCoinsToSend=$3
sendtoaddress(){
	export clipath="$REGTEST_DIR/bitcoin/src/bitcoin-cli"
	cmd="$clipath -datadir="$REGTEST_DIR" -rpcwallet=$rpcwallet   sendtoaddress    $targetAddress $numberOfCoinsToSend  "
#	echo $cmd
	$cmd
}

sendtoaddress
