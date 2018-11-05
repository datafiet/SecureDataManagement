"""Public Health Record interface

Usage:
    hospital.py
    hospital.py new <hospital>
    hospital.py read [-z <hospital>] [-r <record>]
    hospital.py insert [-d <data>] [-z <hospital>] [-p  <patient>] [-t <type>] [-r <record>]
    hospital.py new-patient <hospital> <patient> -g <gender> -d <date> -a <address>


    
"""
import os
import sys
from pathlib import Path
import PHR 
from docopt import docopt
from subprocess import call


def read(hospital, record):
    data = PHR.read(PHR.HOSPITAL(hospital), record)
    print(data)

def new_patient(hospital, patient, gender, date, address):
    type_attribute = "patient"
    data = {'patient': patient, 'gender': gender, 'date_of_birth': date, 'address': address}
    record = 'patient_data_{}'.format(patient)
    hospital_insert(PHR.HOSPITAL(hospital), PHR.USER(patient), data, record, type_attribute)


def hospital_insert(hospital, patient, data, record, type_attribute):
    PHR.insert(hospital, data, record, type_attribute)
    PHR.allow_access(hospital, patient, type_attribute)

    arguments = "python3 proxy.py reencrypt {} {} -r {} -t {}".format(
        hospital,
        patient,
        record, type_attribute)
    call(arguments.split(' '))

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['read']:
        read(arguments['<hospital>'], arguments['<record>'])
    if arguments['insert']:
        hospital_insert(
            PHR.HOSPITAL(arguments['<hospital>']),  
            PHR.USER(arguments['<patient>']),
            {'data': arguments['<data>']}, arguments['<record>'], arguments['<type>'])
    if arguments['new']:
        print('Creating new hospital {}'.format(arguments['<hospital>']))
        PHR.kgc_generate_user(PHR.HOSPITAL(arguments['<hospital>']))
    if arguments['new-patient']:
        new_patient(arguments['<hospital>'], arguments['<patient>'], arguments['<gender>'], arguments['<date>'], arguments['<address>'])
