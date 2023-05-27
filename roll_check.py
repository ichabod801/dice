"""
roll_check.py

Code for the 2,000 dice rolls post.

Functions:
clean_data: Clean a data file with blank roll counts. (None)
read_data: Read a data file with roll counts. (None)
"""

from collections import Counter
import statistics

def clean_data(path):
	"""
	Clean a data file with blank roll counts. (None)

	Parameters:
	path: The file system path to the file to clean. (str)
	"""
	with open(path, 'r+') as data_file:
		cleaned = []
		for line in data_file:
			if line.endswith('\t\n'):
				cleaned.append(line[:-1] + '1\n')
			else:
				cleaned.append(line)
		data_file.seek(0)
		data_file.write(''.join(cleaned))
		data_file.truncate()

def read_data(path, value_type = int):
	"""
	Read a data file with roll counts. (None)

	Parameters:
	path: The file system path to the file to read. (str)
	value_type: The data type for the values. (type)
	"""
	data = Counter()
	with open(path) as data_file:
		for line in data_file:
			value, count = line.strip().split('\t')
			data.update({value_type(value): int(count)})
	return data
