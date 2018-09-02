import sqlite3
import json
import csv
import pandas as pd
import os
from werkzeug import secure_filename
def add_cou(Id, Name, prof_name):
	conn = sqlite3.connect('student.db')
	Name = "\""+Name+"\""
	prof_name = "\""+prof_name+"\""
	table_name = "attendence"+Id
	Id = "\""+Id+"\""
	conn.execute("insert into courses(id,Name,Prof_name)\
		values(%s,%s,%s)"%(Id,Name,prof_name))
	conn.execute("create table %s (id int not null unique, name text, total_attendence int default 0)"%(table_name))
	conn.commit()
	student={}
	student["students"]=[]
	file_name = 'Data/'+str(table_name)+'.json'
	attendence_csv = 'CSV/'+str(table_name)+'.csv'
	with open(file_name, 'w') as outfile:
		json.dump(student, outfile)
	df = pd.read_sql_query("select * from %s"%(table_name),conn)
	df.to_csv(attendence_csv, index=False)
	conn.close()
	return