"""Public Health Record interface

Usage:
    PHR.py
    PHR.py read <record> -l <user> -k <key>
    PHR.py insert <data> -l <user> -k <key>
    PHR.py insert <data> -r <record> -l <user> -k <key>
    PHR.py allow-access <to-user> -t <type> -l <user> -k <key>
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
from docopt import docopt

def say_hello(name):
    return("Hello {}!".format(name))
    
# Logs a user into the system if the correct credentials are provided.
#   user  User that wants to login
def login(user):
    if arguments['-k'] or arguments['--key']:
        key = arguments['<key>']
        # TODO: exit program if wrong key is provided
        authenticate(user,key)
        print("{} logged in with key {}".format(user,key))
    else:
        sys.exit("Please provide a key with the \'-k\' or \'--key\' option for authentication.")

# Authenticates a user, when authentication fails, the program should not continue.
#   user  User that needs to be authenticated
#   key   Key of the user
def authenticate(user,key):
    print("{} is authenticated".format(user))

# Function to read some public health record, this can only succeed if the user is allowed to read this. Returns all parts of the record that can be read.
#   user      User that wants to read the health record
#   key       Key of the user, used for decrypting the public health record
#   record    Public health record to be read
def read(user,key,record):
#    recordfile = get_record(record)
#    decrypt(recordfile,key)
    print("Data is read from record \'{}\' by \'{}\'".format(record,user))

# Insert data into a public health record.
#   user    User that wants to insert data
#   key     Key of the user
#   data    Data to be inserted
#   record  Public health record in which data is inserted, default: own record
def insert(user,key,data,record):
    if record == None:
        record = user
    print("Data is inserted into record \'{}\' by \'{}\'".format(record,user))
    print("Data inserted:\n{}".format(data))
    
# Allow another user read access to own public health record.
#   user        Owner of the public health record
#   key         Key of user
#   to_user     User that will get read access
#   data_type   Type of data that to_user will have access to
def allow_access(user,key,to_user,data_type):
    print("{} has provided {} with read access to their Public Health Record".format(user,to_user))

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['-l'] or arguments['--login']:
        login(arguments['<user>'])
        if arguments['read']:
            read(arguments['<user>'],arguments['<key>'],arguments['<record>'])
        if arguments['insert']:
            insert(arguments['<user>'],arguments['<key>'],arguments['<data>'],arguments['<record>'])
        if arguments['allow-access']:
            allow_access(arguments['<user>'],arguments['<key>'],arguments['<to-user>'],arguments['<type>'])
    else:
        print("Please provide login details.")
        
        
