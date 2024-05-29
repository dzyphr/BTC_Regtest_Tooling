# BTC_Regtest_Tooling


Basic Usage:
1. Generate a config file: `./generateBitcoinConf.sh`
2. Download Build and Install Core: `./downloadBuildAndInstallBitcoinCore.sh`
3. Create a regtest bash alias: `./createBashAlias.sh'
4. Create a wallet: `./createWallet.sh <yourwalletnamehere>`
5. Start the Regtest Daemon: `btcregtestd` (Make any wallet you want to use before starting the Daemon) 
(If you used a custom bash alies different from btcregtest ie `yourcustomalias` the command will be `yourcustomaliasd`)
6. Load your wallet: `./loadWallet.sh <yourwalletnamehere>`
