# BTC_Regtest_Tooling

### NOTE: Currently only tested on Ubuntu Linux

Regtest + Lightning Test Environment Tooling

Inspired by: https://medium.com/@bitstein/setting-up-a-bitcoin-lightning-network-test-environment-ab967167594a
Updated for usage with newest Bitcoin client releases.

Basic Usage:
1. Generate a config file: `./generateBitcoinConf.sh`
2. Download Build and Install Core: `./downloadBuildAndInstallBitcoinCore.sh`
3. Create a regtest bash alias: `. ./createBashAlias.sh` (Ensure to run with `.` before sh file to load bash aliases immediately)
4. Create a wallet: `./createWallet.sh <yourWalletNameHere>`
5. Start the Regtest Daemon: `btcregtestd` (Make any wallet you want to use before starting the Daemon) 
(If you used a custom bash alias different from btcregtest ie `yourCustomAlias` the command will be `yourCustomAliasd`)
6. Load your wallet: `./loadWallet.sh <yourWalletNameHere>`
7. Generate some blocks with your wallet: `./generate.sh <yourWalletNameHere> <numberOfBlocksToGenerate>`
8. Generate at least 100 more blocks to make the previous blocks spendable: `./generate.sh <yourWalletNameHere> 101`
9. Check your wallet's balance: `./getBalance.sh <yourWalletNameHere>` 
10. Download, Build, and Install LND: `./downloadBuildAndInstallLND.sh`
11. Create a Directory for a lightning node( or multiple ): 

Default Node Example: `./createLightningNodeDirAndConf.sh`

Custom Port Node Example: 
`./createLightningNodeDirAndConf.sh 9734 11009 8180`

12. Create a LND bash alias: `. ./createBashAlias_lnd.sh <yourLndDirectoryNameHere>` 
(Ensure to run with `.` before sh file to load bash aliases immediately)
13. Launch LND: `./launchLND.sh <lndDirName>`
14. Create a LND wallet: `createLNDWallet.sh <lndDirName>`
Follow the instructions provided by LND, save the seed phrase if you will ever want to recover the wallet.
15. (If you already created a LND wallet) Unlock LND: `./unlockLND.sh <lndDirName>` 
16. Get info about your LND Node: `./getInfoLND.sh <lndDirName>`
Saves an `identity_pubkey` file in your node directory.
Needed for connecting nodes to eachother. 

