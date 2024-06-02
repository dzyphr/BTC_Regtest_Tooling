import secrets, string, file_tools, sys, os, subprocess, re, json, hmac, hashlib, time, random
from secrets import token_hex, token_urlsafe

def generate_salt(size):
    """Create size byte hex salt"""
    return token_hex(size)

def generate_password():
    """Create 32 byte b64 password"""
    return token_urlsafe(32)

def password_to_hmac(salt, password):
    m = hmac.new(salt.encode('utf-8'), password.encode('utf-8'), 'SHA256')
    return m.hexdigest()

def remove_digits(input_string):
    return re.sub(r'\d+', '', input_string)

def check_go_installed():
    try:
        # Run the `go version` command and capture the output
        result = subprocess.run(['go', 'version'], capture_output=True, text=True)
        # Check if the command was successful (return code 0)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "Go is not installed."
    except FileNotFoundError:
        return False, "Go is not installed."

def downloadBuildAndInstallLND(platform="Linux_x86-64"):
    if platform == "Linux_x86-64":
        goinstalled, version = check_go_installed()
        if goinstalled == False:
            print(os.popen("wget  https://go.dev/dl/go1.22.3.linux-amd64.tar.gz").read())
            print(os.popen("sudo tar -C /usr/local -xzf go1.22.3.linux-amd64.tar.gz").read())
            file_path = os.path.expanduser("~/.bashrc")
            EnvVars = \
                    "export PATH=$PATH:/usr/local/go/bin\n" + \
                    "export GOPATH=~/go\n" + \
                    "export PATH=$PATH:$GOPATH/bin\n"
            with open(file_path, "a") as file:
                file.write(EnvVars)
            output = subprocess.run(
                ["bash", "-i", "-c", "source ~/.bashrc && alias"],
                capture_output=True,
                text=True
            )
            print(output.stdout)
            print(os.popen("go version").read())
        print(os.popen("git clone https://github.com/lightningnetwork/lnd lnd_repo").read())
        print(os.popen("cd lnd_repo && git checkout v0.17.4-beta && make install").read())
        print(os.popen("echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc").read()) 
        output = subprocess.run(
            ["bash", "-i", "-c", "source ~/.bashrc && alias"],
            capture_output=True,
            text=True
        )
        print(output.stdout)
        print(os.popen("lnd --version").read())
        
    else:
        print("unsupported platform:", platform)

def downloadBuildAndInstallBitcoinCore(platform="ubuntu"):
    if platform == "ubuntu":

        print(os.popen("sudo apt-get install build-essential libtool autotools-dev automake pkg-config bsdmainutils python3").read())
        #main dependencies

        print(os.popen("sudo apt-get install libevent-dev libboost-dev").read()) #compiling dependencies

        print(os.popen("sudo apt-get install libsqlite3-dev").read()) #descriptor wallet only

        print(os.popen("sudo apt-get install libminiupnpc-dev libnatpmp-dev").read()) #port mapping

        print(os.popen("sudo apt-get install libzmq3-dev").read()) # ZMQ API

        print(os.popen("sudo apt-get install systemtap-sdt-dev").read()) # User-Space, Statically Defined Tracing 

        '''
        Incase we need GUI at any point:
        GUI dependencies:

        If you want to build bitcoin-qt, make sure that the required packages for Qt development are installed. 
        Qt 5 is necessary to build the GUI. To build without GUI pass --without-gui.

        To build with Qt 5 you need the following:

        sudo apt-get install qtbase5-dev qttools5-dev qttools5-dev-tools
        Additionally, to support Wayland protocol for modern desktop environments:

        sudo apt install qtwayland5
        libqrencode (optional) can be installed with:

        sudo apt-get install libqrencode-dev
        '''
        
        cmd = \
            "git clone https://github.com/bitcoin/bitcoin.git && cd bitcoin && ./autogen.sh && ./configure && make install -j 4"
        print(os.popen(cmd).read())

    else:
        print("unsupported platform:", platform)

