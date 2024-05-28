import secrets, string, file_tools, sys, os, subprocess
from argparse import ArgumentParser
from getpass import getpass
from secrets import token_hex, token_urlsafe
import hmac
import json

def generate_salt(size):
    """Create size byte hex salt"""
    return token_hex(size)

def generate_password():
    """Create 32 byte b64 password"""
    return token_urlsafe(32)

def password_to_hmac(salt, password):
    m = hmac.new(salt.encode('utf-8'), password.encode('utf-8'), 'SHA256')
    return m.hexdigest()

def downloadAndBuildBitcoinCore(platform="ubuntu"):
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
            "git clone https://github.com/bitcoin/bitcoin.git && cd bitcoin && ./autogen.sh && ./configure && make -j 4"
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
            "rpcauth="\
            f'{username}:{salt}${password_hmac}'
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


def createBashAlias(alias="btcregtest"):
    current_directory = os.getcwd()
    aliasinfo = (
        f'export REGTEST_DIR="{current_directory}"\n'
        f'alias {alias}d="bitcoind -datadir=$REGTEST_DIR"\n'
        f'alias {alias}-cli="bitcoin-cli -datadir=$REGTEST_DIR"\n'
    )
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
#    print(f"Aliases added to {file_path}. To apply the changes, run:")
#    print("source ~/.bash_profile")

args = sys.argv
if __name__ == "__main__":
    if len(args) > 1:
        if args[1] == "generateBitcoinConf":
            generateBitcoinConf()
        if args[1] == "createBashAlias":
            createBashAlias()
        if args[1] == "downloadAndBuildBitcoinCore":
            downloadAndBuildBitcoinCore()
    else:
        print(\
                "No args provided!\nOptions: \n" + \
                "generateBitcoinConf - generate bitcoin.conf file\n" + \
                "createBashAlias - create a specific bash alias shortcut for your regtest daemon and cli\n" + \
                "downloadAndBuildBitcoinCore - install dependencies, clone bitcoin core, build, specific to platform"
        )
