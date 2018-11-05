import os
import json
import jsonpickle
import pairing_pickle

from pathlib import Path

class DataHelper:

	def __init__(self, group):
		self.dir_path = os.path.dirname(os.path.realpath(__file__))
		self.data_path = '{}/data/'.format(self.dir_path)
		self.create_folder(self.data_path)
		self.group = group


	def create_folder(self, path):
		try:
			Path(path).mkdir(parents=True)
		except:
			pass

	def save(self, user, type_attribute, data, file_name):
		self.create_folder('{}{}'.format(self.data_path, user))
		path = '{}{}/{}'.format(self.data_path, user, '{}.json'.format(file_name))
		with open(path, 'w') as outfile:
			outfile.write(pairing_pickle.dump2(self.group, data))


	def load(self, user, file_name):
		self.create_folder('{}{}'.format(self.data_path, user))
		path = '{}{}/{}'.format(self.data_path, user, '{}.json'.format(file_name))
		with open(path, 'r') as infile:
			data = pairing_pickle.load2(self.group, infile.read())
		return data










