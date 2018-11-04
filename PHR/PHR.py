"""Public Health Record interface

Usage:
    PHR.py
    PHR.py init
    PHR.py kgc generate masterkey
    PHR.py kgc generate userkey <user_id>
    PHR.py read <record> -l <user> 
    PHR.py insert <data> -l <user> 
    PHR.py insert <data> -r <record> -l <user> 
    PHR.py allow-access <to-user> -t <type> -l <user> 
    PHR.py new patient <user> <gender> <date-of-birth> <patient-address> -t <type_attribute>
    PHR.py new patient <user> <gender> <date-of-birth> <patient-address> <other>
    PHR.py reencrypt <to-user> -l <user> -r <record> -t <type> 
    PHR.py -l <user> 
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

import pairing_pickle
import json
from charm.core.math.pairing import GT
from charm.toolbox.pairinggroup import PairingGroup, extract_key
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction
from database import Database
from docopt import docopt
from type_id_proxy_reencryption import TIPRE
from json_helper import DataHelper

db = Database()

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


def kgc_generate_master():
    master_secret_key, params = pre.setup()

    with (kgc_path / 'master_key').open(mode='wb') as f:
        pairing_pickle.dump(group, master_secret_key, f)
    with (kgc_path / 'params').open(mode='wb') as f:
        pairing_pickle.dump(group, params, f)


def kgc_generate_user(user_id: str):
    #TODO: check if user already exists
    with (kgc_path / 'master_key').open(mode='rb') as f:
        master_key = pairing_pickle.load(group, f)
    with (kgc_path / 'user_id_{}'.format(user_id)).open(mode='wb') as f:
        pairing_pickle.dump(group, pre.keyGen(master_key, user_id), f)


def get_params():
    with (kgc_path / 'params').open(mode='rb') as f:
        return pairing_pickle.load(group, f)


def init():
    """ Initializes the database """
    db.initialize()


def new_patient(user_id, gender, date, address):
    """
    Create a new user, creates a Public Health Record and a key.

    :param user_id: The user public key the, who creates the record
    """

    #Set the attribute
    type_attribute = "patient"

    # Load secret user key
    user_key = load_user_key(user_id)

    # Create new symmetric key
    sym_crypto_key = group.random(GT)
    sym_crypto = SymmetricCryptoAbstraction(extract_key(sym_crypto_key))
    # Encrypt symmetric key with TIPRE
    # and the data using the symmetric key
    encrypted_sym_key = pre.encrypt(get_params(), user_id, sym_crypto_key, user_key, type_attribute)
    p = {'enc_sym_key': encrypted_sym_key,
        'gender': sym_crypto.encrypt(gender),
        'date_of_birth': sym_crypto.encrypt(date),
        'address': sym_crypto.encrypt(address)
        }

    #Store the data
    data_helper.save(user_id, type_attribute, p , "test")

    #print("Inserted new user in database at row {}".format(db.create_patient(patient)))
    print("MOCK | new user \'{}\' created".format(user_id))


def login(user):
    """
    Logs a user into the system if the correct credentials are provided.

    :param user:  User that wants to login
    """
    if arguments['-k'] or arguments['--key']:
        key = arguments['<key>']
        # TODO: exit program if wrong key is provided
        authenticate(user, key)
        print("MOCK | {} logged in with key {}".format(user, key))
    else:
        sys.exit("Please provide a key with the \'-k\' or \'--key\' option for authentication.")


def authenticate(user, key):
    """
    Authenticates a user, when authentication fails, the program should not continue.
    :param user:  User that needs to be authenticated
    :param key:   Key of the user
    """
    print("MOCK | {} is authenticated".format(user))

def load_user_key(user):
    with (kgc_path / 'user_id_{}'.format(user)).open(mode='rb') as f:
        user_key = pairing_pickle.load(group, f)
    return user_key



def read(user, key, record):
    """
    Function to read some public health record, this can only succeed if the user is allowed to read this. Returns
    all parts of the record that can be read.

    :param user:      User public key that wants to read the health record
    :param key:       Key of the user, used for decrypting the public health record
    :param record:    Public health record to be read
    """

    # Get the record from database
    d = data_helper.load(user, record)
    user_key = load_user_key(user)

    # Decrypt the symmetric key from the database
    sym_crypto_key = pre.decrypt(get_params(), user_key, d['enc_sym_key'])

    # Setup symmetric crypto
    sym_crypto = SymmetricCryptoAbstraction(extract_key(sym_crypto_key))

    # Attempt to decrypt all columns
    decrypted_record = [sym_crypto.decrypt(x) for x in [d['gender'], d['date_of_birth']]]  # more

    print("MOCK | Data is read from record \'{}\' by \'{}\'".format(decrypted_record, user))


def insert(user, key, data, record, type_attribute):
    """
    Insert data into a public health record.

    :param user:    User that wants to insert data
    :param key:     Key of the user
    :param data:    Data to be inserted
    :param record:  Public health record in which data is inserted, default: own record
    """
    if record == None:
        record = user

    print("MOCK | Data is inserted into record \'{}\' by \'{}\'".format(record, user))
    print("MOCK | Data inserted:\n{}".format(data))

def reEncrypt(user, to_user, record, type_attribute):

    ciphertext = data_helper.load(user, record)
    # Retrieve the reencryption key
    with (reencryption_path / 'from_{}_to_{}_type_{}'.format(user, to_user, type_attribute)).open(mode='rb') as f:
        re_encryption_key = pairing_pickle.load(group, f)   

    # Reencrypt the data
    cipher = pre.reEncrypt(get_params(), re_encryption_key, ciphertext['enc_sym_key'])
    ciphertext['enc_sym_key'] = cipher
    data_helper.save(to_user, type_attribute, ciphertext, "reencryption_from_{}_{}".format(to_user, record))
    return cipher


def allow_access(user, key, to_user, type_attribute):
    """
    Allow another user read access to own public health record. Ran by delegater.

    :param user:        Owner of the public health record
    :param key:         Key of user
    :param to_user:     Public key of the user that will get read access
    :param type_attribute:   Type of data that to_user will have access to
    """
    key = load_user_key(user)
    re_encryption_key = pre.rkGen(get_params(), key, to_user, type_attribute)

    with (reencryption_path / 'from_{}_to_{}_type_{}'.format(user, to_user, type_attribute)).open(mode='wb') as f:
        pairing_pickle.dump(group, re_encryption_key, f)

    print("MOCK | {} has provided {} with read access to their Public Health Record".format(user, to_user))

def new_hospital(name):
    kgc_generate_user(user)
    print("Created new hospital {}".format(name))

def new_patient(hospital, patient):
    # Use patient as type
    allow_access(hospital, None, patient, patient)

def insert_patient_data(hospital, patient, file_name, data):
    hospital_key = load_user_key(hospital)
    # Create new symmetric key
    sym_crypto_key = group.random(GT)
    sym_crypto = SymmetricCryptoAbstraction(extract_key(sym_crypto_key))
    # Encrypt symmetric key with TIPRE
    # and the data using the symmetric key
    encrypted_sym_key = pre.encrypt(get_params(), user_id, sym_crypto_key, user_key, type_attribute)
    p = {'enc_sym_key': encrypted_sym_key,
        'data': sym_crypto.encrypt(data),
        }
    #Store the data
    data_helper.save(user_id, type_attribute, p , "{}".format(file_name))

    #Reencrypt the data
    reEncrypt(hospital, patient, file_name, patient)
    

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['kgc'] and arguments['masterkey']:
        kgc_generate_master()
    elif arguments['kgc'] and arguments['userkey'] and arguments['<user_id>']:
        kgc_generate_user(arguments['<user_id>'])
    elif arguments['init']:
        init()
    elif arguments['new'] and arguments['patient']:
        kgc_generate_user(arguments['<user>'])
        new_patient(arguments['<user>'], arguments['<gender>'], arguments['<date-of-birth>'],
                 arguments['<patient-address>'])
    elif arguments['-l'] or arguments['--login']:
        login(arguments['<user>'])
        if arguments['read']:
            read(arguments['<user>'], arguments['<key>'], arguments['<record>'])
        if arguments['insert']:
            insert(arguments['<user>'], arguments['<key>'], arguments['<data>'], arguments['<record>'])
        if arguments['allow-access']:
            allow_access(arguments['<user>'], arguments['<key>'], arguments['<to-user>'], arguments['<type>'])
        if arguments['reencrypt']:
            reEncrypt(arguments['<user>'], arguments['<to-user>'], arguments['<record>'], arguments['<type>'])       

    else:
        print("Please provide login details.")
    try:
        db.exit()  # close database connection
    except AttributeError:
        pass
