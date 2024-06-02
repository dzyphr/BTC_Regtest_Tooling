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
17. Connect your local LND Instances by their Directory name: `./connectLocalLNDDir.sh <lndDirName> <targetLndDirName>` 
18. Check that your connection worked by checking your node's peers: `./LNDPeers.sh <lndDirName>`
19. Open a channel between your two LND instances by their directory name: `./openChannelLNDDir.sh <lndDirName> <targetLndDirName> <channelAmount>`
20. Check the existing channels on the node: `./listChannelsLND.sh <lndDirName>`
21. Create an invoice: `./invoiceLND.sh <lndDirectoryName> <invoiceAmount>` Will return a `pay_req` string that you can copy
(If you opened only one channel from lnd to lnd2 for example, create the invoice with lnd2 and pay with lnd.)
22. Pay the invoice: `./payinvoiceLND.sh <lndDirectoryName> <pay_req>` 

