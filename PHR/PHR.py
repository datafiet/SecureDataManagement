"""Public Health Record interface

Usage:
    PHR.py
    PHR.py kgc generate masterkey
    PHR.py -h|--help
    PHR.py -v|--version
Options:
    -h --help                       Show this screen.
    -v --version                    Show version.
    -l<user> --login=<user>         Login as user.
    -r<record> --record=<record>    Execute command for a specific public health record.
    -t<type> --type=<type>          Specify type of data.
"""
import os
import sys
from pathlib import Path
from subprocess import call

import pairing_pickle
from charm.core.math.pairing import GT
from charm.toolbox.pairinggroup import PairingGroup, extract_key
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction
from docopt import docopt
from json_helper import DataHelper, RecordAlreadyExists
from type_id_proxy_reencryption import TIPRE

dir_path = os.path.dirname(os.path.realpath(__file__))

kgc_path = Path('{}/keys/kgc'.format(dir_path))
try:
    kgc_path.mkdir(parents=True)
except:
    pass
reencryption_path = Path('{}/keys/reencryption'.format(dir_path))
try:
    reencryption_path.mkdir(parents=True)
except:
    pass
group = PairingGroup('SS512', secparam=1024)
pre = TIPRE(group)
data_helper = DataHelper(group)


def SYMKEY(): return "enc_sym_key"


def USER(user): return "user_{}".format(user)


def HOSPITAL(hospital): return "hospital_{}".format(hospital)


def HEALTHCLUB(healthclub): return "healthclub_{}".format(healthclub)


def kgc_generate_master():
    master_secret_key, params = pre.setup()

    with (kgc_path / 'master_key').open(mode='wb') as f:
        pairing_pickle.dump(group, master_secret_key, f)
    with (kgc_path / 'params').open(mode='wb') as f:
        pairing_pickle.dump(group, params, f)


def kgc_generate_user(user_id: str):
    with (kgc_path / 'master_key').open(mode='rb') as f:
        master_key = pairing_pickle.load(group, f)

    if (kgc_path / '{}'.format(user_id)).exists():
        print('User with this id is already registered in this KGC')
    else:
        with (kgc_path / '{}'.format(user_id)).open(mode='wb') as f:
            pairing_pickle.dump(group, pre.keyGen(master_key, user_id), f)


def get_params():
    with (kgc_path / 'params').open(mode='rb') as f:
        return pairing_pickle.load(group, f)


def load_user_key(user):
    print('Loading user key: {}'.format(kgc_path / user))
    with (kgc_path / user).open(mode='rb') as f:
        user_key = pairing_pickle.load(group, f)
    return user_key


def read(user, record):
    """
    Function to read some public health record, from a given user. Returns
    all parts of the record.

    :param user:      User public key that wants to read the health record
    :param record:    Public health record to be read
    """

    # Get the record from the file system and load the key
    data = data_helper.load(user, record)
    user_key = load_user_key(user)

    # Decrypt the symmetric key using the TIPRE key
    sym_crypto_key = pre.decrypt(get_params(), user_key, data[SYMKEY()])

    # Setup symmetric crypto
    sym_crypto = SymmetricCryptoAbstraction(extract_key(sym_crypto_key))

    # Attempt to decrypt all columns and return
    decrypted_record = {k: sym_crypto.decrypt(v) for k, v in data.items() if k != SYMKEY()}
    return decrypted_record


def insert(user, data, record, type_attribute):
    """
    Insert data into a public health record.

    :param user:            User that wants to insert data
    :param data:            Data to be inserted
    :param record:          Public health record in which data is inserted.
    :param type_attribute:  The type for this record

    """

    # Check if some arguments are correct
    if record is None:
        sys.exit("Please provide the record")
    if SYMKEY() in data:
        sys.exit("Data contains the key {}, please use a different key".format(SYMKEY()))

    # Load the users key
    user_key = load_user_key(user)

    # Create new symmetric key
    sym_crypto_key = group.random(GT)
    sym_crypto = SymmetricCryptoAbstraction(extract_key(sym_crypto_key))
    # Encrypt symmetric key with TIPRE
    # and the data using the symmetric key
    encrypted_sym_key = pre.encrypt(get_params(), user, sym_crypto_key, user_key, type_attribute)
    encrypted_data = {k: sym_crypto.encrypt(v) for k, v in data.items()}
    encrypted_data[SYMKEY()] = encrypted_sym_key

    # Store the data
    try:
        data_helper.save(user, type_attribute, encrypted_data, record)
        print("Data is inserted into record \'{}\' by \'{}\'".format(record, user))
        print("Data to insert into record:\n{}".format(data))
    except RecordAlreadyExists as e:
        print(e)


def allow_access(user, to_user, type_attribute):
    """
    Allow another user read access to own public health record. Ran by delegater.

    :param user:             Owner of the public health record
    :param to_user:          Public key of the user that will get read access
    :param type_attribute:   Type of data that to_user will have access to
    """

    # Load the users key and create a reencryption key for to_user
    key = load_user_key(user)
    re_encryption_key = pre.rkGen(get_params(), key, to_user, type_attribute)

    # Store the reencryption key for the proxy
    with (reencryption_path / 'from_{}_to_{}_type_{}'.format(user, to_user, type_attribute)).open(mode='wb') as f:
        pairing_pickle.dump(group, re_encryption_key, f)

    print("{} has provided {} with read access to their Public Health Record".format(user, to_user))


def insert_with_proxy(from_user, to_user, data, record, type_attribute):
    """
    Insert data in from_user record and give to_user access as well, by
    calling the proxy to reencrypt the created ciphertext.

    :param from_user:       The user where the ciphertext is from
    :param to_user:         The user for which the reencrypted ciphertext is
    :param data:            The data to be inserted/encrypted
    :param record:          The name of this record
    :param type_attribute   The type

    """

    # Insert in own record and create reencryption key for the proxy
    insert(from_user, data, record, type_attribute)
    allow_access(from_user, to_user, type_attribute)

    # Call the proxy to reencrypt the just created ciphertext
    arguments = "python3 proxy.py reencrypt {} {} -r {} -t {}".format(
        from_user,
        to_user,
        record, type_attribute)
    call(arguments.split(' '))


def select_file(user):
    """
    Let the user select a file in its own records.

    :param user: The user
    """
    files = data_helper.get_data_files(user)

    for idx, val in enumerate(files):
        print("{}. {}".format(idx, val))
    n = int(input("Choose the number of the file you want to read\n"))
    if n < 0 or n >= len(files):
        sys.exit("Please enter a correct number")
    print("\nSelected file {}\n".format(files[n]))
    return read(user, files[n])


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['kgc'] and arguments['masterkey']:
        kgc_generate_master()
    elif arguments['kgc'] and arguments['userkey'] and arguments['<user_id>']:
        kgc_generate_user(arguments['<user_id>'])
    else:
        print(__doc__)