def generateBitcoinConf(rpcauthpasslength=64):
    def gen():
        default = \
            "regtest=1\n" + \
            "daemon=1\n" + \
            "txindex=1\n" + \
            "zmqpubrawblock=tcp://127.0.0.1:28332\n" + \
            "zmqpubrawtx=tcp://127.0.0.1:28333\n"
        password = generate_password()
        salt = generate_salt(16)
        password_hmac = password_to_hmac(salt, password)
        username = "regtestuser1" #TODO custom first username and followup users appended to conf
        generated = \
            default + \
            f'rpcauth={username}:{salt}${password_hmac}\n' + \
            f'rpcuser={username}\n' + \
            f'rpcpass={salt}${password_hmac}'

        file_tools.clean_file_open("bitcoin.conf", "w", generated)
        return True
    if os.path.isfile("bitcoin.conf") == False:
        gen()
    else:
        while True:
            print("bitcoin.conf already exists, regenerating will overwrite the current one, proceed with caution.\n" + 
                    "Overwrite existing and generate new bitcoin.conf? (y\\n)")
            yn = input()
            if yn == "y" or yn == "Y":
                return gen()
            if yn == "n" or yn == "N":
                return False
            else:
                print("unrecognized option:", yn)


def is_lnd_variation(s):
    pattern = r'^lnd\d*$'
    return bool(re.match(pattern, s))

def get_lndconf_value(section, key, configstring):
    pattern = re.compile(r'\[' + re.escape(section) + r'\](.*?)(?:\n\[|\Z)', re.DOTALL)
    section_content = pattern.search(configstring)
    if section_content:
        section_content = section_content.group(1)
        key_pattern = re.compile(r'^' + re.escape(key) + r'=(.*)$', re.MULTILINE)
        key_value = key_pattern.search(section_content)
        if key_value:
            return key_value.group(1).strip()
    return None

def createBashAlias(alias="", application="bitcoin"):
    current_directory = os.getcwd()
    if application == "bitcoin":
        alias = "btcregtest"
        aliasinfo = (
            f'export REGTEST_DIR="{current_directory}"\n'
            f'alias {alias}d="bitcoind -datadir=$REGTEST_DIR"\n'
            f'alias {alias}-cli="bitcoin-cli -datadir=$REGTEST_DIR"\n'
        )
        file_path = os.path.expanduser("~/.bash_aliases")

        with open(file_path, "a") as file:
            file.write(aliasinfo)
        os.popen("chmod +x ~/.bash_aliases").read()

        file_path = os.path.expanduser("~/.bash_profile")
        
        with open(file_path, "a") as file:
            file.write(aliasinfo)
        
        # Reload the .bash_profile in an interactive shell to apply the changes
        # and check the aliases
        output = subprocess.run(
            ["bash", "-i", "-c", "source ~/.bash_profile && alias"],
            capture_output=True,
            text=True
        )
        print(output.stdout)
    if application == "lnd":
        if alias == "":
            print("must provide lnd dirname as alias when using lnd as application in createBashAlias.")
            return
        if os.path.isdir(alias) == False:
            print("lnd directory: ", alias, "not found")
            return
        if is_lnd_variation(alias) == True:
            capitalalias = alias.upper()
            aliasnod = alias.replace("d", "") #assuming aliases be lnd, specific dirnames will encounter errors here TODO
            aliasinfo = (
                f'export {capitalalias}_DIR="{current_directory}/{alias}"\n'
                f'alias {alias}="lnd --lnddir=${capitalalias}_DIR"\n'
                f'alias {aliasnod}cli="lncli -n regtest --lnddir=${capitalalias}_DIR"'
            )
            conf = file_tools.clean_file_open(alias + "/lnd.conf", "r")
            rpcserverport = get_lndconf_value("Application Options", "rpclisten", conf)
            if rpcserverport != None:
                aliasinfo = aliasinfo + f' --rpcserver=localhost:{rpcserverport}\n'
            else: 
                aliasinfo = aliasinfo + "\n"
        else:
            print(
                    "custom dirname lnd aliasing is currently unhandled!" + \
                            "please use automatic lnd dirnames for now or pull request an update to handle custom ones"
            )
            return
        file_path = os.path.expanduser("~/.bash_aliases")

        with open(file_path, "a") as file:
            file.write(aliasinfo)
        os.popen("chmod +x ~/.bash_aliases").read()

        file_path = os.path.expanduser("~/.bash_profile")

        with open(file_path, "a") as file:
            file.write(aliasinfo)
        output = subprocess.run(
            ["/bin/bash",  "-c", "source ~/.bash_aliases && alias"],
            capture_output=True,
            text=True
        )
        print(output.stdout)
        # Reload the .bash_profile in an interactive shell to apply the changes
        # and check the aliases
        output = subprocess.run(
           ["/bin/bash",  "-c", "source ~/.bash_profile && alias"],
            capture_output=True,
            text=True
        )
        print(output.stdout)


