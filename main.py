import secrets, string, file_tools, sys, os
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
    aliasinfo = \
            "export REGTEST_DIR=\"" + current_directory + "\"\n" + \
            "alias " + alias + "d -datadir=$REGTEST_DIR\n" + \
            "alias " + alias + "-cli -datadir=$REGTEST_DIR\n"
    file_path = os.path.expanduser("~/.bash_profile")
    with open(file_path, "a") as file:
        file.write(aliasinfo)
    os.popen("source ~/.bash_profile").read()



args = sys.argv
if __name__ == "__main__":
    if len(args) > 1:
        if args[1] == "generateBitcoinConf":
            generateBitcoinConf()
        if args[1] == "createBashAlias":
            createBashAlias()
    else:
        print(\
                "No args provided!\nOptions: \n" + \
                "generateBitcoinConf - generate bitcoin.conf file\n" + \
                "createBashAlias - create a specific bash alias shortcut for your regtest daemon and cli" \
        )
