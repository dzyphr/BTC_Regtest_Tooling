#!/bin/bash


export REGTEST_DIR=$(pwd)
walletname=$1
createWallet(){
	export clipath="$REGTEST_DIR/bitcoin/src/bitcoin-cli"
	$clipath -datadir="$REGTEST_DIR" createwallet $walletname
}

createWallet
