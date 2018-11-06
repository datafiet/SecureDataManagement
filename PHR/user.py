"""Public Health Record interface

Usage:
    user.py
    user.py read <record> -u <user> 
    user.py read -u <user> 
    user.py insert <data> -u <user> -t <type> -r <record>
    user.py new <user> 

    
Options:
    -h --help                       Show this screen.
    -v --version                    Show version.
    -r<record> --record=<record>    Execute command for a specific public health record.
    -t<type> --type=<type>          Specify type of data.
"""
import os
import sys
from pathlib import Path
import PHR 
from docopt import docopt

def read(arguments):
    data = PHR.read(PHR.USER(arguments['<user>']), arguments['<record>'])
    print(data)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['read']:
        if(arguments['<record>'] != None):
            read(arguments)
        else:
            print(PHR.select_file(PHR.USER(arguments['<user>'])))
    if arguments['insert']:
        PHR.insert(PHR.USER(arguments['<user>']),  {'data': arguments['<data>']}, arguments['<record>'], arguments['<type>'])
    if arguments['new']:
        print('Creating new user {}'.format(arguments['<user>']))
        PHR.kgc_generate_user(PHR.USER(arguments['<user>']))

