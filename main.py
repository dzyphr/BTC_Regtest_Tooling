import secrets, string, file_tools, sys, os, subprocess, re, json, hmac, hashlib, time
from argparse import ArgumentParser
from getpass import getpass
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

def createLightningNodeDirAndConf(dirname="", altListenPort="", altRpcListenPort="", altRestListenPort=""):
    if os.path.isdir("bitcoin") == False: #bitcoin regtest dir not created yet
        print("must create bitcoin regtest directory first!")
        return 
    if os.path.isfile("bitcoin.conf") == False:
        print("must generate a bitcoin.conf first!")
    bitcoinconf = file_tools.clean_file_open("bitcoin.conf", "r")
    rpcauth = get_bitcoin_conf_value(bitcoinconf, "rpcauth" )
    rpcuser = rpcauth.split(":")[0]
    rpcpass = rpcauth.split(":")[1]

    if dirname == "":
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

def gnome_terminal(cmdstr):
    tempname = sha256_hash_string(cmdstr) 
    file_tools.clean_file_open(tempname + ".sh", "w", cmdstr+ "\nexec bash")
    os.popen("chmod +x " + tempname + ".sh").read()
    subprocess.run(['gnome-terminal', '--', 'bash', '-i', tempname + ".sh"])
    time.sleep(2)
    os.remove(tempname + ".sh")

def currentShellInteractiveBashScriptExec(cmd):
    tempname = sha256_hash_string(cmd)
    file_tools.clean_file_open(tempname + ".sh", "w", cmd)
    subprocess.run(['bash', '-i', tempname + ".sh"])
    time.sleep(2)
    os.remove(tempname + ".sh")

def LND(lndDirName, command=""):
    if command == "":
        gnome_terminal(lndDirName)
    if command == "create": #create wallet
        cmd = lndDirName.replace("d", "cli") + " create"
        currentShellInteractiveBashScriptExec(cmd)
    if command == "getinfo":
        cmd = lndDirName.replace("d", "cli") + " getinfo"
        currentShellInteractiveBashScriptExec(cmd)
    if command == "unlock":
        cmd = lndDirName.replace("d", "cli") + " unlock"
        currentShellInteractiveBashScriptExec(cmd)

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
            if args[1] == "lnd_getinfo":
                LND(args[2], command="getinfo")
            if args[1] == "lnd_unlock":
                LND(args[2], command="unlock")
            if args[1] == "createLNDWallet":
                LND(args[2], command="create")
            if args[1] == "launch_lnd":
                LND(args[2]) #must use lnd directory name as followup arg
        if len(args) == 5:
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
                "createBashAlias - create a sbash alias shortcut for your regtest daemon and cli\n\n" + \
                "createBashAlias_lnd [Required Args]: <lndDirectoryName> - create a bash alias shortcut for your lnd node"
                "downloadAndBuildBitcoinCore - install dependencies, clone bitcoin core, build, specific to platform\n\n" + \
                "downloadBuildAndInstallLND - install go(if not installed already), clone LND, make and install LND"
                "createLightningNodeDirAndConf [Optional Args]: <altListenPort> <altRpcListenPort> <altRestListenPort> <dirname>\n" + \
                " - create a directory for a new lightning node and generate it's config\n" + \
                "(Must specify ALL alt ports if using them. Custom dirname arg requires all alt port usage also)\n"

        )