def get_bitcoin_conf_value(conf_string, key):
    # Split the configuration string into lines
    lines = conf_string.split('\n')
    
    # Iterate over each line
    for line in lines:
        # Split the line by '=' to get the key-value pair
        if '=' in line:
            conf_key, conf_value = line.split('=', 1)
            # Check if the current key matches the desired key
            if conf_key.strip() == key:
                return conf_value.strip()
    
    # Return None if the key is not found
    return None

def createLightningNodeDirAndConf(altListenPort="", altRpcListenPort="", altRestListenPort=""):
    if os.path.isdir("bitcoin") == False: #bitcoin regtest dir not created yet
        print("must create bitcoin regtest directory first!")
        return 
    if os.path.isfile("bitcoin.conf") == False:
        print("must generate a bitcoin.conf first!")
    bitcoinconf = file_tools.clean_file_open("bitcoin.conf", "r")
    rpcauth = get_bitcoin_conf_value(bitcoinconf, "rpcauth" )
    rpcuser = rpcauth.split(":")[0]
    rpcpass = rpcauth.split(":")[1]

    dirname = "lnd"
    index = 2
    if os.path.isdir(dirname) == True:
        while True:
            dirname = dirname + str(index)
            if os.path.isdir(dirname) == False:
                break
            else:
                index += 1
                dirname = remove_digits(dirname)
        
    Conf = \
            "[Bitcoin]\n" + \
            "bitcoin.active=1\n" + \
            "bitcoin.regtest=1\n" + \
            "bitcoin.node=bitcoind\n" + \
            "[Bitcoind]\n" + \
            "bitcoind.rpchost=localhost\n" + \
            "bitcoind.rpcuser=" + rpcuser + "\n" + \
            "bitcoind.rpcpass=" + rpcpass + "\n" + \
            "bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332\n" + \
            "bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333\n"
    appOptionsFormat = \
            "[Application Options]\n"
    if altListenPort != "" or altRpcListenPort != "" or altRestListenPort != "":
        if altListenPort != "":
            if altListenPort.isdigit() == False:
                print("port must be an integer, actual value: ", altListenPort)
                return 
            else:
                appOptionsFormat = appOptionsFormat + \
                        "listen=0.0.0.0:" + altListenPort + "\n"
        if altRpcListenPort != "":
            if altRpcListenPort.isdigit() == False:
                print("port must be an integer, actual value: ", altRpcListenPort)
                return
            else:
                appOptionsFormat = appOptionsFormat + \
                        "rpclisten=localhost:" + altRpcListenPort + "\n"
        if altRestListenPort != "":
            if altRestListenPort.isdigit() == False:
                print("port must be an integer, actual value: ", altRestListenPort)
                return 
            else:
                appOptionsFormat = appOptionsFormat + \
                        "restlisten=0.0.0.0:" + altRestListenPort + "\n"
        Conf = appOptionsFormat + Conf
    file_tools.clean_mkdir(dirname)
    file_tools.clean_file_open(dirname + "/lnd.conf", "w", Conf)
     
def sha256_hash_string(input_string):
    sha256 = hashlib.sha256()
    sha256.update(input_string.encode('utf-8'))
    hex_digest = sha256.hexdigest()
    return hex_digest

def gnome_terminal(cmd):
    editcmd = f'source ~/.bashrc && {cmd}'
    subprocess.run(['gnome-terminal', '--', 'bash', '-i', "-c", editcmd])

def currentShellInteractiveBashScriptExecNoReturn(cmd):
    editcmd = f'source ~/.bashrc && {cmd}'
    subprocess.run( 
            ["bash", "-i", "-c", editcmd  ],
    )

def currentShellInteractiveBashScriptExec(cmd):
    editcmd = f'source ~/.bashrc && {cmd}'
    output = subprocess.run( 
            ["bash", "-i", "-c", editcmd  ],
            capture_output=True,
            text=True
    ).stdout
    return output

def contains_number(s):
    return any(char.isdigit() for char in s)

