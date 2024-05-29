#!/bin/bash


export REGTEST_DIR=$(pwd)
walletname=$1
loadWallet(){
	export clipath="$REGTEST_DIR/bitcoin/src/bitcoin-cli"
	$clipath -datadir="$REGTEST_DIR" loadwallet $walletname
}

loadWallet
