"""Public Health Record interface

Usage:
    PHR.py
    PHR.py init
    PHR.py kgc generate masterkey
    PHR.py kgc generate userkey <user_id>
    PHR.py read <record> -l <user> -k <key>
    PHR.py insert <data> -l <user> -k <key>
    PHR.py insert <data> -r <record> -l <user> -k <key>
    PHR.py allow-access <to-user> -t <type> -l <user> -k <key>
    PHR.py new patient <user> <gender> <date-of-birth> <patient-address>
    PHR.py new patient <user> <gender> <date-of-birth> <patient-address> <other>
    PHR.py -l <user> -k <key>
    PHR.py -h|--help
    PHR.py -v|--version
Options:
    -h --help                       Show this screen.
    -v --version                    Show version.
    -l<user> --login=<user>         Login as user.
    -k<key> --key=<key>             Path to key for authentication of user.
    -r<record> --record=<record>    Execute command for a specific public health record.
    -t<type> --type=<type>          Specify type of data.
"""
import sys

from charm.toolbox.pairinggroup import PairingGroup
from docopt import docopt
from database import Database
from type_id_proxy_reencryption import TIPRE
from pathlib import Path
import pairing_pickle

db = Database()

kgc_path = Path('keys/kgc')

group = PairingGroup('SS512', secparam=1024)
pre = TIPRE(group)


def kgc_generate_master():
    master_secret_key, params = pre.setup()

    with (kgc_path / 'master_key').open(mode='wb') as f:
        pairing_pickle.dump(group, master_secret_key, f)
    with (kgc_path / 'params').open(mode='wb') as f:
        pairing_pickle.dump(group, params, f)


def kgc_generate_user(user_id: str):
    with (kgc_path / 'master_key').open(mode='rb') as f:
        master_key = pairing_pickle.load(group, f)
    with (kgc_path / 'user_id_{}'.format(user_id)).open(mode='wb') as f:
        pairing_pickle.dump(group, pre.keyGen(master_key, user_id), f)


def init():
    """ Initializes the database """
    db.initialize()


def new_user(user, gender, date_of_birth, address, other):
    """
    Create a new user, creates a Public Health Record and a key.
    :param user:    The new user to be created
    """
    key = "/path/to/key"
    patient = [gender, date_of_birth, user, address, other]
    patient
    print("Inserted new user in database at row {}".format(db.create_patient(patient)))
    print("MOCK | new user \'{}\' created, key location: {}".format(user, key))


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


def read(user, key, record):
    """
    Function to read some public health record, this can only succeed if the user is allowed to read this. Returns
    all parts of the record that can be read.
    :param user:      User that wants to read the health record
    :param key:       Key of the user, used for decrypting the public health record
    :param record:    Public health record to be read
    """
    #    recordfile = get_record(record)
    #    decrypt(recordfile,key)
    print("MOCK | Data is read from record \'{}\' by \'{}\'".format(record, user))


def insert(user, key, data, record):
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


def allow_access(user, key, to_user, data_type):
    """
    Allow another user read access to own public health record.
    :param user:        Owner of the public health record
    :param key:         Key of user
    :param to_user:     User that will get read access
    :param data_type:   Type of data that to_user will have access to
    """
    print("MOCK | {} has provided {} with read access to their Public Health Record".format(user, to_user))


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['kgc'] and arguments['masterkey']:
        kgc_generate_master()
    elif arguments['kgc'] and arguments['userkey'] and arguments['<user_id>']:
        kgc_generate_user(arguments['<user_id>'])
    elif arguments['init']:
        init()
    elif arguments['new'] and arguments['patient']:
        new_user(arguments['<user>'], arguments['<gender>'], arguments['<date-of-birth>'],
                 arguments['<patient-address>'], arguments['<other>'])
    elif arguments['-l'] or arguments['--login']:
        login(arguments['<user>'])
        if arguments['read']:
            read(arguments['<user>'], arguments['<key>'], arguments['<record>'])
        if arguments['insert']:
            insert(arguments['<user>'], arguments['<key>'], arguments['<data>'], arguments['<record>'])
        if arguments['allow-access']:
            allow_access(arguments['<user>'], arguments['<key>'], arguments['<to-user>'], arguments['<type>'])
    else:
        print("Please provide login details.")
    try:
        db.exit()  # close database connection
    except AttributeError:
        pass