def LND(lndDirName, command="", targetLndDir="", addrtype="", amount="", pay_req=""):
    cmd = ""
    cliEditDirName = ""
    listen = ""
    rpclisten = ""
    restlisten = ""
    if contains_number(lndDirName) == False:
        cliEditDirName = lndDirName.replace("d", "cli")
    else:
        cliEditDirName = lndDirName.replace("d", "") + "cli"
    lndconf = file_tools.clean_file_open(lndDirName + "/lnd.conf", "r")
    if lndconf.find("Application Options") != -1:
        listen = get_lndconf_value("Application Options", "listen", lndconf)
        rpclisten = get_lndconf_value("Application Options", "rpclisten", lndconf)
        restlisten = get_lndconf_value("Application Options", "restlisten", lndconf)
    if command == "":
        gnome_terminal(lndDirName)
    if command == "create": #create wallet for local lnd instance
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " create"
        else:
            cmd = cliEditDirName + " create"
        currentShellInteractiveBashScriptExecNoReturn(cmd)
    if command == "getinfo": #get info about local lnd instance
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten +  " getinfo"
        else:
            cmd = cliEditDirName +  " getinfo"
        info = currentShellInteractiveBashScriptExec(cmd)
        identity_pubkey = json.loads(info)["identity_pubkey"]
        file_tools.clean_file_open(lndDirName + "/identity_pubkey", "w", identity_pubkey)
    if command == "unlock": #unlock local lnd instance
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " unlock"
        else:
            cmd = cliEditDirName + " unlock"
        currentShellInteractiveBashScriptExecNoReturn(cmd)
    if command == "connect_localDir": #connect two local instances by providing only their directory names
        if targetLndDir == "":
            print("must provide targetLndDir")
            return
        if os.path.isdir(targetLndDir) == False:
            print("lnd dir not found! dir:", targetLndDir)
            return
        if os.path.isfile(targetLndDir + "/identity_pubkey") == False:
            print("target lnd dir identity_pubkey not found, run getinfo on this lnd instance first!")
            return
        identity_pubkey = file_tools.clean_file_open(targetLndDir + "/identity_pubkey", "r")
        lndconf = file_tools.clean_file_open(targetLndDir + "/lnd.conf", "r")
        targetlisten = ""
        if lndconf.find("Application Options") != -1:
            targetlisten = get_lndconf_value("Application Options", "listen", lndconf)
        else:
            targetlisten = "0.0.0.0:9735" #default
        connectobject = f'{identity_pubkey}@{targetlisten}'
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten +  " connect "  + connectobject
        else:
            cmd = cliEditDirName +  " connect " + connectobject
        info = currentShellInteractiveBashScriptExec(cmd)
        print(info)
    if command == "peers": #check the peers list for a local lnd instance
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " listpeers"
        else:
            cmd = cliEditDirName + " listpeers"
        print(currentShellInteractiveBashScriptExec(cmd))
    if command == "newaddr":
        if addrtype == "":
            print("must provide addrtype!")
            return
        if addrtype not in["np2wkh"]:
            print("unhandled  addrtype: " + addrtype + " !")
            return
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " newaddress " + addrtype
        else:
            cmd = cliEditDirName + " newaddress " + addrtype
        addrobj = currentShellInteractiveBashScriptExec(cmd)
        addr = json.loads(addrobj)["address"]
        np2wkh_addrs = ""
        np2wkh_addrs_obj = {}
        if os.path.isfile(lndDirName + "/np2wkh_addrs.json") == True:
            np2wkh_addrs = file_tools.clean_file_open(lndDirName + "/np2wkh_addrs.json", "r")
            np2wkh_addrs_obj = json.loads(np2wkh_addrs)
            index = len(np2wkh_addrs_obj)
            np2wkh_addrs_obj[index] = addr
            file_tools.clean_file_open(lndDirName + "/np2wkh_addrs.json", "w", json.dumps(np2wkh_addrs_obj, indent=2))
        else:
            np2wkh_addrs_obj[0] = addr
            file_tools.clean_file_open(lndDirName + "/np2wkh_addrs.json", "w", json.dumps(np2wkh_addrs_obj, indent=2))
        print(addr)
    if command == "openchannel_lnddir":
        if os.path.isdir(lndDirName) == False:
            print("lnd dir:", lndDirName, "not found!")
            return
        if targetLndDir == "":
            print("must provide target lnd dir name")
            return
        if os.path.isfile(targetLndDir + "/identity_pubkey") == False:
            print("target lnd dir identity_pubkey not found! run getinfo on it first")
            return
        if amount == "":
            print("must provide amount")
            return
        targetLNDDir_identity_pubkey = file_tools.clean_file_open(targetLndDir + "/identity_pubkey", "r")
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " openchannel " + targetLNDDir_identity_pubkey + " " + amount
        else:
            cmd = cliEditDirName + " openchannel " + targetLNDDir_identity_pubkey + " " + amount
        print(currentShellInteractiveBashScriptExec(cmd))
    if command == "listchannels":
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " listchannels"
        else:
            cmd = cliEditDirName + " listchannels"
        print(currentShellInteractiveBashScriptExec(cmd))
    if command == "invoice":
        if amount == "":
            print("must provide amount")
            return
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " addinvoice -amt " + amount
        else:
            cmd = cliEditDirName + " addinvoice -amt " + amount
        print(currentShellInteractiveBashScriptExec(cmd))
    if command == "decode_payreq":
        if pay_req == "":
            print("provide payreq!")
            return
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " decodepayreq " + pay_req
        else:
            cmd = cliEditDirName + " decodepayreq " + pay_req
        print(currentShellInteractiveBashScriptExec(cmd))
    if command == "payinvoice":
        if pay_req == "":
            print("provide payreq!")
            return
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " payinvoice " + pay_req
        else:
            cmd = cliEditDirName + " payinvoice " + pay_req
        print(currentShellInteractiveBashScriptExecNoReturn(cmd))
    if command == "listinvoices":
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " listinvoices"
        else:
            cmd = cliEditDirName + " listinvoices"
        print(currentShellInteractiveBashScriptExec(cmd))
    if command == "listpayments":
        if rpclisten != "":
            cmd = cliEditDirName + " --rpcserver=" + rpclisten + " listpayments"
        else:
            cmd = cliEditDirName + " listpayments"
        print(currentShellInteractiveBashScriptExec(cmd))

        

