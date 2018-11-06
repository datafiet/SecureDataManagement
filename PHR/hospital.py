"""Public Health Record interface

Usage:
    hospital.py
    hospital.py new <hospital>
    hospital.py read [-z <hospital>] [-r <record>]
    hospital.py read [-z <hospital>]
    hospital.py insert [-d <data>] [-z <hospital>] [-p  <patient>] [-t <type>] [-r <record>]
    hospital.py new-patient <hospital> <patient> -g <gender> -d <date> -a <address>
"""

from docopt import docopt

import PHR


def read(hospital, record):
    data = PHR.read(PHR.HOSPITAL(hospital), record)
    print(data)


def new_patient(hospital, patient, gender, date, address):
    type_attribute = "patient"
    data = {'patient': patient, 'gender': gender, 'date_of_birth': date, 'address': address}
    record = 'patient_data_{}'.format(patient)
    PHR.insert_with_proxy(PHR.HOSPITAL(hospital), PHR.USER(patient), data, record, type_attribute)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    if arguments['read'] and arguments['<hospital>']:
        if arguments['<record>'] is None:
            print(PHR.select_file(PHR.HOSPITAL(arguments['<hospital>'])))
        else:
            read(arguments['<hospital>'], arguments['<record>'])
    elif arguments['insert']:
        PHR.insert_with_proxy(
            PHR.HOSPITAL(arguments['<hospital>']),
            PHR.USER(arguments['<patient>']),
            {'data': arguments['<data>']},
            'patient_{}_{}_{}'.format(arguments['<patient>'], arguments['<type>'], arguments['<record>']),
            arguments['<type>'])
    elif arguments['new']:
        print('Creating new hospital {}'.format(arguments['<hospital>']))
        PHR.kgc_generate_user(PHR.HOSPITAL(arguments['<hospital>']))
    elif arguments['new-patient']:
        new_patient(arguments['<hospital>'], arguments['<patient>'], arguments['<gender>'], arguments['<date>'],
                    arguments['<address>'])
    else:
        print(__doc__)
