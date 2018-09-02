import sqlite3
from sqlite3 import Error
import json

def create_connection(db_file):
	try:
		conn = sqlite3.connect(db_file)
		print(sqlite3.version)
	except Erorr as e:
		print(e)
		exit(1)
	finally conn.close()

if __name__ == '__main__':
	create_connection('student.db')
	conn = sqlite3.connect('student.db')
	conn.execute("create table details (id int not null, name text not null, file1 text not null, file2 text not null, file3 text not null,PRIMARY KEY(id))")
	conn.execute("create table courses (id text not null unique, name text not null, Prof_name text not null,PRIMARY KEY(id))")
	data = {}
	json_file = "Data/details.json"
	with open(json_file, 'w') as outfile:
		json.dump(data, outfile)
	json_file = "Data/dictionary.json"
	with open(json_file, 'w') as outfile:
		json.dump(data, outfile)
	json_file = "Data/dictionary_reverse.json"
	with open(json_file, 'w') as outfile:
		json.dump(data, outfile)
	return