def regtestCLI(command="", targetLNDDir="", amount="", rpcwallet=""):
    if command == "sendToLNDDir":
        if targetLNDDir == "":
            print("must provide target lnd dir!")
            return
        if os.path.isdir(targetLNDDir) == False:
            print("target lnd dir:", targetLNDDir, " not found!")
            return
        if os.path.isfile(targetLNDDir + "/np2wkh_addrs.json") == False:
            print(targetLNDDir + "/np2wkh_addrs.json file not found! call lnd_new_np2wkh_addr on this lnd dir first!")
            return
        if amount == "":
            print("provide amount!")
            return
        if rpcwallet == "":
            print("provide rpcwallet!")
            return
        obj = json.loads(file_tools.clean_file_open(targetLNDDir + "/np2wkh_addrs.json", "r"))
        keys = list(obj.keys())
        randomkey = random.choice(keys)
        randomaddr = obj[randomkey]
        cmd = \
                "./sendToAddress.sh " + rpcwallet + " " + randomaddr + " " + amount
        print(currentShellInteractiveBashScriptExec(cmd))



args = sys.argv
if __name__ == "__main__":
    if len(args) > 1:
        if len(args) == 2:
            if args[1] == "generateBitcoinConf":
                generateBitcoinConf()
            if args[1] == "createBashAlias":
                createBashAlias()
            if args[1] == "downloadBuildAndInstallBitcoinCore":
                downloadBuildAndInstallBitcoinCore()
            if args[1] == "createLightningNodeDirAndConf":
                createLightningNodeDirAndConf()
            if args[1] == "downloadBuildAndInstallLND":
                downloadBuildAndInstallLND()
        if len(args) == 3:
            if args[1] == "createBashAlias_lnd":
                createBashAlias(alias=args[2], application="lnd")
            if args[1] == "lndPeers":
                LND(args[2], command="peers")
            if args[1] == "lndChannels":
                LND(args[2], command="listchannels")
            if args[1] == "lnd_getinfo":
                LND(args[2], command="getinfo")
            if args[1] == "lnd_unlock":
                LND(args[2], command="unlock")
            if args[1] == "createLNDWallet":
                LND(args[2], command="create")
            if args[1] == "launch_lnd":
                LND(args[2]) #must use lnd directory name as followup arg
            if args[1] == "lnd_new_np2wkh_addr":
                LND(args[2], command="newaddr", addrtype="np2wkh")
            if args[1] == "listinvoicesLND":
                LND(args[2], command="listinvoices")
            if args[1] == "listpaymentsLND":
                LND(args[2], command="listpayments")
        if len(args) == 4:
            if args[1] == "decode_payreqLND":
                LND(args[2], command="decode_payreq", pay_req=args[3])
            if args[1] == "invoiceLND":
                LND(args[2], command="invoice", amount=args[3])
            if args[1] == "payinvoiceLND":
                LND(args[2], command="payinvoice", pay_req=args[3])
            if args[1] == "connect_localDir_lnd":
                LND(args[2], command="connect_localDir", targetLndDir=args[3])
        if len(args) == 5:
            if args[1] == "openchannel_lnddir":
                LND(args[2], command="openchannel_lnddir", targetLndDir=args[3], amount=args[4])
            if args[1] == "sendToLNDDir":
                regtestCLI(command="sendToLNDDir", rpcwallet=args[2], targetLNDDir=args[3], amount=args[4])
            if args[1] == "createLightningNodeDirAndConf":
                createLightningNodeDirAndConf(altListenPort=args[2], altRpcListenPort=args[3], altRestListenPort=args[4])
        if len(args) == 6:
            if args[1] == "createLightningNodeDirAndConf":
                createLightningNodeDirAndConf(
                        altListenPort=args[2], altRpcListenPort=args[3], 
                        altRestListenPort=args[4], dirname=args[5]
                )
    else:
        print(\
                "None or incorrect args provided!\nOptions: \n\n" + \
                "generateBitcoinConf - generate bitcoin.conf file\n\n" + \
                "createBashAlias - create a bash alias shortcut for your regtest daemon and cli\n\n" + \
                "createBashAlias_lnd [Required Args]: <lndDirectoryName> - create a bash alias shortcut for your lnd node\n\n"
                "downloadAndBuildBitcoinCore - install dependencies, clone bitcoin core, build, specific to platform\n\n" + \
                "downloadBuildAndInstallLND - install go(if not installed already), clone LND, make and install LND\n\n"
                "createLightningNodeDirAndConf [Optional Args]: <altListenPort> <altRpcListenPort> <altRestListenPort> \n" + \
                " - create a directory for a new lightning node and generate it's config\n" + \
                "(Must specify ALL alt ports if using them)\n\n" + \
                "launch_lnd [Required Args]: <lndDirectoryName> - launch a specific LND instance\n\n" + \
                "createLNDWallet [Required Args]: <lndDirectoryName> - create a LND wallet for your specific LND instance\n\n" + \
                "lnd_unlock [Required Args]: <lndDirectoryName> - unlock the wallet you created for your specific LND instance\n\n" + \
                "lnd_getinfo [Required Args]: <lndDirectoryName> - get info about your LND node instance," + \
                " saves an identity_pubkey file\n\n" 
                "connect_localDir_lnd: [Required Args]: <lndDirectoryName> <targetLndDirectoryName> " + \
                " - connect two local lnd instances as peers by their directory names\n\n"               
                "lndPeers [Required Args]: <lndDirectoryName> - list the peers connected to the lnd instance given if any\n\n" + \
                "lndChannels [Required Args]: <lndDirectoryName> - list all the channels of the lnd instance given if any\n\n"
                "lnd_new_np2wkh_addr [Required Args]: <lndDirectoryName> - load a new address for a specific lightning instance" + \
                        "\nbuilds a np2wkh_addrs.json file in relevant lnd directory\n\n"
                "sendToLNDDir [Required Args]: <walletNameToSendFrom> <targetLndDirectoryName> <amountToSend> " + \
                        " - send regtest bitcoin to an address belonging to the target LND Directory / Instance\n\n" + \
                "openchannel_lnddir [Required Args]: <lndDirectoryName> <targetLndDirectoryName> <channelSatAmount>" + \
                " - open a lightning channel between two local lnd directory instances\n\n" + \
                "invoiceLND [Required Args]: <lndDirectoryName> <invoiceAmount>"  + \
                " - create a Lightning invoice for amount specified\n\n" + \
                "decode_payreqLND [Required Args]: <lndDirectoryName> <pay_req> - decode a payment request\n\n"
                "listinvoicesLND[Required Args]: <lndDirectoryName> - list invoices generated by specific lnd instance\n\n" + \
                "listpaymentsLND  [Required Args]: <lndDirectoryName> - list payments made by specific lnd instance"

        )
