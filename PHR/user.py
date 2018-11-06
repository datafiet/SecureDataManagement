"""Public Health Record interface

Usage:
    user.py
    user.py read <record> -u <user> 
    user.py read -u <user> 
    user.py insert <data> -u <user> -t <type> -r <record>
    user.py new <user>
    user.py allow-access -u <user> -p <to_user> -t <type> -r <record>

    
Options:
    -h --help                       Show this screen.
    -v --version                    Show version.
    -r<record> --record=<record>    Execute command for a specific public health record.
    -t<type> --type=<type>          Specify type of data.
"""
from subprocess import call

from docopt import docopt

import PHR


def read(arguments):
    data = PHR.read(PHR.USER(arguments['<user>']), arguments['<record>'])
    print(data)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['read']:
        if arguments['<record>'] is not None:
            read(arguments)
        else:
            print(PHR.select_file(PHR.USER(arguments['<user>'])))
    elif arguments['insert']:
        PHR.insert(PHR.USER(arguments['<user>']), {'data': arguments['<data>']}, arguments['<record>'],
                   arguments['<type>'])
    elif arguments['new']:
        print('Creating new user {}'.format(arguments['<user>']))
        PHR.kgc_generate_user(PHR.USER(arguments['<user>']))
    elif arguments['allow-access']:
        PHR.allow_access('user_{}'.format(arguments['<user>']), 'user_{}'.format(arguments['<to_user>']),
                         arguments['<type>'])

        # Call the proxy to reencrypt the just created ciphertext
        arguments = "python3 proxy.py reencrypt {} {} -r {} -t {}".format(
            'user_{}'.format(arguments['<user>']),
            'user_{}'.format(arguments['<to_user>']),
            arguments['<record>'],
            arguments['<type>']
        )
        call(arguments.split(' '))
