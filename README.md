# Alles van een bepaald type, dus reencrypten van alle (werknemer, werkgever)
# Docs, typefouten verbeteren


### Cryptographically Enforced Access Control

#### KGC 

Setup: 
```console
foo@bar:~$ python PHR.py kgc generate masterkey
```
Creates a master key the public parameters


#### Record management

Creating a new user at KGC:
```console
foo@bar:~$ python user.py new john@email.com
``` 

Create a new patient and add data to its record
```console
foo@bar:~$ python user.py new john@email.com
foo@bar:~$ python user.py insert "Personal health data" -u john@email.com -t req2 -r health_data
```

### Read access for other parties than the patient

Create new employer
TODO create requirement 2 persons


##### Read access for the patient
Create a new hospital

```console
foo@bar:~$ python hospital.py new hospital_delft@email.com
```

Create a new patient for this hospital, because it has been treated by this hospital and 
generate a new reencryption key:

```console
foo@bar:~$ python hospital.py new-patient hospital_delft@email.com john@email.com -g male -d 01-01-2018 -a "Road 1"
```

Adding new data to a hospital patient record, by the hospital:

```console
foo@bar:~$ python hospital.py insert -d "Description of procedure: patient was helped in E.R." \
                                     -z hospital_delft@email.com \
                                     -p john@email.com \
                                     -t req3 \
                                     -r "02-02-1999"
```

When the patient wants to reads this hospital record, and select the number of the record that you want to read:

```console
foo@bar:~$ python user.py read patient_john@email.com_req3_02-02-1999 -u john@email.com
0. reencryption_from_hospital_hospital_delft@email.com_patient_john@email.com_req3_02-02-1999
1. health_data
2. reencryption_from_hospital_hospital_delft@email.com_patient_data_john@email.com
Choose the number of the file you want to read
```