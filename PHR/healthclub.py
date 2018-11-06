"""Public Health Record interface

Usage:
    healtclub.py
    healtclub.py new <healtclub>
    healtclub.py read [-z <healtclub>] [-r <record>]
    healtclub.py read [-z <healtclub>]
    healtclub.py insert [-d <data>] [-z <healtclub>] [-p  <patient>] [-t <type>] [-r <record>]
    healtclub.py new-patient <healtclub> <patient> -g <gender> -d <date> -a <address>


    
"""
import os
import sys
from pathlib import Path
import PHR 
from docopt import docopt


def read(healtclub, record):
    data = PHR.read(PHR.HOSPITAL(healtclub), record)
    print(data)

def new_patient(healtclub, patient, gender, date, address):
    type_attribute = "patient"
    data = {'patient': patient, 'gender': gender, 'date_of_birth': date, 'address': address}
    record = 'patient_data_{}'.format(patient)
    PHR.insert_with_proxy(PHR.HEALTHCLUB(healtclub), PHR.USER(patient), data, record, type_attribute)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['read']:
        if(arguments['<record>'] == None):
            print(PHR.select_file(PHR.HEALTHCLUB(arguments['<healtclub>'])))
        else:
            read(arguments['<healtclub>'], arguments['<record>'])
    if arguments['insert']:
        PHR.insert_with_proxy(
            PHR.HEALTHCLUB(arguments['<healtclub>']),  
            PHR.USER(arguments['<patient>']),
            {'data': arguments['<data>']}, 
            'patient_{}_{}_{}'.format(arguments['<patient>'], arguments['<type>'], arguments['<record>']), 
            arguments['<type>'])
    if arguments['new']:
        print('Creating new healtclub {}'.format(arguments['<healtclub>']))
        PHR.kgc_generate_user(PHR.HEALTHCLUB(arguments['<healtclub>']))
    if arguments['new-patient']:
        new_patient(arguments['<healtclub>'], arguments['<patient>'], arguments['<gender>'], arguments['<date>'], arguments['<address>'])
