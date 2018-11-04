import sqlite3
from sqlite3 import Error

db_file = "database/PHR.db"
create_table_patient = """ CREATE TABLE IF NOT EXISTS patient (
                                patient_id INTEGER PRIMARY KEY,
                                gender TEXT NOT NULL,
                                date_of_birth TEXT NOT NULL,
                                patient_name TEXT NOT NULL,
                                patient_address TEXT NOT NULL
                            ); """
create_table_patient_record = """ CREATE TABLE IF NOT EXISTS patient_record (
                                        record_id INTEGER PRIMARY KEY,
                                        patient_id INTEGER,
                                        hospital_id INTEGER,
                                        healthclub_id INTEGER,
                                        updated_date TEXT,
                                        data BLOB,
                                        FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
                                        FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id),
                                        FOREIGN KEY (healthclub_id) REFERENCES healthclub(healthclub_id)
                                    ); """
create_table_patient_record_hospital = """ CREATE TABLE IF NOT EXISTS patient_record_hospital (
                                        record_id INTEGER PRIMARY KEY,
                                        patient_id INTEGER,
                                        hospital_id INTEGER,
                                        healthclub_id INTEGER,
                                        updated_date TEXT,
                                        data BLOB,
                                        FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
                                        FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id),
                                        FOREIGN KEY (healthclub_id) REFERENCES healthclub(healthclub_id)
                                    ); """
create_table_patient_record_healthclub = """ CREATE TABLE IF NOT EXISTS patient_record_healthclub (
                                        record_id INTEGER PRIMARY KEY,
                                        patient_id INTEGER,
                                        hospital_id INTEGER,
                                        healthclub_id INTEGER,
                                        updated_date TEXT,
                                        data BLOB,
                                        FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
                                        FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id),
                                        FOREIGN KEY (healthclub_id) REFERENCES healthclub(healthclub_id)
                                    ); """
create_table_hospital = """ CREATE TABLE IF NOT EXISTS hospital (
                                hospital_id INTEGER PRIMARY KEY,
                                hospital_details TEXT NOT NULL,
                                hospital_name TEXT NOT NULL
                            ); """
create_table_healthclub = """ CREATE TABLE IF NOT EXISTS healthclub (
                                    healthclub_id INTEGER PRIMARY KEY,
                                    healthclub_details TEXT NOT NULL,
                                    healthclub_name TEXT NOT NULL
                                ); """


class Database:
    """Class for all database related methods"""
    conn = None

    def create_connection(self):
        """ create a database connection to a SQLite database """
        if self.conn is not None:
            return self.conn
        try:
            self.conn = sqlite3.connect(db_file)
            return self.conn
        except Error as e:
            print("Error, couldn't create database connection. {}".format(e))
        return None

    def initialize(self):
        conn = self.create_connection()
        if conn is not None:
            self.create_table(conn, create_table_patient)
            self.create_table(conn, create_table_hospital)
            self.create_table(conn, create_table_healthclub)
            self.create_table(conn, create_table_patient_record)
            self.create_table(conn, create_table_patient_record_hospital)
            self.create_table(conn, create_table_patient_record_healthclub)
        else:
            print("Error, couldn't create database connection.")

    def create_table(self, conn, sql):
        """
        Creates a table for the connected database.
        :param conn:    Connection to the database
        :param sql:     SQL script containing instruction for table creation
        """
        try:
            c = conn.cursor()
            c.execute(sql)
        except Error as e:
            print(e)

    def read(self):
        """ Reads data from the database. """
        return "read data"

    def create_patient(self, patient):
        """ 
        Creates a new patient in the database
        :param patient:     Array of patient details
        :return:            patient_id
        """
        conn = self.create_connection()
        if conn is None:
            return
        sql = ''' INSERT INTO patient(gender,
                    date_of_birth,patient_name,patient_address,other)
                    VALUES(?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, patient)
        conn.commit()
        return cur.lastrowid

    def create_hospital(self, hospital):
        """ 
        Creates a new hospital in the database
        :param hospital:     Array of hospital details
        :return:             hospital_id
        """
        conn = self.create_connection()
        if conn is None:
            return
        sql = ''' INSERT INTO hospital(hospital_details,
                    hospital_name)
                    VALUES(?,?) '''
        cur = conn.cursor()
        cur.execute(sql, hospital)
        conn.commit()
        return cur.lastrowid

    def create_healthclub(self, healthclub):
        """ 
        Creates a new healthclub in the database
        :param club:    Array of healthclub details
        :return:        healthclub_id
        """
        conn = self.create_connection()
        if conn is None:
            return
        sql = ''' INSERT INTO healthclub(healthclub_details,
                    healthclub_name)
                    VALUES(?,?) '''
        cur = conn.cursor()
        cur.execute(sql, healthclub)
        conn.commit()
        return cur.lastrowid

    def create_patient_record(self, record, record_table="patient_record"):
        """ 
        Creates a new patient record in the database
        :param record_table:    The table where the data is inserted, either "patient_record","patient_record_hospital", or "patient_record_healthclub"
        :param patient:     Array of patient record details
        :return:            record_id
        """
        conn = self.create_connection()
        if conn is None:
            return
        sql = ''' INSERT INTO ''' + record_table + '''(patient_id,
                    hospital_id,healthclub_id,updated_date,data)
                    VALUES(?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, record)
        conn.commit()
        return cur.lastrowid

    def create_patient_record_hospital(self, record):
        """ Creates a new hospital patient record """
        return self.create_patient_record(record, "patient_record_hospital")

    def create_patient_record_healthclub(self, record):
        """ Creates a new healthclub patient record """
        return self.create_patient_record(record, "patient_record_healthclub")

    def get_patient_record(self, record_table, patient_id=None, hospital_id=None, healthclub_id=None):
        """
        Fetches a patient record from one of the three possible databases
        :param record_table:    The table from which to fetch the data, either "patient_record","patient_record_hospital", or "patient_record_healthclub"
        :param patient_id:      patient_id associated with the record
        :param hospital_id:     hospital_id associated with the record
        :param healthclub_id:   healthclub_id associated with the record
        """
        conn = self.create_connection()
        if conn is None:
            return
        sql = ''' SELECT * FROM ''' + record_table + ''' WHERE '''
        if patient_id is not None:
            sql += ''' patient_id = ''' + str(patient_id) + ''' AND '''
        if hospital_id is not None:
            sql += ''' hospital_id = ''' + str(hospital_id) + ''' AND '''
        if healthclub_id is not None:
            sql += ''' healthclub_id = ''' + str(healthclub_id) + ''' AND '''
        sql = sql[:-4]
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def execute(self, sql):
        """
        Execute a custom build sql command for this database.
        :param sql:     The script
        :return:        Possible results
        """
        conn = self.create_connection()
        if conn is None:
            return False
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return cur.fetchall()

    def exit(self):
        """ Closes the database connection. """
        self.conn.close()
        self.conn = None
