"""Proxy interface

Usage:
    proxy.py
    proxy.py reencrypt <from-user> <to-user> -r <record> -t <type> 
    proxy.py -h|--help
    proxy.py -v|--version
Options:
    -h --help                       Show this screen.
    -v --version                    Show version.
"""

import os
from pathlib import Path

import pairing_pickle
from charm.toolbox.pairinggroup import PairingGroup
from docopt import docopt
from json_helper import DataHelper
from type_id_proxy_reencryption import TIPRE

import PHR

dir_path = os.path.dirname(os.path.realpath(__file__))

kgc_path = Path('{}/keys/kgc'.format(dir_path))
reencryption_path = Path('{}/keys/reencryption'.format(dir_path))
group = PairingGroup('SS512', secparam=1024)
pre = TIPRE(group)
data_helper = DataHelper(group)


def get_params():
    with (kgc_path / 'params').open(mode='rb') as f:
        return pairing_pickle.load(group, f)


def reEncrypt(user, to_user, record, type_attribute):
    ciphertext = data_helper.load(user, record)

    # Retrieve the reencryption key
    with (reencryption_path / 'from_{}_to_{}_type_{}'.format(user, to_user, type_attribute)).open(mode='rb') as f:
        re_encryption_key = pairing_pickle.load(group, f)

        # Reencrypt the data
    cipher = pre.reEncrypt(get_params(), re_encryption_key, ciphertext[PHR.SYMKEY()])
    ciphertext[PHR.SYMKEY()] = cipher
    data_helper.save(to_user, type_attribute, ciphertext, "reencryption_from_{}_{}".format(user, record))
    return cipher


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['reencrypt']:
        reEncrypt(arguments['<from-user>'], arguments['<to-user>'], arguments['<record>'], arguments['<type>'])
